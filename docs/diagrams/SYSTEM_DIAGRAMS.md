# 卒業研究システム概要図集

本ドキュメントは、システム設計ドキュメントの補足資料として、視覚的な図解を提供します。

---

## 1. システム全体構成図 (Mermaid)

```mermaid
flowchart TB
    subgraph User["👤 実験参加者"]
        Browser["Webブラウザ"]
    end

    subgraph Frontend["🖥️ experiment-ui (Next.js 16)"]
        direction TB
        Page["page.tsx<br/>状態管理"]
        Flow["ExperimentFlow.tsx<br/>フロー制御"]
        Chat["ChatInterface.tsx<br/>チャットUI"]
        API["API Route<br/>/api/limitless"]
        
        Page --> Flow
        Flow --> Chat
        Page --> API
    end

    subgraph Backend["🐍 cloneAI (Python)"]
        direction TB
        Agent["AIPersonaAgent<br/>メインエージェント"]
        Persona["PersonaTemplate<br/>ペルソナ定義"]
        Memory["MemoryManager<br/>会話履歴"]
        Thought["ThoughtFlow<br/>思考可視化"]
        Ollama["OllamaClient<br/>LLM通信"]
        
        Agent --> Persona
        Agent --> Memory
        Agent --> Thought
        Agent --> Ollama
    end

    subgraph External["☁️ 外部サービス"]
        direction LR
        OllamaServer["Ollama Server<br/>localhost:11434"]
        Limitless["Limitless API<br/>ライフログ"]
    end

    Browser <--> Page
    API --> Limitless
    Ollama --> OllamaServer
    Backend -.->|"将来実装"| Frontend
    
    style User fill:#e1f5fe
    style Frontend fill:#fff3e0
    style Backend fill:#e8f5e9
    style External fill:#fce4ec
```

---

## 2. 実験フローチャート (Mermaid)

```mermaid
flowchart TD
    Start([🚀 実験開始]) --> Consent
    
    subgraph Phase1["フェーズ1: 準備"]
        Consent["📋 CONSENT<br/>参加同意取得"]
        Instruction["📖 INSTRUCTION<br/>手順説明"]
        Consent --> Instruction
    end
    
    Instruction --> Random{{"🎲 条件ランダム割当<br/>50% : 50%"}}
    
    Random -->|"Condition: P"| SessionP["Personalized AI"]
    Random -->|"Condition: G"| SessionG["Generic AI"]
    
    SessionP --> Sessions
    SessionG --> Sessions
    
    subgraph Phase2["フェーズ2: チャットセッション (各5分)"]
        Sessions["4つのセッション"]
        S1["💬 SESSION_FREE_CHAT<br/>雑談"]
        S2["🧠 SESSION_KNOWLEDGE_PROBE<br/>記憶の確認"]
        S3["⚖️ SESSION_MORAL_CHOICE<br/>価値観の共有"]
        S4["🎨 SESSION_STYLISTIC<br/>創作・大喜利"]
        
        Sessions --> S1 --> S2 --> S3 --> S4
    end
    
    S4 --> Evaluation
    
    subgraph Phase3["フェーズ3: 評価"]
        Evaluation["📊 EVALUATION<br/>アンケート回答<br/>Identity / Naturalness / Offensiveness"]
        Debriefing["✅ DEBRIEFING<br/>終了・データDL"]
        Evaluation --> Debriefing
    end
    
    Debriefing --> End([🏁 実験終了])
    
    style Start fill:#4caf50,color:#fff
    style End fill:#f44336,color:#fff
    style Random fill:#ff9800,color:#fff
```

---

## 3. クラス図 (Mermaid)

```mermaid
classDiagram
    class AIPersonaAgent {
        +PersonaTemplate persona
        +OllamaClient client
        +ThoughtFlow thought_flow
        +MemoryManager memory
        +process_input(user_input: str) str
        -_build_prompt(user_input: str) str
        -_analyze_response(response: str, user_input: str) str
        +get_thought_process() List
        +reset_conversation() void
    }

    class PersonaTemplate {
        +str name
        +str description
        +Dict traits
        +str background
        +str personality
        +str speech_style
        +List knowledge_areas
        +List values
        +to_prompt() str
    }

    class MemoryManager {
        +List conversation_history
        +Dict key_facts
        +int max_history
        +add_interaction(user_input: str, agent_response: str) void
        +add_fact(key: str, value: Any) void
        +get_history_as_text(num_entries: int) str
    }

    class ThoughtFlow {
        +List thoughts
        +add_thought(thought: str, category: str) void
        +get_thoughts() List
        +get_thought_summary() str
    }

    class LLMClient {
        <<abstract>>
        +generate(prompt: str) str*
    }

    class OllamaClient {
        +str model_name
        +str base_url
        +bool simulation_mode
        +generate(prompt: str) str
        -_simulate_generation(prompt: str) str
        -_real_generate(prompt: str) str
        +set_simulation_mode(enabled: bool) void
    }

    class LifelogClient {
        +str api_key
        +str base_url
        +Session _session
        +float _timeout
        +list_lifelogs(**params) Tuple
    }

    class LifelogEntry {
        +str id
        +str title
        +datetime start_time
        +datetime end_time
        +bool is_starred
        +datetime updated_at
        +str markdown
        +List contents
    }

    AIPersonaAgent --> PersonaTemplate : uses
    AIPersonaAgent --> MemoryManager : uses
    AIPersonaAgent --> ThoughtFlow : uses
    AIPersonaAgent --> OllamaClient : uses
    LLMClient <|-- OllamaClient : extends
    LifelogClient --> LifelogEntry : creates
```

---

## 4. データフロー図 (Mermaid)

```mermaid
sequenceDiagram
    participant U as 👤 ユーザー
    participant UI as 🖥️ ChatInterface
    participant EF as 📋 ExperimentFlow
    participant BE as 🐍 AIPersonaAgent
    participant LLM as 🤖 Ollama

    U->>UI: メッセージ入力
    UI->>EF: onSendMessage(content)
    EF->>EF: messages.push(userMsg)
    EF->>EF: setIsTyping(true)
    
    Note over EF,BE: 現在はモック実装<br/>将来的にAPI接続
    
    EF->>BE: process_input(content)
    BE->>BE: _build_prompt()
    BE->>BE: ThoughtFlow.add_thought()
    BE->>LLM: generate(prompt)
    LLM-->>BE: response
    BE->>BE: _analyze_response()
    BE->>BE: Memory.add_interaction()
    BE-->>EF: final_response
    
    EF->>EF: messages.push(aiMsg)
    EF->>EF: setIsTyping(false)
    EF-->>UI: 再描画
    UI-->>U: AI応答表示
```

---

## 5. 評価指標ダイアグラム (Mermaid)

```mermaid
graph LR
    subgraph Metrics["📊 評価指標 (7段階リッカート)"]
        direction TB
        
        subgraph Identity["🎭 Identity (本人らしさ)"]
            I1["1: 全く違う"]
            I4["4: どちらでもない"]
            I7["7: まさに本人"]
            I1 -.-> I4 -.-> I7
        end
        
        subgraph Naturalness["🌿 Naturalness (自然さ)"]
            N1["1: 機械的"]
            N4["4: どちらでもない"]
            N7["7: 人間的"]
            N1 -.-> N4 -.-> N7
        end
        
        subgraph Offensiveness["⚠️ Offensiveness (不快感)"]
            O1["1: なし"]
            O4["4: やや気になる"]
            O7["7: 強い不快感"]
            O1 -.-> O4 -.-> O7
        end
    end
    
    subgraph Analysis["📈 分析観点"]
        Compare["条件間比較<br/>P vs G"]
        Session["セッション別分析"]
        Corr["指標間相関"]
    end
    
    Identity --> Compare
    Naturalness --> Compare
    Offensiveness --> Compare
    Compare --> Session
    Compare --> Corr
    
    style Identity fill:#e3f2fd
    style Naturalness fill:#e8f5e9
    style Offensiveness fill:#ffebee
```

---

## 6. ディレクトリ構造図 (Tree)

```
卒研/
├── 📄 SYSTEM_DESIGN_DOCUMENT.md     # メイン設計ドキュメント
├── 📄 SYSTEM_DIAGRAMS.md            # 本ファイル（図集）
├── 📄 DIAGRAM_GENERATION_PROMPT.md  # 外部ツール用プロンプト
│
├── 🐍 cloneAI/                      # Pythonバックエンド
│   ├── clone_agentAI.py             # [645行] メインエージェント
│   ├── (削除) prottipe.py            # OpenAI直接呼出プロトタイプ（廃止）
│   ├── chat_param_test.py           # [641行] パラメータGUI
│   ├── 福井聖AIパラメーター.json      # AIパラメータ設定
│   ├── requirements.txt             # Python依存関係
│   ├── README.md                    # 使用方法
│   │
│   ├── 📁 src/
│   │   └── 📁 limitless_api/
│   │       ├── __init__.py          # パッケージ初期化
│   │       └── lifelog_client.py    # [205行] APIクライアント
│   │
│   └── 📁 tests/
│       ├── conftest.py              # テスト設定
│       ├── test_lifelog_client.py   # [82行] ユニットテスト
│       └── 📁 data/
│           └── lifelogs_sample.json # テストデータ
│
└── 🖥️ experiment-ui/                # Next.jsフロントエンド
    ├── package.json                 # Node依存関係
    ├── tsconfig.json                # TypeScript設定
    ├── next.config.ts               # Next.js設定
    ├── tailwind.config.js           # Tailwind設定
    │
    └── 📁 src/
        ├── 📁 app/
        │   ├── globals.css          # グローバルCSS
        │   ├── layout.tsx           # レイアウト
        │   ├── page.tsx             # [83行] メインページ
        │   │
        │   ├── 📁 api/limitless/
        │   │   └── route.ts         # [33行] APIプロキシ
        │   │
        │   └── 📁 limitless-test/
        │       └── page.tsx         # [74行] APIテストUI
        │
        ├── 📁 components/
        │   ├── ChatInterface.tsx    # [112行] チャットUI
        │   └── ExperimentFlow.tsx   # [266行] フロー制御
        │
        └── 📁 lib/
            ├── experiment-state.ts  # [54行] 型定義
            └── utils.ts             # [6行] ユーティリティ
```

---

## 7. 状態遷移図 (Mermaid)

```mermaid
stateDiagram-v2
    [*] --> CONSENT: 実験開始
    
    CONSENT --> INSTRUCTION: 同意クリック
    INSTRUCTION --> SESSION_FREE_CHAT: 開始クリック
    
    state "チャットセッション" as Sessions {
        SESSION_FREE_CHAT --> SESSION_KNOWLEDGE_PROBE: 次へ
        SESSION_KNOWLEDGE_PROBE --> SESSION_MORAL_CHOICE: 次へ
        SESSION_MORAL_CHOICE --> SESSION_STYLISTIC: 次へ
    }
    
    SESSION_STYLISTIC --> EVALUATION: 次へ
    EVALUATION --> DEBRIEFING: 送信
    DEBRIEFING --> [*]: ダウンロード完了
    
    note right of CONSENT
        参加同意の取得
        注意事項の確認
    end note
    
    note right of Sessions
        各セッション約5分
        メッセージ履歴を記録
    end note
    
    note right of EVALUATION
        3項目の7段階評価
        自由記述コメント
    end note
```

---

## 8. コンポーネント依存関係図 (Mermaid)

```mermaid
graph TD
    subgraph Frontend["experiment-ui"]
        page["page.tsx"]
        ExperimentFlow["ExperimentFlow.tsx"]
        ChatInterface["ChatInterface.tsx"]
        experimentState["experiment-state.ts"]
        utils["utils.ts"]
        apiRoute["api/limitless/route.ts"]
        
        page --> ExperimentFlow
        page --> experimentState
        ExperimentFlow --> ChatInterface
        ExperimentFlow --> experimentState
        ChatInterface --> experimentState
        ChatInterface --> utils
    end
    
    subgraph Backend["cloneAI"]
        clone_agentAI["clone_agentAI.py"]
        prottipe["prottipe.py"]
        chat_param_test["chat_param_test.py"]
        lifelog_client["lifelog_client.py"]
        params["福井聖AIパラメーター.json"]
        
        clone_agentAI --> params
        prottipe --> params
        chat_param_test --> params
    end
    
    subgraph External["外部"]
        Ollama["Ollama"]
        %% OpenAIは廃止（Ollama専用化）
        Limitless["Limitless"]
    end
    
    apiRoute --> Limitless
    clone_agentAI --> Ollama
    %% prottipe.py は廃止（Ollama専用化）
    lifelog_client --> Limitless
    
    page -.->|"TODO"| clone_agentAI
    
    style page fill:#ff9800
    style clone_agentAI fill:#4caf50
```

---

## Mermaid図のレンダリング方法

### VS Code での表示
1. 拡張機能「Markdown Preview Mermaid Support」をインストール
2. Markdownプレビュー（Ctrl+Shift+V）で表示

### オンラインツール
- [Mermaid Live Editor](https://mermaid.live/)
- [GitHub](GitHubのMarkdownは直接Mermaidをレンダリング)

### 画像出力
```bash
# mermaid-cli インストール
npm install -g @mermaid-js/mermaid-cli

# SVG出力
mmdc -i SYSTEM_DIAGRAMS.md -o diagram.svg
```

---

**作成日**: 2025年12月9日
