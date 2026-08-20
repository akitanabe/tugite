<!-- @contract deletion-test-method-v1 -->
# Deletion Test Method v1

Deletion Test Method identity: `deletion-test-method-v1`.

この reference は、一つの識別された deletion candidate を仮想除去し、残る witness と obligation への影響だけを判定する reusable procedure である。Kernel ではない。Kernel identity と Kernel injection mapping を持たない。

正本はこのファイルであり、各 platform の配布物では `references/deletion-test-method.md` として生成される。caller は判定 procedure を複製しない。

## Inputs

入力は次に限る。

- **stable snapshot**
- **deletion candidate**
- **consumer-supplied obligations / constraints**
- **observable evidence**

snapshot と candidate は caller が識別する。obligation / constraint の意味と範囲も caller が供給する。Method は Target を定義せず、Task Specification を所有しない。

## Procedure

固定手順は次である。

1. 識別された deletion candidate だけを仮想的に除去した更新前提を置く。
2. 除去後に残る具体的な remaining witness を、observable evidence から確認する。
3. consumer-supplied obligations / constraints が壊れるかを確認する。

同じ selected batch 内の別 candidate を stable remaining witness とみなさない。A と B が互いを唯一の witness にする mutual witness は、両方の同時削除を `deletion preserves obligations` として認めない。mutual witness、evidence 不足、obligation 不明を独立した `preserves` に昇格させず、解消不能なら `indeterminate` とする。

判定対象を除去・採用する前に caller が候補を更新した場合は、更新後の stable snapshot で再判定する。古い snapshot の witness を更新後へ持ち越さない。

## Semantic Results

意味結果は次の3つで閉じる。

### `deletion preserves obligations`

除去後にも、残る具体的な remaining witness と、その witness が担保する obligation を特定できる。大きさ、複雑さ、行数、一般的な好みだけを根拠にしない。

### `deletion breaks obligations`

除去すると obligation が壊れ、具体的な Failure と Evidence を示せる。

### `indeterminate`

remaining witness、Broken Obligation、Failure、Evidence、または obligation 自体を確認できず、削除判定を安全に分類できない。mutual witness を解消できない場合も `indeterminate` とする。自動採用・自動却下をしない。

`deletion preserves obligations` / `deletion breaks obligations` / `indeterminate` は新共通 verdict field ではない。caller は既存の返却 Data を使い、親が既存の裁定語彙へ最終裁定する。

## Non-goals

Deletion Test Method は次を行わない。

- Target membership の判定
- scope admission
- accept / reject の裁定
- replacement design の提案
- workflow routing
- 複数 candidate や snapshot 全体を一括して「きれいにする」判断への置換
- Kernel identity または Kernel injection mapping の所有
<!-- @/contract -->
