# impl-lead external effects v1

この reference は、`impl-lead` が扱う外部副作用の Action 状態管理、partial failure 後の retry、conditional persistence の
operation 詳細（filesystem / repository / PR / Issue / API）を定義する。親は `SKILL.md` で指定された時点に全文を読み、
判断と Action を自身の execution data として扱う。

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

<!-- @contract impl-programmatic-flow-external-side-effect-retry -->
### external-side-effect-retry

Trigger: 外部 Action の partial failure または context loss 後に、親が retry 可否の固定判定を要求したとき。
Inputs: fresh context で再観測した resource / result identity、`未実行` / `実行済み` / `結果不明`、idempotency、照合方法、authorization、compensation / rollback、親が確定した safe-retry eligibility。
Procedure: `結果不明` または安全な照合不能なら retry せず `blocked` とする。`未実行` かつ safe-retry eligibility 成立時だけ一回再実行して結果を照合し、`実行済み` は再実行しない。
Outcomes: 照合済み `実行済み` Data、または `blocked`。unknown result を blind retry せず、補償、確認、`stop-incomplete` の意味判断は Agentic な親へ返す。
<!-- @/contract -->

## Conditional persistence operations

保存時は resource の purpose / content、identity、ownership / authorization、sensitivity、current state、idempotency、照合方法、
retention / lifetime、update / cleanup / compensation を確定する。filesystem / repository では path、tracked / untracked、
protected dirty state、overwrite の有無、書き込み後の content / status を確認する。PR / Issue / API / artifact store では URL、
resource ID、revision、remote state、API result を確認する。ユーザー所有 resource を無断で上書きまたは削除しない。必須の永続化を
安全に実行・照合できなければ確認または `stop-incomplete` とする。artifact が存在すること自体を quality evidence にしない。
