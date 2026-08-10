---
name: plan-craft
description: >-
  ユーザーが明示した場合だけ、Human が途中経過を追わず Agent に任せる「おまかせ」workflow として、
  recommendation-first の自由形式の計画・設計成果物を起草する。gate pass 後は review 適用対象を bounded に確認し、
  圧縮した結果と推奨候補を返す。public workflow parent が内部工程として `final-candidate` / `incomplete` と圧縮出力を裁定し、
  Human が最終成果物を採用して後続 Action を許可する。実装・委譲・次工程の自動前進は行わない。
---
<!-- Generated from shared/. Do not edit directly. -->

# plan-craft

この Skill は、依頼に応じた自由形式の計画・設計成果物を起草し、親へ確定候補を返す。成果物は設計判断書、
改修方針、移行計画、比較検討、作業メモ、リスク整理、実装単位の候補案などでよく、特定の実行 schema や
固定された後続工程の入力へ変換しない。規範本文はこの Skill 自身で完結し、別の実装 workflow の本文を前提にしない。

通常の `plan-craft` は、Human が途中経過を追わず Agent に任せる「おまかせ」workflow である。Agent が要求と
repository の evidence を調査し、推奨できる計画を理由付きでまとめ、Human には圧縮した結果だけを返す
recommendation-first を既定とする。Human の途中承認や逐次確認を既定の工程にしない。

推奨の判断は、要求原文・repository evidence・scope・constraints・verification・risk と、親から注入された共有判定基準を同じ
判定基準へ揃えて行う。十分な根拠があれば Agent が方針を選び、選んだ理由と棄却した代替案を残す。要求は解釈するが
書き換えない。ユーザー要求、明示制約、観測事実は覆さず、既存の Agent の判断、過去の plan、review の結論は
authority/freeze とせず、現在の evidence で再評価する。例外は、要求同士または要求と明示制約の不可約な意味衝突だけであり、
その場合だけ Human escalation として必要な一点を返す。`plan-craft-approval` の direction freeze / final acceptance は
この通常 workflow へ持ち込まず、その public workflow の境界を変更しない。

reviewer の `人間確認` は reviewer が観測した signal に留まり、採否・停止・推奨を決めない。public workflow parent が内部工程として `final-candidate` / `incomplete` と圧縮出力を裁定し、Human が最終成果物を採用して後続 Action を許可する。

### candidate status Calculation

candidate status は次の Calculation で一度だけ決める。
`incomplete` は、不可約な意味衝突、blocking evidence 不足、structural budget 等で安全継続不可、workflow/context 不成立、
現 candidate を推奨不能な状態、blocking finding、未反映修正必須、要求意味変更、または evidence不足のいずれかがある場合である。
`final-candidate` は上記の理由が一つもなく、現在の candidate を推奨できる場合である。単なる複数案、別案、軽い不確実性だけでは
`stop-incomplete` にせず、Agent が比較して一案を推奨し、残る不確実性を risk または Human Attention へ記録する。

## おまかせ workflow の review と推奨判定

review の `termination` は review-loop がどのように終了したかを示す process Data であり、`final-candidate` / `incomplete`
という計画の判定とは別軸である。criticism exhaustion、round-limit、残存 finding は process Data として保持し、candidate status は
上記 Calculation の結果を参照する。

review を続ける価値の判断が難しい場合だけ、read-only `plan-quality-advisor` を起動できる。毎 round 起動せず、advisor には request、repository_observation、review_goal、current snapshot、finding ledger、直近差分、verification、residual risk を Data として渡す。advisor は追加 round の期待利益、
残存 finding、churn/限界効用、不足 evidence を非拘束 insight として返す。advisor は candidate を修正せず、parent が
continue / stop-and-finalize / stop-incomplete を裁定する。

上記 Calculation で `final-candidate` となった場合、bounded stop 後の残存 finding は Accepted risk / Out of scope /
Human Attention のうち最終判断に影響するものだけを残す。解消済み、却下済み、軽微な文言、churn の履歴は Human 向け出力へ
残さない。

## おまかせ workflow の圧縮出力

`final-candidate` の既定出力は Result / Semantic Delta / Verification Delta / Human Attention / Artifact である。
Semantic Delta の baseline は最初に `structural-health-gate` へ投入した proposal candidate とし、その後の修正だけを示す。
Verification Delta は境界、failure path、fragile behavior、禁止副作用、責務境界を優先し、差分がなければ短縮する。

final summary は明示 opt-out できる。review skip と final summary skip は独立であり、一方を指定しても他方を暗黙に変更しない。
`final-candidate` の summary opt-out は Artifact だけを返す。ただし `incomplete` の summary opt-out では `Result: incomplete`、
Blocking Reason、Residual Risk を必ず返し、必要な場合だけ Human Decision Needed を示す。途中の decision / review 全履歴を Human に
要求しない。Artifact は通常会話内 Data とし、最終採用と保存・後続 Action の許可は Human が判断する。

`return target` は public workflow parent が所有する。現在の plan-craft は gate の assessment を受けて proposal へ
返すか後段へ進むかを親として判断し、明示されていない別 workflow へ自動 switch しない。

## 発火制御と責務

- ユーザーが `$plan-craft` または同等の明示要求をした場合だけ起動する。自然言語の作業内容や context から暗黙に起動しない。
- Claude frontmatter の `disable-model-invocation: true` と Codex metadata の
  `policy.allow_implicit_invocation: false` はこの explicit-only 契約を表す。
- 起動しても実装、テスト作成、委譲、Worker 起動、worktree 操作、実装開始、次工程の自動前進を行わない。
- `review` の実行、`final-candidate` / `incomplete` と圧縮出力の内部裁定までを担う。最終成果物の採用と保存・後続 Action の許可は Human が判断する。

## proposal の前段

起草は、同じ親 context 内の internal `proposal` を前段として開始する。`proposal` は要求、repository、既存仕様を
調査して candidate を作り、必要なら read-only `plan-quality-advisor` の insight を受け取る。advisor insight は
非拘束 Data であり、planner は一次情報と要求に照らして `adopted` / `rejected` / `unresolved` を裁定する。
自動採用せず、新仕様、scope、AC、ユーザー嗜好を推測しない。具体的な品質向上が残る間だけ bounded に改善し、
不可約な意味衝突、blocking evidence 不足、または安全な candidate を推奨できない場合だけ `stop-incomplete` と必要な判断・evidence を返す。
軽い不確実性や複数案は evidence と比較理由を添えて Agent が推奨する。

`proposal` が caller-owned parent へ返した `candidate snapshot` は内容を識別できる不変 Data として後段へ渡す。
`stop-incomplete` の場合は caller-owned parent がそこで停止し、後段工程を選択しない。それ以外も gate を通過した candidate だけを
`review-loop` へ渡す。

candidate snapshot を受け取った場合、同じ親 context の internal `structural-health-gate` に渡す。親が `pass` と
判断した場合だけ後段へ進む。渡す gate input には、明示起動された proposal-family public workflow parent を識別する
generic `caller_context` Data（`workflow_family: proposal-family`、`invocation: explicit-public-parent`）を含める。
gate が `context 不成立` Data を返した場合は assessment を開始せず、親は別 route へ切り替えずに
`stop-incomplete` とし、candidate/resource の編集や advisor・producer・後段処理の起動を行わない。

親は structural gate の予算を独立した `rounds` Data として管理する。gate assessment 1回を1 `round` と数える。
`rounds.limit` は下限1の ceiling としてユーザー指定を優先し、未指定時は親が loop 開始時に決定して固定する。
`rounds.limit` が1未満なら、親は値を補正・既定値置換せず受理せず、理由を添えて `stop-incomplete` とする。`rounds.limit` が1未満の入力では gate assessment、proposal の再実行、`review-loop` を起動しない。
structural gate budget と review-loop budget は別 Data とし、gate round を `adversarial_review_count` 等へ加算しない。

親は各 gate assessment を次の境界で判断する。
`pass` は上限未消化でも直ちに `review-loop` へ進む。
`return` は gate evidence だけを入力に proposal を再実行し、別 identity の candidate を再評価する。
現在の round が `rounds.limit` 未満の場合だけこの再実行を行う。`rounds.limit` 到達 round の `return` は `stop-incomplete` とする。
`rounds.limit` を超えて proposal と gate の循環を続けない。
`rounds.limit=1` の round 1 `return` は proposal を再実行せず `stop-incomplete` とする。

`insufficient-evidence` は proposal を再実行せず `stop-incomplete` とする。再 proposal 後の構造不健全な `return` は
現在の round が `rounds.limit` 未満なら上記のとおり継続し、limit 到達なら `stop-incomplete` とする。再 proposal 後の
`insufficient-evidence` は常に `stop-incomplete` とする。

gate を通過した candidate snapshot だけを、必要な review goal とともに既存の `review-loop` へ渡す。この順序
（proposal → structural-health-gate → review-loop）を飛ばさず、review-loop の採否・受け入れ・後続 Action は
既存の責務境界に従う。

## 成果物

成果物は依頼に適した自由形式の文書であり、次の最小要素を含める。

- 依頼の目的と対象を、受け取った要求原文に沿って記録する。
- 観測可能な成功条件（AC 相当）を、決まっているものだけ列挙する。
- 変更する範囲、変更しない範囲、依存、制約を明示する。
- 判断済みの前提と未確定の問いを分け、blocking な不足を勝手に補完しない。
- 選んだ方針と採用理由、代替案を採らない理由、残存 risk、確認が必要な決定を記録する。

ユーザーが実装単位の候補を求める場合、または成果物に候補を含める場合だけ、親は同じ context の内部工程として
`work-unit-design` の手順を任意に参照できる。返された `work_units`、分割／統合 signal、`blocking_gaps` は自由形式成果物の
候補部分であり、親が要求、AC、scope、依存、制約、既存調査を再検査して採用する。候補の `acceptance_criteria` は accept の
確定ではなく、base_snapshot を含む base、route、order、実行結果、review 等の execution data、委譲、実装、worker、
isolation、後続 Skill の起動権限、accept の確定、保存を成果物へ含めない。

Codex runtime が Skill 間起動を提供しない場合は、親が `work-unit-design` 本文を候補設計の工程として直接参照する。成果物の
自由形式、採用・確定・保存の責務、実装を開始しない境界は変わらない。

実装を要求と同時に渡されても、成果物の起草で停止し、実装開始を責務外として明示する。成果物を固定の
実装 schema、委譲契約、確定済み実行指示へ変形しない。後続 skill の起動権限や acceptance は出力に含めない。

## 入力の確認

起動前に要求原文、目的、対象、成功条件、scope、exclude、依存、制約、既知の current state を観測する。
不足または矛盾が成果物の品質に影響する場合は、推測で埋めず、成果物に「確定が必要な問い」として記録する。
軽微な不足は、推測ではなく `assumptions` と根拠へ分けて明示する。要求の AC を言い換えて強めたり、対象外の
方針を導入したりしない。

成果物種別を `artifact_kind` として execution data に記録する。実装を前提とするプラン系か否かは review-loop
の reviewer 適用可否だけに使い、自由形式成果物をプラン系へ変える理由にしない。

## review の判断

まず `artifact_kind` と既定 `plan-adversarial-reviewer` の責務から、成果物が reviewer 適用対象かを判定する。
既定 reviewer の適用対象外なら、review goal に対応する別 reviewer の有無にかかわらず `review-loop` に投入せず、通常の起草確定へ進む。
`artifact_kind` の適用可否を review 省略の判定より先に行う。
適用対象なら、ユーザーが review 省略を明示した場合は、`review-loop` を実行せず通常の起草確定へ進む。
適用対象で review 省略が明示されていない場合は、`review` の明示要求がなくても `review-loop` を既定で起動する。
`review_goal` は、ユーザー指定の review goal や追加の具体的な risk がない場合、「実装前プランの具体的な failure path を確認し、確定候補にできるか判断する」とする。
これは plan review 自体の既定目的であり、毎回 risk を事前発見することを要求しない。ユーザー指定 goal や追加 risk は既存 reviewer の責務内で追加できる。
review の明示要求は既定起動の前提にせず、具体的な risk を review goal として追加する場合だけ親が記録する。
ユーザー明示なしの既定 review は、具体的な risk を理由に親が自発選択した review と同じ非 accept 分岐を適用する。

既定 reviewer は `plan-adversarial-reviewer`、final trim は `over-engineering-reviewer`（プラン入力モード）である。
適用対象の成果物に対する他の reviewer はユーザーが明示した場合、または risk が既存 reviewer の責務に対応する場合だけ親が選ぶ。
review を予定し既定 reviewer の適用対象となる成果物は、reviewer の入力前提である「Acceptance Criteria」の節名と「設計」の
節名を持つように起草する。前提不足は review-loop へ渡さず、問いを補って再投入するか、レビュー不成立として返す。

`review-loop` へ渡す入力は成果物の不変 snapshot、artifact_kind、要求と判定基準、review goal、ユーザー指定の
reviewer・回数制約、必要なら継続台帳である。ユーザーが回数・打ち切りを指定しなければ、round 制御を固定値で
渡さず、親が loop 開始時に上限と打ち切りを決める。成果物の内容は review-loop の入力 resource へ書き戻さず、
採用修正を反映した会話内 execution data として受け取る。

Codex runtime が skill 間起動を提供しない場合も、親は同じ `review-loop` 本文を工程として直接参照できる。
この代替は発火条件、入力 Data、裁定、termination、受け入れの責務を変更しない。

## review 結果の受領

review-loop の通常出力は、採用 finding を反映した成果物、指摘台帳、判断保留台帳、未解決 finding、final trim
の有無と理由、`termination`、`adversarial_review_count` である。レビュー不成立（差し戻し、対応 reviewer 不在、
入力エラー）は通常出力と排他であり、理由をそのまま親へ示す。

reviewer は指摘だけを行い、採否や保留を確定しない。親は review-loop の5区分（採用、却下、範囲外、判断保留、
人間確認）と evidence・理由を保持する。判断保留は次回入力へ渡して loop 中凍結し、保留を根拠に新しい仕様を
派生させない。round、誘発収束、final trim の判定は review-loop の出力契約に従い、ここで再計算しない。

## 確定

status は上記 `candidate status Calculation` を唯一の判定として参照し、ここで条件を再定義しない。review を実行した場合も
`termination` と計画の `final-candidate` / `incomplete` を別々に親へ返す。`round-limit`、批判の出尽くし、または残存 finding は
process Data として保持し、status Calculationの入力へ渡す。レビュー不成立や review-loop が `stop-incomplete` を返した場合は、
その process failure を隠さず、status Calculationの結果を返す。
`final-candidate` では残存事項を Accepted risk / Out of scope / Human Attention に絞り、Human 向けに必要なものだけを返す。

review を実行しない場合は、要求の不足、scope、制約、残存 risk を親が確認できる通常の起草確定へ進める。どちらの場合も
成果物の最終採用、保存、issue や file への書き戻し、実装・委譲の開始は Human の許可を受けて親が実行する。

## persistence と出力境界

会話内 execution data を既定とし、成果物を保存しない。ユーザーが保存を要求した場合、後日再開・handoff・外部 review
のために必要な場合だけ、親が指定した resource へ書き出す。保存する場合も、対象 path、snapshot、書き戻し権限、更新結果を
親が記録し、入力 resource を無断更新しない。

通常の既定出力には成果物本文と、review を実行したか、確定候補か、未完了か、親へ返した問い・残存 risk を含め、`summary opt-out` 指定時は先行する「おまかせ workflow の圧縮出力」の例外契約に従う。実装を開始した、
委譲した、次工程へ進んだと誤解される status や invocation を返さない。
