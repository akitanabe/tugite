# Model Construction
<!-- @anchor shared-model-document -->

## Purpose

`Model Construction` は、calling workflow が一回の top-level invocation で必要とする task-local Local Model を構築するための共通 ownership / observation / resolution / integration boundary を定義する。

これは第三の実行 Method ではない。実行 Method は `Agentic Model Construction` と `Interactive Model Construction` の二つとする。

## Ownership

<!-- @contract shared-model-ownership -->
<!-- @anchor shared-model-ownership-relation -->
- **`1 top-level workflow invocation = exactly 1 task-local Local Model`** とする。
- Local Model の owner は calling workflow とする。
- Local Model は invocation の目的に局所化された evidence-grounded な意味構造であり、ephemeral とする。
- canonical artifact、persistent state、共通 fixed schema、score、state machine、mandatory serialized representation を要求しない。
- nested workflow、consumer、reviewer、Research Agent は独自 Local Model を所有しない。
- 複数 Method を利用しても同じ一つの Local Model を継続的に更新する。
<!-- @/contract -->

## Model Construction Core

Agentic / Interactive は同じ Core を利用する。

```text
task-local Local Model
        ↓ semantic subject
Model Observation
        ↓
Exploration Projection
+ Projection Sufficiency
        ↓
Gap identification / qualification
        ↓
Gap Resolution
   ├─ reasoning / analysis
   ├─ available context / repository exploration
   ├─ Research Agent
   └─ Human interaction
        (Interactive のみ)
        ↓
grounded result / judgment
        ↓
Reintegration
        ↓
semantic effect evaluation
   ├─ current semantics remain valid
   │      ↓
   │  bounded re-observation as needed
   │
   └─ material semantic region invalidated
          ↓
      Recomposition
          ↓
      repaired same Local Model
          ↓
      bounded re-observation
```

この図は固定 state machine ではない。現在目的に対する reasoning responsibility と continuation relation を示す。

## Model Observation Boundary

Model Construction は Model Observation の一般理論を再定義せず、construction consumer として次の mapping を利用する。

- Model / Model Identity は、caller-owned task-local Local Model とする。
- Model Semantics は、assigned construction purpose に関係する established Local Model semantics とする。
- Model-relative Judgment / bounded observation question は、assigned construction scope において、construction judgment に必要な意味差を Exploration Projection が十分に識別できるかとする。
- Observable Distinctions は、established Local Model semantics に grounded され、bounded construction judgment を変え得る意味差とする。
- Observable Projection は Exploration Projection とする。
- Projection Sufficiency は、Exploration Projection が bounded observation question に必要な Model Semantics を十分に区別できるかを `sufficient`、`insufficient`、`indeterminate` に分類する。分類は serialized field や mandatory schema にはしない。

### Continuation Policy

Projection Sufficiency State に応じて次へ進む。

- `sufficient`: Exploration Projection を gap identification / qualification へ渡す。
- `insufficient` / `indeterminate`: 不足または不確定の原因を construction gap / qualification として保持し、Method が許す resolution route で解決する。grounded result / judgment を Local Model へ Reintegration した後、affected semantics を bounded に再観測する。
- material な原因を Method が許す bounded resolution route で解消できない場合は、その Method の qualified stop とする。

Projection Sufficiency 単独を Method completion や workflow readiness の判定にはしない。

### Model-first / Grounded Projection

repository や available evidence に存在することだけを理由に、Observable Distinction や requirement を作らない。distinction の relevance は established Local Model semantics に grounded し、projection の過程で Local Model に新しい意味を追加しない。

新しい authoritative information が current semantics を変える場合は、先にその semantic effect を Local Model へ Reintegration し、その後に affected semantics を再観測する。authoritative information から Exploration Projection へ意味を直接注入しない。

Model Observation は Exploration Projection の構成と Projection Sufficiency の評価を所有する。次は所有しない。

- Local Model の ownership / mutation
- factual evidence acquisition
- Research Agent dispatch
- gap resolution
- Reintegration / Recomposition
- Model Construction completion
- workflow readiness / downstream action

### Exploration Projection

`Exploration Projection` は current Local Model の semantics を、現在の construction purpose に必要な観測可能差異へ投影した bounded Observable Projection である。

- 第二の Local Model ではない。
- Local Model のコピーでも persistent companion model でもない。
- 独自 owner / persistence / canonical schema を持たない。
- Projection Sufficiency は Local Model completeness、workflow readiness、Reality completeness を意味しない。

## Gap Resolution

Gap は Exploration Projection 上で current construction purpose に対して unresolved と観測された material distinction / uncertainty / dependency とする。

resolution route は gap の意味、利用可能な source、authority boundary に基づいて選ぶ。

- Agent-side reasoning / analysis
- available context / repository exploration
- bounded evidence acquisition
- Research Agent
- Human-held fact / context または Human authority judgment（Interactive のみ）

共通 fixed gap schema、全 gap の最大列挙、固定 resolution sequence は要求しない。

## Research Agent Boundary

Research Agent は bounded evidence acquisition と local analysis を context-isolated に実行し、grounded result を返す actual subagent である。
caller 共通の delegation / operation policy は同じ directory の `research-agent-delegation.md` が所有する。

Model Construction Method は current gap から bounded objective と必要な boundary を構成し、Research Agent の result を
task-relative に意味判断する。result は第二の Local Model や continuation decision ではなく、必要な semantic effect を same Local Model へ
Reintegration / Recomposition する。

## Reintegration

<!-- @contract shared-model-transition -->
<!-- @anchor shared-model-reintegration -->
新しい grounded information / judgment の bounded semantic effect を same Local Model へ戻す通常更新である。

新 evidence が既存理解を変更する場合、stale understanding を単純追記して残さず、affected semantics を current evidence に合わせて更新する。

## Recomposition

<!-- @anchor shared-model-recomposition -->
Recomposition は、Reintegration または grounded dependency evaluation により current Local Model の material semantic region が invalidated した場合の repair である。

- 新情報のたびには実行しない。
- unaffected semantics / boundaries / decisions は保持する。
- invalidated region と dependency を必要な範囲で再構成する。
- repair 後も same Local Model を継続する。
- repair 後は affected semantics を bounded に再観測する。
<!-- @/contract -->

## Evidence Integrity

calling workflow へ understanding を返すときは、後続判断に必要な supporting evidence、authority relation、material uncertainty / qualification を失わない。

完全な certainty や Reality 全体の網羅は要求しない。

## Method Composition

calling workflow が Method の選択、切り替え、順序、役割を所有する。Method 自身は別 Method を自律起動しない。

```text
calling workflow
  ↓
Agentic Model Construction
  ├─ complete → next workflow responsibility
  └─ material blocking gap → stop
                               ↓
                       workflow-defined branch
                               ↓
                   Interactive Model Construction
```

同じ top-level invocation 内で Method を切り替える場合も、同じ task-local Local Model を継続的に更新する。

## Completion Responsibility

<!-- @contract shared-model-completion -->
<!-- @anchor shared-model-completion-relation -->
各 Method は自身に割り当てられた construction scope の完了または停止を判断する。

calling workflow は、返された understanding を利用して workflow 全体として次責務へ進めるかを判断する。

Projection Sufficiency は Method completion と同一ではなく、Method completion は workflow readiness とも同一ではない。
<!-- @/contract -->

## Non-goals

Model Construction は次を定義しない。

- universal Local Model / Exploration Projection schema
- fixed exploration workflow
- fixed Research Agent count
- mandatory BMO / RMO specialization
- mandatory working file
- exhaustive gap coverage rule
- Method selection policy for every workflow
- downstream artifact format / acceptance
