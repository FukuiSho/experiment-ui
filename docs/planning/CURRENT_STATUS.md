# 現状把握（2025-12-31）

## 研究ゴール

- Condition P（パーソナライズ）と Condition G（汎用）を比較し、参加者評価（Identity / Naturalness / Offensiveness）で差を検証する
- 実験データ（JSON）を回収し、分析結果を論文・発表にまとめる

## 実装の現状（実ファイルに基づく）

### experiment-ui（Next.js）

- 実験フェーズ（CONSENT → INSTRUCTION → 4セッション → EVALUATION → DEBRIEFING）がある
- 条件（G/P）はクライアントでランダム割り当て
- チャットは `POST /api/chat` を呼び出して応答生成
  - G: 通常のsystem promptのみ
  - P: ベクトルストア検索（RAG）→ 取得した記憶をsystem promptへ付与
- LimitlessデータをMarkdown化して保存し、Embedding生成でベクトルストアを作る経路がある

### cloneAI（Python）

- persona/LLMクライアント/メモリなどの実装がある（Ollama対応）
- 現状の実験UIは、Python側を呼ばず Next.js側でOllamaを利用している
  - よって「cloneAIをUIに接続する」は“必須”ではなく、研究の目的に応じて選択

## 実験実施の直前に潰すべきギャップ

- セッション `duration` は実装済み（0固定の解消）
- P条件は事前に ingest を回して `vector-store.json` を生成しておく必要がある
- Ollama運用の確定（実験当日のPCで確実に起動し、モデルが揃っていること）
- 回収後の分析パイプライン（集計・統計・図表）が未整備

## 直近の進捗（デモ完走）

- Ollama を起動し、`experiment-ui` のデモ（4セッション→評価→JSONダウンロード）を完走
- `duration` を含む形で JSON を回収できる状態に到達

## 新たに見えた課題

- 応答が十分に「人間的」ではないため、より高性能なローカルモデル（Ollama）の導入・選定が必要
  - 容量/速度/安定性の制約があるため、複数モデル候補をベンチで比較して本採用する

## 次の一手（最短）

1. P条件のRAG準備手順を固定（save-knowledge → ingest → P条件で retrieved_context が返る）
2. パイロット実験（1〜2名）を回し、手順書を更新
3. ローカルモデルの品質改善（候補モデル導入→比較→採用）

関連:
- `ACTION_PLAN.md`
- `TODO.md`
- `SCHEDULE.md`
- `flowcharts/action-plan.mmd`
- `flowcharts/schedule-flow.mmd`
