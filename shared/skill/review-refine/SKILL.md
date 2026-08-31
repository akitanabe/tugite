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
- optional な `final_trim_reviewer` designation。指定時は applicable な final trim にだけ適用する

生成された Skill から参照する shared Method は次の path にある。各 platform の generated path を基準に解決する。

- `../../references/model-construction.md`
- `../../references/agentic-model-construction.md`
- `../../references/reality-model-observation.md`
- `../../references/researcher-delegation.md`
- `../../references/deletion-test-method.md`

## Reviewer Action and isolation

caller / Human が指定した reviewer は minimum required set とする。current snapshot、fixed purpose / criteria、necessary evidence、remaining material risk に応じて、
追加の specialized reviewer capability を選択できる。具体的な topology、lens、agent inventory はこの Skill で固定しない。

`review-refine` 自身は reviewer を兼ねない。required reviewer または current purpose に applicable な specialized capability が成立しない場合は、
self-review で代行せず、latest verified candidate と material reason を伴う `incomplete` を返す。初回 promotion 前の latest verified candidate は `S0` である。

reviewer Action は、prior reviewer context を持たない `fresh adversarial observation` と、origin reviewer context を保つ
`contextual resolution continuation` に分ける。fresh は initial と additional の二つの起動理由を持つ。

<!-- @contract review-refine-initial-fresh -->
initial fresh は `S0`、fixed purpose / criteria、authority obligations、necessary evidence、bound が成立すれば、additional fresh 用の risk packet を要求せず起動する。
<!-- @/contract -->

<!-- @contract review-refine-fresh-input-boundary -->
fresh reviewer input は current immutable snapshot、fixed purpose / criteria、direction / authority obligations、necessary evidence、observation scope に閉じる。
<!-- @/contract -->

fresh reviewer は context-isolated observer として、次だけを受け取る。

- observation 対象の current immutable snapshot
- fixed review purpose / criteria
- direction / authority obligations
- finding を evidence-grounded にするための necessary evidence
- observation scope

fresh reviewer へ prior finding adjudication history を渡さない。rejected / out-of-scope の照合と再利用は `review-refine` が transient review context 上で所有する。

<!-- @contract review-refine-reviewer-batch -->
`reviewer Batch` は review context 内の局所 Data で、同じ current immutable snapshot に対する一つの normal-review reviewer Action の全 origin reviewer context の findings を parent が全件裁定する単位である。
continuation / additional fresh の返却は次の reviewer Batch を形成する。
<!-- @/contract -->

<!-- @contract review-refine-contextual-resolution -->
contextual resolution continuation は、同じ semantic subject、fixed purpose / criteria、origin reviewer responsibility を維持し、origin reviewer と同じ runtime instance が再利用可能な場合だけ成立する。
<!-- @/contract -->

<!-- @contract review-refine-contextual-input -->
continuation input は current immutable snapshot、prior finding identity と内容、parent adjudication、adopted coherent refinement、verification evidence、affected scope、維持された authority obligations を含む。
<!-- @/contract -->

continuation reviewer は current snapshot と repository evidence を観測基準とし、prior finding 自身や reviewer の解消主張を grounding evidence にしない。
context loss、reviewer capability 不成立、purpose / authority の material change、または continuation input 不足では eligibility は成立しない。

<!-- @contract review-refine-contextual-incomplete -->
required な origin reviewer context を継続できない場合、additional fresh で代替せず、latest verified candidate と material reason を伴う `incomplete` とする。
<!-- @/contract -->

finding、adopted refinement、affected scope、continuation eligibility、runtime identity、resolution observation state は origin reviewer context 単位で保持する。
<!-- @contract review-refine-origin-resolution -->
複数 reviewer の finding が adopted refinement に material に関係する場合は、必要な全 origin context の resolution observation を閉じる。
<!-- @/contract -->
対応する continuation capability がない reviewer を same-context continuation できると推測しない。

<!-- @contract review-refine-additional-fresh -->
additional fresh は、必要な origin resolution observation がすべて閉じた後、parent が independent observation を必要とする具体的 risk と必要 evidence を確定し、bound が残る場合だけ新しい reviewer context で起動する。
<!-- @/contract -->

同じ snapshot に対する独立 reviewer は、runtime が read-only isolation を保証できる場合だけ並列に実行できる。異なる reviewer context の result を
別 reviewer の入力へ直接 chain しない。contextual resolution は caller が origin reviewer の同じ context へ構成した bounded continuation であり、この禁止には該当しない。

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

Trigger: parent が current reviewer Batch の全 finding を裁定し、coherent adopted set、applicable な Deletion Test、workflow-owned verification と局所 correction、semantic progress の意味判断を完了して、snapshot closure を判定するとき。

Inputs: fixed purpose / criteria、origin verified snapshot identity、same-snapshot adjudication completion、coherent adopted set と optional working refinement、applicable な Deletion Test result と parent disposition、verification result、semantic progress judgment。

Procedure:

1. all-adjudicate-before-mutation、coherent apply、applicable な Deletion Test と parent disposition、verification / correction の順序 evidence が揃っていることを確認する。不足または順序違反では working state を promote しない。
2. adopted correction がある場合だけ、verification と semantic progress が成立した working state を verified snapshot に promote する。それ以外の working state は破棄し、prior latest verified snapshot を維持する。
3. adopted correction がない Batch は current verified snapshot を維持する。no-op promotion または semantic progress を作らない。

Outcomes: closure evidence と promoted または unchanged の latest verified snapshot、safe-discard evidence、または `incomplete` と latest verified candidate / material reason。順序 evidence が不足する場合も `incomplete` とする。

この Flow は working refinement の作成、verification、correction、adjudication、materiality、coherence、semantic progress、convergence、次の reviewer Action の意味判断を行わない。複数の受容可能な判断が残る箇所は parent の Agentic judgment へ返す。

### review-action-routing

<!-- @contract review-refine-review-action-entry -->
<!-- @anchor review-refine-review-action-routing-relation -->
normal-review reviewer Action selection と normal review closure の唯一の deterministic witness はこの Flow である。initial fresh は reviewer Batch closure 前の入口とし、Batch 開始後の route は `verified-promotion-control` の applicable な closure evidence を受け取った後にだけ選ぶ。
<!-- @/contract -->

Trigger: parent が initial state、または reviewer Batch の adjudication / refinement / verification closure、origin resolution observation state、normal review closure、independent observation risk を判断し、次の normal-review reviewer Action または normal review closure を判定するとき。

Inputs: `S0` / latest verified snapshot identity と applicable な promotion または safe-discard evidence、fixed purpose / criteria と authority obligations、initial fresh state、current Batch closure evidence、material unresolved state、origin reviewer context ごとの finding / affected scope / continuation eligibility / runtime availability / resolution observation state、independent observation の具体的 risk と必要 evidence、invocation-local bound state、parent-confirmed normal-review-closure judgment。

Procedure:

1. initial fresh が未実行で、`S0`、fixed purpose / criteria、authority obligations、necessary evidence、bound が成立する場合は `initial-fresh` とする。
<!-- @contract review-refine-no-correction-closure -->
2. adopted correction がある場合は、全裁定、coherent apply、applicable な Deletion Test、verification / correction、promotion または safe discard の closure evidence を確認する。不足時は `incomplete` とする。adopted correction がない Batch は全裁定の closure を確認し、current verified snapshot を維持する。
<!-- @/contract -->
3. adopted correction に対する resolution observation が未完了の origin context がある場合は、eligible かつ runtime available な全 context を `contextual-resolution` とする。required context が一つでも不成立なら `incomplete` とする。
4. continuation または additional fresh の material finding は新しい current Batch として parent の裁定、coherent correction、verificationへ戻す。adopted correction が関係する全 origin context の resolution observation が閉じるまで convergence へ進めない。
5. current Batch の裁定、adopted correction、required origin resolution、material unresolved、latest snapshot verification が閉じ、parent-confirmed normal-review-closure judgment が成立した場合は `normal-review-closed` とする。
6. required origin resolution が閉じても normal review closure が成立せず、parent-confirmed な independent observation risk と必要 evidence があり、bound が残る場合は `additional-fresh` とする。
7. additional fresh packet が成立しない material unresolved、または bound 到達では `incomplete` とする。

Outcomes: `initial-fresh`、eligible な全 origin context を伴う `contextual-resolution`、`additional-fresh`、`normal-review-closed`、または latest verified candidate と material reason を伴う `incomplete`。

この Flow は finding の意味、continuation eligibility、independent observation の必要性、normal review closure を判断せず、reviewer Action や artifact mutation を実行しない。final trim の reviewer Action と外向き `converged / incomplete` の判断は既存の後続責務に残す。全 reviewer Action は invocation-local bound の内側に置く。

## Bounded review and convergence

promotion 後は `review-action-routing` に従い、変更された semantic region、その変更で影響を受け得る dependency / boundary、前 Batch の material finding の
解消を contextual resolution で観測する。candidate の中心構造または広い responsibility boundary が変わっても、必要な origin resolution を additional fresh で代替しない。
独立した observation が必要な場合だけ、fixed purpose 内で必要な範囲を持つ additional fresh を起動する。毎回の artifact-wide full review は要求しない。

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

<!-- @contract review-refine-final-trim-reviewer -->
`final_trim_reviewer` が指定された場合、applicable な final trim はその reviewer capability を使い、未指定なら既存の reviewer selection を維持する。`final_trim = off` では適用しない。
<!-- @/contract -->

指定された reviewer capability が成立しない場合は、self-review や別 reviewer への暗黙の切り替えをせず `incomplete` とする。この designation は final trim phase にだけ適用し、normal review の required reviewer、specialized capability selection、round routing へ流用しない。

`applicable` の場合は concrete removal candidate を Deletion Test Method で個別に Test し、`preserves` の候補から作った coherent selected deletion set 全体を
一つの candidate として再 Test する。parent が採用した set だけを working trim に反映し、verification 成功後に promote する。

final trim は原則一 pass とし、trim 自身が new material over-engineering を明確に露出した場合だけ invocation bound 内で bounded additional trim を許可する。
normal review loop へ戻らない。input / evidence が不足する、または pre-existing material defect のため normal review responsibility の再開が必要なら、
unsafe working trim を破棄し、直前の latest verified candidate と `incomplete` を返す。

## Transient context and output

transient review context では origin reviewer context ごとの finding identity / provenance、observation snapshot、4値 adjudication と reason、unresolved materiality、
adopted finding と refinement / affected scope の対応、continuation eligibility、runtime identity、resolution observation state、verified snapshot progression を追跡可能にする。canonical fixed ledger schema、persistent review-history artifact、
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
- all-finding mandatory RMO、異なる reviewer context 間の result の direct chaining、`review-refine` による self-review
- review scope の自律拡張、Human interaction の開始、external persistent write、downstream workflow start
- review の都合による新しい verification framework / test architecture
- caller 指定なしの final trim、fixed multi-pass trim、final trim から normal review loop への復帰
