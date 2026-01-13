import { QdrantClient } from '@qdrant/js-client-rest';

const QDRANT_URL = process.env.QDRANT_URL || 'http://127.0.0.1:6333';

// Singleton instance
let client: QdrantClient | null = null;

export const getQdrantClient = (): QdrantClient => {
    if (!client) {
        client = new QdrantClient({ url: QDRANT_URL });
    }
    return client;
};

export const COLLECTION_NAME = 'limitless_logs';
const VECTOR_SIZE = 768; // nomic-embed-text size

export async function ensureCollection() {
    const client = getQdrantClient();
    try {
        const result = await client.getCollections();
        const exists = result.collections.some(c => c.name === COLLECTION_NAME);

        if (!exists) {
            console.log(`Collection ${COLLECTION_NAME} does not exist. Creating...`);
            await client.createCollection(COLLECTION_NAME, {
                vectors: {
                    size: VECTOR_SIZE,
                    distance: 'Cosine',
                },
            });
            console.log(`Collection ${COLLECTION_NAME} created.`);
        } else {
            // console.log(`Collection ${COLLECTION_NAME} exists.`);
        }
    } catch (error) {
        console.error('Error ensuring collection:', error);
        throw error;
    }
}
