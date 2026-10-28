<!-- @only claude -->
---
name: review-propose
description: >-
  明示起動時、元プランを保持してMOに基づくレビューを行い、整合した修正推奨案と効果・負担の比較をHumanへ返す。
disable-model-invocation: true
---
<!-- @/only -->
<!-- @only codex -->
---
name: review-propose
description: >-
  明示起動時、元プランを保持してMOに基づくレビューを行い、整合した修正推奨案と効果・負担の比較をHumanへ返す。
---
<!-- @/only -->
<!-- @only cursor -->
---
name: review-propose
description: >-
  明示起動時、元プランを保持してMOに基づくレビューを行い、整合した修正推奨案と効果・負担の比較をHumanへ返す。
disable-model-invocation: true
---
<!-- @/only -->

# review-propose

## 入力と所有責務

元プラン、目的・制約、気になる点、利用可能な根拠を受け取る。元プランの identity と内容を不変の比較基準として保持する。
review-propose が観点・担当選択、指摘の吟味、推奨案の整合、比較、終了を所有する。reviewer 指定を Human に求めない。
Human は採用を判断する。レビュー依頼は元プランの上書き、推奨案の採用、実装開始を許可しない。

## 同じ理解から観測する

開始時に `../../references/model-construction.md` と `../../references/agentic-model-construction.md` を読む。
一回の top-level invocation で一つの task-local Local Model を所有する。元プランと推奨案は同じ理解のもとで比較する候補成果物である。
目的と根拠、拘束力を持つ設計意図・条件、実現手段、前提、未確定事項を目的に応じて整理する。元プランの全記述を確定要求とせず、拘束条件と選んだ手段を区別する。
不明な Human の意図は推定で確定せず、必要な点だけ caller 側で確認する。固定 schema、常設台帳、RMO への必須依存を追加しない。

MO は判断を変えうる意味差を bounded な観測 projection にし、必要な区別ができるかを見る。
例えば共通化層の追加なら、今回必要な要求、追加しない場合の具体的な不成立、より単純な手段、将来の可能性との違いを必要な範囲で調べる。固定順のチェックリストにはしない。
projection から新しい要求・制約・事実を追加しない。根拠取得と解釈は caller が担い、同じ Local Model へ Reintegration し、必要な場合だけ Recomposition と再観測を行う。
MO の sufficiency はプランの正しさ、レビュー完了、採用判断を意味せず、reviewer 選択や指摘の採否も代替しない。

## レビューと推奨案

目的成立・前提・依存への反証は `plan-adversarial-reviewer`、追加構造の必要性とより単純な手段は `over-engineering-reviewer` など、具体的な問いに合う担当を選ぶ。
実現手段の別視点が必要なら `plan-quality-advisor` の助言も使える。全員を常時起動しない。
同じ対象と目的・拘束条件・根拠・問いを渡し、fresh / context-isolated、read-only / report-only で観測させる。reviewer は独自 Local Model、採用判断、元プランへの適用を所有しない。
<!-- @only codex -->
fresh reviewer / advisor は `fork_turns = "none"` で起動する。
<!-- @/only -->

caller が指摘を根拠・要求・制約に照らして吟味し、重複・競合・依存を整理する。提案をすべて足し合わせず、元プランとは別の一貫した推奨案へまとめる。
新しい根拠と判断を同じ Local Model へ反映し、影響部分だけ再確認する。前提が変化した場合は両案の比較へ明示する。
妥当な変更がなければ「元プランの維持を推奨」と返す。重要な根拠や意図が不足する場合は判断できる範囲と不足を示す。

## 比較と終了

元プラン（内容または不変な参照）、整合した推奨案、その比較を返す。単なる文章 diff にせず、必要な変更ごとに次を示す。

- 何を変えるか、理由・根拠、得られる効果、変えない場合の具体的な影響
- 増減する実装量、構成要素、依存、保守負担と追加の複雑さ
- 両案のリスク、未確定事項、根拠不足、必要な修正と任意の改善の区別
- 一部採用するときに必要な関連変更と整合性への影響

固定レイアウトや根拠のない工数・数値スコアを要求しない。元案の既知の問題と推奨案の追加コストをともに示す。
`../../references/human-facing-projection.md` を出力前に適用し、意味保持を確認する。
比較と推奨を返して停止する。元案維持、推奨案採用、一部採用後の再整理は Human が判断する。
元プランの上書き、自動採用、実装、Issue / PR 更新、公開へ自動遷移しない。保存は明示された destination / write authority に限る。
