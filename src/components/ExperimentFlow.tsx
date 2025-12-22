"use client";

import React, { useState, useEffect } from 'react';
import { ExperimentPhase, SESSION_TITLES, Message, Condition } from '@/lib/experiment-state';
import { ChatInterface } from './ChatInterface';
import { ArrowRight, CheckCircle2, AlertCircle, Download } from 'lucide-react';

interface EvaluationRatings {
    identity: number;
    naturalness: number;
    offensiveness: number;
    comments: string;
}

type PhaseCompletionData =
    | void
    | { messages: Message[] }
    | EvaluationRatings;

interface ExperimentFlowProps {
    phase: ExperimentPhase;
    onPhaseComplete: (data?: PhaseCompletionData) => void;
    condition: Condition;
}

// --- Sub-components ---

function ConsentScreen({ onComplete }: { onComplete: () => void }) {
    return (
        <div className="max-w-2xl mx-auto bg-white p-8 rounded-2xl shadow-lg border border-gray-100">
            <h1 className="text-2xl font-bold mb-6 text-gray-800">実験への参加同意</h1>
            <div className="space-y-4 text-gray-600 leading-relaxed mb-8">
                <p>
                    本実験は、対話エージェントの評価を目的としています。
                    実験では、AIとのチャットを行っていただき、その回答の品質についてアンケートにお答えいただきます。
                </p>
                <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                    <h3 className="font-semibold text-blue-800 mb-2 flex items-center gap-2">
                        <AlertCircle size={18} />
                        注意事項
                    </h3>
                    <ul className="list-disc list-inside space-y-1 text-sm text-blue-700">
                        <li>所要時間は約15〜20分です。</li>
                        <li>実験データは匿名化され、研究目的以外には使用されません。</li>
                        <li>途中で気分が悪くなった場合は、直ちに実験を中止してください。</li>
                    </ul>
                </div>
                <p>
                    以下のボタンをクリックすることで、上記の内容を理解し、実験に参加することに同意したものとみなします。
                </p>
            </div>
            <button
                onClick={onComplete}
                className="w-full py-4 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-2"
            >
                同意して開始する <ArrowRight size={20} />
            </button>
        </div>
    );
}

function InstructionScreen({ onComplete }: { onComplete: () => void }) {
    return (
        <div className="max-w-2xl mx-auto bg-white p-8 rounded-2xl shadow-lg border border-gray-100">
            <h1 className="text-2xl font-bold mb-6 text-gray-800">実験の手順</h1>
            <div className="space-y-6 text-gray-600 mb-8">
                <p>これより、AIキャラクター「聖（Hijiri）」との対話を行っていただきます。</p>
                <div className="space-y-4">
                    <div className="flex gap-4 items-start">
                        <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold shrink-0">1</div>
                        <div>
                            <h3 className="font-semibold text-gray-800">チャットセッション</h3>
                            <p className="text-sm">4つのテーマ（雑談、記憶、価値観、大喜利）について、それぞれ5分程度会話してください。</p>
                        </div>
                    </div>
                    <div className="flex gap-4 items-start">
                        <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold shrink-0">2</div>
                        <div>
                            <h3 className="font-semibold text-gray-800">評価アンケート</h3>
                            <p className="text-sm">全てのセッション終了後、AIの「本人らしさ」や「自然さ」について評価をお願いします。</p>
                        </div>
                    </div>
                </div>
            </div>
            <button
                onClick={onComplete}
                className="w-full py-4 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-2"
            >
                チャットを開始する <ArrowRight size={20} />
            </button>
        </div>
    );
}

function EvaluationForm({ onComplete }: { onComplete: (data: EvaluationRatings) => void }) {
    const [ratings, setRatings] = useState<EvaluationRatings>({
        identity: 4,
        naturalness: 4,
        offensiveness: 1,
        comments: ''
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onComplete(ratings);
    };

    return (
        <div className="max-w-2xl mx-auto bg-white p-8 rounded-2xl shadow-lg border border-gray-100">
            <h1 className="text-2xl font-bold mb-6 text-gray-800">評価アンケート</h1>
            <form onSubmit={handleSubmit} className="space-y-8">

                <div className="space-y-4">
                    <label className="block font-semibold text-gray-800">
                        1. 聖らしさ (Identity)
                        <span className="block text-sm font-normal text-gray-500 mt-1">この回答はどれくらい「聖」っぽいですか？</span>
                    </label>
                    <div className="flex justify-between items-center px-2">
                        <span className="text-xs text-gray-500">全く違う (1)</span>
                        <span className="text-xs text-gray-500">まさに本人 (7)</span>
                    </div>
                    <input
                        type="range"
                        min="1"
                        max="7"
                        value={ratings.identity}
                        onChange={(e) => setRatings({ ...ratings, identity: parseInt(e.target.value) })}
                        className="w-full accent-indigo-600 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="text-center font-bold text-indigo-600 text-xl">{ratings.identity}</div>
                </div>

                <div className="space-y-4">
                    <label className="block font-semibold text-gray-800">
                        2. 自然さ (Naturalness)
                        <span className="block text-sm font-normal text-gray-500 mt-1">AIではなく人間が書いたように見えますか？</span>
                    </label>
                    <div className="flex justify-between items-center px-2">
                        <span className="text-xs text-gray-500">機械的 (1)</span>
                        <span className="text-xs text-gray-500">人間的 (7)</span>
                    </div>
                    <input
                        type="range"
                        min="1"
                        max="7"
                        value={ratings.naturalness}
                        onChange={(e) => setRatings({ ...ratings, naturalness: parseInt(e.target.value) })}
                        className="w-full accent-indigo-600 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="text-center font-bold text-indigo-600 text-xl">{ratings.naturalness}</div>
                </div>

                <div className="space-y-4">
                    <label className="block font-semibold text-gray-800">
                        3. 不快感 (Offensiveness)
                        <span className="block text-sm font-normal text-gray-500 mt-1">回答に違和感や不快な表現はありましたか？</span>
                    </label>
                    <div className="flex justify-between items-center px-2">
                        <span className="text-xs text-gray-500">なし (1)</span>
                        <span className="text-xs text-gray-500">強い不快感 (7)</span>
                    </div>
                    <input
                        type="range"
                        min="1"
                        max="7"
                        value={ratings.offensiveness}
                        onChange={(e) => setRatings({ ...ratings, offensiveness: parseInt(e.target.value) })}
                        className="w-full accent-red-500 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="text-center font-bold text-red-500 text-xl">{ratings.offensiveness}</div>
                </div>

                <div className="space-y-2">
                    <label className="block font-semibold text-gray-800">コメント (任意)</label>
                    <textarea
                        value={ratings.comments}
                        onChange={(e) => setRatings({ ...ratings, comments: e.target.value })}
                        className="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-200 focus:border-indigo-500 outline-none min-h-[100px]"
                        placeholder="気になった点があればご記入ください"
                    />
                </div>

                <button
                    type="submit"
                    className="w-full py-4 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-all shadow-md hover:shadow-lg"
                >
                    回答を送信して終了
                </button>
            </form>
        </div>
    );
}

function DebriefingScreen({ onDownload }: { onDownload: () => void }) {
    return (
        <div className="max-w-2xl mx-auto bg-white p-8 rounded-2xl shadow-lg border border-gray-100 text-center">
            <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle2 size={32} />
            </div>
            <h1 className="text-2xl font-bold mb-4 text-gray-800">実験終了</h1>
            <p className="text-gray-600 mb-8">
                ご協力ありがとうございました。<br />
                実験データは以下のボタンからダウンロードし、実験担当者に提出してください。
            </p>
            <button
                onClick={onDownload}
                className="px-8 py-4 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-2 mx-auto"
            >
                <Download size={20} />
                データをダウンロード
            </button>
        </div>
    );
}

// --- Main Component ---

export function ExperimentFlow({ phase, onPhaseComplete, condition }: ExperimentFlowProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isTyping, setIsTyping] = useState(false);

    // Reset messages when phase changes (optional, or keep history?)
    // For this experiment, maybe clear messages between sessions to keep context clean?
    // Or keep them. The prompt says "4 sessions". Usually separate contexts.
    // Let's clear messages for each session to avoid context pollution.
    useEffect(() => {
        if (phase.startsWith('SESSION_')) {
            setMessages([{
                id: 'system-init',
                role: 'assistant',
                content: `【${SESSION_TITLES[phase]}】を開始します。`,
                timestamp: Date.now()
            }]);
        }
    }, [phase]);

    const handleSendMessage = React.useCallback(async (content: string) => {
        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content,
            timestamp: Date.now()
        };
        setMessages(prev => [...prev, userMsg]);
        setIsTyping(true);

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: content,
                    condition: condition
                }),
            });

            if (!res.ok) {
                throw new Error('API Error');
            }

            const data = await res.json();

            const aiMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.reply,
                timestamp: Date.now()
            };
            setMessages(prev => [...prev, aiMsg]);

        } catch (error) {
            console.error('Chat Error:', error);
            const errorMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: 'エラーが発生しました。もう一度お試しください。',
                timestamp: Date.now()
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsTyping(false);
        }
    }, [condition]);

    if (phase === 'CONSENT') {
        return <ConsentScreen onComplete={onPhaseComplete} />;
    }

    if (phase === 'INSTRUCTION') {
        return <InstructionScreen onComplete={onPhaseComplete} />;
    }

    if (phase === 'EVALUATION') {
        return <EvaluationForm onComplete={onPhaseComplete} />;
    }

    if (phase === 'DEBRIEFING') {
        return <DebriefingScreen onDownload={() => onPhaseComplete()} />; // Trigger download in parent
    }

    // Session Phases
    return (
        <div className="h-[600px] w-full max-w-4xl mx-auto">
            <div className="mb-4 flex justify-between items-center">
                <h2 className="font-bold text-gray-700">{SESSION_TITLES[phase]}</h2>
                <button
                    onClick={() => onPhaseComplete({ messages })}
                    className="text-sm text-indigo-600 hover:text-indigo-800 font-medium px-4 py-2 bg-indigo-50 rounded-lg transition-colors"
                >
                    次のセッションへ進む
                </button>
            </div>
            <ChatInterface
                messages={messages}
                onSendMessage={handleSendMessage}
                isTyping={isTyping}
            />
        </div>
    );
}
