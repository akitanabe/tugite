<!-- @contract reality-model-observation-kernel-v1 -->
# Reality Model Observation Kernel v1

Kernel identity: `reality-model-observation-kernel-v1`.
Kernel dependencies: `none`.

この共有規範は、与えられた Target に対して Observable Reality Model を導出し、そのモデルで Reality を観測し、Target-relative な discrepancy と Problem を導出する共有 Method である。正本はこのファイルであり、各 platform の配布物では `references/reality-model-observation-kernel.md` として生成される。各 role は全文を複製せず、この規範との自分の既存返却形式への mapping だけを持つ。parent は package reference を読み、role には既存の判定基準または必要な周辺 context の一部として identity / 必要な本文を渡す。

Kernel 自体は reviewer、gate、planner、または consumer 固有の出力形式ではない。異なる consumer が、それぞれの責務に応じて利用できる共通の観測・問題導出手法を提供する。

中核となる考え方は次である。

> Self-reflection is unbounded; Reality is bounded.
> 自己内省は際限なく継続できるが、現在の Target に対して観測すべき Reality は有限の責務境界を持つ。

意味上の結果は次で閉じる。

```text
Target Semantics
  -> Required Reality Distinctions
  -> Ground / Admit
  -> Observable Signals + Conditions / Proxy
  -> Cover / Trim / Classify
  -> Reality Observation
  -> Discrepancy
  -> Mismatch Attribution
  -> Target Membership Check
  -> Target-relative Problem
  -> STOP
```

## Contract

### 入力

consumer は次を Kernel へ渡す。

- **Target**
- **relevant authoritative context**
- **available evidence / observation capability**
- **authority / responsibility boundary**
- optional **Observation Trigger**

Target は consumer が現在の責務内で観測・問題導出の対象とする意味的対象であり、Task Specification 自体ではない。Task Specification、requirements、repository evidence は Target を Reality と照合する authoritative context に置く。

Target の identity と中核的な意味の解決は consumer の責務とする。未解決事項または新しい情報が Target の identity または中核的な意味を変え得る場合、Kernel はそれを内部で解決せず、consumer に再解決を委ねる。

Observation Trigger は、観測の起点または hypothesis になり得る。reviewer finding を含む finding は Observation Trigger / hypothesis に限り、grounding evidence として自己利用しない。Trigger の本文を Reality evidence へ読み替えない。

情報が Target の意味を規定する根拠になれるかどうかは、ファイル種別ではなく authority によって判断する。authority を持つ Context 間に conflict があり precedence が未解決なら、Kernel は一方を選択したり統合したりしない。

必要な Context または evidence surface が不足している場合、Kernel は何を確定できないかまでは示せる。ただし、自身で scope を広げて追加 Context を取得しない。

### 出力

Kernel は共通 serialized schema を持たず、意味上の結果として次を返す。

- **Target-relative Derived Problems**
- **Incidental Findings**
- **Uncertainty / unresolved evidence gap**
- **grounding trace**

あわせて、Observable Reality Model、observed evidence、discrepancy、mismatch attribution、Target Membership judgment、Model Sufficiency、Observed Evidence Sufficiency、observation / inference の区別を、consumer の既存返却形式へ写像できる形で保持する。

`Target-relative` は remediation や `adopted` を意味しない。consumer が下流で裁定する。

Kernel は remediation、proposal、Target revision、routing、accept / reject、Tugite 固有 taxonomy を持たない。

## Observable Reality Model

Observable Reality Model は Target の意味から導出する。available metric / test / log から成功条件を作る Evidence-first Modeling は失敗である。

Model は少なくとも次を保持する。

- Required Reality Distinctions
- Observable Signals
- Target / Context からの grounding
- Interpretation Conditions / Assumptions
- Proxy relationship
- Observation gaps
- Relevant Unresolved Viewpoints
- Model Sufficiency

Reality Distinction は、次の両方を満たす場合だけ Admit する。

1. Target または authoritative Context に grounding がある
2. 観測結果が異なることで Target satisfaction / discrepancy judgment が変わりうる

一般に重要、best practice、測定可能、興味深い、論理上ありうる、という理由だけでは Admit しない。

Observable Signal は proxy であってよい。ただし常に次を追跡可能にする。

```text
Target
  ↓
Required Reality Distinction
  ↓
Observable Signal
  ↓
Interpretation Conditions / Assumptions
```

Proxy を Reality 自体として提示してはならない。Proxy が意味を持つ条件を消してはならない。

Model Sufficiency と Observed Evidence Sufficiency は別である。Model が識別可能であることと、Reality を判断するのに十分な観測が取得済みであることは混同しない。

```text
Model Sufficiency
    ≠
Observed Evidence Sufficiency
```

observation と inference を分離する。観測事実を推論で埋めず、推論を観測事実として提示しない。

## Method

これは固定 state machine ではなく、標準的な reasoning direction である。

### Target Semantics

Target satisfaction と discrepancy を区別するために必要な、すでに grounded な意味を抽出する。Human value、threshold、policy boundary をここで補完しない。不足している Target semantics は unresolved のまま残す。

### Required Reality Distinctions

Target satisfaction と discrepancy を意味的に分離しうる distinction の候補を Discover する。lens は類推の補助であり、固定 taxonomy ではない。固定 Reality category をすべて埋めることを目的化しない。

### Ground / Admit

各 candidate が Target または authoritative Context に grounding を持つか確認する。grounding できない candidate は、もっともらしいという理由だけで採用しない。finding を含む Observation Trigger は hypothesis として探索してよいが、十分な grounding がないまま Reality Distinction や Derived Problem へ進めない。

Admit するのは、観測結果の違いが Target judgment を変えうる grounded candidate だけである。

### Observable Signals + Conditions / Proxy

各 admitted distinction について、Reality 上でその差異を露出しうる evidence surface を特定する。signal は「すでに存在するから」ではなく、required distinction を expose するから選ぶ。各 signal について、どの distinction を表すか、なぜ Target に重要か、どの conditions で意味を持つか、proxy かどうかを説明可能にする。arbitrary threshold を捏造しない。

### Cover / Trim / Classify

Cover: admitted Required Reality Distinctions が current Observable Signals により discriminable か、observation gap / unresolved viewpoint として明示されているかを確認する。Coverage は Target-relative であり、Reality 全体の coverage を意味しない。

Trim: 新しい Target-relevant distinction を増やさない signal を mandatory にしない。measurable だから、reviewer が別の concern を想像できるから、という理由だけで観測を追加しない。

Classify は Model Sufficiency について行う。

- **Sufficient** — admitted Required Reality Distinctions が coherent な signal set で discriminable であり、model structure または Target judgment を materially 変えうる Relevant Unresolved Viewpoint が残っていない。これは Model derivation sufficiency であり、実際の観測データが十分に集まっていることを意味しない。
- **Insufficient** — 具体的な admitted Reality Distinction が unobservable または uncovered のままである。
- **Indeterminate** — 具体的な coverage gap は確定していないが、解決によって distinction / mapping / sufficiency が変わりうる grounded unresolved issue が残る。

`Sufficient` を Reality 全体に問題がない証明として扱わない。

### Reality Observation

Actual observation は Observable Reality Model に沿って行う。観測時に新しい思いつきが生じても、その場で observation criteria を追加してはならない。必要な場合は Reintegration により model derivation 側へ戻る。signal は導出時の interpretation conditions と一緒に読む。条件を消して unconditional fact に平坦化しない。

Model が `Sufficient` でも、actual evidence が足りない場合は observation judgment を確定しない。

signal が Target judgment に使えるのは、その criterion、reference、observed result の意味を Observation 対象となる loop 自身が都合よく再定義できない場合に限る。

同じ observed result が、grounded conditions の下で Target-satisfied state と Target-discrepant state の両方に現れうるなら、その signal 単独では discriminator として不十分である。

### Discrepancy

Observed Reality と Target-relative expected distinction を比較し、discrepancy の有無を判断する。Target-relative mismatch がなければ停止できる。追加の自己内省が可能であることを理由に継続しない。

### Mismatch Attribution

Reality mismatch は、現在の design / semantic model の defect を自動的に意味しない。少なくとも次を区別する。

```text
current design / semantic-model defect
Agent interpretation drift from Human intent
incorrect evidence / environment assumption
```

Human-provided reality を Agent interpretation より下位に置かない。stale evidence、wrong environment assumption、changed population、invalid baseline、unauthorized inference を Target defect と誤認しない。Attribution が確定しない場合は、無理に design problem として確定せず Uncertainty とする。

### Target-relative Problem

Target Membership Check を通過した discrepancy だけを、現在の Target に対する Problem として導出する。Derived Problem は observed evidence に grounding があり、Target との関係が説明可能で、mismatch attribution と矛盾せず、current Target を越えず、solution も improvement proposal も含まない。

Problem Derivation 後、必ず停止する。

```text
Target-relative Problem
  -> STOP
```

Problem が actionable であること、改善案が容易に思いつくこと、改善したほうが有益であることは、本 Kernel を継続する理由にならない。

## Reintegration

`Reintegration` は Problem Derivation 前までの Method 全体に掛かる横断規則とする。

Problem Derivation 前に new grounded evidence / context / constraint が model を無効化した場合、dependent distinctions、signals、conditions、attribution、membership を再評価し、last reliable derivation point から再適用する。古い distinction / signal は、以前に導出したという理由だけで保存しない。

Target identity または central semantics 自体が無効になった場合は Kernel 内で再定義せず caller へ返し、caller が Target を解決して新しい invocation を開始する。

## Target Membership Check

Observed issue を Derived Problem に昇格する前に問う。

> この observed difference は、現在定義済みの Target の satisfaction を変えるか？

- **Yes** — Target-relative Derived Problem として扱う。
- **No** — Target を拡張しない。Incidental Finding として保持する。Incidental Finding は current Target に昇格させない。Incidental Finding は current Target の obligation にしない。
- **Unclear** — Target semantics が unresolved なら Uncertainty / unresolved evidence gap として保持する。Agent が勝手に scope を拡張しない。

membership の意味上の分類は次の3つで閉じる。

```text
Target-relative
Incidental
Uncertainty
```

Relevant Unresolved Viewpoint として保持するには、解決によって Required Reality Distinction、Signal mapping、interpretation condition、mismatch attribution、Target Membership、Sufficiency のいずれかが変わりうることと、Target / Context / observed evidence に concrete signal があることの両方を満たす。理論上の detail、exhaustive でない specification、best practice、想像可能な failure だけでは保持しない。

## Consumer Responsibilities

Kernel は共有 Method であり、Kernel の出力を何に、どのように利用するかは consumer が決める。

consumer は自身の scope / responsibility に従って、次を担う。

- Target の供給と identity / 中核意味の解決
- relevant authoritative context と authority / precedence の指定
- available evidence / observation capability と tool authority の提供
- authority / responsibility boundary の確定
- optional Observation Trigger の供給
- Kernel の出力を利用する目的と評価対象の決定
- consumer 固有の finding、verdict、severity、accept / reject、成果物生成
- Target-relative Derived Problem を remediation Claim の候補にするかどうかの裁定
- Incidental Finding と Uncertainty の下流扱い
- 必要な追加 Context の取得と再注入
- Target revision が必要な場合の新しい Target の定義

Kernel は consumer topology、consumer 名、consumer 固有の成果物、評価対象、workflow phase を正本として保持しない。consumer が増減・変更されても、それ自体を理由に Kernel の Contract / Method を変更しない。

Kernel は finding severity、accept / reject、新しい product requirement を返さない。

Behavior Observation Kernel は resolved Behavior から Expected Observations を導出する Method である。本 Kernel は Target-relative Reality を観測して Problem を導出する Method である。どちらも dependencies none とし、統合も成立条件化もしない。

## Non-goals

`Reality Model Observation Kernel` は次を行わない。

- 共通 serialized Observation schema の定義
- Reality 自体を作る、または再定義する
- Target を再定義する
- Human の価値判断、成功閾値、policy judgment を補完する
- 現在利用可能な metric / test / log / tool から Target の意味を逆算する
- 観測可能だからという理由だけで signal を重要とみなす
- proxy を Reality 自体として扱う
- 固定 taxonomy に Reality を押し込む
- Reality の全状態、全 failure、全 observation を列挙する
- Reality に問題が存在しないことを証明する
- caller の evidence / authority / responsibility boundary を越えて推論する
- 観測された問題から Improvement Candidate を生成する
- remediation plan や implementation task を作る
- 観測結果を理由に Target を拡張する
- Problem Derivation 後に自動的に改善ループへ進む
- consumer 固有の評価対象から Target を逆算すること
- Tugite 固有 taxonomy を Kernel の分類として持つこと
<!-- @/contract -->
