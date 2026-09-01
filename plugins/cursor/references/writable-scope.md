<!-- Generated from shared/. Do not edit directly. -->

# Writable Scope Method

Writable Scope は、caller が current execution に明示する filesystem write boundary を Implementer へ渡す shared Method です。
assignment の確定と target membership の確認は caller / execution orchestration が所有します。

```text
assignment_owner = caller / execution orchestration
write_eligibility = valid assignment + caller-confirmed target membership
missing_invalid_or_unknown = no-write + return to caller
unassigned_or_additional_target = no-write + return to caller
scope_update = valid explicit assignment update + caller-confirmed target membership
data_lifetime = transient execution Data
```

## Assignment と write eligibility

caller は write-capable handoff より前に writable region を明示し、assignment が current execution で有効であることと、各 target が
assigned region に属することを確定します。Implementer が write Action を開始できるのは、valid な assignment と caller による target
membership confirmation の両方がある場合だけです。

assignment が missing、invalid、unknown の場合、または target が assigned region に属さない場合、Implementer は write Action を開始せず、
不足または追加が必要な region を caller へ返します。repository、worktree、path の見た目から assignment、ownership、membership を推測せず、
assigned boundary を暗黙に拡張しません。

追加 region が必要な場合、caller が明示的に assignment を更新します。update の存在だけでは write eligibility は成立しません。更新後の
assignment が valid で、caller が target membership を確定した後だけ、その target を write eligible として扱います。更新後も invalid または
unknown なら no-write のまま caller へ返します。

## Responsibility boundary

Writable Scope は Implementation Unit の identity や semantic specification ではなく、current execution に限定した transient Data です。
この Method は worktree / workspace layout、isolation strategy、filesystem path resolution、platform enforcement、worker selection、execution order / parallelism、
audit log、persistent record を所有しません。それらを確定する caller が、assignment と membership をこの Method の boundary に沿って handoff します。
