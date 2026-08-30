---
name: plan-agent
description: >-
  明示起動の public planning workflow として、唯一の task-local Local Model を Agentic Model Construction で構築し、
  workflow-local な planning direction を共通 Planning Core へ渡して、検証済み Plan candidate または incomplete を返す。
disable-model-invocation: true
---
<!-- Generated from shared/. Do not edit directly. -->

# plan-agent

`plan-agent` は、Agent-side で planning authority を確立し、共通の Planning Core から検証済み Plan candidate を得る、明示起動の
public planning workflow です。別の planning engine、固定 Plan schema、または Planning Core の局所コピーを持ちません。

## Identity and ownership

入力は invocation の request、利用可能な context、planning artifact の出力先と write authority です。

`plan-agent` は一回の top-level invocation に対して exactly one の task-local Local Model を所有し、Agentic Model Construction とすべての downstream planning consumer はその projection を利用します。

Local Model は current task に局所化された ephemeral な意味構造です。Planning Core、Planning Synthesis、nested `review-refine`、advisor、
reviewer は独立した Local Model を作らず、workflow completion、planning authority、artifact の出力責任も引き取りません。

生成された Skill から参照する既存の正本は次のとおりです。各 platform の generated path を基準に解決します。

- `../../references/model-construction.md`
- `../../references/agentic-model-construction.md`
- `../../references/planning-core.md`

## Agentic construction and direction

`plan-agent` は Agentic Model Construction を利用して、request に対する current understanding と planning-relevant projection を構築します。
Agent-side で利用可能な reasoning、context、repository / source observation、許可された evidence acquisition を使い、material な gap を
推測で埋めません。

Agentic Model Construction の completion 後、`plan-agent` は current task の planning direction を workflow-local judgment として確立し、shared Method、固定 schema、persistent artifact、lifecycle object へ昇格させません。

direction の判断には current understanding、request authority、constraints、resolved evidence を使います。複数の受容可能な方向から current
task に適したものを選ぶ意味判断は `plan-agent` に残し、Planning Core や reviewer に選択責任を移しません。

Agentic Model Construction が material blocking gap により qualified stop した場合、`plan-agent` は reason と unresolved gap を保った `incomplete` を返し、Interactive fallback、Planning Core invocation、speculative direction の選択を行いません。

qualified stop 後に Interactive workflow で再開するかは caller または Human が別 invocation として決めます。`plan-agent` は
`plan-interactive` や Interactive Model Construction を fallback として起動しません。

## Planning Core connection

`plan-agent` は planning-relevant Local Model projection、established direction、authority constraints、resolved upstream evidence を共通の Planning Core へ渡します。

Planning Core が所有する Planning Synthesis、S0 baseline preparation、nested review、mandatory reviewer topology、verification、result mapping を
`plan-agent` 内で再実装しません。direction と authority constraints は downstream obligation であり、Planning Core の consumer が別の
direction へ変更するための suggestion ではありません。

## Result and completion

`plan-agent` は Planning Core の final verified Plan candidate、または safest available candidate と material reason を持つ `incomplete` を受け取ったまま返し、後処理で candidate を変更しません。

Planning Core が candidate 成立前の `incomplete` を返した場合は candidate を捏造しません。返却後の polish、normalization、reformat、
serialization、追記は未レビュー差分になるため行いません。Interactive な最終承認をこの workflow の必須完了条件として追加しません。

`plan-agent` の completion は planning artifact の返却までであり、implementation、delegation、Issue / PR 更新、downstream workflow を開始しません。

write は invocation で指定された planning artifact または destination に限ります。計画中に見つけた別の repository finding は、現在の Plan の
scope や qualification に関係する範囲で扱えますが、新しい implementation authority にはなりません。

## Non-goals

- Interactive Model Construction または `plan-interactive` への autonomous fallback
- Planning Synthesis、Planning Core、`review-refine`、reviewer topology の複製
- planning direction の shared Method、固定 schema、persistent authority artifact、lifecycle state への昇格
- second Local Model、Local Model serialization、downstream consumer への ownership 移譲
- candidate の post-review mutation、第二の planning engine、固定 Plan schema
- implementation、delegation、Issue / PR 操作、release、または downstream workflow の開始
