<!-- Generated from shared/. Do not edit directly. -->

# plan-interactive publication v1

この reference は `plan-interactive` の publication phase が所有する destination selection の loader / HOW、
`local-artifact-completion` Flow、publication target を定義する。artifact eligibility / purity の親 authority という
意味の正本は root `SKILL.md` である。publication internal の order anchor はこの reference に co-locate する。

## Programmatic Flows

### local-artifact-completion

以下は final acceptance または明示 opt-out の後に、親が exact target を確定して渡した publication routing だけを持つ。

Trigger: final acceptance が完了した、または Human が final acceptance を明示 opt-out し、親が exact `publication_target` を確定したとき。
Inputs: final acceptance / opt-out Data、凍結した成果物本文 bytes、および親確定の `publication_target` Data。`publication_target` は existing destination の observed destination object identity、または OS-temp の verified temp-root identity / top-level `exact_destination` / exclusive creation intent の排他的 Data を持ち、作成前の directory object identity を要求しない。
Procedure: skill-relative `../../../references/plan-artifact-publication.md` を publication invocation 前に一度だけ load し、identity `plan-artifact-publication-v1` と必要本文を検証する。検証済み reference の `programmatic-publication` Flow に、親確定の `publication_target` をそのまま渡す。Flow の published result から outward status と stdout の Result、Summary、必要な Human Attention、Artifact path だけを projection する。consumer は target selection、candidate ranking、filename、retry bound、publication procedure を再実行・複製しない。
```text
publication_reference = ../../../references/plan-artifact-publication.md
publication_load_timing = once before programmatic-publication use
publication_identity = plan-artifact-publication-v1
publication_use = parent-confirmed publication_target -> programmatic-publication -> outward status/stdout projection
```
Outcomes: published result と `final-candidate` の outward status / stdout projection、`destination-reselection-required`、または `incomplete`。final acceptance / opt-out 前、資格喪失、unsafe / unknown、loader failure は write せず `incomplete` とし、Flow の結果を blind fallback や implicit reselection へ変換しない。

## destination selection

final acceptance が完了した、または Human が final acceptance を明示 opt-out したあと、親は Agentic destination 確定の前に次の Loader Data で `destination-selection` を一度だけ load し、identity と必要本文を検証する。失敗時は推測で destination を確定せず、既存の `incomplete` へ返す。

```text
destination_reference = ../../../references/destination-selection.md
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
