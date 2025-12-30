export type ExperimentPhase =
    | 'CONSENT'
    | 'INSTRUCTION'
    | 'SESSION_FREE_CHAT'
    | 'SESSION_KNOWLEDGE_PROBE'
    | 'SESSION_MORAL_CHOICE'
    | 'SESSION_STYLISTIC'
    | 'EVALUATION'
    | 'DEBRIEFING';

export type Condition = 'G' | 'P'; // Generic | Personalized

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
}

export interface ExperimentData {
    condition: Condition;
    startTime: number;
    endTime?: number;
    sessions: {
        [key in ExperimentPhase]?: {
            messages: Message[];
            startTime?: number;
            endTime?: number;
            duration: number;
        };
    };
    evaluation?: {
        identity: number; // 1-7
        naturalness: number; // 1-7
        offensiveness: number; // 1-7
        comments?: string;
    };
}

export const EXPERIMENT_PHASES: ExperimentPhase[] = [
    'CONSENT',
    'INSTRUCTION',
    'SESSION_FREE_CHAT',
    'SESSION_KNOWLEDGE_PROBE',
    'SESSION_MORAL_CHOICE',
    'SESSION_STYLISTIC',
    'EVALUATION',
    'DEBRIEFING'
];

export const SESSION_TITLES: Record<ExperimentPhase, string> = {
    'CONSENT': '実験への参加同意',
    'INSTRUCTION': '実験の説明',
    'SESSION_FREE_CHAT': 'セッション1: 雑談',
    'SESSION_KNOWLEDGE_PROBE': 'セッション2: 記憶の確認',
    'SESSION_MORAL_CHOICE': 'セッション3: 価値観の共有',
    'SESSION_STYLISTIC': 'セッション4: 創作・大喜利',
    'EVALUATION': '評価アンケート',
    'DEBRIEFING': '実験のまとめ',
};
