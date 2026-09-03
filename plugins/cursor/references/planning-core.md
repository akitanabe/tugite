<!-- Generated from shared/. Do not edit directly. -->

# Planning Core

Planning Core は top-level planning workflow が確立した理解と authority を Planning Synthesis と conditional nested `review-refine` へ接続する shared orchestration Method です。

## Input and synthesis

top-level planning workflow は一つの task-local Local Model の owner のまま、artifact responsibility、current projection、established direction、authority constraints、resolved evidence、review applicability、explicit opt-out を Planning Core へ渡す。

Planning Core は supplied review applicability / opt-out を再判断せず、Local Model、candidate composition、advisor adjudication、final acceptance を所有しません。

## Final-trim necessity context

top-level planning workflow が渡した Local Model projection、established direction、authority constraints、resolved evidence から、Planning Core は
final trim の deletion judgment に必要な invocation-local necessity context を構成します。これは review-refine の `S0` や Local Model とは別の
ephemeral Data であり、candidate ごとの固定対応表、persistent ledger、固定 serialized schema にはしません。

Planning Core は final-trim 用 necessity context を構成・所有し、`required outcomes / obligations`、`binding decisions / must-preserve concepts`、`current scope / explicit excludes`、`permitted-but-optional` を意味上区別し、各分類を deletion judgment に必要な意味と bounded provenance とともに保持する。

必要性の各分類は、単なる source reference ではなく、削除判断に必要な意味そのものを持ちます。
`required outcomes / obligations` は成立させる結果と義務、`binding decisions / must-preserve concepts` は変更・削除してはならない方向と概念、
`current scope / explicit excludes` は今回の対象と明示的な対象外、`permitted-but-optional` は許容されるが必須ではない要素を表します。

necessity context は `S0` と別の invocation-local Data とし、projection integrity が安全に成立せず omission が deletion judgment を変え得る場合、Planning Core は review-refine を起動せず `incomplete` を返す。

Planning Core は review-refine の起動前に projection integrity を判断します。利用可能な context を確認した結果、該当する意味がないことと、
安全に投影できず判断できないことを区別します。後者が削除判断を変え得る場合は review を起動せず、投影不足の理由を付けて `incomplete` を返します。

final-trim の comparison frame は `review target = final-trim stage の latest verified candidate 全体`、`comparison base = plan がまだ存在しない no-plan state` とし、`S0` を base にしない。

initial synthesis、adversarial review、refinement で導入された material element も同じ frame で評価します。
no-plan state は invocation-local Data であり、persistent baseline や schema にはしません。

necessity semantics と comparison-frame selection rule は review-refine 起動時に固定し、invocation 中の normal refinement では変更せず、final trim 前に current evidence に対する validity を再確認する。その再確認から `caller-owned final-trim validity / stop result` を構成して review-refine へ渡し、進行可能なら current verified state の repository evidence / remaining witness を併せて保持し、binding direction、scope、authority の material change なら pre-trim latest verified candidate と `incomplete` の stop result を保持する。

Planning Synthesis が material input gap を返した場合、Planning Core は candidate、S0、review invocation を作らず、gap、candidate を作れない理由、affected semantics を caller-actionable result として返す。

## Conditional review routing

review nonapplicable または explicit opt-out では review を起動せず、applicable かつ opt-out なしの場合だけ S0 を作って nested `review-refine` へ進む。

unreviewed route は semantic completion が成立すれば normal `final-candidate` を返せますが、review verified と表現しません。

review route では coherent candidate の content identity と immutable bytes を固定し、applicable existing syntactic / repository-native evidence を確認した S0 を作ります。S0 が成立しなければ `incomplete` と material reason を返します。

applicable review では parent projection、artifact-relative review purpose / criteria、authority obligations、S0、necessary evidence、required normal reviewer `plan-adversarial-reviewer`、`final_trim = applicable`、final-trim necessity context（final trim の obligations / constraints / evidence context の plan-family における具体形であり、final trim の唯一の意味 input）、`final_trim_reviewer = over-engineering-reviewer` を nested `review-refine` へ渡す。

実装前 plan の品質順序は adversarial review、親裁定 / coherent refinement / verification / affected-semantics re-review、normal convergence、over-engineering final trim、Deletion Test / apply / verification である。

required reviewer unavailable、normal review 未収束、verification 不成立、applicable final trim 未完了は `incomplete` にします。final trim が additive redesign を要する material defect を見つけた場合は normal review を再開せず、pre-trim verified candidate と `incomplete` を返します。

## Result boundary

reviewed / unreviewed route の semantic completion を満たす candidate は `final-candidate` として返し、review 実行の有無を保持し、返却 candidate を後処理で変更しない。

candidate 成立前は candidate を捏造せず、verified snapshot がある場合だけ safest available candidate と material reason を返します。固定 Plan schema、review lifecycle state machine、pre-review structural gate、public workflow Skill は導入しません。
