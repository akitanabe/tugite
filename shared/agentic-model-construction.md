# Agentic Model Construction
<!-- @anchor shared-agentic-document -->

<!-- @contract shared-agentic-human-boundary -->
<!-- @anchor shared-agentic-human-relation -->
## Identity

`Agentic Model Construction` は、Model Construction Core を追加の Human interaction なしで実行し、Agent が利用可能な context、repository、observation、research によって task-local Local Model を構築する shared Method である。

standalone public Skill にはしない。

`Agentic` は Human-derived information を禁止する意味ではない。request 時点ですでに与えられている Human context / constraint / direction は通常の input として利用できる。違いは construction 中に新しい Human interaction channel を開始しないことである。
<!-- @/contract -->

## Shared Core

Agentic は独自の探索 architecture を持たず、共通 Core を利用する。

共通 semantics と責任境界の正本は同じ directory の `model-construction.md` とする。current Local Model の観測から Reintegration / Recomposition、bounded re-observation までを実行するときはその Core に従い、この文書は Agentic 固有の resolution route、Human boundary、completion / qualified stop だけを specialize する。

## Gap Resolution

Exploration Projection 上の current gap について、Agent-side で利用可能な resolution route を bounded に選ぶ。

### Direct Agent-side Resolution

利用可能な context、repository、既知 evidence、analysis / inference で解消できる gap は Method 自身が解消する。

### Research Agent Delegation

bounded な evidence acquisition / local analysis を context-isolated に委譲する価値があり、caller / runtime が actual Research Agent を
利用可能にした場合は resolution route として選ぶ。caller input、operation authority、retry、cleanup、result usability は同じ directory の
`research-agent-delegation.md` に従う。

```text
current gap
    ↓ bounded exploration request
Research Agent
    ↓ grounded evidence / result
Agentic Model Construction
    ↓ semantic judgment
same Local Model へ Reintegration
```

direct exploration または Research Agent から得た grounded result は Core へ渡す。task-relative semantic judgment、same Local Model への
反映、必要な repair、bounded re-observation は `model-construction.md` の責任境界に従う。

## Completion

<!-- @contract shared-agentic-completion -->
<!-- @anchor shared-agentic-completion-relation -->
Agent-side resolution の結果、自身に割り当てられた construction scope について blocking gap が残らない場合は completion できる。

未知がゼロであることや Reality 全体の網羅は要求しない。次工程の方向・範囲・結果を実質的に変えない unresolved uncertainty は qualification として保持したまま completion してよい。

Projection Sufficiency 単独を completion 判定にはしない。Exploration Projection 上の gap / qualification と更新済み Local Model を合わせて Method scope の completion を判断する。
<!-- @/contract -->

## Qualified Stop on Material Gap

<!-- @contract shared-agentic-qualified-stop -->
<!-- @anchor shared-agentic-stop-relation -->
Agent-side で合理的に利用可能な bounded resolution route を用いても gap が解消できず、その gap が次工程の方向・範囲・結果を実質的に変え得る場合は停止する。

grounded basis を得られない material gap を、plausible inference だけで解消済みと扱わない。

停止時は calling workflow が判断できる形で、少なくとも意味として次を返す。

- current understanding
- unresolved material gap
- attempted / unavailable resolution basis where relevant
- その gap がなぜ assigned construction の進行を妨げるか
- retained uncertainty / qualification

固定 return schema は要求しない。

Agentic Model Construction 自身は Human に質問せず、Interactive Model Construction への切り替えも行わない。停止後の扱いは calling workflow が所有する。
<!-- @/contract -->

## Output

calling workflow が利用できる current understanding を返し、後続判断に必要な supporting evidence、authority relation、material uncertainty / qualification を保持する。

final response、plan、artifact の生成は calling workflow / downstream responsibility が所有する。

## Non-goals

Agentic Model Construction は次を所有しない。

- additional Human interaction
- Human approval / authority judgment acquisition
- Local Model ownership
- Research Agent への semantic ownership 移譲
- workflow-wide readiness judgment
- Method switching
- downstream artifact generation / acceptance
