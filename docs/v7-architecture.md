# Tugite v7 Architecture

## Purpose

Tugite v7 は、各 top-level workflow invocation が現在目的に必要な理解を task-local に構築し、その理解を planning、review、observation、execution の各責務へ接続する。

architecture の中心は workflow 手順そのものではなく、**各 invocation に必要な Local Model を構築し、各 consumer が自身の責務だけを実行すること**に置く。

この文書は v7 の横断責務と ownership boundary の正本である。個別 Skill の詳細手順、reviewer 固有観点、platform 固有 integration は各 artifact が所有する。

## Core Principles

### Task-local Local Model

Local Model は、calling workflow が一回の top-level invocation の目的を遂行するために保持する evidence-grounded な意味構造である。

- **`1 top-level workflow invocation = exactly 1 task-local Local Model`** とする。
- Local Model の owner は calling workflow とする。
- `task-local` は独立した Task object を意味せず、その invocation の目的に局所化された理解であることを表す。
- Local Model は ephemeral とし、invocation の終了とともに終了する。canonical artifact や persistent state にしない。
- 共通 fixed schema、score、state machine、mandatory field set を持たない。専用 file / serialized representation も必須にしない。
- nested workflow、consumer、reviewer、Research Agent は独自 Local Model を所有しない。
- nested consumer には、top-level owner が consumer-specific projection を渡す。
- 複数の Model Construction Method を使う場合も Local Model を分割せず、同じ一つの Local Model を継続的に更新する。後続 evidence が既存理解を変える場合は追記だけでなく再統合・修正してよい。

各 Method は自身に割り当てられた構築範囲の完了を判断する。Local Model 全体が workflow の次責務へ進める状態かの最終判断は calling workflow が所有する。Reality 全体の網羅は要求しない。

### Model Construction Methods

v7 では、calling workflow が所有する task-local Local Model を構築するために、次の二つの独立した Method を置く。

- `Agentic Model Construction`: Agent が利用可能な context / evidence / repository / observation を用いて Local Model を構築する。追加の Human interaction は行わない。
- `Interactive Model Construction`: Agent-side の調査・分析を行ったうえで、Human の明示的な判断を completion boundary に含めて Local Model を構築する。

両 Method は repository exploration、Research Agent、Model Observation、evidence integration を必要に応じて利用できる。両者の identity は探索量や探索手法ではなく、**Human の追加判断を completion に必要とするか**にある。

calling workflow は通常、一つの Model Construction Method を利用する。複数 Method の利用・切り替え・順序・役割は、calling workflow が明示的に定義した場合だけ許可する。Method 自身は別 Method を自律起動しない。

calling workflow は、Agentic Model Construction を先に実行し、material な情報不足によって停止した場合だけ Interactive Model Construction へ進む分岐を定義できる。その場合も Local Model は分割せず、同じ一つの task-local Local Model を継続的に更新する。

各 Method は calling workflow が利用できる understanding を返し、後続判断に必要な supporting evidence と material uncertainty を失わない。最終 response / plan / artifact の生成は caller / downstream responsibility が所有する。

### Agentic Model Construction

Agent が利用可能な情報と調査能力だけで Local Model を構築する。

- request 時点ですでに Human から与えられている context / constraint / direction は利用できる。
- repository exploration、Research Agent、Model Observation、追加の evidence acquisition を必要に応じて利用できる。
- 追加の Human interaction は行わない。
- 自身に割り当てられた構築範囲について十分な理解が成立したら完了できる。
- 次工程の方向・範囲・結果を実質的に変え得る material な情報不足が、Agent-side の調査・分析でも解消できない場合は停止する。
- 停止時は、分かっていること、不足していること、その不足がなぜ進行を妨げるかを calling workflow へ返す。
- 次工程に影響しない uncertainty は、明示したまま完了してよい。

### Interactive Model Construction

Agent-side の調査・分析に加えて Human の明示的な判断を completion boundary に含める。

- repository / available context から解消できる事項を先に調査・導出する。
- Agent が分からないこと自体を Human 判断へ置き換えない。
- 必要な Human 判断は途中でも取得できる。
- Human-facing interaction は current domain language で行い、内部の model / decision / exploration vocabulary の理解を要求しない。
- 途中の Human 判断は current understanding へ再統合する。
- **統合後の現在理解を Human が判断できる形で提示し、Human がその理解を downstream の前提として採用して次へ進むことを明示的に認めるまで完了しない。**
- Human が不足・修正を指摘した場合は、必要な再調査・再統合を行い、更新後の理解について再度 Human の判断を得る。
- material uncertainty が残る場合でも、その uncertainty を明示した状態で進むことを Human が判断することはできる。
- 最終確認は downstream artifact / plan 自体の acceptance ではなく、downstream が利用する現在理解の acceptance である。

### Evidence Acquisition and Integration

Model Construction Method は、自身の責務に必要な evidence acquisition を判断する。

Research Agent は、要求された evidence acquisition / bounded exploration を context-isolated に実行し、grounded な結果を caller に返す。

Research Agent は次を所有しない。

- Local Model
- task direction
- planning
- finding の最終的な意味判断
- exploration continuation の最終判断

Research Agent は、取得結果を caller が再統合可能な evidence として返し、scope を自律拡張しない。

## Model Observation Boundary

Model Observation は Local Model を生成する主体ではない。

Model Construction Method は calling workflow が所有する現在理解を更新し、Model Observation は model semantics を observable distinctions へ接続して、何を観測すれば model を評価できるかを導出する。

概念上の関係は次とする。

```text
Model Construction Method
    ├─ Model Observation
    │    ├─ Behavior Model Observation
    │    └─ Reality Model Observation
    └─ Evidence Acquisition
         └─ Research Agent
```

Model Observation の conceptual canonical source は `akitanabe/model-observation-docs` とする。

Tugite v7 は外部 repository を runtime dependency にせず、consumer が実行に必要な semantics、boundary、stopping condition を self-contained に保持する。Tugite 側で Model Observation の一般理論を別定義しない。

## Public Workflows

### explorer-this

`explorer-this` は明示起動のみの薄い public Skill とする。

Agentic Model Construction によって current repository に対する task-local Local Model を構築し、探索レポート自体を目的にせず、caller が求める explanation / comparison / analysis / repository overview / requested artifact へ直接接続する。固定 output schema や固定 workflow は持たない。

repository write は caller が repository artifact を成果物として明示した場合の requested-output authority に限定する。探索 finding 自体は authority を拡張せず、探索中に発見した実装問題を source / test / config へ自律的に修正しない。

### plan-agent

`plan-agent` は discretionary authority entrypoint である。

Human が途中判断を追わず Agent に方向性を委ねる planning workflow とし、task-local Local Model を構築したうえで Planning Synthesis へ進む。

```text
plan-agent
  ↓
Agentic Model Construction
  ↓
Agent-owned direction
  ↓
Planning Synthesis
  ↓
review-refine
```

### plan-interactive

`plan-interactive` は Human / constrained authority entrypoint である。

Interactive Model Construction により repository-grounded な task understanding を形成する。repository から解消できる事項は Agent-side で先に解消し、必要な Human 判断を統合したうえで、統合後の現在理解について Human の最終確認を必ず得る。Human がその理解を planning の前提として採用するまで Planning Synthesis へ進まない。探索中に見つかった追加課題は、それだけで planning scope や authority を拡張しない。Plan candidate の構成と対象範囲の最終責任は `plan-interactive` / Planning Synthesis 側に残す。

```text
plan-interactive
  ↓
Interactive Model Construction
  ↓
planning-ready Local Model / Human-confirmed direction
  ↓
Planning Synthesis
  ↓
Authority Integrity Verification
  ↓
review-refine
```

`plan-agent` と `plan-interactive` は別 planning engine ではなく、**同じ planning capability に対する異なる authority entrypoint** とする。

### review-refine

`review-refine` は artifact / proposal / plan 等を対象に、目的・criteria・evidence に照らして finding を得て、採用した改善を反映する review workflow である。

単独 top-level invocation の場合は自身の task-local Local Model を構築する。`plan-agent` / `plan-interactive` の nested consumer として利用される場合は、親の Local Model から review に必要な projection を受け取り、独自 Local Model を作らない。

structural non-locality は独立 gate ではなく review viewpoint の一つとして扱う。

### code-review

`code-review` は change set / implementation に対する grounded finding を返す review workflow とする。

`review-refine` と共通の Agentic Model Construction / observation mechanism を利用できるが、code-review 自身は remediation や finding adoption を所有しない。

### test-report

`test-report` は Model Construction Method の consumer ではない observation-only public Skill とする。

```text
test-report
  ↓
scope resolution
  ↓
Behavior Model Observation
  ↓
Verification Topology
  ↓
Human
```

責務は次に限定する。

- test / target code の static observation
- Verification Topology の再構成
- observation limits の提示

test quality judgment、remediation、planning、implementation は行わない。

### impl-lead

`impl-lead` は execution workflow として維持する。

v7 core では Model Construction Method を必須化しない。Implementation Unit Design を利用して execution unit を正規化し、worker dispatch、implementation、verification、acceptance を担う。

`impl-lead + Local Model` は v7 完了後に実験し、実装品質、context consumption、overhead を観測して採否を判断する。

## Shared Methods

### Model Construction

`Model Construction` は `Agentic Model Construction` と `Interactive Model Construction` が共有する ownership / integration / composition boundary を定義する。第三の実行 Method ではない。

共通責務:

- calling workflow が所有する一つの task-local Local Model を更新する
- available context、repository evidence、Research Agent、Model Observation 等から得た evidence を必要に応じて統合する
- supporting evidence と material uncertainty を後続判断に必要な範囲で保持する
- 自身に割り当てられた構築範囲の終了を判断する
- calling workflow が利用できる understanding を返す

共通して所有しない責務:

- Local Model の ownership
- Local Model の canonical schema / persistence
- workflow 全体の readiness judgment
- downstream response / plan / artifact の生成
- Method の選択・切り替え・composition

### Agentic Model Construction

shared Method とし、standalone Skill にはしない。

Agent-side の調査・分析・evidence acquisition によって Local Model を構築する。追加の Human interaction は所有しない。

material な情報不足が Agent-side で解消できず、次工程の方向・範囲・結果を実質的に変え得る場合は停止する。停止時は、current understanding、material gap、その gap が進行を妨げる理由を calling workflow へ返す。

### Interactive Model Construction

shared Method とし、standalone Skill にはしない。

Agent-side で解消できる事項を先に処理し、必要な Human 判断を current understanding へ統合する。

completion には Human の最終確認を必須とする。統合後の現在理解と material uncertainty を Human が判断できる形で提示し、Human がその理解を downstream の前提として採用して次へ進むことを明示的に認めるまで完了しない。

Human が不足・修正を指摘した場合は、必要な再調査・再統合を行い、更新後の理解について再度確認する。

### Planning Synthesis

plan-family の共通 planning capability とする。

入力:

- task-local Local Model または必要な projection
- authority
- authority constraints

責務:

- current understanding と authority から coherent な Plan candidate を構成する

所有しない責務:

- repository exploration
- research
- Model Construction
- Human clarification
- review
- final acceptance

### Implementation Unit Design

`impl-lead` が利用する shared Method とする。

責務:

- independently acceptable outcome の boundary を設計する
- split / merge を判断する
- semantic dependency を構成する
- AC / verification / accept / rollback boundary を揃える
- implementer が再設計せず着手できる単位に正規化する

task の再設計、worker selection、execution order、implementation は所有しない。

### Model Construction Artifact Layout

Model Construction は次の三 artifact で構成する。

```text
shared-v7/
  model-construction.md
  agentic-model-construction.md
  interactive-model-construction.md
```

`model-construction.md` は第三の実行 Method ではなく、両 Method の共通 ownership / integration / composition boundary を保持する。

`agentic-model-construction.md` と `interactive-model-construction.md` は独立した Method artifact とする。どちらを使うか、または条件付きで切り替えるかは calling workflow が定義する。

Local Model の internal representation や working file layout は architecture として固定しない。必要な temporary file は implementation detail として利用できるが、canonical artifact / mandatory state にはしない。

### Model Construction Validation

初期 validation は representative case による behavior validation を先行する。特に次を確認する。

- Agentic が repository exploration / Research Agent / Model Observation を必要に応じて使い、Agent-side だけで十分なら完了できる
- Agentic が次工程を変え得る material な情報不足を Agent-side で解消できない場合に停止し、その不足を calling workflow へ返せる
- Interactive が repository / available context から解消できる事項を先に処理できる
- Interactive が途中の Human 判断を current understanding へ再統合できる
- Interactive が統合後の現在理解について Human の最終確認を得るまで完了しない
- Human が不足を指摘した場合に再調査・再統合し、更新後に再確認できる
- Method の切り替えが Method 自身ではなく calling workflow の定義によってのみ発生する
- 複数 Method を利用しても同じ task-local Local Model を更新し続ける
- exploration finding によって caller scope / authority を拡張しない

専用 lint は初期構成に含めない。contract は representative case で重要性が確認され、現在の invariant / responsibility / boundary を機械的に検証できるものだけ追加する。固定文言や過去構造の不存在を守るための contract は作らない。

## Agents

### Research Agent

shared Research Agent を置く。

Research Agent は bounded evidence acquisition / source inspection / exploration を行う stateless helper であり、Local Model を所有しない。

### Specialized Reviewers

reviewer は specialized / stateless / context-isolated observer とする。

```text
Local Model
   ↓ consumer-specific projection
specialized reviewer
   ↓
evidence-grounded findings
   ↓
parent が Local Model / review state へ再統合
```

reviewer は次を所有しない。

- Local Model
- task scope
- finding adoption
- remediation
- review continuation / completion

専門 lens の分離自体を context isolation の価値として維持し、一つの万能 reviewer に統合しない。

## plan-interactive Authority Protection

Human-confirmed direction は downstream synthesis / refinement で意味変更されてはならない。

そのため `plan-interactive` は Authority Integrity Verification を所有する。

```text
Human-confirmed authority
        ↓
Planning Synthesis
        ↓
candidate
        ↓
Authority Integrity Verification
        ↓
review / refinement
        ↓
Authority Integrity Verification
```

Authority Integrity Verification は authority constraint と candidate の semantic preservation だけを照合し、plan quality、improvement proposal、direction change、新仕様を所有しない。

fresh context が必要な場合は専用 observer を execution mechanism として使えるが、多目的 advisor role は作らない。

## Artifact Taxonomy

v7 では `kernel` を first-class concept として使わない。

共有 artifact は「共有したいから kernel」と分類せず、現在の responsibility により分類する。

例:

- Method
- Boundary / Rule
- Agent
- Skill
- consumer-specific reference

`kernel` の代替となる万能カテゴリは作らない。

## v7 Core Topology

```text
Tugite v7

Public Workflows
├─ explorer-this
├─ plan-agent
│    └─ discretionary authority
├─ plan-interactive
│    └─ Human / constrained authority
├─ review-refine
├─ code-review
├─ test-report
│    └─ observation-only / BMO based
└─ impl-lead
     └─ execution

Shared Methods
├─ Model Construction
│    ├─ Agentic Model Construction
│    └─ Interactive Model Construction
├─ Planning Synthesis
└─ Implementation Unit Design

Observation Methods
├─ Model Observation
├─ Behavior Model Observation
└─ Reality Model Observation

Agents
├─ Research Agent
└─ Specialized Reviewer Agents

plan-interactive specific
└─ Authority Integrity Verification
```

## Construction Surface

v7 は current v6 canonical tree と分離した construction surface でゼロベース構築する。

```text
shared/
  → current v6 canonical

shared-v7/
  → v7 construction surface
```

`shared-v7/` は v6 source tree の clone-and-prune にしない。

```text
v7 architecture
  ↓
必要な responsibility を導出
  ↓
必要な artifact だけ selective rebuild
```

v6 artifact は evidence として参照できるが、v7 artifact の初期状態としてコピーしない。

v7 完成時に repository-wide verification を行い、v7 candidate を canonical `shared/` へ切り替える。`shared-v7/` という migration concept を完成 architecture に残さない。

## v7 Core Scope

v7 core に含めない事項:

- `impl-lead` への Local Model 適用
- 未実装 `wayfind` workflow

これらは v7 core 完了後に実測・必要性を再評価する。

## Development Order

推奨する構築順序は次とする。

```text
1. v7 architecture
2. Model Construction
3. Agentic Model Construction
4. Research Agent
5. Model Observation consumer methods
6. Interactive Model Construction
7. Planning Synthesis
8. plan-agent
9. explorer-this
10. plan-interactive
11. review-refine
12. code-review
13. test-report
14. Implementation Unit Design
15. impl-lead
16. integration / canonical switch
```

最初に共通の Model Construction boundary と Agentic Model Construction を成立させ、その後に Research Agent / Model Observation を接続する。Interactive Model Construction は Human judgment boundary を追加する独立 Method として構築する。
