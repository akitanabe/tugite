<!-- Generated from shared/. Do not edit directly. -->

# impl-lead delegation v1

この reference は、`impl-lead` の worker tier 選択、writable scope Kernel loader と handoff、fresh context への委譲、
delegated worker の silence / interrupt policy を定義する。親は `SKILL.md` で指定された時点に全文を読み、判断と
Action を自身の execution data として扱う。

## Worker tier selection

委譲時は4候補から、仕様が明確で既存 pattern を適用できる通常の `implementer` を原則とする。scope が特に狭く
検証が明確なら `focused-implementer`、残存判断や手戻りが大きいなら `senior-implementer`、親相当の推論を必要とする
具体的な理由があり品質を左右する場合だけ `expert-implementer` を選ぶ。単なる変更量や file 数で上位へ昇格せず、迷えば
`implementer` とする。選択した worker、理由、`base_snapshot`、execution constraint を execution data に記録する。
ユーザーが指定した worker が品質下限を満たせない場合も無断で変更・続行せず、制約緩和を確認するか、未完了範囲と判断点を
付けて `stop-incomplete` とする。固定閾値や決定表、暗黙の追加実行環境は持ち込まない。

normalization 後の worker selection は dispatch まで provisional とする。上位 worker の選択理由が実装難易度ではなく、残存判断密度、複数 semantic family の保持、worker による AC / 責任境界 / dependency の再設計である場合、親は同じ candidate identity と観測理由を mandatory implementation-unit-design boundary へ一度だけ戻す。境界が明瞭なら final selection へ進み、閉じなければ `blocking_gaps` または `stop-incomplete` とする。上位 worker が実装難易度のため必要なら維持でき、上位 worker 禁止、自動 split、tier threshold、再帰 loop を導入しない。

## Writable scope Kernel loader and worker handoff


最初の write-capable Worker handoff より前に、親は writable scope Kernel を load して identity と必要 section を検証する。
次の Loader Data がこの load の唯一の正本である。

```text
path = ../../../references/writable-scope-kernel.md
load_timing = before first write-capable Worker handoff
identity = writable-scope-kernel-v1
dependencies = none
required_sections = [Scope assignment model, Parent loader and assignment, Worker write boundary, Scope changes and non-goals]
failure = stop-incomplete
owner = impl-lead parent
assignment_source = parent execution data
assigned_writable_scopes = explicit filesystem region set
repository_root_outside = allowed for explicitly assigned run-owned worktree
worker_path_resolution = parent
scope_change = explicit handoff update
```

assignment は親の execution data であり、
Implementation Unit Data の field ではない。repository root 外の run-owned worktree も、親が明示した assignment に含められる。
親は Worker に path 解決や assignment の確定を委ねず、Kernel と assignment を使う handoff procedure を
`writable-scope-handoff` へ渡す。
<!-- @/anchor -->

### writable-scope-handoff

Trigger: 親が write-capable Worker route と isolation を確定し、handoff の直前に到達したとき。
Inputs: 検証済み `writable-scope-kernel-v1` identity と必要本文、親が path 解決した明示 `assigned_writable_scopes`、Implementation Unit Data、execution constraint。
Procedure: writable scope Kernel だけを scope assignment procedure の唯一の正本として、Kernel 本文と assignment を handoff へ注入する。loader、identity、必要 section、assignment の不足・不正・不明では handoff を作らない。
Outcomes: write boundary を備えた handoff、または no-write の `blocked`。scope 変更や追加領域は Agentic な親の明示 handoff update へ返す。

## Fresh context and continuation

委譲する新しい ID の Implementation Unit は、Implementation Unit Data、依存、`base_snapshot`、選択 worker と route、execution constraint、
isolation、外部副作用の状態、禁止範囲、verification を含む自己完結 handoff で fresh context へ渡す。direct の単位は
親 context で実行し、新しい worker を起動しない。

委譲する新しい単位は新しい subagent の起動で履歴を継承しない新しい subagent context に起動する。追加作業を同じ
context に返す場合に限り、同じ ID の実装上の限定修正だけを同じ subagent context の継続で同じ context に返す。

無応答時の状態確認は親所有の silence status inquiry であり、既存の同じ subagent context の継続を使う。これは実装上の
限定修正でも追加作業でもなく、`implementation-unit-continuation-routing` の対象外である。新しい作業指示、scope 変更、AC 変更を
含めない。

親は追加作業を同じ意味の限定修正か、意味変更または accepted 単位の変更かに分類し、route を
`implementation-unit-continuation-routing` へ渡す。部分成果は、独立した新 ID、AC、QA、baseline への統合がすべて完了した場合だけ accept する。

### Delegated worker silence defaults

介入基準の意味の正本は `impl-lead` 親とする。対象は委譲で起動した worker（fresh と same-ID continuation の両方）で
ある。parent direct と reviewer は対象外である。worker は監視 interval を決めて親へ進捗を要求しない。並列なら
worker ごとに最後の意味ある観測を独立に数える。

progress check は親所有の silence status inquiry である。走行中の delegated worker context に状態確認だけを送る。

- 既定では、最後の意味ある観測から 15 分未満では progress check しない。15 分到達後はしてよい（必須ではない）。
  15 分は異常判定ではなく許可の既定目安である。
- Human が明示した別の時間基準または介入基準がある場合、その指定が既定に優先する。新しい public parameter schema は
  作らない。
- 経過時間だけを根拠に interrupt しない。interrupt は progress check またはその他の観測 evidence から stall、同一失敗の
  反復、scope 逸脱、blocker、contract 違反等が確認された場合に限定する。
- inquiry 送信そのものは、worker 側の意味ある応答が観測されるまで clock を reset しない。
- interrupt 後の再開では、再開した worker に既定の自律実行時間を与える。新しい 15 分 window を数え、過去の interrupt
  そのものを理由に監視頻度を上げない。ここでの continuation は限定修正の追加作業 continuation ではない。
- interrupt 後に追加作業が必要になった場合だけ、既存の限定修正分類と `implementation-unit-continuation-routing` に戻る。

「意味のある進捗・出力・状態変化」は親が観測事実から分類する。file 変更、tool 出力、完了報告、明確な状態遷移を含み、
経過時間そのものや空の keepalive は含めない。決定表は作らない。時計は親が利用可能な観測時刻で足りる。interrupt の
How は各 runtime の停止能力に依存し、この節は When / When-not だけを正本化する。

```text
policy_id = "impl-lead-delegated-worker-silence-defaults-v1"
applies_to = "delegated worker only; not parent-direct; not reviewer"
default_progress_check_allowance = "15 minutes after last observed meaningful progress, output, or state change"
progress_check_meaning = "allowance, not abnormality, not obligation"
human_override = "explicit Human criteria take precedence"
interrupt_time_only = "prohibited"
interrupt_requires = "evidence of stall, repeated same failure, scope deviation, blocker, or contract violation from progress check or other observation"
post_continuation = "give resumed worker a full default autonomous window; do not raise monitoring frequency because of past interrupt"
progress_check = "parent-owned silence status inquiry on running delegated worker context"
progress_check_vehicle = "existing platform continuation vehicle as status inquiry only; not limited-fix continuation; not additional work; not implementation-unit-continuation-routing"
```

Gunte が保証するのは policy identity、required fields、その coherent relation までである。runtime の 15 分遵守と
interrupt 判断の正しさは保証しない。
