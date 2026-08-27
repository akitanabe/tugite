<!-- @only claude -->
---
name: whats-this
description: >-
  明示起動の public consumer として、唯一の task-local Local Model から Interactive Model Construction を利用し、
  current understanding を requested output へ直接接続する。
disable-model-invocation: true
---
<!-- @/only -->
<!-- @only codex -->
---
name: whats-this
description: >-
  明示起動の public consumer として、唯一の task-local Local Model から Interactive Model Construction を利用し、
  current understanding を requested output へ直接接続する。
---
<!-- @/only -->
<!-- @only cursor -->
---
name: whats-this
description: >-
  明示起動の public consumer として、唯一の task-local Local Model から Interactive Model Construction を利用し、
  current understanding を requested output へ直接接続する。
disable-model-invocation: true
---
<!-- @/only -->

# whats-this
<!-- @anchor whats-this-document-relation -->

`whats-this` は、要求された事柄を理解し、その current understanding を要求された出力へつなぐための明示起動の public workflow です。
探索や対話のための新しい architecture、汎用 framework、固定 report を定義しません。

## Identity and invocation

<!-- @contract whats-this-explicit-invocation -->
<!-- @anchor whats-this-explicit-invocation-relation -->
`whats-this` は、明示的に起動されたときだけ利用する public workflow です。
<!-- @/contract -->

<!-- @contract whats-this-ownership -->
<!-- @anchor whats-this-ownership-relation -->
一回の invocation に対して `whats-this` は exactly one の task-local Local Model を所有し、task scope、requested output、write authority も保持します。
<!-- @/contract -->

この Local Model は invocation の目的に局所化された ephemeral な意味構造です。Interactive Model Construction、Research Agent、観測処理は
第二の Local Model を所有せず、モデルの永続化、固定 schema、state machine、score、decision ledger も導入しません。

## Interactive Model Construction connection

`whats-this` は既存の `Interactive Model Construction` を construction Method として利用します。Interactive 固有の Human boundary、
semantic effect、completion の意味は、次の shared source に委ねます。

<!-- @contract whats-this-interactive-connection -->
<!-- @anchor whats-this-interactive-connection-relation -->
`whats-this` は既存の `Interactive Model Construction` を Method として利用し、Agent-side の bounded resolution を先に行います。Agent が単に分からない、または複数案があるというだけでは Human interaction を始めません。material な gap の resolution source または binding authority が Human にある場合だけ、Human-owned resolution に接続します。
<!-- @/contract -->

Agent-side の route には reasoning / analysis、利用可能な context、repository / source exploration、必要な bounded Research Agent による
evidence acquisition を含められます。Research Agent を使う場合も、既存の `research-agent-delegation.md` の caller boundary に従い、
evidence の acquisition と task-relative な判断を分離します。`whats-this` は Interactive の内部 phase、Human question schema、completion
判定を別名で再実装せず、Method の選択・切り替え・順序と workflow 全体の completion を caller として保持します。

生成された Skill から参照する既存の正本は次のとおりです。各 platform の generated path を基準に解決し、ここで package/plugin 相対 path の
探索規則を新設しません。

- `../../references/model-construction.md`
- `../../references/interactive-model-construction.md`
- `../../references/research-agent-delegation.md`

## Reintegration and semantic effect

<!-- @contract whats-this-reintegration -->
<!-- @anchor whats-this-reintegration-relation -->
`whats-this` は Human response または judgment を Interactive の result として受け取り、別の Local Model や独立した report state を作らず、calling workflow の同じ task-local Local Model に戻します。Recomposition と re-observation の要否は既存の `Interactive Model Construction` の semantic-effect rule に従い、応答の到着だけを理由に全域を再構成しません。
<!-- @/contract -->

Interactive の semantic-effect rule に従った result を受け取った後も、`whats-this` は同じ Local Model と requested output の境界を維持します。

## Completion and requested output

<!-- @contract whats-this-completion-output -->
<!-- @anchor whats-this-completion-output-relation -->
`whats-this` は Interactive の final Human judgment boundary を通過した current understanding と retained material uncertainty / qualification を、Human が downstream の前提として採用できる形で扱います。current understanding の acceptance と downstream artifact / plan の acceptance は分け、Human approval は unknown fact を known fact に変えず、requested output へ直接接続し、write authority は invocation 時点で明示された output / destination を越えません。
<!-- @/contract -->

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
