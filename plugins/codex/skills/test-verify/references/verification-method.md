<!-- Generated from shared/. Do not edit directly. -->

# Verification and Causal Repair

## Verification Topology mapping

解決した bounded scope、Behavior / authoritative Context candidate と provenance、Case / Evidence / config facts、membership / completeness basis、source location、authority boundary を consumer input として唯一の semantic witness である shared `Verification Topology` Method に渡す。

Method が返す grounded Expected Observation、many-to-many relation、execution state、grounding / correspondence / completeness limits を保持する。Behavior または authority の material gap が remediation direction を変え得る場合は推測で補わず qualified incomplete とする。

要求から構成した Behavior candidate とその grounding / 未解決を Topology input として渡し、要求探索や対象範囲の解決を Topology / BMO に移さない。

Topology が返す BMO の Collective Sufficiency は、渡された Behavior の Expected Observation Model の導出十分性として保持する。要求範囲から Behavior candidate を構成できたことや、要求全体を検証できたことの判定へ読み替えない。

## Bidirectional reconciliation

Topology が返した各 Expected Observation を取得した Case / Evidence と照合し、同時に bounded scope で取得した各 Case / Evidence を要求から導出した Behavior / Expected Observation へ逆照合する。missing condition、成立・違反を区別できない Evidence、要求にない制約や誤った期待、correspondence / grounding / execution / observed-scope の限界を区別して Local Model に保持する。

照合結果と未読 membership の限界は Topology result のまま Local Model に保持し、対応不明や観測 scope 外を不在へ変換しない。

## Baseline and runtime evidence

remediation または temporary mutation の前に repository identity、commit、tree / dirty-state ownership、runner / command / environment、対象 membership を baseline identity として固定し、初回結果と既知 failure を `pre-existing unrelated`、`target-causal candidate`、`indeterminate` の disposition にする。

targeted test execution は外部 Action である。固定した command と environment で実行し、対象 Case / Evidence が実際に実行されたか、Expected Observation を区別できる runtime evidence が得られたかを観測する。直接影響または repository-native gate が要求する場合だけ execution scope を広げる。

concrete な不安定性 signal がある場合だけ同一条件で bounded rerun し、stabilization evidence を得る。execution identity の drift、結果の不安定、causal attribution の未確定のいずれかが target judgment を阻む場合は qualified incomplete とする。target chain と因果的に独立と判断できる観測だけを incidental finding として扱う。

Topology、固定した baseline disposition、stabilized runtime evidence を照合し、missing verification、ineffective verification、required condition の欠落、statically / runtime non-executed、flaky / indeterminate evidence、test-side defect、correctly grounded test が露出した implementation discrepancy を区別する。

必要な場合は shared Reality Model Observation を discrepancy、attribution、Target Membership の観測に使えるが、evidence acquisition、Problem adoption、remediation decision は `test-verify` が保持する。採用後も同じ baseline identity / disposition を remediation、再実行、review、final verification まで維持し、新しい unrelated failure を obligation に昇格させない。

## Problem adoption and remediation

grounded Expected Observation と stabilized runtime evidence から Derived Problem が target verification に因果的に属すると採用できる場合だけ、repository conventions に従い direct owner が Red → Green → Refactor で直接 remediation する。

test-side と production-side の修正方向は test を通しやすい側ではなく、独立 grounding した Expected Observation と causal attribution から判断する。期待値や assertion を弱めて PASS にせず、要求変更や大きな設計変更が必要なら未解決として返す。metrics、別 test failure、別機能 defect、lint、dead code、refactor opportunity は現在の chain に因果的に属さない限り incidental finding とし、変更しない。

remediation 後は targeted runtime verification と必要な repository-native gate を再実行する。PASS だけを完了根拠にせず、元の Problem が解消され、Evidence が Expected Observation を意味的に区別することを確認する。

remediation の有無にかかわらず、完了判断では bounded target の要求から導出した Expected Observation 全体と最終 Evidence に `Bidirectional reconciliation` の照合を適用する。全件 PASS や一部 Problem の解消だけで完了にせず、完了に影響する要求、grounding、correspondence、derivation、observation scope の不足が残る場合は qualified incomplete とする。非 material な限界も結果に保持する。
