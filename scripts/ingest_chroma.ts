
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
    // For ablation studies, we might want to reset the collection. 
    // But upsert is fine if we delete the collection before running this script in the orchestrator.
    // However, to be safe for ablation, we should probably delete the collection if it exists?
    // The user's plan implies "Recreate ChromaDB". 
    // The orchestrator `auto_eval.py` should handle `client.delete_collection` or we can add a flag here.
    // For now, let's assume the orchestrator will handle the clean state, or we can force reset here.

    // Let's add a RESET flag checking
    if (process.env.RESET_COLLECTION === 'true') {
        try {
            await client.deleteCollection({ name: COLLECTION_NAME });
            console.log(`Deleted existing collection '${COLLECTION_NAME}'`);
        } catch (e) {
            // Ignore if doesn't exist
        }
    }

    const collection = await client.getOrCreateCollection({
        name: COLLECTION_NAME,
        metadata: { "description": "Personal data logs" }
    });
    console.log(`Collection '${COLLECTION_NAME}' ready.`);

    // Exclusion Pattern
    // Exclusion Pattern
    const excludeEnv = process.env.EXCLUDE_PATTERN;
    const excludePatterns = excludeEnv ? excludeEnv.split(',').map(p => p.trim().toLowerCase()).filter(p => p.length > 0) : [];

    if (excludePatterns.length > 0) {
        console.log(`Exclusion Patterns Active: "${excludePatterns.join(', ')}". Files containing these strings will be skipped.`);
    }

    let totalProcessed = 0;
    let totalSkipped = 0;

    for (const category of CATEGORIES) {
        const categoryDir = path.join(SOURCE_DIR, category);
        if (!fs.existsSync(categoryDir)) {
            console.warn(`Category directory missing: ${categoryDir}`);
            continue;
        }

        const files = fs.readdirSync(categoryDir).filter(f => f.endsWith('.txt'));
        console.log(`Processing ${category}: ${files.length} files found.`);

        for (const file of files) {
            // Check exclusion
            const shouldSkip = excludePatterns.some(p => file.toLowerCase().includes(p));
            if (shouldSkip) {
                totalSkipped++;
                // console.log(`Skipping ${file}`); // Optional verbosity
                continue;
            }

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

    console.log(`\nIngestion complete.`);
    console.log(`Processed: ${totalProcessed}`);
    console.log(`Skipped: ${totalSkipped}`);
}

main().catch(console.error);
