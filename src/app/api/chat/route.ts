import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';
import { searchVectorStore } from '@/lib/rag-engine';
import { SYSTEM_PROMPT, CLONE_AI_CONFIG } from '@/lib/constants';

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(request: NextRequest) {
    try {
        const { message, condition } = await request.json();

        if (!message) {
            return NextResponse.json({ error: 'Message is required' }, { status: 400 });
        }

        // 1. Retrieve relevant context (Only for Personalized condition)
        let contextText = "";
        let relevantChunks: any[] = [];

        if (condition === 'P') {
            relevantChunks = await searchVectorStore(message, 3);
            contextText = relevantChunks.map(c => c.content).join('\n\n---\n\n');
        }

        // 2. Construct System Prompt with Context
        let systemPromptWithContext = SYSTEM_PROMPT;

        if (contextText) {
            systemPromptWithContext += `

以下は、あなたの最近の記憶（Limitless Lifelogs）の一部です。
会話の文脈として参考にしてください。
----------------
${contextText}
----------------`;
        }

        // 3. Call OpenAI with CloneAI parameters
        const response = await openai.chat.completions.create({
            model: CLONE_AI_CONFIG.model,
            messages: [
                { role: 'system', content: systemPromptWithContext },
                { role: 'user', content: message },
            ],
            temperature: CLONE_AI_CONFIG.temperature,
            top_p: CLONE_AI_CONFIG.top_p,
            presence_penalty: CLONE_AI_CONFIG.presence_penalty,
            frequency_penalty: CLONE_AI_CONFIG.frequency_penalty,
            max_tokens: CLONE_AI_CONFIG.max_tokens,
        });

        const reply = response.choices[0].message.content;

        return NextResponse.json({
            reply,
            retrieved_context: relevantChunks // For debugging/display
        });

    } catch (error: any) {
        console.error('Chat API Error:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
