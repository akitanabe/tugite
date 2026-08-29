---
name: review-refine
description: >-
  明示された artifact review、または plan-family public workflow からの明示起動で、verified snapshot に対する
  evidence-grounded review、parent-owned adjudication、coherent refinement、verification、bounded re-review を行い、
  converged または incomplete と latest verified candidate を返す。
---

# review-refine
<!-- @anchor review-refine-document -->

`review-refine` は、artifact / proposal / plan などの immutable な verified snapshot を基準に、fixed purpose / criteria の内側で
review → finding adjudication → coherent refinement → verification → bounded re-review を閉じる public workflow である。
ユーザーが artifact review を明示した standalone invocation、または明示起動された plan-family public workflow parent からの nested invocation でだけ開始する。

## Invocation and Local Model ownership

有効な invocation は initial verified snapshot `S0` を必要とする。`S0` は少なくとも content identity、invocation 中に不変な artifact bytes、
baseline verification evidence を持つ。これらが成立しない場合は review loop を開始せず、不足と安全に返せる candidate の有無を caller に返す。

<!-- @contract review-refine-local-model -->
<!-- @anchor review-refine-local-model-relation -->
- standalone invocation では、`review-refine` が `S0`、review request、利用可能な evidence context から Agentic Model Construction を行い、exactly one の task-local Local Model と、current review purpose / criteria / evidence context を解決して所有する。
- nested invocation では、caller-owned Local Model の consumer-specific projection、解決済み review purpose / criteria、必要な evidence context、`S0` を受け取り、独自 Local Model を作らない。
<!-- @/contract -->

どちらの route でも purpose / criteria は invocation boundary で固定する。finding の発見だけを理由に scope を拡張しない。
purpose / criteria の成立性が失われ、安全な継続に必要な解決を Agent-side で得られない場合は `incomplete` とする。

caller は次の invocation Data を必要な範囲で渡す。

- review request と current artifact responsibility
- `S0` と baseline verification evidence
- standalone の construction に利用できる evidence context、または nested の Local Model projection と解決済み purpose / criteria
- caller / Human が指定した required reviewer
- 利用可能な specialized reviewer capability と必要な evidence surface
- user / caller 指定の operational bound。未指定なら invocation-local な bounded execution condition
- `final_trim = off | applicable`。`applicable` の場合は obligations / constraints / evidence context

生成された Skill から参照する shared Method は次の path にある。各 platform の generated path を基準に解決する。

- `../../references/model-construction.md`
- `../../references/agentic-model-construction.md`
- `../../references/reality-model-observation.md`
- `../../references/researcher-delegation.md`
- `../../references/deletion-test-method.md`

## Reviewer selection and isolation

caller / Human が指定した reviewer は minimum required set とする。current snapshot、fixed purpose / criteria、necessary evidence、remaining material risk に応じて、
追加の specialized reviewer capability を選択できる。具体的な topology、lens、agent inventory はこの Skill で固定しない。

`review-refine` 自身は reviewer を兼ねない。required reviewer または current purpose に applicable な specialized capability が成立しない場合は、
self-review で代行せず、latest verified candidate と material reason を伴う `incomplete` を返す。初回 promotion 前の latest verified candidate は `S0` である。

reviewer は stateless / context-isolated observer として、次だけを受け取る。

- observation 対象の current immutable snapshot
- fixed review purpose / criteria
- finding を evidence-grounded にするための necessary evidence

prior finding adjudication history は原則渡さない。rejected / out-of-scope の照合と再利用は `review-refine` が transient review context 上で所有する。
同じ snapshot に対する独立 reviewer は、runtime が read-only isolation を保証できる場合だけ並列に実行できる。reviewer result を別 reviewer の入力へ直接 chain しない。

## Finding adjudication and coherent refinement

各 round は `S0` または latest verified snapshot を origin verified snapshot として固定する。同じ origin snapshot に対する findings を収集し、
必要な evidence grounding、observation snapshot、finding provenance を保持する。

grounding が adjudication に不足する、evidence が競合する、または independent Reality observation が必要な場合だけ、additional observation / RMO を利用する。
reviewer finding 自身を grounding evidence にせず、全 finding を mandatory RMO route へ通さない。RMO は Problem Derivation で停止し、finding の採否は親へ残す。

<!-- @contract review-refine-adjudication -->
<!-- @anchor review-refine-adjudication-relation -->
同じ origin verified snapshot に対する findings は mutation 前に全件を `adopted / rejected / out-of-scope / unresolved` の4値へ parent `review-refine` が裁定し、adopted set 全体の conflict / dependency を解消してから single coherent refinement として working state へ反映する。
<!-- @/contract -->

- `adopted`: current purpose / criteria を成立させる refinement として採用する。
- `rejected`: evidence、current requirements、candidate semantics に照らして採用しない。
- `out-of-scope`: finding は成立し得るが、current purpose / criteria の変更責務に含めない。
- `unresolved`: current loop 内で安全に裁定を確定できない。reason と materiality を保持する。

material unresolved は convergence を阻害し、latest verified candidate とともに `incomplete` を返す。non-material unresolved は remaining issue として保持し、
他の convergence condition が成立する場合の完了を妨げない。`review-refine` 自身は Human interaction を開始しない。

concrete deletion を含む adopted refinement は Deletion Test Method を使う。Method の observation result は parent adjudication の代替ではなく、
`deletion breaks obligations` または `indeterminate` の deletion を自動採用しない。

## Verification and snapshot promotion

working state と verified snapshot を分ける。`review-refine` は refinement の verification を所有し、少なくとも次を確認する。

- adopted finding が意図どおり反映されたこと
- fixed purpose / criteria が維持されていること
- relevant obligations / constraints が維持されていること
- applicable な既存 verification surface と caller-supplied evidence が整合すること

review の都合だけで新しい verification framework / test architecture を作らない。verification failure が current purpose 内で局所解決可能なら、
同じ working refinement の correction → re-verification として扱い、新しい review round にしない。

<!-- @contract review-refine-promotion -->
<!-- @anchor review-refine-promotion-relation -->
working state は、workflow-owned verification と meaningful semantic progress の両方が成立した後だけ verified snapshot へ promote し、failure を安全に閉じられない場合は working state を破棄して prior latest verified snapshot を維持する。
<!-- @/contract -->

semantic progress は current purpose / criteria に対して candidate が実質的により成立したかで判断する。material issue の解消、material unresolved の減少または
非 material 化、verification の成立性向上、同等以上の material risk を新たに誘発していないことを evidence として使える。
risk の移動、同型 finding の再発、risk の増幅だけで progress を説明できない場合は promote せず `incomplete` とする。

## Programmatic Flow

### verified-promotion-control

Trigger: parent が same-snapshot findings を全裁定し、coherent adopted set の working refinement、applicable な Deletion Test、workflow-owned verification と局所 correction、semantic progress の意味判断を完了して、snapshot promotion を判定するとき。

Inputs: fixed purpose / criteria、origin verified snapshot identity、same-snapshot adjudication completion、coherent adopted set と working refinement、applicable な Deletion Test result と parent disposition、verification result、semantic progress judgment、operational bound state。

Procedure:

1. all-adjudicate-before-mutation、coherent apply、applicable な Deletion Test と parent disposition、verification / correction の順序 evidence が揃っていることを確認する。不足または順序違反では working state を promote しない。
2. verification と semantic progress が成立した場合だけ working state を verified snapshot に promote する。それ以外は working state を破棄し、prior latest verified snapshot を維持する。
3. promoted snapshot で operational bound が残る場合は affected semantics の bounded re-review へ渡す。未収束のまま bound に達した場合は latest verified snapshot と `incomplete` を返す。

Outcomes: `next-round` と promoted verified snapshot、または `incomplete` と latest verified candidate / material reason。順序 evidence が不足する場合も `incomplete` とする。

この Flow は working refinement の作成、verification、correction、adjudication、materiality、coherence、semantic progress、convergence の意味判断を行わない。複数の受容可能な判断が残る箇所は parent の Agentic judgment へ返す。

## Bounded re-review and convergence

promotion 後は、変更された semantic region、その変更で影響を受け得る dependency / boundary、前 round の material finding の解消を中心に re-review する。
candidate の中心構造または広い responsibility boundary が変わった場合だけ、fixed purpose 内で必要な範囲まで広げる。毎 round の artifact-wide full review を要求しない。

`rejected / out-of-scope` は、relevant evidence、candidate semantics、または fixed purpose / criteria との意味関係が material に変わって
従来の adjudication basis が invalidated した場合だけ reopen する。同じ finding の再出現だけでは reopen しない。

user / caller 指定の operational bound があれば従う。未指定でも invocation-local な execution bound を持つが、fixed canonical round count や
quality condition にはしない。bound 到達時に未収束なら `incomplete` とし、round 消化を `converged` に変換しない。

<!-- @contract review-refine-convergence -->
<!-- @anchor review-refine-convergence-relation -->
外向き status は `converged / incomplete` の2値とし、`converged` は material / actionable finding の収束、material unresolved なし、latest candidate の verified snapshot 化、meaningful refinement の未処理なし、および applicable な final trim の完了がすべて成立した場合だけ選ぶ。
<!-- @/contract -->

## Final trim

`final_trim` は default `off` とする。caller が `applicable` と、trimming に必要な obligations / constraints / evidence context を渡した場合だけ、
normal convergence 後の subtractive final phase として実行する。`review-refine` は applicability を自律的に追加・変更しない。

`applicable` の場合は concrete removal candidate を Deletion Test Method で個別に Test し、`preserves` の候補から作った coherent selected deletion set 全体を
一つの candidate として再 Test する。parent が採用した set だけを working trim に反映し、verification 成功後に promote する。

final trim は原則一 pass とし、trim 自身が new material over-engineering を明確に露出した場合だけ invocation bound 内で bounded additional trim を許可する。
normal review loop へ戻らない。input / evidence が不足する、または pre-existing material defect のため normal review responsibility の再開が必要なら、
unsafe working trim を破棄し、直前の latest verified candidate と `incomplete` を返す。

## Transient context and output

transient review context では finding identity / provenance、observation snapshot、4値 adjudication と reason、unresolved materiality、
adopted finding と refinement の対応、verified snapshot progression を追跡可能にする。canonical fixed ledger schema、persistent review-history artifact、
invocation 終了後の persistence は要求しない。

`converged / incomplete` のどちらでも、次の current result を caller-actionable な範囲で返す。

- status
- latest verified candidate
- adopted changes の要約
- out-of-scope と unresolved / materiality を含む remaining issues
- `incomplete` の material issue / reason
- applicable な場合の final trim state

全 round history、reviewer raw output、rejected finding 全件、snapshot 全履歴は標準 output にしない。未検証 working state を返却 candidate へ昇格させない。

## Responsibility boundary

<!-- @contract review-refine-responsibility -->
<!-- @anchor review-refine-responsibility-relation -->
`review-refine` は invocation-local candidate の review / adjudication / refinement / verification / completion を所有するが、Human interaction の開始、external resource への persistent write、downstream workflow の開始を所有しない。
<!-- @/contract -->

caller は returned candidate の保存、公開、採用、後続 workflow の開始を所有する。review finding や `converged` はその authority を拡張しない。

## Non-goals

- generic review framework、universal reviewer、固定 reviewer topology / lens / inventory
- canonical finding ledger、persistent review history、全 snapshot history
- fixed normal round count、fixed no-progress threshold、dedicated termination taxonomy
- all-finding mandatory RMO、reviewer result の direct chaining、`review-refine` による self-review
- review scope の自律拡張、Human interaction の開始、external persistent write、downstream workflow start
- review の都合による新しい verification framework / test architecture
- caller 指定なしの final trim、fixed multi-pass trim、final trim から normal review loop への復帰
