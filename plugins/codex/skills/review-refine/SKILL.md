---
name: review-refine
description: >-
  明示された artifact review、または plan-family public workflow からの明示起動で、verified snapshot に対する
  evidence-grounded review、parent-owned adjudication、coherent refinement、verification、bounded re-review を行い、
  converged または incomplete と latest verified candidate を返す。
---
<!-- Generated from shared/. Do not edit directly. -->

# review-refine

`review-refine` は artifact / proposal / plan などの immutable な verified snapshot を基準に、fixed purpose / criteria の内側で
review、finding adjudication、coherent refinement、verification、bounded re-review を閉じる public workflow である。
standalone の artifact review、または plan-family public workflow parent から明示された nested invocation でだけ開始する。

## Identity and invocation

initial verified snapshot `S0` は content identity、invocation 中に不変な artifact bytes、baseline verification evidence を持つ。
成立しなければ review を開始せず、不足と安全に返せる candidate の有無を caller に返す。

```text
standalone → exactly one task-local Local Model
nested → caller-owned Local Model projection; no local construction
both → `S0` / purpose / criteria / authority obligations fixed at invocation boundary
```

standalone では `S0`、review request、利用可能な evidence context から Agentic Model Construction を行い、current review purpose /
criteria / evidence context と exactly one の task-local Local Model を解決して所有する。nested では caller-owned Local Model の
consumer-specific projection、解決済み purpose / criteria、必要な evidence context、`S0` を受け取り、独自 Local Model を作らない。
どちらも finding の発見だけを理由に scope を拡張せず、固定した purpose / criteria / authority obligations が失われて安全に再解決できなければ
`incomplete` とする。

invocation Data は、review request と artifact responsibility、`S0` と baseline evidence、construction context または Local Model
projection、required reviewer と利用可能な specialized capability / evidence surface、caller 指定または invocation-local な operational
bound、`final_trim = off | applicable` と applicable 時の final-trim context、applicable 時の final-trim context とは別の `caller-owned final-trim validity / stop result`、optional な `final_trim_reviewer` である。

caller-owned opaque final-trim context（plan-family では necessity context と comparison frame を含む具体形）を受領した場合、review-refine は invocation 中に欠落なく保持し、意味を再分類・再判定せず designated reviewer へ同じ context と frame を渡す。

この context と frame は `S0` とは別の caller Data です。review-refine はその分類、integrity、completeness、materiality、target、base を解釈・再判定せず、
欠落・置換・推測も行いません。plan 固有の whole-candidate / base / evidence selection と necessity semantics は Planning Core に残します。

shared Method は generated path を基準に次を解決する。

- `../../references/model-construction.md`
- `../../references/agentic-model-construction.md`
- `../../references/reality-model-observation.md`
- `../../references/researcher-delegation.md`
- `../../references/deletion-test-method.md`

## Reviewer actions

caller / Human 指定 reviewer は minimum required set であり、current snapshot、fixed purpose / criteria、necessary evidence、remaining
material risk に応じて specialized capability を追加できる。topology、lens、agent inventory は固定しない。reviewer は findings だけを返し、
parent `review-refine` が adjudication、refinement、routing、completion を所有する。`review-refine` 自身は reviewer を兼ねず、required
capability が成立しなければ self-review せず、latest verified candidate と material reason を伴う `incomplete` とする。初回 promotion 前の
latest verified candidate は `S0` である。

```text
reviewer → findings
parent → adjudication / refinement / routing / completion
initial-fresh → `S0` + fixed review packet → fresh context
contextual-resolution → required origin context + continuation packet → same runtime context; unavailable: `incomplete`
additional-fresh → all required origin resolutions closed + independent risk + evidence + remaining bound → fresh context
```

`initial-fresh` は `S0` と fixed purpose / criteria / authority obligations / necessary evidence / bound が成立すれば起動する。
`additional-fresh` は必要な origin resolution を閉じた後に、parent が確定した concrete independent risk、必要 evidence、remaining
bound がある場合だけ起動する。fresh reviewer input は current immutable snapshot、fixed purpose / criteria、direction / authority
obligations、necessary evidence、observation scope に閉じ、prior adjudication history を渡さない。

fresh reviewer を起動する場合は `fork_turns = "none"` を指定する。

`contextual-resolution` は同じ semantic subject、fixed purpose / criteria、origin responsibility を維持し、origin reviewer の同じ runtime
context を再利用できる場合だけ成立する。continuation packet は current immutable snapshot、prior finding identity / content、parent
adjudication、adopted coherent refinement、verification evidence、affected scope、authority obligations を持つ。current snapshot と
repository evidence を grounding とし、prior finding や解消主張を evidence の代わりにしない。

adopted refinement に material に関係する全 origin context の resolution を閉じる。context loss、capability 不成立、purpose / authority
の material change、または packet 不足により required origin context を継続できなければ、fresh reviewer で代替せず `incomplete` とする。
finding、adjudication、adopted refinement、affected scope、continuation eligibility、runtime identity、resolution state は origin context
ごとに追跡する。

同じ snapshot の独立 reviewer は runtime が read-only isolation を保証する場合だけ並列実行できる。異なる reviewer context の result は
直接 chain しない。同じ origin context への bounded continuation はこの制約を満たす。additional fresh の scope は confirmed risk の観測に
必要な範囲に閉じ、修正確認ごとの artifact-wide fresh review を要求しない。

## Round adjudication and promotion

一つの reviewer action が同じ current immutable snapshot に返した finding set を current round findings とする。各 round は `S0` または
latest verified snapshot を origin snapshot に固定し、finding の evidence grounding、observation snapshot、provenance を保持する。

finding の grounding、Target membership、attribution が不足または競合する場合だけ RMO を利用し、Problem Derivation で停止した result を
parent adjudication の evidence とする。

```text
same immutable snapshot findings → all `adopted / rejected / out-of-scope / unresolved` adjudications
all adjudications → coherent refinement → mutation
```

parent は mutation 前に全 finding を4値裁定する。`adopted` は current criteria を成立させる refinement、`rejected` は evidence /
requirements / candidate semantics 上採用しない finding、`out-of-scope` は成立し得るが current responsibility 外、`unresolved` は
安全に裁定できず reason と materiality を保持する finding である。adopted set の conflict / dependency を解消して single coherent
refinement として working state へ反映する。material unresolved は `incomplete`、non-material unresolved は remaining issue とする。

adopted refinement が concrete deletion を含む場合は Deletion Test Method を利用する。result は observation であり、採否、apply、
verification、snapshot promotion は `review-refine` が所有する。

working state の verification は、adopted finding の反映、fixed purpose / criteria、relevant obligations / constraints、既存 verification
surface と caller-supplied evidence の整合を確認する。review のために新しい verification framework / test architecture を作らない。
局所 correction は同じ working refinement 内で再検証し、新しい round にしない。

meaningful semantic progress は current purpose / criteria に対する material issue / unresolved の減少、verification 成立性の向上、
同等以上の material risk を新たに誘発していないことから parent が判断する。risk の移動、同型 finding の再発、risk の増幅だけでは
promote しない。

## Normal review routing

次の Programmatic Flow は固定 procedure、condition、outcome だけを所有する。adjudication、coherence、materiality、semantic progress、
continuation eligibility、independent risk、normal closure の意味判断と artifact mutation は parent が先に行い、Flow はそれを置換しない。

### verified-promotion-control

Trigger: parent が current round の全 finding、coherent adopted set、applicable な Deletion Test disposition、verification / correction、
semantic progress を確定し、snapshot closure を要求するとき。

Inputs: origin verified snapshot identity、adjudication closure、coherent adopted set / optional working state、Deletion Test disposition、
verification result、semantic progress judgment。

Procedure: 次を上から評価する。

```text
no adopted refinement → keep current verified snapshot
adopted refinement + verification + semantic progress → promote
otherwise → discard working state; keep prior verified snapshot; `incomplete`
```

Outcomes: promoted または unchanged の latest verified snapshot と closure evidence、safe-discard evidence、または latest verified candidate /
material reason を伴う `incomplete`。

### review-action-routing

Trigger: initial state、または adjudication / refinement / verification closure 後に、parent が origin resolution state、normal closure、
independent risk を確定して次の normal-review action を要求するとき。

Inputs: `S0` / latest verified snapshot identity と closure evidence、fixed purpose / criteria / authority obligations、initial state、origin
context ごとの eligibility / runtime availability / resolution state、normal closure judgment、independent risk / evidence、bound state。

Procedure: 次を上から評価する。

```text
initial fresh pending → `initial-fresh`
required origin resolution pending → all eligible `contextual-resolution`; unavailable: `incomplete`
normal review closed → `normal-review-closed`
independent risk + evidence + remaining bound → `additional-fresh`
otherwise → `incomplete`
```

Outcomes: `initial-fresh`、eligible な全 origin context を伴う `contextual-resolution`、`additional-fresh`、
`normal-review-closed`、または latest verified candidate / material reason を伴う `incomplete`。

continuation / additional fresh が material finding を返した場合は、それを次の current round findings として全件裁定する。required origin
resolution を閉じるまで convergence へ進めない。`rejected / out-of-scope` は evidence、candidate semantics、fixed criteria との関係が
material に変わり、従来の adjudication basis が無効になった場合だけ reopen する。

caller 指定の operational bound に従い、未指定でも invocation-local bound を持つ。fixed canonical round count や quality threshold にはせず、
bound 到達を convergence に変換しない。

normal closure は current round の裁定、required origin resolution、material / actionable findings、latest snapshot verification が閉じたという
parent judgment である。

```text
normal closure + no material unresolved + verified candidate + no pending refinement + applicable final trim complete → `converged`
otherwise at stop → `incomplete`
```

外向き status は `converged / incomplete` の2値である。

## Final trim

`final_trim` は default `off` である。caller が `applicable` と final-trim context を渡した場合だけ normal
closure 後に実行し、`review-refine` は applicability を追加・変更しない。

final-trim stage では `caller-owned final-trim validity / stop result` が進行可能なら latest verified snapshot 全体を caller が指定した target と comparison frame に bind し、進行不可ならその stop result に従う。

review-refine は context / comparison frame の分類、integrity、completeness、materiality、
whole-candidate / base / evidence selection を決めず、opaque context を解釈・再判定しません。plan 固有 semantics を normal review や別 caller の一般契約へ拡張しません。

```text
off → skip
applicable → designated reviewer or existing selection → one pass
new material over-engineering exposed by trim + remaining bound → one additional pass
capability / input / verification failure → `incomplete`
final trim → never normal review
```

`final_trim_reviewer` 指定時はその capability を優先し、未指定なら既存 selection を維持する。`off` では designation を適用しない。
指定 capability を利用できなければ self-review や別 reviewer へ切り替えない。designation は final trim にだけ適用し、normal review の required
reviewer、specialized selection、routing へ流用しない。

concrete deletion には Deletion Test Method を利用する。result は observation であり、採否、apply、verification、promotion は
`review-refine` が所有する。final trim は原則一 pass とし、trim が新しい material over-engineering を露出した場合だけ remaining bound 内で
一回の additional pass を許す。input / capability / verification が不足する、または normal review responsibility の再開が必要なら working trim
を破棄し、直前の latest verified candidate と `incomplete` を返す。

## Result and responsibility

transient context は finding と origin snapshot、adjudication、adopted refinement、origin reviewer context、resolution state、verified
snapshot progression の関係を追跡可能にする。固定 ledger、persistent review history、invocation 後の persistence は要求しない。

caller-actionable な current result として status、latest verified candidate、adopted changes、remaining issues / materiality、
`incomplete` reason、applicable な final trim state を返す。raw output や全履歴を標準 result にせず、未検証 working state を返却 candidate に
昇格させない。

```text
review-refine → invocation-local review / adjudication / refinement / verification / completion
caller → persistence / publication / adoption / downstream workflow
Human interaction / external persistent write → not owned by review-refine
```

caller は returned candidate の保存、公開、採用、後続 workflow を所有する。finding や `converged` はその authority を拡張しない。
