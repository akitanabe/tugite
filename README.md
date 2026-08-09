# Tugite v5.4.0

Tugite は Claude Code と Codex のための v5 実装ワークフロープラグインです。親エージェントが要求を Work Unit に正規化し、必要な worker へ実装を依頼し、親 QA と最終検証まで責任を持ちます。

## 現行の構成

### 公開 skill

- `impl-lead`: Work Unit の受け付け、親エージェントによる直接実装または worker への振り分け、TDD、リスクに応じたレビュー、親 QA、最終文章レビューを扱う実装ワークフローです。明示起動時だけ使います。
- `plan-craft`: 要求とリポジトリの観測から実装 plan の候補を作り、回数を制限したレビューと親の裁定へ渡します。
- `plan-craft-approval`: 人間と方向性を確定した候補を構造 gate と固定レビューへ渡す、人間参加型の計画ワークフローです。
- `review-loop`: 不変 snapshot を指定回数の範囲でレビューし、指摘の採否と受け入れ結果を呼び出し元の親へ返します。

`plan-craft` は適用可能なら既定 review を行い、明示的な review skip は通常の起草確定へ進みます。`plan-craft-approval` は適用可能なら固定 review を行い、明示的な skip は未完了として返します。両者とも既定 `plan-adversarial-reviewer` が非適用なら `review-loop` を bypass して通常の起草確定へ進みます。

### 内部 skill

`proposal`、`proposal-dialogue`、`structural-health-gate`、`work-unit-design` は公開ワークフローと同じ親エージェントのコンテキストで使う内部 skill です。直接起動や暗黙のワークフロー切替は行いません。

### Worker / reviewer / advisor

Work Unit worker は `focused-implementer`、`implementer`、`senior-implementer`、`expert-implementer` です。

リスクに応じて選択する reviewer は `plan-adversarial-reviewer`、`responsibility-boundary-reviewer`、`test-quality-reviewer`、`over-engineering-reviewer`、`security-side-effect-reviewer`、`writing-principles-reviewer` です。`writing-principles-reviewer` は実行終了時の最終文章レビューとして使います。

Plan の品質について読み取り専用で助言する advisor は `plan-quality-advisor` です。reviewer と advisor は判断材料を返し、最終受け入れは親エージェントが行います。

## 正本と生成

skill と agent の正本は `shared/`、バージョンは `shared/VERSION`、Codex/Claude の宣言定義の正本は `declarations/`、契約レジストリは `contracts/*.toml`、Gunte のプロジェクト設定は `gunte.toml` です。source と生成物の inventory、構造、byte drift は `gunte check` が検証します。

変更後はリポジトリのルートで次を実行します。

```text
gunte emit
gunte check
```

## 導入と起動

- [Claude Code plugin](plugins/claude/README.md)
- [Codex plugin](plugins/codex/README.md)

Claude Code では `/tugite:impl-lead`、`/tugite:plan-craft`、`/tugite:plan-craft-approval`、`/tugite:review-loop` を明示して起動します。Codex では `$impl-lead`、`$plan-craft`、`$plan-craft-approval`、`$review-loop` を明示して起動します。内部 skill は、これらの公開ワークフローが同じ親エージェントのコンテキスト内で使用します。

親エージェントは変更前の状態、受け入れ条件（AC）、対象範囲、依存関係、差分、テスト結果を確認し、Green（全テスト成功）を再現できるときだけ受け入れます。

## License

MIT License. See [LICENSE](LICENSE).
