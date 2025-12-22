import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
    const apiKey = request.headers.get('X-Limitless-Key');

    if (!apiKey) {
        return NextResponse.json({ error: 'API Key is required' }, { status: 400 });
    }

    // Setup 30 second timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    try {
        console.log('Fetching from Limitless API...');

        let response;
        let lastError;

        // Retry logic: 3 attempts
        for (let i = 0; i < 3; i++) {
            try {
                // Using X-API-Key as per correct documentation
                response = await fetch('https://api.limitless.ai/v1/lifelogs?limit=5', {
                    headers: {
                        'X-API-Key': apiKey,
                    },
                    signal: controller.signal,
                    cache: 'no-store', // Disable cache
                });

                if (response.ok) break; // Success

                // If server error (5xx), retry. If client error (4xx), don't retry.
                if (response.status < 500) break;

            } catch (e) {
                console.log(`Attempt ${i + 1} failed:`, e);
                lastError = e;
                // Wait 1 second before retrying
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }

        clearTimeout(timeoutId);

        if (!response) {
            throw lastError || new Error('Failed to connect after 3 attempts');
        }

        console.log('Limitless API Response Status:', response.status);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Limitless API Error Body:', errorText);
            return NextResponse.json({ error: `Limitless API Error: ${response.status} ${errorText}` }, { status: response.status });
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error: any) {
        clearTimeout(timeoutId);
        console.error('Limitless API Proxy Error:', error);

        if (error.name === 'AbortError') {
            return NextResponse.json({ error: 'Request timed out after 30 seconds' }, { status: 504 });
        }

        return NextResponse.json({ error: `Internal Server Error: ${error.message}` }, { status: 500 });
    }
}
