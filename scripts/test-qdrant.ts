import { getQdrantClient, ensureCollection, COLLECTION_NAME } from '../src/lib/qdrant';

async function testConnection() {
    console.log('--- Testing Qdrant Connection ---');
    try {
        const client = getQdrantClient();
        console.log('Client initialized.');

        console.log('Checking connection by ensuring collection...');
        await ensureCollection();
        console.log('Collection check passed.');

        // Verify collection details
        const collectionInfo = await client.getCollection(COLLECTION_NAME);
        console.log('Collection Info:', collectionInfo);

        if (collectionInfo.status === 'green' || collectionInfo.status === 'yellow') {
            console.log('✅ TEST PASSED: Qdrant is reachable and collection works.');
            process.exit(0);
        } else {
            console.error('❌ TEST FAILED: Collection status is', collectionInfo.status);
            process.exit(1);
        }

    } catch (error: any) {
        console.error('❌ TEST FAILED with error:');
        if (error.cause && error.cause.code === 'ECONNREFUSED') {
            console.error('   Connection Refused. Is Qdrant running on http://127.0.0.1:6333?');
            console.error('   Please run: docker compose up -d');
        } else {
            console.error(error);
        }
        process.exit(1);
    }
}

testConnection();
