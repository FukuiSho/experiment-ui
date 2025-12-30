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
