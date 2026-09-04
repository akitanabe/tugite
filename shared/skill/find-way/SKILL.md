<!-- @only claude -->
---
name: find-way
description: >-
  Destination 全体の Planning Fog と Decision blocker を解像し、self-contained な Work Units を返す明示起動の pre-planning workflow。
disable-model-invocation: true
---
<!-- @/only -->
<!-- @only codex -->
---
name: find-way
description: >-
  Destination 全体の Planning Fog と Decision blocker を解像し、self-contained な Work Units を返す明示起動の pre-planning workflow。
---
<!-- @/only -->
<!-- @only cursor -->
---
name: find-way
description: >-
  Destination 全体の Planning Fog と Decision blocker を解像し、self-contained な Work Units を返す明示起動の pre-planning workflow。
disable-model-invocation: true
---
<!-- @/only -->

# find-way

## Identity and boundary

<!-- @contract find-way-explicit-only -->
`find-way` は Human が明示した場合だけ開始する public pre-planning workflow です。request の Destination 全体にある Planning Fog と planning 前の Decision blocker を解像し、1..N の self-contained な Work Units を返します。
<!-- @/contract -->

入力は request、available context / evidence、optional な `resume_reference`、および state persistence に対する明示 authority / requested destination です。新規 invocation では request から Destination を確立します。一意に推定できる場合は進み、複数の妥当な Destination が material に scope を変える場合は Human-owned gap とします。

<!-- @contract find-way-destination-selection -->
新規 invocation では caller / harness が観測した candidate facts と requested destination を shared Destination Selection へ渡し、返された selection result を変更せず、selected destination は state lifecycle に、unresolved gap / incomplete は workflow result に使用します。
<!-- @/contract -->

<!-- @contract find-way-non-goals -->
`find-way` は plan、plan review、implementation、production work、deliverable completion、complete 後の reopen、または特定 downstream workflow への routing / auto-transition を開始しません。他 workflow は `find-way` を推奨できますが、暗黙起動しません。
<!-- @/contract -->

生成された Skill から、各 platform の generated path を基準に次を参照します。

- `../../references/model-construction.md`
- `../../references/agentic-model-construction.md`
- `../../references/interactive-model-construction.md`
- `../../references/researcher-delegation.md`
- `../../references/external-effects.md`
- `../../references/destination-selection.md`

## One Local Model and current Map

<!-- @contract find-way-local-model -->
一回の invocation は Destination 全体を semantic subject とする exactly one の task-local Local Model を所有します。Agentic Model Construction を first route とし、Human-owned blocker が残り、Agent-side で独立した semantic progress route がない場合だけ Interactive Model Construction を同じ Local Model へ composition します。Decision Unit、Research Agent、nested consumer は別 Local Model を持ちません。
<!-- @/contract -->

resume では supplied `resume_reference` に対する caller / harness の観測結果を shared Destination Selection の deterministic branch へ渡します。resolved same-state identity の保存済み current-state Data と current context / evidence から fresh Local Model を構築します。Local Model、Exploration Projection、推論履歴は serialize しません。

<!-- @contract find-way-map -->
初期観測は breadth-first に主要 uncertainty / decision boundary を横断し、Destination、Work Units、Decision Units、Planning Fog、Out of scope からなる low-resolution current-state Map を構成します。Map は index であり、detail、推論履歴、append-only history を重複保持しません。
<!-- @/contract -->

## Decision and category boundaries

<!-- @contract find-way-decision-unit -->
sharp かつ bounded な question だけを Decision Unit とし、canonical state は `open | resolved` だけとします。`actionable | blocked` は open state と material dependency の resolved / unresolved から導出し、第三の canonical state にしません。
<!-- @/contract -->

`active open Decision Unit` は state が open で current Map の Decision Unit index に属するものです。WU boundary や Destination coverage をまだ変え得る sharp question は active open のまま扱います。question または WU boundary 自体をまだ形成できない領域は Planning Fog、Destination 外は Out of scope とします。

<!-- @contract find-way-resolution-boundary -->
bounded conclusion により question の残部を一つの成立済み WU 内の downstream planning 責務へ局所化できた場合は Decision Unit を resolved にし、material unresolved matter をその WU の `remaining gap` または `established context` へ一度だけ投影します。WU boundary が未形成の Planning Fog は remaining gap へ移しません。
<!-- @/contract -->

actionable な Decision Unit または Fog を縮小できる Agent-side route から、Planning Fog の縮小と WU boundary 確立への情報価値が高いものを親 `find-way` が選びます。repository / source exploration、Research Agent 等の bounded evidence acquisition は resolution の bounded conclusion のためだけに行います。resolution、Fog 分類、Map recomposition、WU boundary、completion の semantic judgment は親が保持します。

<!-- @contract find-way-reintegration -->
resolution は same Local Model へ Reintegration し、material invalidation がある場合だけ affected region を Recomposition します。Map は current evidence に合わせ、Fog の縮小、Decision Unit の形成 / 解消、WU の形成 / split / merge / boundary adjustment、Out of scope の更新を stale state への追記ではなく置換として反映します。
<!-- @/contract -->

## Work Units

<!-- @contract find-way-work-unit -->
各 Work Unit は fresh downstream workflow が Map を読み直さず、他 WU の planning を同時に抱えず扱える self-contained な planning context とします。Data は id、name、scope、`planning-bounded | planning-ready`、established context、planning-bounded 時の remaining gap、material dependencies を持ちます。Scope、established context、material dependencies は単独の handoff に必要な context として保持します。

Work Unit は実装量、file、commit、Implementation Unit 数では split しません。material な planning responsibility の抜けや二重 ownership を避け、context / constraint / dependency の共有は許容します。`planning-bounded` は WU boundary は成立しているが planning 開始前に material な理解不足が残り、additional refinement が扱う `remaining gap` があることを表します。`planning-ready` は additional premise construction なしに planning へ進める状態であり、planning 内で扱う trade-off や選択が残らないことを意味しません。
<!-- @/contract -->

<!-- @contract find-way-work-unit-handoff -->
Human-facing output では、各 Work Unit の `planning-ready | planning-bounded` と、その WU が成立させる planning に渡す結果である Outcome を個別に判別できるようにします。Outcome は Acceptance Criteria、downstream action、implementation design、test plan、decision history、または特定 Skill / routing の指定ではありません。
<!-- @/contract -->

<!-- @contract find-way-work-unit-bounded-gap -->
`planning-bounded` の各 Work Unit では planning 前に残る material な Remaining gap を示し、可能な場合は何が成立すれば `planning-ready` になるかという条件も示します。WU boundary 未形成の Planning Fog は Remaining gap に移しません。
<!-- @/contract -->

<!-- @contract find-way-work-unit-material-context -->
Binding decisions / constraints、Explicit excludes、Evidence / provenance は handoff の再構築に material な場合だけ補います。Material dependency は、必要な場合に planning input、実装順序、独立可否など関係の意味を保持します。
<!-- @/contract -->

## Persistence and continuation

state の create / update / read-back は `find-way` が caller-specific lifecycle として所有します。repository、Human、external evidence、persistent storage との接触は Action とし、shared External Effects boundary に従って Action identity、authority、target、precondition、duplicate semantics、independent verification、retention / cleanup が成立する場合だけ実行します。

<!-- @contract find-way-persistence -->
保存と read-back に成功した場合だけ、destination と same state identity を再解決できる `resume_reference` を `incomplete` result の外部へ明示的に返します。reference は Human-visible または caller-held Data とし、state object 内だけに閉じません。write / read-back failure は partial / unknown state と evidence を伴う `incomplete` とし、広域 scan、silent discovery、relocation / migration を resume 前提にしません。
<!-- @/contract -->

保存する state は Destination、current Map、Decision Unit の canonical state、形成済み provisional WU、evidence relation、current limitation に限定します。persistent state schema や storage adapter は定義せず、complete 後の WU physical persistence は要求しません。

<!-- @contract find-way-completion-disposition -->
`resume_reference` から再開した persisted unfinished state について `complete` を返す前に、exact state と `resume_reference` が再開可能な unfinished state として残らない disposition を確定します。
<!-- @/contract -->

## Programmatic Flow

### find-way-progression

<!-- @contract find-way-flow -->
<!-- @anchor find-way-flow-trigger -->
Trigger: 親 `find-way` が current Map の semantic judgment と completion facts を確定した。

<!-- @anchor find-way-flow-inputs -->
Inputs: Destination coverage、WU count / readiness、Planning Fog の有無、active open Decision Unit の有無、Agent-side progress route の有無、Human-owned blocker の有無、persistence eligibility、resumed persisted unfinished state / resume_reference の有無、completion-time disposition authority / eligibility。

Procedure:

<!-- @anchor find-way-flow-step-1 -->
1. Destination coverage が 1..N WU で成立し、Planning Fog と active open Decision Unit がない completion invariant を評価する。planning-bounded WU は成立を妨げない。成立時は `disposition not required → complete / WU boundary freeze`、`disposition required + authority / eligibility established → shared External Effects boundary の下で completion-time disposition Action → result Data → exact state / resume_reference の independent verification`、`disposition required + authority / eligibility absent | unknown → evidence 付き incomplete` とし、Action branch は `verified non-resumable → complete / freeze`、`failure | unknown → evidence 付き incomplete` に投影する。未成立時は形成済み WU を provisional として step 2 へ進む。
<!-- @anchor find-way-flow-step-2 -->
2. それ以外で Agent-side progress route があれば、same invocation / same Local Model で semantic judgment へ戻る。
<!-- @anchor find-way-flow-step-3 -->
3. 進行 route がなく Human-owned blocker があれば、同じ Local Model に Interactive Model Construction を composition する。gap が解消された result は same Local Model へ Reintegration して same invocation の semantic judgment へ戻し、未解消 result は limitation / evidence 付き `incomplete` へ投影する。
<!-- @anchor find-way-flow-step-4 -->
4. それ以外は persistence eligibility に従う。`eligible` は shared External Effects boundary に従って state create / update / read-back Action を実行し、その後に result Data を得る。`ineligible` は保存せず evidence 付き `incomplete` とする。
<!-- @anchor find-way-flow-step-5 -->
5. `eligible` branch で Action 後に得た result Data を `success → resume_reference を伴う incomplete`、`failure | unknown → evidence 付き incomplete` に投影する。`ineligible` branch は step 4 の `incomplete` をそのまま返し、Action result Data を要求しない。

<!-- @anchor find-way-flow-outcomes -->
Outcomes:

Flow が terminal に返す public result は `complete | incomplete` とします。step 2 と gap 解消済みの step 3 は terminal result を作らず、親の autonomous semantic judgment へ戻ります。

- `complete`: required な completion-time disposition の independent verification を通過したうえで、freeze した stable Work Units を返す。
- `incomplete`: completion invariant 未成立時の provisional Work Units、current limitation、persistence / disposition result を返し、unfinished state の保存成功時だけ externally returned `resume_reference` を含める。
<!-- @/contract -->

Flow は確定済み Data の fixed progression だけを所有します。Destination 推定、sharpness、information value、materiality、Fog 分類、WU boundary / split / merge / readiness、question selection は親の autonomous judgment とし、Flow や expected-output oracle に固定しません。

## Result

Result は supporting evidence、authority relation、material qualification を後続判断に必要な範囲で保持します。
