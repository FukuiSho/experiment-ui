# Gemini-CloneAI 実装詳細ドキュメント

本ドキュメントは、学術論文としての再現性を担保するため、システムの実装詳細を正確に記述したものです。実際のコードベース(`scripts/`, `src/`)の解析に基づいています。

## 1. データ収集・前処理

### データソースと正規化仕様
| 種類 | 生データ形式 | 取得・処理ロジック概要 | 出力形式 (正規化後) |
| :--- | :--- | :--- | :--- |
| **LifeLogs** | `lifelogs.json` (Limitless) | `startTime`を基準に、`contents`内の`blockquote`要素(文字起こし)を抽出。 | `limitless_{Title}_{ID}.txt` |
| **LINE** | テキスト形式 (`.txt`) | タブ区切り解析。`[スタンプ]`, `[写真]`, `[動画]`を含む行は除外。日付ヘッダ(`YYYY/MM/DD`)を解析し、各発話に結合。 | `[YYYY/MM/DD HH:MM] Speaker: Message` |
| **GPT** | `conversations.json` (Export) | 会話ツリー(`mapping`)を走査し、作成日時順にメッセージをソート。役割が`user`/`assistant`のものを抽出。 | `Role: Content` |
| **Twitter** | `tweets.js` (Archive) | `window.YTD.tweets.part0`オブジェクトをパース。`full_text`と`created_at`を抽出。 | `[Date] Text` |
| **メモ** | `.txt` (PC/スマホ) | 単純なテキスト抽出。 | 原文まま |

- **スクリプト**: `scripts/normalize_data.ts`
- **除外規則**:
    - LINE: スタンプ、写真、動画のみの行は削除。
    - ファイル名: 日本語・英数字以外はアンダースコア(`_`)に置換。
- **写真テキスト化 (OCR)**:
    - **モデル**: `gemma3:27b` (Vision対応)
    - **プロンプト**: `"画像内容を日本語で要約し、text(日本語文字列)とconfidence(0..1)のみを含むJSONで返してください。JSON以外は出力しないこと。"`
    - **スクリプト**: `scripts/photo_to_text.py`

### 分類 (Classification)
- **手法**: `gemma2:9b` (高速化のため軽量モデル使用) にテキスト(先頭2000文字)を入力し、`Fact` (事実), `Thought` (考え), `Experience` (体験) の3カテゴリに分類。
- **プロンプト**: System promptにて厳格に3値分類を指示 (temperature 0.1)。
- **スクリプト**: `scripts/classify_data.ts`

---

## 2. DB構築 (ChromaDB)

### パラメータ設定
- **DB**: ChromaDB v3.2.0 (Running on `localhost:8000`)
- **コレクション名**: `limitless_logs`
- **埋め込みモデル**: `nomic-embed-text` (via Ollama API)
    - 次元の記載なし(モデル依存、通常768次元)
- **チャンク設計**:
    - **サイズ**: 500文字 (`chunkSize`)
    - **オーバーラップ**: 50文字 (`overlap`)
    - **分割単位**: 文字数ベースの単純スライス (`String.slice`)
- **メタデータ**:
    - `source`: 元ファイル名
    - `category`: `Fact`, `Thought`, `Experience` のいずれか
    - `chunk_index`: 分割順序
- **スクリプト**: `scripts/ingest_chroma.ts`

---

## 3. 検索 (Retrieval) の仕様

### 検索ロジック
- **クエリ**: ユーザーの入力メッセージをそのまま使用（加工なし）。
- **検索方式**: 純粋なベクトル検索 (`cosine` distance implied by Chroma default).
- **取得件数 (k)**: **3件** (`limit=3`)
- **動的フィルタリング (Intent Routing)**:
    - ユーザー入力に対し、`gemma3:27b`を用いて「検索すべきカテゴリ (`Fact`/`Thought`/`Experience`)」を判定。
    - 判定されたカテゴリ(複数可)に合致するチャンクのみを対象に検索を行う。
    - **意図**: 雑談に事実データが混ざるノイズを防ぐため。
- **再ランキング**: 未実装 (Chromaのスコア順をそのまま使用)。
- **実装ファイル**: `src/app/api/chat/route.ts`

---

## 4. プロンプト設計

### System Prompt (RAG Context Injection)
検索ヒット時(`condition='P'`)、以下の構造でプロンプトが構築されます。

1.  **人格定義**: 「深い思想を持つINTP的な大学生エンジニア」等の詳細なペルソナ記述。
2.  **制約条件**:
        - 「出力は基本10文字以下」
        - 「理由説明をしない」
        - 「質問を返さない」
        - 「丁寧語禁止」
3.  **注入コンテキスト**:
    ```text
    ----------------
    [Category] Content (Chunk 1)
    
    ---
    
    [Category] Content (Chunk 2)
    ...
    ----------------
    ```
    - 引用元メタデータ（ファイル名等）はプロンプトには含めず、カテゴリのみ付与。

### 安全・禁止事項
- **実装**: プロンプト内での自然言語指示のみ（「質問を返さない」等）。
- **後処理**: ルールベースによるフィルタリング等はコード上確認されず、モデルの従順さに依存。

---

## 5. 生成モデル実行条件

- **モデル**: `gemma3:27b` (via Ollama)
- **推論パラメータ**:
    - `temperature`: **1.41** (かなり高めの設定。創造性・多様性重視)
    - `top_p`: **0.9**
    - `num_predict`: **1000** (最大生成トークン)
- **シード**: 固定なし (Runningごとに変動)。
- **量子化**: Ollama標準の4bit量子化 (通常) と推定される。

---

## 6. 評価データ (ベンチマーク) 作成

### 作成パイプライン
1.  **QAペア生成** (`scripts/generate_qa_benchmark.py`):
    - LINE/Limitlessデータから、「ターゲットユーザーの発話」とその「直前5発話(コンテキスト)」をペアとして抽出。
    - これにより「入力(他者) &rarr; 正解(本人)」のペアを作成。
2.  **機械的フィルタ** (`scripts/benchmark/01_syntax_filter.py`):
    - 短すぎる発話、スタンプ代替テキスト、特定のネットスラングを除外。
3.  **スコアリング** (`scripts/benchmark/03_scoring_fast.py`):
    - **正解データの品質**を評価（LLM生成なしで高速化）。
    - 基準: 文字数(20-150文字)、一人称(俺/僕)の有無、感情語の有無、疑問形への回答かどうか。
4.  **最終選定** (`scripts/benchmark/05_compile_final.py`):
    - 手動選定分（優先）＋ スコア上位分をマージし、計100件を確定。

---

## 7. 評価指標の実装詳細

評価スクリプト: `scripts/calculate_similarity.ts`

1.  **正規化レーベンシュタイン距離** (Normalized Levenshtein):
    - 計算式: $1 - \frac{Levenshtein(A, B)}{\max(|A|, |B|)}$
    - 前処理: なし（句読点や空白もそのまま比較）。厳密な一致度を見る。
2.  **Jaccard係数 (Bigram)**:
    - 文を2文字ごとのBi-gram集合に分解。
    - 計算式: $\frac{|Set(A) \cap Set(B)|}{|Set(A) \cup Set(B)|}$
    - 意味的な単語の重複度合いを評価。
3.  **BIG5**:
    - コード上での自動計算ロジックはなし。
    - `src/lib/constants.ts` にユーザー定義の固定値として記載 (`外向性: 57` 等)。外部テスト等で測定した値を入力パラメータとして使用している。

---

## 8. 環境情報

- **フレームワーク**: Next.js 16.0.8, React 19.2.0
- **バックエンド**: Node.js (App Router API routes)
- **DB**: ChromaDB v3.2.0 (Docker/Local)
- **LLM Runtime**: Ollama (Local API)
- **OS**: Windows (User Metadataより)
