---
name: explorer-this
description: >-
  明示起動の public exploration workflow として、唯一の task-local Local Model から Agentic Model Construction を利用し、
  requested output へ直接接続し、解消不能な material gap では qualified stop する。
---
<!-- Generated from shared/. Do not edit directly. -->

# explorer-this

`explorer-this` は、明示的に起動されたときだけ利用する v7 の public exploration workflow です。探索のための別の
architecture や汎用 framework を定義せず、caller が求めた explanation、comparison、analysis、repository overview、
investigation result、または artifact へ直接つなぎます。

## Identity and invocation

入力は invocation の request、利用可能な context、そしてその時点で明示された output / write authority です。`explorer-this`
は一つの top-level workflow invocation に対して exactly one の task-local Local Model を所有します。

この Local Model は invocation の目的に局所化された ephemeral な意味構造です。Skill は Local Model を永続化・共有せず、
固定 schema、固定 state machine、score、または第二の Local Model を導入しません。Exploration Projection は同じ Local Model
に対する bounded な観測結果であり、別の model や workflow completion の代替ではありません。

## Ownership and Core connection

`explorer-this` は calling workflow として Local Model、caller context / authority、requested output、workflow 全体の
completion または qualified stop を所有します。Model Construction の意味、Agentic Model Construction の解消責務、Model
Observation の一般理論はそれぞれの既存の正本に委ねます。

現在の request に対して、`explorer-this` は Agentic Model Construction を利用し、必要な範囲で Model Observation、
Exploration Projection、Projection Sufficiency、gap resolution、Reintegration、または material な invalidation に対する
Recomposition と bounded re-observation へ接続します。Projection Sufficiency は Local Model の completeness、workflow の
readiness、または Reality の completeness を意味しません。

BMO / RMO は observation の意味上必要な場合だけ利用します。どちらも mandatory phase、固定順序、または workflow 全体の
completion 判定にはしません。

生成された Skill から参照する既存の正本は次のとおりです。各 platform の generated path を基準に解決し、ここで Core や
package/plugin 相対 path の探索規則を新設しません。

- `../../references/model-construction.md`
- `../../references/agentic-model-construction.md`
- `../../references/behavior-model-observation.md`
- `../../references/reality-model-observation.md`
- `../../references/research-agent-delegation.md`

## Optional evidence acquisition

repository、source、比較対象、または execution-based evidence の取得に bounded な委譲が有用な場合、caller は既存の
Research Agent delegation boundary に従って current platform の Research Agent を利用できます。caller は objective、scope、
authority、relevant context / evidence surface をその invocation の目的に合わせて与えます。

Research Agent は evidence acquisition と局所的な evidence-relative judgment を返して待機します。task-wide な materiality、
task direction、scope、Local Model、Exploration Projection、Reintegration、Recomposition、workflow continuation、completion、
implementation、または remediation は caller が所有します。返却された observation、inference、limitation、unresolved point を
区別し、必要な場合は同じ Local Model へ Reintegration してから後続の判断を行います。

新しい evidence が current understanding の material な意味領域を invalidation した場合だけ、その影響範囲を caller が
Recomposition し、affected semantics を bounded に再観測します。古い understanding と更新後の意味を並存させません。

## Requested output and write authority

内部の探索結果を `explorer-this` 固有の固定 report schema や固定 gap schema に変換しません。出力の内容と形式は invocation
で要求された成果に従い、current understanding をその requested output へ直接接続します。

write は invocation 時点で明示された requested artifact または destination の範囲に限ります。探索中に別の改善点が見つかっても、
その finding だけを理由に repository write authority、task scope、source / test / config の変更、implementation、または
remediation を開始しません。finding は requested output の内容や qualification には反映できますが、新しい authority にはなりません。

## Completion and qualified stop

許可された agent-side reasoning、利用可能な context、repository / source exploration、Research Agent による bounded evidence
acquisition を通じて current understanding が request を満たし、material な blocking gap が残らない場合、requested output
へ接続して完了します。

それらの解消経路を使っても material な blocking gap が残る場合、plausible inference で埋めず、現在の understanding、未解消の
gap、試した resolution basis、limitation、qualification を caller に返して停止します。Phase 3 のこの Skill は Human question、
Interactive Model Construction、`whats-this`、または Interactive fallback を開始しません。

## Non-goals

- Interactive Model Construction、Human resolution route、`whats-this`、または `explorer-this` からの Interactive fallback
- Planning Synthesis、`plan-agent`、`plan-interactive`
- fixed exploration workflow、universal exploration report、fixed input / output / gap schema
- generic exploration framework または generic public Skill framework
- autonomous repository remediation と exploration finding による authority expansion
