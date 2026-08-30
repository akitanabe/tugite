<!-- Generated from shared/. Do not edit directly. -->

# Planning Core

Planning Core は、top-level planning workflow が確立した理解と authority を Planning Synthesis と nested `review-refine` へ接続する
shared plan-family orchestration Method です。public workflow、別の planning engine、Local Model の owner ではありません。

## Input and ownership

top-level planning workflow は一つの task-local Local Model の owner のまま、current planning projection、established direction、authority constraints、resolved upstream evidence を Planning Core へ渡す。

Planning Core、Planning Synthesis、nested `review-refine`、reviewer は supplied projection をそれぞれの責務に必要な範囲で使い、独立した
Local Model を構築しません。direction と authority constraints は downstream obligation であり、suggestion、review finding、局所的な
改善都合によって変更、拡張、緩和しません。

## Planning Synthesis connection

Planning Core は同じ directory の `planning-synthesis.md` が定める Planning Synthesis に、current planning projection、established
direction、authority constraints、resolved upstream evidence を渡します。Planning Synthesis の planning judgment、bounded advisory、result
boundary はその Method に残し、Planning Core は candidate composition や advisor adjudication を重複所有しません。

Planning Synthesis が material input gap を返した場合、Planning Core は candidate、S0、review invocation を作らず `incomplete` と gap を返す。

coherent candidate が返された場合だけ、Planning Core は review target の準備へ進みます。material gap を plausible guess や placeholder
candidate で埋めず、gap の resolution route を自律的に開始しません。

## S0 baseline preparation

Planning Core は coherent candidate の content identity と immutable bytes を固定し、content consistency と applicable existing syntactic / repository-native structural evidence を確認した S0 を作るが、Plan quality または semantic verification の完了を主張しない。

baseline preparation は review 中の observation target を安定させるための Action です。identity algorithm、Plan serialization、固定 schema を
導入せず、candidate に適用できる既存 verification surface だけを使います。baseline evidence が成立しなければ review-ready と扱わず、
`incomplete` と material reason を返します。

`S0 verified` は immutable review baseline としての成立を意味し、Acceptance Criteria、architecture、review sufficiency、minimality、最終的な
Plan verification を意味しません。Planning Core はこの境界で `structural-health-gate` その他の pre-review quality gate を起動しません。

## Nested review

Planning Core が nested `review-refine` へ渡す fixed review purpose は次のとおりです。

> established planning direction と authority constraints の内側で、downstream implementer が goal、direction、acceptance boundary を
> 再設計せずに実行・受入できる Plan candidate にする。

review criteria は、current task に material な範囲で次を含みます。

- required work と semantic dependency の存在と coherence
- established direction 内に閉じた scope
- externally observable な Acceptance Criteria
- planned behavior に対して executable で sufficient な verification
- 必要な failure / rollback boundary
- internal contradiction と execution blocker の不存在
- downstream implementer による goal / direction / acceptance semantics の再設計が不要であること

Planning Core は parent projection、fixed review purpose / criteria、direction / authority obligations、S0、necessary evidence、required normal reviewer `plan-adversarial-reviewer`、`final_trim = applicable`、`final_trim_reviewer = over-engineering-reviewer` を nested `review-refine` へ渡す。

caller-supplied operational bound がある場合はその Data を改変せず渡します。未指定時は新しい public input、欠落 error、canonical round count を
作らず、`review-refine` が invocation 開始時に所有する bounded execution condition を使います。

品質順序は adversarial strengthening、adjudication / coherent refinement / verification / bounded affected-semantics re-review、normal convergence、over-engineering final trim、Deletion Test / apply / verification である。

normal review では `plan-adversarial-reviewer` を initial round と refinement 後の affected semantics / relevant dependencies の re-review に
必須とします。normal convergence 前に final trim を起動せず、二つの reviewer を initial S0 に並列起動しません。

normal convergence 後は `over-engineering-reviewer` を置換不可の mandatory final-trim reviewer として使います。removal candidate の採否、
Deletion Test Method、apply、verification、verified snapshot の更新は `review-refine` に残します。final trim が normal review の再開を必要とする
pre-existing material additive defect を露出した場合、final trim が設計を追加せず、unsafe working state を昇格せず、pre-trim latest verified
candidate と `incomplete` を返します。final trim から normal loop へ戻りません。

## Result boundary

`review-refine` の `converged` は final verified Plan candidate として吸収し、`incomplete` は latest verified candidate があれば material reason とともに返し、返却 candidate を後処理で変更しない。

required reviewer が利用できない、current authority 内で normal review を完了できない、verification が閉じない、mandatory final trim を完了
できない場合も `incomplete` とします。candidate 成立前なら candidate を捏造せず、verified snapshot がある場合だけ safest available candidate
として返します。Planning Core 固有の詳細な termination taxonomy は作りません。

`review-refine` から受け取った candidate は caller が見る candidate と同一です。Planning Core は返却後に edit、polish、rewrite、normalize、
serialize その他の mutation を行いません。

## Representative cases

### Strengthen then trim

weakness と excess を持つ coherent candidate は adversarial refinement が converged した後だけ mandatory final trim と Deletion Test を通り、verified final candidate になる。

### Synthesis material gap

coherent candidate を妨げる synthesis gap は speculative candidate と review Action を生まず、candidate なしの `incomplete` になる。

### Adversarial review incomplete

current authority 内で解決できない normal finding は direction を変更せず、latest verified candidate と material reason を持つ `incomplete` になる。

### Additive defect during final trim

final trim が additive redesign を要する material defect を見つけた場合、normal review を再開せず、unsafe trim を昇格せず、pre-trim verified candidate と `incomplete` を返す。

### Authority and Local Model preservation

全 consumer と reviewer は parent projection と direction / authority obligations を使い、top-level workflow が唯一の task-local Local Model owner のままである。

## Responsibility boundary

Planning Core は orchestration、S0 baseline preparation、nested input、ordered reviewer topology、outward result mapping を所有します。
Planning Synthesis の candidate judgment、`review-refine` の review / adjudication / refinement / verification / completion、Deletion Test Method の
observation、reviewer finding の採否、top-level workflow の Local Model / authority / persistence / final Plan acceptance は所有しません。

固定 Plan schema、review-context schema、別 Local Model、planning lifecycle state machine、Authority Integrity Verification、pre-review
`structural-health-gate`、public workflow Skill、他の reviewer inventory を導入しません。
