---
name: review-loop
description: >-
  ユーザーが明示した成果物レビュー、または明示起動された proposal-family public workflow が工程として起動する場合だけ、
  不変 snapshot と review goal に対する bounded review round と final trim を実行する。
  reviewer は事実と懸念を報告し、親が裁定と受け入れを保持する。v4 skill と impl-lead の
  実行中には発火せず、成果物を書き戻したり次工程を開始したりしない。
---
<!-- Generated from shared/. Do not edit directly. -->

# review-loop

この Skill は、入力 resource 自体を直接書き換えず、明示された review goal に対して各 round で固定した
snapshot を読み、親が採用した変更と verification を snapshot ごとに反映する review loop である。起動元は
proposal-family public workflow の親が candidate producer 後段の review として明示起動する場合と、親が既存の成果物
（issue 本文へ保存したプラン等）を単独でレビューする場合を含む。reviewer は確認できた事実と懸念に集中し、新しい仕様を
補完せず、finding の採否・保留を確定しない。親は最終的な品質下限、残存 risk、成果物の受け入れを
保持する。

## 発火制御


- ユーザーがこの Skill によるレビューを明示した場合にだけ単独で起動する（ユーザー明示の単独 review）。
- proposal-family public workflow が candidate producer 後段の review として明示起動する場合は起動できる。
- v4 skill の実行中、`impl-lead` の実行中、またはレビューを求めない相談では起動しない。
- 発火条件を満たさない自然言語の作業内容や context から、起動を推測しない。
- 明示された public workflow parent がない context へ自動 switch しない。proposal-family の workflow 間も自動で切り替えない。
- Claude の frontmatter は暗黙起動を無効にしない。ただし上記の description と本文の条件を守る。
- Codex の metadata は `allow_implicit_invocation: true` とし、暗黙起動を許す範囲を上記の条件に限る。

## 入力

起動前に親は次の Data を渡す。入力 resource と各 round の対象 snapshot は不変として扱い、review 中に
書き換えない。採用した修正は入力 resource へ戻さず、次 round が読む新しい snapshot Data を生成する。

- `artifact_snapshot`: 各 round が読む対象成果物の識別子と内容。round 中は不変として扱い、同じ内容を読む。
- `artifact_kind`: 実装を前提とするプラン系か否か。reviewer の適用可否に使う。
- `caller_context`: proposal-family public workflow の parent が明示起動した review か、ユーザー明示の単独 review かを識別する Data。
- `request`: 要求原文、AC 相当の判定基準、constraints、既知の依存。
- `review_goal`: 確認する具体的な risk と、結果が変える親の判断。
- `reviewers`: ユーザー指定または goal に対応して親が選んだ reviewer。省略時の通常 reviewer は
  `plan-adversarial-reviewer`、final trim は常に `over-engineering-reviewer` のプラン入力モード。
- `rounds`: `limit`（下限 1）その他のユーザー指定制約。省略時は親が loop 開始時に上限と打ち切りを
  自動決定して execution data に固定する。
- `over_engineering_review`: `threshold`、`base_rounds`、`escalated_rounds` の部分設定（省略可）。
- 継続 review では `finding_ledger`、`hold_ledger`、各 round の成果物 snapshot を復元可能な loop-owned
  resource として渡す。復元不能なら induced-loop の補助打ち切りを確定しない。

通常 reviewer の適用対象は、観測可能な判定基準を「Acceptance Criteria」の節名で持ち、「設計」の節名を
持つ実装前提プラン系成果物である。前提を欠く場合、または非実装系成果物に goal 対応の既存 reviewer が
ない場合は reviewer を起動せず、理由付きでレビュー不成立を返す。汎用 reviewer を新設しない。

proposal-family public workflow の親から受け取る candidate は、局所的な構造欠陥を事前解消したものに限る。この loop はその後の指摘密度、
実装可能性、検証可能性を扱う。review 中に local fix では閉じない構造欠陥が判明した場合は、location、局所修正で
閉じない理由、予測される amplification / churn を未解決 finding に記録して `stop-incomplete` とする。自動で
`structural-health-gate` または candidate producer へ逆走しない。

## reviewer の責務と選択

通常 round の既定は `plan-adversarial-reviewer` で、具体的な failure path を指摘する。final trim は
`over-engineering-reviewer`（プラン入力モード）に固定する。それ以外の既存 reviewer は、ユーザーが明示
した場合、または review goal が既存 reviewer の責務に対応する場合だけ親が選ぶ。6 reviewer の責務と固有
の入出力契約は変更しない。

reviewer には対象 snapshot、要求と判定基準、goal、直前までの台帳、必要な周辺 context を渡す。reviewer の
出力は事実・evidence・懸念・提案であり、仕様の追加、採用、却下、保留、成果物の書き戻しを含めない。

## necessity-kernel v1 の parent mapping

次の Loader Data が列挙値の唯一の正本である。

```text
path = ../../references/necessity-kernel.md
load_timing = before reviewer invocation or parent adjudication
identity = necessity-kernel-v1
required_sections = [適用範囲, Task Specification, Claim と evidence, Deletion Test]
failure = return-to-parent
owner = review-loop parent
delegate_path_resolution = false
```

reviewer 起動または parent 裁定の前に、親は上記 Loader Data の field を使って load と必要本文の検証を行い、failure field に従って失敗処理する。検証済み本文を既存の `判定基準` または
`必要な周辺 context` の一部にする。`plan-adversarial-reviewer` または final trim の `over-engineering-reviewer` 起動時は既取得 Data を既存の判定基準として渡す。
owner / delegate_path_resolution の境界を維持する。

reviewer の observation / evidence から候補 Claim（追加・維持・変更・除去・検証・調査する obligation）が導かれる
場合、親は既存の判定基準に含めた Task Specification と Deletion Test を一つの snapshot と一つの
Claim に適用する。`necessary` / `unnecessary` / `indeterminate` は新しい verdict field ではなく、親が既存の
`adopted` / `rejected` / `out-of-scope` / `deferred` / `human-confirmation` へ裁定する。`indeterminate` は自動採用・却下せず、必要なら
`stop-incomplete` とする。更新後は新しい snapshot で再判定し、severity、Pass、件数、既存 round budget または
termination を直結させない。これは既存語彙へ写像する規範であり、新verdict fieldではない。

parent-owned adjudication/result values are exactly `adopted`, `rejected`, `out-of-scope`, `deferred`, and `human-confirmation`。

- `adopted`: 成果物を修正して verification する。
- `rejected`: 既存仕様または evidence に基づき修正しない。
- `out-of-scope`: 成立性は否定しないが対象外として残存事項へ渡す。
- `deferred`: 仕様未決、記載漏れ、誤認、対象外、情報不足のいずれかを確定できないため凍結する。
- `human-confirmation`: 実装・公開・互換性など、親だけでは決められない確認を要求する。

## batch-resolve-kernel-v1 の parent mapping

次の Loader Data が列挙値の唯一の正本である。

```text
path = ../../references/batch-resolve-kernel.md
load_timing = before first Resolution Transaction
identity = batch-resolve-kernel-v1
dependencies = none
required_sections = [適用モデル, Snapshot discipline, Resolution Transaction, Caller boundary]
failure = stop-incomplete or review-not-established
owner = review-loop parent
delegate_path_resolution = false
```

親は上記 Loader Data の field を使って load と必要本文の検証を行い、failure field に従って失敗処理する。
owner / delegate_path_resolution の境界を維持する。

次の role Data が列挙値の唯一の正本である。

```text
caller = review-loop parent
resolver = review-loop parent
counterpart = reviewer
target_snapshot = origin verified artifact snapshot
finding = Resolution Point
same_snapshot_findings = Resolution Batch
authority = parent-owned
ledger = finding ledger and hold ledger
```

親は上記 role field を使って既存責務へ mapping する。counterpart observation と reviewer の selection、prompt、
invocation、result collection の Action は transaction 外で行う。

### Normal round の Resolution Transaction

通常の review round は、同じ artifact の origin verified snapshot を固定し、transaction 外で完了した reviewer observation
を finding から Resolution Point へ mapping して、Resolution Batch を transaction 開始時までに固定する。1 normal review round は
原則として1つの Resolution Transaction であり、その内部を次の順序で実行する。

```text
origin verified snapshot + caller-supplied evidence + Resolution Batch
→ 全 finding を裁定し conflict / dependency を解消
→ 親が既存の裁定区分を確定
→ selected set を原則 single partition の coherent revision として apply
→ verify
→ caller-owned semantic progress を確認
→ current verified snapshot を promote
```

mutation 前に Batch 全体の裁定を完了し、未裁定または両立不能な point を selected set に残さない。working state は検証前に
current verified snapshot へ昇格させず、partition ごとに閉じて未検証状態の上へ次の partition を積まない。複数 partition が必要な
場合は applicability check を行い、verify failure は同じ isolation baseline から `isolate` して局所化する。transaction 内で新しい
execution evidence が得られた場合だけ元 Batch の point へ corrective adjudication を行い、新しい point や frontier を追加しない。
成功済み partition は rollback せず、安全に継続できない結果は既存の親 boundary へ返す。

transaction 中に Batch membership を増やさず、snapshot 更新後に frontier を再計算しない。既存 review-loop の round、termination、
adversarial review count、induced-loop、final trim count の意味と境界は維持し、Kernel mapping から変更しない。

verify と semantic progress の両方が成功した後だけ current verified snapshot を更新する。次 round の decision は review-loop-owned
であり、更新済み snapshot を観測する次 round は新しい Resolution Transaction とする。

### Multiple reviewer の Batch 境界

同じ round、同じ artifact、同じ origin verified snapshot に対する複数 reviewer の finding は原則1つの Resolution Batch に束ねる。
各 finding の reviewer provenance は保持するが、reviewer ごとの多数決や priority は導入しない。異なる snapshot の finding は混ぜず、
reviewer identity ではなく observation snapshot を Batch boundary とする。snapshot が混在している場合は推測で統合せず、未検証の
mutation を行わずに既存の caller boundary へ返す。

### Parent-owned ledger

Kernel の execution result と evidence を使い、review-loop parent が既存の `finding_ledger` と `hold_ledger` を更新する。Kernel は
ledger、round、termination、induced-loop、ledger の carry-over を所有または更新しない。既存の5値（`adopted`、`rejected`、`out-of-scope`、
`deferred`、`human-confirmation`）の語彙と意味は変更せず、reviewer の非拘束 finding を親が既存の裁定境界へ写像する。

### final trim の Resolution Transaction

final trim の各回は独立した Resolution Transaction とする。reviewer、goal、trim 回数は review-loop-owned とし、その時点の current
verified snapshot を各回の origin に固定する。trim finding を Resolution Batch に束ねて transaction を閉じ、promotion 後に次の
trim を行う場合は新しい snapshot を origin とする新しい transaction を開始する。Kernel は trim、over-engineering、count semantics
を所有せず、trim を通常 round や誘発判定の窓へ加算しない。

necessity-kernel v1 の mapping はこの batch mapping から独立して不変であり、相互の本文、identity、読み込み順、結果を成立条件に
しない。

## round と実行 Data

1 round は、`snapshot 固定 → review goal に基づくレビュー → 親の finding 裁定 → 採用修正 → verification`
である。verification は採用 finding が成果物へ反映されたことを確認し、成果物が実行可能な検証手段を
持つ場合はそれも含める。同じ snapshot に複数 reviewer を起動しても同じ round なら 1 round と数える。
`adversarial_review_count` は reviewer 起動回数ではなく、全 review round 数である。final trim は round 計数と
誘発判定の窓から除外する。誘発判定の対象は `plan-adversarial-reviewer` を起動した通常 round に限り、loop 全体で
計数する。
trim の finding も同じ指摘台帳へ記録し、発行元 reviewer で区別する。

finding ごとに `id`、発行元、対象 snapshot、evidence、影響する AC / risk、親の裁定、理由、`induced` と
`induced_by`（因果対応する採用修正と verification、非誘発時は null。通常 reviewer の判定対象だけ）を記録する。
全 round・全 reviewer 通算の指摘台帳を維持し、未解決 finding は裁定
未確定、`adopted` 修正の未反映、または `human-confirmation` とする。`deferred` は凍結済みの完了した裁定なので未解決に
含めない。

## 親の裁定

親は各 finding を次の5値の一つへ裁定し、evidence と理由を記録する。

1. **`adopted`** — 成果物を修正して verification する。
2. **`rejected`** — 既存仕様または evidence に基づき修正しない。
3. **`out-of-scope`** — 成立性は否定しないが対象外として残存事項へ渡す。
4. **`deferred`** — 仕様未決、記載漏れ、誤認、対象外、情報不足のいずれかを確定できないため凍結する。
5. **`human-confirmation`** — 実装・公開・互換性など、親だけでは決められない確認を要求する。

裁定区分と別に、通常の `plan-adversarial-reviewer` finding の影響度を `軽微`、`修正推奨`、`修正必須`
のいずれかへ親が確定する。final trim の finding には影響度を要求しない。reviewer の severity や Pass を
親の `accept` へ直結しない。

### `deferred` の凍結

`deferred` は loop 中に次の規則で凍結する。

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


### 誘発指摘による補助ブレーキ

`plan-adversarial-reviewer` を起動した各通常 round について、全体の finding ledger を通じて `induced` を観測する。
`induced: true` は、直前までに親が採用して verification を完了した修正によって finding が新たに成立したという
因果 evidence がある場合だけ付ける。対象文の新旧、snapshot 差分、同じ指摘の再出現だけでは `induced: true` に
しない。因果 evidence がなければ `induced: false` とし、採用した修正との対応を ledger に残す。

旧基準状態を成立条件や窓の開始位置として保存・参照せず、各通常 round の観測から判定する。

各通常 round で、親確定の `修正推奨` 以上だけを対象に、誘発 finding の数が非誘発 finding の数を上回るかを
`induced_dominant` として記録する（母数が空の round は成立しない）。同じ判定を直近の `plan-adversarial-reviewer`
通常 round 2 回で連続して満たし、両 round とも非誘発の `修正必須` が 0 の場合だけ、`induced-loop` を補助的な
早期打ち切りとして選べる。ちょうど半数は支配的とみなさない。1 round だけの成立では打ち切らない。final trim
や同じ round の他 reviewer の finding は判定対象に入れない。

`induced-loop` は自己誘発 churn に対する補助ブレーキであり、`converged` / `round-limit` の定義や必要な親裁定を
置き換えない。打ち切り round の採用 finding は反映し、全 finding の裁定と因果 evidence を記録して裁定未記録を
残さない。


## final trim

accept-candidate（`converged` または `induced-loop`）で未解決 finding が空の場合だけ、適用対象のプラン系
成果物へ final trim を行う。非適用成果物は trim を省略した事実と理由を出力する。trim は通常 loop へ戻らず、
各回を新しい snapshot へ順に適用する。削減後の verification が失敗した場合は、新しい設計を足さず、該当
削減 finding の裁定を原則 `adopted` から `rejected` へ戻す。`human-confirmation` が必要な trim finding は `out-of-scope` として渡す。
trim の finding もその場で5値へ裁定し、未解決一覧と残存事項へ反映する。規定3回なら全体構造、レビュー誘発要素、
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
- `induced-loop`: 自己誘発 churn の補助ブレーキで打ち切った。未解決がなければ trim、残れば trim なしで返す。
- `round-limit`: 上限到達時に未解決が残り、trim なしで返す。
- `stop-incomplete`: 安全に継続・裁定完了できず、未解決を残して早期終了する。trim なしで返す。

成果物の status 確定、入力 resource への書き戻し、成果物の受け入れ、次工程の判断は呼び出し元の親が行う。
この Skill は工程を前進させず、仕様を補完せず、入力 resource を無断更新しない。
