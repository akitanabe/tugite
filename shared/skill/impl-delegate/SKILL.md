<!-- claude-only:start -->
---
name: impl-delegate
description: >-
  ユーザーが `impl-delegate` を明示した場合だけ発火する。
  自然言語の作業内容やタスク規模から推測して発火しない。
  1名の実装 worker へ TDD 実装を委譲し、親は QA と受け入れ判断を担当する。
  専用 worktree は使うが、impl-lead の Branch Plan・QA report・diff artifact は要求しない。
---
<!-- claude-only:end -->
<!-- codex-only:start -->
---
name: impl-delegate
description: >-
  ユーザーが `impl-delegate` を明示した場合だけ発火する。
  自然言語の作業内容やタスク規模から推測して発火しない。
  1名の実装 worker へ TDD 実装を委譲し、親は QA と受け入れ判断を担当する。
  専用 worktree は使うが、impl-lead の Branch Plan・QA report・diff artifact は要求しない。
---
<!-- codex-only:end -->

# impl-delegate

`impl-delegate` は、親が実装を1名の worker に委譲し、親自身が QA と受け入れ判断を行うための軽量な手順である。
この手順は、`impl-lead` の mode や Branch Plan のライフサイクルを簡略化するための別 skill である。

## 発火条件

- ユーザーが `impl-delegate` を明示的に指定した場合だけ発火する。
- 自然言語の作業内容やタスク規模から推測して発火しない。
- `impl-delegate` が明示された場合は `impl-lead` を発火しない。
- 事前適用 gate は設けない。

## Intake

1. 親はユーザーが示した Issue または doc を先に読む。目的、入力、出力、Acceptance Criteria、禁止範囲、
   境界値・異常系を確定する。
2. 対象 file、その周辺、呼び出し元・先、正本と関連 test を読む。
3. 変更前に `pwd -P`、`git branch`、基準 commit、`git status --short` を確認する。
   既存の dirty/untracked を変更しない。元 checkout に残して保護する。
4. Intake 後、親が基準 commit から専用 worktree を作成する。worker はその worktree のみを編集する。親は
   同じ対象を並行編集しない。
5. 専用 worktree は作成するが、Branch Plan を作成・提出しない。永続 QA report を作成・提出しない。
   独立した diff artifact を作成・提出しない。

## 委譲と実装

1. 親は目的、入力、出力、Acceptance Criteria、禁止範囲、境界値・異常系を worker に渡す。
2. 1名の worker へ委譲する。通常は `implementer` を選ぶ。
3. 事前整理後も残る設計または推論判断がある場合、誤実装時の手戻りまたは rollback 負担が大きい場合、
   周辺機能または外部副作用への影響が大きい場合を評価する。上位 model で誤実装リスクを具体的に減らせると
   親が判断した場合だけ `senior-implementer` を選んでよい。変更量、ファイル数、高い失敗コストという
   ラベルだけでは `senior-implementer` に昇格しない。通常と senior で迷えば `implementer` を選ぶ。
4. 親は `senior-implementer` を選んだ具体的理由を記録して最終報告する。
5. worker は指定された範囲で TDD の Red → Green → Refactor を必須として実施する。
6. Red 証跡の提出は親の要求に従う。提出がないことだけを理由に成果を拒否せず、親は実装前後の test、
   diff、AC の観測可能な振る舞いから受け入れを判断する。

## 親 QA

親 QA は必須である。worker の返却後、親は次を自分で確認する。

Red 証跡は親が要求した場合に確認する。Green と test、AC、diff は常に再確認する。

- 変更が Acceptance Criteria と禁止範囲に対応していること。
- test が外部から観測可能な振る舞い、正常系、境界値、異常系を保護していること。
- TDD の Green と test、Acceptance Criteria、diff を再確認し、Green の検証 command を再実行すること。
- 基準 snapshot からの diff を確認する。親が focused test を実行すること。
- 生成された配布物を直接編集しない。既存 test を弱体化しない。scope 外の変更がない。未承認の副作用がないこと。

専門 reviewer と `writing-principles-reviewer` は同じ隔離 worktree の確定 snapshot を読む。`review-patch-refactorer`
も同じ worktree を修正する。

親 QA は reviewer の結論で代替しない。reviewer は finding を返すだけで、最終的な採否を決めない。

## 専門 reviewer の選択

専門 reviewer は `impl-lead` と同じ具体的リスク選択方針に従う。親は次のいずれかが具体的に成立する場合だけ選ぶ。

- ユーザーが reviewer を明示した場合。
- 要求・Acceptance Criteria・既知の失敗影響、または返却 diff から reviewer の責務と一致する具体的リスクがある場合。

対象は次の reviewer である。

- `test-quality-reviewer`: 弱い test、欠けているケース、実装詳細への過度な依存。
- `responsibility-boundary-reviewer`: 責務混在、設計境界、分散した副作用。
- `security-side-effect-reviewer`: security、権限、秘密、外部副作用、rollback の欠落。

該当する reviewer がなければ 0名でよい。mode 名や変更量だけを理由に一律起動しない。
`over-engineering-reviewer` は Acceptance Criteria に不要な追加を行ったという具体的な疑いがある場合だけ、
上記と同じ親判断で選ぶ。

複数 reviewer は同一 snapshot に対して起動する。同一の diff snapshot と同じ親の一次情報を渡し、全 finding を収集して
から親が採否、修正先、または不採用を判断する。同じ diff snapshot、Acceptance Criteria、変更ファイル、focused test
の結果、具体的な review angle を Data として渡す。親は全 finding を受け取るまで採否、修正、または不採用の処理を
開始しない。reviewer 同士の先行結論を次の reviewer の入力にしない。

## 修正後の追加確認

修正後も具体的なリスクが残る場合は、影響を受ける reviewer だけを追加確認してよい。
この追加確認は有界な判断であり、固定 round を要求しない。全 reviewer を再起動しない。収束loopを設けない。
追加確認の要否と対象は親が diff とリスクを根拠に決め、確認後は親 QA と Green の再検証を行う。

## 最終 gate と終了

最終 diff に対して `writing-principles-reviewer` を必ず1回起動する。これは専門 reviewer の選択数には含めない。
採用した指摘だけを `review-patch-refactorer` に渡す。review-patch-refactorer は最小の behavior-preserving patch だけを行う。
`writing-principles-reviewer` の finding が振る舞い変更、仕様判断、または再設計を要する場合は `review-patch-refactorer`
へ渡さない。親が理由付き不採用または未完了と判断する。修正範囲を拡張しない。`writing-principles-reviewer` を再起動しない。
`writing-principles-reviewer` 自身には変更をさせず、patch 後に同 reviewer を再起動しない。
patch 後は親 QA と Green 確認で終了する。

## Closeout

親は repository-native の最終 gate を実行し、最終 diff と `git status --short` を確認する。
commit・push・PR はユーザーが明示した場合だけ行う。
明示された commit/push/PR と最終確認を先に実行する。その後、次の全条件を満たす場合だけ専用 worktree を cleanup する。
(a) worktree の意図した変更が commit 済みである、(b) `git status --short` に未 commit・未追跡の成果がない、
(c) 依頼された push/PR 等があれば成功と最終状態を確認済みである。満たさなければ cleanup せず、path/status を報告する。
force 削除は行わない。Intake 前の dirty/untracked は保持する。
変更ファイル、検証 command と結果、AC 対応、残存 risk、未検証事項を報告する。判断点も報告する。
明示がなければ、親へ変更ファイル、検証 command と結果、AC 対応、Red 証跡、判断点、残存 risk、未検証事項を返して終了する。
