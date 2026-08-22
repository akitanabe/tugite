<!-- Generated from shared/. Do not edit directly. -->

# impl-lead run-owned lifecycle v1

この reference は、`impl-lead` が所有する一時 worktree の作成、local integration、cleanup を定義する。
親は `SKILL.md` で指定された時点に全文を読み、判断と Action を自身の execution data として扱う。

## Creation

### Default run-owned checkout

ユーザーが既存 checkout、別の isolation/worktree、または worktree を使わない制約を指定していない場合、親は
`base_snapshot` を確定し、既存の user-owned tracked state を記録した後、最初の書き込み Action より前に、その snapshot から
run-owned worktree を一つ作成する。作成 Action が run の最初の書き込みであり、source、test、generator、formatter、integration
を既存の current checkout で先に実行してはならない。run-owned worktree は run 全体の既定 checkout とする。Implementation Unit 数だけでは追加 worktree を作らない。
既定実行順は直列のまま、並列 writer や immutable review target など具体的な必要がある場合だけ、既存の
safe-parallel 条件に従って追加 isolation を選ぶ。

この既定の作成では、execution data に `base`（`base_snapshot`）、`owner`（run が所有する resource）、`single_writer`（その時点の
親または委譲 worker）、`paths`（worktree の絶対 path を含む list）、`integration`（親 QA、review、final writing gate、統合、rollback
の責任）、`cleanup`（未統合成果、evidence、再開可能性、user constraint を確認してから決める条件）を確定する。worktree が存在する
こと自体は quality の evidence または accept の根拠にせず、既存の parent QA、review、final writing gate、integration、rollback を
省略しない。

ユーザーが指定した既存 checkout、別 isolation/worktree、または不使用の制約は execution constraint として既定より優先する。
その指定と品質下限が衝突する場合、無断で run-owned または別経路へ変更せず、確認を求めるか `stop-incomplete` とする。run-owned
worktree を作成できない場合も current checkout へ暗黙 fallback しない。未完了範囲と evidence を付けて `stop-incomplete` とする。
作成のために既存の dirty/untracked を commit、move、stash、discard しない。run-owned resource は親が所有し、cleanup は
run の accept 成否だけで機械的に削除せず、user-owned resource（ユーザー指定の checkout/worktree や branch）を無断変更・削除しない。

### Invocation start identity

run-owned Creation Action より前に、親は一つの invocation start Data として repository identity、worktree identity、canonical path、
exact full branch ref、その ref の開始 target である `invocation_start_head`、tracked index/worktree の working state identity を固定する。
Implementation Unit の `base_snapshot` はこの invocation baseline と別の Data として保つ。

tracked working state identity は staged / unstaged、index へ追加済みの entry、削除、mode / type、content identity を表す。secret の本文は
保存・報告せず、安全な digest 等の identity だけを扱う。開始時の untracked / ignored entry は identity baseline として保存しない。
後続の integration preflight では現在の untracked / ignored entry を task changed paths との衝突計算のためだけに観測する。

```text
start_data = invocation identity + tracked working state
invocation_identity = repository + worktree + canonical path + exact full branch ref + invocation_start_head
tracked_state = tracked index/worktree state identity
noise_baseline = none for untracked / ignored
```

## Closeout

### run-owned-closeout

Trigger: run-owned checkout を作成した run で、親が final verification と必要な外部副作用照合を完了し closeout 可否判定へ到達したとき。
Inputs: 検証済み `impl-run-owned-lifecycle-loader` Data と reference 本文、親が観測した成果の永続化、resource identity、tracked state、collision、writer / reviewer 終了 Data。
Procedure: `references/run-owned-lifecycle.md` の `Closeout` だけを procedure の唯一の正本とし、integration result 後の cleanup eligibility を Calculation として判定し、実際の cleanup と post-observation / 照合は Action として実行し、その観測結果を Data として返す。unsafe または unknown なら resource を保持する。
Outcomes: 照合済み integration / cleanup Data、または resource を保持した `blocked`。`blocked` は突破せず `stop-incomplete` と残存 Action の判断を Agentic な親へ返す。

run-owned worktree は成果保管場所ではなく一時的な実行 resource である。ユーザーが保持を指定していない場合、親は
`accepted` と `stop-incomplete` のどちらで終わる run でも、次の closeout 判定を経て安全なときは削除する既定を持つ。
削除は品質 evidence や accept の根拠ではなく、親 QA、選択した risk-directed review、final writing gate、final verification、
必要な外部副作用の照合がすべて完了した後にだけ行う最後の Action である。PR の有無で分岐を作らず、local/remote の
persistence と integration の観測結果を共通の Data として扱う。

closeout は `Action → Data → Calculation → Data → Action → Data` の順に進める。まず親は target の repository identity、worktree identity、
canonical path、exact full branch ref、`invocation_start_head`、HEAD、tracked clean status、全 writer/reviewer の終了、worktree 内だけに残る
exclusive evidence、ユーザーの保持指定、別 run resource との識別を再観測する。Implementation Unit の `base_snapshot` と invocation branch の
baseline は別の Data として pin し、同じ HEAD でも branch ref が違えば同一実行先とは扱わない。継続 PR のように
`base_snapshot` と `invocation_start_head` が異なる場合も、各値を混同せず exact identity を再照合する。

次に Calculation が、(a) run-owned で user-owned checkout/worktree/branch、固定 path、別 run resource ではない、(b) 成果を task-owned
local branch の commit に固定済みで、再開に必要な branch/commit（利用可能なら remote ref も）を報告できる、(c) tracked index/worktree が clean、全
writer/reviewer が終了し、worktree 内だけの未統合成果/evidence がない、(d) target identity と invocation repository/branch ref が一意、
(e) user retention がなく、tracked working state の観測が完了している、を判定 Data にする。
どれかを観測できない、または false なら削除 Action を実行せず、path、branch、commit、理由を付けた `stop-incomplete` を返す。

local integration は別の Action として、integration 直前に invocation repository identity、worktree identity/canonical path、exact full branch
ref、その ref の target、`invocation_start_head`、HEAD、tracked working state identity、tracked clean status を再照合する。
invocation branch の HEAD は開始時 `invocation_start_head` から drift していないことを確認し、Implementation Unit の `base_snapshot` と一致することは
要求しない。開始時から不変の tracked dirty も integration blocker とする。tracked state の保存・照合ができない場合も blocker とする。

task changed paths は `invocation_start_head..task-owned tip` の tree 上の追加・変更・削除 path 集合とする。rename は source / destination、
copy は destination を含める。path は component 単位で比較し、`foo/bar` と `foo/barista` のような文字列 prefix を ancestor / descendant
とはみなさない。

current untracked / ignored entry と task changed paths の同一または component 単位の ancestor / descendant だけを integration collision とする。
noncollision untracked / ignored の追加・削除・内容変更は blocker と通常 result Data の入力にしない。開始時の untracked / ignored baseline は
作らず、現在の entry を必要な preflight 観測として扱う。same / ancestor / descendant collision、repository / worktree / canonical path /
exact ref の identity 不一致、`invocation_start_head` からの HEAD drift、tracked state drift または tracked dirty、観測不能、non-FF を
Calculation してから、blocker がない場合だけ `--ff-only` integration Action を行う。Git operation failure を collision detector として扱わない。
衝突または別の blocker の場合は task-owned branch/commit を保持して未統合理由を Data にする。無条件 checkout/merge、merge commit、rebase、reset、
stash、force、`branch -D` は使わない。

`--ff-only` 成功後は同じ exact branch ref の target と HEAD が task commit に一致すること、tracked working state identity が不変であることを
再観測する。secret の内容は報告せず、path/type/mode/size と安全な content digest などの identity だけで照合する。`--ff-only` の Action status
だけを terminal outcome にせず、失敗後は exact ref/HEAD と tracked working state を再観測する。

再観測が (a) `invocation_start_head` のままなら未統合として扱い、他の安全条件が成立するときだけ worktree を削除して `stop-incomplete`、
(b) task commit なら統合済みとして扱い、tracked working state identity と全 postcondition が成立するときだけ通常 cleanup と `accepted`、
(c) unexpected または観測不能なら worktree を保持して `stop-incomplete` とする。不一致、照合不能、または Action の結果不明なら branch delete
と worktree remove を抑止し、blind retry/force をせず、path、branch、commit、blocker、risk を含む result Data にする。Action 失敗後は
再観測してからでなければ次の Action へ進まない。

統合できない場合でも、task-owned branch/commit に成果が永続化され、tracked index/worktree が clean、tracked working state identity が不変で exclusive evidence がなく、
target identity が一意なら、無理に統合せず `stop-incomplete` と未統合理由を Data にして run-owned worktree を削除する。成果が commit 前、
evidence が worktree 内だけ、writer/reviewer が active、保持指定がある、削除対象 identity が不明、または tracked state の照合不能なら
worktree を残す。

cleanup は integration と分離して Calculation する。integration blocker 後も成果と evidence が worktree 外に固定され、安全条件を満たす
場合だけ run-owned worktree を削除できる。invocation 側の noncollision untracked / ignored drift で cleanup や terminal outcome を止めない。
安全な local integration 後、または上記の安全な未統合終了後の closeout は run-owned worktree を通常削除し、worktree list から対象 identity
が消えたことを照合する。remove が失敗した、または remove 後も identity が list に残る場合は branch delete を行わず、実際に残る path、branch、
commit、blocker、risk を `stop-incomplete` として報告する。merge 済み task branch の safe delete（`git branch -d` 相当）が不成立・失敗でも
worktree の安全な削除を取り消さず、branch を保持して報告する。user-owned branch や別 run resource は変更・削除しない。
closeout の result Data には、`run_outcome`（`accepted` / `stop-incomplete`）、統合/未統合、削除/保持、対象 path、branch、commit、
tracked working state identity、collision を含む観測した blocker、残存 risk を含める。noncollision untracked / ignored は通常 result Data に
出力しない。integration と worktree removal が成立した後の task branch retained は
残存 risk として報告するが、それだけで `accepted` を妨げない。

```text
closeout_scope = tracked identity + collision_free
collision_free = no current task-path collision
protected_identity = repository + worktree + canonical path + exact full branch ref + invocation_start_head + tracked working state
head_drift = blocker
tracked_drift = blocker
tracked_dirty = blocker
exact_ref_target_drift = blocker
task_changed_paths = invocation_start_head..task-owned tip tree path set
collision = current untracked / ignored entry same or component ancestor/descendant of task changed path
noise_baseline = none
noise_report = none unless collision
integration = preflight Calculation then --ff-only Action
cleanup = separate Calculation after integration result
git_failure = not collision evidence
```
