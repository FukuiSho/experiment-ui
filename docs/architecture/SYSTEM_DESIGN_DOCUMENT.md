# 卒業研究システム設計ドキュメント

## 📋 目次

1. [プロジェクト概要](#1-プロジェクト概要)
2. [システムアーキテクチャ](#2-システムアーキテクチャ)
3. [cloneAI モジュール](#3-cloneai-モジュール)
4. [experiment-ui モジュール](#4-experiment-ui-モジュール)
5. [データフロー](#5-データフロー)
6. [API仕様](#6-api仕様)
7. [データモデル](#7-データモデル)
8. [設定・パラメーター](#8-設定パラメーター)
9. [テスト戦略](#9-テスト戦略)
10. [デプロイメント](#10-デプロイメント)
11. [校閲・検証結果](#11-校閲検証結果)

---

## 1. プロジェクト概要

### 1.1 研究目的

本システムは、**個人のクローンAIエージェント**を構築し、その「本人らしさ」を評価する実験プラットフォームです。

### 1.2 研究仮説

パーソナライズされたAIエージェント（Condition: P）は、汎用的なAIエージェント（Condition: G）と比較して、以下の点で優れた評価を得られる：
- **Identity（本人らしさ）**: より「本人らしい」と認識される
- **Naturalness（自然さ）**: より人間的な応答と感じられる
- **Offensiveness（不快感）**: 違和感や不快感が少ない

### 1.3 システム構成

```
卒研/
├── cloneAI/          # バックエンド: クローンAIエージェント実装
├── experiment-ui/    # フロントエンド: 実験用Webインターフェース
└── SYSTEM_DESIGN_DOCUMENT.md  # 本ドキュメント
```

### 1.4 技術スタック

| レイヤー | 技術 |
|---------|------|
| フロントエンド | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| バックエンド | Python 3.x |
| LLM | Ollama (gemma3:27b) |
| 外部API | Limitless Developer API (ライフログ取得) |
| テスト | pytest, requests-mock |

---

## 2. システムアーキテクチャ

### 2.1 全体アーキテクチャ図

```
┌─────────────────────────────────────────────────────────────────┐
│                        実験参加者                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    experiment-ui (Next.js)                      │
│  ┌───────────────┐  ┌──────────────┐  ┌───────────────────┐   │
│  │ ExperimentFlow │  │ChatInterface │  │ Evaluation Form   │   │
│  └───────────────┘  └──────────────┘  └───────────────────┘   │
│           │                │                    │               │
│           └────────────────┼────────────────────┘               │
│                            ▼                                    │
│              ┌─────────────────────────┐                        │
│              │   API Route (/api/*)    │                        │
│              └─────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      cloneAI (Python)                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │ AIPersonaAgent  │  │  PersonaTemplate │  │  MemoryManager │  │
│  └─────────────────┘  └─────────────────┘  └────────────────┘  │
│           │                    │                    │           │
│           └────────────────────┼────────────────────┘           │
│                                ▼                                │
│              ┌─────────────────────────────┐                    │
│              │        OllamaClient        │                    │
│              └─────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      外部サービス                                │
│  ┌───────────────┐  ┌──────────────┐  ┌───────────────────┐   │
│  │ Ollama Server │                      │ Limitless API     │   │
│  │ (localhost)   │                      │ (Lifelog)         │   │
│  └───────────────┘                      └───────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 コンポーネント間の責務

| コンポーネント | 責務 |
|--------------|------|
| experiment-ui | 実験フローの制御、UI提供、データ収集 |
| cloneAI | ペルソナベースの応答生成、思考プロセスの可視化 |
| Limitless API | ユーザーのライフログデータ取得（将来的なパーソナライズ用） |

---

## 3. cloneAI モジュール

### 3.1 ディレクトリ構造

```
cloneAI/
├── clone_agentAI.py      # メインエージェント実装
├── chat_param_test.py    # AIパラメーターチューニングGUIツール
├── 福井聖AIパラメーター.json  # 最適化済みパラメーター
├── requirements.txt      # Python依存関係
├── README.md            # 使用方法
├── src/
│   └── limitless_api/    # Limitless API クライアント
│       ├── __init__.py
│       └── lifelog_client.py
└── tests/
    ├── conftest.py
    ├── test_lifelog_client.py
    └── data/
        └── lifelogs_sample.json
```

### 3.2 主要クラス詳細

#### 3.2.1 ThoughtFlow クラス

**目的**: AIエージェントの思考プロセスを記録・可視化

```python
class ThoughtFlow:
    """思考フローを記録するクラス"""
    
    def __init__(self):
        self.thoughts: List[Dict[str, str]] = []
    
    def add_thought(self, thought: str, category: str = "general") -> None
    def get_thoughts(self) -> List[Dict[str, str]]
    def get_thought_summary(self) -> str
```

**カテゴリ一覧**:
| カテゴリ | 説明 |
|---------|------|
| `input` | ユーザー入力の受信 |
| `thinking` | 思考・分析プロセス |
| `process` | 処理・プロンプト構築 |
| `api` | LLM APIとの通信 |
| `error` | エラー発生 |

#### 3.2.2 LLMClient 抽象基底クラス

```python
class LLMClient:
    """LLMモデルと通信するための抽象基底クラス"""
    def generate(self, prompt: str) -> str:
        raise NotImplementedError
```

#### 3.2.3 OllamaClient クラス

**目的**: Ollamaローカルサーバーとの通信

```python
class OllamaClient(LLMClient):
    def __init__(self, 
                 model_name: str = "gemma3:27b", 
                 base_url: str = "http://localhost:11434/api"):
        self.model_name = model_name
        self.base_url = base_url
        self.simulation_mode = False
    
    def generate(self, prompt: str) -> str
    def _simulate_generation(self, prompt: str) -> str  # テスト用シミュレーション
    def _real_generate(self, prompt: str) -> str        # 実際のAPI呼び出し
    def set_simulation_mode(self, enabled: bool) -> None
```

**シミュレーションモード**: Ollamaサーバーが利用不可の場合、事前定義された応答を返す

#### 3.2.4 PersonaTemplate クラス

**目的**: 特定人物のペルソナを定義

```python
class PersonaTemplate:
    def __init__(self,
                 name: str,
                 description: str,
                 traits: Dict[str, Any] = None,
                 background: str = None,
                 personality: str = None,
                 speech_style: str = None,
                 knowledge_areas: List[str] = None,
                 values: List[str] = None):
        ...
    
    def to_prompt(self) -> str  # ペルソナをLLMプロンプトに変換
```

**ペルソナ属性**:
| 属性 | 説明 | 例 |
|-----|------|-----|
| `name` | 名前 | "福井聖" |
| `description` | 基本説明 | "21歳の日本人大学生..." |
| `traits` | 個人的特徴（辞書） | {"口癖": "たしかに..."} |
| `background` | 経歴・背景 | 年齢、居住地、学歴など |
| `personality` | 性格特性 | ENFP、ビッグファイブスコア |
| `speech_style` | 話し方の特徴 | "カジュアルでフレンドリー" |
| `knowledge_areas` | 専門知識分野 | ["Python", "機械学習"] |
| `values` | 価値観・信条 | ["好奇心が全て", "面白く生きる"] |

#### 3.2.5 MemoryManager クラス

**目的**: 会話履歴と重要情報の管理

```python
class MemoryManager:
    def __init__(self, max_history: int = 10):
        self.conversation_history: List[Dict[str, str]] = []
        self.key_facts: Dict[str, Any] = {}
        self.max_history = max_history
    
    def add_interaction(self, user_input: str, agent_response: str) -> None
    def add_fact(self, key: str, value: Any) -> None
    def get_history_as_text(self, num_entries: Optional[int] = None) -> str
```

**履歴エントリ構造**:
```python
{
    "user": "ユーザーの発言",
    "agent": "エージェントの応答",
    "timestamp": "2024-12-09 10:30:00"
}
```

#### 3.2.6 AIPersonaAgent クラス

**目的**: メインのAIエージェント - 全コンポーネントの統合

```python
class AIPersonaAgent:
    def __init__(self,
                 persona: PersonaTemplate,
                 model_name: str = "gemma3:27b",
                 simulation_mode: bool = False):
        self.persona = persona
        self.client = OllamaClient(model_name)
        self.thought_flow = ThoughtFlow()
        self.memory = MemoryManager()
    
    def process_input(self, user_input: str) -> str  # メイン処理
    def _build_prompt(self, user_input: str) -> str  # プロンプト構築
    def _analyze_response(self, response: str, user_input: str) -> str  # 応答分析
    def get_thought_process(self) -> List[Dict[str, str]]
    def get_thought_summary(self) -> str
    def reset_conversation(self) -> None
```

**処理フロー**:
1. ユーザー入力受信 → 思考記録
2. 入力意図分析（質問検出、挨拶検出）
3. ペルソナ情報 + 会話履歴からプロンプト構築
4. LLMへ問い合わせ
5. 応答分析・品質チェック
6. ペルソナの口癖を確率的に追加
7. 会話履歴更新
8. 最終応答返却

### 3.3 福井聖ペルソナ詳細

`create_yamada_taro_persona()` 関数で定義される詳細なペルソナ:

```python
PersonaTemplate(
    name="福井聖",
    description="21歳の日本人大学生。大阪国際工科専門職大学の3回生で、
                 情報工学科でAI戦略コースを専攻。",
    traits={
        "口癖": "たしかに...",
        "好きな言語": "Python、TypeScript",
        "趣味": "筋トレ、ゲーム、Youtube、自己啓発書を読むこと",
        # ... 50以上の詳細な特徴
    },
    background="""
        年齢：21歳
        性別：男
        居住地：大阪府八尾市
        職業：大学3年生
        学歴：大阪国際工科専門職大学工科学部情報工学科AI戦略コース
        家族構成：長男、5人家族
        # ...
    """,
    personality="""
        性格特性：ENFP
        ビックファイブ:
        - 外向性：57
        - 神経質：29
        - 開放性：68
        - 協調性：48
        - 誠実性：34
        # ...
    """,
    speech_style="カジュアルでフレンドリーな口調",
    knowledge_areas=["バックエンド開発", "データベース設計", "クラウドインフラ", "機械学習"],
    values=["好奇心が全て", "面白く生きること", "本質を重視"]
)
```

### 3.4 LLM呼び出し - Ollama

**目的**: ローカルLLM（Ollama）を使用してクローンAIの応答を生成する。

cloneAI側の実装は `clone_agentAI.py` の Ollama クライアントを使用します。

```python
ollama.chat(
    model="gemma3:27b",
    messages=[
        {"role": "system", "content": "あなたは福井聖です...（詳細なペルソナ）"},
        {"role": "user", "content": "ユーザー入力"},
    ],
)
```

### 3.5 chat_param_test.py - AIパラメーターチューナー

**目的**: ユーザーの好みからAIパラメーターを最適化するGUIツール

```python
class AIParameterTuner:
    """
    30問のアンケートに基づいてLLMパラメーターを計算
    
    計算されるパラメーター:
    - temperature (0.0-2.0): 創造性/ランダム性
    - top_p (0.0-1.0): トークン選択の多様性
    - presence_penalty (-2.0-2.0): 話題の繰り返し抑制
    - frequency_penalty (-2.0-2.0): 単語の繰り返し抑制
    - num_ctx (1024-4096): コンテキスト長
    - repeat_penalty (1.0-2.0): 繰り返し抑制
    - mirostat_mode (0-2): 文章複雑さ制御
    - max_tokens (500-2000): 応答最大長
    - jargon_level (1-5): 専門用語使用度
    - formality_level (1-5): フォーマル度
    - abstraction_level (1-5): 抽象/具体度
    """
```

**質問カテゴリ**:
1. 基本的な特性に関する質問 (Q1-3)
2. Temperature調整のための質問 (Q4-5)
3. 創造性と予測可能性に関する質問 (Q6-8)
4. 文脈理解の深さに関する質問 (Q9-10)
5. 繰り返しと一貫性に関する質問 (Q11-12)
6. 制御性と多様性のバランスに関する質問 (Q13-14)
7. Top_p調整のための質問 (Q15-16)
8. Presence/Frequency Penalty調整のための質問 (Q17-18)
9. Logit_bias調整のための質問 (Q19-21)
10. ユーザー特性把握のための質問 (Q22-27)
11. ユースケースに関する質問 (Q28-30)

### 3.6 Limitless API クライアント

#### 3.6.1 LifelogClient クラス

**目的**: Limitless APIからライフログを取得

```python
class LifelogClient:
    _PATH_LIFELOGS = "/v1/lifelogs"
    
    def __init__(self,
                 api_key: str,
                 base_url: str = "https://api.limitless.ai",
                 session: Optional[requests.Session] = None,
                 timeout: float = 30.0):
        ...
    
    def list_lifelogs(self, **params: Any) -> Tuple[List[LifelogEntry], Optional[str]]:
        """
        ページネーション付きでライフログを取得
        
        Parameters:
            limit: 取得件数 (1-10)
            date: ISO日付 (例: "2024-09-17")
            start: 開始時刻
            end: 終了時刻
            timezone: タイムゾーン (例: "Asia/Tokyo")
            cursor: ページネーションカーソル
        
        Returns:
            (entries, next_cursor): エントリリストと次ページカーソル
        
        Raises:
            RateLimitError: レート制限時 (429)
            ApiError: その他のAPIエラー
        """
```

#### 3.6.2 データモデル

```python
@dataclass
class LifelogEntry:
    id: str                    # 一意識別子
    title: str                 # エントリタイトル
    start_time: datetime       # 開始時刻
    end_time: datetime         # 終了時刻
    is_starred: bool           # スター付きフラグ
    updated_at: datetime       # 更新日時
    markdown: Optional[str]    # Markdown形式のサマリー
    contents: List[Dict]       # 構造化コンテンツ
```

#### 3.6.3 エラーハンドリング

```python
class ApiError(Exception):
    """基本APIエラー"""
    def __init__(self, message: str, status_code: int, payload: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

class RateLimitError(ApiError):
    """レート制限エラー（429）"""
    def __init__(self, message: str, status_code: int, 
                 retry_after: Optional[int] = None, payload: Optional[Dict] = None):
        super().__init__(message, status_code, payload)
        self.retry_after = retry_after  # 再試行までの秒数
```

#### 3.6.4 CLI インターフェース

```bash
# 基本使用
python -m limitless_api.lifelog_client --limit 5 --timezone Asia/Tokyo

# オプション
--api-key     APIキー（環境変数 LIMITLESS_API_KEY が既定）
--base-url    APIベースURL
--limit       取得件数 (1-10)
--date        ISO日付フィルター
--start       開始時刻フィルター
--end         終了時刻フィルター
--timezone    タイムゾーン
--cursor      ページネーションカーソル
```

---

## 4. experiment-ui モジュール

### 4.1 ディレクトリ構造

```
experiment-ui/
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.js
├── postcss.config.mjs
├── eslint.config.mjs
├── public/
└── src/
    ├── app/
    │   ├── globals.css
    │   ├── layout.tsx
    │   ├── page.tsx              # メインページ
    │   ├── api/
    │   │   └── limitless/
    │   │       └── route.ts      # Limitless APIプロキシ
    │   └── limitless-test/
    │       └── page.tsx          # APIテストページ
    ├── components/
    │   ├── ChatInterface.tsx     # チャットUI
    │   └── ExperimentFlow.tsx    # 実験フロー制御
    └── lib/
        ├── experiment-state.ts   # 状態定義
        └── utils.ts              # ユーティリティ
```

### 4.2 状態管理 (experiment-state.ts)

#### 4.2.1 実験フェーズ

```typescript
export type ExperimentPhase =
    | 'CONSENT'              // 同意画面
    | 'INSTRUCTION'          // 説明画面
    | 'SESSION_FREE_CHAT'    // セッション1: 雑談
    | 'SESSION_KNOWLEDGE_PROBE'  // セッション2: 記憶の確認
    | 'SESSION_MORAL_CHOICE'     // セッション3: 価値観の共有
    | 'SESSION_STYLISTIC'        // セッション4: 創作・大喜利
    | 'EVALUATION'           // 評価アンケート
    | 'DEBRIEFING';          // 終了・データダウンロード
```

#### 4.2.2 実験条件

```typescript
export type Condition = 'G' | 'P';
// G = Generic (汎用AI)
// P = Personalized (パーソナライズAI)
```

#### 4.2.3 メッセージ型

```typescript
export interface Message {
    id: string;           // 一意識別子
    role: 'user' | 'assistant';
    content: string;      // メッセージ内容
    timestamp: number;    // Unixタイムスタンプ
}
```

#### 4.2.4 実験データ型

```typescript
export interface ExperimentData {
    condition: Condition;     // 実験条件 (G/P)
    startTime: number;        // 開始時刻
    endTime?: number;         // 終了時刻
    sessions: {
        [key in ExperimentPhase]?: {
            messages: Message[];  // 会話履歴
            duration: number;     // セッション所要時間
        };
    };
    evaluation?: {
        identity: number;     // 本人らしさ (1-7)
        naturalness: number;  // 自然さ (1-7)
        offensiveness: number; // 不快感 (1-7)
        comments?: string;    // 自由記述コメント
    };
}
```

### 4.3 メインページ (page.tsx)

**責務**: 実験全体の状態管理とフロー制御

```typescript
export default function Home() {
    const [phase, setPhase] = useState<ExperimentPhase>('CONSENT');
    const [data, setData] = useState<ExperimentData>({
        condition: 'G',
        startTime: Date.now(),
        sessions: {}
    });

    useEffect(() => {
        // クライアントサイドで条件をランダム割り当て
        const condition: Condition = Math.random() > 0.5 ? 'P' : 'G';
        setData(prev => ({ ...prev, condition }));
    }, []);

    const handlePhaseComplete = (phaseData?: any) => {
        // フェーズデータを保存し、次のフェーズへ遷移
        // DEBRIEFING完了時はデータをJSONでダウンロード
    };

    const handleDownload = () => {
        // 実験データをJSONファイルとしてダウンロード
        // ファイル名: experiment_data_{condition}_{timestamp}.json
    };
}
```

### 4.4 ExperimentFlow コンポーネント

**責務**: 各フェーズに応じたUIコンポーネントの描画

#### 4.4.1 サブコンポーネント

| コンポーネント | フェーズ | 説明 |
|--------------|---------|------|
| `ConsentScreen` | CONSENT | 参加同意取得 |
| `InstructionScreen` | INSTRUCTION | 実験手順説明 |
| `ChatInterface` | SESSION_* | チャットUI |
| `EvaluationForm` | EVALUATION | 7段階評価アンケート |
| `DebriefingScreen` | DEBRIEFING | 終了・ダウンロード案内 |

#### 4.4.2 ConsentScreen

```tsx
function ConsentScreen({ onComplete }: { onComplete: () => void }) {
    // 表示内容:
    // - 実験目的の説明
    // - 注意事項 (所要時間、データ匿名化、中止権利)
    // - 同意ボタン
}
```

#### 4.4.3 InstructionScreen

```tsx
function InstructionScreen({ onComplete }: { onComplete: () => void }) {
    // 表示内容:
    // 1. チャットセッション説明 (4テーマ × 5分)
    // 2. 評価アンケート説明
    // - 開始ボタン
}
```

#### 4.4.4 EvaluationForm

```tsx
interface EvaluationRatings {
    identity: number;      // 1-7 スケール
    naturalness: number;   // 1-7 スケール
    offensiveness: number; // 1-7 スケール
    comments: string;      // 自由記述
}

function EvaluationForm({ onComplete }: { onComplete: (data: EvaluationRatings) => void }) {
    // 評価項目:
    // 1. 聖らしさ (Identity): 「全く違う」〜「まさに本人」
    // 2. 自然さ (Naturalness): 「機械的」〜「人間的」
    // 3. 不快感 (Offensiveness): 「なし」〜「強い不快感」
    // 4. コメント (任意)
}
```

### 4.5 ChatInterface コンポーネント

**責務**: リアルタイムチャットUIの提供

```tsx
interface ChatInterfaceProps {
    messages: Message[];           // 表示するメッセージ
    onSendMessage: (content: string) => void;  // 送信ハンドラ
    isTyping: boolean;             // タイピングインジケーター表示
    disabled?: boolean;            // 入力無効化
}

export function ChatInterface({ messages, onSendMessage, isTyping, disabled }: ChatInterfaceProps) {
    // UI要素:
    // - ヘッダー (AIアバター、名前、オンラインステータス)
    // - メッセージ表示エリア (スクロール可能)
    // - タイピングインジケーター (3ドットアニメーション)
    // - 入力フォーム (テキスト入力 + 送信ボタン)
}
```

**スタイリング**:
- ユーザーメッセージ: 右寄せ、インディゴ背景
- AIメッセージ: 左寄せ、白背景
- タイピング: バウンスアニメーション

### 4.6 API Route - Limitless プロキシ

**ファイル**: `src/app/api/limitless/route.ts`

**目的**: クライアントからのLimitless API呼び出しをプロキシ

```typescript
export async function GET(request: NextRequest) {
    const apiKey = request.headers.get('X-Limitless-Key');
    
    if (!apiKey) {
        return NextResponse.json({ error: 'API Key is required' }, { status: 400 });
    }
    
    // Limitless APIへプロキシ
    const response = await fetch('https://api.limitless.ai/v1/lifelogs?limit=5', {
        headers: { 'X-API-Key': apiKey }
    });
    
    return NextResponse.json(await response.json());
}
```

**セキュリティ考慮**:
- APIキーはクライアントからヘッダーで受け取り、サーバーサイドで転送
- キーはサーバーに保存されない

### 4.7 Limitless テストページ

**ファイル**: `src/app/limitless-test/page.tsx`

**目的**: Limitless API接続のデバッグ・テスト用UI

```tsx
export default function LimitlessTestPage() {
    const [apiKey, setApiKey] = useState('');
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    
    const fetchData = async () => {
        // /api/limitless へリクエスト
    };
    
    // UI: APIキー入力 + フェッチボタン + 結果表示
}
```

### 4.8 ユーティリティ (utils.ts)

```typescript
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Tailwind CSSクラス名を結合するユーティリティ
 * clsx + tailwind-merge を組み合わせて重複クラスを適切に処理
 */
export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}
```

### 4.9 スタイリング (globals.css)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
    --foreground-rgb: 0, 0, 0;
    --background-start-rgb: 240, 242, 245;
    --background-end-rgb: 255, 255, 255;
}

body {
    /* グラデーション背景 */
    background: linear-gradient(...);
    font-family: 'Inter', sans-serif;
}

/* カスタムスクロールバー */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
```

---

## 5. データフロー

### 5.1 実験実行フロー

```
┌─────────────────────────────────────────────────────────────────┐
│                      実験開始                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  CONSENT: 参加同意取得                                           │
│  - 実験目的説明                                                  │
│  - 注意事項確認                                                  │
│  - 同意ボタンクリック                                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  INSTRUCTION: 実験手順説明                                       │
│  - 4つのチャットセッション説明                                   │
│  - 評価アンケート説明                                            │
│  - 開始ボタンクリック                                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           │      ランダム条件割り当て        │
           │      (P: 50%, G: 50%)          │
           └───────────────┬───────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
         ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐
│  Condition: P   │                 │  Condition: G   │
│  (Personalized) │                 │  (Generic)      │
└────────┬────────┘                 └────────┬────────┘
         │                                   │
         └─────────────────┬─────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  SESSION_FREE_CHAT: 雑談セッション (~5分)                        │
│  - 自由な会話                                                    │
│  - メッセージ履歴記録                                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  SESSION_KNOWLEDGE_PROBE: 記憶確認セッション (~5分)              │
│  - 個人的な記憶・知識に関する質問                                │
│  - メッセージ履歴記録                                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  SESSION_MORAL_CHOICE: 価値観共有セッション (~5分)               │
│  - 道徳的・倫理的な選択に関する対話                              │
│  - メッセージ履歴記録                                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  SESSION_STYLISTIC: 創作・大喜利セッション (~5分)                │
│  - 創造的なタスク                                                │
│  - メッセージ履歴記録                                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  EVALUATION: 評価アンケート                                      │
│  - Identity (1-7): 本人らしさ                                    │
│  - Naturalness (1-7): 自然さ                                     │
│  - Offensiveness (1-7): 不快感                                   │
│  - Comments: 自由記述                                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEBRIEFING: 実験終了                                            │
│  - 謝辞表示                                                      │
│  - データダウンロード (JSON)                                     │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 メッセージ処理フロー

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   User Input     │────▶│  ChatInterface   │────▶│  ExperimentFlow  │
│   (テキスト)     │     │  onSendMessage() │     │  handleSend()    │
└──────────────────┘     └──────────────────┘     └────────┬─────────┘
                                                            │
                                                            ▼
                                                  ┌──────────────────┐
                                                  │  State Update    │
                                                  │  messages.push() │
                                                  └────────┬─────────┘
                                                            │
                                                            ▼
                                                  ┌──────────────────┐
                                                  │  AI Backend      │
                                                  │  (TODO: Connect) │
                                                  └────────┬─────────┘
                                                            │
                                                            ▼
                                                  ┌──────────────────┐
                                                  │  Mock Response   │
                                                  │  (現在の実装)    │
                                                  └────────┬─────────┘
                                                            │
                                                            ▼
                                                  ┌──────────────────┐
                                                  │  State Update    │
                                                  │  messages.push() │
                                                  └────────┬─────────┘
                                                            │
                                                            ▼
                                                  ┌──────────────────┐
                                                  │  UI Re-render    │
                                                  │  ChatInterface   │
                                                  └──────────────────┘
```

### 5.3 出力データ構造

**ファイル名**: `experiment_data_{condition}_{timestamp}.json`

```json
{
    "condition": "P",
    "startTime": 1702108800000,
    "endTime": 1702110600000,
    "sessions": {
        "SESSION_FREE_CHAT": {
            "messages": [
                {
                    "id": "1702108900000",
                    "role": "user",
                    "content": "こんにちは、元気?",
                    "timestamp": 1702108900000
                },
                {
                    "id": "1702108901000",
                    "role": "assistant",
                    "content": "たしかに、元気だよ！最近何してた？",
                    "timestamp": 1702108901000
                }
            ],
            "duration": 300000
        },
        "SESSION_KNOWLEDGE_PROBE": { ... },
        "SESSION_MORAL_CHOICE": { ... },
        "SESSION_STYLISTIC": { ... }
    },
    "evaluation": {
        "identity": 5,
        "naturalness": 6,
        "offensiveness": 2,
        "comments": "口調が本人っぽかった"
    }
}
```

---

## 6. API仕様

### 6.1 内部API (Next.js Route)

#### GET /api/limitless

**目的**: Limitless API へのプロキシ

**リクエスト**:
```
GET /api/limitless
Headers:
  X-Limitless-Key: <api_key>
```

**レスポンス (成功)**:
```json
{
    "lifelogs": [
        {
            "id": "log_123",
            "title": "Morning standup",
            "startTime": "2024-09-17T00:00:00.000Z",
            "endTime": "2024-09-17T00:15:00.000Z",
            "isStarred": false,
            "markdown": "## Morning standup\n- discussed sprint goals",
            "contents": [...]
        }
    ],
    "nextCursor": null
}
```

**レスポンス (エラー)**:
```json
{
    "error": "API Key is required"
}
```

### 6.2 外部API

#### Limitless API

**ベースURL**: `https://api.limitless.ai`

**認証**: ヘッダー `X-API-Key: <api_key>`

**エンドポイント**:

| メソッド | パス | 説明 |
|---------|------|------|
| GET | /v1/lifelogs | ライフログ一覧取得 |

**パラメーター**:
| パラメーター | 型 | 説明 |
|------------|-----|------|
| limit | int | 取得件数 (1-10) |
| date | string | ISO日付フィルター |
| start | string | 開始時刻 (ISO8601) |
| end | string | 終了時刻 (ISO8601) |
| timezone | string | タイムゾーン |
| cursor | string | ページネーション |

**エラーコード**:
| コード | 説明 |
|-------|------|
| 400 | 不正なリクエスト |
| 401 | 認証失敗 |
| 429 | レート制限 |
| 500 | サーバーエラー |

#### Ollama API

**ベースURL**: `http://localhost:11434/api`

**エンドポイント**:

| メソッド | パス | 説明 |
|---------|------|------|
| GET | /version | バージョン確認 |
| POST | /generate | テキスト生成 (非使用) |
| POST | /chat | チャット生成 (使用中) |
| POST | /embeddings | 埋め込み生成（RAGで使用） |

**チャットリクエスト** (ollama-python):
```python
ollama.chat(
    model="gemma3:27b",
    messages=[{"role": "user", "content": prompt}]
)
```

---

## 7. データモデル

### 7.1 TypeScript型定義 (フロントエンド)

```typescript
// 実験フェーズ
type ExperimentPhase =
    | 'CONSENT'
    | 'INSTRUCTION'
    | 'SESSION_FREE_CHAT'
    | 'SESSION_KNOWLEDGE_PROBE'
    | 'SESSION_MORAL_CHOICE'
    | 'SESSION_STYLISTIC'
    | 'EVALUATION'
    | 'DEBRIEFING';

// 実験条件
type Condition = 'G' | 'P';

// メッセージ
interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
}

// セッションデータ
interface SessionData {
    messages: Message[];
    duration: number;
}

// 評価データ
interface EvaluationData {
    identity: number;      // 1-7
    naturalness: number;   // 1-7
    offensiveness: number; // 1-7
    comments?: string;
}

// 実験データ全体
interface ExperimentData {
    condition: Condition;
    startTime: number;
    endTime?: number;
    sessions: Partial<Record<ExperimentPhase, SessionData>>;
    evaluation?: EvaluationData;
}
```

### 7.2 Python型定義 (バックエンド)

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any, Optional

@dataclass
class LifelogEntry:
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    is_starred: bool
    updated_at: datetime
    markdown: Optional[str]
    contents: List[Dict[str, Any]]

# 会話履歴エントリ
class ConversationEntry(TypedDict):
    user: str
    agent: str
    timestamp: str

# 思考記録エントリ
class ThoughtEntry(TypedDict):
    timestamp: str
    category: str
    content: str

# AIパラメーター
class AIParameters(TypedDict):
    temperature: float       # 0.0-2.0
    top_p: float            # 0.0-1.0
    presence_penalty: float  # -2.0-2.0
    frequency_penalty: float # -2.0-2.0
    num_ctx: int            # 1024-4096
    repeat_penalty: float    # 1.0-2.0
    mirostat_mode: int      # 0-2
    max_tokens: int         # 500-2000
    jargon_level: int       # 1-5
    formality_level: int    # 1-5
    abstraction_level: int  # 1-5
```

---

## 8. 設定・パラメーター

### 8.1 福井聖AIパラメーター.json

**ファイル**: `cloneAI/福井聖AIパラメーター.json`

```json
{
    "temperature": 1.41,
    "top_p": 0.9,
    "presence_penalty": 0.76,
    "frequency_penalty": 0.6,
    "jargon_level": 4,
    "formality_level": 5,
    "abstraction_level": 2
}
```

**パラメーター解説**:

| パラメーター | 値 | 解説 |
|------------|-----|------|
| temperature | 1.41 | 高め: 創造的で予測不可能な応答を生成 |
| top_p | 0.9 | 高め: 多様な語彙選択 |
| presence_penalty | 0.76 | 中高: 話題の繰り返しを適度に避ける |
| frequency_penalty | 0.6 | 中: 単語の繰り返しを適度に避ける |
| jargon_level | 4 | やや高: 適度に専門用語を使用 |
| formality_level | 5 | 高: カジュアルな表現 |
| abstraction_level | 2 | 低: 具体例を多用 |

### 8.2 環境変数

**cloneAI**:
```bash
LIMITLESS_API_KEY=sk-xxxxx    # Limitless API キー
OLLAMA_HOST=http://127.0.0.1:11434  # 任意: デフォルトは localhost
```

**experiment-ui**:
```bash
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_CHAT_MODEL=gemma3:27b
OLLAMA_EMBED_MODEL=nomic-embed-text
```

### 8.3 Next.js設定 (next.config.ts)

```typescript
// デフォルト設定を使用
```

### 8.4 TypeScript設定 (tsconfig.json)

```json
{
    "compilerOptions": {
        "target": "ES2017",
        "lib": ["dom", "dom.iterable", "esnext"],
        "strict": true,
        "moduleResolution": "bundler",
        "jsx": "react-jsx",
        "paths": {
            "@/*": ["./src/*"]
        }
    }
}
```

---

## 9. テスト戦略

### 9.1 Pythonテスト (pytest)

**テストファイル**: `cloneAI/tests/test_lifelog_client.py`

**テストケース**:

| テスト名 | 検証内容 |
|---------|---------|
| `test_client_requires_api_key` | APIキー未指定時にValueError |
| `test_sends_api_key_header` | X-API-Keyヘッダーが正しく送信される |
| `test_builds_query_parameters` | クエリパラメーターが正しく構築される |
| `test_parses_lifelog_entries` | JSONレスポンスが正しくパースされる |
| `test_handles_rate_limit_error` | 429エラーが適切にハンドリングされる |
| `test_handles_generic_api_error` | 一般的なAPIエラーがハンドリングされる |

**テスト実行**:
```bash
cd cloneAI
python -m pytest
```

### 9.2 フロントエンドテスト

**現状**: 未実装

**推奨テスト戦略**:
- Jest + React Testing Library
- Cypress E2Eテスト

---

## 10. デプロイメント

### 10.1 開発環境セットアップ

#### cloneAI

```powershell
# 仮想環境の有効化
C:\Users\shofu\Desktop\卒研\cloneAI\venv\Scripts\Activate.ps1

# 依存関係インストール
pip install -r requirements.txt

# Ollamaサーバー起動（別ターミナル）
ollama serve

# エージェント実行
python clone_agentAI.py --interactive

# パラメーターチューナー起動
python chat_param_test.py
```

#### experiment-ui

```powershell
cd experiment-ui

# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev

# ビルド
npm run build

# プロダクションサーバー起動
npm start
```

### 10.2 本番環境

**推奨構成**:
- フロントエンド: Vercel (Next.js最適)
- バックエンド: Docker + AWS/GCP

---

## 11. 校閲・検証結果

### 11.1 コード整合性チェック

#### ✅ 確認済み項目

| カテゴリ | 項目 | 結果 |
|---------|------|------|
| 型定義 | ExperimentPhase定義と使用箇所 | 一致 |
| 型定義 | Message型の構造 | 一致 |
| 型定義 | Condition型 ('G' \| 'P') | 一致 |
| API | Limitless APIヘッダー (X-API-Key) | 一致 |
| API | エラーハンドリング (429, 500) | 実装済み |
| UI | フェーズ遷移順序 | 正しい |
| UI | 評価スケール (1-7) | 正しい |

#### ⚠️ 注意事項・改善推奨

| 項目 | 現状 | 推奨 |
|-----|------|------|
| バックエンド接続 | モック応答 | cloneAIとの接続実装 |
| セッション時間計測 | 未実装 (`duration: 0`) | 開始/終了時刻から計算 |
| エラーハンドリング | 基本的 | より詳細なユーザーフィードバック |
| テスト | Pythonのみ | フロントエンドテスト追加 |
| 国際化 | 日本語固定 | i18n対応検討 |

### 11.2 セキュリティ確認

| 項目 | 評価 | コメント |
|-----|------|---------|
| APIキー管理 | ⚠️ | クライアントから送信、サーバー保存なし |
| データ保存 | ✅ | ローカルダウンロードのみ |
| 入力検証 | ⚠️ | 追加検証推奨 |
| XSS対策 | ✅ | React自動エスケープ |

### 11.3 パフォーマンス確認

| 項目 | 評価 | コメント |
|-----|------|---------|
| 初期ロード | ✅ | Next.js SSG/SSR最適化 |
| チャットレスポンス | ⚠️ | モック3-5秒、実装時要調整 |
| メモリ使用 | ✅ | 履歴制限あり (max_history=10) |

### 11.4 ドキュメントと実装の差異

| ドキュメント記載 | 実装状況 | 対応 |
|----------------|---------|------|
| 4つのチャットセッション | ✅ 実装済み | - |
| 条件ランダム割り当て | ✅ 実装済み | - |
| 7段階評価 | ✅ 実装済み | - |
| JSONデータダウンロード | ✅ 実装済み | - |
| バックエンド連携 | ❌ 未実装 | TODO: API接続 |
| セッション時間記録 | ⚠️ 部分実装 | TODO: 計算ロジック |

### 11.5 発見された実装上の課題

#### 11.5.1 TODOコメント一覧

| ファイル | 行 | 内容 |
|---------|-----|------|
| `experiment-ui/src/app/page.tsx` | 35 | `duration: 0 // TODO: Calculate duration` |
| `experiment-ui/src/components/ExperimentFlow.tsx` | 242 | `content: \`(Mock Response...)\` // TODO: Connect to backend` |

#### 11.5.2 関数名と実装の不整合

| 項目 | 問題 | 影響 |
|-----|------|------|
| `create_yamada_taro_persona()` | 関数名が「山田太郎」だが、実際は「福井聖」のペルソナを返す | 可読性低下、要リネーム |

**修正推奨**:
```python
# Before
def create_yamada_taro_persona() -> PersonaTemplate:

# After  
def create_fukui_hijiri_persona() -> PersonaTemplate:
```

#### 11.5.3 未実装機能

| 機能 | 現状 | 優先度 |
|-----|------|-------|
| フロントエンド↔バックエンド連携 | モック応答のみ | **高** |
| セッション時間計測 | `duration: 0` 固定 | 中 |
| エラーリカバリー | 基本的なtry-catch | 中 |
| ログ収集・分析基盤 | 未実装 | 低 |
| 多言語対応 | 日本語固定 | 低 |

#### 11.5.4 コード品質メトリクス

| ファイル | 行数 | 複雑度 | コメント |
|---------|-----|-------|---------|
| clone_agentAI.py | 645 | 中 | 主要ロジック集中、分割推奨 |
| chat_param_test.py | 641 | 高 | GUI+ロジック混在、分離推奨 |
| ExperimentFlow.tsx | 266 | 中 | 適切なコンポーネント分割 |
| lifelog_client.py | 205 | 低 | 良好な構造 |

### 11.6 推奨アクションリスト

#### 即時対応（実験実施前に必須）

1. **バックエンドAPI接続実装**
   - Next.js API RouteからPythonバックエンドへの接続
   - 条件G/Pに応じたAI応答の切り替え

2. **セッション時間計測の実装**
   ```typescript
   // page.tsx 修正案
   const sessionStartTime = useRef<number>(0);
   
   useEffect(() => {
       if (phase.startsWith('SESSION_')) {
           sessionStartTime.current = Date.now();
       }
   }, [phase]);
   
   const handlePhaseComplete = (phaseData) => {
       const duration = Date.now() - sessionStartTime.current;
       // ...
   };
   ```

#### 中期対応（実験品質向上）

3. **関数名リファクタリング**
   - `create_yamada_taro_persona` → `create_fukui_hijiri_persona`

4. **フロントエンドテスト追加**
   - Jestセットアップ
   - コンポーネントユニットテスト
   - E2Eテスト（Cypress）

5. **エラーハンドリング強化**
   - ネットワークエラー時のリトライ
   - ユーザーへの明確なフィードバック

#### 長期対応（研究拡張）

6. **データ分析パイプライン構築**
   - 実験データの自動集計
   - 統計分析ツール連携

7. **A/Bテスト機能強化**
   - より細かい条件分岐
   - 多腕バンディット対応

---

## 付録

### A. ファイル一覧

```
卒研/
├── SYSTEM_DESIGN_DOCUMENT.md  # 本ドキュメント
├── cloneAI/
│   ├── clone_agentAI.py       # 645行
│   ├── chat_param_test.py     # 641行
│   ├── 福井聖AIパラメーター.json  # 8行
│   ├── requirements.txt       # 6行
│   ├── README.md              # 40行
│   ├── src/
│   │   └── limitless_api/
│   │       ├── __init__.py    # 3行
│   │       └── lifelog_client.py  # 205行
│   └── tests/
│       ├── conftest.py        # 12行
│       ├── test_lifelog_client.py  # 82行
│       └── data/
│           └── lifelogs_sample.json  # 24行
└── experiment-ui/
    ├── package.json           # 30行
    ├── tsconfig.json          # 34行
    └── src/
        ├── app/
        │   ├── globals.css    # 48行
        │   ├── layout.tsx     # 32行
        │   ├── page.tsx       # 83行
        │   ├── api/limitless/route.ts  # 33行
        │   └── limitless-test/page.tsx  # 74行
        ├── components/
        │   ├── ChatInterface.tsx  # 112行
        │   └── ExperimentFlow.tsx # 266行
        └── lib/
            ├── experiment-state.ts  # 54行
            └── utils.ts           # 6行
```

### B. 依存関係

**cloneAI (Python)**:
- requests >= 2.32.0
- pytest >= 8.2.0
- requests-mock >= 1.12.0
- ollama (pip install ollama)
- fastapi
- uvicorn[standard]

**experiment-ui (Node.js)**:
- next: 16.0.8
- react: 19.2.0
- react-dom: 19.2.0
- clsx: ^2.1.1
- lucide-react: ^0.554.0
- tailwind-merge: ^3.4.0
- tailwindcss: ^4
- typescript: ^5

### C. 用語集

| 用語 | 定義 |
|-----|------|
| Condition G | Generic - 汎用的なAI（比較対照群） |
| Condition P | Personalized - パーソナライズされたAI（実験群） |
| Identity | 「本人らしさ」の評価指標 |
| Naturalness | 「自然さ」の評価指標 |
| Offensiveness | 「不快感」の評価指標 |
| Lifelog | Limitless APIから取得する生活記録 |
| Persona | AIエージェントの人格設定 |
| ThoughtFlow | AIの思考過程を可視化する仕組み |

---

**ドキュメント作成日**: 2025年12月9日  
**最終更新**: 2025年12月9日  
**作成者**: GitHub Copilot (Claude Opus 4.5)  
**バージョン**: 1.0.0
