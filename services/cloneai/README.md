# Limitless Lifelog Client Prototype

This workspace now includes a prototype client for the Limitless Developer API. The focus is to iteratively build a small test-driven component that can fetch Lifelog entries for a single user using an API key.

The implementation lives under `src/limitless_api` and the accompanying tests live under `tests/`.

## 使い方 (Usage)

1. 依存パッケージを既存の仮想環境にインストールします。

	```powershell
	C:\Users\shofu\Desktop\卒研\cloneAI\venv\Scripts\Activate.ps1
	cd C:\Users\shofu\Desktop\卒研\cloneAI
	python -m pip install -r requirements.txt
	```

2. ユニットテストを実行し、クライアントの基本動作を確認します。

	```powershell
	python -m pytest
	```

3. LimitlessのAPIキーを環境変数 `LIMITLESS_API_KEY` に設定し、ライフログを一覧表示します。

	```powershell
	setx LIMITLESS_API_KEY "sk-xxxxx"
	python -m limitless_api.lifelog_client --limit 5 --timezone Asia/Tokyo
	```

	あるいは `--api-key` オプションで直接キーを渡すこともできます。取得したLifelogのID、タイトル、時間帯、Markdown要約 (先頭数行) が標準出力に表示され、次のページがある場合は `Next cursor` が案内されます。

> ⚠️ 実APIを叩くため、ネットワーク接続および有効なAPIキーが必要です。開発・検証用のキーを利用し、公開リポジトリ等にハードコードしないでください。

## Next steps

- `tests/` に実APIキーを用いたスモークテスト（環境変数でON/OFF）を追加する。
- `/v1/chats` や `/v1/download-audio` も同じパターンでクライアント化し、インジェストジョブから呼び出せるようにする。
