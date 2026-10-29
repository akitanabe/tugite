# Tugite v7 Architecture

## Purpose

Tugite v7 は、各 top-level workflow invocation が現在目的に必要な理解を task-local に構築し、その理解を planning、review、observation、execution の各責務へ接続する。

architecture の中心は workflow 手順そのものではなく、**各 invocation に必要な Local Model を構築し、各 consumer が自身の責務だけを実行すること**に置く。

この文書は v7 の横断責務と ownership boundary の正本である。個別 Skill の詳細手順、reviewer 固有観点、platform 固有 integration は各 artifact が所有する。

## Core Principles

### Task-local Local Model

Local Model は、calling workflow が一回の top-level invocation の目的を遂行するために保持する evidence-grounded な意味構造である。

* **`1 top-level workflow invocation = exactly 1 task-local Local Model`** とする。
* Local Model の owner は calling workflow とする。
* `task-local` は独立した Task object を意味せず、その invocation の目的に局所化された理解であることを表す。
* Local Model は ephemeral とし、invocation の終了とともに終了する。canonical artifact や persistent state にしない。
* 共通 fixed schema、score、state machine、mandatory field set を持たない。専用 file / serialized representation も必須にしない。
* nested workflow、consumer、reviewer、Research Agent は独自 Local Model を所有しない。
* nested consumer には、top-level owner が consumer-specific projection を渡す。
* 複数の Model Construction Method を使う場合も Local Model を分割せず、同じ一つの Local Model を継続的に更新する。後続 evidence が既存理解を変える場合は追記だけでなく再統合・修正してよい。

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

* **Exploration Projection** は、current Local Model の semantics を現在の construction purpose に対して観測可能な差異へ投影した bounded Observable Projection である。第二の Local Model ではなく、独自 ownership / persistence / canonical schema を持たない。
* **Projection Sufficiency** は、その Exploration Projection が現在の bounded construction judgment に必要な意味差を十分に識別できるかを評価する。Local Model 全体の completeness、workflow readiness、Reality completeness とは同一視しない。
* **Gap** は、Exploration Projection により current construction purpose に対して unresolved と観測された material distinction / uncertainty / dependency である。共通 fixed gap schema や exhaustive gap enumeration は要求しない。
* **Gap Resolution** は、current gap の resolution basis と利用可能な source / authority に応じて、Agent-side analysis、repository exploration、evidence acquisition、Research Agent、または Method が許可する Human interaction を利用する。
* **Reintegration** は、新しい grounded information / judgment の semantic effect を同じ Local Model へ戻す。新 evidence が既存理解を変える場合は stale understanding を並置して残すのではなく、affected semantics を更新する。
* **Recomposition** は current Local Model の material semantic region が invalidated した場合の repair として利用できる。新情報のたびに全面再構築することを要求しない。
* semantic delta が Local Model に戻った場合、必要な affected semantics だけを bounded に再観測し、Exploration Projection / Projection Sufficiency を更新する。

この Core により、Model Construction は「Agent が十分だと感じたら終了する」自己内省だけに依存せず、Local Model の semantics を Exploration Projection へ投影して gap / sufficiency を観測しながら construction を進める。

### Model Construction Methods

v7 では、calling workflow が所有する task-local Local Model を構築するために、次の二つの独立した Method を置く。

* `Agentic Model Construction`: Agent が利用可能な context / evidence / repository / observation を用いて Local Model を構築する。追加の Human interaction は行わない。
* `Interactive Model Construction`: Agent-side の調査・分析を行ったうえで、Human の明示的な判断を completion boundary に含めて Local Model を構築する。

両 Method は上記 Model Construction Core を共有し、Local Model → Model Observation → Exploration Projection → Gap Resolution → Reintegration の progression を同じ意味境界で利用する。repository exploration、Research Agent、追加 evidence acquisition は gap resolution の手段であり、両者の identity を分ける基準ではない。両者の identity は探索量や探索手法ではなく、**Human の追加判断を completion に必要とするか**にある。

calling workflow は通常、一つの Model Construction Method を利用する。複数 Method の利用・切り替え・順序・役割は、calling workflow が明示的に定義した場合だけ許可する。Method 自身は別 Method を自律起動しない。

calling workflow は、Agentic Model Construction を先に実行し、material な情報不足によって停止した場合だけ Interactive Model Construction へ進む分岐を定義できる。その場合も Local Model は分割せず、同じ一つの task-local Local Model を継続的に更新する。

各 Method は calling workflow が利用できる understanding を返し、後続判断に必要な supporting evidence と material uncertainty を失わない。最終 response / plan / artifact の生成は caller / downstream responsibility が所有する。

### Agentic Model Construction

Agentic Model Construction は、上記 Model Construction Core を追加の Human interaction なしで実行する。

* request 時点ですでに Human から与えられている context / constraint / direction は通常の input として利用できる。
* current Local Model を Model Observation で Exploration Projection へ投影し、current construction purpose に対する gap / qualification を識別する。
* Agent-side reasoning / analysis、available context / repository exploration、Research Agent による bounded evidence acquisition を gap resolution に利用できる。
* Research Agent result / direct evidence は same Local Model へ Reintegration し、material semantic region が invalidated した場合だけ Recomposition する。
* semantic delta 後は affected semantics を必要な範囲で bounded re-observation する。
* assigned construction scope に blocking gap が残らなければ completion できる。未知ゼロや Reality completeness は要求しない。
* 次工程の方向・範囲・結果を実質的に変えない unresolved uncertainty は qualification として保持したまま completion してよい。
* Agent-side の bounded resolution route でも解消できない material blocking gap が残る場合は、current understanding、material gap、その gap が進行を妨げる理由を calling workflow へ返して停止する。
* 追加の Human interaction は開始せず、Interactive Model Construction への切り替えも自律的に行わない。

### Interactive Model Construction

Interactive Model Construction は、Agentic と同じ Model Construction Core に Human resolution route と final Human judgment boundary を追加する。

* current Local Model を Model Observation で Exploration Projection へ投影し、current construction purpose に対する gap / qualification を識別する。
* Human に入力・判断を求める前に、Agent-side reasoning / analysis、available context / repository exploration、Research Agent で解消できる gap を先に処理する。
* Agent が分からないことや Research Agent へ委譲できること自体を Human interaction の理由にしない。
* Human interaction は、Exploration Projection 上の current gap について resolution source / authority が Human にある場合に利用する。
* Human にのみ保持される factual / contextual information と、Human authority が必要な preference / trade-off / direction / responsibility judgment を意味上区別する。
* Human-facing interaction は current domain language で行い、内部の Local Model / Exploration Projection / gap / Recomposition vocabulary の理解を要求しない。
* Human response、Research Agent result、direct evidence は same Local Model へ Reintegration する。Human response 自体を Recomposition trigger にしない。
* grounded information / judgment により material semantic region が invalidated した場合だけ Recomposition し、semantic delta 後は affected semantics を bounded re-observation する。
* 途中で Human interaction を行っていても final Human judgment は省略しない。
* **統合・再観測後の current understanding を Human が判断できる形で提示し、Human がその理解を downstream の前提として採用して次へ進むことを明示的に認めるまで completion しない。**
* Human が不足・修正を指摘した場合はその semantic effect を再統合し、必要なら Recomposition / bounded re-observation を行い、更新後の理解について再度 Human の判断を得る。
* material uncertainty が残る場合でも、その uncertainty を明示した状態で進むことを Human が判断できる。Human approval によって unknown fact を known fact に変えない。
* final confirmation は downstream artifact / plan 自体の acceptance ではなく、downstream が利用する current understanding の acceptance である。

### Evidence Acquisition and Integration

Model Construction Method は Exploration Projection 上の current gap と自身の authority boundary に基づき、必要な resolution route を判断する。新しい factual evidence との接触が必要な場合は evidence acquisition を行い、その結果を same Local Model へ再統合する。

repository / available context の直接探索で解消できる gap は Method 自身が解消してよい。bounded な source inspection / exploration を context-isolated に委譲する価値がある場合は Research Agent を利用できる。

Research Agent は、要求された evidence acquisition / bounded exploration を context-isolated に実行し、grounded な結果を caller に返す。

Research Agent は次を所有しない。

* Local Model
* Exploration Projection の意味判断
* gap の最終的な materiality / priority
* task direction
* planning
* finding の最終的な意味判断
* exploration continuation / completion の最終判断

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

* Local Model ownership / mutation
* factual evidence acquisition
* Research Agent dispatch
* gap resolution
* Human judgment
* Reintegration / Recomposition
* Model Construction completion
* workflow readiness / downstream action

Exploration Projection は Model Observation の bounded output であり、Local Model の代替・コピー・persistent companion model ではない。Projection Sufficiency が `sufficient` であることも Local Model 全体の completeness や workflow readiness を保証しない。

新しい evidence contact により current understanding が変化した場合、その semantic effect は Model Construction 側が Local Model へ Reintegration し、その後に必要な範囲で Model Observation を再実行する。Model Observation 自身が evidence を取得して Local Model を mutate したことにはしない。

Model Observation の conceptual canonical source は `akitanabe/model-observation-docs` とする。特に次を canonical reference とする。

* `docs/ja/model-observation-epistemic-foundation.md`
* `docs/ja/model-observation.md`

Tugite v7 は外部 repository を runtime dependency にせず、consumer が実行に必要な semantics、boundary、stopping condition を self-contained に保持する。Tugite 側で Model Observation の一般理論を別定義しない。

Behavior Model Observation / Reality Model Observation は concrete specialization として必要時に利用できるが、Model Construction Core は特定 specialization の常時実行を要求しない。

## Public Workflows

### visualize-that

`visualize-that` は任意の supplied material を、人が理解しやすい順序の図と説明からなる単独 HTML にする明示起動の public Skill である。一回の invocation で exactly one の task-local Local Model を所有し、Agentic Model Construction を first route、Agent-side resolution 後にも Human-owned material gap が残る場合だけ Interactive Model Construction を同じ Local Model へ composition する。

入力の事実、関係、制約、不確実性を保ち、主要項目に成果物内で stable な識別子を付ける。識別子による deep dive は元 overview を残した別 HTML とする。browser launch、screenshot capture、actual inspection を分けた local Programmatic Flow で描画を確認し、capability 不足や未修復の視認性問題では HTML を保持した `render-unverified` を返す。意味保持と visual acceptance は Agent の判断に残す。

### test-report

`test-report` は exactly one の task-local Local Model を所有する静的診断の public Skill である。Agentic Model Construction を first route とし、Human-owned material gap だけを局所確認する。要求・仕様からも Behavior candidate を構成し、対象 test 自身を期待値の正当性の根拠にしない。shared Verification Topology は grounding、semantic precedence、BMO、many-to-many relation、state を所有し、診断と report は consumer が所有する。

```text
test-report
  ↓
scope resolution → requirements / tests / source / config observation
  ↓
shared Verification Topology
  ↓
static diagnosis → full-scope report → Human
```

概要に加え、問題のない箇所を含む observed scope 全体の Behavior → Expected Observation ↔ Case → Evidence、条件、実際の assertion、source location を辿れる詳細を示す。未対応 Evidence、要求側の evidence gap、未読・未実行・skip・対応不明・証拠なしと観測限界を保持する。静的に確認した問題、実行確認が必要な疑い、判断材料の不足を区別し、指摘の識別子、根拠、見逃しうる問題、次に確認する点を残す。

report の repository / ref、scope、要求根拠と参照先は任意の `test-verify` 引き継ぎに利用できる。test / source / CI の実行、source / test / config の変更、verify への自動遷移は行わない。固定 schema や専用台帳は要求しない。

### test-verify

`test-verify` は明示された report 全体・選択した指摘、または直接の bounded target を shared Verification Topology と grounded runtime evidence で検証し、direct owner が許可された target-causal Problem だけを Red → Green → Refactor で修復する public Skill である。report の根拠は現状と再照合し、変化・不足・未確定部分を補う。未選択の指摘は解決済みにしない。report の事前実行や nested invocation は必要としない。

```text
report / selected findings / direct bounded target
  ↓
current scope and authority → shared Verification Topology
  ↓
baseline / runtime evidence → Problem and causal judgment
  ↓
authorized repair if needed → bidirectional reconciliation
  ├─ no change → final verification
  └─ changed immutable snapshot → applicable test acceptance
                                 → Completion Gate → final verification
```

direct owner は repository Test QA baseline の obligation、common oracle、validation plane、final adjudication を履行する。test / fixture / oracle / executable test contract の変更には両 coverage / validity reviewer の観測と direct owner の採否を必要とし、production-only / no-change に既存テスト全体の再審査を要求しない。risk review は concrete risk の追加観測とし、変更テスト受入と重複させない。`impl-lead` の Parent QA phase、parent / worker hierarchy、Implementation Unit、Implementer delegation は導入しない。

baseline identity と failure disposition を維持し、test-side defect と production-side discrepancy を独立した要求根拠から区別する。PASS や一部修正だけを完了根拠にせず、要求と最終 Evidence の双方向照合を行う。no-change は変更レビューや空コミットなしで閉じる。変更ありでは immutable candidate snapshot に applicable gate と final verification を行い、commit authority がなければ base / exact diff / content identity を固定した uncommitted snapshot を使う。検証の成立と commit の実施を別々に報告する。

shared External Effects boundary を pre-action safety に利用する。material な evidence / authority / causal attribution の不足や、要求変更・大きな設計変更が必要な問題は qualified incomplete とし、自動的に対象を拡張しない。local Flow の `stop-incomplete` も同じ外向き状態へ投影する。

### impl-plan と impl-lead

`impl-plan` は supplied plan の意味を維持して実装単位・担当・文脈・依存順序・検証を委譲文書へ具体化する。
Implementation Unit Design は impl-plan 配下で Unit boundary、split / merge、semantic dependency、independent acceptability を判断し、既存 RMO の semantics を用いる。
Unit の8 field と担当・route 等の実行計画情報を区別する。規模適否と分担の最終採用は Human が所有する。

`impl-lead` は準備済み委譲文書を消費し、現時点の readiness / authority / state を確認して依存順に直列実行する。
委譲計画が未作成の場合だけ impl-plan の責務を利用する。準備済み計画を無条件に再作成せず、前提不一致は明示して停止する。
実際の dispatch、monitoring、clarification / correction、Parent QA、review、受入 gate、commit、最終検証、integration / closeout は impl-lead に残る。
最初の実装・別 Unit・独立観測は fresh、同じ Unit の同じ担当の clarification / correction だけ continuation とする。

### explain-this と review-propose

`explain-this` はコードを主な根拠に一つの適応的 Local Model を構築し、意味のある処理ごとに主要クラス・関数の実コードをまとまった抜粋で示し、短い補足とともにHumanへ実装の流れを説明する。
実コードを主、説明を補助とし、抜粋の出典・省略箇所を明示する。複数箇所のコードはそれぞれの原文と出典を保って読み順につなぎ、実装を書いていないHumanも内部の判断・変更と次へ渡す値・呼出先を追えるようにする。補足はコードをまたぐ接続、重要な分岐・状態変化・実行順序へ集中し、引数や値の説明はその理解に必要な範囲に絞る。
調査では暗黙の接続や共通基盤も必要に応じて追い、出力の粒度は機能理解への寄与で選ぶ。重要な条件、状態変化、副作用、処理順と失敗・トランザクション境界を保つ。
テスト期待値は補助根拠とし、実装・意図・実行観測・不確実性を区別する。必要で許可された小さな実行確認も使える。
`review-propose` は元プランと推奨案を同じ Local Model のもとで比較し、MO で判断に必要な意味差を観測する。
caller が根拠取得・指摘吟味・整合・比較を所有し、Human が採用を判断する。両 workflow とも RMO を必須にせず、実装修正へ自動遷移しない。

### impl-review

`impl-review` は明示対象、保持 context、必要時の Human 確認の順で実装済み差分を特定する。
`shared/implementation-review.md` は impl-lead と共有する観点・適用条件・入力・指摘処理の正本であり、実行・受入工程を所有しない。
専門 review は具体的 risk に応じ、変更テストには coverage / validity を適用し、writing review も行う。修正表を返して変更前に停止する。

調査・初期プラン作成は通常のエージェントへ依頼する。これらは用途別の入口であり、固定の自動実行チェーンではない。

## Shared Methods

### Model Construction

`Model Construction` は `Agentic Model Construction` と `Interactive Model Construction` が共有する ownership / integration / composition boundary を定義する。第三の実行 Method ではない。

共通責務:

* calling workflow が所有する一つの task-local Local Model を更新する
* current Local Model を Model Observation の semantic subject として扱い、bounded Exploration Projection / Projection Sufficiency を得る
* Exploration Projection から current construction purpose に対する gap / qualification を識別する
* current gap の resolution basis に応じて available context、repository exploration、evidence acquisition、Research Agent、Method が許可する Human interaction を利用する
* grounded result / judgment の semantic effect を same Local Model へ Reintegration し、必要なら invalidated region を Recomposition する
* semantic delta 後は affected semantics を必要な範囲で bounded re-observation する
* supporting evidence と material uncertainty を後続判断に必要な範囲で保持する
* 自身に割り当てられた構築範囲の終了を判断する
* calling workflow が利用できる understanding を返す

共通して所有しない責務:

* Local Model の ownership
* Local Model / Exploration Projection の canonical schema / persistence
* Projection Sufficiency と Local Model completeness / workflow readiness の同一視
* workflow 全体の readiness judgment
* downstream response / plan / artifact の生成
* Method の選択・切り替え・composition

### Agentic Model Construction

shared Method とし、standalone Skill にはしない。

同じ Model Construction Core を追加の Human interaction なしで実行する。Exploration Projection 上の gap を Agent-side reasoning / repository exploration / Research Agent で解消し、result を same Local Model へ Reintegration する。material semantic region が invalidated した場合だけ Recomposition し、affected semantics を bounded re-observation する。

assigned construction scope に blocking gap が残らなければ completion できる。Agent-side の bounded resolution route でも解消不能で、次工程を実質的に変え得る material gap が残る場合は caller へ qualified stop を返す。

### Interactive Model Construction

shared Method とし、standalone Skill にはしない。

Agentic と同じ Model Construction Core に Human resolution route と final Human judgment boundary を追加する。Agent-side で解消できる gap を先に処理し、Human-held fact / context または Human authority judgment が resolution basis である場合だけ Human interaction を利用する。

Human response を same Local Model へ Reintegration し、material invalidation が成立した場合だけ Recomposition / bounded re-observation を行う。completion には、統合・再観測後の current understanding を Human が downstream の前提として採用する final judgment を必須とする。

### Model Construction Artifact Layout

Model Construction は次の三 artifact で構成する。

```text
shared/
  model-construction.md
  agentic-model-construction.md
  interactive-model-construction.md
```

`model-construction.md` は第三の実行 Method ではなく、両 Method の共通 ownership / integration / composition boundary を保持する。

`agentic-model-construction.md` と `interactive-model-construction.md` は独立した Method artifact とする。どちらを使うか、または条件付きで切り替えるかは calling workflow が定義する。

Local Model の internal representation や working file layout は architecture として固定しない。必要な temporary file は implementation detail として利用できるが、canonical artifact / mandatory state にはしない。

### Model Construction Validation

初期 validation は representative case による behavior validation を先行する。特に次を確認する。

* current Local Model から Model Observation により bounded Exploration Projection / Projection Sufficiency を構成できる
* Exploration Projection が第二の Local Model / persistent state として扱われない
* Projection Sufficiency と Local Model completeness / workflow readiness / Reality completeness を同一視しない
* observed gap が適切な resolution route へ接続され、new evidence / judgment が same Local Model へ再統合される
* corrective evidence が既存理解を変えた場合、stale understanding の追記ではなく affected semantics が更新される
* local semantic update で整合が保てる場合に unnecessary Recomposition を行わない
* grounded information / judgment により material semantic region が invalidated した場合だけ Recomposition し、unaffected semantics / boundaries を保持する
* Recomposition 後も same task-local Local Model を維持する
* semantic delta 後の re-observation が affected semantics に対して bounded に行われる
* Model Observation が factual evidence acquisition / Research Agent dispatch / Reintegration / completion を所有しない
* Agentic が同じ Core を利用し、repository exploration / Research Agent 等の Agent-side resolution だけで十分なら Human interaction なしで完了できる
* Agentic が次工程を変え得る material な情報不足を Agent-side で解消できない場合に停止し、その不足を calling workflow へ返せる
* Interactive が同じ Core を利用し、repository / available context から解消できる事項を先に処理できる
* Interactive が途中の Human 判断を current understanding へ再統合できる
* Interactive が統合後の現在理解について Human の最終確認を得るまで完了しない
* Human が不足を指摘した場合に再調査・再統合・bounded re-observation し、更新後に再確認できる
* Method の切り替えが Method 自身ではなく calling workflow の定義によってのみ発生する
* 複数 Method を利用しても同じ task-local Local Model を更新し続ける
* exploration finding によって caller scope / authority を拡張しない

専用 lint は初期構成に含めない。contract は representative case で重要性が確認され、現在の invariant / responsibility / boundary を機械的に検証できるものだけ追加する。固定文言や過去構造の不存在を守るための contract は作らない。
