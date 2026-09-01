# Planning Core

Planning Core は top-level planning workflow が確立した理解と authority を Planning Synthesis と conditional nested `review-refine` へ接続する shared orchestration Method です。

## Input and synthesis

<!-- @contract planning-core-input-boundary -->
top-level planning workflow は一つの task-local Local Model の owner のまま、artifact responsibility、current projection、established direction、authority constraints、resolved evidence、review applicability、explicit opt-out を Planning Core へ渡す。
<!-- @/contract -->

Planning Core は supplied review applicability / opt-out を再判断せず、Local Model、candidate composition、advisor adjudication、final acceptance を所有しません。

<!-- @contract planning-core-synthesis-gap -->
Planning Synthesis が material input gap を返した場合、Planning Core は candidate、S0、review invocation を作らず、gap、candidate を作れない理由、affected semantics を caller-actionable result として返す。
<!-- @/contract -->

## Conditional review routing

<!-- @contract planning-core-review-routing -->
review nonapplicable または explicit opt-out では review を起動せず、applicable かつ opt-out なしの場合だけ S0 を作って nested `review-refine` へ進む。
<!-- @/contract -->

unreviewed route は semantic completion が成立すれば normal `final-candidate` を返せますが、review verified と表現しません。

review route では coherent candidate の content identity と immutable bytes を固定し、applicable existing syntactic / repository-native evidence を確認した S0 を作ります。S0 が成立しなければ `incomplete` と material reason を返します。

<!-- @contract planning-core-review-input -->
applicable review では parent projection、artifact-relative review purpose / criteria、authority obligations、S0、necessary evidence、required normal reviewer `plan-adversarial-reviewer`、`final_trim = applicable`、final trim の obligations / constraints / evidence context、`final_trim_reviewer = over-engineering-reviewer` を nested `review-refine` へ渡す。
<!-- @/contract -->

<!-- @contract planning-core-review-sequence -->
実装前 plan の品質順序は adversarial review、親裁定 / coherent refinement / verification / affected-semantics re-review、normal convergence、over-engineering final trim、Deletion Test / apply / verification である。
<!-- @/contract -->

required reviewer unavailable、normal review 未収束、verification 不成立、applicable final trim 未完了は `incomplete` にします。final trim が additive redesign を要する material defect を見つけた場合は normal review を再開せず、pre-trim verified candidate と `incomplete` を返します。

## Result boundary

<!-- @contract planning-core-result-boundary -->
reviewed / unreviewed route の semantic completion を満たす candidate は `final-candidate` として返し、review 実行の有無を保持し、返却 candidate を後処理で変更しない。
<!-- @/contract -->

candidate 成立前は candidate を捏造せず、verified snapshot がある場合だけ safest available candidate と material reason を返します。固定 Plan schema、review lifecycle state machine、pre-review structural gate、public workflow Skill は導入しません。
