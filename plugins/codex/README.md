<!-- Generated from shared/. Do not edit directly. -->

# Tugite for Codex

Tugite は、親 Codex エージェントが plan、Implementation Unit の route、QA、受け入れ、最終検証を保持しながら実装を worker へ依頼する plugin です。

## 現行の構成

### 公開 skill

- `how-it`: 未確定な request の前提、選択肢、成立条件を Human とともに構築し、current understanding を requested output へ接続します。明示起動時だけ使います。
- `explorer-this`: Agentic Model Construction を first route とする探索 workflow で、Human-owned material gap の場合だけ Interactive Model Construction を利用します。明示起動時だけ使います。
- `impl-lead`: implementation work を execution 前の Implementation Unit へ正規化し、実装、Parent QA、受入、final verification、安全な統合まで所有します。明示起動時だけ使います。
- `plan-agent`: 要求とリポジトリの観測から実装 plan の候補を作り、回数を制限したレビューと親の裁定へ渡します。
- `plan-interactive`: Human-confirmed direction と constraints を受け取り、Interactive Model Construction と common Planning Core を経て Plan candidate または incomplete を返します。
- `review-refine`: 不変 snapshot を指定回数の範囲でレビューし、指摘の採否と受け入れ結果を呼び出し元の親へ返します。

`plan-agent` は適用可能なら既定 review を行い、明示的な review skip は通常の起草確定へ進みます。`plan-interactive` は適用可能なら既定 review を行い、明示的な skip と reviewer 非適用は Human final acceptance へ進みます。readiness 不足は review-not-established とします。両者とも既定 `plan-adversarial-reviewer` が非適用なら `review-refine` を bypass して通常の起草確定へ進みます。

### 内部 skill

`plan-candidate-producer` と `structural-health-gate` は公開ワークフローと同じ親エージェントのコンテキストで使う内部 skill です。`implementation-unit-design` は `impl-lead` 配下の consumer-specific Method です。いずれも直接起動や暗黙のワークフロー切替は行いません。

### Worker / reviewer / advisor

Implementation Unit worker は `focused-implementer`、`implementer`、`senior-implementer`、`expert-implementer` です。

リスクに応じて選択する reviewer は `plan-adversarial-reviewer`、`responsibility-boundary-reviewer`、`test-quality-reviewer`、`over-engineering-reviewer`、`security-side-effect-reviewer`、`static-performance-reviewer`、`writing-principles-reviewer` です。`writing-principles-reviewer` は実行終了時の最終文章レビューとして使います。

Plan の品質について読み取り専用で助言する advisor は `plan-quality-advisor` です。reviewer と advisor は判断材料を返し、最終受け入れは親エージェントが行います。

## Install and launch

Git marketplace を登録して plugin を導入します。

```text
codex plugin marketplace add akitanabe/tugite
codex plugin add tugite@tugite
```

ローカル checkout を使う場合は repository root で `codex plugin marketplace add .agents/plugins` を実行してから `codex plugin add tugite@tugite` を実行します。導入後は Codex session を再起動してください。

Public skill は次のコマンドで明示起動できます。

```text
$how-it <相談したい進め方>
$explorer-this <探索タスク>
$impl-lead <実装タスク>
$plan-agent <plan task>
$plan-interactive <human-directed plan task>
$review-refine <artifact review task>
```

## Custom agents

`install/agents/*.toml` は配布素材です。user scope または project scope へ導入する前に状態を確認します。

新しい Codex session では `$install-custom-agents` を使って対象 scope の状態確認と導入を依頼できます。導入または更新後は session を再起動してください。

```text
plugins/codex/install/install-agents.sh --check --user
plugins/codex/install/install-agents.sh --check --repo <repo>
```

導入後は Codex session を再起動してください。既存定義を更新する場合は内容を確認してから `--force` を指定します。


## 正本と生成

skill と agent の正本は `shared/`、バージョンは `shared/VERSION`、platform ごとの宣言定義の正本は `declarations/`、契約レジストリは `contracts/*.toml`、Gunte のプロジェクト設定は `gunte.toml` です。source と生成物の inventory、構造、byte drift は `gunte check` が検証します。

変更後はリポジトリのルートで次を実行します。

```text
gunte emit
gunte lock
gunte check
```

親エージェントは変更前の状態、受け入れ条件（AC）、対象範囲、依存関係、差分、テスト結果を確認し、Green（全テスト成功）を再現できるときだけ受け入れます。

## License

MIT License. See [LICENSE](https://github.com/akitanabe/tugite/blob/main/LICENSE).
