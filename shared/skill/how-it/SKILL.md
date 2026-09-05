<!-- @only claude -->
---
name: how-it
description: >-
  明示起動の public consumer として、唯一の task-local Local Model から Interactive Model Construction を利用し、
  「どう進めるか／どう成立させるか」の current understanding を requested output へ直接接続する。
disable-model-invocation: true
---
<!-- @/only -->
<!-- @only codex -->
---
name: how-it
description: >-
  明示起動の public consumer として、唯一の task-local Local Model から Interactive Model Construction を利用し、
  「どう進めるか／どう成立させるか」の current understanding を requested output へ直接接続する。
---
<!-- @/only -->
<!-- @only cursor -->
---
name: how-it
description: >-
  明示起動の public consumer として、唯一の task-local Local Model から Interactive Model Construction を利用し、
  「どう進めるか／どう成立させるか」の current understanding を requested output へ直接接続する。
disable-model-invocation: true
---
<!-- @/only -->

# how-it
<!-- @anchor how-it-document-relation -->

`how-it` は、「これ、どうやろう？」という未確定な request を受け取り、必要な前提・選択肢・成立条件を Human とともに構築し、その current understanding を requested output へつなぐための明示起動の public workflow です。
計画だけに限定せず、探索や対話のための新しい architecture、汎用 framework、固定 report を定義しません。

## Identity and invocation

<!-- @contract how-it-explicit-invocation -->
<!-- @anchor how-it-explicit-invocation-relation -->
`how-it` は、明示的に起動されたときだけ利用する public workflow です。
<!-- @/contract -->

<!-- @contract how-it-ownership -->
<!-- @anchor how-it-ownership-relation -->
一回の invocation に対して `how-it` は exactly one の task-local Local Model を所有し、task scope、requested output、write authority も保持します。
<!-- @/contract -->

この Local Model は invocation の目的に局所化された ephemeral な意味構造です。Interactive Model Construction、Research Agent、観測処理は
第二の Local Model を所有せず、モデルの永続化、固定 schema、state machine、score、decision ledger も導入しません。

## Interactive Model Construction connection

<!-- @contract how-it-interactive-connection -->
<!-- @anchor how-it-interactive-connection-relation -->
`how-it` は既存の `Interactive Model Construction` を construction Method として利用します。
<!-- @/contract -->

Interactive 固有の意味、Agent-side resolution、Human interaction、必要な evidence acquisition、およびその completion boundary は、次の shared source に従います。
`how-it` は Interactive の内部 phase、Human question schema、completion 判定を別名で再実装せず、Method の選択・切り替え・順序と
workflow 全体の completion を caller として保持します。

生成された Skill から参照する既存の正本は次のとおりです。各 platform の generated path を基準に解決し、ここで package/plugin 相対 path の
探索規則を新設しません。

- `../../references/model-construction.md`
- `../../references/interactive-model-construction.md`
- `../../references/researcher-delegation.md`

## Human-facing decision support

<!-- @contract how-it-decision-support-boundary -->
<!-- @anchor how-it-decision-support-relation -->
Human-owned resolution を開始した後、`how-it` は caller-side の Human-facing decision support を担い、current understanding に応じて提示と選択を調整します。

decision context、比較対象・軸、選択肢、推奨と理由、提示順、tone を確定した後、Human へ提示する文章に `../../references/human-facing-projection.md` の共有 Method を対話用途で軽く適用します。選択・比較・推奨・構成と最終出力責任は `how-it` に残し、Interactive の入力分類、Reintegration、`ex`、final Human judgment は既存 Method の責務を維持します。
<!-- @/contract -->

<!-- @contract how-it-decision-context -->
原則は一問一答であり、一度に扱うのも原則として一つの独立した decision context です。これらは別の要件です。同じ decision context の解消に複数の問いが必要な場合は、一つの turn に複数の問いを含められ、固定した質問数は持ちません。
<!-- @/contract -->

<!-- @contract how-it-decision-selection -->
`how-it` は FIFO、事前に作った queue、固定 score で順番を決めず、より上位の判断、後続判断を多く消去または拘束すること、判断空間を安定させること、重要な不整合を解消することを基準に current decision context を選びます。
<!-- @/contract -->

<!-- @contract how-it-authority-presentation -->
Human authority judgment を求めるときは、比較可能性を保つため同一の対象・軸・抽象度の選択肢と主要差分を示し、圧縮した判断材料を添えます。提示の標準原則は選択肢を先にすることであり、推奨を選択肢より先にすることを標準にはしません。evidence が推奨を支える場合だけ理由付きで推奨し、必要な主要対案も示します。優劣が evidence から定まらない場合は、特定の案を誘導せず、選択を分ける中立な価値軸を示します。
<!-- @/contract -->

<!-- @contract how-it-response-reintegration -->
Human の response を既存の Interactive Reintegration に統合した後、dependency と remaining context を再評価します。不要となった context の除去、新たな context の追加、context の統合、必要な範囲の再構成、または completion を選べます。質問列の完遂を completion の条件にしません。
<!-- @/contract -->

<!-- @contract how-it-decision-continuity -->
evidence または premise の変化で優劣が変わった場合は、current context の推奨と理由を更新します。短い承認は、応答対象が一意に特定できる current context の採否だけに限定し、Local Model 全体、未提示の context、downstream artifact / plan の acceptance には拡張しません。context が不連続に切り替わる場合だけ、current understanding または遷移理由を最小限添え、確定済みの説明・前提・判断を毎 turn 定型的に繰り返しません。
<!-- @/contract -->

<!-- @contract how-it-decision-support-integrity -->
この caller-side support は fixed dialogue schema、fixed question sequence、pre-generated queue、fixed option count、score、decision ledger、Programmatic Flow を導入しません。
<!-- @/contract -->
<!-- @anchor how-it-decision-support-end-relation -->

## Reintegration and semantic effect

<!-- @contract how-it-reintegration -->
<!-- @anchor how-it-reintegration-relation -->
`how-it` は Interactive の result を、calling workflow が所有する同じ task-local Local Model に戻し、別の Local Model や独立した report state を作りません。
<!-- @/contract -->

Interactive の semantic-effect rule に従った result を受け取った後も、`how-it` は requested output の境界を維持します。

## Completion and requested output

<!-- @contract how-it-completion-output -->
<!-- @anchor how-it-completion-output-relation -->
`how-it` は Interactive の completion boundary を通過した current understanding と retained material uncertainty / qualification を requested output へ直接接続し、write authority は invocation 時点で明示された output / destination を越えません。

requested output の内容・構成・tone を確定した文章にも、`../../references/human-facing-projection.md` を実際の出力用途に応じて適用します。通常の説明はその用途、後から単独で判断根拠にする成果物は厳密な意味保持を基準とし、出力前の確認と最終出力責任は `how-it` が担います。
<!-- @/contract -->

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
- Planning、`plan-agent`、downstream artifact / plan の acceptance
- `how-it` による repository remediation、実装、scope expansion、未指定 write、または `shared/VERSION` の更新
