# Tugite for Claude Code

Tugite v5.22.0 は、親 Claude エージェントが plan、Work Unit の route、QA、受け入れ、最終検証を保持しながら実装を worker へ依頼する plugin です。

## Skill surface

Public skill は次の5つです。

- `impl-lead`: Work Unit を正規化し、direct または worker の実装、TDD、必要な risk-directed review、親 QA、final writing gate を進めます。
- `plan-craft`: 要求と repository の観測から plan candidate を作り、bounded review と親の裁定へ渡します。
- `plan-craft-approval`: 人間と方向性を確定した candidate を structural gate と固定 review へ渡します。
- `review-loop`: 不変 artifact snapshot を bounded round で review し、finding と evidence を親へ返します。
- `clarify-it`: 明示指定、または対話しながら設計・方針・判断を段階的に明確化する意図が明確な依頼で、現在の意思決定モデルへ再統合して返します。成果物や Issue の編集、実装、後続 Action は実行しません。

`plan-craft` は適用可能なら既定 review を行い、明示的な review skip は通常の起草確定へ進みます。`plan-craft-approval` は適用可能なら固定 review を行い、明示的な skip は未完了として返します。両者とも既定 `plan-adversarial-reviewer` が非適用なら `review-loop` を bypass して通常の起草確定へ進みます。

`proposal`、`structural-health-gate`、`work-unit-design` は public workflow の同じ親 context だけで使う internal skill です。直接の user invocation は受け付けません。

## Agent surface

Worker は `focused-implementer`、`implementer`、`senior-implementer`、`expert-implementer` です。

Reviewer は `plan-adversarial-reviewer`、`responsibility-boundary-reviewer`、`test-quality-reviewer`、`over-engineering-reviewer`、`security-side-effect-reviewer`、`writing-principles-reviewer` です。`writing-principles-reviewer` は final writing gate に使います。

Advisor は read-only の `plan-quality-advisor` です。reviewer と advisor は evidence を返し、受け入れ判断は親が行います。

## Install and launch

Claude Code で marketplace を登録し、plugin を導入します。

```text
/plugin marketplace add akitanabe/tugite
/plugin install tugite@tugite
/reload-plugins
```

導入後、public skill は次のコマンドで明示起動できます。

```text
/tugite:impl-lead <実装タスク>
/tugite:plan-craft <plan task>
/tugite:plan-craft-approval <human-directed plan task>
/tugite:review-loop <artifact review task>
/tugite:clarify-it <clarification task>
```

`clarify-it` は明示指定がなくても、対話しながら段階的に明確化する意図が明確な依頼に適用できます。

## Source of truth

共通原稿は `shared/`（version は `shared/VERSION`）、platform 宣言は `declarations/`、契約は `contracts/*.toml`、Gunte 設定は `gunte.toml` が正本です。`plugins/claude` の skill と agent は生成物なので直接編集せず、正本変更後に repository root で次を実行します。

```text
gunte emit
gunte check
```

詳細は [ルート README](../../README.md) を参照してください。
