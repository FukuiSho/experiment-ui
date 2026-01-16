
import { ChromaClient } from 'chromadb';

const CHROMA_URL = 'http://[::1]:8000';
const COLLECTION_NAME = 'limitless_logs';

async function main() {
    console.log(`Connecting to Chroma at ${CHROMA_URL}...`);
    const client = new ChromaClient({ path: CHROMA_URL });

    try {
        const collection = await client.getCollection({
            name: COLLECTION_NAME,
            embeddingFunction: {
                generate: async (texts) => texts.map(() => [])
            }
        });

        const count = await collection.count();
        console.log(`Collection '${COLLECTION_NAME}' contains ${count} items.`);

        if (count > 0) {
            const peek = await collection.peek({ limit: 1 });
            console.log('Sample item:', JSON.stringify(peek, null, 2));
        }

    } catch (e) {
        console.error("Verification failed:", e);
    }
}

main();
