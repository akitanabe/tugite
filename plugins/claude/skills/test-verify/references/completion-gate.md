<!-- Generated from shared/. Do not edit directly. -->

# Completion Gate

## Identity

Completion Gate は Green と必要な risk review を通過した candidate commit を final verification 前に閉じる mandatory consumer-specific gate である。`writing-principles-reviewer` は read-only / report-only であり、finding の採否、correction、completion を所有しない。

## Programmatic Flow

### test-verify-completion-control

Trigger: remediation と applicable verification が Green で、target-causal scope の candidate commit が存在する。

Inputs: verified baseline identity、candidate commit / immutable diff、bounded target、Acceptance Criteria、grounded Expected Observation、Derived Problem、causal membership、runtime / mutation / risk-review evidence、repository state。

Procedure:

1. candidate commit が verified baseline から target-causal scope の最終変更だけを含み、temporary mutation と mutation-only artifact を含まず、HEAD が candidate commit と一致し、index と working tree が clean であることを確認する。
2. fresh `writing-principles-reviewer` を一度起動し、code の How、test の What、commit の Why、comment / DocBlock の Why Not、public documentation / caller-facing contract accuracy に対する writing-only finding Data を回収する。
3. finding がなければ candidate commit を `gate-complete` とする。
4. finding があれば `owner-adjudication-required` として direct owner へ返し、Flow 内では採否や correction を決めない。

Outcomes: `gate-complete`、`owner-adjudication-required`、または candidate integrity / reviewer result の不足を伴う `stop-incomplete`。

Completion Gate の writing-only reviewer 観点は public documentation / caller-facing contract accuracy に対する writing-only finding Data を含む。


## Owner adjudication and bounded correction

direct owner は finding を `adopted`、`rejected`、`unresolved` に裁定する。finding がないか全 finding が rejected なら candidate commit を変更せず gate-complete とする。unresolved が残る場合は complete にしない。

adopted finding は observable Behavior、bounded target、causal attribution、public contract を変えず writing-only に局所化できる場合だけ direct owner が修正する。修正後に affected verification を再実行して同じ candidate commit を amend し、reviewed snapshot との差が adopted correction だけであること、HEAD / index / working tree、temporary artifact の不在を再確認する。確認できた場合だけ writing review を反復せず gate-complete とする。

observable Behavior、scope、causal attributionを変え得る finding は gate 内で修正せず qualified incomplete に戻す。gate 内で risk review や一般 implementation review を反復しない。gate-complete commit に対する repository-native final verification は caller lifecycle が所有する。
