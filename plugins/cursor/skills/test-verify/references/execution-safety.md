<!-- Generated from shared/. Do not edit directly. -->

# Execution Safety

filesystem mutation、test runner、Git commit その他の external Action は、Action field と control の唯一の正本である shared `External Effects` boundary に従う。この lifecycle の baseline / causal / risk disposition と temporary / output artifact の retention / cleanup state を consumer-specific disposition として渡す。

destructive または irreversible な test effect は isolated かつ non-production の exact target を default precondition とする。成立しない場合は principal、exact target、operation を示す effect 単位の Human explicit confirmation を blocking precondition とし、effect identity または target が不明なら qualified incomplete とする。


## Temporary mutation

temporary mutation は、Expected Observation 違反を対象 verification が検出できるか、または独立した要求・契約に照らして正当な変種を誤拒否しないか確認する必要がある場合だけ、識別 evidence を得るために bounded に使える。実行前に exact target、pre-mutation byte / diff identity、dirty-state ownership、restore procedure、restore verification を固定し、task-owned かつ安全に完全復元できる範囲に限定する。

変更前に検証方向、具体的な変種と成立条件、要求・契約の provenance / 適用範囲、対象 assertion と予測される観測を固定する。正当変種は公開契約、互換性、非機能要求、authoritative Context に独立して照合し、対象 test や現実装だけで正当化しない。根拠が不明なら実証済みとせず、材料不足を保持する。

変更前の baseline と同じ runner / command / environment / membership で対象 assertion への到達と結果を記録する。違反が成功する場合も、正当変種が失敗する場合も、対象が実際に実行されたことと因果関係を確認する。対象 assertion による拒否と syntax / setup / runner / 環境 failure、別 test の failure を区別し、単なる失敗や skip を検出・誤拒否の実証にしない。

runner failure、結果不明、authority drift、qualified incomplete を含むすべての exit で、remediation、review、outcome projection より前に finally 相当の restoration を行い、pre-mutation byte / diff identity と mutation-only artifact の不在を検証する。restore result が不明なら後続の write / commit を禁止し、retained state evidence を伴う qualified incomplete とする。

mutation と mutation-only test / fixture / helper / config / dependency は deliverable に含めず、candidate snapshot（commit 済みならその tree）でも不在を確認する。mutation result が不安定なら同一条件の bounded rerun で観測し、stable evidence が得られない場合は verification success や implementation discrepancy を結論しない。
