# 詳細設計：Chat + RAG（実験実行に移せる状態）

更新日: 2025-12-22

## 0. 今日の達成目標（Definition of Done）

**目的**: 実験フロー（4セッション→評価→JSON回収）を回せる前提として、Chat応答生成とRAG（P条件の記憶注入）が再現性高く動く状態を作る。

**今日のDoD（満たせばOK）**

- G条件で `/api/chat` がエラーなく応答する（Ollamaが起動している）
- P条件で `/api/chat` が **retrieved_context を返す**（＝RAGが実際に参照されている）
- `limitless-knowledge.md` → ingest → `vector-store.json` の生成が成功する（手順が固定されている）
- UI側（ExperimentFlow）から `condition` を渡して応答が返る

> 注: セッションの `duration` 計測は「実験データ品質」に重要だが、本設計はまず“Chat/RAGの成立”にフォーカスする。

---

## 1. スコープ

### 対象（今回やる）

- Next.js API: Chat（Ollama）
- RAG: knowledge(md) → embedding → vector store(json) → 検索 → system promptへ注入
- Limitless取得（プロキシ）→ Markdown化 → 保存
- 動作確認用UI（limitless-test / rag-test）を用いた手順の固定化

### 対象外（今回やらない）

- Python `cloneAI` を experiment-ui に接続する（experiment-uiはNext.js側でOllamaを使用する）
- 統計分析スクリプトの実装（別設計）
- UIの追加/改修（必要最小限の修正は別タスク）

---

## 2. 現状アーキテクチャ（実装準拠）

### コンポーネント

- experiment-ui（Next.js / React）
  - UI: 4セッション + 評価 + DL
  - API Routes:
    - `POST /api/chat`
    - `POST /api/rag/ingest`
    - `POST /api/save-knowledge`
    - `GET /api/limitless`
- データファイル:
  - `experiment-ui/src/data/limitless-knowledge.md`（Limitlessから生成する知識）
  - `experiment-ui/src/data/vector-store.json`（embedding済みのベクトルストア）

### 条件（G/P）の意味

- **G**: system prompt（ペルソナ）だけで応答
- **P**: system prompt（ペルソナ） + RAGで検索した“最近の記憶”を追記して応答

---

## 3. データフロー（手順の固定化）

### 3.1 Limitless → Knowledge(Markdown) の生成

**目的**: 被験者（=本人）の「記憶」をRAG入力にする。

- UI: `limitless-test` ページ
- Server: `GET /api/limitless`
- Client: `convertLimitlessToMarkdown()` で Markdown化
- Server: `POST /api/save-knowledge` で `src/data/limitless-knowledge.md` に保存

**要点**

- Limitless APIキーはクライアントから `X-Limitless-Key` で渡し、サーバーが `X-API-Key` として外部APIへ中継
- 保存先は `experiment-ui/src/data/limitless-knowledge.md`（固定）

### 3.2 Knowledge → Embedding → Vector Store

**目的**: RAG検索可能なインデックスを作る。

- `POST /api/rag/ingest`
  - 入力: `src/data/limitless-knowledge.md`（固定）
  - split: `\n---\n` 区切り（converterのセパレータ）
  - embedding: Ollama（例: `nomic-embed-text`）
  - 出力: `src/data/vector-store.json`

**要点（実験当日事故りやすい）**

- Ollamaが未起動/未インストール/ポート不一致だと ingest も chat も失敗する
- `limitless-knowledge.md` が空/存在しないと ingest は失敗する（404）

### 3.3 Chat（RAG検索→応答生成）

- UI（ExperimentFlow） → `POST /api/chat` に `{ message, condition }`
- P条件:
  - `searchVectorStore(message, 3)`
  - 上位チャンクを `contextText` として system prompt へ追記
- Ollama Chat:
  - model: `OLLAMA_CHAT_MODEL`（例: `gemma3:1b`）
  - options: temperature / top_p / num_predict

---

## 4. API詳細設計

### 4.1 `POST /api/chat`

**目的**: チャット応答（G/P切替 + P時RAG）

**Request JSON**

```json
{
  "message": "string",
  "condition": "G" 
}
```

- `condition` は `"G" | "P"` を想定
- 未指定の場合はG相当（現状実装では `condition === 'P'` のときだけRAG）

**Response JSON（成功）**

```json
{
  "reply": "string | null",
  "retrieved_context": [
    {
      "id": "string",
      "content": "string",
      "metadata": {
        "source": "string",
        "timestamp": "string"
      },
      "embedding": [0.0]
    }
  ]
}
```

- `retrieved_context` はデバッグ用途。P条件かつvector storeがある場合に返る。

**エラー**

- `400`: messageが空
- `500`: Ollama呼び出し失敗／内部例外

**セキュリティ/運用**

- Chat/RAGはローカルOllamaを利用し、外部APIキーは不要
- Limitless APIキーはクライアント入力→サーバプロキシ経由で利用（クライアントに永続保持しない）

### 4.2 `POST /api/rag/ingest`

**目的**: `limitless-knowledge.md` を embedding して `vector-store.json` を生成

**Request**: bodyなし

**Response（成功）**

```json
{
  "success": true,
  "count": 12,
  "message": "Ingestion complete"
}
```

**エラー**

- `404`: knowledgeファイルがない
- `500`: embedding（Ollama）失敗

### 4.3 `POST /api/save-knowledge`

**目的**: Markdown knowledgeを保存

**Request JSON**

```json
{
  "content": "# ...markdown...",
  "filename": "limitless-knowledge.md"
}
```

- `filename` は省略可（既定: `limitless-knowledge.md`）

### 4.4 `GET /api/limitless`

**目的**: Limitless APIプロキシ

**Request headers**

- `X-Limitless-Key: <limitless_api_key>`

**設計意図**

- 30秒タイムアウト + 3回リトライ

---

## 5. 画面（動作確認の導線）

### 5.1 Limitless Test

- 目的: Limitless疎通 → Markdown変換 → 保存
- 操作:
  - API Key入力 → Fetch → Save to File

### 5.2 RAG Test

- 目的: ingest → chat の疎通確認
- 操作:
  - Run Ingestion → Chat Verification（返答 + retrieved_context確認）

---

## 6. 実験実行前チェックリスト（最短）

- [ ] `ollama --version` が通る（Ollama導入済み）
- [ ] `OLLAMA_HOST` が正しい（既定: `http://127.0.0.1:11434`）
- [ ] `OLLAMA_CHAT_MODEL` / `OLLAMA_EMBED_MODEL` を `ollama pull` 済み
- [ ] `limitless-knowledge.md` が生成済み
- [ ] ingest済みで `vector-store.json` が生成済み
- [ ] `rag-test` で P相当の検索が働く（retrieved_contextが空でない）
- [ ] `experiment-ui` の本番フロー（4セッション→評価→DL）が完走する

---

## 7. 例外・失敗時の期待挙動（仕様として固定）

- vector storeが空/未生成:
  - P条件でも `retrieved_context` が空配列になり得る
  - その場合でもチャットは通常のsystem promptで成立する（実験を止めない）
- Ollama未起動/接続不可:
  - ingestもchatも失敗するため、実験開始前に必ず検証する
- Limitlessキーが無効:
  - knowledge生成ができない → P条件の再現性が落ちる
  - 実験当日までに本人環境でknowledge作成を終えておく（推奨）

---

## 8. 受け入れテスト（手順）

### テストA: G条件 chat

1. `experiment-ui` を起動
2. `POST /api/chat` に `{"message":"こんにちは","condition":"G"}`
3. `reply` が返る

### テストB: P条件 RAG

1. Limitless Test で保存 → ingest
2. `POST /api/chat` に `{"message":"最近何してた？","condition":"P"}`
3. `retrieved_context.length >= 1` を確認

### テストC: UIからの経路

1. 実験UIを開始
2. セッションで発言して返信が返る
3. 次のセッションへ進む

---

## 9. 実装タスク（この設計に沿って今日やること）

- 手順の固定化（README的運用メモでも可）
- 最低限の成功条件を満たすまで `rag-test` / `limitless-test` で検証
- 不足があれば、APIの入力検証/エラーメッセージの明確化など“最小変更”で整える
