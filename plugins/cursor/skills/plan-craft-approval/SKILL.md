---
name: plan-craft-approval
description: >-
  ユーザーが明示した場合だけ、人間と方向性を逐次裁定して自由形式の計画・設計成果物を作る。
  direction freeze 後に structural gate と固定 review を通し、最終結果を人間へ返す。
  実装・委譲・次工程の自動前進は行わない。
disable-model-invocation: true
---
<!-- Generated from shared/. Do not edit directly. -->

# plan-craft-approval

この Skill は人間参加型の自由形式計画・設計成果物を起草し、親が確定候補または未完了結果を返す public workflow
である。`plan-craft` と自動切替せず、双方向ともユーザーの明示起動だけで開始する。

## 発火制御と責務

- `plan-craft-approval` の起動または同等の明示要求がある場合だけ起動し、context から暗黙起動しない。
- 各 platform の invocation metadata は上記の explicit-only 契約を表し、その範囲を拡張しない。
- 実装、委譲、Worker 起動、worktree 操作、後続の実装開始を行わず、final acceptance 後の final-candidate だけを local artifact へ保存する。
- 起草、対話、gate、review、final acceptance 候補または未完了の返却までを担う。人間は方向性と最終結果の責任を持ち、
  public workflow parent は planner として、調査、具体化、整合性、verification、工程の経過責任を持つ。後続 Action は
  人間へ残す。

## 入力と成果物

要求原文、目的、対象、成功条件、scope、exclude、依存、制約、current state を先に観測する。blocking な不足を
推測せず、軽微な不足は根拠付き assumption に分離する。成果物には目的、観測可能な成功条件、設計、scope と exclude、
依存、制約、選択理由、棄却した代替案、verification、残存 risk、未確定の問いを含める。

成果物種別を `artifact_kind` Data として保持する。実装前提プラン系か否かは reviewer 適用可否だけに使い、自由形式
成果物をプラン系へ変える理由にしない。実装前提プラン系は `Acceptance Criteria` と `設計` の節名を持つ。

## proposal-dialogue の caller mapping

`plan-craft-approval` は `proposal-dialogue` の invocation boundary、人間判断の binding authority、resolution execution bound を所有する。
ユーザーが安全上限を指定しない場合は、親が dialogue loop の開始時に internal responsibility として固定する。固定値、新しい public parameter または schema、`resolve_rounds` は追加しない。
resolution execution bound を structural-health-gate の `rounds` または review の回数制約へ加算・混同しない。

internal `proposal-dialogue` の開始前に、`proposal-dialogue` が規定する resolve-kernel loader を親 Action として一度だけ実行する。

## proposal-dialogue の前段

同じ親 context の internal `proposal-dialogue` を開始し、人間の裁定を逐次反映・verification した direction freeze
候補を受け取る。blocking な人間判断が残る、または `stop-incomplete` の場合はそこで停止し、後段へ進めない。

direction freeze は成果物全文の固定ではなく、人間が確定した意味判断を保護する境界とする。親は方向性、実装イメージ、
重要な verification を圧縮して人間へ示し、freeze 後の gate と review へ frozen decisions と変更可能な具体化を区別して渡す。
大きな purpose または scope の変更が入力された場合は既存成果物へ増分追加せず、この public workflow 全体を再策定する。
過去 decision は自動継承せず、candidate prior decisions と再利用知見として現在の要求と evidence で再検証する。

## structural-health-gate

direction freeze 候補を受け取った場合は、提案が全件却下された場合も同じ親 context の internal
`structural-health-gate` へ渡す。input には generic `caller_context` Data（`workflow_family: proposal-family`、
`invocation: explicit-public-parent`）を含める。`context 不成立` は別 route へ切り替えず `stop-incomplete` とする。

親は gate 予算を独立した `rounds` Data として管理し、assessment 1回を1 round と数える。`rounds.limit` は下限1の
ceiling とし、ユーザー指定を優先する。未指定なら親が loop 開始時に固定し、1未満は補正せず `stop-incomplete` とする。
1未満では assessment、producer の再実行、後段を起動しない。gate 予算と review 予算は別 Data とする。

`pass` は直ちに後段へ進む。`return` は現在の round が limit 未満の場合だけ、gate evidence を人間へ自然文の新しい
判断点として提示できる入力にして `proposal-dialogue` を新しい対話 loop として再実行し、別内容の candidate を再評価する。
limit 到達 round の `return` と `insufficient-evidence` は
`stop-incomplete` とする。人間が構造 finding への対応を全件却下し candidate 内容が変わらない場合、同一内容へ
別 identity を付けて再投入せず、構造欠陥未解消として `stop-incomplete` とする。

## review の適用と固定順序

工程順序は `proposal-dialogue → structural-health-gate → review-loop` であり、gate が `pass` した snapshot だけを
次の判定へ渡す。まず `artifact_kind` と既定 `plan-adversarial-reviewer` の責務から reviewer 適用可否を判定する。既定 reviewer の適用対象外なら、review goal に対応する別 reviewer の有無にかかわらず `review-loop` に投入せず、通常の起草確定へ進む。review 省略の明示より reviewer 適用可否の判定を先に行う。

reviewer 適用可能な成果物は、ユーザーによる review の明示要求がなくても固定工程として `review-loop` へ渡す。
ユーザーが review 省略を明示した場合は、確定候補とせず、review 未実施の起草物と残存 risk を添えて未完了として返す。

`review-loop` には不変 snapshot、`artifact_kind`、`caller_context`、要求と判定基準、review goal、reviewer・回数制約、
必要なら継続台帳を渡す。回数制約がなければ親が loop 開始時に上限と打ち切りを決める。既定 reviewer は
`plan-adversarial-reviewer`、final trim は `over-engineering-reviewer` のプラン入力モードである。`review_goal` は、ユーザー指定の review goal や追加の具体的な risk がない場合、「実装前プランの具体的な failure path を確認し、確定候補にできるか判断する」とする。これは plan review 自体の既定目的であり、毎回 risk を事前発見することを要求しない。ユーザー指定 goal や追加 risk は既存 reviewer の責務内で追加できる。入力前提不足は
補って再投入するかレビュー不成立として返す。

## review 結果と direction freeze の保護

通常出力の成果物、指摘台帳、判断保留台帳、未解決 finding、final trim、`termination`、
`adversarial_review_count` を受け取る。親は finding を既存5区分（採用、却下、範囲外、判断保留、人間確認）へ
evidence と理由付きで裁定する。判断保留は loop 中凍結し、round、誘発収束、未解決 finding を再計算しない。

decision ledger で人間が裁定済みの方向性を変更・撤回する finding は、局所修正で閉じる場合も親だけで採用せず
`人間確認` へ裁定する。人間の再判断後だけ成果物へ反映し、既存の裁定区分を増やさない。

review は frozen decisions を守る限り、実装の具体化、verification の補強、複雑性の削減を行える。frozen decision の
変更が必要なら、改善案を採用せず `人間確認` へ止める。

## review 完了と final acceptance

review 実行経路では `converged` または未解決 finding のない `induced-loop` だけを確定候補とする。レビュー不成立、
`round-limit`、`stop-incomplete`、未解決 finding を伴う `induced-loop` は確定候補とせず、理由、台帳、残存 risk を
添えて未完了として返す。代替 evidence で完了扱いにしない。

`review-loop` が新しい設計選択を必要として `stop-incomplete` を返しても `proposal-dialogue` へ自動逆遷移しない。
人間へ対話の再開、未完了終了、scope 外への分離を提示する。未完了返却後の受け入れと再投入は人間が明示的に判断し、未完了結果を artifact として保存しない。

final acceptance は direction freeze と分離し、既定で必須とする。人間が明示的に opt-out した場合だけ承認 Action を
省略できるが、final report は省略しない。承認 Action の入力には、成果物内容の短い要約、方向変更の有無、追加・変更した検証とその結果、
残存 risk、必要な人間判断を含める。承認完了または明示 opt-out までは、direction freeze、gate 通過、review 済み candidate のいずれも artifact として保存しない。

final acceptance での修正要求は正常な結果として扱う。親は変更の影響と依存する判断だけを新しい `proposal-dialogue` loop で
局所 reopen し、decision ledger 全体をリセットしない。再 review は変更箇所と直接・間接の波及へ限定し、無関係な領域へ
探索を広げない。大きな purpose または scope の変更なら局所 reopen を行わず、public workflow 全体を再策定する。

## final acceptance 後の local artifact completion

final acceptance が完了した場合、または人間が final acceptance を明示 opt-out した場合だけ、成果物本文の byte snapshot を凍結し、
保存先選択と保存 Action を開始する。それ以外の `incomplete`、direction freeze、gate、review、acceptance candidate では path 選択も write も行わない。
明示保存先を最優先し、directory 指定なら自動 filename をその配下に置き、file path 指定なら basename を尊重する。指定先の path type、containment、
symlink / junction 非追従、no-clobber publish を安全に確認できなければ、無言で別の保存先へ fallback せず `incomplete` とする。

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
workflow = plan-craft-approval
artifact_eligibility = final acceptance completed and verified save success
pre_acceptance_artifact = none at direction freeze, gate, review, or acceptance candidate
artifact_body = frozen final accepted candidate body only
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

publish 成功後だけ outward status を一度計算し `final-candidate` とする。保存失敗は final acceptance の成否にかかわらず `incomplete` に写像する。
artifact には凍結した成果物本文の bytes だけを入れ、要約、Human Attention、gate / review 結果、decision / finding ledger その他の process Data を追記しない。
`final-candidate` の stdout は成果物全文を出さず、`Result: final-candidate`、成果物内容だけの短い `Summary`、必要な場合だけ `Human Attention`、
実際に保存・確認した `Artifact: <local path>` に限る。final summary の明示 opt-out では `Artifact` だけを返す。clickable decoration は local path 自体に代えない。
保存した artifact は Git 管理、永続保存、最終採用、または後続 Action の許可を意味しない。
