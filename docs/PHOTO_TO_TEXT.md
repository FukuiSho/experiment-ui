# スマホ写真→テキスト抽出（Gemma3 27B）

最終更新: 2026-01-09

## 確定事項（これまでの合意）

### 目的
- `smartphonephoto` 配下の写真を **全件** 読み取り、画像から読み取れる情報の「解釈テキスト」を生成する。
- **1画像につき1つ**の解釈テキストを出力する。

### 入力（対象ディレクトリ）
- 物理パス: `C:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata\smartphonephoto`
- リポジトリ相対: `src/lib/pesonaldata/unlabeldata/smartphonephoto`

### 出力（保存先ディレクトリ）
- 物理パス: `C:\Users\ok220109\experiment-ui\src\lib\pesonaldata\derived\photo_to_text`
- リポジトリ相対: `src/lib/pesonaldata/derived/photo_to_text`

### 前処理
- 前処理として、元画像を **JPGへ変換** する。
- 変換したJPGは出力配下に `jpg_cache/` を作って保存する方針。

期待ディレクトリ構成（例）:

- `src/lib/pesonaldata/derived/photo_to_text/`
  - `jpg_cache/`（前処理で作成したJPGのキャッシュ）
  - `*.json`（各画像に対応する出力JSON）

### モデル入力
- 前処理で作成した **JPGをそのままGemma3に画像入力として与える**。
- Gemma3（27B）により、画像内容から読み取れることをテキストで出力させる。

※前提: ローカルで `gemma3:27b` が利用可能（例: Ollamaでpull済み）。

### 出力形式
- 出力は **JSON形式**。
- **1画像につき1JSONファイル**を生成する。

### 出力JSONスキーマ（確定）

#### 最小必須フィールド（確定）

1画像につき1ファイルのJSON（root object）を出力する。

- `source_path` (string): 元画像へのリポジトリ相対パス（例: `src/lib/pesonaldata/unlabeldata/smartphonephoto/...`）
- `text` (string): 画像から読み取れる情報の解釈テキスト
- `text` は **必ず日本語** で出力する（モデルプロンプトで強制）
- `confidence` (number): 0.0〜1.0 の小数（confidence≠正解確率。後述）

#### 推奨（任意）メタフィールド

運用・再実行・比較に必要になりやすいもの。

- `schema_version` (string): 例 `photo_to_text.v1`
- `image_sha256` (string): 元画像バイト列のSHA256（重複排除・ID用途）
- `jpg_cache_path` (string): 生成したJPGキャッシュへのリポジトリ相対パス（例: `src/lib/pesonaldata/derived/photo_to_text/jpg_cache/<sha256>.jpg`）
- `model` (string): 例 `gemma3:27b`
- `created_at` (string): ISO-8601（例: `2026-01-09T12:34:56+09:00`）

#### 例（1ファイル）

```json
{
  "schema_version": "photo_to_text.v1",
  "source_path": "src/lib/pesonaldata/unlabeldata/smartphonephoto/2026/01/IMG_0001.HEIC",
  "image_sha256": "...",
  "jpg_cache_path": "src/lib/pesonaldata/derived/photo_to_text/jpg_cache/...jpg",
  "model": "gemma3:27b",
  "created_at": "2026-01-09T12:34:56+09:00",
  "text": "...",
  "confidence": 0.62
}
```

### confidence（採用・確定）

#### 採用根拠

- 後段で検索/要約/共有に使う際に、「怪しい出力」を機械的に弾いたり、人手確認対象に回したりするためのフラグになる。
- プロンプト/モデル/前処理の変更による品質差を比較・評価しやすくする（ログ指標）。

#### 定義（確定）

- `confidence` は **正解確率ではない**（校正されている前提ではない）。
- `confidence` は `0.0〜1.0` の小数（number）で、出力の「品質推定値」として扱う。

#### confidenceデータ詳細（原文）

> なぜ必要か: 後段で検索/要約/共有に使うとき、「怪しい出力」を機械的に弾いたり、人手確認対象に回したりするためのフラグになります。
> 
> 何を表すか（推奨定義）:
> confidence.overall = 画像の読み取りやすさと出力の安定性を含む “品質推定値”（0..1）
> これは確率ではなく、運用上の優先度付けのためのスコアです。
> 
> どうやって作るか（代表例）:
> 自己申告型: プロンプトで「0..1で自信度も出して」と要求し、その値を取り込む（ただし過信しない）
> ヒューリスティック型: 出力に「たぶん/おそらく/見えない/不明」等が多ければ下げる、数字や固有名詞が多い場合は慎重に下げる等
> 一致度型（上級）: 温度違い/別プロンプトで複数回生成し、結果の一致度で上げ下げ（コスト増）

#### 今後の展望（短期/中期）

- 短期: まずは `confidence` を1値（overall相当）として安定運用し、低confidence群を優先してサンプリング目視確認する。
- 中期: 必要になったら `confidence_components`（例: readability/ocr_text_fidelity 等）や、複数回生成による一致度ベースの推定へ拡張する。

### Git運用
- 生成物は個人情報を含む可能性があるため、**Gitにコミットしない**。
- `src/lib/pesonaldata/derived/photo_to_text` は `.gitignore` により無視する。

### 実装ステータス（TDDで実装済み）
- 実装: `scripts/photo_to_text.py`（JPG変換＋Ollama画像入力＋JSON出力＋失敗ログ）。
- テスト: `scripts/tests/test_photo_to_text.py`（ハッシュ計算、PNG→JPG変換、Ollama画像入力payload、スキーマ、created_at、vision capabilityチェック、max-images制御）。
- 依存: `.venv` に `pillow`, `pillow-heif`, `requests-mock`, `ollama` などをインストール済み（`python -m pip install -r services/cloneai/requirements.txt`）。
- モデルcapability: 実行時に `/api/show` で `vision` を確認し、未対応なら停止。

### 起動手順（バッチ実行）
1. 仮想環境を有効化: `./.venv/Scripts/Activate.ps1`
2. 依存確認（初回のみ）: `python -m pip install -r services/cloneai/requirements.txt`
3. スモークテスト（1枚だけ）:
  - `python scripts/photo_to_text.py --input src/lib/pesonaldata/unlabeldata/smartphonephoto --output src/lib/pesonaldata/derived/photo_to_text --max-images 1`
4. 全件実行: `python scripts/photo_to_text.py --input src/lib/pesonaldata/unlabeldata/smartphonephoto --output src/lib/pesonaldata/derived/photo_to_text`
  - 既存で成功済みJSONがあるものはスキップ、失敗は `_failures.jsonl` に記録。
5. 必要に応じて `--model` / `--ollama-host` / `--no-skip-existing` / `--timeout` / `--max-images` を指定。

## 未決事項（重要：実装前に最終確定が必要）

以下は実装内容に影響するため、別途確定する。

- 対象拡張子（例: `*.heic, *.jpg, *.jpeg, *.png`）
- HEIC→JPG変換の方式（Pythonのみで完結させる方針）
- 出力ファイル命名規則（推奨: `image_sha256` ベース）
- 再実行戦略（方針: 既存の成功出力はスキップ、失敗分は再実行）
