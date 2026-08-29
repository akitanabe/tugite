---
name: whats-this
description: >-
  明示起動の public consumer として、唯一の task-local Local Model から Interactive Model Construction を利用し、
  current understanding を requested output へ直接接続する。
---
<!-- Generated from shared/. Do not edit directly. -->

# whats-this

`whats-this` は、要求された事柄を理解し、その current understanding を要求された出力へつなぐための明示起動の public workflow です。
探索や対話のための新しい architecture、汎用 framework、固定 report を定義しません。

## Identity and invocation

`whats-this` は、明示的に起動されたときだけ利用する public workflow です。

一回の invocation に対して `whats-this` は exactly one の task-local Local Model を所有し、task scope、requested output、write authority も保持します。

この Local Model は invocation の目的に局所化された ephemeral な意味構造です。Interactive Model Construction、Research Agent、観測処理は
第二の Local Model を所有せず、モデルの永続化、固定 schema、state machine、score、decision ledger も導入しません。

## Interactive Model Construction connection

`whats-this` は既存の `Interactive Model Construction` を construction Method として利用します。

Interactive 固有の意味、Agent-side resolution、Human interaction、必要な evidence acquisition、およびその completion boundary は、次の shared source に従います。
`whats-this` は Interactive の内部 phase、Human question schema、completion 判定を別名で再実装せず、Method の選択・切り替え・順序と
workflow 全体の completion を caller として保持します。

生成された Skill から参照する既存の正本は次のとおりです。各 platform の generated path を基準に解決し、ここで package/plugin 相対 path の
探索規則を新設しません。

- `../../references/model-construction.md`
- `../../references/interactive-model-construction.md`
- `../../references/researcher-delegation.md`

## Reintegration and semantic effect

`whats-this` は Interactive の result を、calling workflow が所有する同じ task-local Local Model に戻し、別の Local Model や独立した report state を作りません。

Interactive の semantic-effect rule に従った result を受け取った後も、`whats-this` は requested output の境界を維持します。

## Completion and requested output

`whats-this` は Interactive の completion boundary を通過した current understanding と retained material uncertainty / qualification を requested output へ直接接続し、write authority は invocation 時点で明示された output / destination を越えません。

current understanding の acceptance と downstream artifact / plan の acceptance は分けます。
出力は explanation、comparison、analysis、repository overview、investigation result、または invocation が明示した artifact など、要求された
成果へ直接つなぎます。探索中に別の finding が見つかっても、それだけで task scope、repository write authority、implementation、remediation を
拡張しません。指定された出力の qualification に反映できない変更は行いません。

Human が correction、missing premise、または unresolved concern を返した場合は、既存の Interactive Method へ再接続し、同じ Local Model と
requested output の境界を維持します。

## Non-goals

- Model Construction Core、Interactive Model Construction、Agentic Model Construction、Model Observation の redesign
- `explorer-this` の変更、`explorer-this` からの Interactive fallback、または新しい clarification / dialogue / exploration architecture
- generic router、generic workflow framework、汎用 public Skill framework
- fixed dialogue schema、state machine、question queue、decision ledger、Interactive 専用 Local Model / Research Agent / projection
- Planning、`plan-agent`、`plan-interactive`、downstream artifact / plan の acceptance
- `whats-this` による repository remediation、実装、scope expansion、未指定 write、または `shared/VERSION` の更新
