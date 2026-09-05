<!-- Generated from shared/. Do not edit directly. -->

# Tugite（Codex 用）

Tugite は Claude Code、Codex、Cursor 向けに、複数の作業手順、エージェント、スキルを配布するプラグインです。それぞれの作業手順は決められた役割と起動条件に従い、必要に応じて実装、レビュー、助言を担うエージェントを組み合わせます。

## 現行の構成

### 公開スキル

- `how-it`: 進め方が決まっていない依頼について、前提、選択肢、成立条件を利用者と一緒に整理し、求められた形で回答します。利用者が指定したときだけ使います。
- `explorer-this`: まずエージェント自身で調査し、判断に必要な情報や方針を人にしか確認できない場合に限って質問します。調査結果は依頼された形式で返します。利用者が指定したときだけ使います。
- `visualize-that`: 文書やデータなど任意の入力を、意味と不確実性を保った図解 HTML にします。利用可能な描画機能で実物を確認し、確認できない場合も HTML と理由を返します。利用者が指定したときだけ使います。
- `impl-lead`: 実装依頼を着手前に明確な作業単位へ整理し、実装、品質確認、受け入れ判断、最終検証、安全な取り込みまで責任を持ちます。利用者が指定したときだけ使います。
- `plan-agent`: 会話や提示資料をもとに、依頼に合った自由形式の計画・設計資料を、推奨案を中心に作ります。必要な場合だけレビューします。利用者が指定したときだけ使います。
- `find-way`: 目標全体の不明点と判断待ちの事項を整理し、1つ以上の自己完結した作業単位に分けて返します。利用者が指定したときだけ使います。
- `test-report`: 指定されたテスト範囲を実行せずに読み取り、期待する動作とテストケース・根拠の対応、および確認できない点を報告します。評価や修正は行いません。
- `test-verify`: 指定されたテスト対象を実行結果などの根拠に基づいて検証し、その対象が原因の問題だけを修正して、完了条件の確認と最終検証まで行います。利用者が指定したときだけ使います。
- `review-refine`: 途中で内容が変わらない対象を指定回数までレビューし、指摘を採用するかどうかと受け入れ結果を呼び出し元の親エージェントへ返します。

`plan-agent` は計画にレビューが必要か、利用者がレビュー不要と指定したかを判断します。レビューが不要な場合はそのまま最終候補を返します。レビューが必要で、利用者も不要と指定していない場合は `plan-adversarial-reviewer` と `over-engineering-reviewer` による厳格なレビューへ進みます。

### 実装・レビュー・助言を担うエージェント

実装を担うエージェントは `focused-implementer`、`implementer`、`senior-implementer`、`expert-implementer` です。

リスクに応じて選択するレビュー担当は `plan-adversarial-reviewer`、`responsibility-boundary-reviewer`、`test-quality-reviewer`、`over-engineering-reviewer`、`security-side-effect-reviewer`、`static-performance-reviewer`、`writing-principles-reviewer` です。`writing-principles-reviewer` は作業終了時の最終文章レビューに使います。

計画の品質について、内容を変更せずに助言する担当は `plan-quality-advisor` です。レビュー担当と助言担当は判断材料を返し、最終的な受け入れは親エージェントが行います。

## 導入と起動

Git リポジトリをマーケットプレイスとして登録し、プラグインを導入します。

```text
codex plugin marketplace add akitanabe/tugite
codex plugin add tugite@tugite
```

ローカルの作業コピーを使う場合は、リポジトリのルートで `codex plugin marketplace add .agents/plugins` を実行してから `codex plugin add tugite@tugite` を実行します。導入後は Codex セッションを再起動してください。

公開スキルは次のコマンドで直接起動できます。

```text
$how-it <相談したい進め方>
$explorer-this <探索タスク>
$visualize-that <可視化する入力>
$impl-lead <実装タスク>
$plan-agent <計画タスク>
$find-way <目標>
$test-report <確認するテスト範囲>
$test-verify <検証するテスト対象>
$review-refine <レビュー対象>
```

## カスタムエージェント

`install/agents/*.toml` は配布用のファイルです。ユーザー単位またはプロジェクト単位で導入する前に、現在の状態を確認してください。

新しい Codex セッションでは `$install-custom-agents` を使って、導入先の状態確認と導入を依頼できます。導入または更新後はセッションを再起動してください。

```text
plugins/codex/install/install-agents.sh --check --user
plugins/codex/install/install-agents.sh --check --repo <リポジトリ>
```

導入後は Codex セッションを再起動してください。既存の定義を更新する場合は、内容を確認してから `--force` を指定します。


親エージェントは変更前の状態、受け入れ条件、対象範囲、依存関係、差分、テスト結果を確認し、すべてのテストが成功する状態を再現できるときだけ変更を受け入れます。

## ライセンス

MIT License です。詳細は [LICENSE](https://github.com/akitanabe/tugite/blob/main/LICENSE) を参照してください。
