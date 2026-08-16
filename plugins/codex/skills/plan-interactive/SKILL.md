---
name: plan-interactive
description: >-
  ユーザーが明示した場合だけ、人間との方向性裁定から計画・設計成果物を起草し、gate と固定 review を経た
  確定候補または未完了結果を返す public workflow。
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

親は loop 開始時に bound、remaining decisions、semantic progress、materiality を入力 Data として固定し、
`clarify-loop-bound-routing` Flow へ渡す。bound の値、progress の意味、materiality の判断は親が所有し、Flow 外の
Human Decision や public parameter へ拡張しない。gate と review の budget は別 Data とする。

## kernel preflight と caller mapping

`interactive-kernel-preflight` Flow が resolve / necessity の load timing、identity、必要本文、failure routing の唯一の詳細 witness である。
親は skill-relative loader Data、caller=`plan-interactive`、resolver=`planner`、counterpart=`human`、authority=`binding`、
ledger=`decision ledger` を入力として準備し、検証済み本文だけを既存の判定基準へ注入する。

stable Loader Data は次の値を持つ。

```text
resolve_path = ../../references/resolve-kernel.md
resolve_identity = resolve-kernel-v1
resolve_dependencies = none
resolve_required_sections = [Caller boundary と role, Current verified snapshot、working state、frontier, Atomic resolution unit, Exit と停止, Kernel non-dependency]
necessity_path = ../../references/necessity-kernel.md
necessity_identity = necessity-kernel-v1
necessity_dependencies = none
necessity_required_sections = [適用範囲, Task Specification, Claim と evidence, Deletion Test]
caller = plan-interactive
resolver = planner
counterpart = human
authority = binding
ledger = decision ledger
```

`interactive-kernel-preflight` Flow はこの Data を使い、path 解決と最終判断は親が所有する。

## 観測 Action と clarify-it 適用

親は request、repository、Issue、existing specification、required runtime behavior と provenance 付き action evidence を観測 Data として準備する。
`observation-reapply` Flow が最小 observation、同じ decision model / parent context への再適用、technical gap の返却を唯一の詳細 witness とする。
観測の意味評価、Human clarification、contradictory Action の裁定は Flow 外の親責務である。

## clarify-it result の projection

`clarify-it` の `Completed` / `Stopped` を direction freeze candidate または未完了へ写像する詳細手続きは
`direction-freeze-projection` と `clarify-loop-bound-routing` Flow が担う。親は verified comparison、remaining decisions、reason を入力として保持し、
projection を workflow completion や candidate acceptance と同一視しない。

direction freeze は成果物全文の固定ではなく、人間が確定した意味判断を保護する境界とする。親は方向性、実装イメージ、
重要な verification を圧縮して人間へ示し、freeze 後の gate と review へ frozen decisions と変更可能な具体化を区別して渡す。
大きな purpose または scope の変更が入力された場合は既存成果物へ増分追加せず、この public workflow 全体を再策定する。
過去 decision は自動継承せず、candidate prior decisions と再利用知見として現在の要求と evidence で再検証する。

## direction freeze Data と optional proposal refinement

親は要求原文、verified decision ledger、freeze candidate から、Human-confirmed な価値、重要な scope / exclude、責務、
意図的な非採用、判断点にならなかった raw specification を含む `freeze_source_snapshot` を入力として固定する。
projection の identity／bijection／meaning-evidence 対応は `direction-freeze-projection` Flow に渡し、Human の価値判断と evidence の意味評価は親に残す。
親は freeze 要約と同じ turn に recommendation、短い理由、Human の一度だけの `Yes / No` を提示し、選択 Data を
`optional-proposal-refinement-routing` Flow に渡す。score、件数 threshold、新しい public knob は作らない。
freeze-integrity では全 constraints の verifier verdict と evidence、最新 snapshot、Human recovery の結果、candidate location を親が準備する。
affected dependency closure、immutable `request.scope` / `request.exclude`、scope 外の意味分類は親の Calculation / adjudication であり、
`freeze-integrity-recovery-routing` Flow はそれらを入力として routing する。未解決 Human Decision が残る candidate は gate へ渡さない。

## structural-health-gate

direction freeze 候補を受け取った場合は、提案が全件却下された場合も同じ親 context の internal
`structural-health-gate` へ渡す。input には generic `caller_context` Data（`workflow_family: plan-family`、
`invocation: explicit-public-parent`）を含める。`context 不成立` は別 route へ切り替えず `stop-incomplete` とする。

親は gate 予算を独立した `rounds` Data として管理し、assessment 1回を1 round と数える。`rounds.limit` は下限1の
ceiling とし、ユーザー指定を優先する。未指定なら親が loop 開始時に固定し、1未満は補正せず `stop-incomplete` とする。
1未満では assessment、producer の再実行、後段を起動しない。gate 予算と review 予算は別 Data とする。
gate assessment、current round、Human response、affected decision / dependency closure、new freeze、new selection、changed review scope を親が確定 Data として
`structural-gate-reopen-routing` Flow に渡す。gate finding の意味、Human response、candidate の採否は親が裁定する。

## review の適用と固定順序

工程順序は `clarify-it → direction freeze projection → optional proposal refinement / freeze-integrity → structural-health-gate → review-refine` であり、gate が `pass` した snapshot だけを
次の判定へ渡す。親は `artifact_kind` と既定 `plan-adversarial-reviewer` の責務から reviewer applicability を判定し、
review skip、review goal、reviewer data、Acceptance Criteria / 設計 readiness とともに `fixed-review-routing` Flow へ渡す。
適用可否、Human の review skip、入力の意味と readiness は親が所有する。

`review-refine` には不変 snapshot、`artifact_kind`、`caller_context`、要求と判定基準、review goal、reviewer・回数制約、
必要なら継続台帳を渡す。回数制約がなければ親が loop 開始時に上限と打ち切りを決める。既定 reviewer は
`plan-adversarial-reviewer`、final trim は `over-engineering-reviewer` のプラン入力モードである。`review_goal` は、ユーザー指定の review goal や追加の具体的な risk がない場合、「実装前プランの具体的な failure path を確認し、確定候補にできるか判断する」とする。これは plan review 自体の既定目的であり、毎回 risk を事前発見することを要求しない。ユーザー指定 goal や追加 risk は既存 reviewer の責務内で追加できる。入力前提不足は
補って再投入するかレビュー不成立として返す。

## review 結果と direction freeze の保護

親は成果物、finding / hold ledger、未解決 finding、final trim、`termination`、`adversarial_review_count` を受け取り、
finding を既存5区分へ evidence と理由付きで裁定する。frozen decision の変更、affected dependency closure、再 review scope は親の意味判断である。
`fixed-review-routing` Flow は applicability、skip、input failure、review result の固定 routing だけを担い、finding の採否を決めない。

review は frozen decisions を守る限り具体化・verification 補強・複雑性削減を許す。frozen decision の変更が必要なら親が `人間確認` へ止める。

## review 完了と final acceptance

review 実行結果、`converged` / `induced-loop`、未解決 finding、レビュー不成立、`round-limit`、`stop-incomplete`、台帳、残存 risk は親が受け取り、
確定候補か未完了かを裁定する。代替 evidence による完了扱い、clarify-it への自動逆遷移、未完了 artifact 保存は行わない。

final acceptance は direction freeze と分離し、既定で必須とする。Human の明示 opt-out は親が approval Action の省略として確定するが、report は残す。
Semantic Delta baseline、summary、方向変更、verification、risk、Human Decision、correction classification は `final-acceptance-routing` Flow の入力 Data とする。
Flow 外では Human acceptance、local / large / closure の分類、correction scope、意味評価を親が保持する。

final report の provenance は親が governing phase-selection point から計算し、過去 cycle や advisor history を露出しない。

## clarify-it 局所再適用の親 routing Data

工程順序は `clarify-it → direction freeze projection → optional proposal refinement / freeze-integrity → structural-health-gate → review-refine` とし、
親は gate return、frozen review finding、review stop、final acceptance correction の分類と affected closure を入力として各 Flow に渡す。
`structural-gate-reopen-routing`、`fixed-review-routing`、`final-acceptance-routing` が deterministic routing の唯一の詳細 witness であり、
Human の再判断、closure の意味、out-of-scope 分類、large purpose / scope change の判断は親が保持する。

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

親は direction freeze summary、recommendation、short reason、Human の一度だけの `Yes / No`、proposal result、freeze-integrity verdict / evidence、
Human recovery decision、latest snapshot、affected closure、scope / exclude を Data として準備する。分岐、proposal stop、check #1 recovery の固定 routing は
`optional-proposal-refinement-routing` と `freeze-integrity-recovery-routing` Flow に集約し、親は Human Decision と evidence の意味を裁定する。

## Programmatic Flows

以下は、親が意味判断を完了して確定 Data を渡した後の局所的な deterministic routing だけを持つ。Flow の procedure、条件、outcome は固定であり、Agent は override、bypass、置換しない。outcome 後に複数の妥当な Action が残る意味判断は親へ返す。

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

### interactive-kernel-preflight

Trigger: 親が最初の clarify-it または candidate Claim adjudication を開始する直前で、kernel preflight を要求したとき。
Inputs: resolve-kernel と necessity-kernel の skill-relative path、各 identity、必要 section、dependencies、plan-interactive の caller/role mapping、親の判定基準。
Procedure: resolve は clarify-it 適用前に一度だけ load・identity・必要本文を検証し、necessity は candidate Claim adjudication 前に一度だけ load・identity・必要本文を検証する。resolve の failure は clarify-it 前、necessity の failure は Claim adjudication 前に `incomplete` とし、検証済み本文だけを親の既存判定基準へ注入する。二つの timing を統合せず、path 解決と最終判断は親が所有する。
Outcomes: 検証済み kernel Data と role mapping、または対応する timing の `incomplete`。Flow は Human の意味判断、Claim の採否、clarify-it の対話結果を expected oracle にせず、loader failure を突破しない。

### observation-reapply

Trigger: 親の最小観測後も同じ decision model に追加の技術 evidence が必要、または既存 evidence と runtime behavior の不一致が観測されたとき。
Inputs: 同じ current decision model、request / repository / Issue / existing specification / required runtime behavior の observation、provenance 付き action evidence、clarify-it の同じ parent context、最小限の observation Action。
Procedure: 親は必要最小限の observation Action だけを実行し、固定した action evidence を Data として同じ model に追加して、同じ parent context で clarify-it を再適用する。technical evidence gap は親境界へ返し、Human Decision Point や clarify-it Stopped に変換しない。contradictory Action、新しい status、固定 output schema、別 context は導入しない。
Outcomes: 更新済み同一 model への clarify-it 再適用結果、または親へ返す technical evidence gap。Flow は observation の意味評価や Human の clarification 内容を expected oracle にしない。

### clarify-loop-bound-routing

Trigger: 各 clarify または resolution loop の開始時に、親が execution bound を固定して routing を要求したとき。
Inputs: 親が loop 開始時に確定した bound、同一 loop 中の immutable bound、remaining decisions、semantic progress、materiality、clarify-it の result。
Procedure: bound を各 loop 開始時に固定し、その loop 中は変更しない。bound 到達、または material な decisions が残るのに semantic progress がない場合は、remaining decisions と reasons を保持して plan-interactive `incomplete` とし downstream を禁止する。clarify-it の `Stopped` は reason と remaining decisions を preserve して plan-interactive `incomplete` とし downstream を禁止する。bound は structural-health-gate と review limit から独立させ、親の terminal を clarify-it `Stopped` として捏造しない。
Outcomes: 固定 bound 内の loop 継続、または preserve された Data 付き `incomplete`。progress と materiality の意味、bound の選択、clarification 内容は親入力であり Flow の expected oracle ではない。

### direction-freeze-projection

Trigger: clarify-it `Completed` の verified Data comparison が一意の direction freeze candidate projection を許可したとき。
Inputs: 要求原文、verified decision ledger、freeze candidate、全意味単位を含む `freeze_source_snapshot`、source evidence、workflow-local opaque ID 候補。
Procedure: source item ごとに非空で一意な ID を一度だけ付与し、source ID 集合と constraint ID 集合の exact bijection、未投影・重複・余分・meaning mismatch の不在を全数照合する。照合済み `{id, frozen_meaning, source_evidence}` だけを projection し、新しい meaning、condition、decision を加えない。不完全・空・再生成・曖昧な投影は proposal 前に `stop-incomplete` とする。
Outcomes: verified Data comparison に対応した unique direction freeze candidate projection、または proposal を禁止する `stop-incomplete`。Human Decision、clarification 内容、evidence の意味評価、candidate の採否は親が保持し expected oracle にしない。

### optional-proposal-refinement-routing

Trigger: direction freeze summary と同じ turn で、親が optional proposal refinement の routing を Human の `Yes / No` として提示するとき。
Inputs: verified direction-freeze candidate S0、短い recommendation と理由、Human の一度だけの `Yes / No`、constrained proposal の fixed 2 pass result、fresh-context freeze-integrity input。
Procedure: `No` は proposal と freeze-integrity を実行せず structural-health-gate へ送る。`Yes` は S0 に束縛した constrained proposal fixed 2 pass と fresh-context freeze-integrity check を実行する。proposal の `stop-incomplete` は authority conflict かつ verified result の場合だけ返却された verified candidate を使った local Human recovery の入力にし、それ以外は pre-refinement fallback と gate を禁止して outward `incomplete` とする。
Outcomes: proposal skipped から gate、proposal と integrity を通過した routing、local Human recovery の入力、または `incomplete`。Yes / No、proposal の意味評価、Human Decision、adoption は親入力・親裁定であり Flow は expected oracle を固定しない。

### freeze-integrity-recovery-routing

Trigger: successful refinement 後の fresh-context freeze-integrity check #1 が `intact`、`violated`、または `indeterminate` を返したとき。
Inputs: check #1 の全 evidence、constraint IDs と candidate locations、Human が再判断した decision、最新 verified snapshot S0、affected dependency closure、immutable `request.scope` / `request.exclude`、recovery freeze、fresh bounded proposal、check #2 context。
Procedure: check #1 が `intact` の場合だけ verified candidate を structural-health-gate へ送る。`violated` または `indeterminate` の場合は check #1 evidence を保持し、親の Human 再判断を反映・verify して affected obligations を closure として計算した後、local clarify-it、verified recovery freeze、fresh bounded proposal fixed 2 pass、fresh-context check #2 を mandatory に順に実行する。`affected_scope = constraint IDs + candidate locations -> dependency closure -> affected obligations`、`request.scope = affected obligations`、`request.exclude = all other candidate obligations` とし、scope 外は `rejected | out-of-scope` として apply せず、locator / closure / exclusivity を安全に確定できなければ proposal 前に `stop-incomplete` とする。authority conflict への Human 再判断を反映・verify した後は、最新 verified snapshot と更新済みの完全な constraints で fresh proposal fixed 2 pass を行う。optional selection、direct structural gate、legacy dialogue route を挟まず、check #2 が `intact` でなければ Trust failure の `stop-incomplete` とし再 reopen しない。
Outcomes: check #1 `intact` の gate routing、check #2 `intact` の verified candidate を structural-health-gate へ送る routing、または Trust failure / scope failure の `stop-incomplete`。Trust failure では check #2 が非 `intact` だったこと、verdict、問題が残る constraint 周辺、`stop-incomplete` だけを報告し、raw advisor history は露出しない。Human recovery の内容、evidence の意味評価、affected closure の妥当性は親が裁定し expected oracle にしない。

### structural-gate-reopen-routing

Trigger: structural-health-gate が current candidate に対する `return`、`pass`、または `insufficient-evidence` を親へ返したとき。
Inputs: gate assessment の problem / impact / recommendation、独立した rounds と `rounds.limit`、current round、Human response、affected decision と dependency closure、new direction freeze、new optional selection、changed review scope。
Procedure: `pass` は downstream review へ送る。`return` は current round が limit 未満のときだけ、gate の問題・影響・推奨対応を Human へ圧縮し、affected closure を clarify-it に局所適用して new freeze と new `Yes / No` selection を経て gate を再実行する。前 cycle の opt-in や governing value を継承せず、新しい direction freeze で proposal refinement の `Yes / No` を再確認する。limit 到達、`insufficient-evidence`、closure failure、または finding 全件却下で内容不変の場合は `stop-incomplete` とし、同一内容の別 identity を作らない。
Outcomes: downstream review、budget 内 local reopen、または `stop-incomplete`。gate finding の意味、Human response、reopen scope、candidate の採否は親入力・親裁定であり Flow は expected oracle を固定しない。

### fixed-review-routing

Trigger: structural gate `pass` 後に、親が artifact snapshot と reviewer applicability / readiness を確定して fixed review routing を要求したとき。
Inputs: artifact_kind、reviewer applicability、Human の明示 review skip、review goal、reviewer data / availability、Acceptance Criteria / design readiness、review result classification。
Procedure: reviewer applicability を explicit skip より先に評価する。nonapplicable は正常に review を省略して起草確定へ進める。applicable かつ明示 skip は review 未実施の draft と残存 risk を `incomplete` として返す。applicable かつ skip なしで input が成立した場合だけ fixed review を実行し、input failure または reviewer failure は review 未成立として `incomplete` にする。review result は `converged` または未解決 finding のない `induced-loop` だけを candidate routing へ渡し、`round-limit`、`stop-incomplete`、未解決 finding を伴う `induced-loop`、review-not-established は candidate にしない。frozen decision の変更を要する finding は親の Human confirmation へ返し、自動 reopen や自動 clarify-it を行わない。
Outcomes: nonapplicable completion、fixed review dispatch、review candidate、parent Human-confirmation input、または review-not-established / `incomplete`。finding の意味的な採否、Human Decision、converged / induced-loop の受容、changed review scope は親裁定であり Flow は唯一の expected oracle にしない。

### final-acceptance-routing

Trigger: gate と fixed review を通過した candidate、または review 非適用の draft が final acceptance の親判定へ到達したとき。
Inputs: final candidate、最新 direction freeze を Semantic Delta baseline とする Data、summary、direction change、verification result、remaining risk、Human Decision、default required / explicit opt-out、親が分類した correction scope。
Procedure: direction freeze、gate pass、review 済み candidate を final acceptance と同一視せず、既定で acceptance Action と report を要求する。explicit opt-out は approval Action だけを省略し report を残す。親が local correction と分類した場合は affected closure の clarify-it、new freeze、new selection、gate、changed-scope review、再 acceptance を routing し、large purpose / scope change は public workflow 全体を再策定し、closure failure は `incomplete` とする。final report は governing phase-selection point の `proposal refinement: executed | skipped` だけを表示する。`executed -> gate return -> skipped = skipped`、`skipped -> gate return -> executed = executed`、`executed -> Trust recovery -> intact = executed`、`executed -> final acceptance correction -> skipped = skipped` とし、gate return または correction の新 selection を使用する。
Outcomes: final acceptance、明示 opt-out 後の report、local correction loop、large reformulation、または closure failure の `incomplete`。local / large / closure の分類、Human acceptance、verification の意味評価、最終採否は親入力・親裁定であり Flow は expected oracle にしない。
