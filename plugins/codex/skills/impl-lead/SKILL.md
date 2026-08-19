---
name: impl-lead
description: >-
  明示起動時だけ、親が一つ以上の Implementation Unit を正規化し、direct または各単位の worker を選び、
  必要な場合だけ risk-directed review を選び、必須の final writing gate、TDD と親 QA を経て accept または stop-incomplete で安全に閉じる実装 loop。
---
<!-- Generated from shared/. Do not edit directly. -->

# Active main

この skill はユーザーが明示的に起動した場合だけ開始する。自然言語の作業内容、規模、現在の
context から暗黙に起動しない。起動後も、親が受け入れ判断と最終報告を保持する。単一 Implementation Unit の direct または
一名 worker という既存経路は保ちつつ、同じ run で複数単位を安全に処理できる。
`risk-directed review` は固定 phase や全作業の必須手順ではなく、親が具体的な risk と判断への影響を説明できる場合だけ実行する。
これは run を閉じる直前の必須 `final writing gate` とは別責務である。

## Intake and Implementation Unit normalization

親は実装を始める前の初期 Intake で、要求全体、対象 repository、現在の dirty state、基準状態を観測する。Issue、doc、
plan section、ユーザーの箇条書き、freeze 済み設計などの source boundary を Implementation Unit boundary とみなさず、対象 file と
その周辺、呼び出し元・先、関連 test を読んでから、意味上区別できる到達結果を recall 寄りに成果候補として一度観測する。
1 source から複数、複数 source から一つ、1 source から一つの成果と Implementation Unit をいずれも許容し、対応数を固定しない。

成果候補は semantic end-state についての transient observation である。統合できそうという理由で早期に候補を落とさない一方、
file 編集、generator、version 更新、verification command などの実装手段・工程は、それ自体が要求成果でない限り候補にしない。
新しい Data model、schema、必須 ID、Implementation Unit Data field、固定 input field、provenance field、永続 artifact を導入しない。

親は coverage を二段階で確認する。成果候補の抽出時には要求全体から意味上の到達結果を取りこぼしていないか確認し、
Implementation Unit 確定時には全要求が最終集合へ反映されているか確認する。成果要求は原則としてちょうど一つの Implementation Unit を primary
owner とし、横断 constraint / invariant は複数単位へ適用でき、non-goal / 今回除外は owner を持たず理由または境界判断を明示する。
未割当要求を残したまま dispatch しない。

親は成果候補と coverage から run の目的を一つ以上の Implementation Unit に正規化する。複数であることだけを停止理由にしない。
Implementation Unit Data の意味と field の唯一の正本はこの section である。各単位は次の Data を持つ。

- `id`: run 内で一意な識別子。
- `purpose`: 単一の目的。
- `acceptance_criteria`: 外部から観測可能で検証可能な Acceptance Criteria。これは候補条件であり、accept の確定ではない。
- `scope`: `change`（変更を許す範囲）と `exclude`（変更しない範囲）。
- `implementation_freedom`: worker に任せてよい局所判断。なければ空。
- `constraints`: ユーザー指定、互換性、依存、実行環境その他の制約。
- `depends_on`: Implementation Unit ID 間の semantic dependency と、外部・repository・environment の precondition を分けた記述。同じ file、writer、generated output、generator、contract registry、Gunte gate、verification surface の共有だけでは semantic dependency または Implementation Unit 統合の根拠にならず、execution conflict として扱う。
- `verification`: AC ごとの native test、focused test、必要な最終 gate。

Implementation Unit Data は上記 canonical field だけを表す。

Implementation Unit は、単一 purpose、観測可能な完結成果、単独で Green になる検証、無関係な変更なしに accept / revert できる
変更集合（後続依存の cascade rollback は許す）、独立した副作用と rollback 境界を持つ。

単一 Implementation Unit として正規化する場合も、内部に独立して Green / accept できる複数成果、独立 AC / verification / rollback
boundary、foundation / application の別成果が残っていないか親が自己再検査する。分割しない理由の専用 field、固定 ledger、
常時の外部説明は要求しない。

不足、矛盾、または scope を閉じられない状態が品質に影響する場合、推測で補わず必要な情報を親へ戻すか、理由・
未完了範囲・evidence・残存 risk を含む `stop-incomplete` とする。要求と repository の状態を観測せずに worker を
起動しない。既存の dirty/untracked は scope に含めず、勝手に変更・削除しない。

worker、base、route、order、isolation、result は実行時の execution data として親が記録し、Implementation Unit の
意味を書き換えない。review goal、reviewer handoff、finding、QA result、persistence resource も Implementation Unit の意味ではなく
execution data として扱う。

### Optional implementation-unit design step

初期 Intake で明らかな境界は親が Implementation Unit 化する。分割、統合、semantic dependency が非自明な場合だけ、相互に境界判断が
影響する関連成果候補群をまとめ、同じ context の内部工程として `implementation-unit-design` の手順を参照できる。成果候補ごとに個別起動せず、
raw request から成果候補を再抽出させない。返された `implementation_units`、分割／統合 signal、`blocking_gaps` は候補であり、親は境界分析を
同じ深さで繰り返さず、成果候補が暗黙に消えていないこと、要求 coverage、要求されていない新成果がないこと、unresolved
`blocking_gaps` がないこと、Implementation Unit Data と execution data の境界だけを run-wide responsibility として再確認する。

初期のこの step では、親は候補群と grounding に加えて、invocation 固有の確認順序と attention priority を
`partition_perspectives` として渡せる。これは答えを先付けするものではなく、次の観点を必要な順序で照らすための
transient execution Data である。
親は `partition_perspectives` として semantic outcome / purpose、independent AC / focused verification、accept / rollback boundary、semantic dependency、execution conflict / order / isolation、run-wide final gate を渡せる。

- `semantic outcome / purpose`: 各候補が生む外部から観測可能な outcome と単一 purpose。
- `independent AC / focused verification`: 候補ごとに独立して Green と検証ができる AC と focused verification。
- `accept / rollback boundary`: 候補単位で accept または rollback できる境界。
- `semantic dependency`: 候補間で意味上必要な dependency と、その理由。
- `execution conflict / order / isolation`: shared file、writer、generated output、generator、contract registry、Gunte gate、
  verification surface の共有を semantic dependency や merge の根拠にせず、execution conflict として order / isolation とともに扱う。
- `run-wide final gate`: full / run-wide gate は focused verification の代替ではなく、候補確定後の最終 gate として扱う。

この mapping は候補数、split point、merge 対象を指定せず、固定 mode、threshold、expected-output oracle、ledger も導入しない。
`implementation-unit-design` の返却後は、候補の採否、全要求の coverage、未要求成果、`blocking_gaps`、Implementation Unit Data と execution Data の
境界を親が再確認し、実装・委譲・accept の判断を引き取る。

runtime が Skill 間起動を提供しない場合は、親が `implementation-unit-design` 本文を同じ Intake／再正規化工程として直接参照する。
親が候補を採用・差し戻し・stop-incomplete とする判断と、実装・委譲の実行責務は変わらない。

実行中の再正規化では新しい成果候補抽出 phase を追加しない。既存の統合、追加分割、部分成果の独立再構成、semantic dependency
edge の再接続を維持し、必要なら `implementation-unit-design` を使えるが、初期 Intake の成果候補 discipline を execution-time 全体へ広げない。

## Programmatic Flows

以下は、親が意味判断を完了して確定 Data を渡した後の局所的な deterministic procedure だけを持つ。
Flow の procedure、条件、outcome は固定であり、Agent は override、bypass、置換しない。Flow が blocked を返した場合は突破せず、outcome の後に複数の妥当な Action が残る意味判断は Agentic な親責務へ返す。

### dependency-dispatch-guard

Trigger: 親が Implementation Unit、依存、precondition の意味を確定し、dispatch 可否の固定判定を要求したとき。
Inputs: run 内 ID の存在と cycle の解消結果、依存先の acceptance、外部・repository・environment precondition の観測値と成立条件・安定性・pin、現在の `base_snapshot`、dispatch 直前に更新した current `protected_dirty_record` と現在の repository / run baseline の比較 Data。
Procedure: dependency、precondition、protected drift の既存 guard 群に新しい意味順序を付けず全件を評価し、全 guard 成立時だけ `dispatch-ready` とする。いずれかの failure、観測不能、または drift は `blocked` とし、Action を実行しない。
Outcomes: `dispatch-ready`、または `blocked` と failure Data。`blocked` は突破せず、再正規化、確認、`stop-incomplete` の選択を Agentic な親へ返す。

### run-owned-checkout-creation

Trigger: 親が default run-owned checkout を確定し、その Creation Action の直前に到達したとき。
Inputs: 親が確定した `base_snapshot` と isolation、検証済み `impl-run-owned-lifecycle-loader` Data、identity と必要 section を検証した reference 本文。
Procedure: `references/run-owned-lifecycle.md` の `Creation` だけを procedure の唯一の正本として実行・照合する。作成不能時に current checkout へ fallback しない。
Outcomes: 作成・照合済み run-owned checkout Data、または `blocked`。`blocked` は突破せず、次の妥当な Action の選択は Agentic な親へ返す。

### explicit-route-constraint

Trigger: 親がユーザー指定の route execution constraint の有無と内容を確定したとき。
Inputs: direct / 委譲、指定 worker、isolation、order、parallel の禁止または要求、および constraint conflict の確定 Data。
Procedure: 明示 constraint が一貫していればそのまま route Data に写像し、conflict は `blocked` とする。明示 constraint がなければ route または worker を選択しない。
Outcomes: 明示指定どおりの route Data、`blocked`、または `agentic-selection-required`。後二者を突破せず、制約確認または自律的 route / worker 選択を Agentic な親へ返す。

### writable-scope-handoff

Trigger: 親が write-capable Worker route と isolation を確定し、handoff の直前に到達したとき。
Inputs: 検証済み `writable-scope-kernel-v1` identity と必要本文、親が path 解決した明示 `assigned_writable_scopes`、Implementation Unit Data、execution constraint。
Procedure: writable scope Kernel だけを scope assignment procedure の唯一の正本として、Kernel 本文と assignment を handoff へ注入する。loader、identity、必要 section、assignment の不足・不正・不明では handoff を作らない。
Outcomes: write boundary を備えた handoff、または no-write の `blocked`。scope 変更や追加領域は Agentic な親の明示 handoff update へ返す。

### implementation-unit-continuation-routing

Trigger: 親が返却結果に追加作業が必要と確定し、変更の意味分類を完了したとき。
Inputs: 同じ ID の AC・scope・責任境界・依存が不変な限定修正、または意味変更・accepted 単位の変更という親の分類、旧 ID / context、依存 edge。
Procedure: 限定修正だけを同じ ID / context へ continuation し、意味変更または accepted 単位の変更は新しい ID / fresh context へ送る。依存 edge を一意に再接続できなければ `blocked` とし、二重計上しない。
Outcomes: `same-context-continuation`、`new-id-fresh-context`、または `blocked`。分類や再接続の意味判断が未確定なら Agentic な親へ返す。

### parallel-candidate-integration

Trigger: 親が parallel eligibility と適用順不変を確定した batch の候補が返却されたとき。
Inputs: 親が固定した候補順、最後の Green な run baseline、各候補の diff・AC・scope・precondition・dirty state・side effect・native verification Data。
Procedure: 最後の Green な baseline へ候補を一件ずつ統合・検証し、Green の候補だけを accept する。failure は accept せず最後の Green へ rollback・再検証し、戻せなければ `blocked` とする。最後の候補の統合 verification を `final combined verification` とし、別の combined gate を重ねない。
Outcomes: accepted 候補を含む latest Green baseline と final combined verification Data、または rollback 済み / rollback 不能の `blocked`。hidden dependency の扱いは Agentic な親へ返す。

### final-writing-gate-invocation

Trigger: 全 Implementation Unit が accept 候補で、親 QA が Green、risk-directed finding の処理が完了したと親が確定し、run accept 直前に到達したとき。
Inputs: 検証済み `impl-final-writing-loader` Data、identity と必要 section を検証した reference 本文、親が固定した target snapshot と self-contained handoff Data。
Procedure: `references/final-writing-gate.md` の `Final writing acceptance gate` だけを invocation procedure の唯一の正本として、有効な read-only gate を一回実施する。省略、既実施 review での代替、writer との重複をしない。
Outcomes: snapshot に結び付いた有効な reviewer result Data、または `blocked`。loader / invocation failure は突破せず `stop-incomplete` へ送る。

### final-writing-result-routing

Trigger: final writing gate の reviewer result が親へ返却されたとき。
Inputs: target snapshot と照合済み result、finding Data の有無、検証済み `impl-final-writing-loader` Data と reference 本文。
Procedure: `references/final-writing-gate.md` の `Final writing findings and remediation` だけを result routing procedure の唯一の正本として、result を no-finding、parent-adjudication-required、invalid / incomplete に振り分ける。finding の意味的な採否を Flow 内で決めない。
Outcomes: `gate-complete`、`parent-adjudication-required`、または `blocked`。後続 remediation の eligibility、risk、採否は Agentic な親へ返し、invalid / incomplete は `stop-incomplete` へ送る。

### external-side-effect-retry

Trigger: 外部 Action の partial failure または context loss 後に、親が retry 可否の固定判定を要求したとき。
Inputs: fresh context で再観測した resource / result identity、`未実行` / `実行済み` / `結果不明`、idempotency、照合方法、authorization、compensation / rollback、親が確定した safe-retry eligibility。
Procedure: `結果不明` または安全な照合不能なら retry せず `blocked` とする。`未実行` かつ safe-retry eligibility 成立時だけ一回再実行して結果を照合し、`実行済み` は再実行しない。
Outcomes: 照合済み `実行済み` Data、または `blocked`。unknown result を blind retry せず、補償、確認、`stop-incomplete` の意味判断は Agentic な親へ返す。

### run-owned-closeout

Trigger: run-owned checkout を作成した run で、親が final verification と必要な外部副作用照合を完了し closeout 可否判定へ到達したとき。
Inputs: 検証済み `impl-run-owned-lifecycle-loader` Data と reference 本文、親が観測した成果の永続化、resource identity、tracked state、collision、writer / reviewer 終了 Data。
Procedure: `references/run-owned-lifecycle.md` の `Closeout` だけを procedure の唯一の正本とし、integration result 後の cleanup eligibility を Calculation として判定し、実際の cleanup と post-observation / 照合は Action として実行し、その観測結果を Data として返す。unsafe または unknown なら resource を保持する。
Outcomes: 照合済み integration / cleanup Data、または resource を保持した `blocked`。`blocked` は突破せず `stop-incomplete` と残存 Action の判断を Agentic な親へ返す。

## Dependencies, snapshots, and isolation

親は Implementation Unit の依存と precondition の意味、観測方法、成立条件、安定性、pin 方法を確定し、dispatch 直前の固定判定を
`dependency-dispatch-guard` へ渡す。
外部・repository・environment の precondition には、観測方法、成立条件、安定性、pin 方法を記録する。mutable な
状態を再観測する時点は dispatch 開始直前、外部 Action 直前、accept 直前とする。pin できる precondition は親が dispatch 前に
`base_snapshot` へ固定し、handoff はその識別を参照する。drift 時は
新しい `base_snapshot` を確定し、task-owned isolation に安全に再適用できる場合だけ進む。ユーザー所有 branch や dirty
checkout の ref・履歴を書き換えず、対象・所有権・旧 snapshot への復旧可能性を確認できなければ、確認・再正規化・
`stop-incomplete` のいずれかを親が選ぶ。

各 Implementation Unit の dispatch 直前に、親は repository、protected dirty/untracked、依存、現在の run baseline を再観測し、
`protected_dirty_record` を更新する。これは Implementation Unit の dispatch、candidate integration、QA / review snapshot protection に限定する。
Implementation Unit の統合と QA では現在状態をこの record と比較し、drift があれば Action と accept を止めて再正規化・確認・`stop-incomplete` を選ぶ。
更新した current `protected_dirty_record` と現在の repository / run baseline の比較 Data は `dependency-dispatch-guard` へ渡す。
`protected_dirty_record` は run-owned closeout の noise drift 判定へ流用しない。

`base_snapshot` は編集前内容を後から比較・再現できる不変の識別を持つ（commit に限定しない）。保護対象の dirty
state は `protected_dirty_record` として別管理し、uncommitted の変更を暗黙に commit、移送、破棄しない。snapshot
を再現できなければ別 snapshot、直列化、確認、`stop-incomplete` のいずれかにする。review target は対象内容を不変に識別できる
snapshot とし、review 中はその checkout へ writer を入れない。複数 reviewer は同じ snapshot を参照し、read-only と isolation が
保証できる場合だけ同時に起動できる。実装、親 QA、integration、その他の書き込み Action とは重ねない。reviewer 起動前後に
target と protected dirty/untracked state を再観測し、意味のある drift があればその snapshot の finding を受け入れ根拠に使わず、
新しい snapshot で再 review、確認または `stop-incomplete` を選ぶ。

isolation は execution data であり、全環境に固定 path や branch を要求しない。user constraint、dirty overlap、base、同時
writer、external resource、integration/rollback の必要性から選び、`base`、`owner`、`single_writer`、`paths`（1件でも list）、
`integration`、`cleanup` を確定する。親 direct、worker、継続修正、generator、formatter、write test などを含め、
同一 checkout への同時 writer は禁止する。既存変更を commit、move、discard して isolation を作らない。

### Default run-owned checkout

ユーザーが既存 checkout、別 isolation/worktree、または worktree を使わない制約を指定していない場合は、最初の書き込み
Action より前に、親は run 全体の既定 checkout として run-owned worktree を選ぶ。ユーザー指定はこの既定より優先する。
作成 Action と結果照合は `run-owned-checkout-creation` へ渡す。

次の Loader Data が列挙値の唯一の正本である。

```text
path = references/run-owned-lifecycle.md
load_timing = before run-owned Creation Action
identity = impl-lead run-owned lifecycle v1
required_sections = [Creation, Closeout]
required_scope = [creation, integration, cleanup]
failure = stop-incomplete
owner = impl-lead parent
```

この経路を選ぶ場合、親は上記 Loader Data の field を使って load と必要本文の検証を行い、failure field に従って失敗処理する。
owner が run-owned resource の ownership、判断、Action、結果照合を保持する。

## Route and execution order

親はユーザーの direct または委譲の制約を execution constraint として確定し、明示 constraint の適用を
`explicit-route-constraint` へ渡す。経路の指定がない場合、各単位について、親 direct の方が安く安全なら direct、それ以外で
安全に委譲できるなら一名の worker を選ぶ。worker の能力は実装自由度、残存判断、推論難度、手戻り、検証可能性、
実行コストを相対比較して選び、単なる変更量や file 数だけで上位の worker を選ばない。選択理由を execution data に
記録する。

委譲時は4候補から、仕様が明確で既存 pattern を適用できる通常の `implementer` を原則とする。scope が特に狭く
検証が明確なら `focused-implementer`、残存判断や手戻りが大きいなら `senior-implementer`、親相当の推論を必要とする
具体的な理由があり品質を左右する場合だけ `expert-implementer` を選ぶ。単なる変更量や file 数で上位へ昇格せず、迷えば
`implementer` とする。選択した worker、理由、`base_snapshot`、execution constraint を execution data に記録する。
ユーザーが指定した worker が品質下限を満たせない場合も無断で変更・続行せず、制約緩和を確認するか、未完了範囲と判断点を
付けて `stop-incomplete` とする。固定閾値や決定表、暗黙の追加実行環境は持ち込まない。

normalization 後の worker selection は dispatch まで provisional とする。上位 worker の選択理由が実装難易度ではなく、残存判断密度、複数 semantic family の保持、worker による AC / 責任境界 / dependency の再設計である場合、親は同じ candidate identity と観測理由を `implementation-unit-design` へ一度だけ戻す。境界が明瞭なら final selection へ進み、閉じなければ `blocking_gaps` または `stop-incomplete` とする。上位 worker が実装難易度のため必要なら維持でき、上位 worker 禁止、自動 split、tier threshold、再帰 loop を導入しない。

既定の実行順は直列である。各 worker の結果は accept 候補に過ぎず、親が run の baseline に適用して確認するまで
accepted ではない。統合後の diff、dirty state、AC、scope、precondition、side effect、repository-native verification
を親が確認し、Green で再現可能な accepted baseline だけを後続単位の base にする。

## Writable scope Kernel loader and worker handoff


最初の write-capable Worker handoff より前に、親は writable scope Kernel を load して identity と必要 section を検証する。
次の Loader Data がこの load の唯一の正本である。

```text
path = ../../references/writable-scope-kernel.md
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

## Fresh context and continuation

委譲する新しい ID の Implementation Unit は、Implementation Unit Data、依存、`base_snapshot`、選択 worker と route、execution constraint、
isolation、外部副作用の状態、禁止範囲、verification を含む自己完結 handoff で fresh context へ渡す。direct の単位は
親 context で実行し、新しい worker を起動しない。

委譲する新しい単位は新しい worker の起動で `fork_turns: "none"` の新しい worker context に起動する。追加作業を
同じ context に返す場合に限り、同じ ID の実装上の限定修正だけを`followup_task`で同じ context に返す。

無応答時の状態確認は親所有の silence status inquiry であり、既存の`followup_task`を使う。これは実装上の
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

## Safe parallel dispatch and integration

ここで扱う並列化は実装 batch に限る。immutable snapshot と no writer を満たす reviewer の同時 read-only 観測は、実装 batch と重ねない別の実行として許す。候補間の依存がなく、path、derived output、semantic invariant、shared mutable state、
external namespace の競合がなく、同じ再現可能な base から隔離され、個別 QA と統合 verification が可能で、適用順が
結果を変えないことをすべて説明できる場合だけ並列に dispatch する。要求されても一つでも説明できない場合、ユーザーが
parallel を要求していなければ直列化できるが、要求している場合は無断で直列化せず確認または `stop-incomplete` とする。
判断理由と isolation を execution data に残す。並列中に hidden dependency、scope overlap、base drift が判明した場合は
新規の並列 dispatch を止め、返却を個別候補として QA し、無理に merge しない。

親が eligibility と順序不変を確定した並列返却の統合は `parallel-candidate-integration` へ渡す。この Flow の
`final combined verification` は run closeout の repository gate を省略しない。

## Review principle

自己検証は不確実性を減らすが、独立レビューの代替にはならない。

親は、自己検証の結果だけを理由に独立 review の価値を消去せず、独立した観点による追加の反証機会の価値を
自己検証とは別に評価する。reviewer を選ばない判断も、自己検証が Green であること自体ではなく、追加の反証機会が
親の判断を変えうるかの評価に基づける。その後、既存の risk-directed review に従い、review の要否、対象、重点を
自律的に判断する。

## Risk-directed review selection and handoff

reviewer はユーザーが明示した review goal、または親が AC、diff、test、外部副作用、責務境界その他から特定した具体的な
risk があり、review 結果が修正、`accept`、`stop-incomplete` の判断を変えうる場合だけ選ぶ。ただし、この risk-directed な
任意選択とは別に、全 Implementation Unit の run を閉じる直前には `writing-principles-reviewer` の final writing gate を必ず実施する。
全作業を reviewer に通す固定 phase、非選択 reviewer の台帳、固定 threshold、巨大な decision table は作らない。明示された
reviewer、目的、回数その他の制約は守る。指定 reviewer が利用不能で、親と代替 evidence だけでは許容不能 risk を検証できない
場合は確認を求めるか、`stop-incomplete` とする。

既存 reviewer の責務は review goal に対応するものだけを選ぶ。

- `plan-adversarial-reviewer`: 実装前 plan の具体的な failure path。
- `test-quality-reviewer`: test 設計、欠落 case、Gunte antipattern。
- `responsibility-boundary-reviewer`: 責務混在、境界、分散した副作用。
- `security-side-effect-reviewer`: security、破壊的操作、外部副作用。
- `static-performance-reviewer`: diff が発火または増幅した、静的 evidence で示せる性能・資源効率リスク。
- `writing-principles-reviewer`: How / What / Why / Why Not の配置。
- `over-engineering-reviewer`: 除去しても AC と制約を失わない要素。

汎用 reviewer を作らず、選択理由と期待する判断変更を execution data に記録する。各 reviewer へは固有の既存入力・出力形式を
保った自己完結 handoff を渡す。diff reviewer には task / Implementation Unit、AC、scope と constraints、base / target snapshot、
commit range、変更 file、完全な diff text、必要な test 結果と周辺 context を含め、checkout path、repository path、commit ID
だけで diff text を代替しない。plan reviewer には plan 全文と AC / constraints を渡す。diff artifact の存在は必須にせず、
inline か reviewer が全文を読み込める artifact のいずれかを使う。

## batch-resolve-kernel v1 の risk-directed review mapping

次の Loader Data が列挙値の唯一の正本である。

```text
path = ../../references/batch-resolve-kernel.md
identity = batch-resolve-kernel-v1
dependencies = none
required_sections = [適用モデル, snapshot discipline, Resolution Transaction, caller boundary]
failure = stop-incomplete
owner = impl-lead parent
```

親は risk-directed review の最初の Resolution Transaction 前に、上記 Loader Data の field を使って load と必要本文の検証を行い、
failure field に従って失敗処理する。owner の path-resolution boundary を維持する。
この loader は finding が0件の review、final writing gate だけの処理のためには起動しない。

次の role Data が列挙値の唯一の正本である。

```text
caller = impl-lead parent
resolver = impl-lead parent
counterpart = risk-directed reviewer
target_snapshot = origin verified snapshot
finding = Resolution Point
same_snapshot_findings = Resolution Batch
dispositions = [adopted, rejected, unresolved]
```

親は上記 role field と後続の transaction field を使って finding の mapping、return、Implementation Unit / run acceptance の
Action を行い、既存の親境界を変更しない。

親は counterpart invocation 前に review set を固定する。必要な全 observation と result を回収し、finding を normalize して
evidence を確認してから Resolution Transaction を開始する。一部でも欠ける場合は暗黙に縮退せず、既存の caller boundary または
`stop-incomplete` へ返す。

### risk-directed review の Resolution Transaction

```text
reviewer_observation = outside Resolution Transaction
result_collection = outside Resolution Transaction
batch_freeze = before mutation
zero_findings = no Resolution Transaction
adopted_findings = coherent remediation
updated_snapshot_re_review = new Resolution Transaction
transaction_closure = not Implementation Unit acceptance, not run acceptance
final_writing_gate = outside mapping
```

上記 Data は impl-lead 固有の caller mapping だけを定める。generic Transaction procedure は Kernel を唯一の正本とし、
既存の Implementation Unit、AC、scope、exclude、責任境界を拡張しない。

### selected finding remediation の Implementation Unit normalization

同じ origin verified snapshot の Resolution Batch を全件裁定して selected finding set を固定した後、set が非空なら、親は trivial / nontrivial を先に分類せず、mutation / apply の前に関連 remediation candidates を必ず `implementation-unit-design` へ渡す。zero findings では起動しない。
入力は各 finding の identity、obligation、AC、mutation oracle、disposition と既存 Implementation Unit context を保持する。返却される canonical Implementation Unit candidates について、親が要求 coverage、`blocking_gaps`、Implementation Unit Data / execution Data 境界、採否、ID を確定する。

remediation の `partition_perspectives` は、origin verified snapshot、finding dependency / shared invariant、coherent apply / combined verification、authority / external side effect、rollback / failure isolation、independent promotion boundary を照らす。元の Skill 数や Implementation Unit 数を根拠にせず、固定 remediation mode、件数 threshold、solver、expected-output oracle、ledger を導入しない。

apply / verify / isolate / applicability check により、membership、dependency / conflict / shared invariant、verification point interaction、authority / side effect、rollback / failure isolation、promotion precondition の grouping-relevant evidence が実質変化した場合、親は元の Resolution Batch に閉じた corrective adjudication を行い、次の apply 前に current verified snapshot と未処理 selected obligations だけを `implementation-unit-design` へ再入力する。promoted obligation は再入力、再 apply、別 group への再統合をせず、evidence と membership が不変なら再実行しない。

各 remediation group 全体を既存の `implementation-unit-continuation-routing` へ渡す。一つの既存 ID に由来する全 obligation が一 group に閉じ、aggregate AC、scope、責任境界、dependency が不変の場合だけ same ID / context を使う。cross-ID、new-ID-required、または一つの既存 ID 由来の obligation を複数 group へ split した各 group には fresh unique ID / context を割り当て、finding identity は保持する。

Implementation Unit grouping は外側の accept / dispatch boundary、Batch Resolve Kernel partition は各 Implementation Unit 内側の apply / verify boundary とする。Kernel は一つの Implementation Unit を複数 partition へ refine できるが、複数 Implementation Unit を一つの partition へ coarsen せず、常時 1:1 ともしない。inner transaction closure だけで Implementation Unit を accept しない。

## Review findings and continuation

親は reviewer の固有出力を execution data に正規化する。各 finding は `source_reviewer`、`target_snapshot`、reviewer の
native ID（なければ run 内一意の normalized finding ID）、evidence、影響する AC / risk、提案、親の採否と理由を持つ。
成立性は主張に応じた一次情報で確認する。repository 内の事実は diff / code / test、ユーザー制約は要求原文、外部契約は
authoritative な契約または文書、外部状態は Action が観測した Data を根拠にする。repository 内に根拠がないという理由だけで
不採用にしない。

各 finding を `adopted`、`rejected`、`unresolved` のいずれかに確定し、evidence、AC、risk、上位制約に基づく理由を示す。
reviewer の severity や結論を `accept` に直結させず、unresolved finding または許容不能 risk を残したまま accept しない。
同じ snapshot の全 reviewer 結果を集めてから、AC、evidence、security / data loss などの許容不能 risk、scope、rollback、
検証可能性、最小性で競合を解消する。安全に解消できない競合は確認、再正規化または `stop-incomplete` とする。

以下の一般的な `adopted` finding の修正・継続規則は `risk-directed review` に限る。`final writing gate` の finding はこの規則の
対象外であり、後段の final writing gate 固有の stop / remediation 規則に従う。`adopted` finding の修正は既存の route / context 規則へ戻す。同じ ID で AC、scope、責任境界、依存が不変の限定修正だけを
同じ context へ返す。意味契約が変わる修正は新しい ID と fresh context へ再正規化し、固定修正 agent を導入しない。修正後は
親 QA と repository-native verification を再実行し、影響を受けた review goal
だけを新しい snapshot で再 review する。親 QA、新 diff、新 test、副作用 evidence が新しい具体的 risk を示し、結果が判断を
変えうる場合だけ新しい review goal と対応 reviewer を追加する。影響も新 risk もない reviewer を一律再起動しない。

review を `continue` するのは、次に確認する具体的な未解決 risk と期待する新しい evidence を説明できる場合だけとする。
固定 round、0 findings、reviewer の Pass は打ち切りや accept の条件にしない。親が品質下限、known finding の処理、残存 risk
の許容を独立して確認し、必要な判断が完了した時点で review を打ち切る。

## Final writing acceptance gate

親は全 Implementation Unit、QA、選択した review goal と finding の処理状態を確定し、run accept 直前の必須 invocation を
`final-writing-gate-invocation` へ渡す。返却 result は `final-writing-result-routing` へ渡す。この gate は risk-directed reviewer の
選択数・回数の外にある。

次の Loader Data が列挙値の唯一の正本である。

```text
path = references/final-writing-gate.md
load_timing = before final writing gate
identity = impl-lead final writing gate v1
required_sections = [Final writing acceptance gate, Final writing findings and remediation]
required_scope = [snapshot, handoff, read-only isolation, finding adjudication, bounded remediation, re-gate, closeout data]
failure = stop-incomplete
owner = impl-lead parent
reviewer_authority = report-only
```

親は上記 Loader Data の field を使って load と必要本文の検証を行い、failure field に従って失敗処理する。
owner / reviewer_authority の境界を維持し、reviewer を writer または受入決定者にしない。

## External side effects

外部副作用は worktree と別に execution data で管理する。各 Action に `未実行`、`実行済み`、`結果不明`、resource、
idempotency、照合方法、補償または rollback を記録する。partial failure または context loss 後の retry は、親が状態と
safe-retry eligibility を確定して `external-side-effect-retry` へ渡す。共有 resource の順序や競合がある場合は並列化しない。
未実行の外部 Action について、選択済み review goal の結果が実行可否、対象 / 入力、
authorization、idempotency、compensation / rollback を変えうる場合、その review 完了と関連 finding の解決を当該 Action の
precondition にする。外部副作用を伴わない code 作成、および外部 Action を含まない local / read-only verification だけは先行できる。
verification command 内に外部 Action が含まれる場合も、同じ review 完了と関連 finding 解決の precondition を適用する。外部 Action 後に初めて risk が判明した場合は
外部状態と result identity を再観測し、既存の外部副作用契約に従って補償、確認または `stop-incomplete` を選ぶ。事後 review を
実行前保証として扱わない。

## Execution data and conditional persistence

Implementation Unit、plan、finding、QA 結果は会話内 execution data を既定とする。ユーザー要求、後日再開、別 session / 別担当への
handoff、外部 review、PR、監査、tool / repository 運用によって現在 context より長く生存する必要がある場合だけ、必要な data を
一般化した persistence resource へ保存する。complexity、file 数、Implementation Unit 数を固定 threshold にしない。

保存時は resource の purpose / content、identity、ownership / authorization、sensitivity、current state、idempotency、照合方法、
retention / lifetime、update / cleanup / compensation を確定する。filesystem / repository では path、tracked / untracked、
protected dirty state、overwrite の有無、書き込み後の content / status を確認する。PR / Issue / API / artifact store では URL、
resource ID、revision、remote state、API result を確認する。ユーザー所有 resource を無断で上書きまたは削除しない。必須の永続化を
安全に実行・照合できなければ確認または `stop-incomplete` とする。artifact が存在すること自体を quality evidence にしない。

## Implementation and TDD

親と worker は、確定した purpose、AC、scope、constraints、depends_on、verification を共有し、指定範囲だけを
編集する。既存 test の削除、skip、期待値の弱体化、未承認の依存追加、生成物の直接編集はしない。

observable な code behavior は各 Implementation Unit で Red → Green → Refactor を進める。

1. **Red** — AC から正常系、境界値、異常系、例外経路を導いた test を先に追加し、意味のある failing output を記録する。
   これを Red 証跡として返却 data に含める。意味のある failing test が成立しない場合は、変更前の evidence、成立しない
   理由、代替 verification を返す。形式的な mutation は行わない。
2. **Green** — 最小の実装で test を通し、focused test と必要な native verification の command と結果を記録する。
3. **Refactor** — AC、責任境界、error handling、命名を保ったまま重複を整理し、Green を再実行する。意味が変わる場合は
   Green に戻り、同じ Implementation Unit の範囲を越えない。

## Parent QA and closeout

direct でも委譲でも、親は各単位の結果を受け取った時点の baseline diff、AC、scope、precondition、dirty state、
test、side effect、既知 risk を自分で確認する。親は worker の報告を鵜呑みにせず、Red/Green/Refactor の evidence、focused
test、repository-native verification を再実行し、変更が同じ Implementation Unit の責任境界内にあることを確認する。

### Run-owned closeout

run-owned worktree を作成した run は、先に読み込んだ `run-owned lifecycle` reference の `Closeout` に従う。親 QA、選択した
risk-directed review、final writing gate、final verification、必要な外部副作用の照合後に、親は観測 Data を
`run-owned-closeout` へ渡す。

追加作業の continuation route は `implementation-unit-continuation-routing` に従う。親が品質下限を満たし、全要求単位を accepted とし、
選択した review goal と finding の処理結果を確認し、AC、scope、制約、evidence、残存 risk を説明できる場合は、run accept 前に closeout の repository gate を含む final closeout verification を
実施する。その verification が Green なら run を accept する。新しい failure が出た場合は run を accept せず Adapt または
`stop-incomplete` へ戻す。品質下限等を満たせない場合は、未完了範囲、満たせない条件、判断点、evidence、残存 risk、未検証事項を明記して
`stop-incomplete` とする。固定状態機械や常時必須の永続化された実行成果を新設しない。

### Final report quality signals

最終報告は run の品質シグナルを短く示す。以下の policy Data は要約の意味を固定する正本であり、report output schema、固定 format、新しい Data model、永続 artifact を導入するものではない。

```text
signal_policy = "bounded final-report quality signals"
run_verdict = "accept | stop-incomplete"
implementation_unit_signal = "identity + short summary + implementation owner + scoped optional risk-directed reviewer + viewpoint + distinguishable verification result"
reviewer_absence = "none is explicit"
verification_result = "a result Human can distinguish as passed, failed, not run, or unverified"
final_writing_gate = "mandatory run-wide; separate from optional risk-directed review; report execution fact and scope"
pre_gate_stop = "stop-incomplete before gate => gate not run"
conditional_concern = "notable decision / unresolved concern only when present; short; no ledger or fixed decision table"
default_push = "commands, finding adjudication, base, isolation, dependency are not pushed"
conversation_pull = "same-run observed and recorded conversation execution data only"
historical_reconstruction = "do not claim retrieval or reconstruction of past state"
responsibility_invariance = "route, worker/reviewer selection, review responsibility, accept/stop-incomplete, persistence responsibility and conditions unchanged"
```

この policy Data を満たす範囲で、説明の文言、並び、表示方法は柔軟にできる。Data にない詳細な command、全 finding の裁定、base / isolation / dependency は必要時だけ同じ run の既存 conversation execution data から Pull し、過去状態を再取得・再構成できるとは主張しない。Data の意味に反する decoy や責務の逸脱は、親の semantic QA で裁定する。route、worker / reviewer 選択、review 責務、accept / stop-incomplete、persistence の責務・判断条件は変更しない。
