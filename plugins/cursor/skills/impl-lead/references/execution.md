<!-- Generated from shared/. Do not edit directly. -->

# impl-lead execution v1

この reference は、`impl-lead` の dependency/precondition 判定、base snapshot と isolation、direct route の実行順、TDD、
継続修正の routing を定義する。親は `SKILL.md` で指定された時点に全文を読み、判断と Action を自身の execution data として扱う。

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

### implementation-unit-continuation-routing

Trigger: 親が返却結果に追加作業が必要と確定し、変更の意味分類を完了したとき。
Inputs: 同じ ID の AC・scope・責任境界・依存が不変な限定修正、または意味変更・accepted 単位の変更という親の分類、旧 ID / context、依存 edge。
Procedure: 限定修正だけを同じ ID / context へ continuation し、意味変更または accepted 単位の変更は ID / context を確定せず `renormalization-required` を返す。依存 edge を一意に再接続できなければ `blocked` とし、二重計上しない。
Outcomes: `same-context-continuation`、`renormalization-required`、または `blocked`。分類や再接続の意味判断が未確定なら Agentic な親へ返す。

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
安全に委譲できるなら一名の worker を選ぶ。worker tier の選択は `references/delegation.md` に従う。選択理由を execution data に
記録する。

既定の実行順は直列である。各 worker の結果は accept 候補に過ぎず、親が run の baseline に適用して確認するまで
accepted ではない。統合後の diff、dirty state、AC、scope、precondition、side effect、repository-native verification
を親が確認し、Green で再現可能な accepted baseline だけを後続単位の base にする。

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
