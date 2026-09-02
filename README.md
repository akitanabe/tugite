<!-- @contract cursor-readme-title -->
# Tugite v7.1.0
<!-- @/contract -->

Tugite は Claude Code、Codex、Cursor のための実装ワークフロープラグインです。親エージェントが要求を Implementation Unit に正規化し、必要な worker へ実装を依頼し、親 QA と最終検証まで責任を持ちます。

## 現行の構成

### 公開 skill

- `how-it`: 未確定な request の前提、選択肢、成立条件を Human とともに構築し、current understanding を requested output へ接続します。明示起動時だけ使います。
- `explorer-this`: Agentic Model Construction を first route とする探索 workflow で、Human-owned material gap の場合だけ Interactive Model Construction を利用します。明示起動時だけ使います。
- `impl-lead`: implementation work を execution 前の Implementation Unit へ正規化し、実装、Parent QA、受入、final verification、安全な統合まで所有します。明示起動時だけ使います。
- `plan-agent`: normal context から request-relative な自由形式 planning / design artifact を recommendation-first で作り、必要な場合だけ review します。
- `review-refine`: 不変 snapshot を指定回数の範囲でレビューし、指摘の採否と受け入れ結果を呼び出し元の親へ返します。

`plan-agent` は review applicability と explicit opt-out を判断し、nonapplicable / opt-out は unreviewed の normal final-candidate、applicable / no opt-out は strict review route へ進みます。

### Worker / reviewer / advisor

Implementation Unit worker は `focused-implementer`、`implementer`、`senior-implementer`、`expert-implementer` です。

<!-- @contract readme-risk-directed-static-performance-reviewer -->
リスクに応じて選択する reviewer は `plan-adversarial-reviewer`、`responsibility-boundary-reviewer`、`test-quality-reviewer`、`over-engineering-reviewer`、`security-side-effect-reviewer`、`static-performance-reviewer`、`writing-principles-reviewer` です。`writing-principles-reviewer` は実行終了時の最終文章レビューとして使います。
<!-- @/contract -->

Plan の品質について読み取り専用で助言する advisor は `plan-quality-advisor` です。reviewer と advisor は判断材料を返し、最終受け入れは親エージェントが行います。

## 導入と起動

- [Claude Code plugin](https://github.com/akitanabe/tugite/blob/main/plugins/claude/README.md)
- [Codex plugin](https://github.com/akitanabe/tugite/blob/main/plugins/codex/README.md)
- [Cursor plugin](https://github.com/akitanabe/tugite/blob/main/plugins/cursor/README.md)

Claude Code では `/tugite:how-it`、`/tugite:explorer-this`、`/tugite:impl-lead`、`/tugite:plan-agent`、`/tugite:review-refine`、Codex では `$how-it`、`$explorer-this`、`$impl-lead`、`$plan-agent`、`$review-refine` を明示して起動できます。

<!-- @contract cursor-readme-boundary -->
### Cursor local plugin

Cursor では Git の main 先端にある `plugins/cursor` を user scope の `~/.cursor/plugins/local/tugite` へ copy して導入します。symlink は使いません。既存の local plugin がある場合は内容を確認してから `--force` / `-Force` で置き換えてください。導入後は Cursor を再起動するか `Developer: Reload Window` を実行して再読込します。

Linux / macOS / WSL / Git Bash:

```text
plugins/cursor/install/install-plugin.sh --user
plugins/cursor/install/install-plugin.sh --check --user
plugins/cursor/install/install-plugin.sh --force --user
```

Windows PowerShell:

```text
plugins/cursor/install/install-plugin.ps1 -User
plugins/cursor/install/install-plugin.ps1 -Check -User
plugins/cursor/install/install-plugin.ps1 -Force -User
```

一度導入したあとは、新しい Cursor session で `/install-plugin` を使い、状態確認と更新を依頼できます。更新後は Cursor を再起動するか `Developer: Reload Window` を実行してください。

repository checkout を直接検証する場合は、repository root で次を実行します。

```text
agent --plugin-dir plugins/cursor
```

public skill は次のコマンドで明示起動できます。

```text
/how-it <相談したい進め方>
/explorer-this <探索タスク>
/impl-lead <実装タスク>
/plan-agent <plan task>
/review-refine <artifact review task>
/install-plugin
```

Cursor 用 Marketplace 配布はこの version の対象外です。
<!-- @/contract -->

親エージェントは変更前の状態、受け入れ条件（AC）、対象範囲、依存関係、差分、テスト結果を確認し、Green（全テスト成功）を再現できるときだけ受け入れます。

## License

MIT License. See [LICENSE](https://github.com/akitanabe/tugite/blob/main/LICENSE).
