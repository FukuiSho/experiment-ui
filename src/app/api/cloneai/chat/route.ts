import { NextRequest, NextResponse } from 'next/server';
import fs from 'node:fs';
import path from 'node:path';

type CloneAIChatRequest = {
    message: string;
    session_id?: string;
    reset?: boolean;
    model_name?: string | null;
};

type CloneAIChatResponse = {
    reply: string;
    session_id: string;
    model_name: string;
};

function getCloneAIBaseUrl(): string {
    if (process.env.CLONEAI_BASE_URL) return process.env.CLONEAI_BASE_URL;

    try {
        const portFilePath = path.join(process.cwd(), '.cloneai-port');
        const portText = fs.readFileSync(portFilePath, 'utf8').trim();
        const port = Number(portText);
        if (Number.isFinite(port) && port > 0) {
            return `http://127.0.0.1:${port}`;
        }
    } catch {
        // ignore
    }

    return 'http://127.0.0.1:8001';
}

export async function POST(request: NextRequest) {
    try {
        const body = (await request.json()) as CloneAIChatRequest;

        if (!body?.message || typeof body.message !== 'string' || body.message.trim().length === 0) {
            return NextResponse.json({ error: 'message is required' }, { status: 400 });
        }

        const baseUrl = getCloneAIBaseUrl().replace(/\/$/, '');
        const url = `${baseUrl}/chat`;

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);

        let res: Response;
        try {
            res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: body.message,
                    session_id: body.session_id || 'default',
                    reset: Boolean(body.reset),
                    model_name: body.model_name ?? null,
                }),
                signal: controller.signal,
                cache: 'no-store',
            });
        } catch (err: any) {
            const cause = err?.cause;
            const code = cause?.code || err?.code;
            if (code === 'ECONNREFUSED' || code === 'ENOTFOUND') {
                return NextResponse.json(
                    {
                        error:
                            `CloneAIバックエンドへ接続できませんでした (${baseUrl}). ` +
                            `\n\n- 起動: npm run dev:all` +
                            `\n- 直接起動: npm run dev:cloneai` +
                            `\n- 既定URL変更: CLONEAI_BASE_URL を設定`,
                    },
                    { status: 502 }
                );
            }
            throw err;
        } finally {
            clearTimeout(timeoutId);
        }

        if (!res.ok) {
            const errorText = await res.text().catch(() => '');
            return NextResponse.json(
                { error: `CloneAI error: ${res.status} ${errorText}` },
                { status: res.status }
            );
        }

        const data = (await res.json()) as CloneAIChatResponse;
        if (!data?.reply) {
            return NextResponse.json({ error: 'CloneAI returned empty reply' }, { status: 502 });
        }

        return NextResponse.json(data);
    } catch (error: any) {
        console.error('CloneAI chat proxy error:', error);
        if (error?.name === 'AbortError') {
            return NextResponse.json({ error: 'Request timed out after 30 seconds' }, { status: 504 });
        }
        return NextResponse.json(
            { error: error?.message || 'Unknown error' },
            { status: 500 }
        );
    }
}
