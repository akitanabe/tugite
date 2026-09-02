<!-- Generated from shared/. Do not edit directly. -->

# Tugite for Codex

Tugite は、親 Codex エージェントが plan、Implementation Unit の route、QA、受け入れ、最終検証を保持しながら実装を worker へ依頼する plugin です。

## 現行の構成

### 公開 skill

- `how-it`: 未確定な request の前提、選択肢、成立条件を Human とともに構築し、current understanding を requested output へ接続します。明示起動時だけ使います。
- `explorer-this`: Agentic Model Construction を first route とする探索 workflow で、Human-owned material gap の場合だけ Interactive Model Construction を利用します。明示起動時だけ使います。
- `impl-lead`: implementation work を execution 前の Implementation Unit へ正規化し、実装、Parent QA、受入、final verification、安全な統合まで所有します。明示起動時だけ使います。
- `plan-agent`: normal context から request-relative な自由形式 planning / design artifact を recommendation-first で作り、必要な場合だけ review します。明示起動時だけ使います。
- `test-report`: 指定範囲を静的に観測し、独立 grounding できた Expected Observation と Case / Evidence の対応、および grounding できない場合の limitation を、評価や remediation なしで Verification Topology として報告します。
- `review-refine`: 不変 snapshot を指定回数の範囲でレビューし、指摘の採否と受け入れ結果を呼び出し元の親へ返します。

`plan-agent` は review applicability と explicit opt-out を判断し、nonapplicable / opt-out は unreviewed の normal final-candidate、applicable / no opt-out は `plan-adversarial-reviewer` と `over-engineering-reviewer` を使う strict review route へ進みます。

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
$test-report <test scope>
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


親エージェントは変更前の状態、受け入れ条件（AC）、対象範囲、依存関係、差分、テスト結果を確認し、Green（全テスト成功）を再現できるときだけ受け入れます。

## License

MIT License. See [LICENSE](https://github.com/akitanabe/tugite/blob/main/LICENSE).
