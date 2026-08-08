# Tugite for Codex

Tugite v5.0.0 は、親 Codex エージェントが plan、Work Unit の route、QA、受け入れ、最終検証を保持しながら実装を worker へ依頼する plugin です。

## Skill surface

Public skill は次の3つです。

- `impl-lead`: Work Unit を正規化し、direct または worker の実装、TDD、必要な risk-directed review、親 QA、final writing gate を進めます。
- `plan-craft`: 要求と repository の観測から plan candidate を作り、bounded review と親の裁定へ渡します。
- `review-loop`: 不変 artifact snapshot を bounded round で review し、finding と evidence を親へ返します。

`proposal`、`structural-health-gate`、`work-unit-design` は public workflow の同じ親 context だけで使う internal skill です。直接の user invocation は受け付けません。

## Agent surface

Worker は `focused-implementer`、`implementer`、`senior-implementer`、`expert-implementer` です。

Reviewer は `plan-adversarial-reviewer`、`responsibility-boundary-reviewer`、`test-quality-reviewer`、`over-engineering-reviewer`、`security-side-effect-reviewer`、`writing-principles-reviewer` です。`writing-principles-reviewer` は final writing gate に使います。

Advisor は read-only の `plan-quality-advisor` です。reviewer と advisor は evidence を返し、受け入れ判断は親が行います。

## Install and launch

Git marketplace を登録して plugin を導入します。

```text
codex plugin marketplace add akitanabe/tugite
codex plugin add tugite@tugite
```

ローカル checkout を使う場合は repository root で `codex plugin marketplace add .agents/plugins` を実行してから `codex plugin add tugite@tugite` を実行します。導入後は Codex session を再起動してください。

Public skill は明示して起動します。

```text
$impl-lead <実装タスク>
$plan-craft <plan task>
$review-loop <artifact review task>
```

## Custom agents

`install/agents/*.toml` は配布素材です。user scope または project scope へ導入する前に状態を確認します。

新しい Codex session では `$install-custom-agents` を使って対象 scope の状態確認と導入を依頼できます。導入または更新後は session を再起動してください。

```text
plugins/codex/install/install-agents.sh --check --user
plugins/codex/install/install-agents.sh --check --repo <repo>
```

導入後は Codex session を再起動してください。既存定義を更新する場合は内容を確認してから `--force` を指定します。

## Source of truth

共通原稿は `shared/`（version は `shared/VERSION`）、platform 宣言は `declarations/`、契約は `contracts.toml`、Gunte 設定は `gunte.toml` が正本です。`gunte.toml` が管理する v5 workflow skill と `install/agents/*.toml` は生成物なので直接編集せず、正本変更後に repository root で次を実行します。

```text
gunte emit
gunte check
```

詳細は [ルート README](../../README.md) を参照してください。
