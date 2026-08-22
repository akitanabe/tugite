# plan-interactive clarification v1

この reference は `plan-interactive` の clarification phase が所有する clarify-it caller mapping、kernel preflight、
clarify-it result の projection procedure を定義する。親は invocation 開始時にこの reference を読み、判断と Action を
自身の execution data として扱う。Human / caller authority の意味の正本は root `SKILL.md` である。

## clarify-it の caller mapping

<!-- @contract plan-interactive-clarify-caller -->
`plan-interactive` 起動時に、親は次の Loader Data で pinned 内部 snapshot を一度だけ load する。最初の成功本文を同一
invocation 内で固定し、local clarify-it（freeze-integrity recovery、gate reopen、final acceptance local correction）でも
再 load しない。load 失敗時は推測で fallback clarification を行わず、既存の `incomplete` へ返す。clarify-it の semantic identity は検証しない。

```text
clarify_it_reference = ../../../references/upstream/clarify-it/SKILL.md
clarify_it_load_timing = once at plan-interactive start
clarify_it_snapshot = first successful body frozen for the invocation
clarify_it_failure = existing incomplete; no fallback clarification
clarify_it_identity_check = none
```

`references/philosophy.md` の参照要否と相対 path は、loaded artifact 自身の規則に従う。

```text
application = pinned internal upstream clarify-it snapshot in the same plan-interactive parent context
caller_owns = invocation boundary | binding Human authority | verified workflow Data | observation capability | Completed/Stopped workflow projection | direction freeze | downstream workflow
public_extension = none
```
<!-- @/contract -->

## kernel preflight と caller mapping

`interactive-kernel-preflight` Flow が resolve-kernel の load timing、identity、必要本文、failure routing の唯一の詳細 witness である。
親は skill-relative loader Data、caller=`plan-interactive`、resolver=`planner`、counterpart=`human`、authority=`binding`、
ledger=`decision ledger` を入力として準備し、検証済み本文だけを既存の判定基準へ注入する。

<!-- @contract plan-interactive-kernel-mapping -->
stable Loader Data は次の値を持つ。

```text
resolve_path = ../../../references/resolve-kernel.md
resolve_identity = resolve-kernel-v1
resolve_dependencies = none
resolve_required_sections = [Caller boundary と role, Current verified snapshot、working state、frontier, Atomic resolution unit, Exit と停止, Kernel non-dependency]
caller = plan-interactive
resolver = planner
counterpart = human
authority = binding
ledger = decision ledger
```
<!-- @/contract -->

`interactive-kernel-preflight` Flow はこの Data を使い、path 解決と最終判断は親が所有する。

## clarify-it result の projection

<!-- @contract plan-interactive-clarify-completion -->
clarify phase の終了判断は次の2つだけとする。回数上限、remaining decisions count、semantic progress 管理、Tugite 独自 completion 判定は
`plan-interactive` 側で持たない。`clarify-it: Completed` は Human Decision Context の completion であり、Plan Artifact completion ではない。

- `Completed` → 親が current decision model から freeze に必要な意味単位を抽出する（clarify-it 出力に固定 schema を要求しない）→ `freeze_source_snapshot` → `direction-freeze-projection`
- `Stopped` → 停止理由と未解決 Human decisions / inconsistency を保持した既存 `incomplete`。独自 clarification 継続も、独自 recovery / continuation status も作らない
<!-- @/contract -->

## Programmatic Flows

<!-- @contract plan-interactive-interactive-kernel-preflight -->
### interactive-kernel-preflight

Trigger: 親が最初の clarify-it を開始する直前で、kernel preflight を要求したとき。
Inputs: resolve-kernel の skill-relative path、identity、必要 section、dependencies、plan-interactive の caller/role mapping、親の判定基準。
Procedure: resolve は clarify-it 適用前に一度だけ load・identity・必要本文を検証する。resolve の failure は clarify-it 前に `incomplete` とし、検証済み本文だけを親の既存判定基準へ注入する。path 解決と最終判断は親が所有する。
Outcomes: 検証済み kernel Data と role mapping、または `incomplete`。Flow は Human の意味判断、clarify-it の対話結果を expected oracle にせず、loader failure を突破しない。
<!-- @/contract -->
