# Issue #215 mutation evidence

この証跡は一時copy内でsourceと対象generated outputを同期させ、`gunte.lock.json` が必要なstateではそのstateで再生成して取得した。byte drift、lock drift、削除済みpredicate、未使用sliceなどの無関係failureは期待diagnosticに数えていない。

## Red → Green → Refactor

| phase | state identity | target | mutation | expected | actual diagnostic | exit |
| --- | --- | --- | --- | --- | --- | ---: |
| Red: current defect | `96ade388b92eca8298213ad7ffaba2741774d6ed` + synced mutation | Claude | run-owned loaderの「作成 Action より前に」を同義の「作成 Action に先立ち」へ変更 | 意味不変なのでGreenであるべき | `impl-run-owned-lifecycle-loader-requires-11ecfc78e5d5` `requires_violation` | 1 |
| Red: current defect | 同上 | Codex | 同上 | 意味不変なのでGreenであるべき | `impl-run-owned-lifecycle-loader-requires-11ecfc78e5d5` `requires_violation` | 1 |
| Red: replacement test | final inventory `1df3100a…` から `impl-run-owned-loader-data-81ec1c69764c` と `advisor-return-fields-data-eb3fb802df39` を除き、対応slice markerを診断対象外にしてlock同期 | Claude | loader `failure=continue` + advisor field `evidence` 削除 | 新しいobligation diagnosticが必要 | diagnosticなし（old prose predicateもなし） | 0 |
| Red: replacement test | 同上 | Codex | 同上 | 新しいobligation diagnosticが必要 | diagnosticなし（old prose predicateもなし） | 0 |
| Green: clean | final inventory `sha256:1df3100a2e5c8f8c8368afa086a107362d65f7d45c3ccf1375939cac3728378c` | Claude | なし | Green | diagnosticなし | 0 |
| Green: clean | 同上 | Codex | なし | Green | diagnosticなし | 0 |
| Green: nonsemantic | 同上からsourceをrewordし`gunte emit`で同期 | Claude | batch/impl/approval/plan/workersの5 domainで、Data/structured fieldを変えない同義reword | Green | diagnosticなし | 0 |
| Green: nonsemantic | 同上 | Codex | 同上 | Green | diagnosticなし | 0 |
| Green: structure | 同上 + synced mutation | Claude | run-owned loader Dataの`failure = stop-incomplete`を`continue`へ反転 | replacementだけがFail | `impl-run-owned-loader-data-81ec1c69764c` `requires_violation` | 1 |
| Green: structure | 同上 | Codex | 同上 | replacementだけがFail | `impl-run-owned-loader-data-81ec1c69764c` `requires_violation` | 1 |
| Green: external Data | 同上 + synced mutation | Claude | advisor `insight_fields`から`evidence`を削除 | replacementだけがFail | `advisor-return-fields-data-eb3fb802df39` `requires_violation` | 1 |
| Green: external Data | 同上 | Codex | 同上 | replacementだけがFail | `advisor-return-fields-data-eb3fb802df39` `requires_violation` | 1 |
| Green: delete / remaining keep-bounded | 同上 + synced mutation | Claude | run-owned referenceの必須headingを`Default`から`Standard`へ変更 | replacementを新設せずremaining witnessがFail | `impl-run-owned-default-requires-24af2bb38936` `requires_violation`; `impl-run-owned-default-occurrences` expected 1 / actual 0 | 1 |
| Green: delete / remaining keep-bounded | 同上 | Codex | 同上 | replacementを新設せずremaining witnessがFail | 同じ2 diagnostic | 1 |
| Green: keep-exact | 同上 + synced mutation | Claude | structured transition Dataの`advisor #1`を`advisor #one`へ破壊 | exact Data predicateがFail | `proposal-two-pass-flow-417135ee9357` `requires_violation` | 1 |
| Green: keep-exact | 同上 | Codex | 同上 | exact Data predicateがFail | `proposal-two-pass-flow-417135ee9357` `requires_violation` | 1 |

Refactor後のcontractは、loader/role/return interfaceをcoherent Dataへ集約し、同じ関係を短いsubstringへ再分割していない。実行上意味のある既存anchor orderだけを維持した。

## EVAL disposition

EVALへ移したsemantic predicateには決定論的substring mutationを設定しない。case identityとtargeted resultは次のとおりであり、各baseline recordの詳細はCSVの `applicable_mutation_or_nonapplicable_reason` に記録した。

| case identity | target | targeted result |
| --- | --- | --- |
| `review-loop-batch-resolution` | Claude / Codex | A〜Iでapplicability、fixed Batch、全件裁定、coherent partition、verify/progress/promotion、isolate、corrective evidence、caller/counterpart boundaryを区別する |
| `proposal-bounded-advisor-adjudication` | Claude / Codex | advisor observationをtransaction外に置き、fixed Batchを裁定してverified candidateだけを更新する |
| `proposal-dialogue-verified-resolution-cycle` | Claude / Codex | Human binding decisionを一件apply/verify後にだけsnapshotへ反映しfrontierを再評価する |
| `plan-craft-approval-final-handoff` | Claude / Codex | nonsemantic reword、Human confirmation、局所reopen、全体再策定をA〜Dで区別する |
| `necessity-kernel-necessary` / `unnecessary` / `indeterminate` | Claude / Codex | Broken Obligation、remaining witness、不足evidenceを既存Dataで返し、agentが採否・新verdictを持たない |

これらのmanual EVAL runtimeはこのWork Unitでは実行していない。case definitionとtargeted oracleの静的整合を追加・再照合したが、実モデルの結果は未検証である。
