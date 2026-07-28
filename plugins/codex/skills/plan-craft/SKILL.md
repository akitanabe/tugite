---
name: plan-craft
description: >-
  ユーザー要求から実装プランを起草し、`plan-adversarial-reviewer` の敵対的レビューループと
  `over-engineering-reviewer` のプラン審査を経た Implementation Plan Data を返す planning skill。
  レビュー付きプラン作成の明示要求時に使う。実装・委譲・枝分割は行わず
  `branch-design` を直接起動しない。次工程の開始権限は含まない。
---
<!-- Generated from shared/. Do not edit directly. -->

# 実装プランの起草とレビュー

ユーザー要求から実装プランを起草し、敵対的レビューループと過剰実装審査を経た Implementation Plan
Data へ確定する。この Skill はプランの起草と確定までを担い、実装・委譲・枝分割は行わない。確定済み
Implementation Plan は `branch-design` へ渡せるが、受け渡しは親 Codex エージェントの責務で
あり、この Skill は `branch-design` を直接起動しない。

## この Skill の責務

- 出力は Implementation Plan Data だけである。実装、テスト作成、実装枝への分割、worktree 準備、
  Worker 起動は行わない。
- 承認と次工程の開始権限は独立している。この Skill が扱うのは Implementation Plan の確定までであり、
  枝分割・委譲の開始権限は含まない。次工程はユーザーの明示的な要求だけを根拠に、親 Codex エージェントが
  後から開始する。
- 要求の不足を勝手に補完しない。AC 充足・scope・実行可否に影響する blocking な不足は
  `open_questions` として確定を求め、影響しない minor な不足は `assumptions` に明示する。

## 発火条件

- ユーザーがレビュー付きの実装プラン作成を明示的に要求したとき。

次の場合は発火しない。

- 枝分割計画の要求（`branch-design` の責務）。
- 実装・委譲の要求（`impl-lead` の責務）。
- レビューを求めない相談・調査・回答だけの要求。

## 入力の確認

着手前に次を確認する。不足が blocking なら補完せず `open_questions` にする。

- 要求原文（言い換えずに保持する）。
- 対象 repository と読み取り可能な現状。
- 既知の制約・依存。
- `rounds_limit` の明示指定。`rounds_limit` の既定は 10 とし、ユーザーが明示した場合のみ変更する。
- 確認モードの既定は `review` とし、`auto` はユーザーが明示した場合のみ使う。

## 全体の流れ

1. 上の入力を確認する。
2. [起草手順](references/plan-drafting.md) に従い、安定 ID 付きで観測可能な振る舞いを表す AC、
   scope、dependencies、constraints を持つプランを起草する。
3. [Implementation Plan 正規スキーマ](references/implementation-plan-schema.md) に従い
   Implementation Plan Data を生成する。
4. [敵対的レビューループ](references/adversarial-review.md) に従い、`plan-adversarial-reviewer` に
   よる round を打ち切り条件が成立するまで繰り返す。
5. adversarial の収束後、[過剰実装のプラン審査](references/overengineering-plan-review.md) に従い
   `over-engineering-reviewer` をプラン入力モードで起動する。指摘採用でプランを修正した場合は
   手順4へ戻る。
6. blocking violation code 表を入力 Data から再計算し、`validation.blocking` を確定する。
7. `open_questions` と `validation.blocking` から `status` を決める。いずれかが非空なら `blocked`。
   空で `confirmation_mode: review` なら `awaiting_review`、`auto` なら `approved`（`method: auto`）。
   ただし `termination: round-limit` で `resolution: unresolved` の指摘が残る場合は、`auto` でも
   自動承認しない。
8. 未解決一覧（あれば）→ 指摘台帳の要約 → Implementation Plan の YAML 全文の順で提示する。

## レビューと権限境界

- reviewer は指摘 Data だけを返す。verdict の確定、採用・不採用の判断、プランへの反映は
  親 Codex エージェントが行い、reviewer の自己申告をそのまま採用しない。
- 承認は Implementation Plan の確定だけを意味する。枝分割は、確定した Implementation Plan を
  親 Codex エージェントが `branch-design` へ渡した後に、あちら側で行う。この Skill は
  `branch-design` を直接起動しない。
