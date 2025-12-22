'use client';

import { useState } from 'react';

import { convertLimitlessToMarkdown } from '@/lib/limitless-converter';

export default function LimitlessTestPage() {
    const [apiKey, setApiKey] = useState('');
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [viewMode, setViewMode] = useState<'json' | 'markdown'>('markdown');

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        setData(null);

        // Sanitize API key: remove whitespace and ensure no non-ASCII characters
        const sanitizedKey = apiKey.trim();

        // Check for non-ASCII characters which cause the "String contains non ISO-8859-1 code point" error
        if (/[^\x00-\x7F]/.test(sanitizedKey)) {
            setError('API Key contains invalid characters. Please check for full-width characters or hidden symbols.');
            setLoading(false);
            return;
        }

        try {
            const res = await fetch('/api/limitless', {
                headers: {
                    'X-Limitless-Key': sanitizedKey,
                },
            });

            const json = await res.json();

            if (!res.ok) {
                throw new Error(json.error || 'Failed to fetch data');
            }

            setData(json);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-md overflow-hidden p-6">
                <h1 className="text-2xl font-bold mb-4 text-gray-800">Limitless API Test</h1>

                <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        API Key (X-API-Key)
                    </label>
                    <div className="flex gap-2">
                        <input
                            type="password"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            className="flex-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            placeholder="Enter your Limitless API Key"
                        />
                        <button
                            onClick={fetchData}
                            disabled={loading || !apiKey}
                            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                        >
                            {loading ? 'Fetching...' : 'Fetch Data'}
                        </button>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                        Your key is sent securely to the server and not stored.
                    </p>
                </div>

                {error && (
                    <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
                        <p className="text-red-700">{error}</p>
                    </div>
                )}

                {data && (
                    <div className="mt-6">
                        <div className="flex justify-between items-center mb-2">
                            <h2 className="text-xl font-semibold text-gray-800">Response Data</h2>
                            <div className="flex gap-2">
                                <button
                                    onClick={async () => {
                                        const markdown = convertLimitlessToMarkdown(data);
                                        try {
                                            const res = await fetch('/api/save-knowledge', {
                                                method: 'POST',
                                                headers: { 'Content-Type': 'application/json' },
                                                body: JSON.stringify({ content: markdown })
                                            });
                                            if (res.ok) {
                                                alert('Saved successfully to src/data/limitless-knowledge.md');
                                            } else {
                                                alert('Failed to save file');
                                            }
                                        } catch (e) {
                                            alert('Error saving file');
                                        }
                                    }}
                                    className="px-3 py-1 text-sm rounded-md bg-green-600 text-white hover:bg-green-700 transition-colors"
                                >
                                    Save to File
                                </button>
                                <div className="flex gap-2 bg-gray-100 p-1 rounded-lg">
                                    <button
                                        onClick={() => setViewMode('markdown')}
                                        className={`px-3 py-1 text-sm rounded-md transition-colors ${viewMode === 'markdown'
                                            ? 'bg-white text-blue-600 shadow-sm'
                                            : 'text-gray-600 hover:text-gray-900'
                                            }`}
                                    >
                                        Markdown
                                    </button>
                                    <button
                                        onClick={() => setViewMode('json')}
                                        className={`px-3 py-1 text-sm rounded-md transition-colors ${viewMode === 'json'
                                            ? 'bg-white text-blue-600 shadow-sm'
                                            : 'text-gray-600 hover:text-gray-900'
                                            }`}
                                    >
                                        JSON
                                    </button>
                                </div>
                            </div>
                        </div>

                        {viewMode === 'markdown' ? (
                            <div className="bg-white border border-gray-200 p-6 rounded-md overflow-auto max-h-[600px] prose prose-sm max-w-none">
                                <pre className="whitespace-pre-wrap font-sans text-gray-800">
                                    {convertLimitlessToMarkdown(data)}
                                </pre>
                            </div>
                        ) : (
                            <div className="bg-gray-900 text-gray-100 p-4 rounded-md overflow-auto max-h-[600px]">
                                <pre className="font-mono text-sm">
                                    {JSON.stringify(data, null, 2)}
                                </pre>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
