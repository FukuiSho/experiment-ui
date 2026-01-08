'use client';

import React from 'react';
import { ChatInterface } from '@/components/ChatInterface';
import { Message } from '@/lib/experiment-state';

export default function CloneAITestPage() {
    const [messages, setMessages] = React.useState<Message[]>([
        {
            id: 'system-init',
            role: 'assistant',
            content: 'cloneAI（人格エージェント）テストを開始します。',
            timestamp: Date.now(),
        },
    ]);
    const [isTyping, setIsTyping] = React.useState(false);

    const handleSendMessage = React.useCallback(async (content: string) => {
        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content,
            timestamp: Date.now(),
        };

        setMessages((prev) => [...prev, userMsg]);
        setIsTyping(true);

        try {
            const res = await fetch('/api/cloneai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: content, session_id: 'default' }),
            });

            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
                const errMsg = data?.error || 'API Error';
                throw new Error(errMsg);
            }

            const replyText = String(data?.reply || '');
            const assistantMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: replyText,
                timestamp: Date.now(),
            };

            setMessages((prev) => [...prev, assistantMsg]);
        } catch (error: any) {
            const assistantMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: `エラー: ${error?.message || 'Unknown error'}`,
                timestamp: Date.now(),
            };
            setMessages((prev) => [...prev, assistantMsg]);
        } finally {
            setIsTyping(false);
        }
    }, []);

    return (
        <main className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-3xl mx-auto space-y-4">
                <h1 className="text-2xl font-bold text-gray-800">cloneAI テスト</h1>
                <p className="text-sm text-gray-600">
                    このページは、同梱した cloneAI（Python FastAPI）へ疎通確認するための最小UIです。
                </p>
                <div className="h-[70vh]">
                    <ChatInterface
                        messages={messages}
                        onSendMessage={handleSendMessage}
                        isTyping={isTyping}
                    />
                </div>
            </div>
        </main>
    );
}
