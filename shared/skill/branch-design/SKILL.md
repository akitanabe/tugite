<!-- claude-only:start -->
---
name: branch-design
description: >-
  実装プランを、委譲可能な実装枝へ正規化した Branch Plan Data へ変換する planning skill。
  ユーザーが枝分割計画を明示的に要求したとき、または委譲予定のタスクが分割シグナルに
  該当するときに使う。実装や委譲は行わず、`impl-lead` を直接起動しない。
  Branch Plan Data を返すだけで、委譲開始権限は含まない。
  ユーザーからプランから実装までの一括実行を直接要求された場合、および確定済みの
  Implementation Plan を渡して実装までの一括実行を直接要求された場合は、`feature-lead` の
  責務であり発火しない。`feature-lead` の段として起動された場合はこの条件の対象外であり、
  通常どおり動作する。
---
<!-- claude-only:end -->
<!-- codex-only:start -->
---
name: branch-design
description: >-
  実装プランを、委譲可能な実装枝へ正規化した Branch Plan Data へ変換する planning skill。
  ユーザーが枝分割計画を明示的に要求したとき、または委譲予定のタスクが分割シグナルに
  該当するときに使う。実装や委譲は行わず、`impl-lead` を直接起動しない。
  Branch Plan Data を返すだけで、委譲開始権限は含まない。
  ユーザーからプランから実装までの一括実行を直接要求された場合、および確定済みの
  Implementation Plan を渡して実装までの一括実行を直接要求された場合は、`feature-lead` の
  責務であり発火しない。`feature-lead` の段として起動された場合はこの条件の対象外であり、
  通常どおり動作する。
---
<!-- codex-only:end -->

# 実装枝計画の正規化

実装プランを、委譲可能な実装枝へ正規化した Branch Plan Data へ変換する。この Skill は計画の
正規化だけを担い、実装も委譲も行わない。確定済み Branch Plan は `impl-lead` へ
渡せるが、受け渡しは親エージェントの責務であり、この Skill は `impl-lead` を
直接起動しない。

## この Skill の責務

- 出力は Branch Plan Data だけである。実装、テスト作成、worktree 準備、Worker 起動は行わない。
- 承認と委譲開始権限は独立している。この Skill が扱うのは Branch Plan の確定までであり、
  `delegation.authorized` は常に `false` で返す。委譲開始権限はユーザーの明示的な委譲要求だけを
  根拠に、親エージェントが後から設定する。
- 元プランの不足を勝手に補完しない。枝構造・実行順序・AC 割り当てに影響する blocking な不足は
  `unresolved_decisions` として確定を求め、影響しない minor な不足は `assumptions` に明示する。

## 発火条件

- ユーザーが枝分割計画を明示的に要求したとき。
- 委譲予定のタスクが分割シグナル([枝分割判断](references/branch-splitting.md))に該当するとき。

委譲要求がなくても、計画のみの作成が可能である。分割シグナルの詳細と統合条件は
[枝分割判断](references/branch-splitting.md) を参照する。

ただし、ユーザーからプランから実装までの一括実行を直接要求された場合、および確定済みの
Implementation Plan を渡して実装までの一括実行を直接要求された場合は、`feature-lead` の
責務であり発火しない。`feature-lead` の段として起動された場合はこの条件の対象外であり、
通常どおり動作する。

## 入力の確認

着手前に次を確認する。不足が blocking なら補完せず `unresolved_decisions` にする。

- 実装目的。
- 元プラン(path / issue URL / 会話内 / `test-audit` の Test Inventory 報告の findings)。
- Acceptance Criteria(原文。言い換えない)。findings 由来の AC では、原文はユーザーが確定した
  文言を指す。
- 変更可能範囲と変更禁止範囲。
- 既知の依存。
- 確認モードの既定は `review` とし、`auto` はユーザーが明示した場合のみ使う。

### findings を元プランにする場合

- 対象 findings の ID(`G-*`)をユーザーが明示的に指定する。全 findings の自動採用はしない。
  対象 ID の指定がないまま findings 全体を渡された場合は、自動採用せず対象 ID の明示指定を求める。
- 導出は `suggestion` を受け入れ条件の形に整えることに限る。findings にない対象・範囲・実装方針を
  足さない。

導出した AC の提示と確定の手順は [ユーザー確認](references/plan-review.md)、`derived_from` と
`kind: ac-derivation` の意味と検査規則は
[Branch Plan 正規スキーマ](references/branch-plan-schema.md) に従う。

## 全体の流れ

1. 上の入力を確認する。
2. 各 AC に安定 ID を付与する。枝の増減で振り直さない。原文をそのまま保持する。findings 由来の AC は
   [ユーザー確認](references/plan-review.md) に従って文言の確定を得る。
3. [枝分割判断](references/branch-splitting.md) に従い、外部から観測可能な振る舞いの縦割りで
   実装枝へ分ける。分割しない場合は `decision.split: false` と理由を記録する。
4. [Branch Plan 正規スキーマ](references/branch-plan-schema.md) に従い Branch Plan を生成する。
   AC 割り当ては枝側の一方向参照だけにする。
5. blocking violation code 表を入力 Data から再計算し、`validation.blocking` を確定する。
6. `unresolved_decisions` と `validation.blocking` から `status` を決める。いずれかが非空なら
   `blocked`。空で `confirmation_mode: review` なら `awaiting_review`、`auto` なら
   `approved`(`method: auto`)。
7. [ユーザー確認](references/plan-review.md) に従い、要約表と Branch Plan を提示する。

## 承認と委譲開始の分離

承認は Branch Plan の確定だけを意味する。`confirmation_mode: auto` は Branch Plan の承認だけを
自動化した記録であり、委譲開始権限を含まない。委譲開始には、ユーザーの明示的な委譲要求を
根拠に親エージェントが `delegation` を設定し、`status: approved` であることが別途必要になる。

この Skill は Branch Plan Data を返すだけで委譲を開始しない。委譲は、確定した Branch Plan を
親エージェントが `impl-lead` へ渡した後に、Executor 側で行う。
