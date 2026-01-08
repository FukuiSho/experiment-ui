import { NextResponse } from 'next/server';
import fs from 'node:fs';
import path from 'node:path';

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

export async function GET() {
    const baseUrl = getCloneAIBaseUrl().replace(/\/$/, '');
    const url = `${baseUrl}/health`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    try {
        const res = await fetch(url, {
            method: 'GET',
            signal: controller.signal,
            cache: 'no-store',
        });

        if (!res.ok) {
            const text = await res.text().catch(() => '');
            return NextResponse.json(
                { ok: false, status: res.status, error: text },
                { status: 502 }
            );
        }

        const data = await res.json().catch(() => ({}));
        return NextResponse.json({ ok: true, cloneai: data });
    } catch (error: any) {
        if (error?.name === 'AbortError') {
            return NextResponse.json({ ok: false, error: 'timeout' }, { status: 504 });
        }
        return NextResponse.json(
            { ok: false, error: error?.message || 'Unknown error' },
            { status: 502 }
        );
    } finally {
        clearTimeout(timeoutId);
    }
}
