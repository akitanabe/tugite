<!-- Generated from shared/. Do not edit directly. -->

# Implementation Unit Design

Method identity: `impl-lead implementation-unit-design v1`.

## Identity and responsibility boundary

この文書は `impl-lead` の同一 invocation 内だけで使う `impl-lead` 専用の consumer-specific Method である。独立した public / internal Skill、
shared reusable Method、直接 invocation surface を持たない。

Method は supplied outcome candidates に対する Unit boundary、split / merge、semantic dependency、independent acceptability、
Implementation Unit candidates の構成を所有する。raw request から outcome を追加せず、scope、要求 coverage、候補の最終採用、ID、
execution、worker / reviewer、acceptance、persistence を所有しない。

## Inputs and outputs

入力は `impl-lead` が固定した non-empty initial outcome candidates と、request / Plan / established direction、Acceptance Criteria の素材、
scope / constraints、repository evidence、known dependency、verification reality、accept / rollback reality からなる grounding である。
Method は追加 evidence acquisition を開始しない。

出力は次の会話内 execution data である。

- Implementation Unit candidates: `id` 以外の canonical Unit Data と、候補間の semantic dependency relation。
- 判断理由 / qualification: split / merge、dependency、acceptability の根拠と non-blocking uncertainty。
- `blocking_gaps`: Unit boundary、dependency、acceptabilityを安全に確定できない material gap。

Unit field の一覧や意味をこの Method で再定義しない。worker、route、order、isolation、execution result、review、QA、保存先を出力へ
混入させない。run-unique ID の付与と、返した dependency relation の ID への束縛は `impl-lead` 親へ残す。

## RMO loading and mapping

caller context を確定した後、partition reasoning の直前に一度 load する。

```text
path = ../../../references/reality-model-observation.md
load_timing = after caller context is established and immediately before partition reasoning
identity = # Reality Model Observation
required_sections = [Identity and boundary, Inputs, Outputs and ownership, Projection derivation, Concrete observation and evidence sufficiency, Attribution and Target Membership]
failure = blocking_gaps before partition reasoning
owner = implementation-unit-design Method
```

load、identity、required section の不足・不一致では partition reasoning を開始しない。この failure は Reality evidence の uncertainty と
区別し、`impl-lead` の `stop-incomplete` boundary へ返す。

この Method では RMO を mandatory に利用し、次の5入力を consumer mapping する。

- **Target**: Target は Unit boundary、semantic dependency、independent acceptability に限定する。
- **Relevant Authoritative Context**: supplied candidates、request / Plan / established direction、AC / verification、scope / constraints、repository / dependency evidence、accept / rollback reality。
- **Available Evidence Surface**: grounding 内の authorized repository facts、verification / dependency / acceptability evidence。
- **Authority / Responsibility Boundary**: outcome / scope / coverage は `impl-lead`、observation / Problem derivation は RMO、partition judgment は Method、execution / acceptance は `impl-lead` の後続 Phase が所有する。
- **Observer Boundary**: supplied evidence に接触し、Current Reality と bounded RMO judgment を構成する `impl-lead` 親 context。

RMO result では observation / inference、Model Sufficiency / Observed Evidence Sufficiency、Target-relative Problem / Incidental Finding /
Uncertainty を区別可能に保持する。RMO result を split / merge / dependency verdict へ直接変換せず、Incidental Finding を Unit や obligation へ
昇格させない。RMO の一般 semantics は canonical RMO source を参照し、この文書へ複製しない。

## Partition judgment

1. 各 outcome candidate を grounding と照合し、purpose、AC、scope、dependency、focused verification、accept / rollback boundary を確認する。
2. 「新しい Implementer がこの Unit だけを読み、AC、responsibility、dependency、Unit boundary を再設計せず、受入候補 diff に集中できるか」を確認する。
3. split signal と merge / over-split signal を中立に適用し、1 Unit / N Units のいずれも初期前提にしない。
4. semantic dependency を構成し、shared surface による execution conflict で代替しない。
5. 返却前に under-split、over-split、dependency 欠落、independent acceptability を再確認する。

file 数、行数、architecture layer、実装工程、同じ worker、shared file / writer / generator / generated output / contract registry / full gate /
verification surface の共有だけでは split / merge を決めない。context token 数や overflow score を hard criterion にしない。

### Split signals

次の signal を個別に観測し、成立する意味関係を理由として保持する。

1. 独立した accept purpose が複数ある。
2. 先行 Unit の学習結果で後続 Unit の設計が変わる。
3. 複数の外部副作用、または異なる rollback boundary がある。
4. verification または acceptance judgment が異なる。
5. 旧仕様 parity と新規 behavior が混在する。
6. Implementer が AC、responsibility boundary、dependency を再設計しないと着手できない。
7. 未解決の設計・推論判断が多く、Implementer が受入候補 diff に集中できない。

### Merge / over-split signals

次の具体的 evidence があり、同じ受入境界でしか成立しない候補だけを merge する。

1. 同じ verification でしか Green / invariant を確認できない。
2. 一方だけでは Green にならない、または invariant が成立しない。
3. 一方だけでは accept / revert できない。
4. architecture layer の名前だけで横割りしている。
5. Unit 間 handoff が統合内部の結合より複雑である。

独立 purpose、focused verification、accept / revert boundary を持つ候補は、shared surface や run-wide gate だけを理由に消さない。
foundation は独立 capability / contract、単独 AC、focused verification、accept boundary を持つ場合だけ単独 Unit にする。

### Semantic dependency and execution conflict

semantic dependency は、後続 Unit の意味的成立に先行 Unit の成果が必要な関係である。execution conflict は同じ file、writer、generator、
generated surface、contract registry、verification surface などを共有する関係である。Method は semantic dependency だけを Unit Data の
`depends_on` に構成し、execution conflict の order / isolation を決めない。

## Uncertainty and return boundary

material uncertainty が Unit boundary、semantic dependency、independent acceptability を変え得る場合は plausible inference で埋めず、
Unit を確定しない `blocking_gaps` として返す。判断を変えない uncertainty は qualification として保持できる。

Method は candidates、理由 / qualification、blocking gaps を返して終了する。`impl-lead` は coverage、scope、blocking gap、Data boundary を
確認するが、Method の partition judgment を再設計しない。Unit 確定後に Method へ戻る renormalization loop を作らない。設計前提が後続の
execution 中に崩れた場合は current execution を継続せず、上流 / `stop-incomplete` boundary へ返す。

run-wide final verification 後の Final Correction Unit は、既存 accepted Unit の boundary から親が一意に導出する bounded exception であり、
この Method の対象に含めない。Unit boundary、split / merge、semantic dependency、independent acceptability の再判断が必要になった時点で eligibility を失う。
親は Method を再 invocation せず `stop-incomplete` とする。

## Representative contrasts

次の Case は exact Unit 数を expected-output oracle にせず、入力 facts と意味差に対する source-level walkthrough として使う。

### Case A — single candidate

単一 purpose、単独 AC、focused verification、accept / rollback boundary を持つ小規模候補も Method を通す。grounding 上で独立成果が一つなら
不要に split せず 1 Unit candidate を返す。

### Case B — independently acceptable outcomes

複数候補が独立 purpose、AC、focused verification、accept / revert boundary を持つ場合は、shared file / generator を共有しても別 Unit とする。
意味上の dependency が実在する場合だけ `depends_on` に保持する。

### Case C — over-split candidates

候補の一方だけでは同じ invariant、Green、accept / revert が成立しない場合は、over-split evidence に基づいて同じ Unit へ merge する。

### Case D — Implementer redesign burden

一見一つの outcome でも、AC、responsibility、dependency、boundary の未解決判断が独立成果を隠している場合は split signal とする。
token 数を推定せず、Implementer が受入候補 diff に集中できる境界を構成する。

### Case E — RMO prevents speculative partition

partition 仮説と repository evidence / acceptability relation が一致しない場合は、RMO の observation、discrepancy、uncertainty を保持し、
RMO finding を verdict にせず grounded split / merge criteria で判断する。

### Case F — blocking uncertainty

dependency または acceptability を変え得る evidence gap が残る場合は Unit を確定せず、何が不足し何を観測すれば閉じるかを
`blocking_gaps` として返す。
