---
name: proposal
description: >-
  plan-craft の同じ親 context 内だけで、要求と repository の観測から計画 candidate を起草し、
  read-only advisor の非拘束な insight を裁定して candidate snapshot または stop-incomplete を caller-owned parent へ返す internal skill。
user-invocable: false
---
<!-- Generated from shared/. Do not edit directly. -->

# proposal

## 位置づけと発火

この Skill は `plan-craft` の同じ親 context 内だけで使う internal skill であり、ユーザーから直接起動しない。
要求、repository、既存仕様を観測して計画 candidate を作る producer を担う。
自身は実装、委譲、worktree 操作、保存、最終受入を行わず、caller-owned parent へ判断材料を返す。

## 入力と観測

親から次の Data を受け取る。

- `request`: 要求原文、目的、成功条件、scope、exclude、制約、既知の依存。
- `repository_observation`: current state、既存仕様、関連成果物、検証可能な境界。
- `caller_context`: `plan-craft` が同じ context で保持する判断と、必要なら既存の current verified candidate snapshot。

要求、対象、成功条件、scope、exclude、依存、制約の不足または矛盾が品質を変える場合は推測せず、
`stop-incomplete` として必要な判断を返す。軽微な不足は根拠付き `assumptions` として分離する。

## batch-resolve-kernel v1 の parent mapping

次の Loader Data が列挙値の唯一の正本である。

```text
path = ../../references/batch-resolve-kernel.md
load_timing = once at proposal invocation start
identity = batch-resolve-kernel-v1
dependencies = none
required_sections = [適用モデル, Snapshot discipline, Resolution Transaction, Caller boundary]
failure = stop-incomplete
owner = proposal parent
delegate_path_resolution = false
```

親は上記 Loader Data の field を使って load と必要本文の検証を行い、failure field に従って失敗処理する。
Resolution Transaction ごとには再読込せず、owner / delegate_path_resolution の境界を維持する。
検証済み本文だけを、以降の Resolution Transaction の既存の `判定基準` または `必要な周辺 context` に注入する。

## batch-resolve-kernel v1 の role mapping

次の role Data が列挙値の唯一の正本である。

```text
caller = plan-craft
resolver = proposal planner
counterpart = plan-quality-advisor
target_snapshot = origin verified candidate snapshot
insight = Resolution Point
same_snapshot_insights = Resolution Batch
authority = discretionary
ledger = adoption ledger
```

親は上記 role field を使って既存責務へ mapping する。counterpart observation Action は Resolution Transaction 外の
one-shotとし、resolver が要求、一次情報、current verified snapshot を基準に裁定する。

この batch-resolve-kernel mapping と後述の necessity-kernel mapping は別 section の独立した規範である。互いの本文を
前提にせず、相互の読み込み順に依存させない。

## current verified candidate の caller mapping

`caller_context` で既存 candidate を受け取る場合は current verified candidate snapshot とし、未検証の working state を
baseline にしない。初回は要求、一次情報、観測可能な条件から working candidate を起草し、それらに対する verify の成功と semantic progress の確認後にだけ、初期 current verified snapshot として確立する。
各改善は working state へ apply し、verify と semantic progress が成功した後にだけ current verified snapshot を更新する。
失敗時の snapshot 維持と selected partition の扱いは後述の Resolution Transaction に従い、working state を昇格させない。

## candidate の起草と advisor insight

planner は一次情報（要求原文、repository、既存仕様）を調査し、観測可能な AC、設計、scope、依存、制約、
verification、残存 risk を含む working candidate を起草する。上記 caller mapping に従って検証した内容だけを、
同じ内容を識別できる current verified `candidate snapshot` として保持する。

## necessity-kernel v1 の parent mapping

次の Loader Data が列挙値の唯一の正本である。

```text
path = ../../references/necessity-kernel.md
load_timing = before candidate Claim adjudication
identity = necessity-kernel-v1
required_sections = [適用範囲, Task Specification, Claim と evidence, Deletion Test]
failure = stop-incomplete
owner = proposal parent
delegate_path_resolution = false
```

candidate Claim を判定する前に、advisor 起動の有無にかかわらず、親は上記 Loader Data の field を使って load と必要本文の検証を行い、failure field に従って失敗処理する。検証済み本文を既存の
`判定基準` または `必要な周辺 context` の一部にする。`plan-quality-advisor` 起動時は既取得 Data を既存の判定基準として渡し、owner / delegate_path_resolution の境界を維持する。

候補 Claim の必要性は既存の判定基準に含めた Task Specification と Deletion Test で観察する。
Claim は finding / insight 本文ではなく、candidate に追加・維持・変更・除去・検証・調査する obligation の候補
であり、必要性の根拠を既存の observation / evidence から追跡する。`necessary` / `unnecessary` /
`indeterminate` を新しい返却 field にせず、親は下記の adoption ledger の語彙へ写像する。候補を更新した後は
更新された snapshot で再判定し、互いを witness とする同時削除を認めない。必要性分類は既存語彙へ写像し、新verdict fieldではない。round budget / termination へ直結させない。`structural-health-gate` の意味は
この mapping の対象外である。

必要な場合だけ `plan-craft` 内の proposal planner は read-only `plan-quality-advisor` に candidate snapshot と判定基準を渡す。
advisor の返す insight は非拘束の Data であり、planner は各 insight を一次情報と要求に照らして次の台帳へ裁定する。

- `adopted`: 根拠があり、candidate の具体的な品質向上になるため採用した insight。
- `rejected`: 一次情報に反する、既存の制約で不要、または scope 外のため採用しない insight。
- `unresolved`: 根拠または人間の判断が不足し、採否を決められない insight。

advisor insight を自動採用せず、採否を根拠なしに planner の推測で埋めない。新仕様、新しい scope、AC、
ユーザー嗜好を advisor から派生させない。

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

## plan-quality-advisor の固定2 pass

advisor invocation は caller-owned であり、proposal は次の exactly 2 pass を実行する。

```text
candidate S0
→ fresh-context advisor #1
→ Resolution Batch #1
→ Resolution Transaction #1
→ verify + semantic progress
→ verified candidate S1
→ fresh-context advisor #2
→ Resolution Batch #2
→ Resolution Transaction #2
→ verify + semantic progress
→ verified candidate S2
→ return
```

第1 pass の Batch または selected set が空でも第2 passを必ず起動する。第2 pass後に第3 passを起動しない。第2 pass は全面
再レビューではなく、次の既存 insight 境界だけを観測する。

- fulfillment check: 第1 passで `adopted` とした obligation、revision の所在 / 内容、verify で確認した観測事実だけを
  context として渡し、S1 で実際に充足しているかを確認する。
- revision-induced issue: 第1 passのrevisionとの因果、問題箇所、S0では同じ形で成立していなかったこと、S1で成立した
  理由の全 evidence がある場合だけ扱う。
- rejected contest: 第1 pass時点にはなかった new evidence が rejection reason を直接崩す場合に一度だけ扱う。
- unresolved revisit: S1 または第1 pass後に確定した事実が、元の evidence gap を実際に補った場合だけ扱う。

第2 pass 専用の output schema は新設せず、既存の non-binding output boundary を維持する。
第2 pass へ planner の `fully satisfied` 結論や fulfillment check に不要な adopted 理由を渡さず、advisor 自身に S1 と
obligation を照合させる。第2 pass の insight も既存の non-binding output から通常どおり Resolution Point へ mapping し、
該当しなければ空 Batch として第2 Transaction を閉じる。第2 Transaction の修正は verify と semantic progress まで閉じ、
残余 risk は後段 review-loop に返す。

## bounded な改善と返却

candidate の改善は、要求と一次情報から具体的な品質向上が残る間だけ bounded に行い、snapshot 更新は上記
current verified candidate の caller mapping に従う。固定2 passの Resolution Transaction を完了し、採否台帳と残存 risk を
保った後にだけ return を判定する。判断密度が高まり scope や
責務が変わる場合、または material な `unresolved` により安全な candidate を推奨できない場合は、勝手に進めず
判断点・evidence・必要な問いを付けて `stop-incomplete` を返す。軽い不確実性は既存の candidate status Calculation
へ渡し、`unresolved` という分類だけで無条件に停止しない。

改善を終えた通常の返却は、`candidate_snapshot`、`adoption_ledger`（`adopted` / `rejected` /
`unresolved`）、`assumptions`、`blocking_gaps`、`residual_risks`、`status` を持つ Data である。安全な
candidate を作れない返却では `status: stop-incomplete` と未完了範囲、必要な判断、evidence、未検証事項を返す。
いずれも後段工程を選択・起動せず、受け入れを主張せず、caller-owned parent へ返して終了する。
