This is the experiment UI for the graduation research project.

It is designed to run **locally with Ollama** for both chat and RAG embeddings.

## Getting Started

### 0) Prerequisites

- Install Ollama (Windows): https://ollama.com/
- Ensure the server is running and accessible at `http://127.0.0.1:11434` (default)

Pull models (example):

```powershell
ollama pull gemma3:1b
ollama pull nomic-embed-text
```

Set environment variables (PowerShell example):

```powershell
$env:OLLAMA_HOST = 'http://127.0.0.1:11434'
$env:OLLAMA_CHAT_MODEL = 'gemma3:1b'
$env:OLLAMA_EMBED_MODEL = 'nomic-embed-text'
```

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## CloneAI (Python backend) 同梱

このリポジトリには、元 `cloneAI/` のFastAPIサーバ実装を `services/cloneai/` として同梱しています。
これにより、`experiment-ui` レポジトリ内だけで cloneAI のバックエンドを起動できます。

### 1) Python依存のセットアップ（初回のみ）

PowerShell例:

```powershell
cd C:\Users\shofu\Desktop\sotuken\experiment-ui

python -m venv services\cloneai\venv
services\cloneai\venv\Scripts\Activate.ps1

python -m pip install -r services\cloneai\requirements.txt
```

※ `chat_param_test.py`（パラメーターチューナー）を動かす場合は、別途 `matplotlib` 等が必要になる場合があります。

### 2) フロント＋バックエンドをまとめて起動

```powershell
npm install
npm run dev:all
```

もし `experiment-ui` の親フォルダ（例: `C:\Users\shofu\Desktop\sotuken`）でコマンドを打っている場合、`package.json` が見つからず `Missing script: "dev:all"` になります。
その場合は次のどちらかで起動してください。

**A) 先にexperiment-uiへ移動してから実行**

```powershell
cd C:\Users\shofu\Desktop\sotuken\experiment-ui
npm run dev:all
```

**B) 親フォルダから `--prefix` で実行（移動不要）**

```powershell
cd C:\Users\shofu\Desktop\sotuken
npm --prefix .\experiment-ui run dev:all
```

**C) PowerShellスクリプトで起動（作業ディレクトリ非依存）**

```powershell
cd C:\Users\shofu\Desktop\sotuken
powershell -ExecutionPolicy Bypass -File .\experiment-ui\scripts\dev-all.ps1
```

### 3) 動作確認

- Front: http://localhost:3000
- CloneAI Test UI: http://localhost:3000/cloneai-test

ポートが既に使われている場合:

- Next.js: `3000` が使用中なら自動で `3001` 等に切り替わります（ログに表示されます）。
- CloneAI(FastAPI): `8001` が使用中なら `8002`〜`8010` の空きを自動で探して起動します。

Next.jsの `Unable to acquire lock ... .next\\dev\\lock` が出る場合:

- 同じ `experiment-ui` で別の `next dev` が既に動いています（または前回の異常終了でロックが残っています）。
- まず既存の開発サーバを停止（起動しているPowerShellで `Ctrl + C`）してから再実行してください。

環境変数（任意）:

- `CLONEAI_BASE_URL`（default: `http://127.0.0.1:8001`）
- `CLONEAI_OLLAMA_MODEL`（cloneAI側のデフォルトモデル。default: `gemma3:1b`）

### RAG (P condition) quick check

1) Generate/save `src/data/limitless-knowledge.md` via `/limitless-test`
2) Build the vector store via `/rag-test` → "Run Ingestion"
3) In `/rag-test`, keep "P条件（RAG検索）で実行" enabled and send a message
	- Confirm `retrieved_context` is non-empty when the vector store matches

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
