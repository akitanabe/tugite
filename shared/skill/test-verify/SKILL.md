<!-- @only claude -->
---
name: test-verify
description: >-
  明示された bounded test target を runtime evidence で検証し、因果境界内の Problem だけを直接修復して Completion Gate と final verification まで閉じる。
disable-model-invocation: true
---
<!-- @/only -->
<!-- @only codex -->
---
name: test-verify
description: >-
  明示された bounded test target を runtime evidence で検証し、因果境界内の Problem だけを直接修復して Completion Gate と final verification まで閉じる。
---
<!-- @/only -->
<!-- @only cursor -->
---
name: test-verify
description: >-
  明示された bounded test target を runtime evidence で検証し、因果境界内の Problem だけを直接修復して Completion Gate と final verification まで閉じる。
disable-model-invocation: true
---
<!-- @/only -->

# test-verify

## Identity and authority

<!-- @contract test-verify-explicit-only -->
`test-verify` は Human が明示した場合だけ開始する public Skill である。自然言語の test request だけから暗黙に起動せず、別 workflow から自動遷移しない。
<!-- @/contract -->

<!-- @contract test-verify-direct-ownership -->
top-level で `test-verify` を実行する agent が direct owner であり、bounded verification target の解決、runtime evidence の取得、Problem の採否、因果境界内の remediation、risk review、candidate commit、Completion Gate、final verification を一つの lifecycle で所有する。
<!-- @/contract -->

<!-- @contract test-verify-baseline-parent-self-qa -->
その agent は repository Test QA baseline の parent responsibility（obligation、common oracle、validation plane、final adjudication）を baseline self-QA として履行する。この責務は独立した `impl-lead` 固有の Parent QA phase や parent / worker hierarchy、Implementation Unit を導入しない。
<!-- @/contract -->

<!-- @contract test-verify-local-model -->
direct owner は invocation 全体で exactly one の task-local Local Model を所有し、shared Verification Topology result、runtime evidence、任意に取得した RMO result を同じ Model へ reintegrate する。new evidence によって authority、Expected Observation、causal attribution が material に変わる場合だけ affected semantic region を再構成し、stale result を置換する。
<!-- @/contract -->

<!-- @contract test-verify-consumer-boundary -->
`test-report` や `impl-lead` を nested invocation しない。Implementer delegation、Parent QA、Implementation Unit Design をこの Skill の責務へ導入しない。
<!-- @/contract -->

入力は request、repository / source / config、authoritative Context、test scope、runner / command / environment、write / commit authority である。最初に対象 test membership、対応し得る Behavior と provenance / precedence、execution surface、変更可能範囲を解決する。対象 test は discovery signal、Case、Evidence にはできるが、自身と照合する Behavior または Expected Observation の authority / grounding にはしない。

<!-- @contract test-verify-invocation-identity -->
invocation の開始時に bounded verification target、対象 membership、authority boundary を invocation identity として固定する。current state または authority の material drift が remediation direction や scope を変え得る場合は、guess や stale identity のままの継続をせず qualified incomplete とする。
<!-- @/contract -->

生成された Skill から参照する正本は、各 platform の generated path を基準に解決する。

- `../../references/verification-topology.md`
- `../../references/reality-model-observation.md`
- `../../references/external-effects.md`
- `references/risk-review.md`
- `references/completion-gate.md`

## Verification Topology mapping

<!-- @contract test-verify-topology-method -->
解決した bounded scope、Behavior / authoritative Context candidate と provenance、Case / Evidence / config facts、membership / completeness basis、source location、authority boundary を consumer input として唯一の semantic witness である shared `Verification Topology` Method に渡す。
<!-- @/contract -->

Method が返す grounded Expected Observation、many-to-many relation、execution state、grounding / correspondence / completeness limits を保持する。Behavior または authority の material gap が remediation direction を変え得る場合は推測で補わず qualified incomplete とする。

## Baseline and runtime evidence

<!-- @contract test-verify-baseline-identity -->
remediation または temporary mutation の前に repository identity、commit、tree / dirty-state ownership、runner / command / environment、対象 membership を baseline identity として固定し、初回結果と既知 failure を `pre-existing unrelated`、`target-causal candidate`、`indeterminate` の disposition にする。
<!-- @/contract -->

targeted test execution は外部 Action である。固定した command と environment で実行し、対象 Case / Evidence が実際に実行されたか、Expected Observation を区別できる runtime evidence が得られたかを観測する。直接影響または repository-native gate が要求する場合だけ execution scope を広げる。

<!-- @contract test-verify-runtime-attribution -->
concrete な不安定性 signal がある場合だけ同一条件で bounded rerun し、stabilization evidence を得る。execution identity の drift、結果の不安定、causal attribution の未確定のいずれかが target judgment を阻む場合は qualified incomplete とする。target chain と因果的に独立と判断できる観測だけを incidental finding として扱う。
<!-- @/contract -->

<!-- @contract test-verify-problem-classification -->
Topology、固定した baseline disposition、stabilized runtime evidence を照合し、missing verification、ineffective verification、required condition の欠落、statically / runtime non-executed、flaky / indeterminate evidence、test-side defect、correctly grounded test が露出した implementation discrepancy を区別する。
<!-- @/contract -->

必要な場合は shared Reality Model Observation を discrepancy、attribution、Target Membership の観測に使えるが、evidence acquisition、Problem adoption、remediation decision は `test-verify` が保持する。採用後も同じ baseline identity / disposition を remediation、再実行、review、final verification まで維持し、新しい unrelated failure を obligation に昇格させない。

## Temporary mutation

<!-- @contract test-verify-temporary-mutation -->
temporary mutation は、Expected Observation 違反を対象 verification が検出できるか確認する必要がある場合だけ任意に一度使える。実行前に exact target、pre-mutation byte / diff identity、dirty-state ownership、restore procedure、restore verification を固定し、task-owned かつ安全に完全復元できる範囲に限定する。

runner failure、結果不明、authority drift、qualified incomplete を含むすべての exit で、remediation、review、outcome projection より前に finally 相当の restoration を行い、pre-mutation byte / diff identity と mutation-only artifact の不在を検証する。restore result が不明なら後続の write / commit を禁止し、retained state evidence を伴う qualified incomplete とする。

mutation と mutation-only test / fixture / helper / config / dependency は deliverable に含めず、candidate commit tree でも不在を確認する。mutation result が不安定なら同一条件の bounded rerun で観測し、stable evidence が得られない場合は verification success や implementation discrepancy を結論しない。
<!-- @/contract -->

## Problem adoption and remediation

<!-- @contract test-verify-causal-remediation -->
grounded Expected Observation と stabilized runtime evidence から Derived Problem が target verification に因果的に属すると採用できる場合だけ、repository conventions に従い direct owner が Red → Green → Refactor で直接 remediation する。
<!-- @/contract -->

test-side と production-side の修正方向は test を通しやすい側ではなく、独立 grounding した Expected Observation と causal attribution から判断する。metrics、別 test failure、別機能 defect、lint、dead code、refactor opportunity は現在の chain に因果的に属さない限り incidental finding とし、変更しない。

<!-- @contract test-verify-pass-boundary -->
remediation 後は targeted runtime verification と必要な repository-native gate を再実行する。PASS だけを完了根拠にせず、元の Problem が解消され、Evidence が Expected Observation を意味的に区別することを確認する。
<!-- @/contract -->

## External effects, review, and completion

<!-- @contract test-verify-external-effects -->
filesystem mutation、test runner、Git commit その他の external Action は、Action field と control の唯一の正本である shared `External Effects` boundary に従う。この lifecycle の baseline / causal / risk disposition と temporary / output artifact の retention / cleanup state を consumer-specific disposition として渡す。
<!-- @/contract -->

<!-- @contract test-verify-destructive-effect -->
destructive または irreversible な test effect は isolated かつ non-production の exact target を default precondition とする。成立しない場合は principal、exact target、operation を示す effect 単位の Human explicit confirmation を blocking precondition とし、effect identity または target が不明なら qualified incomplete とする。
<!-- @/contract -->

Green 後、direct owner が obligation / common oracle / validation plane / applicable mutation evidence を含む baseline self-QA を行う。acceptance、remediation direction、external Action safety を変え得る concrete risk がある場合だけ `references/risk-review.md` を適用する。

<!-- @contract test-verify-completion-sequence -->
target-causal scope の exact change だけを candidate commit にし、必須の `references/completion-gate.md` を通過させた後、その gate-complete commit に repository-native final verification を実行する。
<!-- @/contract -->

candidate commit、amend、final verification も external Action として authority と結果 identity を独立確認する。final verification failure が同じ bounded causal repair として閉じない場合は complete にしない。

<!-- @contract test-verify-flow-incomplete-projection -->
risk review と Completion Gate の local Flow が返す `stop-incomplete` は invocation 外向きには `qualified incomplete` へ投影し、別の terminal state は作らない。
<!-- @/contract -->

<!-- @contract test-verify-post-final-state -->
final verification 後かつ complete の前に、gate-complete commit、HEAD、index、working tree、temporary / output artifact、retention / cleanup state を独立再観測して safe post-state を確認する。state が unknown または unexpected dirty なら complete にしない。
<!-- @/contract -->

## Outcomes

完了時は bounded target、grounded Expected Observation、baseline identity / disposition、Derived Problem と causal basis、変更、runtime / gate / final evidence、candidate commit identity、incidental finding を返す。

<!-- @contract test-verify-incomplete -->
runtime evidence が不足する、authority / scope が material に未解決である、必須 Action が未実行または結果不明である、または required remediation が bounded test-driven repair を超える場合は、別 implementation workflow へ自動遷移せず、成立済み evidence と未解決事項を伴う qualified incomplete を返す。
<!-- @/contract -->
