<!-- Generated from shared/. Do not edit directly. -->

# Tugite for Claude Code

Tugite は Claude Code、Codex、Cursor 向けに複数の public workflow、agent、skill を配布する plugin です。各 workflow は固有の責務境界と起動条件に従い、必要に応じて agent、reviewer、advisor を組み合わせます。

## 現行の構成

### 公開 skill

- `how-it`: 未確定な request の前提、選択肢、成立条件を Human とともに構築し、current understanding を requested output へ接続します。明示起動時だけ使います。
- `explorer-this`: Agentic Model Construction を first route とする探索 workflow で、Human-owned material gap の場合だけ Interactive Model Construction を利用します。明示起動時だけ使います。
- `impl-lead`: implementation work を execution 前の Implementation Unit へ正規化し、実装、Parent QA、受入、final verification、安全な統合まで所有します。明示起動時だけ使います。
- `plan-agent`: normal context から request-relative な自由形式 planning / design artifact を recommendation-first で作り、必要な場合だけ review します。明示起動時だけ使います。
- `wayfind`: Destination 全体の Planning Fog と Decision blocker を解像し、1..N の self-contained な Work Units を返します。明示起動時だけ使います。
- `test-report`: 指定範囲を静的に観測し、独立 grounding できた Expected Observation と Case / Evidence の対応、および grounding できない場合の limitation を、評価や remediation なしで Verification Topology として報告します。
- `test-verify`: 明示された bounded test target を grounded runtime evidence で検証し、target-causal Problem だけを直接修復して Completion Gate と final verification まで閉じます。明示起動時だけ使います。
- `review-refine`: 不変 snapshot を指定回数の範囲でレビューし、指摘の採否と受け入れ結果を呼び出し元の親へ返します。

`plan-agent` は review applicability と explicit opt-out を判断し、nonapplicable / opt-out は unreviewed の normal final-candidate、applicable / no opt-out は `plan-adversarial-reviewer` と `over-engineering-reviewer` を使う strict review route へ進みます。

### Worker / reviewer / advisor

Implementation Unit worker は `focused-implementer`、`implementer`、`senior-implementer`、`expert-implementer` です。

リスクに応じて選択する reviewer は `plan-adversarial-reviewer`、`responsibility-boundary-reviewer`、`test-quality-reviewer`、`over-engineering-reviewer`、`security-side-effect-reviewer`、`static-performance-reviewer`、`writing-principles-reviewer` です。`writing-principles-reviewer` は実行終了時の最終文章レビューとして使います。

Plan の品質について読み取り専用で助言する advisor は `plan-quality-advisor` です。reviewer と advisor は判断材料を返し、最終受け入れは親エージェントが行います。

## Install and launch

Claude Code で marketplace を登録し、plugin を導入します。

```text
/plugin marketplace add akitanabe/tugite
/plugin install tugite@tugite
/reload-plugins
```

導入後、public skill は次のコマンドで明示起動できます。

```text
/tugite:how-it <相談したい進め方>
/tugite:explorer-this <探索タスク>
/tugite:impl-lead <実装タスク>
/tugite:plan-agent <plan task>
/tugite:wayfind <destination>
/tugite:test-report <test scope>
/tugite:test-verify <test target>
/tugite:review-refine <artifact review task>
```


親エージェントは変更前の状態、受け入れ条件（AC）、対象範囲、依存関係、差分、テスト結果を確認し、Green（全テスト成功）を再現できるときだけ受け入れます。

## License

MIT License. See [LICENSE](https://github.com/akitanabe/tugite/blob/main/LICENSE).
