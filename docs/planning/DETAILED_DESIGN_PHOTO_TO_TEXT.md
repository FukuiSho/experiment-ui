# 詳細設計: スマホ写真→JPG→Gemma3→JSON（photo_to_text）

最終更新: 2026-01-09

## 1. ゴールとスコープ

### ゴール
- `src/lib/pesonaldata/unlabeldata/smartphonephoto` 配下の画像を再帰走査する。
- 画像をJPGへ正規化（前処理）し、JPGをGemma3 27Bへ「画像入力」として渡して解釈テキストを生成する。
- 1画像につき1JSONファイルを `src/lib/pesonaldata/derived/photo_to_text` に出力する。
- 既に成功出力がある画像はスキップし、失敗分のみ再実行できる。
- 生成物はGitにコミットしない（.gitignore済み）。

### 非ゴール
- OCR専用エンジンの導入や、別モデル併用などの保険設計は現時点では行わない。
- UI（Next.js画面）への統合は行わない（バッチ実行前提）。

## 2. 入出力仕様

### 入力
- ルート: `src/lib/pesonaldata/unlabeldata/smartphonephoto`
- 対象拡張子（初期案）: `.heic`, `.jpg`, `.jpeg`, `.png`

### 出力
- ルート: `src/lib/pesonaldata/derived/photo_to_text`
- キャッシュ: `src/lib/pesonaldata/derived/photo_to_text/jpg_cache/`
- 結果: `src/lib/pesonaldata/derived/photo_to_text/<image_sha256>.json`

## 3. 出力JSONスキーマ（実装準拠）

`docs/PHOTO_TO_TEXT.md` の「出力JSONスキーマ（確定）」に準拠する。

### 3.1 必須
- `source_path` (string)
- `text` (string)
- `confidence` (number, 0.0〜1.0)

### 3.2 推奨（任意）
- `schema_version` (string) = `photo_to_text.v1`
- `image_sha256` (string)
- `jpg_cache_path` (string)
- `model` (string)
- `created_at` (string, ISO-8601)

## 4. 再実行・スキップ・失敗扱い

### 4.1 ステータス
- 「成功」とは、出力JSONが存在し、JSONとしてパースでき、`text` が空でないこと。
- 失敗は以下のいずれか:
  - 前処理（変換）が失敗
  - Ollama呼び出しが失敗（HTTPエラー/タイムアウト/JSON不正）
  - 生成JSONがスキーマ不一致

### 4.2 再実行ポリシー
- 成功出力がある `image_sha256` はスキップ。
- 失敗したものは次回実行時に再試行。

### 4.3 失敗ログ
- 失敗時は `src/lib/pesonaldata/derived/photo_to_text/_failures.jsonl` に追記（1行1レコード）する。
- 1レコードに最低限: `source_path`, `stage`（convert/ollama/parse/write）, `error`, `timestamp`。

## 5. 前処理（Pythonのみで完結するHEIC→JPG）

### 5.1 方式（採用案）
- Pythonで画像ロード/変換を完結する。
- HEICは `pillow-heif` を用いて読み込み可能にし、`Pillow` でJPGとして保存する。
  - 依存候補: `pillow`, `pillow-heif`（Windows対応wheelが提供されている前提）

### 5.2 変換仕様
- 出力JPGはRGBに正規化。
- EXIF回転（Orientation）は適用して保存。
- 保存品質（quality）は固定値（例: 92）で統一。

### 5.3 キャッシュ設計
- `jpg_cache/<image_sha256>.jpg` を正とする。
- 既にJPGが存在する場合は再生成しない（ただしサイズ0や破損の場合は作り直し）。

## 6. Ollama（Gemma3画像入力）

### 6.1 API仕様（Ollama公式）
- `/api/chat` に対し、`messages[].images` に base64 文字列配列を渡せる。
- `format` に `json` または JSON schema を渡し、構造化出力を強制できる。

### 6.2 モデル互換性チェック
- 実行前に `/api/show` で対象モデルを確認し、`capabilities` に `vision` が含まれることをチェックする。
  - 含まれない場合は「設計前提を満たさない」ため停止（現時点で保険設計はしない）。

### 6.3 リクエスト形
- `model`: `gemma3:27b`
- `messages`: user 1通（contentに指示文、imagesにJPG base64）
- `stream`: false
- `format`: JSON schema（推奨）
- `options`: `temperature` など（再現性優先なら `temperature=0`, `seed` 固定）

### 6.4 期待レスポンス
- `message.content` が JSON文字列になる。
- パースして `text` と `confidence` を抽出。

## 7. プロンプト設計（最小）

- 出力は必ずJSONで返すこと。
- `text` は画像内容の解釈テキスト（日本語）。
- `confidence` は 0.0〜1.0。
- 余計なキーや前置きは禁止。

## 8. 実装配置と実行インターフェース（次ターンで実装）

### 8.1 実装候補
- `scripts/photo_to_text.py`（推奨）
  - 理由: バッチ用途でNext.jsとは独立、Windows長パス対応などをPython側で扱いやすい。

### 8.2 CLI（案）
- `--input`（default: smartphonephoto）
- `--output`（default: derived/photo_to_text）
- `--model`（default: `gemma3:27b`）
- `--ollama-host`（default: `http://127.0.0.1:11434`）
- `--concurrency`（default: 1〜2）
- `--max-images`（デバッグ用）
- `--retry-failures-only`（default: true）

### 8.3 環境変数（案）
- `PHOTO_TO_TEXT_OLLAMA_HOST`
- `PHOTO_TO_TEXT_MODEL`

## 9. Windows向け注意

- パス長問題（MAX_PATH）を避けるため、出力ファイル名は `image_sha256` を利用する。
- 入力ファイル走査で長パスが発生する場合、Python側で `\\?\` プレフィックスを使う方針を検討する。

## 10. 検証手順（実装後）

- 1枚だけでスモークテスト（JPG生成、Ollama vision capabilityチェック、JSON生成）。
- 10枚程度で失敗率と実行時間を確認。
- `_failures.jsonl` の内容を確認し、失敗ステージが偏っていないか確認。
