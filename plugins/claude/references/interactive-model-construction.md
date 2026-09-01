<!-- Generated from shared/. Do not edit directly. -->

# Interactive Model Construction

## Identity

`Interactive Model Construction` は、calling workflow が所有する task-local Local Model を、Model Construction Core に従って
Human-owned resolution route と final Human judgment boundary 付きで構築する shared Method である。

これは standalone public Skill ではない。共通の Local Model ownership、Model Observation、Exploration Projection、Gap Resolution、
Reintegration、Recomposition、bounded re-observation の意味は `model-construction.md` を正本とし、この文書では Interactive 固有の
Human boundary と completion boundary だけを定める。

## Ownership and shared Core

一回の top-level workflow invocation では、calling workflow が exactly one の task-local Local Model を所有する。Interactive Method は
独自の Local Model、Exploration Projection、observation architecture、persistent model、fixed schema、state machine、score を作らない。
Human response と Human judgment も、calling workflow の同じ Local Model に統合する。

calling workflow は Local Model、task scope、requested output、Method の選択・切り替え・順序、workflow 全体の completion と
downstream artifact / plan の acceptance を所有する。Interactive Method は assigned construction scope、Agent-side resolution first、
Human-owned resolution、同じ Local Model への Reintegration、必要な Recomposition / bounded re-observation、および current understanding
に対する final Human judgment boundary を所有する。

Model Observation、BMO、RMO、Research Agent は、それぞれ caller が与えた対象に対する観測または evidence acquisition の責務だけを持つ。
これらは Local Model の ownership / mutation、Human judgment、Reintegration、Recomposition、Method completion を所有しない。

## Agent-side resolution first

Exploration Projection から construction gap または qualification が観測された場合、Human に入力や判断を求める前に、Agent-side で
解消できる範囲を処理する。利用可能な route は、reasoning / analysis、available context、repository / source exploration、bounded な
Research Agent による evidence acquisition / local analysis である。Research Agent を使う場合の caller-side delegation と operation は
`researcher-delegation.md`、agent の evidence-relative boundary は `agents/researcher.md` に従う。

Agent が分からないこと、複数の案があること、Research Agent を利用できることだけでは Human interaction を開始しない。Agent-side の
resolution で得た grounded result は、task-wide な意味判断を外部へ移さず、Interactive Method が同じ Local Model へ Reintegration する。

Agent-side の bounded route を尽くしても material な gap が残り、その resolution source または binding authority が Human にある場合
だけ、Human-owned resolution を開始できる。Human interaction を、単なる不足感や推測の補強のために使わない。

## Human-owned resolution

Human interaction は現在の task / domain に必要な入力を、次の意味上異なる二つの source として扱う。

### Human-held fact / context

これは repository や利用可能な source から取得できず、Human だけが保持する、既に成立している factual / contextual premise である。
既存の外部前提、task に固有の context、外部の制約や history などが含まれる。Human が今回の task で選ぶ binding direction、scope、
authority はここに含めず、事実または文脈の source として扱う。

### Human authority judgment

これは preference、trade-off、direction、responsibility、scope、authority のように、Human authority が今回の task に対する binding
direction を選ぶ必要がある判断である。既に成立している technical fact / context とこの判断を混同せず、Human の approval や preference
を factual evidence として扱わない。
Human の判断は current task に対する binding input として同じ Local Model に統合するが、それだけを理由に未許可の operation や scope
expansion を始めない。

### Human-facing interaction

Human には、現在の task / domain language で判断対象、必要な理由、既知の前提、残る uncertainty または qualification を提示する。
Local Model、Exploration Projection、Projection Sufficiency、gap、Reintegration、Recomposition などの内部語彙の理解を質問の前提に
しない。固定された質問 schema、question queue、dialogue state machine、decision ledger で task-specific な判断を置き換えない。

## Reintegration and semantic effect

Human response または judgment は結果として扱い、calling workflow が所有する同じ task-local Local Model へ Reintegration する。応答が
返ったこと自体は Recomposition の trigger ではない。Reintegration 後に semantic effect を評価し、必要な範囲だけを更新する。

- current semantics が維持される、または non-material な局所更新で足りる場合は、同じ Local Model の local repair / Reintegration と
  必要な bounded re-observation だけを行う。
- material な semantic region が invalidated した場合だけ、affected region とその dependency を Recomposition する。same Local
  Model を継続し、unaffected semantics、boundaries、decisions を保持し、修復後に affected semantics だけを bounded に再観測する。

新しい Human information を stale understanding への追記として残さず、影響を受けた意味を current evidence / judgment に合わせて更新する。
Human response、correction、missing premise、unresolved concern の semantic effect が不明な場合は、unknown を確定事実へ変換せず、必要な
uncertainty を保持したまま追加の判断または確認へ戻す。

## Final Human judgment and completion

Agent-side resolution、Human response の Reintegration、必要な repair と bounded re-observation の後、Interactive Method は current
understanding と retained material uncertainty / qualification を Human が判断できる形で提示する。

Human がその current understanding を downstream の前提として採用し、次へ進むことを明示的に認めるまで、Interactive Method は completion
しない。これは current understanding の acceptance であり、downstream plan や artifact 自体の acceptance ではない。uncertainty を残した
状態で進む判断は可能だが、Human の approval によって unknown fact を known fact に変えない。

Human が correction、missing premise、または unresolved concern を返した場合は、同じ Local Model へ再度 Reintegration し、semantic effect
に応じて local repair または affected region の Recomposition と bounded re-observation を行ったうえで、current understanding の final
Human judgment を取り直す。

## Method composition

Interactive Model Construction 自身は Agentic Model Construction を起動しない。Agentic から Interactive への switching、Method の順序、
および複数 Method を同じ invocation で組み合わせる判断は calling workflow が所有する。

```text
calling workflow
  → Method selection / switching / order

Agentic Model Construction
  ✕ autonomous Interactive fallback

Interactive Model Construction
  ✕ autonomous Agentic invocation
```

Interactive Method は、`explorer-this`、`how-it`、または任意の downstream workflow を自律的に起動しない。

## Non-goals

- Model Construction Core、Agentic Model Construction、Model Observation の redesign
- standalone public Skill、platform invocation metadata、plugin manifest、generic Human interaction framework
- fixed dialogue schema、state machine、question queue、decision ledger
- Interactive 専用 Research Agent、Human による探索 architecture、または独自の Local Model / projection
- Method switching、`explorer-this` からの fallback、`how-it`、Planning Synthesis、downstream artifact / plan の acceptance
- Human approval による unknown fact の確定、または materiality を無視した全域 Recomposition
