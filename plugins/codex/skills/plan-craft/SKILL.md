---
name: plan-craft
description: >-
  ユーザーが明示した場合だけ、実装接続を前提にしない自由形式の計画・設計成果物を起草し、
  必要な場合だけ review-loop を起動して確定候補を返す。実装・委譲・次工程の自動前進は行わず、
  親が成果物の受け入れを判断する。
---
<!-- Generated from shared/. Do not edit directly. -->

# plan-craft

この Skill は、依頼に応じた自由形式の計画・設計成果物を起草し、親へ確定候補を返す。成果物は設計判断書、
改修方針、移行計画、比較検討、作業メモ、リスク整理、実装単位の候補案などでよく、特定の実行 schema や
固定された後続工程の入力へ変換しない。規範本文はこの Skill 自身で完結し、別の実装 workflow の本文を前提にしない。

## 発火制御と責務

- ユーザーが `$plan-craft` または同等の明示要求をした場合だけ起動する。自然言語の作業内容や context から暗黙に起動しない。
- Claude frontmatter の `disable-model-invocation: true` と Codex metadata の
  `policy.allow_implicit_invocation: false` はこの explicit-only 契約を表す。
- 起動しても実装、テスト作成、委譲、Worker 起動、worktree 操作、実装開始、次工程の自動前進を行わない。
- `review` の実行、成果物の確定候補、必要な問いの提示までを担い、受け入れと後続 Action は親へ残す。

## proposal の前段

起草は、同じ親 context 内の internal `proposal` を前段として開始する。`proposal` は要求、repository、既存仕様を
調査して candidate を作り、必要なら read-only `plan-quality-advisor` の insight を受け取る。advisor insight は
非拘束 Data であり、planner は一次情報と要求に照らして `adopted` / `rejected` / `unresolved` を裁定する。
自動採用せず、新仕様、scope、AC、ユーザー嗜好を推測しない。具体的な品質向上が残る間だけ bounded に改善し、
人間の判断が必要、または安全な candidate を作れない場合は `stop-incomplete` と必要な判断・evidence を返す。

`proposal` が返した `candidate snapshot` は内容を識別できる不変 Data として後段へ渡す。`stop-incomplete` の場合は
plan-craft がそこで停止し、review-loop を起動しない。

candidate snapshot を受け取った場合だけ、必要な review goal と
ともに既存の `review-loop` へ渡す。この順序（proposal → review-loop）を飛ばさず、review-loop の採否・受け入れ・
後続 Action は既存の責務境界に従う。

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

review は固定 phase ではない。ユーザーが review を明示した場合は実行する。それ以外は、具体的な risk と
review 結果が親の判断を変えることを期待できる evidence を説明できる場合だけ `review-loop` を起動する。明示も具体的な
risk もなければ review を起動せず、通常の起草確定へ進む。

既定 reviewer は `plan-adversarial-reviewer`、final trim は `over-engineering-reviewer`（プラン入力モード）である。
他の reviewer はユーザーが明示した場合、または risk が既存 reviewer の責務に対応する場合だけ親が選ぶ。review を
予定し既定 reviewer の適用対象となる成果物は、reviewer の入力前提である「Acceptance Criteria」の節名と「設計」の
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

review を実行した場合、`converged` または未解決 finding のない `induced-loop` だけを確定候補とする。
ユーザーが review を明示したのにレビュー不成立、`round-limit`、`stop-incomplete`、未解決を伴う `induced-loop`
になった場合は、代替 evidence で完了扱いにせず、ユーザー確認または未完了終了だけを選ぶ。親が具体的な risk を理由に
自発選択した review のレビュー不成立に限り、代替 evidence で品質下限を独立確認できた場合は確定候補にできる。
それ以外の非 accept 返却では成果物を確定せず、残存 risk と問いを示す。

review を実行しない場合は、要求の不足、scope、制約、残存 risk を親が確認できる通常の起草確定へ進める。どちらの場合も
成果物の受け入れ、保存、issue や file への書き戻し、実装・委譲の開始は親の明示 Action とする。

## persistence と出力境界

会話内 execution data を既定とし、成果物を保存しない。ユーザーが保存を要求した場合、後日再開・handoff・外部 review
のために必要な場合だけ、親が指定した resource へ書き出す。保存する場合も、対象 path、snapshot、書き戻し権限、更新結果を
親が記録し、入力 resource を無断更新しない。

出力には成果物本文と、review を実行したか、確定候補か、未完了か、親へ返した問い・残存 risk を含める。実装を開始した、
委譲した、次工程へ進んだと誤解される status や invocation を返さない。
