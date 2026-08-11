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
| Green: F2 out-of-slice | final inventory `2d34e621…` + synced mutation `sha256:a3734656207b13c9e833f95ac0c08be1c861f8521104b576aa81bfe1a5e2fd4e` | Claude | run-owned Loader Data全体を`impl-run-owned-lifecycle-loader` slice直前へ移動し、source/generated/lockを同期 | replacementだけがFail | `impl-run-owned-loader-data-81ec1c69764c` `requires_violation`のみ。byte/lock/unused span/old predicate diagnosticなし | 1 |
| Green: F2 out-of-slice | 同上 | Codex | 同上 | replacementだけがFail | `impl-run-owned-loader-data-81ec1c69764c` `requires_violation`のみ。byte/lock/unused span/old predicate diagnosticなし | 1 |
| Green: F3 exact policy Data | final inventory `2d34e621…` + synced mutation `sha256:7c0cae6005646dcdacc590ed7d1d73a79a786c05dda6d4492d38a61576418bf1` | agents-guidance | `common_evidence`のcommon parent oracleをvariant別へ反転 | 新canonical predicateがFail | `repository-test-qa-baseline-a0b98d2f7393` `requires_violation`のみ | 1 |
| Green: F3 exact policy Data | 同上 | claude-guidance | 同上 | 新canonical predicateがFail | `repository-test-qa-baseline-a0b98d2f7393` `requires_violation`のみ | 1 |
| Green: F4 sole-source prose | final inventory `sha256:2d34e621a429cfa3a323f1c004023c1568f37bea5799acd24739728de85eb4ea` | Claude | proposal/review-loop/impl-lead/proposal-dialogue/advisorの列挙値を変えず、Data参照のAction/失敗処理proseへreword | Green | diagnosticなし | 0 |
| Green: F4 sole-source prose | 同上 | Codex | 同上 | Green | diagnosticなし | 0 |
| Green: F5 ownership Data | final inventory `2d34e621…` + synced mutation `sha256:5fbcef3aa40e403ef27276e0c72d256c57f25148969504dd8caf5089fe5b9fbf` | Claude | `caller_owns`の`workflow completion`を`kernel workflow completion`へ破壊 | 新predicateだけがFail | `batch-resolve-ownership-data-fc45b9ecc23c` `requires_violation`のみ | 1 |
| Green: F5 ownership Data | 同上 | Codex | 同上 | 新predicateだけがFail | `batch-resolve-ownership-data-fc45b9ecc23c` `requires_violation`のみ | 1 |
| Green: resolution batch clean | final inventory `sha256:2d34e621a429cfa3a323f1c004023c1568f37bea5799acd24739728de85eb4ea` | Claude | なし | Green | diagnosticなし | 0 |
| Green: resolution batch clean | 同上 | Codex | なし | Green | diagnosticなし | 0 |

Refactor後のcontractは、loader/role/return interfaceをcoherent Dataへ集約し、Data blockを列挙値の唯一の正本として、直後proseをfield参照のAction/失敗処理へ整理した。同じ関係を短いsubstringへ再分割せず、実行上意味のある既存anchor orderだけを維持した。

## EVAL disposition

EVALへ移したsemantic predicateには決定論的substring mutationを設定しない。case identityとtargeted resultは次のとおりであり、各baseline recordの詳細はCSVの `applicable_mutation_or_nonapplicable_reason` に記録した。

| case identity | target | targeted result |
| --- | --- | --- |
| `review-loop-batch-resolution` | Claude / Codex | A〜Nでapplicability、fixed Batch、全件裁定、coherent partition、verify/progress/promotion、isolate、corrective evidence、caller/counterpart boundaryを区別し、J〜Nでbinding適用外、部分authority、no-progress、外部evidence、後続failureを個別に判定する |
| `test-qa-baseline-route-independent` | Claude / Codex | `E-P` / `E-N` / `E-M`を各A〜D間で固定し、12 subvariantすべてでparent oracle `O-parent`を共有する |
| `proposal-bounded-advisor-adjudication` | Claude / Codex | advisor observationをtransaction外に置き、fixed Batchを裁定してverified candidateだけを更新する |
| `proposal-dialogue-verified-resolution-cycle` | Claude / Codex | Human binding decisionを一件apply/verify後にだけsnapshotへ反映しfrontierを再評価する |
| `plan-craft-approval-final-handoff` | Claude / Codex | nonsemantic reword、Human confirmation、局所reopen、全体再策定をA〜Dで区別する |
| `necessity-kernel-necessary` / `unnecessary` / `indeterminate` | Claude / Codex | Broken Obligation、remaining witness、不足evidenceを既存Dataで返し、agentが採否・新verdictを持たない |

これらのmanual EVAL runtimeはこのWork Unitでは実行していない。case definitionとtargeted oracleの静的整合を追加・再照合したが、実モデルの結果は未検証である。
