<!-- @contract necessity-kernel-v1 -->
# Necessity Kernel v1

Kernel identity: `necessity-kernel-v1`.
Kernel dependencies: `none`.

この共有規範は、reviewer または advisor が返す observation / evidence から導かれた候補を、現在の
Task Specification に対する必要性で裁定するための最小規範である。正本はこのファイルであり、各 platform
の配布物では `references/necessity-kernel.md` として生成される。各 role は全文を複製せず、この規範との
自分の既存返却形式への mapping だけを持つ。parent は package reference を読み、role には既存の
判定基準または必要な周辺 context の一部として identity / 必要な本文を渡す。

## 適用範囲

v1 の適用対象は `plan-adversarial-reviewer`、`over-engineering-reviewer`、`plan-quality-advisor` と、
それらを呼び出す `proposal` / `plan-craft-approval` / `review-loop` の既存 parent responsibility に限る。
`structural-health-gate 適用外`。gate の意味、assessment、caller contract を
この規範で変更しない。

## Task Specification

判定に使う Task Specification は、次の観測可能な Data を含む。

- `requested outcome`（要求された成果）
- 明示AC（Acceptance Criteria）
- `scope` / `exclude` / `constraints` / `verification`
- 適用される既存仕様
- 公開/外部観測動作
- 外部契約/API
- repository invariant
- サポート対象入力/状態/環境

Task Specification field group: scope/exclude/constraints/verification.

Task Specification は current task の受入境界である。一般的に有用/将来有用だけの改善、きれいさ、網羅性、
将来の拡張余地を Task Specification に含めない。不足または矛盾が判定を変える場合、推測で埋めず既存の親の停止・
確認経路へ返す。

## Claim と evidence

`Claim` は finding / insight 本文そのものではなく、candidate snapshot に追加、維持、変更、除去、検証、
調査する候補 obligation である。finding / insight は observation、evidence、necessity basis として
Claim の根拠を示す。test / log / measurement / investigation / additional review の実施も、必要なら
それ自体を Claim として扱うが、現在の Task Specification を破らない限り暗黙に scope へ追加しない。
Claim basis fields: observation/evidence/necessity basis.

## Deletion Test

Deletion Test は、一つの識別された candidate snapshot と、一つの Claim に対して適用する。複数 Claim や
snapshot 全体を一括して「きれいにする」判断に置き換えない。

1. Claim が担う obligation、候補を除去した場合の Failure、観測された Evidence、必要な
   Minimum Resolution Condition を既存 Data から特定する。
2. 候補だけを仮想的に除去した更新前提を置き、Task Specification の obligation が壊れるかを確認する。
3. 次のいずれかへ分類し、既存 role の返却 field と parent の語彙へ写像する。

### `necessary`

除去すると Broken Obligation が生じ、具体的な Failure と Evidence があり、親が満たすべき Minimum
Resolution Condition を示せる。role は Minimum Form（最小の実現形）を決めず、親が既存の責務内で決める。

### `unnecessary`

除去後にも、残る具体的な `remaining witness` と、その witness が担保する obligation を特定できる。
大きさ、複雑さ、行数、一般的な好みだけを根拠にしない。A と B が互いを唯一の witness にする場合は、
両方の同時削除を `unnecessary` として認めない（mutual deletion guard）。

### `indeterminate`

Broken Obligation、Failure、Evidence、Minimum Resolution Condition、または remaining witness を確認
できず、必要性を安全に分類できない。自動採用・自動却下をせず、既存の `unresolved` / `判断保留` /
`人間確認`、または安全な candidate を作れない場合の `stop-incomplete` に写像する。

`necessary` / `unnecessary` / `indeterminate` は新共通 verdict field ではない。plan-adversarial-reviewer
は既存 finding Data、over-engineering-reviewer は既存 finding Data、plan-quality-advisor は既存 insight
Data を返し、親が既存の `adopted` / `rejected` / `unresolved` または `採用` / `却下` / `範囲外` /
`判断保留` / `人間確認` へ最終裁定する。severity、Pass、件数をこの分類へ直結しない。

判定対象を除去・採用する前に、親が候補を更新した場合は `updated snapshot` を識別し、その snapshot で
Deletion Test を再判定する。古い snapshot の witness を更新後へ持ち越さない。
成果物更新後は、必ず更新された snapshot を判定対象にする。

## 発見と追加の境界

`discovered != admitted`。新発見の問題は Claim になり得るが、発見しただけで admitted にはならない。
evidence collection（test、log、measurement、investigation、additional review）も必要性を判定し、
Task Specification の scope を親の裁定なしに拡張しない。

### Stop Adding Rule

必要または indeterminate の未処理 Claim がなく、Task Specification を受入可能な evidence が揃ったら、
綺麗さ、網羅性、将来性、厳密さだけを理由に Task Specification 外の Claim や work を追加しない。この Rule は
Claim / work の current Task Specification への追加可否だけを扱い、workflow の進行や停止を要求・決定せず、存在しない
ことの証明も要求しない。新 Claim の探索を要求せず、親が保持する既存の責務と語彙へ返す。
<!-- @/contract -->
