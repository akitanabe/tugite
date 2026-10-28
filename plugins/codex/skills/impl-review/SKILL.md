---
name: impl-review
description: >-
  明示起動時、実装済み差分を共通の専門・テスト・記法基準でレビューし、Human確認用の修正表を返して変更前に停止する。
---
<!-- Generated from shared/. Do not edit directly. -->

# impl-review

## 対象の決定

明示指定を優先し、指定がなければ会話・作業 context に保持された変更を使う。両方から特定できない、または解釈で対象範囲が変わる場合だけ Human に必要な点を確認する。
明示指定が曖昧・不整合なら別対象へ置き換えない。直前の変更を無条件に最新 commit や全 working tree と同一視せず、混在する無関係な変更を取り込まない。
推定した対象を現在の code / diff と照合し、何を対象にしたか示す。周辺コード・テストを読む範囲と修正提案の対象範囲を区別する。

## 入力と snapshot

利用可能な根拠から比較元、差分、目的・要求・制約、周辺 context、実施済み検証、未確認事項を整理する。毎回 Human へ入力一式を要求しない。
base と対象を安全に確定できなければ確認する。検証証拠の不足は未確認として保持し、事実を Human の選択で補わない。
コミット済み・未コミットの両方を扱い、対象ファイルの内容、差分と比較元を固定する。未コミット状態は内容と status を記録して観測の同一性を確保し、レビュー用 commit は作らない。

## 三つのレビュー

`../../references/implementation-review.md` を読み、共通 input packet、専門 reviewer 選択、changed-test applicability / evidence、writing review、finding handling を適用する。
専門観点は具体的な risk に応じて選び、changed test artifact があれば coverage / validity の両 reviewer を用いる。writing reviewer は対象全体の記法を観測する。
reviewer は独立 context で同じ対象を read-only / report-only で確認する。必要な reviewer が利用できなければ、その観点は未確認と明示する。
共有基準の適用は Parent QA、Unit 受入、commit 確定や impl-lead の全工程完了を意味しない。実装単位の再分解・再委譲は行わない。

対象が途中で変わった場合は影響を確認し、古い結果を現状のレビュー完了としない。修正後の再レビューも現在の対象状態と影響した観点を確認する。
レビューのための恒久的な test 変更や mutation を自動実施しない。既存実行証拠の参照と今回実行した確認を区別する。

## 修正表と停止

caller が根拠を確認し、重複・競合・依存を整理して推奨を作る。指摘をすべて採用扱いにせず、不確かな懸念、対象外、好みは必要な修正と分ける。
対象、base、確認状態、適用観点、非適用と未確認を示したうえで、次の意味を持つ修正表を返す。

- 対象箇所と観点、問題・懸念と根拠
- 推奨修正と、修正しない場合の影響
- 修正の影響・追加複雑さ、要求成立に必要か任意改善か
- 関連修正・依存関係、追加確認が必要な事項

指摘なしの場合も確認範囲と限界を示す。件数を増やすことを目的にせず、Pass や指摘なしから全体の正しさ・検証完了を保証しない。
`../../references/human-facing-projection.md` を適用して意味保持を確認し、修正表を返したところで停止する。
コード・テスト・設定の変更、commit・push・merge を行わない。Human が採用・見送り・再検討を判断し、その後の依頼が修正と必要な検証の authority になる。
