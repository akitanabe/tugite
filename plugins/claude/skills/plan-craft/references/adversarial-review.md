<!-- Generated from shared/. Do not edit directly. -->

# 敵対的レビューループ

`plan-adversarial-reviewer` によるプランの敵対的レビューを、打ち切り条件が成立するまで round として
繰り返す規約を定める。reviewer は指摘 Data だけを返し、verdict の確定・採用判断・プランへの反映・
打ち切り判定はすべて親エージェントが行う。必須完了ゲートと同じく、reviewer の自己申告を信用せず、
指摘IDごとの判断を記録してから先へ進む。

## 目次

- round の構成
- 指摘台帳
- evidence を欠く指摘の扱い
- 打ち切り条件
- 誘発指摘による収束
- 過剰実装審査との接続
- round-limit 時の提示

## round の構成

レビューが判定する対象はプラン文書の「設計」節であって AC の集合ではない
（判定の軸の正本は `plan-adversarial-reviewer`）。
プラン文書の節構成と各節の責務は
[起草手順](plan-drafting.md) の「プラン文書の節構成」を正本とする。

1 round = `plan-adversarial-reviewer` 起動1回とする（adversarial round）。各 round は次の順で進める。

1. reviewer へプラン文書の全文と、2 round 目以降は前 round までの
   指摘台帳を渡して起動する。
2. 親が指摘IDごとに内容を確認し、`軽微` の定義（`plan-adversarial-reviewer` が持つ影響基準 +
   軽微類型カタログ）に照らして verdict を確定する。reviewer の verdict 申告をそのまま採用しない。
3. 親が指摘IDごとに採用（`adopted`）/ 不採用（`rejected`）を判断し、確定 verdict・判断・理由を
   `review.findings` に記録する。
4. 採用した指摘をプランへ反映し、`rounds_completed` を進めて次 round へ台帳を渡す。

## 指摘台帳

- 指摘台帳と round 状態はプラン文書の外に持つ。本文へ書くと、指摘の解消が本文の変更として
  現れず、round ごとに本文と台帳の両方を同期することになる。
- 台帳はレビュー状態の `review` block そのものとし、新しい field 名を導入しない。
  field 定義の正本は [プラン artifact](plan-artifacts.md) に置く。
  確定時は写し替えや構造変換を行わず、そのまま `review` の下へ置く。
- `review.findings` は全 round・全 reviewer 通算の台帳とする。指摘 ID（`PF-*`）は round をまたいで
  振り直さず、`reviewer` field で発行元を区別する。
- `resolution` は `adopted` / `rejected` のいずれかを指摘IDごとに記録する。`resolution: unresolved`
  を書けるのは `round-limit` で打ち切る場合だけである。
- 不採用（`rejected`）には理由を `resolution_note` に記録する。判断未記録の指摘を残したまま
  ループを終えない。

## evidence を欠く指摘の扱い

reviewer が示す evidence は
[Reviewer findings の共通契約](../../impl-lead/references/reviewer-findings.md) の
「指摘ごとの evidence」に従う。
evidence を欠く指摘だけを根拠にプランを修正しない。

親が該当ファイルと行の引用・再現手順・参照した Data の path と id のいずれかを、親自身が確認した
repository の現状・プラン文書・既存 manuscript から特定できる場合は、親が evidence を補って通常の
判断（`軽微` の定義への照合と `adopted` / `rejected` の判断）へ戻す。

evidence を補えない指摘は、指摘が成立したと仮定した場合の影響を影響基準に当てて verdict を確定した
うえで、指摘IDごとに不採用（理由: evidence 不足）として `review.findings` に記録する。

## 打ち切り条件

次のいずれかが成立した round でループを打ち切り、`review.termination` に記録する。

- `zero-findings`: その round の指摘が0件。
- `trivial-only`: 親が確定した verdict が全指摘で `軽微` のみとなる round が1回成立したとき。
  reviewer の申告ではなく親の確定 verdict で判定し、親が `修正推奨` 以上へ引き上げた指摘が1件でも
  あればループを継続する。打ち切る前に、軽微指摘にも指摘IDごとに `adopted` / `rejected` と理由を
  記録し、`unresolved` を残さない。
- `round-limit`: `rounds_completed` が `rounds_limit`（既定10）に到達したとき。

## 誘発指摘による収束

修正が新しい指摘を誘発し続ける経路を、台帳上で識別して有界に打ち切る。

- 親が確定した verdict に `修正必須` が1件もない最初の round を基準とし、
  `review.baseline_round` にその番号を記録する。いったん記録した基準は取り直さない。
- 誘発指摘は、基準プランには存在せず、基準以降に採用した修正が導入した記述を対象とする。基準 round
  自体は `induced` を記録せず、基準の次 round 以降の各 `plan-adversarial-reviewer` finding の
  `review.findings[].induced` に `true | false` を記録する。基準前の round は `induced` を記録しない（「基準なし round」は
  `induced` の記録なしを指す）。
- 基準の2 round後から毎 round、rolling の最新2つの `plan-adversarial-reviewer` round にある
  `修正推奨` 以上の finding だけを母数にする。`induced` が母数の半数を超える strict majority で、
  窓に非誘発の `修正必須` が含まれない場合に限り、`termination: induced-loop` を確定する。
  ちょうど半数は成立せず、窓に非誘発の `修正必須` が含まれる場合は次 round へ繰り越す。最新2つの窓を
  評価する。
- `induced-loop` を確定する round では、その round の採用指摘をプランへ反映してから打ち切る。
  `unresolved` は残さない。`induced-loop` の確定それ自体を理由に、採用修正に必要な範囲を超えて指摘を
  取り下げたり条項を追加削除したりしない。有界性は `round-limit` が担い、基準や多数決を理由に
  `rounds_limit` を変更しない。

## 過剰実装審査との接続

- adversarial の収束（`zero-findings`、`trivial-only`、または `induced-loop`）後に、`over-engineering-reviewer` を
  プラン入力モードで1回起動する（[過剰実装のプラン審査](overengineering-plan-review.md)）。これは adversarial の round
  計数対象外の必須最終ゲートであり、`rounds_completed` / `rounds_limit` を増やさない。最後の adversarial round で
  収束条件が成立してもこの1回を実行する。完了時に `overengineering_snapshot_round` へ
  `rounds_completed` を記録する。0 findings でも記録して完了とする。
- `over-engineering-reviewer` の finding の `round` は adversarial 収束時点の `rounds_completed`（確定 snapshot の番号）とする。
  その finding の `round` は `overengineering_snapshot_round` と一致する。reviewer field で同じ round の adversarial finding と
  区別する。採用修正後は追加の adversarial round を実行しない。
- 過剰実装審査の指摘を採用してプランを修正した場合は、adversarial レビューへ戻らず、修正済み
  プランでレビュー工程を終了する。過剰実装審査も再起動しない。採用した指摘を台帳へ記録し、
  その修正を反映した2 artifactを提示する。
- 過剰実装審査の指摘も同じ `PF-*` 台帳へ記録し、`reviewer: over-engineering-reviewer` で区別する。

## round-limit 時の提示

- `修正推奨` 以上の未対応指摘を `resolution: unresolved` として台帳に残す。
- 提示では、レビュー状態の YAML より前に未解決一覧（指摘ID・verdict・summary）を明示する。
- 確認モードが `auto` でも自動承認しない。未解決指摘の扱い（追加 round の明示指定、指摘の
  採用・不採用の確定、このまま承認）をユーザーに確定してもらう。
