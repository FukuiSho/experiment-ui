# 引き継ぎメモ（2025-12-22）ローカルモデルPoC/モデル選定

## 状況サマリ

- 方針: ローカルモデル（Ollama）前提で、PoC→安定化→複数モデル比較→本採用→実験、の流れに切替。
- ただし現PCは空き容量が約10GBで、Ollama + 複数モデルDLが厳しいため「別PCで作業」想定。

## 今日までにできたこと（実装・成果物）

### 計画・設計

- ローカルモデル前提の計画: [sotsuken/planning/LOCAL_MODEL_SELECTION_PLAN.md](sotsuken/planning/LOCAL_MODEL_SELECTION_PLAN.md)
- 選定フロー図（Mermaid）: [sotsuken/planning/flowcharts/local-model-selection.mmd](sotsuken/planning/flowcharts/local-model-selection.mmd)

### cloneAI（既存実装を活かすPoC基盤）

- 依存関係の整備（追記）: [cloneAI/requirements.txt](cloneAI/requirements.txt)
  - `fastapi`, `uvicorn`, `ollama` をrequirementsに追記
- `cloneAI/clone_agentAI.py` 修正
  - Ollamaモデル名がハードコードされていた箇所を `self.model_name` に修正
  - `ollama` import失敗時のエラーメッセージを追加
- PoC用ローカルAPI（FastAPI）を追加: [cloneAI/clone_server.py](cloneAI/clone_server.py)
  - `POST /chat`（session_idで簡易セッション）
  - `GET /health`
  - Ollamaが利用不可の場合はシミュレーションに自動フォールバックするよう修正

### ベンチ/評価スクリプト（モデル比較の土台）

- Limitless MarkdownからベンチJSONL作成: [cloneAI/benchmark/build_benchmark_from_limitless_md.py](cloneAI/benchmark/build_benchmark_from_limitless_md.py)
- 複数Ollamaモデル評価（自動スコア）: [cloneAI/benchmark/evaluate_models.py](cloneAI/benchmark/evaluate_models.py)

## 現PCで確認できたこと

- Python側の `ollama` パッケージはimportできる
- `clone_agentAI.py` の `test_mode()` は動作（ただしOllama本体が無いのでシミュレーション応答）
- `fastapi/uvicorn` は仮想環境へインストール済み
- 重要: **Ollama本体（Windowsのollamaコマンド/サーバー）は未インストール**
  - `Get-Command ollama` が失敗
  - そのためローカルモデル実行はできていない

## 未完了（ブロッカー）

- 別PCで Ollama本体をインストールし、モデルをpullして動作確認する必要がある
- 「ローカルモデルで応答」PoCを成立させるのはここから

## 別PCでの再開手順（最短）

### 1) リポジトリ/フォルダ

- `卒研/` をそのまま別PCへコピー（またはgit等で同期）

### 2) Python環境

- 既存の venv を使うならそのまま、難しければ新規作成して以下を入れる
  - `pip install -r cloneAI/requirements.txt`

### 3) Ollama（必須）

- WindowsへOllamaをインストール
- インストール後、PowerShellで以下が通ること
  - `ollama --version`

### 4) モデル取得（例）

- 軽量モデル例:
  - `ollama pull gemma3:1b`

### 5) PoCサーバ起動

- PowerShell（別PC）で

```powershell
Push-Location "C:\Users\<you>\Desktop\卒研\cloneAI"
.\venv\Scripts\python.exe -m uvicorn clone_server:app --host 127.0.0.1 --port 8001
```

### 6) 疎通確認

```powershell
Invoke-RestMethod http://127.0.0.1:8001/health | ConvertTo-Json
$body = @{ message = 'こんにちは。自己紹介して'; session_id = 'poc'; reset = $true; model_name = 'gemma3:1b' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8001/chat -ContentType 'application/json' -Body $body | ConvertTo-Json -Depth 5
```

- Ollamaが動いていればローカルモデルで返答
- まだ動いていなければシミュレーション（または接続エラー）

## ベンチ作成→評価の流れ（別PCでOllama動作後）

### 1) ベンチJSONL作成

入力は Limitless由来のMarkdown（例: experiment-ui側で生成した `limitless-knowledge.md`）

```powershell
Push-Location "C:\Users\<you>\Desktop\卒研\cloneAI"
.\venv\Scripts\python.exe .\benchmark\build_benchmark_from_limitless_md.py --input "<path-to>\limitless-knowledge.md" --output .\benchmark\hijiri_bench.jsonl --limit 200
```

### 2) 複数モデル評価

```powershell
.\venv\Scripts\python.exe .\benchmark\evaluate_models.py --benchmark .\benchmark\hijiri_bench.jsonl --models "gemma3:1b,qwen2.5:1.5b" --out .\benchmark\results.json --max 50
```

- 出力: `results.json`（avg_similarity, pronoun_rate等）

## 注意（容量・運用）

- モデルDLは容量を食うので、別PCは十分な空き容量（最低でも数十GB推奨）があると安全
- 実会話データ（Limitless由来）は取り扱い注意（共有範囲・保管場所・提出方法のルール化推奨）
