---
name: plan-craft-approval
description: >-
  ユーザーが明示した場合だけ、人間との方向性裁定から計画・設計成果物を起草し、gate と固定 review を経た
  確定候補または未完了結果を返す public workflow。
disable-model-invocation: true
---
<!-- Generated from shared/. Do not edit directly. -->

# plan-craft-approval

この Skill は人間参加型の自由形式計画・設計成果物を起草し、親が確定候補または未完了結果を返す public workflow
である。`plan-craft` と自動切替せず、双方向ともユーザーの明示起動だけで開始する。

## 発火制御と責務

- `$plan-craft-approval` または同等の明示要求がある場合だけ起動し、context から暗黙起動しない。
- Claude の `disable-model-invocation: true` と Codex metadata の `policy.allow_implicit_invocation: false` が
  explicit-only 契約を表す。
- 実装、委譲、Worker 起動、worktree 操作、後続の実装開始を行わず、workflow は成果物を自律的に保存しない。
- 起草、対話、gate、review、final acceptance 候補または未完了の返却までを担う。人間は方向性と最終結果の責任を持ち、
  public workflow parent は planner として、調査、具体化、整合性、verification、工程の経過責任を持つ。後続 Action は
  人間へ残す。

## 入力と成果物

要求原文、目的、対象、成功条件、scope、exclude、依存、制約、current state を先に観測する。blocking な不足を
推測せず、軽微な不足は根拠付き assumption に分離する。成果物には目的、観測可能な成功条件、設計、scope と exclude、
依存、制約、選択理由、棄却した代替案、verification、残存 risk、未確定の問いを含める。

成果物種別を `artifact_kind` Data として保持する。実装前提プラン系か否かは reviewer 適用可否だけに使い、自由形式
成果物をプラン系へ変える理由にしない。実装前提プラン系は `Acceptance Criteria` と `設計` の節名を持つ。

## proposal-dialogue の前段

同じ親 context の internal `proposal-dialogue` を開始し、人間の裁定を逐次反映・verification した direction freeze
候補を受け取る。blocking な人間判断が残る、または `stop-incomplete` の場合はそこで停止し、後段へ進めない。

direction freeze は成果物全文の固定ではなく、人間が確定した意味判断を保護する境界とする。親は方向性、実装イメージ、
重要な verification を圧縮して人間へ示し、freeze 後の gate と review へ frozen decisions と変更可能な具体化を区別して渡す。
大きな purpose または scope の変更が入力された場合は既存成果物へ増分追加せず、この public workflow 全体を再策定する。
過去 decision は自動継承せず、candidate prior decisions と再利用知見として現在の要求と evidence で再検証する。

## structural-health-gate

direction freeze 候補を受け取った場合は、提案が全件却下された場合も同じ親 context の internal
`structural-health-gate` へ渡す。input には generic `caller_context` Data（`workflow_family: proposal-family`、
`invocation: explicit-public-parent`）を含める。`context 不成立` は別 route へ切り替えず `stop-incomplete` とする。

親は gate 予算を独立した `rounds` Data として管理し、assessment 1回を1 round と数える。`rounds.limit` は下限1の
ceiling とし、ユーザー指定を優先する。未指定なら親が loop 開始時に固定し、1未満は補正せず `stop-incomplete` とする。
1未満では assessment、producer の再実行、後段を起動しない。gate 予算と review 予算は別 Data とする。

`pass` は直ちに後段へ進む。`return` は現在の round が limit 未満の場合だけ、gate evidence を人間へ自然文の新しい
判断点として提示できる入力にして `proposal-dialogue` を新しい対話 loop として再実行し、別内容の candidate を再評価する。
limit 到達 round の `return` と `insufficient-evidence` は
`stop-incomplete` とする。人間が構造 finding への対応を全件却下し candidate 内容が変わらない場合、同一内容へ
別 identity を付けて再投入せず、構造欠陥未解消として `stop-incomplete` とする。

## review の適用と固定順序

工程順序は `proposal-dialogue → structural-health-gate → review-loop` であり、gate が `pass` した snapshot だけを
次の判定へ渡す。まず `artifact_kind` と既定 `plan-adversarial-reviewer` の責務から reviewer 適用可否を判定する。既定 reviewer の適用対象外なら、review goal に対応する別 reviewer の有無にかかわらず `review-loop` に投入せず、通常の起草確定へ進む。review 省略の明示より reviewer 適用可否の判定を先に行う。

reviewer 適用可能な成果物は、ユーザーによる review の明示要求がなくても固定工程として `review-loop` へ渡す。
ユーザーが review 省略を明示した場合は、確定候補とせず、review 未実施の起草物と残存 risk を添えて未完了として返す。

`review-loop` には不変 snapshot、`artifact_kind`、`caller_context`、要求と判定基準、review goal、reviewer・回数制約、
必要なら継続台帳を渡す。回数制約がなければ親が loop 開始時に上限と打ち切りを決める。既定 reviewer は
`plan-adversarial-reviewer`、final trim は `over-engineering-reviewer` のプラン入力モードである。`review_goal` は、ユーザー指定の review goal や追加の具体的な risk がない場合、「実装前プランの具体的な failure path を確認し、確定候補にできるか判断する」とする。これは plan review 自体の既定目的であり、毎回 risk を事前発見することを要求しない。ユーザー指定 goal や追加 risk は既存 reviewer の責務内で追加できる。入力前提不足は
補って再投入するかレビュー不成立として返す。

## review 結果と direction freeze の保護

通常出力の成果物、指摘台帳、判断保留台帳、未解決 finding、final trim、`termination`、
`adversarial_review_count` を受け取る。親は finding を既存5区分（採用、却下、範囲外、判断保留、人間確認）へ
evidence と理由付きで裁定する。判断保留は loop 中凍結し、round、誘発収束、未解決 finding を再計算しない。

decision ledger で人間が裁定済みの方向性を変更・撤回する finding は、局所修正で閉じる場合も親だけで採用せず
`人間確認` へ裁定する。人間の再判断後だけ成果物へ反映し、既存の裁定区分を増やさない。

review は frozen decisions を守る限り、実装の具体化、verification の補強、複雑性の削減を行える。frozen decision の
変更が必要なら、改善案を採用せず `人間確認` へ止める。

## review 完了と final acceptance

review 実行経路では `converged` または未解決 finding のない `induced-loop` だけを確定候補とする。レビュー不成立、
`round-limit`、`stop-incomplete`、未解決 finding を伴う `induced-loop` は確定候補とせず、理由、台帳、残存 risk を
添えて未完了として返す。代替 evidence で完了扱いにしない。

`review-loop` が新しい設計選択を必要として `stop-incomplete` を返しても `proposal-dialogue` へ自動逆遷移しない。
人間へ対話の再開、未完了終了、scope 外への分離を提示する。未完了返却後の受け入れと再投入、および保存を許可するかは
人間が明示的に判断する。

final acceptance は direction freeze と分離し、既定で必須とする。人間が明示的に opt-out した場合だけ承認 Action を
省略できるが、final report は省略しない。親は全文精読を要求せず、方向変更の有無を明記した `Semantic Delta`、追加・変更した
検証とその結果を示す `Verification Delta`、残存 risk を提示する。Verification Delta は特に境界、異常・failure path、
壊れやすい既存挙動、禁止副作用、責務境界を優先し、成果物全文は人間が要求した場合だけ提示する。

final acceptance での修正要求は正常な結果として扱う。親は変更の影響と依存する判断だけを新しい `proposal-dialogue` loop で
局所 reopen し、decision ledger 全体をリセットしない。再 review は変更箇所と直接・間接の波及へ限定し、無関係な領域へ
探索を広げない。大きな purpose または scope の変更なら局所 reopen を行わず、public workflow 全体を再策定する。

## persistence と出力境界

成果物は既定で会話内 Data とする。人間の明示要求または許可がある場合だけ、public workflow parent が結果確定後に
指定 resource へ保存 Action を実行する。出力には成果物本文、direction freeze、
gate と review の実行結果、確定候補か未完了か、問い、残存 risk を含める。実装・委譲・次工程へ進んだと誤解される
status を返さない。
