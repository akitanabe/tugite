# Interactive Model Construction
<!-- @anchor shared-interactive-document -->

## Identity

`Interactive Model Construction` は、calling workflow が選んだ assigned semantic scope を、Model Construction Core に従って
Human と共同構築し、calling workflow が所有する task-local Local Model へ返す shared Method である。

これは standalone public Skill ではない。共通の Local Model ownership、Model Observation、Exploration Projection、Gap Resolution、
Reintegration、Recomposition、bounded re-observation の意味は `model-construction.md` を正本とし、この文書では Interactive 固有の
Human input、scope 内の共同構築、completion boundary だけを定める。

## Ownership and shared Core

一回の top-level workflow invocation では、calling workflow が exactly one の task-local Local Model を所有する。Interactive Method は
独自の Local Model、Exploration Projection、observation architecture、persistent model、fixed schema、state machine、score を作らない。
Human response と Human judgment も、calling workflow の同じ Local Model に統合する。

calling workflow は Local Model、task scope、requested output、Interactive に渡す assigned semantic scope、Human に聞く必要性、
Method の選択・切り替え・順序、workflow 全体の completion と downstream artifact / plan の acceptance を所有する。Interactive Method は
渡された scope 内で Human-held fact / context と Human authority judgment を区別し、Human と意味を共同構築して同じ Local Model へ
Reintegration し、必要な Recomposition / bounded re-observation を経た result / qualification または unresolved scope を caller に返す。

Model Observation、BMO、RMO、Research Agent は、それぞれ caller が与えた対象に対する観測または evidence acquisition の責務だけを持つ。
これらは Local Model の ownership / mutation、Human judgment、Reintegration、Recomposition、Method completion を所有しない。

## Assigned semantic scope

<!-- @contract shared-interactive-assigned-scope -->
<!-- @anchor shared-interactive-assigned-scope-relation -->
Interactive は caller-selected assigned semantic scope を入力として受け、その scope を再審査、拡張、縮小せず、scope 内で必要な
Human input と複数 turn の共同構築を扱う。caller が渡していない task-wide gap、workflow completion、downstream artifact の acceptance を
Interactive の completion 対象に含めない。
<!-- @/contract -->

## Human-owned resolution

Human interaction から現在の task / domain に必要な semantic input を得る場合、その入力は次の意味上異なる二つの source として扱う。

<!-- @contract shared-interactive-human-boundary -->
<!-- @anchor shared-interactive-human-relation -->
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

<!-- @/contract -->

## Reintegration and semantic effect

<!-- @contract shared-interactive-reintegration -->
<!-- @anchor shared-interactive-reintegration-relation -->
Human interaction から得た Human-held fact / context または Human authority judgment は result として扱い、calling workflow が所有する同じ
task-local Local Model へ Reintegration する。semantic input が返ったこと自体は Recomposition の trigger ではない。Reintegration 後に
semantic effect を評価し、必要な範囲だけを更新する。
<!-- @/contract -->

- current semantics が維持される、または non-material な局所更新で足りる場合は、同じ Local Model の local repair / Reintegration と
  必要な bounded re-observation だけを行う。
- material な semantic region が invalidated した場合だけ、affected region とその dependency を Recomposition する。same Local
  Model を継続し、unaffected semantics、boundaries、decisions を保持し、修復後に affected semantics だけを bounded に再観測する。

新しい Human information を stale understanding への追記として残さず、影響を受けた意味を current evidence / judgment に合わせて更新する。
Human response、correction、missing premise、unresolved concern の semantic effect が不明な場合は、unknown を確定事実へ変換せず、必要な
uncertainty を保持したまま追加の判断または確認へ戻す。

## Completion

<!-- @anchor shared-interactive-completion-relation -->
<!-- @contract shared-interactive-fact-completion -->
Human-held fact / context だけを含む assigned scope は、正しい Reintegration と必要な更新・再観測により解消した時点で result / qualification を
caller に返し、追加の Human approval を completion 条件にしない。
<!-- @/contract -->

<!-- @contract shared-interactive-authority-completion -->
Human authority judgment を含む assigned scope は、必要な更新・再観測後、その scope の current understanding と qualification に対する
final Human judgment を得てから result を caller に返す。この judgment を workflow 全体、downstream artifact、plan、最終 Work Units の acceptance へ広げない。
<!-- @/contract -->

Human が correction、missing premise、または unresolved concern を返した場合は同じ assigned scope に戻し、同じ Local Model への
Reintegration、必要な local repair または affected region の Recomposition と bounded re-observation を続ける。scope が解消できない場合は、
unresolved scope と retained qualification を caller に返す。Human の approval によって unknown fact を known fact に変えない。

## Method composition

<!-- @contract shared-interactive-composition -->
<!-- @anchor shared-interactive-composition-relation -->
Interactive Model Construction 自身は Agentic Model Construction を起動しない。Agentic から Interactive への switching、Method の順序、
および複数 Method を同じ invocation で組み合わせる判断は calling workflow が所有する。
<!-- @/contract -->

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
- Human に聞く必要性の判断、Agent-side resolution、対話の presentation、`ex`、Method switching、`how-it`、Planning Synthesis、downstream artifact / plan の acceptance
- Human approval による unknown fact の確定、または materiality を無視した全域 Recomposition
