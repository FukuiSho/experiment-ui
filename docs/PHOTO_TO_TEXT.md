# スマホ写真→テキスト抽出（Gemma3 27B）

最終更新: 2026-01-08

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

### Git運用
- 生成物は個人情報を含む可能性があるため、**Gitにコミットしない**。
- `src/lib/pesonaldata/derived/photo_to_text` は `.gitignore` により無視する。

## 未決事項（重要：実装前に最終確定が必要）

以下は実装内容に影響するため、別途確定する。

- 対象拡張子（例: `*.heic, *.jpg, *.jpeg, *.png`）
- HEIC→JPG変換の方式（Windows環境での依存関係・変換品質）
- 出力JSONスキーマ（最低限 `text` のみか、`source_path`/`model`/`timestamp` 等のメタを含めるか）
- 出力ファイル命名規則（元パスベースか、ハッシュIDベースか）
- 再実行戦略（差分更新、失敗リトライ、並列度、ログ保存）
