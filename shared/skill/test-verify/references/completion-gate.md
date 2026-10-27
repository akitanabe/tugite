# Completion Gate

## Identity

Completion Gate は Green と必要な risk review、test-accepted / not-applicable を確認した変更ありの immutable candidate snapshot を final verification 前に閉じる mandatory consumer-specific gate である。`writing-principles-reviewer` は read-only / report-only であり、finding の採否、correction、completion を所有しない。

## Programmatic Flow

<!-- @contract test-verify-completion-flow -->
### test-verify-completion-control

Trigger: 変更ありの candidate snapshot に対する applicable verification と必要な review が完了し、Test Acceptance Gate が test-accepted または not-applicable である。

Inputs: verified baseline identity、candidate snapshot / exact diff、bounded target、Acceptance Criteria、grounded Expected Observation、Derived Problem、causal membership、runtime / mutation / risk-review / test-acceptance evidence、repository state。

Procedure:

1. candidate snapshot が verified baseline から target-causal scope の最終変更だけを含み、temporary mutation と mutation-only artifact を含まず、current content / diff と一致し、既存 dirty state が baseline ownership と一致することを確認する。commit 済みなら HEAD が candidate commit と一致することも確認する。
2. fresh `writing-principles-reviewer` を一度起動し、code の How、test の What、commit の Why、comment / DocBlock の Why Not、public documentation / caller-facing contract accuracy に対する writing-only finding Data を回収する。
3. finding がなければ candidate snapshot を `gate-complete` とする。
4. finding があれば `owner-adjudication-required` として direct owner へ返し、Flow 内では採否や correction を決めない。

Outcomes: `gate-complete`、`owner-adjudication-required`、または candidate integrity / reviewer result の不足を伴う `stop-incomplete`。
<!-- @/contract -->

<!-- @contract test-verify-completion-writing-scope -->
Completion Gate の writing-only reviewer 観点は public documentation / caller-facing contract accuracy に対する writing-only finding Data を含む。
<!-- @/contract -->

<!-- @only codex -->
fresh `writing-principles-reviewer` を起動する場合は `fork_turns = "none"` を指定する。
<!-- @/only -->

## Owner adjudication and bounded correction

direct owner は finding を `adopted`、`rejected`、`unresolved` に裁定する。finding がないか全 finding が rejected なら candidate snapshot を変更せず gate-complete とする。unresolved が残る場合は complete にしない。

adopted finding は observable Behavior、bounded target、causal attribution、public contract を変えず writing-only に局所化できる場合だけ direct owner が修正する。修正後に affected verification を再実行してcandidate snapshot を更新し（commit authority がある場合だけ amend し）、reviewed snapshot との差が adopted correction だけであること、HEAD / index / working tree、temporary artifact の不在を再確認する。test acceptance evidence が引き続き有効であることも確認できた場合だけ writing review を反復せず gate-complete とする。

observable Behavior、scope、causal attributionを変え得る finding は gate 内で修正せず qualified incomplete に戻す。gate 内で risk review や一般 implementation review を反復しない。test semantics に影響する correction は Test Acceptance Gate の affected review へ返す。gate-complete snapshot に対する repository-native final verification は caller lifecycle が所有する。

no-change は caller の final verification 経路で閉じ、この変更レビューを起動しない。uncommitted snapshot では commit の Why は not-applicable とし、commit 権限をこの gate のために要求しない。
