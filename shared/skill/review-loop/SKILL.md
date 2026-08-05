<!-- @only claude -->
---
name: review-loop
description: >-
  ユーザーが明示した成果物レビュー、または plan-craft が工程として起動する場合だけ、
  不変 snapshot と review goal に対する bounded review round と final trim を実行する。
  reviewer は事実と懸念を報告し、親が裁定と受け入れを保持する。v4 skill と impl-lead の
  実行中には発火せず、成果物を書き戻したり次工程を開始したりしない。
---
<!-- @/only -->
<!-- @only codex -->
---
name: review-loop
description: >-
  ユーザーが明示した成果物レビュー、または plan-craft が工程として起動する場合だけ、
  不変 snapshot と review goal に対する bounded review round と final trim を実行する。
  reviewer は事実と懸念を報告し、親が裁定と受け入れを保持する。v4 skill と impl-lead の
  実行中には発火せず、成果物を書き戻したり次工程を開始したりしない。
---
<!-- @/only -->

# review-loop

この Skill は、入力 resource 自体を直接書き換えず、明示された review goal に対して各 round で固定した
snapshot を読み、親が採用した変更と verification を snapshot ごとに反映する review loop である。起動元は
`plan-craft` に限らず、親が既存の成果物（issue 本文へ保存した
プラン等）を単独でレビューする場合も含む。reviewer は確認できた事実と懸念に集中し、新しい仕様を
補完せず、finding の採否・保留を確定しない。親は最終的な品質下限、残存 risk、成果物の受け入れを
保持する。

## 発火制御

- ユーザーがこの Skill によるレビューを明示した場合にだけ単独で起動する。
- `plan-craft` が起草工程の review として起動する場合は起動できる。
- v4 skill の実行中、`impl-lead` の実行中、またはレビューを求めない相談では起動しない。
- 発火条件を満たさない自然言語の作業内容や context から、起動を推測しない。
- Claude の frontmatter は暗黙起動を無効にしない。ただし上記の description と本文の条件を守る。
- Codex の metadata は `allow_implicit_invocation: true` とし、暗黙起動を許す範囲を上記の条件に限る。

## 入力

起動前に親は次の Data を渡す。入力 resource と各 round の対象 snapshot は不変として扱い、review 中に
書き換えない。採用した修正は入力 resource へ戻さず、次 round が読む新しい snapshot Data を生成する。

- `artifact_snapshot`: 各 round が読む対象成果物の識別子と内容。round 中は不変として扱い、同じ内容を読む。
- `artifact_kind`: 実装を前提とするプラン系か否か。reviewer の適用可否に使う。
- `request`: 要求原文、AC 相当の判定基準、constraints、既知の依存。
- `review_goal`: 確認する具体的な risk と、結果が変える親の判断。
- `reviewers`: ユーザー指定または goal に対応して親が選んだ reviewer。省略時の通常 reviewer は
  `plan-adversarial-reviewer`、final trim は常に `over-engineering-reviewer` のプラン入力モード。
- `rounds`: `limit`（下限 1）その他のユーザー指定制約。省略時は親が loop 開始時に上限と打ち切りを
  自動決定して execution data に固定する。
- `over_engineering_review`: `threshold`、`base_rounds`、`escalated_rounds` の部分設定（省略可）。
- 継続 review では `finding_ledger`、`hold_ledger`、各 round の成果物 snapshot を復元可能な loop-owned
  resource として渡す。復元不能なら induced convergence を確定しない。

通常 reviewer の適用対象は、観測可能な判定基準を「Acceptance Criteria」の節名で持ち、「設計」の節名を
持つ実装前提プラン系成果物である。前提を欠く場合、または非実装系成果物に goal 対応の既存 reviewer が
ない場合は reviewer を起動せず、理由付きでレビュー不成立を返す。汎用 reviewer を新設しない。

## reviewer の責務と選択

通常 round の既定は `plan-adversarial-reviewer` で、具体的な failure path を指摘する。final trim は
`over-engineering-reviewer`（プラン入力モード）に固定する。それ以外の既存 reviewer は、ユーザーが明示
した場合、または review goal が既存 reviewer の責務に対応する場合だけ親が選ぶ。6 reviewer の責務と固有
の入出力契約は変更しない。

reviewer には対象 snapshot、要求と判定基準、goal、直前までの台帳、必要な周辺 context を渡す。reviewer の
出力は事実・evidence・懸念・提案であり、仕様の追加、採用、却下、保留、成果物の書き戻しを含めない。

## round と実行 Data

1 round は、`snapshot 固定 → review goal に基づくレビュー → 親の finding 裁定 → 採用修正 → verification`
である。verification は採用 finding が成果物へ反映されたことを確認し、成果物が実行可能な検証手段を
持つ場合はそれも含める。同じ snapshot に複数 reviewer を起動しても同じ round なら 1 round と数える。
`adversarial_review_count` は reviewer 起動回数ではなく、全 review round 数である。final trim は round 計数と
誘発判定の窓から除外する。`plan-adversarial-reviewer` を起動した round だけを baseline と induced 窓の計数へ使う。
trim の finding も同じ指摘台帳へ記録し、発行元 reviewer で区別する。

finding ごとに `id`、発行元、対象 snapshot、evidence、影響する AC / risk、親の裁定、理由、`induced`（通常
reviewer の収束母数だけ）を記録する。全 round・全 reviewer 通算の指摘台帳を維持し、未解決 finding は裁定
未確定、採用修正の未反映、または `人間確認` とする。`判断保留` は凍結済みの完了した裁定なので未解決に
含めない。

## 親の裁定

親は各 finding を次の5区分の一つへ裁定し、evidence と理由を記録する。

1. **採用** — 成果物を修正して verification する。
2. **却下** — 既存仕様または evidence に基づき修正しない。
3. **範囲外** — 成立性は否定しないが対象外として残存事項へ渡す。
4. **判断保留** — 仕様未決、記載漏れ、誤認、対象外、情報不足のいずれかを確定できないため凍結する。
5. **人間確認** — 実装・公開・互換性など、親だけでは決められない確認を要求する。

裁定区分と別に、通常の `plan-adversarial-reviewer` finding の影響度を `軽微`、`修正推奨`、`修正必須`
のいずれかへ親が確定する。final trim の finding には影響度を要求しない。reviewer の severity や Pass を
親の `accept` へ直結しない。

### 判断保留の凍結

判断保留は loop 中に次の規則で凍結する。

1. `hold_ledger` へ記録する。
2. 次 round の入力へ台帳を渡す。
3. reviewer へ再指摘・深掘りを抑制するよう明示する。新しい根拠なしの再指摘は既存保留へ紐付ける。
4. 保留事項を根拠に追加仕様や例外処理を派生させない。
5. loop 後の扱いは親または人間が別途決める。

## 打ち切りと収束

ユーザーが round 数または打ち切りを指定した場合はその制約を優先する。指定がなければ、親は開始時に
round 上限を宣言し、具体的な未解決 risk と期待する新しい evidence を説明できる間だけ continue する。
固定 round、0 findings、reviewer の Pass、上限の消化だけを受け入れ根拠にしない。上限到達時は必ず
`termination` を確定する。

### 誘発指摘による有界収束

`plan-adversarial-reviewer` を起動した round のうち、親確定の `修正必須` が初めて 0 になった round を
`baseline_round` として記録し、取り直さない。既定 reviewer を起動していない round は基準にも「基準の
2 round 後」の計数にも入れない。基準以降に採用した修正が導入した記述を対象とする finding へ `induced: true`
を付ける。

基準の 2 round 後から、既定 reviewer の直近 2 round を rolling 窓として評価する。親確定の `修正推奨` 以上
だけを母数とし、誘発 finding が strict majority を占め、窓に非誘発の `修正必須` がなく、母数が空でない
場合だけ `induced-loop` として打ち切る。ちょうど半数は成立しない。final trim や同じ round の他 reviewer
の finding はこの窓へ入れない。打ち切り round の採用 finding は反映し、裁定未記録を残さない。

## final trim

accept-candidate（`converged` または `induced-loop`）で未解決 finding が空の場合だけ、適用対象のプラン系
成果物へ final trim を行う。非適用成果物は trim を省略した事実と理由を出力する。trim は通常 loop へ戻らず、
各回を新しい snapshot へ順に適用する。削減後の verification が失敗した場合は、新しい設計を足さず、該当
削減 finding の裁定を原則 `採用` から `却下` へ戻す。`人間確認` が必要な trim finding は `範囲外` として渡す。
trim の finding もその場で5区分へ裁定し、未解決一覧と残存事項へ反映する。規定3回なら全体構造、レビュー誘発要素、
残存する過剰の順を推奨観点とし、回数を上書きした場合の観点は親が決める。

回数は次で決める。

```text
over_engineering_review_count =
  adversarial_review_count > threshold ? escalated_rounds : base_rounds
```

既定値は `threshold: 5`、`base_rounds: 1`、`escalated_rounds: 3`（`>` なので 6 round 目から 3 回）。各値は
部分上書きを許し、validation は `threshold >= 0`、`base_rounds >= 1`、`escalated_rounds >= base_rounds`。
不正値は補正せず入力エラーとして返す。

## 出力と終了値

通常の出力は、採用 finding を反映した成果物、指摘台帳、判断保留台帳、未解決 finding 一覧、final trim の
実行有無と省略理由、`termination`、`adversarial_review_count` を含む。レビュー不成立（前提不足、対応 reviewer
不在、入力エラー）は通常出力と排他で、理由を含め `termination` と count を付けない。

`termination` は次の4値だけである。

- `converged`: 親が収束と判断した、または上限到達時に未解決がなく、trim へ進む。
- `induced-loop`: 有界な誘発収束で打ち切った。未解決がなければ trim、残れば trim なしで返す。
- `round-limit`: 上限到達時に未解決が残り、trim なしで返す。
- `stop-incomplete`: 安全に継続・裁定完了できず、未解決を残して早期終了する。trim なしで返す。

成果物の status 確定、入力 resource への書き戻し、成果物の受け入れ、次工程の判断は呼び出し元の親が行う。
この Skill は工程を前進させず、仕様を補完せず、入力 resource を無断更新しない。
