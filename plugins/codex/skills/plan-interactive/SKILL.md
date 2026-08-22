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

- `plan-interactive` の起動または同等の明示要求がある場合だけ起動し、context から暗黙に起動しない。
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

## Phase reference と load 境界

この Skill の phase-specific / conditional な operational procedure と Programmatic Flow は、`references/` 配下の
phase reference へ分離する。root は public parent / Human authority、direction freeze の意味、全件 immutable
`authority_constraints`、mandatory synthesis、fresh integrity、review / final acceptance / publication の親
authority を保持し、reference は親確定 trigger Data を受けた execution procedure だけを持つ。reference は
load predicate、authority、state、status を再定義・拡張・上書きしない。

各 reference の初回成功 load は同一 invocation 内で固定した snapshot として扱い、retry や re-entry で再 load しない。
load 失敗は既存の `incomplete` へ返し、fallback を作らない。conditional load の trigger は、reference を読まずに親が
既読 Data だけから判定できる predicate に限る。

| Phase | Root の load trigger | Reference / identity |
|---|---|---|
| Clarification | invocation 開始 | `references/clarification.md` / `plan-interactive-clarification-v1` |
| Observation | clarify-it 中の同じ decision model に、最小観測後も追加 technical evidence が必要、または evidence / runtime mismatch を親が確定（producer の通常 repository observation では load しない） | `references/observation.md` / `plan-interactive-observation-v1` |
| Pre-freeze advisor | 親が `trigger_only` の成立を確定 | `references/pre-freeze-advisor.md` / `plan-interactive-pre-freeze-advisor-v1` |
| Direction freeze | clarify-it `Completed` と freeze source が揃った | `references/direction-freeze.md` / `plan-interactive-direction-freeze-v1` |
| Synthesis | verified freeze 全件が確定した | `references/synthesis.md` / `plan-interactive-synthesis-v1` |
| Freeze integrity | producer complete、または adopted review revision 反映後 | `references/freeze-integrity.md` / `plan-interactive-freeze-integrity-v1` |
| Structural gate | producer complete かつ integrity intact | `references/structural-gate.md` / `plan-interactive-structural-gate-v1` |
| Review | structural gate pass | `references/review.md` / `plan-interactive-review-v1` |
| Final acceptance | review completion、nonapplicable、または explicit opt-out | `references/final-acceptance.md` / `plan-interactive-final-acceptance-v1` |
| Publication | final acceptance complete、または binding explicit opt-out | `references/publication.md` / `plan-interactive-publication-v1` |

## clarify-it の caller 境界

`plan-interactive` は internal upstream clarify-it の pinned snapshot を同じ parent context で一度だけ使う。invocation
boundary、binding Human authority、verified workflow Data、observation capability、`Completed` / `Stopped` workflow
projection、direction freeze、downstream workflow の所有は caller である `plan-interactive` に残り、public に拡張しない。
loader Data、kernel preflight の HOW、Completed / Stopped の projection procedure は `references/clarification.md` を正本とする。

clarify-it 開始前に、`plan-interactive` は decision resolution 用 kernel の preflight を一度実施する。caller / resolver /
counterpart / authority / ledger の role mapping と load 手順は `references/clarification.md` を正本とし、この Skill では複製しない。

## 観測 Action

親が clarify-it 中の同じ decision model について、最小観測後も追加 technical evidence の必要または evidence /
runtime mismatch を確定した場合だけ、`references/observation.md` を load して observation Action を実行する。
producer handoff のための通常の repository observation や、freeze 後 phase の調査ではこの reference を load しない。
technical fact の取得は常に親 authority であり、観測の意味評価、decision-model への再適用、Human clarification は親責務として
この Skill に残る。この context は conditional であり、trigger が成立しない run では load しない。

## clarify-it result と Plan completion の非同一性

`clarify-it: Completed` は Human Decision Context の completion であり、Plan Artifact completion ではない。回数上限、
remaining decisions count、semantic progress 管理、Tugite 独自 completion 判定は `plan-interactive` 側で持たない。
`Completed` / `Stopped` の projection procedure は `references/clarification.md` を正本とする。

`direction-freeze-projection` Flow が semantic projection の唯一の詳細 witness である。親は verified comparison を入力として保持し、
projection を workflow completion や candidate acceptance と同一視しない。

direction freeze は成果物全文の固定ではなく、人間が確定した意味判断を保護する境界とする。親は方向性、実装イメージ、
重要な verification を圧縮して人間へ示し、freeze 後の mandatory producer へ frozen decisions を immutable `authority_constraints` として渡す。
大きな purpose または scope の変更が入力された場合は既存成果物へ増分追加せず、この public workflow 全体を再策定する。
過去 decision は自動継承せず、candidate prior decisions と再利用知見として現在の要求と evidence で再検証する。

## direction freeze の意味

親は要求原文、verified decision ledger、raw source と evidence から Human-confirmed な価値、重要な scope / exclude、責務、
意図的な非採用、判断点にならなかった raw specification を全件投影する。verified freeze 全件を immutable
`authority_constraints` とし、direction freeze 自体を existing verified candidate または初期 S0 として扱わない。未解決 Human
Decision が残る freeze は producer へ渡さない。freeze source construction、verification derivation の HOW、projection の
identity／bijection 照合は `references/direction-freeze.md` を正本とする。

## freeze 前 advisor

親は次の `trigger_only` に固定した 4 条件が成立する場合だけ、非binding な read-only `plan-quality-advisor` を
起動する。この 4 条件は root の唯一の load trigger predicate であり、reference 側で再定義しない。

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

親が上記 trigger を確定したあと、handoff と adoption ledger の実行手順だけを
`references/pre-freeze-advisor.md` から読む。

## Synthesis: mandatory constrained producer

plan-candidate-producer の invocation は mandatory であり、`plan-interactive` は caller-owned constrained authority を
保持する。`authority = constrained`、`authority_constraints = verified freeze 全件` を注入し、direction freeze を
existing verified candidate や初期 S0 として渡さない。additional refinement の Human choice で producer を skip せず、
direction freeze から gate / review / final acceptance へ直行しない。loader、handoff、routing の HOW は
`references/synthesis.md` を正本とする。

## Freeze integrity

Human authority protection は一つの fresh freeze-integrity procedure を正本とする。producer `complete` の latest S2 の後、
または `review-refine` の adopted revision を反映した latest snapshot の後に、全 constraint ID / `frozen_meaning` /
`source_evidence` を fresh に独立照合する。stale check や subset check を再利用しない。verifier handoff と recovery
routing の HOW は `references/freeze-integrity.md` を正本とする。

## Structural gate

producer `complete` かつ freeze-integrity `intact` の current verified candidate だけを internal `structural-health-gate`
へ渡す。direction freeze や `clarify-it: Completed` を直接送らない。gate evidence、current round、candidate の採否は
親が保持する。caller context、独立した gate budget、reopen / retry routing の HOW は `references/structural-gate.md`
を正本とする。

## Review

工程順序は `clarify-it → direction freeze projection → mandatory constrained producer → freeze-integrity →
structural-health-gate → review dispatch` であり、gate が `pass` した snapshot だけを次へ渡す。review applicability /
opt-out / readiness、finding の採否、artifact status は親が所有する。`review-refine` は applicable かつ no opt-out かつ
ready のときだけ load / execute する。handoff、`review-dispatch` Flow、re-entry の HOW は `references/review.md` を
正本とする。

## Final acceptance

direction freeze、gate pass、review 済み candidate を final acceptance と同一視せず、既定で必須とする。Human の明示
opt-out は approval Action の省略として確定するが report は残す。final acceptance は direction freeze / gate / review
のいずれとも別責務であり、最終的な Human authority を持つ。report / acceptance Action、local correction / large
reformulation の routing HOW は `references/final-acceptance.md` を正本とする。

## Publication

final acceptance が完了した場合、または Human が final acceptance を明示 opt-out した場合だけ、成果物本文の byte
snapshot を凍結して publication routing を開始する。それ以外の `incomplete`、direction freeze、gate、review、
acceptance candidate では path 選択も write も行わない。artifact body は凍結した成果物本文だけを持ち、要約や
process Data、gate / review 結果、decision / finding ledger を追記しない。保存した artifact は Git 管理、永続保存、
最終採用、後続 Action の許可を意味しない。destination selection、publication target 確定、`local-artifact-completion`
Flow の HOW は `references/publication.md` を正本とする。

## Programmatic Flows

以下は、親が意味判断を完了して確定 Data を渡した後の局所的な deterministic routing だけを持つ。Flow の procedure、条件、outcome は固定であり、Agent は override、bypass、置換しない。outcome 後に複数の妥当な Action が残る意味判断は親へ返す。

各 Flow の Trigger / Inputs / Procedure / Outcomes の唯一の canonical witness は、上記の phase reference table が指す
1ファイルだけにある。root はいずれの Flow 本文も複製しない。

```text
clarification
  -> direction freeze
  -> synthesis
  -> freeze-integrity
  -> structural gate
  -> review dispatch
  -> final acceptance
  -> publication eligibility
```
