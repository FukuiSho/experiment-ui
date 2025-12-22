'use client';

import { useState } from 'react';

export default function RagTestPage() {
    const [ingestStatus, setIngestStatus] = useState<string | null>(null);
    const [chatInput, setChatInput] = useState('');
    const [chatResponse, setChatResponse] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const runIngest = async () => {
        setLoading(true);
        setIngestStatus('Ingesting...');
        try {
            const res = await fetch('/api/rag/ingest', { method: 'POST' });
            const json = await res.json();
            setIngestStatus(JSON.stringify(json, null, 2));
        } catch (e: any) {
            setIngestStatus('Error: ' + e.message);
        } finally {
            setLoading(false);
        }
    };

    const sendChat = async () => {
        if (!chatInput) return;
        setLoading(true);
        setChatResponse(null);
        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: chatInput }),
            });
            const json = await res.json();
            setChatResponse(json);
        } catch (e: any) {
            setChatResponse({ error: e.message });
        } finally {
            setLoading(false);
        }
    };

    const runUnitTest = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/test/rag-unit');
            const json = await res.json();
            alert(JSON.stringify(json, null, 2));
        } catch (e: any) {
            alert('Test Failed: ' + e.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 p-8">
            <div className="max-w-3xl mx-auto space-y-8">

                {/* Unit Test Section */}
                <div className="bg-white p-6 rounded-xl shadow-sm">
                    <h2 className="text-xl font-bold mb-4">1. Unit Test (TDD)</h2>
                    <p className="text-sm text-gray-600 mb-4">
                        Verify RAG engine logic (Embedding generation & Cosine Similarity).
                    </p>
                    <button
                        onClick={runUnitTest}
                        disabled={loading}
                        className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 disabled:opacity-50"
                    >
                        Run Unit Test
                    </button>
                </div>

                {/* Ingestion Section */}
                <div className="bg-white p-6 rounded-xl shadow-sm">
                    <h2 className="text-xl font-bold mb-4">2. Ingestion (Build Index)</h2>
                    <p className="text-sm text-gray-600 mb-4">
                        Reads <code>src/data/limitless-knowledge.md</code> and creates vector embeddings.
                    </p>
                    <button
                        onClick={runIngest}
                        disabled={loading}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                        {loading ? 'Processing...' : 'Run Ingestion'}
                    </button>
                    {ingestStatus && (
                        <pre className="mt-4 p-4 bg-gray-900 text-green-400 rounded text-xs overflow-auto">
                            {ingestStatus}
                        </pre>
                    )}
                </div>

                {/* Chat Section */}
                <div className="bg-white p-6 rounded-xl shadow-sm">
                    <h2 className="text-xl font-bold mb-4">3. Chat Verification</h2>
                    <div className="flex gap-2 mb-4">
                        <input
                            type="text"
                            value={chatInput}
                            onChange={(e) => setChatInput(e.target.value)}
                            className="flex-1 border p-2 rounded"
                            placeholder="Ask something about your logs..."
                        />
                        <button
                            onClick={sendChat}
                            disabled={loading}
                            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
                        >
                            Send
                        </button>
                    </div>

                    {chatResponse && (
                        <div className="space-y-4">
                            <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                                <p className="font-bold text-blue-800 mb-2">AI Response:</p>
                                <p className="text-gray-800 whitespace-pre-wrap">{chatResponse.reply}</p>
                            </div>

                            {chatResponse.retrieved_context && (
                                <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                                    <p className="font-bold text-gray-600 mb-2 text-xs uppercase">Retrieved Context (RAG):</p>
                                    <pre className="text-xs text-gray-500 whitespace-pre-wrap overflow-auto max-h-40">
                                        {JSON.stringify(chatResponse.retrieved_context, null, 2)}
                                    </pre>
                                </div>
                            )}
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
}
