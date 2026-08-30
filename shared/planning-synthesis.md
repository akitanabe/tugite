# Planning Synthesis

Planning Synthesis は、plan-family が確定済みの方向を実行可能で coherent な Plan candidate へ構成するための共有 Method です。
単なる formatter ではなく、与えられた authority の内側で必要な planning judgment を担います。

## Input and ownership

<!-- @contract planning-synthesis-input-boundary -->
caller は一つの task-local Local Model の owner のまま、planning に必要な current understanding、established planning direction、authority constraints、必要なら upstream Researcher evidence を Data として渡す。
<!-- @/contract -->

current understanding は current task に planning-relevant な projection であり、Planning Synthesis は別の Local Model を構築しません。
planning direction、authority constraints、Researcher evidence に固定 serialized schema や永続 artifact は要求しません。Researcher
evidence が supplied input に含まれる場合は、observed evidence、source basis、bounded inference、limitation など、upstream ですでに
成立している区別を判断材料として維持します。

Planning Synthesis は repository exploration、research、Researcher invocation、Model Construction、Human clarification を行いません。
追加 evidence が material に必要なら、取得経路を自分で開始せず、具体的な gap を caller へ返します。

## Synthesis responsibility

established direction の内側で、current task に必要な次の planning semantics を自律的に判断します。

- work decomposition
- ordering と semantic dependency
- established direction 内の work scope
- 外部から観測可能な Acceptance Criteria
- repository-native な verification strategy
- material に必要な risk と rollback boundary
- requested planning artifact に適した composition

これらは複数の受容可能な結果から current task に coherent な構成を選ぶ planning judgment です。固定 procedure、score、required section
一覧、expected-output oracle へ変換しません。実装者が goal、中心方向、受入境界を再設計しなくても実行と受入へ進めるだけの material
semantics を candidate に含めますが、task に不要な risk や rollback section を儀式的に追加しません。

## Authority boundary

<!-- @contract planning-synthesis-authority-boundary -->
Planning Synthesis は supplied direction と authority constraints の意味を保持し、その内側でだけ planning decision を行う。
<!-- @/contract -->

goal や scope を変更・拡張せず、別の design direction へ切り替えず、Human-confirmed constraint を緩和または独自再解釈しません。
current authority の外に新しい specification を作らず、material missing fact を plausible guess で埋めません。input 間の conflict が candidate
coherence または authority の保持を妨げる場合も、一方を無断で優先せず gap として扱います。

## Bounded advisory Action

local planning decision に第二の観点が material に有用だと Planning Synthesis が判断した場合だけ、`plan-quality-advisor` を使えます。
advisor は mandatory phase、comprehensive review、gate ではありません。

各 invocation は一つの concrete advisory question と、その question に必要な current planning projection / candidate context、必要なら supplied
upstream Researcher evidence だけを渡す fresh / context-isolated request とします。異なる question は独立した invocation に分け、prior
advisor conversation や advisor output を次の invocation へ暗黙に継承しません。複数回使うか、どの question を渡すかは Planning
Synthesis が判断し、advisor に loop、next question、continuation、round limit の所有を移しません。

<!-- @contract planning-synthesis-advisor-boundary -->
Planning Synthesis は advice の採否を所有し、advisor output を新しい direction や binding conclusion として扱わない。
<!-- @/contract -->

advice が supplied evidence と inference を区別していても、その存在だけで candidate を変更しません。current input、authority、candidate
coherence に照らして採用、部分採用、または不採用を判断します。

## Result boundary

<!-- @contract planning-synthesis-result-boundary -->
返す結果は current task に material な planning semantics を持つ coherent Plan candidate、または candidate coherence を妨げる具体的な material input gap である。
<!-- @/contract -->

Plan candidate の serialization や section 構成は固定しません。material input gap は、何が不足または矛盾しているか、それが established
direction 内の synthesis をどう妨げるかを caller が判断できる形で返します。Planning Synthesis は workflow fallback、Human interaction、
`incomplete` status、review、verification completion、final acceptance を決めません。

Phase 6b の completion は synthesis の完了だけを意味します。返した candidate を review-complete、verified、final と主張せず、後続の
review や workflow continuation を開始しません。

## Representative cases

### Direct synthesis

<!-- @contract planning-synthesis-direct-case -->
input が coherent synthesis に十分なら、advisor を起動せず Planning Synthesis が必要な判断を行い candidate を返せる。
<!-- @/contract -->

この経路では、advisor 利用を品質条件にせず、Planning Synthesis が decomposition、dependency、AC、verification など必要な judgment を
直接所有します。output を input の並べ替えだけに縮退させません。

### Bounded advice with supplied Researcher evidence

<!-- @contract planning-synthesis-advice-case -->
supplied Researcher evidence が局所 trade-off に関係する場合、concrete question と必要 context だけの fresh advisor request を使い、Planning Synthesis が advice を裁定する。
<!-- @/contract -->

たとえば複数の ordering 候補があり、upstream evidence が trade-off の一部を示す場合、advisor は source evidence と自分の inference を
区別した non-binding material を返します。Planning Synthesis は comprehensive review や Researcher の再起動へ広げず、authority の内側で
その material を candidate に採用するか判断します。

### Material input gap

<!-- @contract planning-synthesis-gap-case -->
candidate coherence に material な fact が input にない場合、その fact と影響を gap として caller へ返す。
<!-- @/contract -->

たとえば direction 内の AC や verification を確定するための fact が欠けている場合、plausible な値を選ばず、repository exploration、
research、Human fallback を開始せずに停止します。caller が gap の解消方法と workflow-level status を所有します。

## Responsibility boundary

Planning Synthesis は plan-family の public entrypoint、review/refinement loop、structural gate、Authority Integrity Verification、final acceptance
ではありません。fixed Plan schema、planning-direction schema、lifecycle state machine、completeness score、advisor ledger を定義しません。
