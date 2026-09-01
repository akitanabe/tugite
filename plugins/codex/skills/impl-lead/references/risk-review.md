<!-- Generated from shared/. Do not edit directly. -->

# Risk-directed Review

## Selection and snapshot

specialized review は concrete risk が Unit acceptance、external Action の可否、correction direction を変え得る場合だけ起動する。generic checklist や reviewer inventory を理由に全 reviewer を起動しない。`writing-principles-reviewer` はこの risk review に含めない。

責務境界、security / external side effect、static performance / resource、changed test quality、change が導入した過剰実装の各 risk に応じて `responsibility-boundary-reviewer`、`security-side-effect-reviewer`、`static-performance-reviewer`、`test-quality-reviewer`、`over-engineering-reviewer` を選ぶ。reviewer には Task Spec、base、AC、同一の immutable diff / evidence identity、surrounding context、Parent QA baseline と起動理由を渡し、fresh / context-isolated session で観測させる。

fresh specialized reviewer を起動する場合は `fork_turns = "none"` を指定する。

同一 snapshot に対して選んだ reviewer の全結果を回収してから親が裁定する。batch 中は immutable read-only target に writer を入れず、全 result の回収と裁定後にだけ adopted finding の mutation を開始する。reviewer の Pass、finding 数、固定 round は accept / completion basis にしない。

## Adjudication and correction

親は各 finding を evidence、AC、scope、risk、rollback、verifiability、maintainability により `adopted`、`rejected`、`unresolved` へ裁定する。external Action の実行可否を変える unresolved risk は Action 前の blocking precondition とする。

adopted finding は元 Implementer または boundary と correction に適した fresh Implementer へ渡し、変更後に Parent QA と applicable verification を再実行する。diff が変わった場合、影響を受ける review goal だけを fresh reviewer に再 review させ、影響しない goal を反復しない。

unresolved finding は concrete risk と acceptance を変える expected evidence が残る間だけ追加観測または correction を選べる。input authority 内で閉じない、同じ evidence で進展しない、または要求成果を成立させるために input authority 外の material work を要する場合は `stop-incomplete` とする。要求成果と独立した input authority 外の finding は obligation に昇格させず final report に残す。
