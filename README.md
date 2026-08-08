# Tugite v5.1.0

Tugite は Claude Code と Codex のための v5 workflow plugin です。親エージェントが要求を Work Unit に正規化し、必要な worker へ実装を依頼し、親 QA と最終検証まで責任を持ちます。

## 現行 surface

### Public skill

- `impl-lead`: Work Unit の intake、direct または worker の route、TDD、risk-directed review、親 QA、final writing gate を扱う実装 workflow です。明示起動時だけ使います。
- `plan-craft`: 要求と repository の観測から実装 plan の candidate を作り、bounded review と親の裁定へ渡します。
- `review-loop`: 不変 snapshot を bounded round で review し、finding の採否と受け入れを呼び出し元の親へ返します。

### Internal skill

`proposal`、`structural-health-gate`、`work-unit-design` は public workflow の同じ親 context で使う internal skill です。直接起動や暗黙の workflow 切替は行いません。

### Worker / reviewer / advisor

Work Unit worker は `focused-implementer`、`implementer`、`senior-implementer`、`expert-implementer` です。

Risk-directed reviewer は `plan-adversarial-reviewer`、`responsibility-boundary-reviewer`、`test-quality-reviewer`、`over-engineering-reviewer`、`security-side-effect-reviewer`、`writing-principles-reviewer` です。`writing-principles-reviewer` は run closeout の final writing gate として使います。

Plan の品質を read-only で助言する advisor は `plan-quality-advisor` です。reviewer と advisor は判断材料を返し、最終受け入れは親エージェントが行います。

## 正本と生成

skill と agent の正本は `shared/`、version は `shared/VERSION`、Codex/Claude の宣言正本は `declarations/`、契約 registry は `contracts.toml`、Gunte project 設定は `gunte.toml` です。`gunte.toml` が管理する `plugins/` 以下の生成対象は直接編集しません。

変更後は repository root で次を実行します。

```text
gunte emit
gunte check
```

## 導入と起動

- [Claude Code plugin](plugins/claude/README.md)
- [Codex plugin](plugins/codex/README.md)

Claude Code では `/tugite:impl-lead`、`/tugite:plan-craft`、`/tugite:review-loop` を明示して起動します。Codex では `$impl-lead`、`$plan-craft`、`$review-loop` を明示して起動します。internal skill はこれらの public workflow が同じ親 context 内で使用します。

親エージェントは変更前の状態、AC、scope、依存、diff、テスト結果を確認し、Green を再現できるときだけ受け入れます。

## License

MIT License. See [LICENSE](LICENSE).
