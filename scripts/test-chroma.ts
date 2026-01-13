import { getCollection, COLLECTION_NAME } from '../src/lib/chroma';
import { generateEmbedding } from '../src/lib/rag-engine';

async function testChroma() {
    console.log('--- Testing ChromaDB Connection ---');
    try {
        // 1. Connection & Collection Check
        console.log(`Connecting to ChromaDB and getting collection '${COLLECTION_NAME}'...`);
        const collection = await getCollection();
        console.log('✅ Collection retrieved successfully.');

        // 2. Test Embedding (Ollama)
        console.log('Testing Ollama embedding generation...');
        const testText = "Hello Chroma";
        const embedding = await generateEmbedding(testText);
        console.log(`✅ Embedding generated. Dimension: ${embedding.length}`);

        // 3. Test Upsert
        console.log('Testing Upsert...');
        const id = 'test_id_1';
        await collection.upsert({
            ids: [id],
            embeddings: [embedding],
            metadatas: [{ source: 'test-script' }],
            documents: [testText]
        });
        console.log('✅ Upsert successful.');

        // 4. Test Query
        console.log('Testing Query...');
        const results = await collection.query({
            queryEmbeddings: [embedding],
            nResults: 1
        });

        if (results.ids[0].includes(id)) {
            console.log('✅ Query successful. Found ingested document.');
            console.log('Document:', results.documents[0][0]);
        } else {
            console.error('❌ Query failed. Did not find ingested document.');
            console.log('Results:', JSON.stringify(results, null, 2));
            process.exit(1);
        }

        console.log('🎉 ALL TESTS PASSED');
        process.exit(0);

    } catch (error: any) {
        console.error('❌ TEST FAILED with error:');
        console.error(error);

        if (error.code === 'ECONNREFUSED') {
            console.error('\n⚠️  Could not connect to ChromaDB.');
            console.error('Please make sure you have started the ChromaDB server:');
            console.error('Run: .\\scripts\\start-chroma.ps1');
        }

        process.exit(1);
    }
}

testChroma();
