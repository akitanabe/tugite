# Risk-directed Review

## Identity and baseline

<!-- @contract test-verify-risk-baseline -->
specialized review は、direct owner が baseline self-QA を完了した後、acceptance、remediation direction、external Action safety を変え得る concrete risk がある場合だけ行う。reviewer inventory や固定 checklist を起動理由にせず、`writing-principles-reviewer` はこの review に含めない。

baseline self-QA は Task Specification、base、Acceptance Criteria、immutable diff / evidence identity、surrounding context、grounded Expected Observation、Derived Problem、causal membership、runtime evidence、baseline failure disposition に対して obligation、common oracle、validation plane、applicable mutation evidence を direct owner が確認する。reviewer の Pass は acceptance basis にならず、reviewer は oracle、finding adoption、correction、completion を所有しない。
<!-- @/contract -->

責務境界、security / external side effect、static performance / resource、changed test quality、過剰実装の concrete risk に応じて、direct owner は `responsibility-boundary-reviewer`、`security-side-effect-reviewer`、`static-performance-reviewer`、`test-quality-reviewer`、`over-engineering-reviewer` から必要最小限を選ぶ。この risk materiality と reviewer selection は autonomous judgment であり、Programmatic Flow の expected-output oracle にしない。

## Programmatic Flow

<!-- @contract test-verify-risk-review-flow -->
### risk-review-control

Trigger: baseline self-QA 完了後に、direct owner が concrete risk と reviewer selection を確定した。

Inputs: Task Specification、base、Acceptance Criteria、immutable diff / evidence identity、surrounding context、grounded Expected Observation、Derived Problem、causal membership、runtime evidence、baseline failure disposition、baseline self-QA、起動理由、選択済み reviewer。

Procedure:

1. required input、同一 snapshot identity、baseline self-QA、起動理由が揃っていることを確認する。
2. 選択済み reviewer に同じ packet を渡し、immutable read-only snapshot を観測させる。
3. 選択した全 reviewer の result を回収する。
4. result を finding Data として direct owner へ返し、Flow 内では finding の採否、correction direction、acceptance を決めない。

Outcomes: review finding Data、または input / snapshot / reviewer result の不足を伴う `stop-incomplete`。
<!-- @/contract -->

<!-- @only codex -->
fresh specialized reviewer を起動する場合は `fork_turns = "none"` を指定する。
<!-- @/only -->

## Adjudication and correction

direct owner は各 finding を evidence、Expected Observation、causal attribution、AC、authority、risk、rollback、verifiability、maintainability により `adopted`、`rejected`、`unresolved` へ裁定する。adopted finding は causal scope 内で直接修正し、affected Behavior / Case の runtime verification と applicable verification を再実行する。

external Action の可否を変える unresolved risk は Action 前の blocking precondition とする。authority 内で閉じない、同じ evidence で進展しない、または bounded test-driven repair を超える場合は qualified incomplete とする。target chain と独立した finding は obligation にせず incidental finding として保持する。
