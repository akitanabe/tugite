---
name: plan-interactive
description: >-
  ユーザーが明示した場合だけ、人間との方向性裁定から計画・設計成果物を起草し、mandatory な common Plan
  synthesis、gate、bounded review を経た確定候補または未完了結果を返す public workflow。
---
<!-- Generated from shared/. Do not edit directly. -->

# plan-interactive

この Skill は人間参加型の自由形式計画・設計成果物を起草し、親が確定候補または未完了結果を返す public workflow
である。`plan-agent` と自動切替せず、双方向ともユーザーの明示起動だけで開始する。

`plan-agent` と `plan-interactive` の違いは、Plan synthesis 前の direction / authority の決定方法と、
`plan-interactive` 固有の Human recovery / final acceptance に限定する。full Plan synthesis の canonical owner は
既存 `plan-candidate-producer` である。direction freeze は constraint Data であり、Plan Artifact candidate または
初期 S0 ではない。

```text
plan-agent
  Agent-owned direction
  authority = discretionary
        ↓
plan-candidate-producer

plan-interactive
  clarify-it + verified Human direction freeze
  authority = constrained
  authority_constraints = verified freeze 全件
        ↓
plan-candidate-producer
```

## 発火制御と責務

- `plan-interactive` の起動または同等の明示要求がある場合だけ起動し、context から暗黙起動しない。
- 各 platform の invocation metadata は上記の explicit-only 契約を表し、その範囲を拡張しない。
- 実装、委譲、Worker 起動、worktree 操作、後続の実装開始を行わず、final acceptance 後の final-candidate だけを local artifact へ保存する。
- 起草、対話、mandatory synthesis、gate、review、final acceptance 候補または未完了の返却までを担う。人間は方向性と最終結果の責任を持ち、
  public workflow parent は planner として、調査、具体化、整合性、verification、工程の経過責任を持つ。後続 Action は
  人間へ残す。

## 入力と成果物

要求原文、目的、対象、成功条件、scope、exclude、依存、制約、current state を先に観測する。blocking な不足を
推測せず、軽微な不足は根拠付き assumption に分離する。一般的な artifact content（目的、観測可能な成功条件、設計、scope と exclude、
依存、制約、verification、残存 risk、未確定の問い）は検証済み `plan-artifact-design` を正本とする。選択理由と棄却した代替案は
Human-confirmed decision として記録する。

成果物種別を `artifact_kind` Data として保持する。実装前提プラン系か否かは reviewer 適用可否だけに使い、自由形式
成果物をプラン系へ変える理由にしない。実装前提プラン系は `Acceptance Criteria` と `設計` の節名を持つ。

## clarify-it の caller mapping

`plan-interactive` 起動時に、親は次の Loader Data で pinned 内部 snapshot を一度だけ load する。最初の成功本文を同一
invocation 内で固定し、local clarify-it（freeze-integrity recovery、gate reopen、final acceptance local correction）でも
再 load しない。load 失敗時は推測で fallback clarification を行わず、既存の `incomplete` へ返す。clarify-it の semantic identity は検証しない。

```text
clarify_it_reference = ../../references/upstream/clarify-it/SKILL.md
clarify_it_load_timing = once at plan-interactive start
clarify_it_snapshot = first successful body frozen for the invocation
clarify_it_failure = existing incomplete; no fallback clarification
clarify_it_identity_check = none
```

`references/philosophy.md` の参照要否と相対 path は、loaded artifact 自身の規則に従う。

```text
application = pinned internal upstream clarify-it snapshot in the same plan-interactive parent context
caller_owns = invocation boundary | binding Human authority | verified workflow Data | observation capability | Completed/Stopped workflow projection | direction freeze | downstream workflow
public_extension = none
```

## kernel preflight と caller mapping

`interactive-kernel-preflight` Flow が resolve-kernel の load timing、identity、必要本文、failure routing の唯一の詳細 witness である。
親は skill-relative loader Data、caller=`plan-interactive`、resolver=`planner`、counterpart=`human`、authority=`binding`、
ledger=`decision ledger` を入力として準備し、検証済み本文だけを既存の判定基準へ注入する。

stable Loader Data は次の値を持つ。

```text
resolve_path = ../../references/resolve-kernel.md
resolve_identity = resolve-kernel-v1
resolve_dependencies = none
resolve_required_sections = [Caller boundary と role, Current verified snapshot、working state、frontier, Atomic resolution unit, Exit と停止, Kernel non-dependency]
caller = plan-interactive
resolver = planner
counterpart = human
authority = binding
ledger = decision ledger
```

`interactive-kernel-preflight` Flow はこの Data を使い、path 解決と最終判断は親が所有する。

## 観測 Action

親は current decision model、parent context、必要な runtime behavior、最小 observation request / criteria を Action 実行前 Data として準備する。
`observation-reapply` Flow が最小 Observation Action の実行と technical evidence gap の返却を唯一の詳細 witness とする。
観測の意味評価、decision-model への再適用、Human clarification、contradictory Action の裁定は Flow 外の親責務である。

## clarify-it result の projection

clarify phase の終了判断は次の2つだけとする。回数上限、remaining decisions count、semantic progress 管理、Tugite 独自 completion 判定は
`plan-interactive` 側で持たない。`clarify-it: Completed` は Human Decision Context の completion であり、Plan Artifact completion ではない。

- `Completed` → 親が current decision model から freeze に必要な意味単位を抽出する（clarify-it 出力に固定 schema を要求しない）→ `freeze_source_snapshot` → `direction-freeze-projection`
- `Stopped` → 停止理由と未解決 Human decisions / inconsistency を保持した既存 `incomplete`。独自 clarification 継続も、独自 recovery / continuation status も作らない

`direction-freeze-projection` Flow が semantic projection の唯一の詳細 witness である。親は verified comparison を入力として保持し、
projection を workflow completion や candidate acceptance と同一視しない。

direction freeze は成果物全文の固定ではなく、人間が確定した意味判断を保護する境界とする。親は方向性、実装イメージ、
重要な verification を圧縮して人間へ示し、freeze 後の mandatory producer へ frozen decisions を immutable `authority_constraints` として渡す。
大きな purpose または scope の変更が入力された場合は既存成果物へ増分追加せず、この public workflow 全体を再策定する。
過去 decision は自動継承せず、candidate prior decisions と再利用知見として現在の要求と evidence で再検証する。

## direction freeze Data

親は要求原文、verified decision ledger、raw source と evidence から、Human-confirmed な価値、重要な scope / exclude、責務、
意図的な非採用、判断点にならなかった raw specification を含む `freeze_source_snapshot` を入力として固定する。
projection の identity／bijection／meaning-evidence 対応は `direction-freeze-projection` Flow に渡し、Human の価値判断と evidence の意味評価は親に残す。
verified freeze 全件を immutable `authority_constraints` とし、direction freeze 自体を existing verified candidate または初期 S0 として扱わない。
未解決 Human Decision が残る freeze は producer へ渡さない。

## plan-artifact-design の parent-owned load

`interactive-kernel-preflight` に相乗りしない。clarify-it 中は load しない。最初の artifact 本文起草・再構成の直前に、親は次の
Loader Data で局所 validation として一度だけ load し、identity と required section を検証する。最初の成功 snapshot を同一
invocation 内で固定し、gate retry の producer 再実行と review 採用修正でも再利用する。失敗時は推測で従来形式の artifact を生成せず、既存の
`incomplete` へ返す。検証済み本文だけを既存の判定基準へ注入する。

```text
design_reference = ../../references/plan-artifact-design.md
design_load_timing = once immediately before first artifact drafting or restructuring in the invocation
design_identity = plan-artifact-design-v1
design_required_sections = [適用範囲, Human-facing Summary, Agent-facing Detail, Verification / Completion Criteria の近接配置, Acceptance Criteria / Verification / Completion Criteria の責務分離, Information placement, Reference pointer]
design_failure = existing incomplete path; no new status
design_snapshot = first successful verified body is frozen for the invocation
design_use = inject verified body into existing 判定基準; Loader Data and path are not producer Inputs; no dedicated channel or return field
```

## constrained producer の caller ownership

plan-candidate-producer の invocation boundary、constrained authority、resolution execution bound は `plan-interactive` が所有する。
internal `plan-candidate-producer` の開始時に、caller=`plan-interactive`、resolver=planner、counterpart=`plan-quality-advisor`（Resolution
Transaction 外の one-shot observation）を mapping し、`authority = constrained` を注入する。`authority_constraints` は verified
direction freeze 全件であり、subset や再生成した集合ではない。direction freeze を existing verified candidate / 初期 S0 として渡さない。
初回は要求、repository observation、全 authority constraints から candidate を構成し、gate retry では current verified candidate を
S0 として同じ constraints で再実行してよい。

```text
caller = plan-interactive
authority = constrained
authority_constraints = verified freeze 全件
freeze_as_existing_s0 = prohibited
producer_skip = prohibited
```

`plan-candidate-producer` は request、repository observation、全 authority constraints から `plan-artifact-design` 準拠の candidate を構成し、
RMO grounding、verify、固定 2 advisor pass を閉じる。`complete` で返した latest S2 / current verified candidate だけを downstream 候補にする。
`stop-incomplete` の場合は caller-owned parent がそこで停止し、integrity / gate / review を選択しない。`authority_conflict` は
constraint ID、evidence、影響範囲とともに Human boundary へ返す。producer の固定 2-pass と重複する additional refinement orchestration は置かない。

## freeze-integrity

Human authority protection は一つの freeze-integrity procedure を正本とする。candidate-changing boundary の後に、latest candidate と
全 constraint ID / `frozen_meaning` / `source_evidence` を fresh に照合する。stale check や subset check を再利用しない。

trigger は次に固定する。

- 各 producer invocation が `complete` で返した latest S2 の後。初回、gate retry、new freeze 後の recovery を含む。
- `review-refine` の adopted revision を反映した latest snapshot の後。

final-acceptance local correction は、affected closure に対する local `clarify-it → verified new freeze → constrained producer complete` へ戻すため、
producer-complete trigger で保護する。

親は全 constraints の verifier verdict と evidence、最新 snapshot、candidate location、fixed bounds / invocation Data を初期入力として準備する。
`freeze-integrity-routing` Flow が deterministic routing の唯一の詳細 witness である。全 frozen meaning を保持した AC / verification /
local detail の追加は許可し、baseline 全文を変更禁止対象にしない。

## structural-health-gate

producer `complete` かつ freeze-integrity `intact` の current verified candidate だけを、同じ親 context の internal
`structural-health-gate` へ渡す。direction freeze や `clarify-it: Completed` を gate へ直接送らない。input には generic
`caller_context` Data（`workflow_family: plan-family`、`invocation: explicit-public-parent`）を含める。`context 不成立` は別 route へ切り替えず `stop-incomplete` とする。

親は gate 予算を独立した `rounds` Data として管理し、assessment 1回を1 round と数える。`rounds.limit` は下限1の
ceiling とし、ユーザー指定を優先する。未指定なら親が loop 開始時に固定し、1未満は補正せず `stop-incomplete` とする。
1未満では assessment、producer の再実行、後段を起動しない。gate 予算と review 予算は別 Data とする。
gate assessment / evidence、current round、fixed context を初期 Data として `structural-gate-reopen-routing` Flow に渡す。
Human response、affected decision / dependency closure、new freeze は return 後の intermediate Data とし、
gate finding の意味、Human response、candidate の採否は親が裁定する。

## review の適用と dispatch

工程順序は `clarify-it → direction freeze projection → mandatory constrained producer → freeze-integrity → structural-health-gate → review dispatch` であり、gate が `pass` した snapshot だけを
次の判定へ渡す。review applicability / opt-out / readiness は public parent dispatch が `plan-agent` と同じ意味で所有する。
`review-refine` は dispatch 後の loop / termination を所有し、artifact status は caller が別に裁定する。
親は `artifact_kind` と既定 `plan-adversarial-reviewer` の責務から reviewer applicability を判定し、
確認済み applicability、明示 opt-out、review goal、reviewer data、Acceptance Criteria / 設計 readiness とともに Action 実行前 Data として `review-dispatch` Flow へ渡す。
適用可否、Human の review opt-out、入力の意味と readiness は親が所有する。

`review-refine` には不変 snapshot、`artifact_kind`、`caller_context`、要求と判定基準、review goal、reviewer・回数制約、
必要なら継続台帳を渡す。回数制約がなければ親が loop 開始時に上限と打ち切りを決める。既定 reviewer は
`plan-adversarial-reviewer`、final trim は `over-engineering-reviewer` のプラン入力モードである。`review_goal` は、ユーザー指定の review goal や追加の具体的な risk がない場合、「実装前プランの具体的な failure path を確認し、確定候補にできるか判断する」とする。これは plan review 自体の既定目的であり、毎回 risk を事前発見することを要求しない。ユーザー指定 goal や追加 risk は既存 reviewer の責務内で追加できる。入力前提不足は
補って再投入するかレビュー不成立として返す。

## review 結果と direction freeze の保護

親は成果物、finding / hold ledger、未解決 finding、final trim、`termination`、`adversarial_review_count` を受け取り、
finding を既存5区分へ evidence と理由付きで裁定する。frozen decision の変更、affected dependency closure、再 review scope は親の意味判断である。
`review-dispatch` Flow は applicability、opt-out、readiness、input failure の固定 routing だけを担い、finding の採否を決めない。
`termination` は review-refine がどのように終了したかを示す process Data であり、candidate status は caller が別に裁定する。

review は frozen decisions を守る限り具体化・verification 補強・複雑性削減を許す。採用修正後の latest snapshot は fresh integrity check を通してから
final acceptance 候補にする。frozen decision の変更が必要なら親が `人間確認` へ止める。

## review 完了と final acceptance

review 実行結果、`converged` / `induced-loop`、未解決 finding、レビュー不成立、`round-limit`、`stop-incomplete`、台帳、残存 risk は親が受け取り、
確定候補か未完了かを裁定する。代替 evidence による完了扱い、clarify-it への自動逆遷移、未完了 artifact 保存は行わない。
`nonapplicable` と `applicable + explicit opt-out` は normal completion として Human final acceptance へ進める。

final acceptance は direction freeze と分離し、既定で必須とする。Human の明示 opt-out は親が approval Action の省略として確定するが、report は残す。
Semantic Delta baseline、summary、方向変更、verification、risk、default required / pre-existing binding opt-out は `final-acceptance-routing` Flow の初期入力 Data とする。
Human response と correction classification は acceptance Action 後に親が裁定して再投入する intermediate Data とする。
Flow 外では Human acceptance、local / large / closure の分類、correction scope、意味評価を親が保持する。

final report は過去 cycle や advisor history を露出しない。

## clarify-it 局所再適用の親 routing Data

工程順序は `clarify-it → direction freeze projection → mandatory constrained producer → freeze-integrity → structural-health-gate → review dispatch` とし、
親は gate return、frozen review finding、review stop、final acceptance correction の分類と affected closure を入力として各 Flow に渡す。
`structural-gate-reopen-routing`、`review-dispatch`、`final-acceptance-routing` が deterministic routing の唯一の詳細 witness であり、
Human の再判断、closure の意味、out-of-scope 分類、large purpose / scope change の判断は親が保持する。

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

## Programmatic Flows

以下は、親が意味判断を完了して確定 Data を渡した後の局所的な deterministic routing だけを持つ。Flow の procedure、条件、outcome は固定であり、Agent は override、bypass、置換しない。outcome 後に複数の妥当な Action が残る意味判断は親へ返す。

### local-artifact-completion

以下は final acceptance または明示 opt-out の後に、親が exact target を確定して渡した publication routing だけを持つ。

Trigger: final acceptance が完了した、または Human が final acceptance を明示 opt-out し、親が exact `publication_target` を確定したとき。
Inputs: final acceptance / opt-out Data、凍結した成果物本文 bytes、および親確定の `publication_target` Data。`publication_target` は existing destination の observed destination object identity、または OS-temp の verified temp-root identity / top-level `exact_destination` / exclusive creation intent の排他的 Data を持ち、作成前の directory object identity を要求しない。
Procedure: skill-relative `../../references/plan-artifact-publication.md` を publication invocation 前に一度だけ load し、identity `plan-artifact-publication-v1` と必要本文を検証する。検証済み reference の `programmatic-publication` Flow に、親確定の `publication_target` をそのまま渡す。Flow の published result から outward status と stdout の Result、Summary、必要な Human Attention、Artifact path だけを projection する。consumer は target selection、candidate ranking、filename、retry bound、publication procedure を再実行・複製しない。
```text
publication_reference = ../../references/plan-artifact-publication.md
publication_load_timing = once before programmatic-publication use
publication_identity = plan-artifact-publication-v1
publication_use = parent-confirmed publication_target -> programmatic-publication -> outward status/stdout projection
```
Outcomes: published result と `final-candidate` の outward status / stdout projection、`destination-reselection-required`、または `incomplete`。final acceptance / opt-out 前、資格喪失、unsafe / unknown、loader failure は write せず `incomplete` とし、Flow の結果を blind fallback や implicit reselection へ変換しない。

## destination selection

final acceptance が完了した、または Human が final acceptance を明示 opt-out したあと、親は Agentic destination 確定の前に次の Loader Data で `destination-selection` を一度だけ load し、identity と必要本文を検証する。失敗時は推測で destination を確定せず、既存の `incomplete` へ返す。

```text
destination_reference = ../../references/destination-selection.md
destination_load_timing = once before Agentic destination confirmation
destination_identity = destination-selection-v1
destination_required_sections = [Inputs / Outputs, Candidate facts, caller_owned_predicates の適用範囲, Programmatic Flows, Agentic unique selection, destination-reselection]
destination_failure = existing incomplete path; no new status
```

親は既存 project-local の用途 evidence と verified OS-temp を candidate facts として観測し、Git ignored/index predicates を project-local および canonical path が repository 内に入る OS-temp にだけ適用する範囲で渡す。repository 外の verified OS-temp に Git predicates を適用しない。decoy 一覧 HOW と ranking procedure をこの Skill に置かない。

destination 確定は destination-qualification の 3 値に従う:

1. explicit 確定 → それを使う
2. qualified set のときだけ unique selection 本文を適用する
3. explicit incomplete および入力不足 incomplete → unique selection を起動せず incomplete。`publication_target` を組まない

成功 destination に filename / retry を足して `publication_target` を確定し、`local-artifact-completion` へ渡す。
`destination-reselection-required` を受けたとき、元が Human explicit なら同じ requested_destination を保持し unique-best auto-select へ落とさない。元が auto unique-best なら別 destination を無言で選ばない。

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

Trigger: 親が最初の clarify-it を開始する直前で、kernel preflight を要求したとき。
Inputs: resolve-kernel の skill-relative path、identity、必要 section、dependencies、plan-interactive の caller/role mapping、親の判定基準。
Procedure: resolve は clarify-it 適用前に一度だけ load・identity・必要本文を検証する。resolve の failure は clarify-it 前に `incomplete` とし、検証済み本文だけを親の既存判定基準へ注入する。path 解決と最終判断は親が所有する。
Outcomes: 検証済み kernel Data と role mapping、または `incomplete`。Flow は Human の意味判断、clarify-it の対話結果を expected oracle にせず、loader failure を突破しない。

### observation-reapply

Trigger: 親の最小観測後も同じ decision model に追加の技術 evidence が必要、または既存 evidence と runtime behavior の不一致が観測されたとき。
Inputs: initial Action 実行前 Data として、同じ current decision model、親確定の最小 observation request / criteria、required runtime behavior、同じ clarify-it parent context、current verified context。observation result と action evidence は含めない。
Procedure: 親確定の最小 Observation Action を一度だけ実行し、result と provenance / evidence を中間 Data として freeze して Agentic 親へ返す。technical evidence gap は親境界へ返し、Human Decision Point や clarify-it Stopped に変換しない。contradictory Action、新しい status、固定 output schema、別 context は導入しない。decision-model への再適用は Flow に置かない。
Outcomes: observation result と provenance / evidence、または親へ返す technical evidence gap。Flow は observation の意味評価、decision-model への再適用、Human の clarification 内容を expected oracle にしない。

### direction-freeze-projection

Trigger: clarify-it `Completed` の verified Data comparison が一意の direction freeze candidate projection を許可したとき。
Inputs: initial Calculation 実行前 Data として、要求原文、verified decision ledger、全意味単位を含む raw `freeze_source_snapshot`、source evidence、workflow-local opaque ID generation input。direction freeze candidate は含めない。
Procedure: source item ごとに非空で一意な ID を一度だけ付与し、source から projection した direction freeze candidate と exact comparison result を中間 Data として扱う。source ID 集合と constraint ID 集合の exact bijection、未投影・重複・余分・meaning mismatch の不在を全数照合し、照合済み `{id, frozen_meaning, source_evidence}` だけを candidate Outcome へ projection する。新しい meaning、condition、decision は加えず、不完全・空・再生成・曖昧な投影は producer 前に `stop-incomplete` とする。
Outcomes: verified Data comparison に対応した unique direction freeze candidate projection、または producer を禁止する `stop-incomplete`。Human Decision、clarification 内容、evidence の意味評価、candidate の採否は親が保持し expected oracle にしない。

### constrained-producer-routing

Trigger: 親が verified direction freeze 全件を immutable `authority_constraints` として確定し、mandatory constrained producer の routing を要求したとき。
Inputs: initial Action 実行前 Data として、要求原文、repository observation、`authority = constrained`、verified freeze 全件の `authority_constraints`、producer invocation Data。direction freeze を existing verified candidate / 初期 S0 としては含めない。producer result は含めない。
Procedure: producer を必ず一度起動する。direction freeze から gate / review / final acceptance へ直行せず、additional refinement の Human choice で base synthesis を skip しない。producer `stop-incomplete` は downstream を起動せず `incomplete` とする。`authority_conflict` は constraint ID、evidence、影響範囲とともに Human boundary へ返す。`complete` の latest S2 だけを freeze-integrity へ送る。
Outcomes: producer-complete latest S2 の integrity routing、`authority_conflict` の Human boundary、または `incomplete`。constraint の意味変更、candidate の採否、Human Decision は親裁定であり Flow は expected oracle にしない。

### freeze-integrity-routing

Trigger: producer が `complete` で返した latest S2 の後、または `review-refine` の adopted revision を反映した latest snapshot の後に、親が fresh freeze-integrity を要求したとき。
Inputs: initial Action 実行前 Data として、全 constraint ID / `frozen_meaning` / `source_evidence`、latest candidate、trigger 種別（post-producer / post-review）、fixed bounds / invocation Data。stale check evidence と subset check は含めない。Human decision と recovery freeze は含めない。
Procedure: 全 constraints を latest candidate に対して fresh に独立照合する。stale check や subset check を再利用しない。`intact` は次の gate、review dispatch、または final acceptance へ進める。post-producer `violated` は constraint を変更せずには安全な candidate を作れない場合、`authority_conflict` として Human boundary へ返し、new freeze 後は producer から再開する。post-review `violated` は violating working snapshot を promote せず、last constraint-intact verified snapshot を維持し、影響 finding を `human-confirmation` へ再裁定する。Human が freeze を維持する場合は finding を再裁定し、安全な candidate に対する changed-scope review を経て final acceptance へ進む。Human が direction を変える場合は `Human decision → verified new freeze → constrained producer complete latest S2 → fresh integrity → gate → review dispatch → final acceptance` の順で再入する。`indeterminate` は Agent authority 内で evidence を取得できる場合だけ同じ candidate を fresh に再照合する。取得不能、closure 不成立、または fixed budget 到達では `incomplete` とする。violating snapshot を再開 baseline にしない。
Outcomes: `intact` の downstream routing、post-producer `authority_conflict`、post-review last-intact 維持と `human-confirmation`、または `incomplete`。Human recovery の内容、evidence の意味評価、finding の採否は親が裁定し expected oracle にしない。

### structural-gate-reopen-routing

Trigger: structural-health-gate が current candidate に対する `return`、`pass`、または `insufficient-evidence` を親へ返したとき。
Inputs: initial Action 実行前 Data として、gate result / evidence の problem / impact / recommendation、独立した `rounds.limit`、current round、fixed parent context、current verified candidate、同じ immutable `authority_constraints`。Human response、affected closure、new freeze、producer result、integrity result は含めない。
Procedure: `pass` は review dispatch へ送る。`return` かつ current round が limit 未満の場合だけ finding を Agentic 親へ返す。親が constraints 内の具体化で閉じると裁定した場合は、current verified candidate と同じ constraints で producer を retry し、`complete` 後に fresh integrity check を行う。constraint 変更が必要なら local `clarify-it → new freeze → constrained producer` へ戻し、complete 後に fresh integrity を行う。各 result / evidence は中間 Data として親へ戻し、親裁定 Data を再投入してから次へ進む。前 cycle の freeze / constraints / review opt-out を次 cycle の既定として継承しない。limit 到達、`insufficient-evidence`、closure failure、または evidence 不足は `incomplete` とし、別 identity を作らない。old integrity evidence を再利用しない。
Outcomes: review dispatch、budget 内 producer retry または new-freeze recovery、または `incomplete`。gate finding の意味、Human response、constraint 変更要否、candidate の採否は親入力・親裁定であり Flow は expected oracle を固定しない。

### review-dispatch

Trigger: 親が artifact snapshot と review readiness を確定し、review routing を要求したとき。
Inputs: 親確定の artifact_kind、applicability、user review opt-out、review goal、reviewer data、Acceptance Criteria / 設計 readiness、reviewer availability。
Procedure: parent-confirmed applicability は opt-out より先に評価する。nonapplicable は normal completion、applicable + opt-out は normal completion、applicable + no opt-out + ready は review dispatch とする。readiness failure または reviewer failure は review-not-established として親へ返す。
Outcomes: nonapplicable、opt-out、review dispatch、または明示的な `review-not-established`。Flow は accept を返さず、finding の意味的な採否と artifact status は親へ返す。

### final-acceptance-routing

Trigger: gate と review dispatch を通過した candidate、または review 非適用 / explicit opt-out の draft が final acceptance の親判定へ到達したとき。
Inputs: initial Action 実行前 Data として、final candidate、最新 direction freeze を Semantic Delta baseline とする Data、summary、direction change、verification result、remaining risk、default required、pre-existing binding explicit opt-out、acceptance invocation Data。Human Decision と correction classification result は含めない。
Procedure: direction freeze、gate pass、review 済み candidate を final acceptance と同一視せず、既定で acceptance Action と report を要求する。explicit opt-out は approval Action だけを省略し report を残す。それ以外は acceptance Action を一度実行し、Human response を中間 Data として Agentic 親へ返す。親が裁定した local / large / closure classification の再投入後だけ routing する。local correction は affected closure の local `clarify-it → verified new freeze → constrained producer complete` を順に routing し、complete 後の fresh integrity、gate、changed-scope review、再 acceptance を経る。各 autonomous result と親裁定 Data を中間 Data として parent round-trip する。large purpose / scope change は public workflow 全体を再策定し、closure failure は `incomplete` とする。non-intact な snapshot から final acceptance へ直行しない。
Outcomes: final acceptance、明示 opt-out 後の report、local correction loop、large reformulation、または closure failure の `incomplete`。local / large / closure の分類、Human acceptance、verification の意味評価、最終採否は親入力・親裁定であり Flow は expected oracle にしない。
