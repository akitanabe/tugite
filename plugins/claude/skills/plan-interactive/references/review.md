<!-- Generated from shared/. Do not edit directly. -->

# plan-interactive review v1

この reference は `plan-interactive` の review phase が所有する applicability → opt-out → readiness の判定、
`review-refine` への handoff、`review-dispatch` Flow、re-entry の HOW を定義する。`review-refine` は applicable かつ
no opt-out かつ ready のときだけ load / execute する。applicability / opt-out / artifact status の親 ownership という
意味の正本は root `SKILL.md` である。

## review の適用と dispatch

工程順序は `clarify-it → direction freeze projection → mandatory constrained producer → freeze-integrity → structural-health-gate → review dispatch` であり、gate が `pass` した snapshot だけを
次の判定へ渡す。review applicability / opt-out / readiness は public parent dispatch が `plan-agent` と同じ意味で所有する。
`review-refine` は dispatch 後の loop / termination を所有し、artifact status は caller が別に裁定する。
親は `artifact_kind` と既定 `plan-adversarial-reviewer` の責務から reviewer applicability を判定し、
確認済み applicability、明示 opt-out、review goal、reviewer data、Acceptance Criteria / 設計 readiness とともに Action 実行前 Data として `review-dispatch` Flow へ渡す。
適用可否、Human の review opt-out、入力の意味と readiness は親が所有する。

`review-refine` には不変 snapshot、`artifact_kind`、`caller_context`、要求と判定基準、review goal、reviewer・回数制約、
必要なら継続台帳を渡す。回数制約がなければ親が loop 開始時に上限と打ち切りを決める。既定 reviewer は
`plan-adversarial-reviewer`、final trim は `over-engineering-reviewer` のプラン入力モードである。`review_goal` は、ユーザー指定の review goal や追加の具体的な risk がない場合、「実装前プランの具体的な failure path を確認し、確定候補にできるか判断する」とする。これは plan review 自体の既定目的であり、毎回 risk を事前発見することを要求しない。ユーザー指定 goal や追加 risk は既存 reviewer の責務内で追加できる。入力前提不足は
補って再投入するかレビュー不成立として返す。

## review 結果と direction freeze の保護

親は成果物、finding / hold ledger、未解決 finding、final trim、`termination`、`adversarial_review_count` を受け取り、
finding を既存5区分へ evidence と理由付きで裁定する。frozen decision の変更、affected dependency closure、再 review scope は親の意味判断である。
`review-dispatch` Flow は applicability、opt-out、readiness、input failure の固定 routing だけを担い、finding の採否を決めない。
`termination` は review-refine がどのように終了したかを示す process Data であり、candidate status は caller が別に裁定する。

review は frozen decisions を守る限り具体化・verification 補強・複雑性削減を許す。採用修正後の latest snapshot は fresh integrity check を通してから
final acceptance 候補にする。frozen decision の変更が必要なら親が `人間確認` へ止める。

## Programmatic Flows

### review-dispatch

Trigger: 親が artifact snapshot と review readiness を確定し、review routing を要求したとき。
Inputs: 親確定の artifact_kind、applicability、user review opt-out、review goal、reviewer data、Acceptance Criteria / 設計 readiness、reviewer availability。
Procedure: parent-confirmed applicability は opt-out より先に評価する。nonapplicable は normal completion、applicable + opt-out は normal completion、applicable + no opt-out + ready は review dispatch とする。readiness failure または reviewer failure は review-not-established として親へ返す。
Outcomes: nonapplicable、opt-out、review dispatch、または明示的な `review-not-established`。Flow は accept を返さず、finding の意味的な採否と artifact status は親へ返す。
