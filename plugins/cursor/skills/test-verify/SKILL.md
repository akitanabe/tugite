---
name: test-verify
description: >-
  report の選択指摘または直接指定した bounded target を検証し、許可された因果範囲の修復・受入・最終検証まで閉じる。
disable-model-invocation: true
---
<!-- Generated from shared/. Do not edit directly. -->

# test-verify

## Identity and authority

`test-verify` は Human が明示した場合だけ開始する public Skill である。自然言語の test request だけから暗黙に起動せず、別 workflow から自動遷移しない。

top-level で `test-verify` を実行する agent が direct owner であり、bounded verification target の解決、runtime evidence の取得、Problem の採否、因果境界内の remediation、risk review、changed-test acceptance、applicable Completion Gate、final verification を一つの lifecycle で所有する。

その agent は repository Test QA baseline の owner responsibility（obligation、common oracle、validation plane、final adjudication）を baseline self-QA として履行する。この責務は独立した `impl-lead` 固有の Parent QA phase や parent / worker hierarchy、Implementation Unit を導入しない。

direct owner は invocation 全体で exactly one の task-local Local Model を所有し、shared Verification Topology result、runtime evidence、任意に取得した RMO result を同じ Model へ reintegrate する。new evidence によって authority、Expected Observation、causal attribution が material に変わる場合だけ affected semantic region を再構成し、stale result を置換する。

`test-report` や `impl-lead` を nested invocation しない。Implementer delegation、Parent QA、Implementation Unit Design をこの Skill の責務へ導入しない。

入力は report 全体・選択した指摘、または直接指定した bounded target と request、repository / source / config、要求と authoritative Context、test scope、runner / command / environment、write / commit authority である。最初に対象 test membership、対応し得る Behavior と provenance / precedence、execution surface、変更可能範囲を解決する。対象 test は discovery signal、Case、Evidence にはできるが、自身と照合する Behavior または Expected Observation の authority / grounding にはしない。

bounded target に適用される要求・Context、その provenance、適用範囲、未解決点を取得し、その意味から Behavior candidate を構成する。candidate 集合を既存 test に現れる Behavior へ縮約せず、candidate 探索では test を discovery signal とし、要求・Context に独立して grounding できない candidate を採用しない。

要求の意味範囲と対象 test membership を同じものと扱わず、scope 内の候補構成根拠と未解決の要求を task-local Local Model に保持する。関連要求の意味を調べても実行・修正範囲を拡張しない。

invocation の開始時に bounded verification target、対象 membership、authority boundary を invocation identity として固定する。current state または authority の material drift が remediation direction や scope を変え得る場合は、guess や stale identity のままの継続をせず qualified incomplete とする。

生成された Skill から参照する正本は、各 platform の generated path を基準に解決する。

- `../../references/verification-topology.md`
- `../../references/reality-model-observation.md`
- `../../references/external-effects.md`
- `references/verification-method.md`
- `references/execution-safety.md`
- `references/test-acceptance-gate.md`
- `references/risk-review.md`
- `references/completion-gate.md`

## Report handoff and current scope

report は任意の入口であり、事前実行を必要としない。report がある場合は repository / ref、観測 scope、要求根拠、Expected Observation、Case / Evidence 参照、選択した指摘 ID と確認状態を入力として受け取る。report の結論を採用済み Problem として扱わず、現在の repository / ref と根拠を再確認する。

選択した指摘の根拠と影響範囲を先に確認し、変化した箇所、不足、未確定事項を補う。再利用できる観測は provenance と現状一致を確認して利用し、毎回無条件に全探索しない。直接指定では同じ bounded scope の要求・test・source・config から必要な input を構成する。古い report の差分が material なら current evidence で affected region を再構成し、対象や権限の判断が必要なら Human に局所確認する。

report 全体を選んだ場合も実行・修正可能範囲を確認する。指摘の選択は scope の入力であり write / commit authority を付与しない。未選択の指摘は未選択のまま保持し、解決済みにしない。

## Verification and repair lifecycle

1. 対象・権限・現状を確定し、`references/verification-method.md` に従って要求側から candidate を構成し shared Verification Topology で grounding と対応を得る。
2. 同 reference の baseline identity を固定し、`references/execution-safety.md` に従って許可された runtime evidence を得る。静的診断、実行が必要な疑い、材料不足を runtime 実証と混同しない。
3. 双方向照合から問題成立と原因を判断する。問題不成立も根拠とともに残す。採用した Problem だけを許可された因果範囲で修復し、対象と影響範囲を再検証する。
4. direct owner が repository Test QA baseline の obligation、oracle、validation plane、applicable mutation evidence を確認し、必要な `references/risk-review.md` を適用する。
5. 下記の変更有無に応じた受入・完了経路へ進む。要求と最終 Evidence の双方向照合は両経路で必須である。

## Acceptance and completion

変更不要・問題不成立のときは baseline と最終 state の一致、bounded target の要求と最終 Evidence の双方向照合、applicable repository-native final verification を確認して complete にできる。変更レビュー、Test Acceptance Gate、Completion Gate、空コミットは要求しない。

変更があるときは target-causal scope の exact change を immutable candidate snapshot として固定し、`references/test-acceptance-gate.md` の applicability を判定する。test-accepted または not-applicable の snapshot を `references/completion-gate.md` へ渡し、gate-complete snapshot に repository-native final verification を実行する。

commit authority がある場合だけ candidate commit を作成・amend する。authority がない場合は base、exact diff / content identity、既存 dirty-state ownership を固定した uncommitted snapshot で gate と検証を行う。検証の成立と commit の実施を別々に報告し、commit しないことだけを verification failure にしない。依頼された必須 commit が未完了ならその action は pending と明記する。

final verification 後かつ complete の前に、検証対象 snapshot、HEAD、index、working tree、temporary / output artifact、retention / cleanup state を独立再観測して safe post-state を確認する。既存の無関係な dirty state は baseline ownership と比較して保存する。state が unknown または unexpected dirty なら complete にしない。

risk review、Test Acceptance Gate、Completion Gate の local Flow が返す `stop-incomplete` は invocation 外向きには `qualified incomplete` へ投影し、別の terminal state は作らない。

## Outcomes

選択した対象とその影響範囲について、要求根拠、Expected Observation ↔ Case / Evidence の双方向照合、baseline / final snapshot、実行結果と未実行事項、変更、gate evidence、commit 状態、限界を返す。元 report 全体の無条件な再出力や専用台帳は要求しない。

report 由来の指摘は同じ ID を保持して、修正・検証済み／問題不成立／未解決とその根拠を説明する。直接指定から得た Problem も同様に追跡可能にし、未選択・incidental finding と区別する。未読、skip、未実行、対応不明、証拠なしの区別を保持する。

runtime evidence が不足する、authority / scope が material に未解決である、必須 Action が未実行または結果不明である、または required remediation が bounded test-driven repair を超える場合は、別 implementation workflow へ自動遷移せず、成立済み evidence と未解決事項を伴う qualified incomplete を返す。
