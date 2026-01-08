# ローカルデモ手順（Ollama版）

更新日: 2025-12-31

目的: `experiment-ui` を **ローカルLLM（Ollama）** で動かし、4セッション→評価→JSONダウンロードまで完走できる状態を固定する。

---

## 0. 前提

- Windows
- `experiment-ui` は `npm install` 済み
- Ollama をインストールできる（管理者権限が必要な場合あり）

> 更新: 2025-12-31に Ollama 起動 + デモ完走を確認（以降、この手順は導入済み前提）。

---

## 1. Ollama の導入

### 1.1 インストール

- 公式インストーラで導入（推奨）
  - https://ollama.com/

または winget が使える場合:

```powershell
winget install Ollama.Ollama
```

インストール後、PowerShell で確認:

```powershell
ollama --version
```

起動確認（サーバ疎通）:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags | ConvertTo-Json -Depth 5
```

> `ollama serve` を実行して「port already in use」が出る場合は、すでに Ollama が起動中です（問題なし）。

### 1.2 モデル取得（例）

チャット用（軽量）:

```powershell
ollama pull gemma3:1b
```

RAG用の埋め込みモデル（ローカル完結したい場合）:

```powershell
ollama pull nomic-embed-text
```

取得確認:

```powershell
ollama list
```

---

## 2. experiment-ui をローカルLLMに切り替える

`experiment-ui` の API は **Ollama前提** です（旧方式は削除済み）。

### 2.1 Chat（Ollama）

```powershell
$env:OLLAMA_HOST = 'http://127.0.0.1:11434'
$env:OLLAMA_CHAT_MODEL = 'gemma3:1b'
```

### 2.2 RAG の埋め込み（Ollama）

```powershell
$env:OLLAMA_EMBED_MODEL = 'nomic-embed-text'
```

> 旧Embedding方式は削除済みのため利用できません。

---

## 3. デモ実施手順（最短）

### 3.1 experiment-ui 起動

```powershell
Push-Location "C:\Users\shofu\Desktop\卒研\experiment-ui"
npm run dev
```

ブラウザで `http://localhost:3000` を開く。

### 3.2 P条件（RAG）を成立させる

P条件を確実に成立させるには、事前に以下が必要です。

- `src/data/limitless-knowledge.md` を保存済み
- ingest を実行して `src/data/vector-store.json` を生成済み

実行経路（UI）:

- `limitless-test` で取得→保存
- `rag-test` で ingestion 実行

> `rag-test` では「P条件（RAG検索）」をONにして、`retrieved_context` が返ることを確認する。

---

## 4. 完走チェック（Definition of Done）

- 4セッションで会話できる
- 各セッションの `duration` が 0 ではない
- 評価フォームを送信できる
- 最後に JSON をダウンロードできる

---

## 5. トラブルシュート

- `Ollama error` / 接続不可: Ollama アプリが起動しているか、`OLLAMA_HOST` が正しいかを確認
- embedding で失敗: 
  - `OLLAMA_EMBED_MODEL` を設定し、モデルを `ollama pull` 済みにする
