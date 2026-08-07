<!-- @only claude -->
---
name: proposal
description: >-
  plan-craft の同じ親 context 内だけで、要求と repository の観測から計画 candidate を起草し、
  read-only advisor の非拘束な insight を裁定して candidate snapshot または stop-incomplete を返す internal skill。
user-invocable: false
---
<!-- @/only -->
<!-- @only codex -->
---
name: proposal
description: >-
  plan-craft の同じ親 context 内だけで、要求と repository の観測から計画 candidate を起草し、
  read-only advisor の非拘束な insight を裁定して candidate snapshot または stop-incomplete を返す internal skill。
---
<!-- @/only -->

# proposal

## 位置づけと発火

この Skill は `plan-craft` の同じ親 context 内だけで使う internal skill であり、ユーザーから直接起動しない。
要求、repository、既存仕様を観測して計画 candidate を作る前段を担う。自身は実装、委譲、worktree 操作、
保存、最終受入を行わない。

## 入力と観測

親から次の Data を受け取る。

- `request`: 要求原文、目的、成功条件、scope、exclude、制約、既知の依存。
- `repository_observation`: current state、既存仕様、関連成果物、検証可能な境界。
- `caller_context`: `plan-craft` が同じ context で保持する判断と、必要なら既存の candidate snapshot。

要求、対象、成功条件、scope、exclude、依存、制約の不足または矛盾が品質を変える場合は推測せず、
`stop-incomplete` として必要な判断を返す。軽微な不足は根拠付き `assumptions` として分離する。

<!-- @contract proposal-boundary -->
## candidate の起草と advisor insight

planner は一次情報（要求原文、repository、既存仕様）を調査し、観測可能な AC、設計、scope、依存、制約、
verification、残存 risk を含む candidate を起草する。candidate は同じ内容を識別できる `candidate snapshot`
として保持する。

必要な場合だけ proposal の planner は read-only `plan-quality-advisor` に candidate snapshot と判定基準を渡す。
advisor の返す insight は非拘束の Data であり、planner は各 insight を一次情報と要求に照らして次の台帳へ裁定する。

この Skill は `review-loop` を起動しない。

- `adopted`: 根拠があり、candidate の具体的な品質向上になるため採用した insight。
- `rejected`: 一次情報に反する、既存の制約で不要、または scope 外のため採用しない insight。
- `unresolved`: 根拠または人間の判断が不足し、採否を決められない insight。

advisor insight を自動採用せず、採否を根拠なしに planner の推測で埋めない。新仕様、新しい scope、AC、
ユーザー嗜好を advisor から派生させない。

## bounded な改善と返却

candidate の改善は、要求と一次情報から具体的な品質向上が残る間だけ bounded に行う。改善のたびに snapshot
を更新し、採否台帳と残存 risk を保つ。判断密度が高まり scope や責務が変わる場合、または人間の選択が必要な
`unresolved` が残る場合は、勝手に進めず判断点・evidence・必要な問いを付けて `stop-incomplete` を返す。

改善を終えた通常の返却は、`candidate_snapshot`、`adoption_ledger`（`adopted` / `rejected` /
`unresolved`）、`assumptions`、`blocking_gaps`、`residual_risks`、`status` を持つ Data である。安全な
candidate を作れない返却では `status: stop-incomplete` と未完了範囲、必要な判断、evidence、未検証事項を返す。
いずれも後段の起動や受け入れを主張せず、caller へ返して終了する。
<!-- @/contract -->
