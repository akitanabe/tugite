<!-- @only claude -->
---
name: plan-candidate-producer
description: >-
  plan-family public workflow parent の同じ context 内だけで、要求と repository の観測から計画 candidate を起草または洗練し、
  read-only advisor の非拘束な insight を裁定して candidate snapshot または stop-incomplete を caller-owned parent へ返す internal skill。
user-invocable: false
---
<!-- @/only -->
<!-- @only codex -->
---
name: plan-candidate-producer
description: >-
  plan-family public workflow parent の同じ context 内だけで、要求と repository の観測から計画 candidate を起草または洗練し、
  read-only advisor の非拘束な insight を裁定して candidate snapshot または stop-incomplete を caller-owned parent へ返す internal skill。
---
<!-- @/only -->
<!-- @only cursor -->
---
name: plan-candidate-producer
description: >-
  plan-family public workflow parent の同じ context 内だけで、要求と repository の観測から計画 candidate を起草または洗練し、
  read-only advisor の非拘束な insight を裁定して candidate snapshot または stop-incomplete を caller-owned parent へ返す internal skill。
---
<!-- @/only -->

# plan-candidate-producer

<!-- @contract plan-candidate-producer-internal-guard -->
## 位置づけと発火

この Skill は plan-family public workflow parent の同じ context 内だけで使う internal skill であり、ユーザーから直接起動しない。
要求、repository、既存仕様を観測して計画 candidate を起草または洗練する producer を担う。
自身は実装、委譲、worktree 操作、保存、最終受入を行わず、caller-owned parent へ判断材料を返す。
<!-- @/contract -->

## 入力と観測

親から次の Data を受け取る。

- `request`: 要求原文、目的、成功条件、scope、exclude、制約、既知の依存。
- `repository_observation`: current state、既存仕様、関連成果物、検証可能な境界。
- `caller_context`: public workflow parent が同じ context で保持する判断と、必要なら既存の current verified candidate snapshot。
- `authority`: `discretionary | constrained`。
- `authority_constraints`: constrained invocation で保護する `id`、`frozen_meaning`、`source_evidence` の全件。discretionary では空とする。

要求、対象、成功条件、scope、exclude、依存、制約の不足または矛盾が品質を変える場合は推測せず、
`stop-incomplete` として必要な判断を返す。軽微な不足は根拠付き `assumptions` として分離する。

## Programmatic Flows

<!-- @contract plan-candidate-producer-programmatic-flows -->
以下は、親が意味判断を完了して確定 Data を渡した後の局所的な deterministic procedure だけを持つ。
Flow の procedure、条件、outcome は固定であり、Agent は override、bypass、置換しない。outcome の後に複数の妥当な Action が残る意味判断は Agentic な親へ返す。
<!-- @/contract -->

<!-- @contract producer-invocation-preflight -->
### producer-invocation-preflight

<!-- @anchor producer-preflight-trigger -->
Trigger: 親が plan-candidate-producer invocation を開始し、固定 preflight の実行を要求したとき。
<!-- @anchor producer-preflight-inputs -->
Inputs: 親が注入した batch-resolve-kernel v1 の Loader Data、authority、authority_constraints。
<!-- @anchor producer-preflight-procedure -->
Procedure: batch-resolve-kernel loader を invocation start に一度だけ検証し、必要本文と identity / required_sections / failure / owner / delegate_path_resolution を確認する。authority の列挙 / shape / identity / traceability は fixed validation として扱う。candidate content と Claim の採否・意味判断をこの Flow に入れない。
<!-- @anchor producer-preflight-outcomes -->
Outcomes: 検証済み preflight Data、または `stop-incomplete`。loader / authority failure は突破せず、candidate content と Claim の意味判断は Agentic な親へ返す。
<!-- @/contract -->

<!-- @contract candidate-reality-grounding -->
### candidate-reality-grounding

<!-- @anchor producer-grounding-trigger -->
Trigger: working candidate draft の change model が形成され、initial verified candidate S0 として verify / promote する直前。または、既に grounding closure を満たした candidate について、change model の identity / central semantics の material change、または新しい grounded evidence / context / constraint により既存 Observable Reality Model / discrepancy derivation が無効化されたと producer が確認したとき。invocation が新しいこと自体、wording、根拠の整理、同じ change model 内の局所的具体化は trigger にしない。
<!-- @anchor producer-grounding-inputs -->
Inputs: working candidate 全体から解決した単一の candidate change-model Target。request、Human-confirmed / frozen specification、repository contract / invariant、caller-confirmed constraint。repository current state、code / config / schema、existing tests、verification surface など独立した observable evidence。candidate が前提にする dependency / constraint。再 grounding では、検証可能な直前 closure と、それが依存した Target / evidence / context / constraint、および今回の変更差分。candidate は Target semantics / evaluation subject としてのみ使い、自身の正しさを示す evidence にしない。
<!-- @anchor producer-grounding-procedure -->
Procedure: Flow owner は後述 Loader Data で `reality-model-observation-kernel-v1` と必要 section を検証してから RMO を実行する。失敗時は推測せず既存 `stop-incomplete` へ返す。1 candidate = 1 change-model Target と authoritative context / observable evidence capability を解決し、step / Claim 単位へ Target を分割しない。raw semantic result を transient な Data として Agentic な producer parent へ返す。parent の Claim 導出・裁定・反映は Flow 外で行い、その後に invalidation condition と closure condition を固定確認する。central semantics または derivation が再び無効化された場合だけ再 grounding する。
<!-- @anchor producer-grounding-outcomes -->
Outcomes: grounding closure を満たし、S0 の verify / promotion または既存 advisor flow への復帰が可能な candidate。Agent 権限内の追加観測で解消できない material な evidence gap のため、安全な verify / recommend ができない `stop-incomplete`。loader / identity / required section failure または検証不能な過去 closure による既存 incomplete 結果。
<!-- @/contract -->

<!-- @contract advisor-two-pass-orchestration -->
### advisor-two-pass-orchestration

<!-- @anchor advisor-two-pass-trigger -->
Trigger: 親が検証済み candidate S0 と advisor invocation の固定実行を確定したとき。
<!-- @anchor advisor-two-pass-inputs -->
Inputs: 親確定の verified candidate S0、fresh-context advisor #1 / #2 の invocation Data、検証済み kernel / role / Resolution Transaction Data、親が loop 開始時に選択・固定した resolution execution bound。
<!-- @anchor advisor-two-pass-procedure -->
Procedure: 次の唯一の順序を実行する。
candidate S0
→ fresh-context advisor #1
→ Resolution Batch #1
→ Resolution Transaction #1 closure
→ verified candidate S1
→ fresh-context advisor #2
→ Resolution Batch #2
→ Resolution Transaction #2 closure
→ verified candidate S2
→ complete
各 advisor output は得た時点で Agentic な親へ返す。親は insight の採否、Resolution Batch の確定、Resolution Transaction の裁定と closure、verify、semantic progress を既存の唯一の正本に従って行い、その結果 Data を次の固定 step へ再投入する。Flow は insight の採否、Transaction 内部、verify または semantic progress の値を決めず、これらの intermediate result を initial Inputs として要求しない。
Batch または selected set が空でも第2 passを必ず起動し、該当しなければ空 Batch として第2 Transaction を閉じる。第2 pass後に第3 passを起動しない。第2 pass の insight は既存の non-binding output から Resolution Point へ mapping する。advisor invocation は exactly 2 pass とする。
<!-- @anchor advisor-two-pass-outcomes -->
Outcomes: verified candidate S2 と `complete`、または `stop-incomplete`。第2 passの insight採否、Transaction内部、semantic progress は Flow 外で親が判断する。
<!-- @/contract -->

<!-- @contract plan-candidate-producer-batch-resolve-kernel-loader -->
## batch-resolve-kernel v1 の parent mapping

<!-- @anchor plan-candidate-producer-batch-resolve-kernel-loader-start -->
次の Loader Data が列挙値の唯一の正本である。

```text
path = ../../references/batch-resolve-kernel.md
load_timing = once at plan-candidate-producer invocation start
identity = batch-resolve-kernel-v1
dependencies = none
required_sections = [適用モデル, Snapshot discipline, Resolution Transaction, Caller boundary]
failure = stop-incomplete
owner = plan-candidate-producer parent
delegate_path_resolution = false
```

`producer-invocation-preflight` がこの Loader Data を消費する唯一の loader procedure である。この section は列挙 Data の mapping だけを提供し、load / identity / required section / failure routing を再定義しない。
<!-- @anchor plan-candidate-producer-batch-resolve-kernel-use -->
検証済み本文だけを、以降の Resolution Transaction の既存の `判定基準` または `必要な周辺 context` に注入する。
<!-- @/contract -->

<!-- @contract plan-candidate-producer-batch-resolution-role-mapping -->
## batch-resolve-kernel v1 の role mapping

次の role Data が列挙値の唯一の正本である。

```text
caller = plan-family public workflow parent
resolver = plan-candidate-producer planner
counterpart = plan-quality-advisor
target_snapshot = origin verified candidate snapshot
insight = Resolution Point
same_snapshot_insights = Resolution Batch
authority = discretionary | constrained
authority_constraints = immutable invocation Data injected by public parent
authority_source = injected Data only; never caller identity
ledger = adoption ledger
```

親は上記 role field を使って既存責務へ mapping する。counterpart observation Action は Resolution Transaction 外の
one-shotとし、resolver が要求、一次情報、current verified snapshot を基準に裁定する。

この batch-resolve-kernel mapping は Reality Model Observation および Deletion Test Method と独立した規範である。
RMO Derived Problem を Resolution Point にせず、RMO を closed Batch の内側へ挿入せず、Batch membership / semantics を変更しない。
互いの本文を前提にせず、相互の読み込み順に依存させない。

### authority の開始前 validation

plan-candidate-producer は caller 名から authority または振る舞いを選ばず、親が注入した Data だけに従う。`authority` が列挙外なら
working state、advisor、Resolution Transaction を開始せず `stop-incomplete` とする。`constrained` では開始前に
全 `authority_constraints` の shape、非空で一意な `id`、一意に解釈できる `frozen_meaning`、解決可能な
`source_evidence`、全件の traceability を検証する。集合が空、欠落、不正、重複、余分、または曖昧な場合は開始前
`stop-incomplete` とする。検証済み constraints は item identity、意味、source evidence を含む invocation Data 全体を
immutable とし、plan-candidate-producer 内で再生成・追加・削除・置換しない。

```text
constrained_validation_timing = before working state / advisor / Resolution Transaction
constraint_failure_cases = [missing, invalid, ambiguous, duplicate, extra, identity regeneration, meaning-evidence mismatch]
constraint_failure = stop-incomplete before refinement
```
<!-- @/contract -->

<!-- @anchor plan-candidate-producer-verified-baseline-start -->
<!-- @contract plan-candidate-producer-verified-snapshot-baseline -->
## current verified candidate の caller mapping

`caller_context` で既存 candidate を受け取る場合は current verified candidate snapshot を S0 とし、一から再起草せず、未検証の working state を
baseline にしない。過去の grounding closure とその依存を既存 caller / process evidence から検証できる場合だけ、その closure を差分比較に使う。検証不能な既存 verified candidate は grounding 済みと推測せず、invocation identity だけを理由に RMO を無条件再実行せず、既存の incomplete 境界へ返す。
初回は要求、一次情報、観測可能な条件から working candidate を起草し、`candidate-reality-grounding` の grounding closure を満たしたうえで、それらに対する verify の成功と semantic progress の確認後にだけ、初期 current verified snapshot として確立する。
各改善は working state へ apply し、verify と semantic progress が成功した後にだけ current verified snapshot を更新する。
失敗時の snapshot 維持と selected partition の扱いは後述の Resolution Transaction に従い、working state を昇格させない。grounding closure を満たすまで、candidate を次の advisor input または producer の S1 / S2 return として引き渡さない。
<!-- @/contract -->

<!-- @contract candidate-producer-boundary -->
## candidate の起草と advisor insight

planner は一次情報（要求原文、repository、既存仕様）を調査し、観測可能な AC、設計、scope、依存、制約、
verification、残存 risk を含む working candidate を起草する。上記 caller mapping に従って検証した内容だけを、
同じ内容を識別できる current verified `candidate snapshot` として保持する。

必要な場合だけ plan-candidate-producer planner は normal invocation の read-only `plan-quality-advisor` に candidate snapshot と判定基準を渡す。
advisor の返す insight は非拘束の Data であり、planner は各 insight を一次情報と要求に照らして次の台帳へ裁定する。

- `adopted`: 根拠があり、candidate の具体的な品質向上になるため採用した insight。
- `rejected`: 一次情報に反する、既存の制約で不要、または scope 外のため採用しない insight。
- `unresolved`: 根拠または人間の判断が不足し、採否を決められない insight。安全な推奨ができない場合の返却は既存の `stop-incomplete` 境界に従う。

advisor insight を自動採用せず、採否を根拠なしに planner の推測で埋めない。新仕様、新しい scope、AC、
ユーザー嗜好を advisor から派生させない。
<!-- @/contract -->

<!-- @contract plan-candidate-producer-rmo-parent-mapping -->
## reality-model-observation-kernel v1 の parent mapping

次の Loader Data が列挙値の唯一の正本である。

```text
path = ../../references/reality-model-observation-kernel.md
load_timing = before initial verified candidate S0 verify / promote, and on invalidation-triggered re-grounding
identity = reality-model-observation-kernel-v1
required_sections = [Contract, Observable Reality Model, Method, Reintegration, Target Membership Check, Consumer Responsibilities, Non-goals]
failure = stop-incomplete
owner = plan-candidate-producer parent
delegate_path_resolution = false
```

`candidate-reality-grounding` がこの Loader Data を消費する唯一の loader procedure である。この section は列挙 Data の mapping と consumer 境界だけを提供し、load / identity / required section / failure routing を再定義しない。`producer-invocation-preflight` と `advisor-two-pass-orchestration` はこの Loader を所有しない。

Target は 1 candidate = 1 change-model Target に限定する。current state / current reality assumptions、desired state、current → desired の change relationship、candidate が前提とする dependency / constraint を扱う。Task Specification / request / repository evidence / accepted specification は Target 自体ではなく authoritative context とする。個々の plan step / Claim ごとに Target を細分化しない。

working candidate は Target semantics / evaluation subject として使うが、その Target が正しいことの grounding evidence として自己利用しない。candidate 内の主張だけを理由に Reality distinction / dependency / constraint を成立させない。discrepancy は request、確定仕様、repository contract / invariant、独立した observable evidence から導出する。

Target-relative Problem は current Target との discrepancy として扱い、必要なら別の remediation Claim を導出して producer が採否を裁定する。Problem を `adopted` や Resolution Point へ直結しない。RMO 自身は修正案、採否、candidate mutation を決めない。

Incidental Finding は current candidate satisfaction を変えない限り candidate obligation / adoption ledger へ昇格させない。

Uncertainty は、未解消では安全な verify / recommend ができず、Target semantics に material で、Agent 権限内の追加観測でも解消不能という 3 条件をすべて満たす場合だけ blocking gap / `stop-incomplete` とする。その他は既存 assumptions / residual risks 境界へ写像する。Uncertainty の存在だけで停止しない。Agent が取得可能な evidence で解消できる technical gap を fabricated assumption で埋めない。

raw RMO result は reintegration 後に保持せず、RMO 専用 ledger、status、verdict、per-Claim result を作らない。新しい persistent witness field は作らない。同一 workflow 内で必要な closure / promotion evidence は既存 caller context、verification evidence、process Data の境界で運ぶ。

grounding closure は Derived Problem が 0 件になるまで回す improvement loop ではない。current change-model Target に対する RMO invocation / required reintegration が完了し、必要な remediation Claim の導出・裁定・反映が完了し、candidate verification を阻害する unresolved Uncertainty が残っていない candidate だけを grounding-eligible とする。Incidental Finding は closure を妨げない。Problem 0 件や exhaustive observation は要求しない。

advisor insight は従来どおり Resolution Point → immutable Resolution Batch → Batch Resolve Kernel transaction で裁定・適用・verify・promote する。各 Batch 完了後、producer caller boundary が実際に promoted された candidate と、直前 closure が依存した Target / evidence / context / constraint を比較する。invalidation がなければ既存 closure を維持し、RMO を再実行しない。invalidation があれば、closed Batch は変更せず、その candidate を Target として `candidate-reality-grounding` を実行する。採用 remediation は Batch 外の producer-owned grounding revision path で反映し、既存 verified-snapshot 規則で verify / promote する。stale closure を再利用せず、actual revised candidate と新しい grounded evidence を比較する。structural gate retry などから新しい evidence / context / constraint が入る場合も同じ invalidation 判定を使い、単なる再 invocation は trigger にしない。
<!-- @/contract -->

<!-- @contract plan-candidate-producer-deletion-test-parent-mapping -->
## deletion-test-method v1 の parent mapping

producer が具体的な deletion / trim / merge による要素消去 Claim を選択した後、適用前にだけ load する。add / modify / verify / investigate Claim や final candidate 全体へ DTM を実行しない。exhaustive Claim exploration を別名で復活させない。

次の Loader Data が列挙値の唯一の正本である。

```text
path = ../../references/deletion-test-method.md
load_timing = after a concrete deletion / trim / merge removal Claim is selected and before apply
identity = deletion-test-method-v1
required_sections = [Inputs, Procedure, Semantic Results, Non-goals]
failure = stop-incomplete
owner = plan-candidate-producer parent
delegate_path_resolution = false
```

loader / identity / required section の不足では削除を実行しない。`preserves / breaks / indeterminate` は producer adjudication への入力であり、`adopted / rejected / unresolved` の別名や自動 mapping にしない。loader failure または `indeterminate` では削除を実行せず対象要素を保持し、removal Claim を unresolved とする。削除しない candidate を安全に verify / recommend できる場合だけ継続し、できない場合は `stop-incomplete` とする。
<!-- @/contract -->

<!-- @contract plan-candidate-producer-behavior-observation-kernel-loader -->
## behavior-observation-kernel v1 の parent mapping

次の Loader Data が列挙値の唯一の正本である。

```text
path = ../../references/behavior-observation-kernel.md
load_timing = immediately before plan-quality-advisor normal invocation
identity = behavior-observation-kernel-v1
required_sections = [Contract, Method, Reintegration, Consumer の責務, 非目標]
failure = stop-incomplete
owner = plan-candidate-producer parent
delegate_path_resolution = false
```

`plan-candidate-producer` が advisor invocation Data を組み立てる Agentic Action として load する。`producer-invocation-preflight` と `advisor-two-pass-orchestration` はこの Loader を所有しない。planner 起草中の `判定基準` と freeze-integrity invocation Data の `判定基準` / `必要な周辺 context` には入れない。検証済み本文は normal advisor の既存 `判定基準` / `必要な周辺 context` へだけ注入する。Loader Data と path は advisor Inputs の専用 field にしない。
<!-- @/contract -->

<!-- @anchor plan-candidate-producer-batch-resolution-transaction-start -->
<!-- @contract plan-candidate-producer-batch-resolution-transaction -->
## Resolution Batch と Resolution Transaction

`plan-quality-advisor` の一回の one-shot observation と result collection は Resolution Transaction の外側で完了させる。
その全 insight を、同じ origin verified candidate snapshot に束縛され transaction 開始時までに固定された Resolution
Batch の Resolution Point へ mapping する。transaction 中に Batch membership を追加せず、snapshot 更新後に frontier を
再計算しない。空 Batch も有効だが workflow completion ではない。

planner は mutation 前に Batch 全体を裁定し、conflict / dependency を解消する。全 point を caller-owned disposition として
確定した後、selected set を原則 single partition の coherent revision として apply する。working state は partition ごとに
閉じ、verify と caller-owned semantic progress が成功するまで current verified snapshot に promote しない。失敗した
partition は直前の verified snapshot を維持し、必要なら同じ isolation baseline から `isolate` して安全に処理できる subset を
caller-owned adjudication へ返す。成功済み partition を rollback せず、未検証 state の上へ次 partition を積まない。

複数 partition では apply 前に applicability check を行い、selected obligation、前提、conflict、dependency の維持だけを確認する。
apply / verify / isolate / applicability check から得た新しい execution evidence に限り、元 Batch の point への corrective
adjudication を許す。新しい point や新しい frontier を追加せず、counterpart を再起動しない。authority または evidence が
不足する point は推測で selected set に含めず、独立して処理できる point を止めずに caller-owned boundary へ返す。
<!-- @/contract -->

## plan-quality-advisor の semantic observation boundaries

<!-- @contract plan-candidate-producer-two-advisor-passes -->
advisor invocation は caller-owned であり、orchestration の唯一の witness は上記 `advisor-two-pass-orchestration` Flow である。
advisor の semantic observation は全面再レビューではなく、次の既存 insight 境界だけを扱う。

- fulfillment check: 第1 passで `adopted` とした obligation、revision の所在 / 内容、verify で確認した観測事実だけを
  context として渡し、S1 で実際に充足しているかを確認する。
- revision-induced issue: 第1 passのrevisionとの因果、問題箇所、S0では同じ形で成立していなかったこと、S1で成立した
  理由の全 evidence がある場合だけ扱う。
- rejected contest: 第1 pass時点にはなかった new evidence が rejection reason を直接崩す場合に一度だけ扱う。
- unresolved revisit: S1 または第1 pass後に確定した事実が、元の evidence gap を実際に補った場合だけ扱う。

planner の `fully satisfied` 結論や fulfillment check に不要な adopted 理由を advisor の観測 context に含めず、専用の output schema は新設せず既存の non-binding output boundary を維持する。insight の採否と Resolution Point への mapping、Transaction 内部、verify と semantic progress、残余 risk の扱いは親の意味判断として保持する。
<!-- @/contract -->

<!-- @anchor plan-candidate-producer-bounded-return-start -->
<!-- @contract plan-candidate-producer-bounded-return -->
## bounded な改善と返却

candidate の改善は、要求と一次情報から具体的な品質向上が残る間だけ bounded に行い、snapshot 更新は上記
current verified candidate の caller mapping に従い、Resolution Transaction を完了し、採否台帳と残存 risk を
保った後にだけ return を判定する。判断密度が高まり scope や
責務が変わる場合、または material な `unresolved` により安全な candidate を推奨できない場合は、勝手に進めず
判断点・evidence・必要な問いを付けて `stop-incomplete` を返す。軽い不確実性は既存の candidate status Calculation
へ渡し、`unresolved` という分類だけで無条件に停止しない。

改善を終えた通常の返却は、`candidate_snapshot`、`adoption_ledger`（`adopted` / `rejected` /
`unresolved`）、`assumptions`、`blocking_gaps`、`residual_risks`、`status` を持つ Data である。安全な
candidate を作れない返却では `status: stop-incomplete` と未完了範囲、必要な判断、evidence、未検証事項を返す。
verified result がある場合だけ、`candidate_snapshot` identity、constraint-compliant として promote 済みの completed partition、
その verification evidence を返す。verified snapshot がない場合は `candidate_snapshot: absent`、completed partition は空とし、
fake identity を作らない。未検証または非昇格の working state は再開 baseline から除外する。

```text
verified_present_return = candidate snapshot identity + constraint-compliant completed partitions + verification evidence
absent_return = candidate_snapshot absent + empty completed partitions + no fabricated identity
restart_baseline = verified promoted state only; exclude unverified or non-promoted working state
```

constraint の変更が必要な場合は、必要な Human Decision、衝突した constraint ID、evidence、影響範囲を `authority_conflict`
packet として付ける。Human Decision と独立な partition は verify と promote を続けてもよいが、未解決 point に依存する partition を
その上へ積まない。いずれも後段工程を選択・起動せず、受け入れを主張せず、caller-owned parent へ返して終了する。
<!-- @/contract -->
