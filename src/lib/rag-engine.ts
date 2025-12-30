import fs from 'fs';
import path from 'path';

type OllamaEmbeddingResponse = {
    embedding?: number[];
    error?: string;
};

const VECTOR_STORE_PATH = path.join(process.cwd(), 'src', 'data', 'vector-store.json');

export interface VectorChunk {
    id: string;
    content: string;
    metadata: {
        source: string;
        timestamp?: string;
        speaker?: string;
    };
    embedding: number[];
}

export async function generateEmbedding(text: string): Promise<number[]> {
    try {
        const host = process.env.OLLAMA_HOST || 'http://127.0.0.1:11434';
        const model = process.env.OLLAMA_EMBED_MODEL || 'nomic-embed-text';
        const url = `${host.replace(/\/$/, '')}/api/embeddings`;

        let res: Response;
        try {
            res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model, prompt: text }),
            });
        } catch (err: any) {
            const cause = err?.cause;
            const code = cause?.code || err?.code;
            if (code === 'ECONNREFUSED' || code === 'ENOTFOUND') {
                throw new Error(
                    `Ollama Embeddingsへ接続できませんでした (${host}). Ollamaが起動しているか確認してください。` +
                    `\n- 確認: http://127.0.0.1:11434/api/tags` +
                    `\n- 別ホストなら OLLAMA_HOST を設定` +
                    `\n- モデル未取得なら: ollama pull ${model}`
                );
            }
            throw err;
        }

        if (!res.ok) {
            const errorText = await res.text().catch(() => '');
            throw new Error(`Ollama embeddings error: ${res.status} ${errorText}`);
        }

        const data = (await res.json()) as OllamaEmbeddingResponse;
        if (!data.embedding || data.embedding.length === 0) {
            throw new Error('Ollama embeddings returned empty embedding');
        }
        return data.embedding;
    } catch (error) {
        console.error("Embedding Error:", error);
        throw error;
    }
}

export function calculateCosineSimilarity(vecA: number[], vecB: number[]): number {
    const dotProduct = vecA.reduce((sum, a, i) => sum + a * vecB[i], 0);
    const magnitudeA = Math.sqrt(vecA.reduce((sum, a) => sum + a * a, 0));
    const magnitudeB = Math.sqrt(vecB.reduce((sum, b) => sum + b * b, 0));
    return dotProduct / (magnitudeA * magnitudeB);
}

export async function saveVectorStore(chunks: VectorChunk[]) {
    const dir = path.dirname(VECTOR_STORE_PATH);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(VECTOR_STORE_PATH, JSON.stringify(chunks, null, 2));
}

export function loadVectorStore(): VectorChunk[] {
    if (!fs.existsSync(VECTOR_STORE_PATH)) return [];
    const data = fs.readFileSync(VECTOR_STORE_PATH, 'utf-8');
    return JSON.parse(data);
}

export async function searchVectorStore(query: string, limit: number = 3): Promise<VectorChunk[]> {
    const store = loadVectorStore();
    if (store.length === 0) return [];

    const queryEmbedding = await generateEmbedding(query);

    const scored = store.map(chunk => ({
        chunk,
        score: calculateCosineSimilarity(queryEmbedding, chunk.embedding),
    }));

    // Sort by score descending
    scored.sort((a, b) => b.score - a.score);

    return scored.slice(0, limit).map(item => item.chunk);
}
