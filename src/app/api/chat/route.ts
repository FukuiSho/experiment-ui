import { NextRequest, NextResponse } from 'next/server';
import { searchVectorStore } from '@/lib/rag-engine';
import { SYSTEM_PROMPT, OLLAMA_CHAT_CONFIG } from '@/lib/constants';

type OllamaChatResponse = {
    message?: { role?: string; content?: string };
    error?: string;
};

async function chatWithOllama(params: {
    model: string;
    system: string;
    user: string;
}): Promise<string> {
    const host = process.env.OLLAMA_HOST || 'http://127.0.0.1:11434';
    const url = `${host.replace(/\/$/, '')}/api/chat`;

    let res: Response;
    try {
        res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: params.model,
                stream: false,
                messages: [
                    { role: 'system', content: params.system },
                    { role: 'user', content: params.user },
                ],
                options: {
                    temperature: OLLAMA_CHAT_CONFIG.temperature,
                    top_p: OLLAMA_CHAT_CONFIG.top_p,
                    num_predict: OLLAMA_CHAT_CONFIG.num_predict,
                },
            }),
        });
    } catch (err: any) {
        const cause = err?.cause;
        const code = cause?.code || err?.code;
        if (code === 'ECONNREFUSED' || code === 'ENOTFOUND') {
            throw new Error(
                `Ollamaへ接続できませんでした (${host}). Ollamaが起動しているか確認してください。` +
                `\n- Windows: Ollamaアプリを起動（または再起動）` +
                `\n- 確認: http://127.0.0.1:11434/api/tags` +
                `\n- 別ホストなら OLLAMA_HOST を設定` +
                `\n- モデル未取得なら: ollama pull ${process.env.OLLAMA_CHAT_MODEL || 'gemma3:1b'}`
            );
        }
        throw err;
    }

    if (!res.ok) {
        const errorText = await res.text().catch(() => '');
        throw new Error(`Ollama error: ${res.status} ${errorText}`);
    }

    const data = (await res.json()) as OllamaChatResponse;
    const content = data?.message?.content;
    if (!content) {
        throw new Error('Ollama returned empty message');
    }
    return content;
}

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

        // 3. Call Ollama
        const ollamaModel = process.env.OLLAMA_CHAT_MODEL || 'gemma3:1b';
        const reply = await chatWithOllama({
            model: ollamaModel,
            system: systemPromptWithContext,
            user: message,
        });

        return NextResponse.json({
            reply,
            retrieved_context: relevantChunks // For debugging/display
        });

    } catch (error: any) {
        console.error('Chat API Error:', error);
        return NextResponse.json(
            { error: error?.message || 'Unknown error' },
            { status: 500 }
        );
    }
}
