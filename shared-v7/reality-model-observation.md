# Reality Model Observation
<!-- @anchor shared-v7-rmo-document -->

<!-- @contract shared-v7-rmo-identity-boundary -->
<!-- @anchor shared-v7-rmo-identity-relation -->
## Identity and boundary

`Reality Model Observation`（RMO）は、bounded な `Target` を、Observer が扱う Reality
上の Target-relative な観測可能差異へ投影し、authorized な concrete evidence との接触で
Observer の `Current Reality` を更新して、Target-relative discrepancy と Problem までを導出する
Tugite consumer method である。RMO は canonical Model Observation の Reality specialization であり、
利用するかどうかは caller が決める optional な選択である。

`External Real`、Observer が現在扱う `Current Reality`、および `Observable Reality Model` を同一視しない。
`Observable Reality Model` は Reality の完全な写像や代替物ではなく、現在の Target に必要な差異を
識別する Target-relative Observable Projection over Reality である。Concrete observation は
evidence との接触によって Observer の Current Reality を更新するが、External Real 自体を変更しない。

RMO は Problem Derivation で停止する。RMO の projection は calling workflow の task-local Local Model、
第二の Local Model、persistent state、canonical な固定 schema ではない。また mandatory phase、独立
lifecycle、固定 state machine、exhaustive な Reality taxonomy を導入しない。
<!-- @/contract -->

```text
Target + authoritative Context + evidence surface
      + authority / responsibility / Observer boundary
        ↓
Target Semantics
        ↓
Required Reality Distinctions
        ↓ Ground / Admit
Observable Signals + conditions / proxy
        ↓ Cover / Trim / Classify
Observable Reality Model + Model Sufficiency
        ↓ (Sufficient の場合だけ authorized observation)
Concrete Observation → Updated Current Reality
        ↓
Observed Evidence Sufficiency → discrepancy
        ↓ (discrepancy の場合だけ)
Mismatch Attribution → Target Membership
        ↓
Target-relative Problem / Incidental / Uncertainty
        ↓
STOP
```

この図は責務と判断の方向を示すものであり、呼び出し側へ固定された実行状態や手順を要求しない。

## Inputs

caller は、少なくとも次の意味を RMO に渡す。

- **Target** — 現在評価する bounded な達成状態と、その identity / semantics。
- **Relevant Authoritative Context** — Target の意味、条件、制約を確定または補足する context。
- **Available Evidence Surface** — Current Reality を更新しうる事実、runtime behavior、test result、
  production signal、Human observation、external contract、authorized source など。
- **Authority / Responsibility Boundary** — established とみなせる事実、決定できること、推論できること、
  および caller が評価・行動する責務の境界。
- **Observer Boundary** — concrete evidence に接触し、Current Reality の更新と bounded judgment を担う
  Observer の境界。

Target identity / central semantics、Human の value judgment、成功 threshold、policy、または scope が
未解決であり、それが model や Target-relative judgment を変えうる場合、RMO は補完せず qualification
または unresolved viewpoint として停止する。authoritative Context 間の precedence が同様に未解決なら、
一方を選んだり silent merge したりしない。RMO は利用可能な metric、test、log、tool から Target の意味を
逆算しない。

## Outputs and ownership

<!-- @contract shared-v7-rmo-output-boundary -->
<!-- @anchor shared-v7-rmo-output-relation -->
必要に応じて、RMO は次の意味を caller が追跡できる形で返す。

- **Observable Reality Model** — Required Reality Distinctions、各 distinction の Target / Context
  への grounding、Observable Signals、interpretation conditions / assumptions、proxy relationship、
  observation gap、Relevant Unresolved Viewpoint、および `Model Sufficiency`。
- **Observation result** — observed evidence、観測された state、更新後の Current Reality、conditions、
  `Observed Evidence Sufficiency`、observation と inference の区別、discrepancy、limitation、未確定の
  attribution。
- **Problem derivation result** — mismatch attribution、Target Membership judgment、Target-relative
  Derived Problem、必要に応じた Incidental Finding または Uncertainty。

RMO は次を所有・出力する責務を持たない。

- remediation、implementation、Improvement Candidate、Change Proposal
- Target の再定義・拡張、次の Improvement Loop、workflow continuation / completion
- finding の採否、severity、accept / reject、downstream verdict
- evidence acquisition、Research Agent の dispatch、same Local Model への Reintegration / Recomposition
<!-- @/contract -->

## Projection derivation

次は RMO の specialization を読み合わせるための reasoning direction である。すべての入力値や failure を
列挙する固定 taxonomy ではない。

### Target Semantics → Required Reality Distinctions

Target が satisfied である状態と discrepant である状態を意味上分けるために必要な Reality Distinction
の candidate を、Target Semantics と Relevant Authoritative Context から導出する。candidate は次の両方を
満たす場合だけ `Admit` する。

1. Target または authoritative Context に grounding がある。
2. 観測結果の違いが Target satisfaction / discrepancy judgment を変えうる。

測定可能、一般に重要、興味深い、best practice、または既存 artifact に現れるというだけでは admission の
根拠にならない。独立して成立・不成立を判定できる別の意味や、現在 Target に関係しない差異を、同じ Target
の distinction に畳み込まない。

### Observable Signals and conditions

Admitted distinction を concrete evidence との接触で識別可能にする signal を選ぶ。一つの distinction に
複数 signal、複数 distinction に一つの signal、joint interpretation のいずれも許容するが、各 mapping は
次を説明できなければならない。

- どの Required Reality Distinction を表すか。
- なぜその distinction が Target に relevant か。
- どの baseline、observation window、workload / population、event definition などの conditions で
  signal が意味を持つか。
- proxy である場合、proxy と distinction の関係および assumptions は何か。

Signal は因果関係を証明する必要はない。ただし Target judgment を変えうる grounded な discriminative
relationship を持つ必要がある。proxy を Reality 自体として提示したり、条件を消して unconditional fact に
flatten したりしない。

### Cover → Trim → Classify

<!-- @contract shared-v7-rmo-model-sufficiency -->
<!-- @anchor shared-v7-rmo-model-sufficiency-relation -->
admitted な Required Reality Distinctions が、coherent な signal set で discriminable であるか、または
具体的な gap / unresolved viewpoint として明示されているかを確認する。Target judgment を変えない signal
や、利用できるだけの内部 step・値・組み合わせは mandatory にしない。

`Model Sufficiency` は Observable Reality Model の導出十分性である。

- **Sufficient** — admitted な distinction が coherent な signal set で discriminable であり、model
  structure または Target judgment を変えうる Relevant Unresolved Viewpoint が残っていない。
- **Insufficient** — admitted な distinction が具体的に uncovered または unobservable のままである。
- **Indeterminate** — coverage gap は確定できないが、grounded な unresolved issue の解決により distinction、
  mapping、condition、または sufficiency が変わりうる。

同じ conditions の下で同じ signal / signal set が Target-satisfied state と Target-discrepant state の
両方に現れうるなら、それを `Sufficient` な discriminator としない。別の grounded signal との組合せ、
condition の明確化、observation gap、または Relevant Unresolved Viewpoint に戻す。

`Sufficient` は Reality 全体の completeness、External Real への到達、actual evidence の取得、workflow
readiness を意味しない。`Insufficient` / `Indeterminate` は、authority / observability resolution または
責務内の grounded repair が実際に可能な場合だけ再導出し、それ以外は qualification とともに停止する。

`Relevant Unresolved Viewpoint` として保持するのは、Target / Context / observed evidence に concrete signal
があり、その解決が distinction、signal mapping、interpretation condition、attribution、membership、または
sufficiency を変えうる場合に限る。Reality に理論上さらに detail があることや、generic best practice だけでは
`Indeterminate` の理由にしない。
<!-- @/contract -->

## Concrete observation and evidence sufficiency

<!-- @contract shared-v7-rmo-observation-gate -->
<!-- @anchor shared-v7-rmo-observation-relation -->
Model Sufficiency が `Sufficient` の場合、caller が許可した boundary 内で、frozen な criteria / conditions
に沿って concrete evidence と接触する。観測中に新しい思いつきがあっても、criteria を都合よく追加・変更
しない。新 evidence が model を無効化した場合、RMO は stale な model のまま観測を続けない。caller がその
evidence の authority / semantic effect を判断し、必要なら同じ task-local Local Model へ Reintegration /
Recomposition を行う。caller が更新済みの Target / Context を RMO へ再注入した後、RMO は影響を受けた
distinction / signal だけを再導出してから観測を続ける。

直接観測した evidence、そこからの inference、limitation、未取得の根拠を分ける。`Model Sufficiency` と
`Observed Evidence Sufficiency` は別であり、前者が十分でも、後者が不足していれば Reality judgment、
discrepancy、attribution、membership を確定しない。その場合は observation limitation / unresolved evidence
として停止するか、caller-owned additional acquisition に返す。

`Observed Evidence Sufficiency` は、frozen な model と conditions に沿った actual evidence が Current Reality
の更新と Target-relative judgment に足りるかの bounded な判断である。十分な evidence がそろった状態を
`Sufficient`、必要な observation が欠けている状態を `Insufficient` として扱うが、これは Model Sufficiency の
再分類でも Reality 全体の completeness の主張でもない。

Observed Evidence Sufficiency が十分なときだけ、Updated Current Reality と Target-relative expected
distinction を照合する。discrepancy がなければ Problem を生成せず停止する。自己内省の余地や別の測定可能な
signal があることは継続理由にならない。
<!-- @/contract -->

## Attribution and Target Membership

<!-- @contract shared-v7-rmo-membership-stop -->
<!-- @anchor shared-v7-rmo-attribution-relation -->
discrepancy がある場合に限り、少なくとも次の可能性を区別して mismatch attribution を行う。

- current design / semantic-model defect
- Human intent / meaning の解釈 drift
- stale evidence、baseline、environment、population、event definition などの evidence / environment
  assumption

これらを固定された exhaustive taxonomy として扱わず、根拠が足りない場合は design defect に自動昇格しない。
attribution が未確定なら `Uncertainty` として停止する。

attribution を踏まえ、次を問う。

<!-- @anchor shared-v7-rmo-membership-relation -->
> この observed difference は、現在定義済みの Target の satisfaction を変えるか。

- **Yes** — current Target に属する discrepancy として Target-relative Problem を導出できる。
- **No** — Target を拡張せず、必要なら Incidental Finding として返して停止する。
- **Unclear** — Target semantics、authority、または observed evidence の解決が必要な `Uncertainty` として
  停止する。

Target-relative Problem は observed evidence に grounded で、Target との関係と attribution が説明でき、
current Target の scope 内にあり、solution や improvement proposal を含まない。Problem Derivation 後は
必ず停止する。観測で発見した外部の問題は、その発見だけでは current Target、continuation condition、
Improvement Candidate にならない。
<!-- @/contract -->

## Caller-owned Research Agent composition

<!-- @contract shared-v7-rmo-caller-ownership -->
<!-- @anchor shared-v7-rmo-caller-relation -->
RMO は Research Agent を dispatch しない。RMO の Required Reality Distinction に対して追加 evidence が必要
な場合、caller が bounded objective、scope、authority、relevant context / evidence surface を確定して
Research Agent に委譲してよい。Research Agent の result は evidence、source basis、execution result、
observation / inference、limitation、unresolved point を伴う caller-owned result であり、RMO の意味判断や
Problem へ自動変換されない。

caller は result の authority と semantic effect を判断し、必要なら同じ top-level invocation の同じ
task-local Local Model へ Reintegration / Recomposition する。caller はその結果の更新済み Target / Context を
RMO へ再注入し、RMO は影響を受けた distinction / signal だけを再導出して bounded に再観測する。Research Agent は第二の Local Model、独自の task semantics、continuation を
持たず、RMO もその result を理由に Target を拡張したり remediation を開始したりしない。これは Phase 1 の
`1 top-level workflow invocation = exactly 1 task-local Local Model` と caller-owned Reintegration boundary
を維持する。
<!-- @/contract -->

## Case F / G representative contrasts

| 対照 | RMO が返す意味 |
| --- | --- |
| 同じ Target / model で discrepancy がない | Observed Evidence Sufficiency が十分で、更新後 Current Reality が expected distinction を満たすなら、Problem を生成せず停止する。 |
| 同じ Target / model で discrepancy がある | まず observation と inference、conditions、Observed Evidence Sufficiency を確認し、十分な場合だけ attribution → Target Membership へ進む。 |
| membership が current Target の内側 | attribution が整合し、Target satisfaction を変える discrepancy だけを Target-relative Problem として導出し、そこで停止する。 |
| membership が current Target の外側 | Target を拡張せず、Incidental Finding として停止する。 |
| membership が未確定 | scope や Target semantics を補完せず、Uncertainty として停止する。 |
| Observed Evidence Sufficiency が不足 | discrepancy、attribution、membership、Problem を確定せず、limitation / unresolved evidence を保持して停止するか、caller-owned additional acquisition に返す。 |
| signal が ambiguous で satisfied / discrepant の両方を同じ結果に写す | Model Sufficiency を `Sufficient` とせず、grounded discriminator、conditions、gap、または unresolved viewpoint の解決へ戻す。 |
| grounded discriminator があり、admitted distinctions が cover される | proxy 条件と observation / inference を保持したうえで Model Sufficiency を評価し、`Sufficient` のときだけ authorized concrete observation へ進む。 |
| caller が RMO gap から bounded Research Agent objective を作る | caller が dispatch と authority を所有し、返却 result の authority / semantic effect を判断して同じ Local Model へ Reintegration / Recomposition する。更新済み Target / Context を RMO へ再注入した後、RMO は必要な依存 distinction / signal だけを再導出する。 |
| Research Agent が scope や Target を広げたくなる | objective、authority、Target、RMO semantics を拡張せず、limitation / unresolved point を返して停止する。RMO は implicit dispatch、第二 Local Model、remediation を持たない。 |

これらの対照は、Target-first、signal grounding、Model / Observed Evidence の二つの sufficiency、
observation / inference の分離、attribution、membership、Problem stop、および caller-owned dispatch を
同じ RMO contract から判別できることを示す。

## Conceptual reference

この consumer specialization の conceptual authority は、canonical snapshot
`2d68476142c8781bf83740b856787041beb0a3a6` の次の文書である。

- `akitanabe/model-observation-docs/docs/ja/model-observation.md`
- `akitanabe/model-observation-docs/docs/ja/applications/reality-model-observation.md`

この参照は provenance のためであり、runtime dependency や外部文書の読み込みを要求しない。RMO は Tugite の
Model Construction / Agentic Model Construction と Research Agent の current ownership boundary に適合し、
canonical 一般理論を別の固定 schema や実行 lifecycle として複製しない。
