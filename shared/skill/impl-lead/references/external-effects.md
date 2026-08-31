# External Effects

## Cross-cutting pre-action boundary

この boundary は implementation、verification、integration、cleanup を含む run 全体の Action に適用する。filesystem、Git、API、Issue / PR、message、database など外部状態を変える操作は Action として、判断する Calculation から分離する。親は Action ごとに identity、authority、target、input、precondition、idempotency key / duplicate semantics、verification、compensation、safe retry、sensitivity、retention、cleanup を確定する。

親は各 Action 前に Task Spec、current state、current risk evidence から、その Action の eligibility、target、input、authority、idempotency、compensation を review result が変え得るか pre-action disposition を行う。変え得ると裁定して選択した review は当該 Action 前に完了する。specialized reviewer が post-implementation diff を必要とする場合、task-owned local implementation または read-only verification 自体の eligibility をその review が変えないと親が裁定できる範囲だけ先行できる。実 external effect と影響対象 Action は review と finding 解決まで待つ。Git / worktree lifecycle 固有の手順は `run-owned-lifecycle.md`、post-diff specialized review は `risk-review.md` に残し、この reference は各 Action の precondition と result safety だけを横断的に評価する。

Action state は `未実行`、`実行済み`、`結果不明` を区別する。実行応答だけで成功とせず、可能なら independent read で target state を確認する。partial failure は完了済み effect、未実行 effect、結果不明 effect を分離する。

## Programmatic Flow

### external-action-control

Trigger: authorized outcome に external Action が必要である。

Inputs: Action identity、authority、precondition、current state、idempotency / duplicate semantics、verification、compensation、retry safety、sensitivity / retention / cleanup Data、risk disposition。

Procedure:

1. Task Spec、current state、current risk evidence に基づく pre-action disposition と、必要な review / finding が解決済みであることを確認する。
2. state が `未実行` で条件が成立する場合だけ Action を一度実行する。
3. independent verification で effect identity と target state を再観測し、`実行済み` または `結果不明` を確定する。
4. `結果不明` では duplicate semantics と safe retry が証明できるまで再実行しない。
5. failure / partial result では authorized compensation の可否、sensitive Data の retention と cleanup を別々に裁定する。

Outcomes: verified `実行済み`、安全に保持された `未実行`、または evidence と retention state を伴う `結果不明` / `stop-incomplete`。必須 Action の `未実行` / `結果不明` は run acceptance に進めず、Human が明示的に不要化した場合だけ obligation から外せる。

blind retry、authority の推測、destructive compensation、sensitive artifact の無期限保持を行わない。
