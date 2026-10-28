# Execution Orchestration

## Identity and responsibility boundary

この reference は確定済み Implementation Unit の dispatch、implementation context、monitoring を所有する。Unit の再設計、acceptance、review finding の裁定は親に残す。

## Dispatch readiness

<!-- @contract impl-lead-dispatch-integrity -->
親は dependency が accepted または外部 precondition が満たされ、Unit の8 field、selected isolation、明示した Writable Scope assignment と target membership、verification environment が実行可能であることを確認する。dispatch 直前に current HEAD が expected accepted baseline と一致し、明示的に許可した既存 state 以外の tracked change がないことを確認する。expected accepted baseline は最初の Unit では固定した run base、後続 Unit では直前の accepted commit とする。不足、不一致、または material repository / execution drift が結果を変える場合は dispatch せず `stop-incomplete` とする。
<!-- @/contract -->

準備済み委譲文書の route / tier / handoff を利用する。担当や環境が利用できない場合は相違を示し、黙って別の分担へ置き換えない。

最初の実装は fresh context に渡す。同じ Implementer に clarification または現在の Unit 内 correction を続けさせる場合だけ continuation を使い、別 Unit、別責務、失効した前提、independent observation には fresh context を使う。
<!-- @only codex -->

fresh Implementer を起動する場合は `fork_turns = "none"` を指定する。
<!-- @/only -->

handoff は Unit Data、base、必要な surrounding context、検証方法と、`../../../references/writable-scope.md` の Writable Scope Method に従って親が確定した assignment / target membership を含む。Implementer に assignment の推測や暗黙拡張をさせない。追加 region が Unit scope 内なら親が explicit assignment update と target membership を確定して再 handoff し、Unit scope の拡張を要するなら update せず `stop-incomplete` とする。

Implementer は Red → Green → Refactor で外部から観測可能な振る舞いを実装し、正常、境界、異常、failure path、side effect の order / retry / partial failure / idempotency を applicable な範囲で検証する。meaningful Red が成立しない変更では failing test を捏造せず、pre-change evidence、理由、alternative verification を返す。commit は `impl-lead` 親が所有し、Implementer は commit しない。

## Monitoring

<!-- @contract impl-lead-monitoring -->
Human が明示した monitoring / intervention criteria は15分の既定より優先する。既定の elapsed time は最後の meaningful progress、output、state change を起点にする。そこから15分未満は status inquiry を行わず、15分経過は inquiry を許すだけで abnormality や mandatory poll を意味しない。elapsed time だけでは interrupt しない。tool failure、明示された block、contradictory evidence、user interruptionなど concrete signal がある場合だけ必要な介入を判断する。
<!-- @/contract -->

返却された diff と evidence は worker report を真と仮定せず、親が repository state から再観測して Parent QA へ渡す。
