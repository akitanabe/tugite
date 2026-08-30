---
name: plan-interactive
description: >-
  明示起動の public planning workflow として、唯一の task-local Local Model を Interactive Model Construction で構築し、
  Human-confirmed direction と constraints を共通 Planning Core へ渡して、検証済み Plan candidate または incomplete を返す。
---
<!-- Generated from shared/. Do not edit directly. -->

# plan-interactive

`plan-interactive` は、Human と current understanding と planning authority を確立し、共通の Planning Core から検証済み Plan candidate を
得る、明示起動の public planning workflow です。別の planning engine、固定 dialogue / Plan schema、または Planning Core の局所コピーを
持ちません。

## Identity and ownership

入力は invocation の request、利用可能な context、planning artifact の出力先と write authority です。

`plan-interactive` は一回の top-level invocation に対して exactly one の task-local Local Model を所有し、Interactive Model Construction とすべての downstream planning consumer はその projection を利用します。

Local Model は current task に局所化された ephemeral な意味構造です。Planning Core、Planning Synthesis、nested `review-refine`、advisor、
reviewer は独立した Local Model を作らず、workflow completion、Human interaction、planning authority、artifact の出力責任も引き取りません。

生成された Skill から参照する既存の正本は次のとおりです。各 platform の generated path を基準に解決します。

- `../../references/model-construction.md`
- `../../references/interactive-model-construction.md`
- `../../references/planning-core.md`

## Interactive construction and authority

`plan-interactive` は Interactive Model Construction を利用し、Agent-side resolution を先に行った current understanding に対して、Human だけが
持つ material fact / context または binding authority judgment を一度に一つずつ解決します。Human response は同じ Local Model へ
Reintegration し、material な invalidation がある範囲だけを Recomposition します。

Interactive Model Construction の completion で、`plan-interactive` は Human-confirmed current understanding、planning direction、constraints を current invocation の downstream authority obligations として確立します。

Human-confirmed authority は current invocation に局所化された semantic Data です。固定 authority schema、persistent artifact、decision ledger、
lifecycle object、または別の shared Method へ昇格させません。Interactive Model Construction の completion 前に不明な direction を推測して
Planning Core へ進みません。

## Planning Core connection

`plan-interactive` は planning-relevant Local Model projection、Human-confirmed direction、authority constraints、resolved upstream evidence を共通の Planning Core へ渡します。

Planning Core が所有する Planning Synthesis、S0 baseline preparation、nested review、mandatory reviewer topology、verification、result mapping を
`plan-interactive` 内で再実装しません。

Planning Core とその consumer は Human-confirmed direction の内側で判断し、direction や constraints を変更、拡張、緩和、置換せず、review finding を新しい authority にしません。

Planning Synthesis、advisor、nested `review-refine`、reviewer は established authority の内側で複数の受容可能な planning decision を選べますが、
Human-confirmed authority の再解釈や別方向への切り替えは行いません。

downstream planning が current Human-confirmed authority 内で安全に完了できない場合、`plan-interactive` は direction を変えず `incomplete` を返し、独立した Authority Integrity Verification checker を追加しません。

authority は caller と downstream consumer の ownership boundary で保護します。post-hoc checker、第二の quality gate、または review finding による
authority expansion で代替しません。

## Human and result boundaries

Interactive Model Construction の final Human judgment は planning direction と constraints を確立する境界であり、final Plan artifact の acceptance や Planning Core 後の第二の mandatory Human acceptance ではありません。

caller が別の Human review を明示的に要求した場合は、この workflow の canonical completion とは別の higher-level orchestration として扱います。

`plan-interactive` は Planning Core の final verified Plan candidate、または safest available candidate と material reason を持つ `incomplete` を受け取ったまま返し、後処理で candidate を変更しません。

Planning Core が candidate 成立前の `incomplete` を返した場合は candidate を捏造しません。返却後の polish、normalization、reformat、
serialization、追記は未レビュー差分になるため行いません。

`plan-interactive` の completion は planning artifact の返却までであり、implementation、delegation、Issue / PR 更新、downstream workflow を開始しません。

write は invocation で指定された planning artifact または destination に限ります。対話や計画中の finding は新しい implementation authority、
repository remediation、または scope expansion の根拠になりません。

## Non-goals

- Planning Synthesis、Planning Core、`review-refine`、reviewer topology の複製
- Authority Integrity Verification、post-hoc authority gate、第二の mandatory Human acceptance
- Human-confirmed direction の変更、拡張、緩和、置換、または finding からの authority 生成
- fixed dialogue / direction / Plan schema、persistent authority artifact、decision ledger、lifecycle state
- second Local Model、Local Model serialization、downstream consumer への ownership 移譲
- candidate の post-review mutation、第二の planning engine
- implementation、delegation、Issue / PR 操作、release、または downstream workflow の開始
