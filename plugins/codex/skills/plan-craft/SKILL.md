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

reviewer の `人間確認` は reviewer が観測した signal に留まり、採否・停止・推奨を決めない。public workflow parent が内部工程として `final-candidate` / `incomplete` と圧縮出力を裁定し、Human が最終成果物の採用と後続 Action を許可する。

### semantic completion eligibility Calculation

artifact 保存前の semantic completion eligibility は、不可約な意味衝突、blocking evidence 不足、structural budget 等で
安全継続不可、workflow/context 不成立、現 candidate を推奨不能な状態、blocking finding、未反映修正必須、要求意味変更、
または evidence 不足のいずれもなく、現在の candidate を推奨できる場合だけ成立する。単なる複数案、別案、軽い不確実性だけでは
`stop-incomplete` にせず、Agent が比較して一案を推奨し、残る不確実性を risk または Human Attention へ記録する。

outward candidate status は次の Calculation で一度だけ決める。semantic completion eligibility と後述の保存結果を入力とし、
両方が成功した場合だけ `final-candidate`、それ以外は `incomplete` とする。semantic 判定と保存後で status を二度確定しない。

## おまかせ workflow の review と推奨判定

review の `termination` は review-loop がどのように終了したかを示す process Data であり、`final-candidate` / `incomplete`
という計画の判定とは別軸である。criticism exhaustion、round-limit、残存 finding は process Data として保持し、candidate status は
上記 Calculation の結果を参照する。

review を続ける価値の判断が難しい場合だけ、read-only `plan-quality-advisor` を起動できる。毎 round 起動せず、advisor には request、repository_observation、review_goal、current snapshot、finding ledger、直近差分、verification、residual risk を Data として渡す。advisor は追加 round の期待利益、
残存 finding、churn/限界効用、不足 evidence を非拘束 insight として返す。advisor は candidate を修正せず、parent が
continue / stop-and-finalize / stop-incomplete を裁定する。

semantic completion eligibility が成立した場合、bounded stop 後の残存 finding が成果物自体の residual risk または scope 外事項に
実質的な影響を持つときだけ、成果物本文の内容として反映する。Human の最終判断が必要な事項は stdout の Human Attention に絞る。
解消済み、却下済み、軽微な文言、disposition、churn の履歴は成果物または stdout へ残さない。

## おまかせ workflow の圧縮出力

`final-candidate` の既定出力は Result / 短い Summary / 必要な場合だけの Human Attention / Artifact local path とする。
final summary は明示 opt-out できる。review skip と final summary skip は独立であり、一方を指定しても他方を暗黙に変更しない。
`final-candidate` の summary opt-out は Artifact だけを返す。ただし `incomplete` の summary opt-out では `Result: incomplete`、
Blocking Reason、Residual Risk を必ず返し、必要な場合だけ Human Attention を示す。途中の decision / review 全履歴を Human に
要求しない。詳細な artifact と stdout の境界は後述の completion contract に従う。

`return target` は public workflow parent が所有する。現在の plan-craft は gate の assessment を受けて proposal へ
返すか後段へ進むかを親として判断し、明示されていない別 workflow へ自動 switch しない。

## 発火制御と責務

- ユーザーが `plan-craft` の起動または同等の明示要求をした場合だけ起動する。自然言語の作業内容や context から暗黙に起動しない。
- 各 platform の invocation metadata は上記の explicit-only 契約を表し、その範囲を拡張しない。
- 起動しても実装、テスト作成、委譲、Worker 起動、worktree 操作、実装開始、次工程の自動前進を行わない。
- `review` の実行、local artifact の安全な保存、`final-candidate` / `incomplete` と圧縮出力の内部裁定までを担う。最終成果物の採用と後続 Action の許可は Human が判断する。

## proposal resolution の caller ownership

proposal の invocation boundary、discretionary authority、resolution execution bound は `plan-craft` が所有する。
internal `proposal` の開始時に、caller=`plan-craft`、resolver=planner、counterpart=`plan-quality-advisor`（Resolution
Transaction 外の one-shot observation）、authority=discretionary として mapping し、proposal が規定する
batch-resolve-kernel loader を親 Action として一度だけ実行する。advisor は非拘束 Data を返し、planner が一次情報を
基準に既存 adoption ledger へ裁定する。proposal の advisor invocation は candidate S0→advisor #1→Resolution
Transaction #1→verified S1→fresh-context advisor #2→Resolution Transaction #2→verified S2→return の exactly 2 pass
であり、Batch / selected set の空判定にかかわらず第2 passを起動し、第3 passを起動しない。

ユーザーが安全上限を指定していない場合、親は proposal loop の開始時に resolution execution bound を internal responsibility
として決定し、loop 中は固定する。固定数、新しい public parameter / schema、`resolve_rounds` は追加しない。この bound は
structural gate budget および review-loop budget と別 Data とし、相互に加算・流用しない。

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

ユーザーが実装単位の案を求める場合は自由形式成果物の一部として自然文で記述してよいが、正式な Work Unit Data または
Work Unit normalization とは扱わない。正式な normalization は implementation-time の `impl-lead` が current repository state を
再観測して行う。base_snapshot を含む base、route、order、実行結果、review 等の execution data、委譲、実装、worker、isolation、
後続 Skill の起動権限、accept の確定、保存を成果物へ含めない。

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

runtime が skill 間起動を提供しない場合も、親は同じ `review-loop` 本文を工程として直接参照できる。
この代替は発火条件、入力 Data、裁定、termination、受け入れの責務を変更しない。

## review 結果の受領

review-loop の通常出力は、採用 finding を反映した成果物、指摘台帳、判断保留台帳、未解決 finding、final trim
の有無と理由、`termination`、`adversarial_review_count` である。レビュー不成立（差し戻し、対応 reviewer 不在、
入力エラー）は通常出力と排他であり、理由をそのまま親へ示す。

reviewer は指摘だけを行い、採否や保留を確定しない。親は review-loop の結果を `adopted` / `rejected` / `out-of-scope` /
`deferred` / `human-confirmation` のいずれかへ evidence・理由とともに裁定して保持する。`deferred` は既存の hold ledger を
通じて次回入力へ渡し、loop 中は凍結する。保留を根拠に新しい仕様を派生させない。round、誘発収束、final trim の判定は
review-loop の出力契約に従い、ここで再計算しない。

## 確定

status は上記 `outward candidate status Calculation` を唯一の判定として参照し、ここで条件を再定義しない。review を実行した場合も
`termination` と計画の `final-candidate` / `incomplete` を別々に親へ返す。`round-limit`、批判の出尽くし、または残存 finding は
process Data として保持し、status Calculationの入力へ渡す。レビュー不成立や review-loop が `stop-incomplete` を返した場合は、
その process failure を隠さず、status Calculationの結果を返す。
`final-candidate` では、成果物内容に属する residual risk と scope 外事項は本文に統合し、Human の最終判断に必要なものだけを Human Attention へ渡す。

review を実行しない場合は、要求の不足、scope、制約、残存 risk を親が確認できる通常の起草確定へ進める。どちらの場合も
成果物の最終採用、issue や既存 resource への書き戻し、実装・委譲の開始は Human の許可を受けて親が実行する。

## local artifact completion

semantic completion eligibility が成立した場合だけ、成果物本文の byte snapshot を凍結し、保存先選択と保存 Action を開始する。
成立しない場合は path 選択も write も行わず `incomplete` とする。明示保存先を最優先し、directory 指定なら自動 filename をその配下に置き、
file path 指定なら basename を尊重する。指定先の path type、containment、symlink / junction 非追従、no-clobber publish を安全に確認できなければ、
無言で別の保存先へ fallback せず `incomplete` とする。

保存先が未指定なら、既存 directory であり、project の documentation、configuration、ignore comment、または既存の同種 artifact から
temporary / local-only 用途を直接観測できる project-local 候補だけを評価する。directory 名や ignored であることだけは用途 evidence とせず、
cache、build、vendor 等の decoy を除外する。repository root から final path と staging path までの各 component を symlink / junction 非追従で確認し、
canonical containment が成立し、その exact final path が ignored かつ index 未登録と確認できる場合だけ候補にする。同種 artifact の convention として
最も直接的な evidence を持つ候補を一意に選べる場合だけ project-local を使う。候補なし、同順位、non-Git project、または用途・Git 管理外・containment を
確認できない場合は OS temporary directory へ fallback する。OS temp は platform が提供する temp root の identity、canonical path、symlink / junction 非追従を、
run-owned directory の作成前に検証する。temp root または予定する final / staging の canonical path が repository 内に入る場合は OS temp という名称を根拠にせず、
project-local と同じ用途・ignored・index 未登録・containment の資格を作成前に適用する。資格が成立した場合だけ temp root 直下に secure / exclusive な
run-owned directory を新規作成し、作成時の directory object identity を記録する。final と staging の canonical containment と各 component の非追従を再確認する。
temp root、run-owned directory、containment、非追従、repository との関係を確認できなければ write 前に `incomplete` とする。未指定時に project-local directory や ignore rule を新設しない。

自動 filename は成果物の内容由来の短く可読な単一 component とし、空文字、`.`、`..`、absolute path、path separator を採用しない。
既存 final path は bytes が同一でも上書きせず collision とし、数値 suffix 付きの次 candidate を評価する。再試行上限は invocation 開始時に有限値として固定し、
collision の場合だけ suffix を変える。各 exact path の資格は publish 直前に再確認し、未指定の project-local が資格を失った場合はそこへ書かず、
OS temporary directory から選択をやり直す。

```text
workflow = plan-craft
artifact_eligibility = semantic completion eligibility and verified save success
artifact_body = frozen final candidate body only
artifact_excludes = [Semantic Delta, Verification Delta, Human Attention, gate result, review result, decision ledger, finding ledger, process history]
incomplete_artifact = none
explicit_destination = highest priority; unsafe or unusable means incomplete without fallback
unspecified_project_local = existing temporary or local-only purpose is directly evidenced; exact final path is ignored and index-unregistered
os_temp_fallback = no candidate, tied candidates, non-Git project, or unconfirmed qualification
project_mutation = do not create a project-local directory or ignore rule
filename = content-derived safe single component
collision = never overwrite an existing file; finite numeric suffix retry only on collision
save = same-filesystem run-owned staging write -> close -> byte-identical readback -> complete-only no-clobber publish
save_failure = incomplete; clean exact staging residue or report it as residual risk
stdout = Result, short Summary, optional Human Attention, Artifact local path
stdout_excludes = full artifact body, Semantic Delta, Verification Delta, gate or review result, decision or finding ledger, process history
summary_opt_out = Artifact only
authority = not Git management, durable persistence, final acceptance, or downstream Action permission
```

```text
staging_creation = atomic exclusive non-follow new object beneath verified destination identity
staging_identity = same object identity through write, readback, and cleanup
qualification_recheck = immediately before staging creation and immediately before publish
destination_reselection = owned staging identity must match and cleanup must succeed first
cleanup_excludes = pre-existing or identity-mismatched object
unsafe_primitive = stop before write or return safe incomplete
os_temp = validated platform temp root -> secure exclusive run-owned directory
os_temp_paths = canonical containment and non-follow for final and staging
os_temp_repo_overlap = project-local qualification applies when canonical path is inside repository
os_temp_unconfirmed = stop before write as incomplete
run_owned_directory_identity = record at creation
run_owned_directory_cleanup = before publish commit on incomplete or destination reselection; after owned staging handling; same identity and empty; non-recursive non-follow remove only
run_owned_directory_residue = identity mismatch, non-empty, or removal failure means leave and report exact residue
run_owned_directory_commit = preserve directory containing published final artifact
```

選択した destination の資格と object identity を staging 作成の直前に再確認する。検証済み destination identity の下で、同じ filesystem 上の
run-owned staging path を atomic / exclusive / non-follow で新規作成する。作成した object identity を記録し、その同一 object を write、close 後の readback、
cleanup まで保持して byte 一致を確認する。既存 object の排他取得に失敗したら書き込まず、run-owned staging として扱わない。
安全で確定的な staging / publish primitive または identity 確認が利用できなければ、本文を write する前に停止するか、すでに所有済みの staging を同一 identity で安全に cleanup できる場合だけ `incomplete` とする。

readback 成功後、destination の資格と identity、staging の所有 identity を publish の直前に再確認する。未完成 final path を露出せず既存 final path を
上書きしない確定的 no-clobber operation で publish し、その成功を保存の commit point とする。destination の資格喪失等で別 destination を選び直す場合は、
記録した staging identity と現 object の identity が一致し、その run-owned staging の cleanup が成功したことを確認してから再選択する。identity 不一致、所有確認不能、
または cleanup failure では他者 object を削除せず `incomplete` とする。
その destination のために OS-temp run-owned directory を作成済みなら、staging の処理後に記録済み directory identity と現在の identity が一致し、directory が空であることを
確認し、non-recursive / non-follow operation でその directory だけを削除する。この cleanup の成功後だけ destination を再選択する。identity 不一致、非空、
または削除失敗では directory を変更せず、exact residue を報告して `incomplete` とする。recursive delete は行わない。
publish 直前の collision は資格確認から有限再試行し、それ以外の write、readback、publish failure または上限到達は final path が成果物として生成されていないことを確認して
`incomplete` とする。記録済み identity と一致する run-owned staging だけを cleanup し、所有を確認できない residue は削除せず未完成の residual risk として返す。
publish commit 前に `incomplete` となる OS-temp run-owned directory にも、owned staging 処理後の同じ identity / empty / non-recursive / non-follow cleanup を適用する。
identity 不一致、非空、または削除失敗はそのまま残し exact residue として報告する。publish 成功済み final artifact を含む run-owned directory は削除せず保持する。

publish 結果を semantic completion eligibility とともに outward candidate status Calculation へ渡す。artifact には凍結した成果物本文の bytes だけを入れ、
要約、Human Attention、gate / review 結果、decision / finding ledger その他の process Data を追記しない。`final-candidate` の stdout は成果物全文を出さず、
`Result: final-candidate`、成果物内容だけの短い `Summary`、必要な場合だけ `Human Attention`、実際に保存・確認した `Artifact: <local path>` に限る。
clickable decoration は local path 自体に代えない。保存した artifact は Git 管理、永続保存、最終採用、または後続 Action の許可を意味しない。
