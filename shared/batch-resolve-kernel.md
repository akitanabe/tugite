<!-- @contract batch-resolve-kernel-v1 -->
# Batch Resolve Kernel v1

Kernel identity: `batch-resolve-kernel-v1`.
Kernel dependencies: `none`.

## 適用モデル

この Kernel の適用可能性は caller 名ではなく、counterpart model と snapshot coherence で決める。一つの
Resolution Batch の全 Resolution Point が同じ origin verified snapshot を観測して生成済みで、counterpart
observation が Resolution Transaction の外側で完了し、その判断が non-binding Data であり、resolver が
caller-owned authority に従って各 point を裁定でき、transaction 中に counterpart が更新後 snapshot を再観測しない
場合に適用できる。counterpart の判断が binding である場合、または point が snapshot 更新後に逐次観測される場合は
適用しない。

## Resolution の語彙

`Resolution Point` は、caller が Resolution Transaction で裁定対象として供給する個々の論点である。finding、insight、
suggestion などの caller 固有語彙は caller が point へ mapping し、Kernel は point schema や ID を新設しない。

`Resolution Batch` は、一つの origin verified snapshot に束縛され、Resolution Transaction の開始時までに観測済みの
Resolution Point の固定集合である。transaction 中に membership を増やさず、snapshot 更新後も再計算せず、異なる
origin snapshot の point を混ぜない。空 Batch は有効だが、workflow completion を意味しない。

`Resolution Transaction` は、一つの Resolution Batch を adjudication から verified snapshot promotion または caller
boundary への返却まで扱う規範上の実行単位である。DB-style ACID transaction や batch 全体の rollback を意味せず、
atomic promotion boundary は partition とする。

## Snapshot discipline

`origin verified snapshot` は transaction 開始時の verified snapshot であり、Batch の全 point が観測された固定基準かつ
adjudication の基準である。transaction 中は不変とする。`current verified snapshot` は、transaction 内で最後に
`verify + semantic progress` を通過した状態であり、開始時は origin verified snapshot と同一で、partition promotion
ごとに更新できる。

`working state` は、一つの selected partition を current verified snapshot へ apply している未検証状態である。verify
前に current verified snapshot へ昇格させず、partition ごとに閉じ、未検証状態の上へ次 partition を積まない。

## Resolution Transaction の discipline

通常経路は次の順序とする。

```text
origin verified snapshot + caller-supplied evidence + Resolution Batch
→ adjudicate all
→ caller-owned dispositions
→ selected set
→ partition (default: single partition)
→ coherent apply
→ verify
→ semantic progress observation
→ promote current verified snapshot
```

### Adjudicate all

mutation 前に Resolution Batch 全体を裁定する純粋な Calculation とし、adjudication 中に artifact または working state を
変更しない。origin verified snapshot と transaction 開始時の caller-supplied evidence を固定 baseline として、conflict
と dependency を Batch 全体で確認する。両立不能な point を同時に selected set へ残さず、apply 開始前に全 point を
裁定済み、または caller-owned boundary へ返す対象として確定する。未裁定 point を残したまま apply へ進まない。

### Selected set、重複、dependency

`selected set` は、caller-owned disposition のうち apply 対象となる point の transaction-local な一時集合であり、public
verdict や ledger field ではない。authority または evidence が不足する point を推測で含めない。空なら mutation せず
transaction を閉じられるが、workflow completion ではない。

Resolution Point の identity と provenance は保持する。複数の selected point が同じ obligation または revision で充足
できる場合、apply effect を一つの coherent revision へ統合できるが、dedup ID、group ID、canonical finding の schema は
導入しない。dependency は adjudication 時の ordering constraint とし、dependency graph schema は新設しない。
dependency があるだけでは partition を分けず、中間 verified snapshot が必要な場合だけ分割理由になり得る。

### Partition と coherent apply

default は single partition とする。partition は execution と verification の boundary であり conflict 解決手段ではなく、
point 数や編集量だけでは分割しない。中間 verified snapshot が必要な dependency、分離しなければ安全に確認できない
verification boundary、verify failure 後の isolate を主な分割理由とする。各 partition は単独で
`verify + semantic progress + promote` しても意味的に成立する independently promotable boundary でなければならない。

apply の入力は個々の point ではなく selected partition とし、partition 全体を満たす coherent revision として working
state へ反映する。point ごとの patch 順次適用を標準モデルにせず、coherent revision を理由に新しい scope、
specification、obligation を追加しない。

### Verify、semantic progress、promotion

verify は selected obligations が意図した結果を満たすこと、caller から与えられた既知の constraints、invariants、
externally observable conditions が保存されること、partition 内の conflict と dependency の解消が反映後も成立すること
に限定する。Kernel は verification method、test schema、quality metric を新設せず、latent issue を探索しない。偶然
観測した新しい問題は evidence として caller へ返す。

verify success に加えて selected obligation に対する semantic progress を確認した場合だけ working state を current
verified snapshot へ promote する。diff があることだけを progress とせず、progress criteria は caller-owned とする。
no-progress の working state は昇格させず、同じ state、evidence、decision の表現だけを変えた retry を繰り返さない。

## 複数 partition の discipline

2つ目以降の partition は origin verified snapshot 上で裁定済みだが、更新済み current verified snapshot 上で apply
されるため、apply 前に `applicability check` を行う。adjudication や counterpart の判断を再実行せず、latent issue を
探索せず、前 partition の promotion によって selected obligation が既に充足されたか、成立前提が失われたか、新たな
conflict が成立したか、dependency condition が維持されているかだけを確認する。適用不能の evidence は corrective
adjudication に利用できる。

成功済み partition は rollback しない。後続 partition の成功がなければ成立しない変更は同じ partition に入れる。
後から先行 partition 単独では成立しないと判明した場合、partition または verification boundary の不備として
caller-owned incomplete / unresolved へ返す。Kernel は transaction-wide rollback protocol を持たない。

## Verify failure と isolate

verify failure では、failing partition を failure を局所化できるより小さい非空 subset へ `isolate` する。二分固定にせず、
resolver が conflict、dependency、verification boundary などから分割戦略を選ぶ。未検証の partition を前進させず、単一
culprit point の特定や mathematically global minimum の探索を保証しない。point interaction が原因なら failing subset
を failing unit として扱い、caller-owned execution bound 内で安全にこれ以上縮小できない subset まで局所化する。

isolate は diagnostic operation である。全 subset の diagnostic apply と verify は、failing partition が失敗する直前の
current verified snapshot を同一の isolation baseline として開始し、diagnostic working state を昇格しない。isolation 後に
caller-owned adjudication を確定し、残った selected subset は通常の `apply → verify → semantic progress → promote` で
改めて処理する。安全に進められなければ caller-owned boundary へ返し、Kernel は isolate retry count や budget を持たない。

## Corrective adjudication と evidence

通常の adjudication は mutation 前に一度だけ行う。ただし apply、verify、isolate、applicability check から transaction
内で新しい execution evidence が得られた場合に限り、元の Resolution Batch 内の point への corrective adjudication を
許す。新 evidence により caller-owned disposition を再確定できるが、元 Batch の membership 外に新しい Resolution
Point を追加せず、counterpart を再起動しない。selected set が変われば残りを改めて partition し、安全に裁定できなければ
caller-owned boundary へ返す。new evidence may revise old points, but may not create a new frontier.

transaction 開始時の adjudication baseline は origin verified snapshot、caller-supplied evidence、origin-bound Resolution
Batch の組として固定し、adjudicate 中に外部情報を再取得して暗黙更新しない。transaction 内で verify、isolate、
applicability check が生成した evidence だけを corrective adjudication に利用できる。transaction 外から新しい evidence が
入った場合は途中へ混ぜず caller boundary へ返し、必要なら caller が新しい Resolution Transaction を起動する。

## Caller boundary、authority、exit

caller は invocation boundary、resolver と counterpart の mapping、authority、execution bound、verification criteria、
既存の verdict、ledger、return vocabulary、workflow completion を所有する。Kernel は caller 名を列挙せず、invocation
前に role、authority、snapshot、return boundary が既存責務へ mapping されていなければ推測しない。

authority が不足する point を selected set に入れず、その point から独立して安全に処理できる他 point は自動停止
させない。authority 未確定 point と selected point が意味的に不可分なら caller boundary へ返す。Kernel は
workflow-level status、ledger schema、public parameter、retry count、fixed round、round orchestration を導入しない。
Transaction の close、空 Batch、空 selected set はいずれも workflow completion を意味しない。

## Counterpart observation と transaction boundary

counterpart invocation、selection、prompt、result collection は Resolution Transaction の外側に置く。更新後 snapshot を
counterpart が新たに観測した時点で、新しい Resolution Batch と Resolution Transaction とする。transaction 間の
orchestration、pass 数、round 数、ledger carry-over は caller-owned である。

## Kernel non-dependency

この Kernel は単独で適用でき、別 Kernel の存在、identity、本文、適用順、結果を成立条件にしない。複数 Kernel を併用
する場合も caller が独立して load、mapping、authority、return boundary を所有し、Kernel 間の結線を本文へ追加しない。

## review-loop caller mapping draft

この mapping は v1 freeze の設計根拠であり、review-loop 本体の integration contract ではない。

### Loader と role mapping

review-loop parent は invocation 内で最初の Resolution Transaction を開始する前に、生成後の skill directory から
skill-relative `../../references/batch-resolve-kernel.md` を読み、identity、Kernel dependencies、適用モデル、snapshot
discipline、Resolution Transaction、caller boundary の必要本文を確認する。不足、identity 不一致、必要本文の欠落、
読み取り失敗では推測せず既存の caller-owned incomplete boundary へ返す。reviewer は package 相対 path を解決しない。

caller と resolver は review-loop parent、counterpart は transaction 外で non-binding finding を返す reviewer、authority と
return boundary は親の既存責務へ mapping する。複数 reviewer の invocation と result collection はすべて transaction 外で
完了させ、親が finding を Resolution Point に正規化する。Kernel は reviewer の選択、prompt、起動、結果収集を行わない。

### Normal round

一つの review round では artifact snapshot に対する reviewer observation を transaction 外で完了し、finding を Resolution
Point、同じ snapshot の finding 集合を Resolution Batch へ mapping する。親は一つの Resolution Transaction で全 finding
を裁定し、selected set を原則一つの coherent revision として apply、verify、semantic progress、promote する。次 round
decision は review-loop-owned であり、更新済み snapshot を観測する次 round は新しい Transaction とする。

### Multiple reviewers

同じ round、同じ origin verified snapshot、同じ artifact に対する複数 reviewer の finding は、原則一つの Resolution
Batch に統合する。reviewer provenance を保持し、多数決や reviewer ごとの優先順位を導入しない。異なる snapshot の
finding は混ぜず、reviewer identity ではなく observation snapshot を Batch boundary とする。

### Parent-owned ledger と final trim

finding ledger、hold ledger、round、termination、induced-loop は review-loop parent-owned とし、Kernel は ledger を直接
更新せず、point や ledger を round 間で持ち越さない。Kernel の execution result と evidence は、親が既存の裁定結果語彙と
ledger を更新するための Data として返す。

final trim の各回も独立した Resolution Transaction へ mapping できる。reviewer、goal、回数は review-loop-owned で、各回は
その時点の verified snapshot を origin とする。一つの trim transaction の promotion 後に次の trim を行うなら、新しい
snapshot を観測する別 Transaction とする。Kernel は trim、over-engineering、count semantics を所有しない。
<!-- @/contract -->
