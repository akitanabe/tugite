<!-- Generated from shared/. Do not edit directly. -->

# Execution Safety

filesystem mutation、test runner、Git commit その他の external Action は、Action field と control の唯一の正本である shared `External Effects` boundary に従う。この lifecycle の baseline / causal / risk disposition と temporary / output artifact の retention / cleanup state を consumer-specific disposition として渡す。

destructive または irreversible な test effect は isolated かつ non-production の exact target を default precondition とする。成立しない場合は principal、exact target、operation を示す effect 単位の Human explicit confirmation を blocking precondition とし、effect identity または target が不明なら qualified incomplete とする。


## Temporary mutation

temporary mutation は、Expected Observation 違反を対象 verification が検出できるか確認する必要がある場合だけ、識別 evidence を得るために bounded に使える。実行前に exact target、pre-mutation byte / diff identity、dirty-state ownership、restore procedure、restore verification を固定し、task-owned かつ安全に完全復元できる範囲に限定する。

runner failure、結果不明、authority drift、qualified incomplete を含むすべての exit で、remediation、review、outcome projection より前に finally 相当の restoration を行い、pre-mutation byte / diff identity と mutation-only artifact の不在を検証する。restore result が不明なら後続の write / commit を禁止し、retained state evidence を伴う qualified incomplete とする。

mutation と mutation-only test / fixture / helper / config / dependency は deliverable に含めず、candidate snapshot（commit 済みならその tree）でも不在を確認する。mutation result が不安定なら同一条件の bounded rerun で観測し、stable evidence が得られない場合は verification success や implementation discrepancy を結論しない。
