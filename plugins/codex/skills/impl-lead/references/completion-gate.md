<!-- Generated from shared/. Do not edit directly. -->

# Completion Gate

## Identity

Completion Gate は Parent QA と必要な risk review を通過した Unit を accepted commit に閉じる mandatory final-writing gate である。writing-level correction だけを扱い、risk review、Unit Design、一般 implementation review を反復しない。

候補 snapshot を1 commitにし、その commit を fresh / context-isolated な `writing-principles-reviewer` に一度だけ渡して、code の How、test の What、commit の Why、comment / DocBlock の Why Not を確認する。

fresh `writing-principles-reviewer` を起動する場合は `fork_turns = "none"` を指定する。

## Programmatic Flow

### unit-completion-control

Trigger: Parent QA と必要な risk review が Green で candidate commit が存在する。

Inputs: Unit Data、base、candidate commit / immutable diff、AC、verification evidence。

Procedure:

1. fresh `writing-principles-reviewer` を一度起動し、writing reviewer finding Data を result として回収する。
2. finding がなければ candidate commit を accepted baseline として閉じる。
3. writing-level に局所化された finding だけなら fresh `focused-implementer` に correction を渡す。
4. correction 後に Parent QA と applicable verification を行い、同じ Unit commit を amend する。
5. amend 後の commit を accepted baseline として閉じる。

Outcomes: immutable accepted Unit commit、または writing-level に閉じない material reason を伴う `stop-incomplete`。

correction は observable behavior、scope、Unit responsibility を変えない。変え得る finding は writing correction として処理せず authority boundary へ返す。gate 内で risk review、writing review、Unit Design に戻らない。
