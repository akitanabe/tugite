<!-- Generated from shared/. Do not edit directly. -->

# plan-interactive freeze-integrity v1

この reference は `plan-interactive` の freeze-integrity phase が所有する verifier handoff と
post-producer / post-review recovery routing の HOW を定義する。fresh integrity という不変条件の意味の正本は
root `SKILL.md` である。

## freeze-integrity

Human authority protection は一つの freeze-integrity procedure を正本とする。candidate-changing boundary の後に、latest candidate と
全 constraint ID / `frozen_meaning` / `source_evidence` を fresh に照合する。stale check や subset check を再利用しない。

trigger は次に固定する。

- 各 producer invocation が `complete` で返した latest S2 の後。初回、gate retry、new freeze 後の recovery を含む。
- `review-refine` の adopted revision を反映した latest snapshot の後。

final-acceptance local correction は、affected closure に対する local `clarify-it → verified new freeze → constrained producer complete` へ戻すため、
producer-complete trigger で保護する。

親は全 constraints の verifier verdict と evidence、最新 snapshot、candidate location、fixed bounds / invocation Data を初期入力として準備する。
`freeze-integrity-routing` Flow が deterministic routing の唯一の詳細 witness である。全 frozen meaning を保持した AC / verification /
local detail の追加は許可し、baseline 全文を変更禁止対象にしない。

## Programmatic Flows

### freeze-integrity-routing

Trigger: producer が `complete` で返した latest S2 の後、または `review-refine` の adopted revision を反映した latest snapshot の後に、親が fresh freeze-integrity を要求したとき。
Inputs: initial Action 実行前 Data として、全 constraint ID / `frozen_meaning` / `source_evidence`、latest candidate、trigger 種別（post-producer / post-review）、fixed bounds / invocation Data。stale check evidence と subset check は含めない。Human decision と recovery freeze は含めない。
Procedure: 全 constraints を latest candidate に対して fresh に独立照合する。stale check や subset check を再利用しない。`intact` は次の gate、review dispatch、または final acceptance へ進める。post-producer `violated` は constraint を変更せずには安全な candidate を作れない場合、`authority_conflict` として Human boundary へ返し、new freeze 後は producer から再開する。post-review `violated` は violating working snapshot を promote せず、last constraint-intact verified snapshot を維持し、影響 finding を `human-confirmation` へ再裁定する。Human が freeze を維持する場合は finding を再裁定し、安全な candidate に対する changed-scope review を経て final acceptance へ進む。Human が direction を変える場合は `Human decision → verified new freeze → constrained producer complete latest S2 → fresh integrity → gate → review dispatch → final acceptance` の順で再入する。`indeterminate` は Agent authority 内で evidence を取得できる場合だけ同じ candidate を fresh に再照合する。取得不能、closure 不成立、または fixed budget 到達では `incomplete` とする。violating snapshot を再開 baseline にしない。
Outcomes: `intact` の downstream routing、post-producer `authority_conflict`、post-review last-intact 維持と `human-confirmation`、または `incomplete`。Human recovery の内容、evidence の意味評価、finding の採否は親が裁定し expected oracle にしない。
