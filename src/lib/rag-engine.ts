import OpenAI from 'openai';
import fs from 'fs';
import path from 'path';

// Initialize OpenAI client
// Note: This requires OPENAI_API_KEY in .env.local
const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

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
        console.log(`Generating embedding for text: "${text.substring(0, 20)}..." using key: ${process.env.OPENAI_API_KEY ? 'Set' : 'Not Set'}`);

        const response = await openai.embeddings.create({
            model: "text-embedding-3-small",
            input: text,
            encoding_format: "float",
        });
        return response.data[0].embedding;
    } catch (error) {
        console.error("OpenAI Embedding Error:", error);
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
