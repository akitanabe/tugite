# Run-owned Lifecycle

## Run isolation

親は実装前に integration target の repository / worktree identity、canonical path、exact full ref / head、tracked state、task path collision reality を capture する。run 全体で一つの task-owned branch と repository root 外の run-owned worktree を作り、全 Unit と final verification をその中で行う。user-owned checkout の dirty / untracked / ignored state を変更しない。この reference は Git / worktree lifecycle 固有 procedure を所有し、各 Action の cross-cutting eligibility は `external-effects.md` に従う。

`stop-incomplete` となった run は accepted commits を task-owned branch に保持するが integration target へ部分 integration しない。cleanup eligibility は integration result と分離し、保持が必要な branch / worktree / artifact を先に報告する。

cleanup は成果 commit が固定され、全 writer / reviewer が終了し、必要 evidence が worktree 内だけに残っておらず、対象 identity が明確で、retention obligation がない場合だけ eligible とする。

## Programmatic Flow

### safe-fast-forward-integration

Trigger: 全 Unit accepted、run-wide final verification Green、integration が request authority に含まれる。

Inputs: start / current repository and worktree identity、canonical path、exact full ref / head、task branch head、tracked state、task changed paths、ignored / untracked entries、worktree ownership、integration authority。

Procedure:

1. Action 直前に start / current repository and worktree identity、canonical path、exact full ref / head、tracked state を再観測し、明示的に許可されていない drift がないことを確認する。
2. task changed paths は rename の source / destination と copy の destination を含める。各 changed path と current ignored / untracked entry の same / ancestor / descendant relation を path component 単位で計算し、collision がないことを確認する。
3. target が captured start から許容された状態にあり、tracked change / collision がなく、task head へ fast-forward 可能な場合だけ `--ff-only` 相当の Action を実行する。
4. Action 後に exact full ref / head と tracked state を再観測し、task headとの一致を確認する。
5. integration の成否とは別に cleanup eligibility を確認する。

Outcomes: verified fast-forward と独立した cleanup decision、または task branch を保持した `stop-incomplete`。Action failure / result unknown では force / retryせず branch を保持する。

precondition を merge、rebase、reset、stash、force、tracked-file overwrite で突破しない。result が不明なら再実行せず external-effects の verification boundary に従う。

## Cleanup execution

cleanup Action の直前ごとに run ownership、exact target identity、clean stateまたは明示された discard authority、retention obligation を再確認する。最初に worktree を non-force removeし、消失を再観測できた後だけ task branch のsafe deleteを判断する。いずれかの Actionがfailure / result unknownなら残りを削除せず、identityとevidenceを保持して `stop-incomplete` とする。safe deleteが成立せず成果がbranchに保持される場合は、保持対象と残存riskを報告し、強制削除しない。
