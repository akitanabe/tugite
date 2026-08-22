<!-- Generated from shared/. Do not edit directly. -->

# plan-interactive structural-gate v1

この reference は `plan-interactive` の structural gate phase が所有する caller context、独立した gate budget、
`structural-gate-reopen-routing` Flow を定義する。gate evidence と candidate 採否の親 ownership という意味の正本は
root `SKILL.md` である。

## structural-health-gate

producer `complete` かつ freeze-integrity `intact` の current verified candidate だけを、同じ親 context の internal
`structural-health-gate` へ渡す。direction freeze や `clarify-it: Completed` を gate へ直接送らない。input には generic
`caller_context` Data（`workflow_family: plan-family`、`invocation: explicit-public-parent`）を含める。`context 不成立` は別 route へ切り替えず `stop-incomplete` とする。

親は gate 予算を独立した `rounds` Data として管理し、assessment 1回を1 round と数える。`rounds.limit` は下限1の
ceiling とし、ユーザー指定を優先する。未指定なら親が loop 開始時に固定し、1未満は補正せず `stop-incomplete` とする。
1未満では assessment、producer の再実行、後段を起動しない。gate 予算と review 予算は別 Data とする。
gate assessment / evidence、current round、fixed context を初期 Data として `structural-gate-reopen-routing` Flow に渡す。
Human response、affected decision / dependency closure、new freeze は return 後の intermediate Data とし、
gate finding の意味、Human response、candidate の採否は親が裁定する。

## Programmatic Flows

### structural-gate-reopen-routing

Trigger: structural-health-gate が current candidate に対する `return`、`pass`、または `insufficient-evidence` を親へ返したとき。
Inputs: initial Action 実行前 Data として、gate result / evidence の problem / impact / recommendation、独立した `rounds.limit`、current round、fixed parent context、current verified candidate、同じ immutable `authority_constraints`。Human response、affected closure、new freeze、producer result、integrity result は含めない。
Procedure: `pass` は review dispatch へ送る。`return` かつ current round が limit 未満の場合だけ finding を Agentic 親へ返す。親が constraints 内の具体化で閉じると裁定した場合は、current verified candidate と同じ constraints で producer を retry し、`complete` 後に fresh integrity check を行う。constraint 変更が必要なら local `clarify-it → new freeze → constrained producer` へ戻し、complete 後に fresh integrity を行う。各 result / evidence は中間 Data として親へ戻し、親裁定 Data を再投入してから次へ進む。前 cycle の freeze / constraints / review opt-out を次 cycle の既定として継承しない。limit 到達、`insufficient-evidence`、closure failure、または evidence 不足は `incomplete` とし、別 identity を作らない。old integrity evidence を再利用しない。
Outcomes: review dispatch、budget 内 producer retry または new-freeze recovery、または `incomplete`。gate finding の意味、Human response、constraint 変更要否、candidate の採否は親入力・親裁定であり Flow は expected oracle を固定しない。
