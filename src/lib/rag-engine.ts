import { getCollection } from './chroma';

type OllamaEmbeddingResponse = {
    embedding?: number[];
    error?: string;
};

export interface VectorChunk {
    id: string;
    content: string;
    metadata: {
        source: string;
        timestamp?: string;
        speaker?: string;
        [key: string]: any; // Chroma allows flexible metadata
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

export async function saveVectorStore(chunks: VectorChunk[]) {
    if (chunks.length === 0) return;

    const collection = await getCollection();

    // ChromaDB expects separate arrays
    const ids = chunks.map(c => c.id);
    const embeddings = chunks.map(c => c.embedding);
    // Metadata values must be primitives (string, number, boolean)
    // We ensure metadata matches this requirement.
    const metadatas = chunks.map(c => c.metadata);
    const documents = chunks.map(c => c.content);

    await collection.upsert({
        ids,
        embeddings,
        metadatas,
        documents
    });

    console.log(`Upserted ${chunks.length} chunks to ChromaDB.`);
}

export async function searchVectorStore(query: string, limit: number = 3, filterCategories: string[] = []): Promise<VectorChunk[]> {
    const collection = await getCollection();

    // Generate embedding for the query
    const queryEmbedding = await generateEmbedding(query);

    // Build where clause if categories are provided
    const whereClause: any = filterCategories.length > 0
        ? { category: { "$in": filterCategories } }
        : undefined;

    // Query ChromaDB
    const results = await collection.query({
        queryEmbeddings: [queryEmbedding],
        nResults: limit,
        where: whereClause
    });

    // Map back to VectorChunk structure
    const queryResults = results.ids[0];
    if (!queryResults || queryResults.length === 0) return [];

    const chunks: VectorChunk[] = [];

    for (let i = 0; i < queryResults.length; i++) {
        chunks.push({
            id: results.ids[0][i],
            content: results.documents?.[0]?.[i] || '',
            metadata: results.metadatas?.[0]?.[i] as any || {},
            embedding: []
        });
    }

    return chunks;
}
