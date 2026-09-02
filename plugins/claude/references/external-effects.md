<!-- Generated from shared/. Do not edit directly. -->

# External Effects

## Cross-cutting pre-action boundary

この boundary は caller-neutral shared boundary として特定 consumer の lifecycle / review procedure を所有しない。

この boundary は filesystem、Git、API、Issue / PR、message、database など外部状態を変えるすべての Action に適用する。外部状態を変える Action は、その実行を判断する Calculation から分離する。

caller は各 Action の identity、authority、target、input、precondition を入力として確定する。

caller は各 Action の idempotency key / duplicate semantics、independent verification、compensation、safe retry を入力として確定する。

caller は各 Action の sensitivity、retention、cleanup、および consumer-specific risk / lifecycle disposition を入力として確定する。

caller は各 Action 前に、渡された risk / lifecycle disposition と current state がその Action の eligibility、target、input、authority、idempotency、compensation を変え得るかを裁定する。変え得ると裁定した場合は、必要な review または finding の解決を Action より前に完了する。Action の precondition と result safety はこの boundary に従い、consumer-specific な lifecycle procedure は caller が所有する。

Action state は `未実行`、`実行済み`、`結果不明` を区別する。

実行応答だけで成功とせず、可能なら independent read で effect identity と target state を確認する。partial failure は完了済み effect、未実行 effect、結果不明 effect を分離する。

## Programmatic Flow

### external-action-control

Trigger: authorized outcome に external Action が必要である。

Inputs: Action identity、authority、target、input、precondition、current state、idempotency / duplicate semantics、independent verification、compensation、safe retry、sensitivity / retention / cleanup Data、consumer-specific risk / lifecycle disposition。

Procedure:

1. caller が渡した risk / lifecycle disposition、precondition、および必要な review / finding の解決済み状態を確認する。
2. state が `未実行` で条件が成立する場合だけ Action を一度実行する。
3. independent verification で effect identity と target state を再観測し、`実行済み` または `結果不明` を確定する。
4. `結果不明` では duplicate semantics と safe retry が証明できるまで再実行しない。
5. failure / partial result では authorized compensation の可否、sensitive Data の retention、cleanup を別々に裁定する。

Outcomes: verified `実行済み`、安全に保持された `未実行`、または evidence と retention state を伴う `結果不明`。必須 Action の `未実行` / `結果不明` は caller の completion decision に戻し、不要化の明示がない限り downstream acceptance に進めない。

blind retry、authority の推測、destructive compensation、sensitive artifact の無期限保持を行わない。
