# プロジェクト進捗（監視用サマリ）

最終更新: 2026-01-08

## いまの状況（1ページで追う）

- 目的: Condition P（パーソナライズ）と Condition G（汎用）を比較し、参加者評価（Identity / Naturalness / Offensiveness）で差を検証する
- 現状: ローカル（Ollama）でデモ完走は到達。P条件のRAGは事前準備（knowledge保存→ingest→vector-store生成）の運用固定が重要。

## 今週の最重要（最大3つ）

- [ ] Condition P の事前準備手順を固定（save-knowledge → ingest → P条件で retrieved_context が返る）
- [ ] パイロット実験（1〜2名）で手順・運用の穴を洗い出し
- [ ] 本番で使うローカルモデルの品質改善（候補比較→採用モデル決定）

## 直近の完了・到達点

- [x] ローカル（Ollama）で 4セッション→評価→JSONダウンロードまで完走
- [x] `duration` を含む形で JSON を回収できる状態に到達

## ブロッカー / リスク

- P条件はベクトルストアが未生成だと再現性が落ちる（実験当日の事故要因）
- 実験後の分析パイプライン（集計・統計・図表）が未整備

## 関連ドキュメント

- 目次: [README.md](./README.md)
- 現状把握: [planning/CURRENT_STATUS.md](./planning/CURRENT_STATUS.md)
- ToDo: [planning/TODO.md](./planning/TODO.md)
- スケジュール: [planning/SCHEDULE.md](./planning/SCHEDULE.md)
- 作業ログ: [worklog/](./worklog/)
