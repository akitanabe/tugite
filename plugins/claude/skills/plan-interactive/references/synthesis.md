<!-- Generated from shared/. Do not edit directly. -->

# plan-interactive synthesis v1

この reference は `plan-interactive` の synthesis phase が所有する `plan-artifact-design` loader、
`plan-candidate-producer` への handoff、constrained routing の HOW を定義する。mandatory producer invocation、
caller-owned constrained authority、全 constraints 入力、producer skip 禁止という意味の正本は root `SKILL.md` である。

## plan-artifact-design の parent-owned load

`interactive-kernel-preflight` に相乗りしない。clarify-it 中は load しない。最初の artifact 本文起草・再構成の直前に、親は次の
Loader Data で局所 validation として一度だけ load し、identity と required section を検証する。最初の成功 snapshot を同一
invocation 内で固定し、gate retry の producer 再実行と review 採用修正でも再利用する。失敗時は推測で従来形式の artifact を生成せず、既存の
`incomplete` へ返す。検証済み本文だけを既存の判定基準へ注入する。

```text
design_reference = ../../../references/plan-artifact-design.md
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

## Programmatic Flows

### constrained-producer-routing

Trigger: 親が verified direction freeze 全件を immutable `authority_constraints` として確定し、mandatory constrained producer の routing を要求したとき。
Inputs: initial Action 実行前 Data として、要求原文、repository observation、`authority = constrained`、verified freeze 全件の `authority_constraints`、producer invocation Data。direction freeze を existing verified candidate / 初期 S0 としては含めない。producer result は含めない。
Procedure: producer を必ず一度起動する。direction freeze から gate / review / final acceptance へ直行せず、additional refinement の Human choice で base synthesis を skip しない。producer `stop-incomplete` は downstream を起動せず `incomplete` とする。`authority_conflict` は constraint ID、evidence、影響範囲とともに Human boundary へ返す。`complete` の latest S2 だけを freeze-integrity へ送る。
Outcomes: producer-complete latest S2 の integrity routing、`authority_conflict` の Human boundary、または `incomplete`。constraint の意味変更、candidate の採否、Human Decision は親裁定であり Flow は expected oracle にしない。
