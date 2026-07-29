<!-- Generated from shared/. Do not edit directly. -->

# 過剰実装のプラン審査

`over-engineering-reviewer` をプラン入力モードで起動し、プランが新規に導入しようとする要素のうち、
取り除いても AC と明示された制約を満たせるものを実装前に検出する規約を定める。読み替えの正本は
`over-engineering-reviewer` 自身の `## プラン入力モード` 節にあり、この文書は起動契約だけを定める。

## 目次

- 起動契約
- 渡す入力
- 指摘の反映経路
- 差し戻し条件

## 起動契約

- adversarial の収束後に1回だけ起動する。起動タイミングと再実行の規約は
  [敵対的レビューループ](adversarial-review.md) の「過剰実装審査との接続」に従う。
- 起動時にプラン入力モードであることを明示し、Implementation Plan Data を渡す。明示しない起動は
  既定の diff 入力モードになるため、プラン審査には使えない。
- 指摘は同じ `PF-*` 台帳へ `reviewer: over-engineering-reviewer` として記録し、指摘IDごとに
  verdict の確定と `adopted` / `rejected` の判断を記録する（敵対的レビューループと同一規約）。

## 渡す入力

- 実装プラン本体（`plan.objective` / `plan.design` / `plan.approach` / `plan.steps`）。
- AC の全文と、ユーザーが明示した constraints。
- scope（`allowed_paths` / `forbidden_paths` / `out_of_scope`）。
- テスト結果は渡さない。プラン時点では存在せず、reviewer も入力として要求しない。

## 指摘の反映経路

- 指摘の反映経路はプラン修正だけとする。採用した指摘は親がプランへ反映する。
- `review-patch-refactorer` を使わない。修正対象は code ではなくプランであり、除去経路の判断は
  発生しない。
- 指摘を採用してプランを修正した場合は adversarial レビューへ戻る。不採用だけで修正がなければ
  審査は完了とする。

## 差し戻し条件

- AC または明示された制約が無い Implementation Plan Data は、reviewer が判定せず親へ差し戻す。
  親は起草へ戻って AC・制約を確定してから再起動する。
- 差し戻しは指摘0件と区別して扱い、`termination` や台帳に審査完了として記録しない。
