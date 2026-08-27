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

### Model Construction Core

Model Construction は、**task-local Local Model を現在の construction purpose に対して観測可能な gap へ投影し、必要な resolution を行い、結果を同じ Local Model へ戻す共通 progression** を持つ。この Core は特定の既存 workflow architecture や state machine を前提とせず、Tugite v7 の current responsibility / boundary として自己完結して定義する。

概念上の共通 Core は次とする。

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
        ├─ available context / repository exploration
        ├─ bounded evidence acquisition
        ├─ Research Agent
        └─ Human interaction
             (Method boundary が許可する場合のみ)
        ↓
grounded result / judgment
        ↓
Reintegration / Recomposition as needed
        ↓
same task-local Local Model
        ↓
bounded re-observation as needed
```

この progression は固定 state machine ではない。現在目的に対する reasoning responsibility と continuation relation を表す。

- **Exploration Projection** は、current Local Model の semantics を現在の construction purpose に対して観測可能な差異へ投影した bounded Observable Projection である。第二の Local Model ではなく、独自 ownership / persistence / canonical schema を持たない。
- **Projection Sufficiency** は、その Exploration Projection が現在の bounded construction judgment に必要な意味差を十分に識別できるかを評価する。Local Model 全体の completeness、workflow readiness、Reality completeness とは同一視しない。
- **Gap** は、Exploration Projection により current construction purpose に対して unresolved と観測された material distinction / uncertainty / dependency である。共通 fixed gap schema や exhaustive gap enumeration は要求しない。
- **Gap Resolution** は、current gap の resolution basis と利用可能な source / authority に応じて、Agent-side analysis、repository exploration、evidence acquisition、Research Agent、または Method が許可する Human interaction を利用する。
- **Reintegration** は、新しい grounded information / judgment の semantic effect を同じ Local Model へ戻す。新 evidence が既存理解を変える場合は stale understanding を並置して残すのではなく、affected semantics を更新する。
- **Recomposition** は current Local Model の material semantic region が invalidated した場合の repair として利用できる。新情報のたびに全面再構築することを要求しない。
- semantic delta が Local Model に戻った場合、必要な affected semantics だけを bounded に再観測し、Exploration Projection / Projection Sufficiency を更新する。

この Core により、Model Construction は「Agent が十分だと感じたら終了する」自己内省だけに依存せず、Local Model の semantics を Exploration Projection へ投影して gap / sufficiency を観測しながら construction を進める。

### Model Construction Methods

v7 では、calling workflow が所有する task-local Local Model を構築するために、次の二つの独立した Method を置く。

- `Agentic Model Construction`: Agent が利用可能な context / evidence / repository / observation を用いて Local Model を構築する。追加の Human interaction は行わない。
- `Interactive Model Construction`: Agent-side の調査・分析を行ったうえで、Human の明示的な判断を completion boundary に含めて Local Model を構築する。

両 Method は上記 Model Construction Core を共有し、Local Model → Model Observation → Exploration Projection → Gap Resolution → Reintegration の progression を同じ意味境界で利用する。repository exploration、Research Agent、追加 evidence acquisition は gap resolution の手段であり、両者の identity を分ける基準ではない。両者の identity は探索量や探索手法ではなく、**Human の追加判断を completion に必要とするか**にある。

calling workflow は通常、一つの Model Construction Method を利用する。複数 Method の利用・切り替え・順序・役割は、calling workflow が明示的に定義した場合だけ許可する。Method 自身は別 Method を自律起動しない。

calling workflow は、Agentic Model Construction を先に実行し、material な情報不足によって停止した場合だけ Interactive Model Construction へ進む分岐を定義できる。その場合も Local Model は分割せず、同じ一つの task-local Local Model を継続的に更新する。

各 Method は calling workflow が利用できる understanding を返し、後続判断に必要な supporting evidence と material uncertainty を失わない。最終 response / plan / artifact の生成は caller / downstream responsibility が所有する。

### Agentic Model Construction

Agentic Model Construction は、上記 Model Construction Core を追加の Human interaction なしで実行する。

- request 時点ですでに Human から与えられている context / constraint / direction は通常の input として利用できる。
- current Local Model を Model Observation で Exploration Projection へ投影し、current construction purpose に対する gap / qualification を識別する。
- Agent-side reasoning / analysis、available context / repository exploration、Research Agent による bounded evidence acquisition を gap resolution に利用できる。
- Research Agent result / direct evidence は same Local Model へ Reintegration し、material semantic region が invalidated した場合だけ Recomposition する。
- semantic delta 後は affected semantics を必要な範囲で bounded re-observation する。
- assigned construction scope に blocking gap が残らなければ completion できる。未知ゼロや Reality completeness は要求しない。
- 次工程の方向・範囲・結果を実質的に変えない unresolved uncertainty は qualification として保持したまま completion してよい。
- Agent-side の bounded resolution route でも解消できない material blocking gap が残る場合は、current understanding、material gap、その gap が進行を妨げる理由を calling workflow へ返して停止する。
- 追加の Human interaction は開始せず、Interactive Model Construction への切り替えも自律的に行わない。

### Interactive Model Construction

Interactive Model Construction は、Agentic と同じ Model Construction Core に Human resolution route と final Human judgment boundary を追加する。

- current Local Model を Model Observation で Exploration Projection へ投影し、current construction purpose に対する gap / qualification を識別する。
- Human に入力・判断を求める前に、Agent-side reasoning / analysis、available context / repository exploration、Research Agent で解消できる gap を先に処理する。
- Agent が分からないことや Research Agent へ委譲できること自体を Human interaction の理由にしない。
- Human interaction は、Exploration Projection 上の current gap について resolution source / authority が Human にある場合に利用する。
- Human にのみ保持される factual / contextual information と、Human authority が必要な preference / trade-off / direction / responsibility judgment を意味上区別する。
- Human-facing interaction は current domain language で行い、内部の Local Model / Exploration Projection / gap / Recomposition vocabulary の理解を要求しない。
- Human response、Research Agent result、direct evidence は same Local Model へ Reintegration する。Human response 自体を Recomposition trigger にしない。
- grounded information / judgment により material semantic region が invalidated した場合だけ Recomposition し、semantic delta 後は affected semantics を bounded re-observation する。
- 途中で Human interaction を行っていても final Human judgment は省略しない。
- **統合・再観測後の current understanding を Human が判断できる形で提示し、Human がその理解を downstream の前提として採用して次へ進むことを明示的に認めるまで completion しない。**
- Human が不足・修正を指摘した場合はその semantic effect を再統合し、必要なら Recomposition / bounded re-observation を行い、更新後の理解について再度 Human の判断を得る。
- material uncertainty が残る場合でも、その uncertainty を明示した状態で進むことを Human が判断できる。Human approval によって unknown fact を known fact に変えない。
- final confirmation は downstream artifact / plan 自体の acceptance ではなく、downstream が利用する current understanding の acceptance である。

### Evidence Acquisition and Integration

Model Construction Method は Exploration Projection 上の current gap と自身の authority boundary に基づき、必要な resolution route を判断する。新しい factual evidence との接触が必要な場合は evidence acquisition を行い、その結果を same Local Model へ再統合する。

repository / available context の直接探索で解消できる gap は Method 自身が解消してよい。bounded な source inspection / exploration を context-isolated に委譲する価値がある場合は Research Agent を利用できる。

Research Agent は、要求された evidence acquisition / bounded exploration を context-isolated に実行し、grounded な結果を caller に返す。

Research Agent は次を所有しない。

- Local Model
- Exploration Projection の意味判断
- gap の最終的な materiality / priority
- task direction
- planning
- finding の最終的な意味判断
- exploration continuation / completion の最終判断

Research Agent は、取得結果を caller が再統合可能な evidence として返し、scope を自律拡張しない。Research Agent の result 自体を新しい Local Model または canonical exploration state にしない。

## Model Observation Boundary

Model Observation は Local Model を生成・所有・更新する主体ではない。Model Construction Core において、**current Local Model を semantic subject として Exploration Projection へ投影し、その Projection Sufficiency を評価する observation responsibility** を担う。

概念上の関係は次とする。

```text
task-local Local Model
        ↓
Model Observation
        ↓
Exploration Projection
+ Projection Sufficiency
        ↓
Model Construction
  gap identification / resolution
        ↓
Reintegration
        ↓
same task-local Local Model
```

Model Observation は次を所有しない。

- Local Model ownership / mutation
- factual evidence acquisition
- Research Agent dispatch
- gap resolution
- Human judgment
- Reintegration / Recomposition
- Model Construction completion
- workflow readiness / downstream action

Exploration Projection は Model Observation の bounded output であり、Local Model の代替・コピー・persistent companion model ではない。Projection Sufficiency が `sufficient` であることも Local Model 全体の completeness や workflow readiness を保証しない。

新しい evidence contact により current understanding が変化した場合、その semantic effect は Model Construction 側が Local Model へ Reintegration し、その後に必要な範囲で Model Observation を再実行する。Model Observation 自身が evidence を取得して Local Model を mutate したことにはしない。

Model Observation の conceptual canonical source は `akitanabe/model-observation-docs` とする。特に次を canonical reference とする。

- `docs/ja/model-observation-epistemic-foundation.md`
- `docs/ja/model-observation.md`

Tugite v7 は外部 repository を runtime dependency にせず、consumer が実行に必要な semantics、boundary、stopping condition を self-contained に保持する。Tugite 側で Model Observation の一般理論を別定義しない。

Behavior Model Observation / Reality Model Observation は concrete specialization として必要時に利用できるが、Model Construction Core は特定 specialization の常時実行を要求しない。

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
- current Local Model を Model Observation の semantic subject として扱い、bounded Exploration Projection / Projection Sufficiency を得る
- Exploration Projection から current construction purpose に対する gap / qualification を識別する
- current gap の resolution basis に応じて available context、repository exploration、evidence acquisition、Research Agent、Method が許可する Human interaction を利用する
- grounded result / judgment の semantic effect を same Local Model へ Reintegration し、必要なら invalidated region を Recomposition する
- semantic delta 後は affected semantics を必要な範囲で bounded re-observation する
- supporting evidence と material uncertainty を後続判断に必要な範囲で保持する
- 自身に割り当てられた構築範囲の終了を判断する
- calling workflow が利用できる understanding を返す

共通して所有しない責務:

- Local Model の ownership
- Local Model / Exploration Projection の canonical schema / persistence
- Projection Sufficiency と Local Model completeness / workflow readiness の同一視
- workflow 全体の readiness judgment
- downstream response / plan / artifact の生成
- Method の選択・切り替え・composition

### Agentic Model Construction

shared Method とし、standalone Skill にはしない。

同じ Model Construction Core を追加の Human interaction なしで実行する。Exploration Projection 上の gap を Agent-side reasoning / repository exploration / Research Agent で解消し、result を same Local Model へ Reintegration する。material semantic region が invalidated した場合だけ Recomposition し、affected semantics を bounded re-observation する。

assigned construction scope に blocking gap が残らなければ completion できる。Agent-side の bounded resolution route でも解消不能で、次工程を実質的に変え得る material gap が残る場合は caller へ qualified stop を返す。

### Interactive Model Construction

shared Method とし、standalone Skill にはしない。

Agentic と同じ Model Construction Core に Human resolution route と final Human judgment boundary を追加する。Agent-side で解消できる gap を先に処理し、Human-held fact / context または Human authority judgment が resolution basis である場合だけ Human interaction を利用する。

Human response を same Local Model へ Reintegration し、material invalidation が成立した場合だけ Recomposition / bounded re-observation を行う。completion には、統合・再観測後の current understanding を Human が downstream の前提として採用する final judgment を必須とする。

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

- current Local Model から Model Observation により bounded Exploration Projection / Projection Sufficiency を構成できる
- Exploration Projection が第二の Local Model / persistent state として扱われない
- Projection Sufficiency と Local Model completeness / workflow readiness / Reality completeness を同一視しない
- observed gap が適切な resolution route へ接続され、new evidence / judgment が same Local Model へ再統合される
- corrective evidence が既存理解を変えた場合、stale understanding の追記ではなく affected semantics が更新される
- local semantic update で整合が保てる場合に unnecessary Recomposition を行わない
- grounded information / judgment により material semantic region が invalidated した場合だけ Recomposition し、unaffected semantics / boundaries を保持する
- Recomposition 後も same task-local Local Model を維持する
- semantic delta 後の re-observation が affected semantics に対して bounded に行われる
- Model Observation が factual evidence acquisition / Research Agent dispatch / Reintegration / completion を所有しない
- Agentic が同じ Core を利用し、repository exploration / Research Agent 等の Agent-side resolution だけで十分なら Human interaction なしで完了できる
- Agentic が次工程を変え得る material な情報不足を Agent-side で解消できない場合に停止し、その不足を calling workflow へ返せる
- Interactive が同じ Core を利用し、repository / available context から解消できる事項を先に処理できる
- Interactive が途中の Human 判断を current understanding へ再統合できる
- Interactive が統合後の現在理解について Human の最終確認を得るまで完了しない
- Human が不足を指摘した場合に再調査・再統合・bounded re-observation し、更新後に再確認できる
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
│    ├─ Core: Local Model → Model Observation → Exploration Projection → Gap Resolution → Reintegration
│    ├─ Agentic Model Construction
│    └─ Interactive Model Construction
├─ Planning Synthesis
└─ Implementation Unit Design

Observation Methods
├─ Model Observation
│    └─ Exploration Projection / Projection Sufficiency
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

### Current Infrastructure as Implementation Evidence

v6 / current canonical artifact の semantics / responsibility を v7 artifact の設計根拠として継承しない。一方、新しい v7 artifact が repository に既存の infrastructure category を利用する場合は、その current integration mechanism を implementation evidence として確認する。

これは clone-and-prune の例外ではない。確認対象は旧 artifact の意味仕様ではなく、artifact が repository 上で成立するための integration surface である。該当するものについて、少なくとも次を確認対象に含める。

- canonical source / artifact representation
- platform-specific generation / declaration
- packaging / distribution / installation
- applicable lint / contract / repository test
- current verification command / regression path

既存 mechanism を利用できる場合でも、その mechanism に載っている v6 semantics / responsibility を v7 へ暗黙継承しない。current need がない generic integration framework / test framework も新設しない。

v7 artifact が既存 infrastructure category を利用する場合、実装完了前に対応する integration surface を確認し、該当する generation / distribution / installation / test / verification path が v7 candidate に対して成立することを verification boundary に含める。

### Per-Artifact Implementation and Verification

```text
architecture / current responsibility
        ↓
artifact implementation
        ↓
existing infrastructure integration check
        ↓
representative behavior validation
        ↓
applicable generation / distribution / installation / test verification
        ↓
必要なら current invariant の contract
        ↓
lint / repository verification
```

`existing infrastructure integration check` は、実装対象が既存 infrastructure category を利用する場合だけ適用する。既存 infrastructure を利用しない artifact のために v6 / current canonical を儀式的に探索しない。

変更された integration boundary に machine-observable behavior がある場合、対応する既存 test を更新するか、必要最小限の test を追加する。representative Agent behavior validation と infrastructure verification / repository test は代替関係にしない。既存 test / verification path で十分な場合は v7 専用 framework を増やさない。

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
2. Model Construction Core + Model Observation integration / Exploration Projection
3. Agentic Model Construction
4. Research Agent
5. Model Observation specialization consumer methods (BMO / RMO)
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

最初に `Local Model → Model Observation → Exploration Projection → Gap Resolution → Reintegration` の共通 Model Construction Core を成立させ、その Core 上で Agentic Model Construction を構築する。その後に delegated evidence acquisition として Research Agent、必要な concrete observation specialization として BMO / RMO consumer semantics を接続する。Interactive Model Construction は同じ Core に Human judgment boundary を追加する独立 Method として構築する。