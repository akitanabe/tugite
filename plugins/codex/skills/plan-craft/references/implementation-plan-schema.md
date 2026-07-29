<!-- Generated from shared/. Do not edit directly. -->

# Implementation Plan 正規スキーマ

`plan-craft` Skill の出力であり、`branch-design` への入力にできる
Implementation Plan の正規スキーマ（正本）を定義する。確定済み Implementation Plan を
`branch-design` へ渡せるが、受け渡しは親エージェントの責務であり、この Skill は
次工程を開始しない。

## 目次

- 設計方針
- スキーマ本体
- blocking violation code
- 状態遷移と権限
- branch-design への引き渡し

## 設計方針

- 実装枝・git branch・Branch Plan の用語の書き分けは正本
  [実装枝の準備と委譲](../../impl-lead/references/implementation-branches.md)の
  「用語」節に従う。`impl-lead` と `branch-design` が共有する語彙を
  この Skill でも複製せずそのまま使う。
- Implementation Plan は実装枝への分割を持たない。分割は `branch-design` の責務で
  あり、`plan.steps` は起草者が実装の道筋を示す順序付き作業であって、AC を所有しない。
- `plan.design` は決めた規約の本体を1箇所に置く正本とする。`plan.approach` は `design` の規約を
  対象 repository の現状へ当てはめる方針、`plan.steps` は `design` を実現する作業、
  `acceptance_criteria` は `design` の充足を判定する観測点であり、いずれも規約本文自体を
  保持しない。
- 1つの設計判断を複数の field へ別々の言い回しで写すと、レビューは写しの不一致の同期に
  費やされる。`design` を正本に置くのはこの写しを無くすためであり、`plan.approach` を
  設計文書に据える案と別 artifact に分離する案は棄却した。`approach` は `design` の要約ではなく、
  `design` が答えない「どこへ・既存構造のどれを使うか」を担当する。要約にすると `design` と
  変更理由を共有し、写しが要約の粒度で残るためである。
- AC は安定 ID を持ち、Branch Plan の `acceptance_criteria` へそのまま引き継げる形（観測可能な
  振る舞いの原文）で保持する。ID は round の増減やプラン修正で振り直さない。
- レビューの経過は `review.findings` に全 round・全 reviewer 通算の指摘台帳として持つ。指摘 ID
  （`PF-*`）は round をまたいで振り直さず、`reviewer` field で発行元を区別する。verdict は親が
  確認した確定値だけを記録し、reviewer の自己申告をそのまま書かない。
- `validation.blocking` は安定した code を持つ violation の配列とし、承認可否は blocking violation
  の有無だけで決まる。自己評価 boolean は持たない。
- 承認（`approval`）は Implementation Plan の確定だけを意味し、枝分割・委譲の開始権限を含まない。
  次工程はユーザーの明示的な要求だけを根拠に親エージェントが開始する。

## スキーマ本体

```yaml
# ============================================================
# Implementation Plan 正規スキーマ (plan-craft の出力)
# ============================================================

status: blocked | awaiting_review | approved
# blocked:          open_questions または validation.blocking のいずれかが非空
# awaiting_review:  confirmation_mode: review で blocking なし。ユーザー承認待ち
# approved:         承認済み。open_questions と validation.blocking がすべて空であることが前提

confirmation_mode: review | auto
# すべての status で保持する。既定は review。auto はユーザーが明示した場合のみ。
# blocked の解消後にどちらへ遷移するかは、この値から復元する

approval:
  method: null | user | auto    # 未承認の間は null。auto は「Implementation Plan の承認」だけを
                                # 自動化した記録であり、次工程の開始権限を含まない。
                                # termination: round-limit で resolution: unresolved の指摘が残る
                                # 場合は、confirmation_mode: auto でも自動承認しない

plan:
  objective: <実装目的の1行要約>
  source: <要求の所在。「会話内」/ path>
  design: <決めた規約の本体。設計判断の正本>
                                # 書くのは決めたことだけで、要求の再掲や背景の説明は含めない。
                                # 分量はそのプランで実際に決めた事項の数に従い、決めた事項が少なければ短くてよい
  approach: <design の規約を対象 repository の現状へ当てはめる方針>
                                # どこへ・既存構造のどれを使うかを書く。
                                # design が答えた規約そのものは書かない
  steps: []                     # 順序付きの作業。実装枝への分割はしない。AC を所有しない。
                                # 規約本文は持たず、plan.design を正本として参照する

acceptance_criteria:
  - id: AC-1                    # 安定 ID。Branch Plan へそのまま引き継ぎ可能。振り直さない
    text: <観測可能な振る舞い>   # 規約本文の正本は plan.design。
                                # AC はその充足を判定する観測可能な振る舞いだけを書く

scope:
  allowed_paths: []             # 変更を許可する物理的なファイル範囲
  forbidden_paths: []           # 変更を禁止する物理的なファイル範囲
  out_of_scope: []              # 許可範囲内でも扱わない責務・作業

dependencies: []                # 既知の依存（外部サービス、他タスク、順序制約）
constraints: []                 # ユーザーが明示した制約の原文

open_questions:                 # blocking のみ。1件でもあれば status: blocked
  - question: <確定が必要な問い>
    affects: []                 # 影響するスキーマ上の path または AC id

assumptions:                    # minor のみ。AC 充足・scope・実行可否に影響しない仮定
  - topic: <対象>
    assumption: <置いた仮定>
    rationale: <この仮定が blocking でない理由>

review:
  rounds_limit: 10              # 既定10。ユーザー明示時のみ変更
  rounds_completed: 0
  termination: null | zero-findings | trivial-only | round-limit
  findings:                     # 全 round・全 reviewer 通算の指摘台帳
    - id: PF-1                  # 安定 ID。round をまたいで振り直さない
      round: 1
      reviewer: plan-adversarial-reviewer | over-engineering-reviewer
      verdict: 軽微 | 修正推奨 | 修正必須    # 親が確認した確定値
      summary: <指摘の要約>
      resolution: adopted | rejected | unresolved   # unresolved は round-limit 時のみ
      resolution_note: <採用内容または不採用理由>

validation:
  blocking: []                  # violation の配列。1件でもあれば status: blocked
  # - code: <violation code 表の安定 code>
  #   path: <問題があるスキーマ上の path。例: review.findings[2].resolution>
  #   message: <修正に必要な説明>
```

## blocking violation code

親エージェントは reviewer と自身の申告を信用せず、入力 Data から再計算する。

| code | 検査内容 |
| --- | --- |
| `duplicate-id` | AC / finding の id 重複 |
| `unknown-reference` | 存在しない AC id / finding id への参照（`open_questions[].affects` の AC id を含む） |
| `vocabulary-invalid` | `verdict` / `resolution` / `termination` / `reviewer` が定義済み語彙にない値 |
| `state-invalid` | `status` と他フィールドの矛盾（`approved` なのに `open_questions` が非空、`awaiting_review` なのに `approval.method` が非 null など）。有効な組み合わせ表から再計算する |
| `scope-conflict` | `scope.allowed_paths` / `scope.forbidden_paths` の矛盾 |
| `review-incomplete` | `termination` が null のまま、または過剰実装審査（`reviewer: over-engineering-reviewer` の round）未実行のまま `awaiting_review` 以降へ遷移している |
| `resolution-missing` | `resolution` が未記録の finding、または `resolution: unresolved` が `termination: round-limit` 以外で残っている |
| `rounds-invalid` | `rounds_completed` が `rounds_limit` を超えている、または `findings[].round` と矛盾する |
| `design-missing` | `plan.design` が未記載または空のまま `awaiting_review` 以降へ遷移している |
| `handoff-incomplete` | 引き渡し必須 field（`plan.objective` / `plan.source` / `acceptance_criteria` / `scope`）の欠落 |

この表は、入力 Data から再計算できる検査だけで成り立つ。`approach` / `steps` /
`acceptance_criteria` が `design` の規約本文を再掲しているかは意味判断であり、Data から
再計算できない。表へ入れると表全体の再計算可能性が壊れるため、再掲の有無は code にしない。
再掲の抑止は起草手順とレビューの判定が担う。

トップレベル状態は値を個別に検査せず、次の有効な組み合わせ表から検査する。表にない組み合わせは
`state-invalid` を生成する。

| status | approval.method | confirmation_mode |
| --- | --- | --- |
| `blocked` | `null` | `review` / `auto` |
| `awaiting_review` | `null` | `review` のみ |
| `approved` | `user` | `review` のみ |
| `approved` | `auto` | `auto` のみ |

## 状態遷移と権限

| 遷移 | 実行主体 | 条件 |
| --- | --- | --- |
| (生成) → `blocked` | planning Skill | `open_questions` または `validation.blocking` が非空 |
| (生成) → `awaiting_review` | planning Skill | `confirmation_mode: review` かつ blocking なし |
| (生成) → `approved` (`method: auto`) | planning Skill | `confirmation_mode: auto` かつ blocking なし、かつ `resolution: unresolved` の指摘なし |
| `blocked` → `awaiting_review` | planning Skill（再実行） | 原因解消後に全 validation を再実行して blocking なし、`confirmation_mode: review` |
| `blocked` → `approved` (`method: auto`) | planning Skill（再実行） | 同上、`confirmation_mode: auto`、かつ `resolution: unresolved` の指摘なし |
| `awaiting_review` → `approved` (`method: user`) | 親エージェント | ユーザーの承認操作。blocking violation が残る場合は承認操作があっても遷移しない |

承認と次工程の開始は独立している。`awaiting_review` から承認された場合も、枝分割・委譲の要求が
なければプランの確定だけで停止する。確認モードの既定値は `review` とし、`auto` はユーザーが明示した
場合のみ使う。

## branch-design への引き渡し

確定した Implementation Plan は、`branch-design` の「入力の確認」が求める項目へ次の
とおり対応する。受け渡しは親エージェントの責務であり、この Skill は `branch-design`
を起動しない。`branch-design` 側の入力要件は変更しない。

| branch-design の入力 | Implementation Plan の field |
| --- | --- |
| 実装目的 | `plan.objective` |
| 元プラン | `plan.source`（この Data 自体を渡す場合は本 Data の所在） |
| Acceptance Criteria（原文） | `acceptance_criteria[].text`（ID ごと原文のまま） |
| 変更可能範囲と変更禁止範囲 | `scope.allowed_paths` / `scope.forbidden_paths` |
| 既知の依存 | `dependencies` |

`handoff-incomplete` は、この表の左列を充足できない field 欠落を検査する。

`plan.design` はこの表へ足さない。左列は `branch-design` の入力要件そのものであり、行を足す
ことは入力要件の変更になる。加えて、足すと `handoff-incomplete` と `design-missing` の検査
対象が二重になり、1つの欠落に2つの code が立つ。
