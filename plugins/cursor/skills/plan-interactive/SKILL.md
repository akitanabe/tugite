---
name: plan-interactive
description: >-
  ユーザーが明示した場合だけ、人間と方向性を逐次裁定して自由形式の計画・設計成果物を作る。
  direction freeze 後に structural gate と固定 review を通し、最終結果を人間へ返す。
  実装・委譲・次工程の自動前進は行わない。
disable-model-invocation: true
---
<!-- Generated from shared/. Do not edit directly. -->

# plan-interactive

この Skill は人間参加型の自由形式計画・設計成果物を起草し、親が確定候補または未完了結果を返す public workflow
である。`plan-agent` と自動切替せず、双方向ともユーザーの明示起動だけで開始する。

## 発火制御と責務

- `plan-interactive` の起動または同等の明示要求がある場合だけ起動し、context から暗黙起動しない。
- 各 platform の invocation metadata は上記の explicit-only 契約を表し、その範囲を拡張しない。
- 実装、委譲、Worker 起動、worktree 操作、後続の実装開始を行わず、final acceptance 後の final-candidate だけを local artifact へ保存する。
- 起草、対話、gate、review、final acceptance 候補または未完了の返却までを担う。人間は方向性と最終結果の責任を持ち、
  public workflow parent は planner として、調査、具体化、整合性、verification、工程の経過責任を持つ。後続 Action は
  人間へ残す。

## 入力と成果物

要求原文、目的、対象、成功条件、scope、exclude、依存、制約、current state を先に観測する。blocking な不足を
推測せず、軽微な不足は根拠付き assumption に分離する。成果物には目的、観測可能な成功条件、設計、scope と exclude、
依存、制約、選択理由、棄却した代替案、verification、残存 risk、未確定の問いを含める。

成果物種別を `artifact_kind` Data として保持する。実装前提プラン系か否かは reviewer 適用可否だけに使い、自由形式
成果物をプラン系へ変える理由にしない。実装前提プラン系は `Acceptance Criteria` と `設計` の節名を持つ。

## clarify-it の caller mapping

```text
application = public clarify-it in the same plan-interactive parent context
dialogue_norm = inherit clarify-it Specification, Method, and Casebook without copying or override
caller_owns = invocation boundary | binding Human authority | verified workflow Data | direction freeze | downstream workflow
public_extension = none
```

## clarify / resolution execution bound

```text
fix_timing = at each clarify or resolution loop start
immutability = unchanged during that loop
terminal = bound reached or no semantic progress with material decisions remaining -> preserve remaining decisions and reasons -> plan-interactive incomplete -> prohibit downstream
public_contract = no fixed value, public parameter, schema, or resolve_rounds
budget_boundary = separate from structural-health-gate rounds and review limits
clarify_stopped = never fabricate this caller-owned terminal as clarify-it Stopped
```

clarify loop の開始前に、親 Action は次の Loader Data をそれぞれ一度だけ使って kernel を読み、identity と必須本文を検証する。

<!-- Why Not: Loader Data は load/use relation を一体で保持するため分離しない。 -->
```text
resolve_path = ../../references/resolve-kernel.md
resolve_load_timing = once before clarify-it application
resolve_identity = resolve-kernel-v1
resolve_dependencies = none
resolve_required_sections = [Caller boundary と role, Current verified snapshot、working state、frontier, Atomic resolution unit, Exit と停止, Kernel non-dependency]
necessity_path = ../../references/necessity-kernel.md
necessity_load_timing = once before candidate Claim adjudication
necessity_identity = necessity-kernel-v1
necessity_dependencies = none
necessity_required_sections = [適用範囲, Task Specification, Claim と evidence, Deletion Test]
failure = incomplete before clarify-it application
owner = plan-interactive parent
delegate_path_resolution = false
```

次の role Data を唯一の正本として mapping する。

<!-- Why Not: role Data は caller と role mapping の一体性を失うため分離しない。 -->
```text
caller = plan-interactive
resolver = planner
counterpart = human
authority = binding
ledger = decision ledger
```

検証済み本文だけを親が既存の判定基準または必要な周辺 context に注入する。loader、role mapping、advisor、verified snapshot、
decision / adoption ledger、direction freeze source / constraints は親の workflow Data であり、`clarify-it` の入力または output contract にしない。
親は後述の necessity adjudication、限定 advisor、verification derivation の normative Data を direction freeze 前に適用する。

## 観測 Action と clarify-it 適用

```text
clarify_action_boundary = inherit clarify-it prohibition without override
parent_observation = observe request, repository, Issue, existing specification, and required runtime behavior
observation_data = freeze observation with provenance and evidence while inheriting clarify-it Data distinctions
technical_evidence_gap = return to parent boundary; never Human Decision Point or clarify-it Stopped
parent_action = perform only the minimum required observation
data_update = add the observed Data to the same current decision model
reapply = apply clarify-it to that same model in the same parent context
public_extension = no new status, fixed output schema, or separate context
contradictory_action_permission = prohibited
```

## clarify-it result の projection

```text
Completed = verified Data comparison -> unique direction freeze candidate projection
projection = add no new meaning, condition, or decision
freeze_only_reconfirmation = prohibited
Stopped = preserve reason and remaining decisions -> plan-interactive incomplete -> prohibit downstream
Completed_meaning = not workflow completion or candidate acceptance
```


direction freeze は成果物全文の固定ではなく、人間が確定した意味判断を保護する境界とする。親は方向性、実装イメージ、
重要な verification を圧縮して人間へ示し、freeze 後の gate と review へ frozen decisions と変更可能な具体化を区別して渡す。
大きな purpose または scope の変更が入力された場合は既存成果物へ増分追加せず、この public workflow 全体を再策定する。
過去 decision は自動継承せず、candidate prior decisions と再利用知見として現在の要求と evidence で再検証する。

## direction freeze Data と optional proposal refinement

direction freeze 成立時、親は要求原文、verified decision ledger、freeze candidate から、Human-confirmed な価値、重要な
scope / exclude、責務、意図的な非採用、判断点にならなかった raw specification を含む全意味単位を `freeze_source_snapshot`
として固定する。親の Calculation は非空で一意な workflow-local opaque `id` を一度だけ付与し、各 source item から同じ ID の
`{id, frozen_meaning, source_evidence}` を exactly one 投影する。source ID 集合と constraint ID 集合、1対1、未投影・重複・余分の不在、
meaning の一意性、Human / raw statement と verified candidate 上の解決可能な evidence を開始前に全数照合する。
不完全、空、identity 再生成、または曖昧な投影は proposal 開始前 `stop-incomplete` とする。

親は freeze 要約と同じターンに、planner 裁量の proposal refinement 実行推奨または省略推奨、短い理由、`Yes / No` を一度提示する。
score、件数 threshold、新しい public knob は作らず、selection は decision ledger ではなく workflow process Data とする。
実行分岐と proposal 停止時の後段制御は、後述の専用 normative Data を唯一の正本とする。
authority conflict への Human 再判断を反映・verify した後は、最新 verified snapshot と更新済みの完全な constraints で fresh proposal fixed 2 pass と
fresh-context check #1 へ必ず進み、新しい optional selection を挟まず governing `executed` を維持する。この recovery は integrity check count を消費しない。

successful refinement 後は semantic change がなくても、親が別 fresh context の `plan-quality-advisor` を `freeze-integrity`
invocation で起動する。verifier は全 constraints を独立照合し、`intact | violated | indeterminate` と追跡可能な evidence を返す。
verdict は binding であり、親は覆さない。`intact` だけが gate へ進む。

check #1 非 intact 時の停止・reopen 関係は、後述の専用 normative Data を唯一の正本とする。Human 再判断の反映・verification 後、最新 verified
candidate で recovery freeze を作り、保持した check evidence の constraint ID / candidate location から decision / adoption ledger の直接・間接依存を
閉じた affected obligations を Calculation する。それを immutable `request.scope`、その他の obligation を `request.exclude` に固定し、
同じ bounded request を advisor #1 / #2、両 Transaction、verification へ渡す。scope 外 point は apply せず `rejected` または `out-of-scope` とする。
locator、dependency closure、scope / exclude の排他性を安全に確定できなければ開始前 `stop-incomplete` とする。

```text
affected_scope = constraint IDs + candidate locations -> dependency closure -> affected obligations
request.scope = affected obligations
request.exclude = all other candidate obligations
scope_outside = rejected | out-of-scope; never apply
scope_failure = unresolved locator / closure / exclusivity -> stop-incomplete before proposal
```

最新 verified snapshot を S0 とする fresh proposal fixed 2 pass と、別 fresh context の check #2 を mandatory continuation として実行し、
新しい optional selection を挟まない。check #2 が非 `intact` なら Trust failure の `stop-incomplete` とし、再 reopen しない。Human へは
2回目も `intact` でなかったこと、verdict、問題が残る constraint 周辺、`stop-incomplete` だけを報告し、raw advisor history は露出しない。
Human Decision と独立な partition は verify / promote できるが、未解決 Human Decision が残る candidate は gate へ渡さない。

## structural-health-gate

direction freeze 候補を受け取った場合は、提案が全件却下された場合も同じ親 context の internal
`structural-health-gate` へ渡す。input には generic `caller_context` Data（`workflow_family: plan-family`、
`invocation: explicit-public-parent`）を含める。`context 不成立` は別 route へ切り替えず `stop-incomplete` とする。

親は gate 予算を独立した `rounds` Data として管理し、assessment 1回を1 round と数える。`rounds.limit` は下限1の
ceiling とし、ユーザー指定を優先する。未指定なら親が loop 開始時に固定し、1未満は補正せず `stop-incomplete` とする。
1未満では assessment、producer の再実行、後段を起動しない。gate 予算と review 予算は別 Data とする。

`pass` は直ちに後段へ進む。`return` は現在の round が limit 未満の場合だけ、gate の問題・影響・推奨対応を Human へ圧縮し、
影響する判断と直接・間接依存を closure にして、後述の routing Data に従い局所 reopen する。
新しい direction freeze で proposal refinement の `Yes / No` を再確認し、前回の opt-in を継承せず、後段は routing Data に従う。前 cycle の opt-in や governing value を継承しない。
limit 到達 round の `return` と `insufficient-evidence` は
`stop-incomplete` とする。人間が構造 finding への対応を全件却下し candidate 内容が変わらない場合、同一内容へ
別 identity を付けて再投入せず、構造欠陥未解消として `stop-incomplete` とする。

## review の適用と固定順序

工程順序は `clarify-it → direction freeze projection → optional proposal refinement / freeze-integrity → structural-health-gate → review-refine` であり、gate が `pass` した snapshot だけを
次の判定へ渡す。まず `artifact_kind` と既定 `plan-adversarial-reviewer` の責務から reviewer 適用可否を判定する。既定 reviewer の適用対象外なら、review goal に対応する別 reviewer の有無にかかわらず `review-refine` に投入せず、通常の起草確定へ進む。review 省略の明示より reviewer 適用可否の判定を先に行う。

reviewer 適用可能な成果物は、ユーザーによる review の明示要求がなくても固定工程として `review-refine` へ渡す。
ユーザーが review 省略を明示した場合は、確定候補とせず、review 未実施の起草物と残存 risk を添えて未完了として返す。

`review-refine` には不変 snapshot、`artifact_kind`、`caller_context`、要求と判定基準、review goal、reviewer・回数制約、
必要なら継続台帳を渡す。回数制約がなければ親が loop 開始時に上限と打ち切りを決める。既定 reviewer は
`plan-adversarial-reviewer`、final trim は `over-engineering-reviewer` のプラン入力モードである。`review_goal` は、ユーザー指定の review goal や追加の具体的な risk がない場合、「実装前プランの具体的な failure path を確認し、確定候補にできるか判断する」とする。これは plan review 自体の既定目的であり、毎回 risk を事前発見することを要求しない。ユーザー指定 goal や追加 risk は既存 reviewer の責務内で追加できる。入力前提不足は
補って再投入するかレビュー不成立として返す。

## review 結果と direction freeze の保護

通常出力の成果物、指摘台帳、判断保留台帳、未解決 finding、final trim、`termination`、
`adversarial_review_count` を受け取る。親は finding を既存5区分（採用、却下、範囲外、判断保留、人間確認）へ
evidence と理由付きで裁定する。判断保留は loop 中凍結し、round、誘発収束、未解決 finding を再計算しない。

decision ledger で人間が裁定済みの方向性を変更・撤回する finding は、局所修正で閉じる場合も親だけで採用せず
`人間確認` へ裁定する。影響する判断と dependency closure を確定し、後述の routing Data に従い局所 reopen する。
再 review の scope は変更と波及に限定する。dependency closure を確定できなければ推測せず `incomplete` とする。
既存の裁定区分は増やさない。

review は frozen decisions を守る限り、実装の具体化、verification の補強、複雑性の削減を行える。frozen decision の
変更が必要なら、改善案を採用せず `人間確認` へ止める。

## review 完了と final acceptance

review 実行経路では `converged` または未解決 finding のない `induced-loop` だけを確定候補とする。レビュー不成立、
`round-limit`、`stop-incomplete`、未解決 finding を伴う `induced-loop` は確定候補とせず、理由、台帳、残存 risk を
添えて未完了として返す。代替 evidence で完了扱いにしない。

`review-refine` が新しい設計選択を必要として `stop-incomplete` を返しても `clarify-it` へ自動逆遷移しない。後述の routing Data が定める Human の選択に委ね、
明示判断まで停止する。未完了返却後の受け入れと再投入は人間が明示的に判断し、未完了結果を artifact として保存しない。

final acceptance は direction freeze と分離し、既定で必須とする。人間が明示的に opt-out した場合だけ承認 Action を
省略できるが、final report は省略しない。承認 Action の `Semantic Delta` baseline は final candidate に対応する最新 direction freeze とする。
入力には、成果物内容の短い要約、方向変更の有無、追加・変更した検証とその結果、
残存 risk、必要な人間判断を含める。承認完了または明示 opt-out までは、direction freeze、gate 通過、review 済み candidate のいずれも artifact として保存しない。

final acceptance での修正要求は正常な結果として扱う。親は変更の影響と依存する判断だけへ `clarify-it` を局所適用し、
局所 reopen し、decision ledger 全体をリセットしない。後述の routing Data に従い再評価し、再 review は変更箇所と直接・間接の波及に限定する。
大きな purpose または scope の変更なら局所 reopen を行わず、public workflow 全体を再策定する。

final report の provenance は final candidate を gate へ送った governing phase-selection point で上書きし、
`proposal refinement: executed | skipped` だけを表示する。authority conflict / integrity recovery は executed cycle の mandatory continuation なので
`executed` を維持する。gate return または final acceptance correction の新 selection は古い governing value を捨てる。
過去 cycle、正常な integrity success、fixed 2 pass、advisor evidence は final report に追加しない。

```text
executed -> gate return -> skipped = skipped
skipped -> gate return -> executed = executed
executed -> Trust recovery -> intact = executed
executed -> final acceptance correction -> skipped = skipped
```

## clarify-it 局所再適用の親 routing Data

```text
workflow_order = clarify-it -> direction freeze projection -> optional proposal refinement / freeze-integrity -> structural-health-gate -> review-refine
gate_return = problem / impact / recommendation -> affected dependency closure -> clarify-it application -> new freeze -> new selection -> gate
frozen_review_finding = parent human-confirmation adjudication -> affected dependency closure -> clarify-it application -> new freeze -> new selection -> gate -> review changed closure only
review_stop_incomplete = no automatic clarify-it application; Human explicitly selects resume | incomplete end | out-of-scope split
final_acceptance_correction = affected dependency closure -> clarify-it application -> new freeze -> new selection -> gate -> review changed closure only -> final acceptance
large_purpose_or_scope_change = reformulate the whole public workflow; no local reopen
closure_failure = incomplete; never guess affected scope
```

## necessity adjudication の親 Data

親は検証済み necessity kernel を caller 固有責務へ次の最小 Data だけで mapping する。

```text
criteria_injection = verified Task Specification + Deletion Test
mapping = necessary -> adopted; unnecessary -> rejected; indeterminate -> unresolved
mapping_target = existing adoption ledger; no new result field
```

Claim、evidence、updated snapshot 再判定、mutual deletion guard、budget / termination 非直結、gate 適用外は検証済み kernel 本文を
既存の判定基準として継承し、この caller mapping または `clarify-it` に再記述しない。

## freeze 前 advisor の親 Data

親は次の限定条件のいずれかが成立する場合だけ advisor を起動する。

```text
trigger_only = scope or responsibility boundary change | adopted-Claim dependency | decision-completing additional Claim | non-trivial pre-freeze change chain
advisor = read-only plan-quality-advisor
input = candidate snapshot + verified criteria Data
insight = non-binding Data
adjudicator = plan-interactive parent against primary evidence and request
mapping = adopted | rejected | unresolved in adoption ledger
ledger_boundary = decision ledger is separate from adoption ledger
fixed_phase = prohibited
empty_insights = not direction freeze evidence
```

insight の Human 境界は次の Data に固定する。

```text
automatic_adoption = prohibited
automatic_question_generation = prohibited
direct_human_question = prohibited
human_direction_impact = unresolved -> parent verifies evidence and reconstructs its own recommendation -> clarify-it application
raw_insight = parent-only unless Human explicitly requests process details
```

advisor は Human の advisor、仲裁経路、または対話主体ではない。この orchestration と adoption ledger は親責務であり、
`clarify-it` の input / output contract へ追加しない。

## freeze 前 verification derivation の親 Data

```text
timing = before direction freeze and after each updated snapshot
owner = plan-interactive parent Calculation
input = Task Specification + verified workflow Data
coverage = normal | boundary | failure path | side effect | prohibition | responsibility boundary | scope exclude
output = how each obligation will be observed after implementation
clarify_it = do not add this derivation or its schema to clarify-it
blocking_gap = incomplete before direction freeze
```

親はこの Calculation の結果を direction freeze の verified workflow Data に反映する。Human へは必要な判断材料だけを
`clarify-it` の既存規範で提示し、verification schema 自体を流入させない。

## optional proposal refinement の normative relations

以下の3 Data blockは、分岐、proposal 停止、check #1 recovery の唯一の正本である。

```text
selection_presentation = direction freeze summary same turn; recommend execute or skip + short reason + Yes / No; exactly once
No = skip proposal and freeze-integrity check -> structural-health-gate
Yes = verified direction-freeze candidate S0 -> constrained proposal fixed 2 pass -> fresh-context freeze-integrity check
```

```text
proposal stop-incomplete
authority_conflict + verified result = use only returned verified candidate for local Human Decision recovery
otherwise = outward incomplete; no pre-refinement snapshot fallback; no structural-health-gate
```

```text
check #1 violated | indeterminate = retain all evidence -> affected dependency closure -> local clarify-it application -> verified recovery freeze -> fresh bounded proposal fixed 2 pass -> fresh-context check #2
direct_structural_health_gate = prohibited
legacy_dialogue_route = prohibited
check #2 non-intact = Trust failure incomplete; no reopen
```

## Programmatic Flows

以下は final acceptance または明示 opt-out の後に、親が exact target を確定して渡した publication routing だけを持つ。

### local-artifact-completion

Trigger: final acceptance が完了した、または Human が final acceptance を明示 opt-out し、親が exact `publication_target` を確定したとき。
Inputs: final acceptance / opt-out Data、凍結した成果物本文 bytes、exact destination、exact filename、finite retry bound、qualification evidence、destination object identity、および必要な OS-temp identity / creation intent。
Procedure: skill-relative `../../references/plan-artifact-publication.md` を publication invocation 前に一度だけ load し、identity `plan-artifact-publication-v1` と必要本文を検証する。検証済み reference の `programmatic-publication` Flow に、親確定の `publication_target` をそのまま渡す。Flow の published result から outward status と stdout の Result、Summary、必要な Human Attention、Artifact path だけを projection する。consumer は target selection、candidate ranking、filename、retry bound、publication procedure を再実行・複製しない。
```text
publication_reference = ../../references/plan-artifact-publication.md
publication_load_timing = once before programmatic-publication use
publication_identity = plan-artifact-publication-v1
publication_use = parent-confirmed publication_target -> programmatic-publication -> outward status/stdout projection
```
Outcomes: published result と `final-candidate` の outward status / stdout projection、`destination-reselection-required`、または `incomplete`。final acceptance / opt-out 前、資格喪失、unsafe / unknown、loader failure は write せず `incomplete` とし、Flow の結果を blind fallback や implicit reselection へ変換しない。

## final acceptance 後の local artifact completion

final acceptance が完了した場合、または Human が final acceptance を明示 opt-out した場合だけ成果物本文の byte snapshot を凍結し、
`local-artifact-completion` Flow を開始する。それ以外の `incomplete`、direction freeze、gate、review、acceptance candidate では path 選択も write も行わない。
artifact には凍結した成果物本文の bytes だけを入れ、要約、Human Attention、gate / review 結果、decision / finding ledger その他の process Data を追記しない。
`final-candidate` の stdout は成果物全文を出さず、Result、成果物内容だけの短い Summary、必要な場合だけ Human Attention、実際に保存・確認した
Artifact local path に限る。final summary の明示 opt-out では Artifact だけを返す。保存した artifact は Git 管理、永続保存、最終採用、または後続 Action の許可を意味しない。
```text
workflow = plan-interactive
artifact_eligibility = final acceptance completed or explicit opt-out and verified publication_target
pre_acceptance_artifact = none at direction freeze, gate, review, or acceptance candidate
artifact_body = frozen final accepted candidate body only
artifact_excludes = [Semantic Delta, Verification Delta, Human Attention, gate result, review result, decision ledger, finding ledger, process history]
stdout = Result, short Summary, optional Human Attention, Artifact local path
stdout_excludes = full artifact body, Semantic Delta, Verification Delta, gate or review result, decision or finding ledger, process history
summary_opt_out = Artifact only
authority = not Git management, durable persistence, final acceptance, or downstream Action permission
```
