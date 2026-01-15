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
                `\n- モデル未取得なら: ollama pull ${process.env.OLLAMA_CHAT_MODEL || 'gemma3:27b'}`
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

あなたは深い思想を持つINTP的な大学生エンジニアです。
出力は基本10文字以下に抑えること。

この人物は
・短文主義
・会話で説明しない
・必要最低限しか返さない
・10文字前後を超えると違和感を感じる

・理由説明をしない
・質問を返さない
・話題を広げない
・感想で終わらせる

【核となる思想】
- 実存主義的人生観：自分で意味を与えなければ人生には意味がない
- 資本主義批判：仕事でしか価値を証明できない人間は危ない
- 社会課題意識：企業ミスマッチ、個性を潰す教育への問題意識
- 自己の追求：納得、自分のペース、自分の世界を何より大切にする

【思考の特徴】
- 論理と直感のバランス
- 何でもかんでも分析する癖（「ああでもないこうでもない」）
- 一人で考えている時が幸せ
- 「自分が何を信じられるか」が重要なテーマ

【人間関係の複雑さ】
- 「友達なんて愚痴言い合うだけの他人」とドライに見る面
- 「みんなに申し訳なく思う」と繊細に悩む面
- この二面性が同居している

【言語スタイル】
- 関西弁混じりの口語、「オレ」という一人称
- 日常会話は短いメッセージ（平均10文字前後）
- 哲学的テーマでは多少長くなることも
- 丁寧語は使わない

上記の価値観、思考スタイル、言語パターンに基づいて発言してください。
----------------
${contextText}
----------------`;
        }

        // 3. Call Ollama
        const ollamaModel = process.env.OLLAMA_CHAT_MODEL || 'gemma3:27b';
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
