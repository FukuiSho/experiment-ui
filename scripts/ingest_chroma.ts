
import fs from 'fs';
import path from 'path';
import { ChromaClient } from 'chromadb';

// Configuration
const SOURCE_DIR = path.join(__dirname, '../src/lib/pesonaldata/DBmakedused/chunks');
const CHROMA_URL = process.env.CHROMA_URL || 'http://localhost:8000';
const COLLECTION_NAME = 'limitless_logs';
const OLLAMA_HOST = process.env.OLLAMA_HOST || 'http://127.0.0.1:11434';
const OLLAMA_EMBED_MODEL = process.env.OLLAMA_EMBED_MODEL || 'nomic-embed-text';

const CATEGORIES = ['Fact', 'Thought', 'Experience'];

// --- Helpers ---

// Generate embedding using Ollama
async function generateEmbedding(text: string): Promise<number[]> {
    const url = `${OLLAMA_HOST.replace(/\/$/, '')}/api/embeddings`;
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model: OLLAMA_EMBED_MODEL, prompt: text }),
        });

        if (!res.ok) throw new Error(`Ollama error: ${res.status} ${res.statusText}`);

        const data: any = await res.json();
        return data.embedding || [];
    } catch (e) {
        console.error('Embedding generation failed:', e);
        return [];
    }
}

// Split text into chunks
function splitText(text: string, chunkSize: number = 500, overlap: number = 50): string[] {
    const chunks: string[] = [];
    let start = 0;
    while (start < text.length) {
        const end = Math.min(start + chunkSize, text.length);
        chunks.push(text.slice(start, end));
        start += (chunkSize - overlap);
    }
    return chunks;
}

// Main Ingestion Logic
async function main() {
    console.log(`Connecting to Chroma at ${CHROMA_URL}...`);
    const client = new ChromaClient({ path: CHROMA_URL });

    // Get or Create Collection
    const collection = await client.getOrCreateCollection({
        name: COLLECTION_NAME,
        metadata: { "description": "Personal data logs" }
    });
    console.log(`Collection '${COLLECTION_NAME}' ready.`);

    let totalProcessed = 0;

    for (const category of CATEGORIES) {
        const categoryDir = path.join(SOURCE_DIR, category);
        if (!fs.existsSync(categoryDir)) {
            console.warn(`Category directory missing: ${categoryDir}`);
            continue;
        }

        const files = fs.readdirSync(categoryDir).filter(f => f.endsWith('.txt'));
        console.log(`Processing ${category}: ${files.length} files found.`);

        for (const file of files) {
            const filePath = path.join(categoryDir, file);
            const content = fs.readFileSync(filePath, 'utf-8');

            if (!content.trim()) continue;

            // Split into chunks
            const textChunks = splitText(content);
            const ids: string[] = [];
            const embeddings: number[][] = [];
            const metadatas: any[] = [];
            const documents: string[] = [];

            for (let i = 0; i < textChunks.length; i++) {
                const chunk = textChunks[i];
                const embedding = await generateEmbedding(chunk);

                if (embedding.length === 0) continue; // Skip failed embeddings

                const id = `${category}_${file}_${i}`;

                ids.push(id);
                embeddings.push(embedding);
                metadatas.push({
                    source: file,
                    category: category,
                    chunk_index: i
                });
                documents.push(chunk);
            }

            if (ids.length > 0) {
                await collection.upsert({
                    ids,
                    embeddings,
                    metadatas,
                    documents
                });
                // dot progress
                process.stdout.write('.');
            }
            totalProcessed++;
        }
        console.log(`\nFinished ${category}.`);
    }

    console.log(`\nIngestion complete. Processed ${totalProcessed} files.`);
}

main().catch(console.error);
