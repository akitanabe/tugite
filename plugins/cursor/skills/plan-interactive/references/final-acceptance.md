<!-- Generated from shared/. Do not edit directly. -->

# plan-interactive final-acceptance v1

この reference は `plan-interactive` の final acceptance phase が所有する report / acceptance Action、
local correction / large reformulation の routing、`final-acceptance-routing` Flow を定義する。Human final authority
という意味の正本は root `SKILL.md` である。

## review 完了と final acceptance

review 実行結果、`converged` / `induced-loop`、未解決 finding、レビュー不成立、`round-limit`、`stop-incomplete`、台帳、残存 risk は親が受け取り、
確定候補か未完了かを裁定する。代替 evidence による完了扱い、clarify-it への自動逆遷移、未完了 artifact 保存は行わない。
`nonapplicable` と `applicable + explicit opt-out` は normal completion として Human final acceptance へ進める。

final acceptance は direction freeze と分離し、既定で必須とする。Human の明示 opt-out は親が approval Action の省略として確定するが、report は残す。
Semantic Delta baseline、summary、方向変更、verification、risk、default required / pre-existing binding opt-out は `final-acceptance-routing` Flow の初期入力 Data とする。
Human response と correction classification は acceptance Action 後に親が裁定して再投入する intermediate Data とする。
Flow 外では Human acceptance、local / large / closure の分類、correction scope、意味評価を親が保持する。

final report は過去 cycle や advisor history を露出しない。

## Programmatic Flows

### final-acceptance-routing

Trigger: gate と review dispatch を通過した candidate、または review 非適用 / explicit opt-out の draft が final acceptance の親判定へ到達したとき。
Inputs: initial Action 実行前 Data として、final candidate、最新 direction freeze を Semantic Delta baseline とする Data、summary、direction change、verification result、remaining risk、default required、pre-existing binding explicit opt-out、acceptance invocation Data。Human Decision と correction classification result は含めない。
Procedure: direction freeze、gate pass、review 済み candidate を final acceptance と同一視せず、既定で acceptance Action と report を要求する。explicit opt-out は approval Action だけを省略し report を残す。それ以外は acceptance Action を一度実行し、Human response を中間 Data として Agentic 親へ返す。親が裁定した local / large / closure classification の再投入後だけ routing する。local correction は affected closure の local `clarify-it → verified new freeze → constrained producer complete` を順に routing し、complete 後の fresh integrity、gate、changed-scope review、再 acceptance を経る。各 autonomous result と親裁定 Data を中間 Data として parent round-trip する。large purpose / scope change は public workflow 全体を再策定し、closure failure は `incomplete` とする。non-intact な snapshot から final acceptance へ直行しない。
Outcomes: final acceptance、明示 opt-out 後の report、local correction loop、large reformulation、または closure failure の `incomplete`。local / large / closure の分類、Human acceptance、verification の意味評価、最終採否は親入力・親裁定であり Flow は expected oracle にしない。
