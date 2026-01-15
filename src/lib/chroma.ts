import { ChromaClient, Collection } from 'chromadb';

const CHROMA_URL = process.env.CHROMA_URL || 'http://localhost:8000';

// Singleton instance
let client: ChromaClient | null = null;

export const getChromaClient = (): ChromaClient => {
    if (!client) {
        client = new ChromaClient({ path: CHROMA_URL });
    }
    return client;
};

export const COLLECTION_NAME = 'limitless_logs';

export async function getCollection(): Promise<Collection> {
    const client = getChromaClient();
    try {
        // getOrCreateCollection is the standard way in JS client
        const collection = await client.getOrCreateCollection({
            name: COLLECTION_NAME,
            metadata: { "description": "Limitless logs for RAG" },
            // We handle embeddings manually with Ollama, so we provide a dummy embedding function
            // to prevent Chroma from trying to load the default-embed package.
            embeddingFunction: {
                generate: async (texts: string[]) => {
                    return texts.map(() => []); // Return empty or dummy embeddings, we won't use this path
                }
            }
        });
        return collection;
    } catch (error) {
        console.error('Error getting/creating collection:', error);
        throw error;
    }
}
