<!-- Generated from shared/. Do not edit directly. -->

# Tugite v7.2.0

Tugite は Claude Code、Codex、Cursor で実装作業を進めるためのプラグインです。親エージェントが依頼内容を実装単位に整理し、適切な担当へ実装を依頼して、品質確認と最終検証まで責任を持ちます。

細かな実装時のルールは [リポジトリガイドライン](docs/repository-guidelines.md) を参照してください。

## 現行の構成

### 公開スキル

- `how-it`: 進め方が決まっていない依頼について、前提、選択肢、成立条件を利用者と一緒に整理し、求められた形で回答します。利用者が指定したときだけ使います。
- `explorer-this`: まずエージェント自身で調査し、判断に必要な情報や方針を人にしか確認できない場合に限って質問します。調査結果は依頼された形式で返します。利用者が指定したときだけ使います。
- `impl-lead`: 実装依頼を着手前に明確な作業単位へ整理し、実装、品質確認、受け入れ判断、最終検証、安全な取り込みまで責任を持ちます。利用者が指定したときだけ使います。
- `plan-agent`: 会話や提示資料をもとに、依頼に合った自由形式の計画・設計資料を、推奨案を中心に作ります。必要な場合だけレビューします。
- `navigate-way`: 目標全体の不明点と判断待ちの事項を整理し、1つ以上の自己完結した作業単位に分けて返します。利用者が指定したときだけ使います。
- `test-report`: 指定されたテスト範囲を実行せずに読み取り、期待する動作とテストケース・根拠の対応、および確認できない点を報告します。評価や修正は行いません。
- `test-verify`: 指定されたテスト対象を実行結果などの根拠に基づいて検証し、その対象が原因の問題だけを修正して、完了条件の確認と最終検証まで行います。利用者が指定したときだけ使います。
- `review-refine`: 途中で内容が変わらない対象を指定回数までレビューし、指摘を採用するかどうかと受け入れ結果を呼び出し元の親エージェントへ返します。

`plan-agent` は計画にレビューが必要か、利用者がレビュー不要と指定したかを判断します。レビューが不要な場合はそのまま最終候補を返します。レビューが必要で、利用者も不要と指定していない場合は厳格なレビューへ進みます。

### 実装・レビュー・助言を担うエージェント

実装を担うエージェントは `focused-implementer`、`implementer`、`senior-implementer`、`expert-implementer` です。

リスクに応じて選択するレビュー担当は `plan-adversarial-reviewer`、`responsibility-boundary-reviewer`、`test-quality-reviewer`、`over-engineering-reviewer`、`security-side-effect-reviewer`、`static-performance-reviewer`、`writing-principles-reviewer` です。`writing-principles-reviewer` は作業終了時の最終文章レビューに使います。

計画の品質について、内容を変更せずに助言する担当は `plan-quality-advisor` です。レビュー担当と助言担当は判断材料を返し、最終的な受け入れは親エージェントが行います。

## 導入と起動

- [Claude Code プラグイン](https://github.com/akitanabe/tugite/blob/main/plugins/claude/README.md)
- [Codex プラグイン](https://github.com/akitanabe/tugite/blob/main/plugins/codex/README.md)
- [Cursor プラグイン](https://github.com/akitanabe/tugite/blob/main/plugins/cursor/README.md)

## ライセンス

MIT License です。詳細は [LICENSE](https://github.com/akitanabe/tugite/blob/main/LICENSE) を参照してください。
