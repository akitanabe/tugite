# Completion Gate

## Identity

Completion Gate は Parent QA と必要な risk review を通過した Unit を accepted commit に閉じる mandatory final-writing gate である。`writing-principles-reviewer` は read-only / report-only であり、finding の採否、correction、acceptance を所有しない。writing-level correction だけを扱い、risk review、Unit Design、一般 implementation review を反復しない。

<!-- @contract impl-lead-completion-gate -->
候補 snapshot を1 commitにし、その commit を fresh / context-isolated な `writing-principles-reviewer` に一度だけ渡して、code の How、test の What、commit の Why、comment / DocBlock の Why Not を確認する。
<!-- @only codex -->

fresh `writing-principles-reviewer` を起動する場合は `fork_turns = "none"` を指定する。
<!-- @/only -->

## Programmatic Flow

### unit-completion-control

Trigger: Parent QA と必要な risk review が Green で candidate commit が存在する。

Inputs: Unit Data、expected accepted baseline、candidate commit / immutable diff、AC、verification evidence、repository state。

Procedure:

1. candidate commit が expected accepted baseline から当該 Unit の全変更だけを含み、HEAD が candidate commit と一致し、index と working tree が clean であることを確認する。
2. fresh `writing-principles-reviewer` を一度起動し、writing reviewer finding Data を result として回収する。
3. finding がなければ candidate commit を `gate-complete` とする。
4. finding があれば finding Data を `parent-adjudication-required` として親へ返し、Flow 内では採否や correction を決めない。

Outcomes: `gate-complete`、`parent-adjudication-required`、または candidate integrity / reviewer result の不足を伴う `stop-incomplete`。

## Parent adjudication and bounded correction

親は各 finding を `adopted`、`rejected`、`unresolved` に裁定する。finding がないか全 finding が `rejected` なら、candidate commit を変更せず gate-complete とする。`unresolved` が残る場合は accepted baseline にせず `stop-incomplete` とする。

`adopted` finding は、observable behavior、scope、Unit responsibility、public contract を変えず writing-level に局所化できる場合だけ gate 内で修正する。`commit-message-only correction` は commit owner である親が行う。code、test、comment、DocBlock、document の correction は fresh `focused-implementer` に渡す。correction 後に親が Parent QA と applicable verification を再実行し、同じ Unit commit を amend する。

amend 後は reviewed snapshot と amended snapshot の before / after diff から adopted finding 対応以外の変更がないことを親が確認する。さらに HEAD が amended commit と一致し、index と working tree が clean であることを再確認する。局所性、非 semantic 性、verification、repository state を確認できる場合だけ、reviewed snapshot と accepted snapshot の差を same-run exception として明示し、writing review を反復せず amended commit を gate-complete とする。いずれかを確認できない場合は `stop-incomplete` とする。

correction は observable behavior、scope、Unit responsibility を変えない。変え得る finding は writing correction として処理せず authority boundary へ返す。gate 内で risk review、writing review、Unit Design に戻らない。
<!-- @/contract -->
