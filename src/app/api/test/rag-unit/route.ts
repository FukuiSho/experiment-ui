import { NextResponse } from 'next/server';
import { generateEmbedding, calculateCosineSimilarity } from '@/lib/rag-engine';

export async function GET() {
    console.log('RAG Unit Test Started');
    try {
        // 1. Test Embedding Generation
        const text = "Hello world";
        const embedding = await generateEmbedding(text);

        if (!embedding || embedding.length !== 1536) {
            throw new Error(`Embedding generation failed. Length: ${embedding?.length}`);
        }

        // 2. Test Similarity
        const vecA = [1, 0, 0];
        const vecB = [1, 0, 0];
        const vecC = [0, 1, 0];

        // Mock similarity for simple vectors (our function expects full length but math works for any length)
        // We'll just test the math logic separately or trust the function if we pass full vectors.
        // Let's just test the function with the real embedding against itself (should be 1.0)
        const sim = calculateCosineSimilarity(embedding, embedding);

        if (Math.abs(sim - 1.0) > 0.0001) {
            throw new Error(`Self-similarity is not 1.0. Got: ${sim}`);
        }

        return NextResponse.json({ success: true, message: "RAG Unit Tests Passed" });
    } catch (error: any) {
        console.error('RAG Unit Test Error:', JSON.stringify(error, Object.getOwnPropertyNames(error)));
        return NextResponse.json({ success: false, error: error.message, details: JSON.stringify(error, Object.getOwnPropertyNames(error)) }, { status: 500 });
    }
}
