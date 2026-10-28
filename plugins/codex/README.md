<!-- Generated from shared/. Do not edit directly. -->

# Tugite（Codex 用）

Tugite は Claude Code、Codex、Cursor 向けに、複数の作業手順、エージェント、スキルを配布するプラグインです。それぞれの作業手順は決められた役割と起動条件に従い、必要に応じて実装、レビュー、助言を担うエージェントを組み合わせます。

## 現行の構成

### 公開スキル

- `explain-this`: 実装の全体像・処理の流れ・各処理の意味を、コード根拠と観測の限界付きで説明します。
- `review-propose`: 元プランを保持し、整合した推奨案と効果・複雑さ・負担の比較を返します。採用は利用者が判断します。
- `impl-plan`: 与えられたプランを、実装単位・担当・依存順序・検証が分かる委譲文書へ具体化して終了します。全体規模と分担の最終判断は利用者に残します。
- `impl-review`: 実装済み差分を専門・テスト・記法の共通基準でレビューし、修正表を返して変更前に停止します。

- `visualize-that`: 文書やデータなど任意の入力を、意味と不確実性を保った図解 HTML にします。利用可能な描画機能で実物を確認し、確認できない場合も HTML と理由を返します。利用者が指定したときだけ使います。
- `impl-lead`: 委譲文書の内容と実行時の前提を確認し、実装、品質確認、受け入れ判断、最終検証、安全な取り込みまで責任を持ちます。利用者が指定したときだけ使います。
- `test-report`: 指定されたテスト範囲を実行せずに読み取り、全体像と振る舞い別の期待・条件・assertion・根拠、静的に確認した問題、実行確認が必要な疑い、判断材料の不足を報告します。実行や修正は行いません。
- `test-verify`: report の全体・選択した指摘、または直接指定された対象を再確認し、実行結果などに基づいて検証・因果修復して最終検証まで行います。変更不要な場合も結果を返します。利用者が指定したときだけ使います。


調査・初期プラン作成は通常のエージェントへ依頼します。必要な skill だけを選び、各起動条件に従います。固定の自動チェーンにはしません。通常プランは `impl-plan` へ、委譲文書を指定した実装依頼は `impl-lead` へ渡します。

### 実装・レビュー・助言を担うエージェント

実装を担うエージェントは `focused-implementer`、`implementer`、`senior-implementer`、`expert-implementer` です。

レビュー担当は `plan-adversarial-reviewer`、`responsibility-boundary-reviewer`、`test-coverage-reviewer`、`test-validity-reviewer`、`over-engineering-reviewer`、`security-side-effect-reviewer`、`static-performance-reviewer`、`writing-principles-reviewer` です。`impl-lead` でテストを追加・変更・削除する実装単位は、coverage と validity の両レビューを受けてから親が受け入れを裁定します。`impl-review` でも変更テストには両レビューを適用し、修正候補として返します。その他の作業手順の起動条件は各 workflow に従い、`writing-principles-reviewer` は作業終了時の最終文章レビューに使います。

initial candidate の実装方法について、内容を変更せずに別の視点を返す担当は `plan-quality-advisor` です。レビュー担当と助言担当は判断材料を返し、採否と最終的な受け入れは親エージェントが行います。

## 導入と起動

Git リポジトリをマーケットプレイスとして登録し、プラグインを導入します。

```text
codex plugin marketplace add akitanabe/tugite
codex plugin add tugite@tugite
```

ローカルの作業コピーを使う場合は、リポジトリのルートで `codex plugin marketplace add .agents/plugins` を実行してから `codex plugin add tugite@tugite` を実行します。導入後は Codex セッションを再起動してください。

公開スキルは次のコマンドで直接起動できます。

```text
$explain-this <理解する実装>
$review-propose <比較する元プラン>
$impl-plan <具体化するプラン>
$impl-review <実装差分（省略時はcontextから特定）>
$visualize-that <可視化する入力>
$impl-lead <実装タスク>
$test-report <確認するテスト範囲>
$test-verify <検証するテスト対象>
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
