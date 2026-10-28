# Risk-directed Review

## Selection and snapshot

`../../../references/implementation-review.md` を読み、specialist selection、共通 input packet、fresh / context-isolated な read-only observation、finding handling を適用する。
<!-- @only codex -->
fresh specialized reviewer を起動する場合は `fork_turns = "none"` を指定する。
<!-- @/only -->

親は選んだ全 reviewer の結果を回収して裁定した後にだけ adopted finding の mutation を開始する。
changed test artifact の通常の coverage / validity acceptance は `test-acceptance-gate.md` が所有し、specialist review で代替しない。

## Adjudication and correction

親は各 finding を 共有 reference の finding handling により `adopted`、`rejected`、`unresolved` へ裁定する。external Action の実行可否を変える unresolved risk は Action 前の blocking precondition とする。

adopted finding は元 Implementer または boundary と correction に適した fresh Implementer へ渡し、変更後に Parent QA と applicable verification を再実行する。diff が変わった場合、影響を受ける review goal だけを fresh reviewer に再 review させ、影響しない goal を反復しない。

unresolved finding は concrete risk と acceptance を変える expected evidence が残る間だけ追加観測または correction を選べる。input authority 内で閉じない、同じ evidence で進展しない、または要求成果を成立させるために input authority 外の material work を要する場合は `stop-incomplete` とする。要求成果と独立した input authority 外の finding は obligation に昇格させず final report に残す。
