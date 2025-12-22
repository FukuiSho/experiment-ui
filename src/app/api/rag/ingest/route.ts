import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { generateEmbedding, saveVectorStore, VectorChunk } from '@/lib/rag-engine';

const KNOWLEDGE_FILE_PATH = path.join(process.cwd(), 'src', 'data', 'limitless-knowledge.md');

export async function POST() {
    try {
        if (!fs.existsSync(KNOWLEDGE_FILE_PATH)) {
            return NextResponse.json({ error: 'Knowledge file not found. Please save data first.' }, { status: 404 });
        }

        const markdown = fs.readFileSync(KNOWLEDGE_FILE_PATH, 'utf-8');

        // Simple splitting strategy: Split by "---" separator used in our converter
        const rawChunks = markdown.split('\n---\n').filter(c => c.trim().length > 0);

        const vectorChunks: VectorChunk[] = [];

        console.log(`Processing ${rawChunks.length} chunks...`);

        for (let i = 0; i < rawChunks.length; i++) {
            const content = rawChunks[i].trim();
            if (!content) continue;

            // Generate embedding
            // Note: In production, you might want to batch these or rate limit
            const embedding = await generateEmbedding(content);

            vectorChunks.push({
                id: `chunk_${Date.now()}_${i}`,
                content,
                metadata: {
                    source: 'limitless-knowledge.md',
                    timestamp: new Date().toISOString(),
                },
                embedding,
            });
        }

        await saveVectorStore(vectorChunks);

        return NextResponse.json({
            success: true,
            count: vectorChunks.length,
            message: 'Ingestion complete'
        });

    } catch (error: any) {
        console.error('Ingestion Error:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
