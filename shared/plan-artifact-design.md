# Plan artifact design

Plan artifact design reference identity: `plan-artifact-design-v1`.

この reference は `plan-agent` / `plan-interactive` が生成する plan / design artifact の意味と情報構造を定める Practice である。
Kernel ではなく、各 public workflow が選択して load する shared reference として扱う。Programmatic Flow は持たない。

## 適用範囲

対象は `plan-agent` / `plan-interactive` が生成する plan / design artifact である。

次は適用しない。

- skill 全体への Principle 適用
- impl-lead の Work Unit
- `plan-artifact-publication` の保存・publication procedure
- 上位 Philosophy / Principle 本文

上位の Agent-facing Documentation Philosophy / Principle は、設計根拠として何があるかを示す外部正本である。通常の plan 実行では読まない。設計根拠の確認が必要なときにだけ https://github.com/akitanabe/agentic-design-philosophies/blob/main/philosophies/agent-facing-documentation.md を読む。

## Human-facing Summary

artifact 冒頭に Human-facing Summary を置く。

原則として次を含める。

- Goal
- Approach
- Scope
- Verification

Risk / Attention は該当事項がある場合のみ含める。Goal / Approach / Scope / Verification は原則必須とする。

Summary は本文からの Human 向け projection であり、独立した意味上の正本にしない。stdout の summary も artifact の projection として扱う。stdout の field 集合は既存契約のまま変更しない。

## Agent-facing Detail

本文は Agent が実行・verification に必要な詳細を保持する。固定 schema / 固定見出しは要求しない。

該当する場合は、scope / exclude、dependency、constraint、assumption、unresolved question、residual risk を含める。

`Work Unit` は汎用 plan artifact の基本構造に使わない。

## Verification / Completion Criteria の近接配置

実行または変更を要求する各項目の近くに、実行・変更内容、Verification、Completion Criteria を置く。

説明・背景・比較・判断整理だけの項目には Completion Criteria を要求しない。

## Acceptance Criteria / Verification / Completion Criteria の責務分離

- Acceptance Criteria は plan 全体の成功条件である。
- Verification は結果を確認する方法である。
- Completion Criteria は局所項目の終了条件である。

同じ意味を複数箇所へ言い換えて保持しない。

実行・変更・到達状態を計画する成果物は原則として Acceptance Criteria を持つ。純粋な比較検討・設計メモ・判断整理には全体 Acceptance Criteria を要求しない。

## Information placement

情報は、判断・実行に必要となる最小の共通 scope へ置く。

- 全体に効く情報は上位へ置く
- 項目固有の情報はその項目の近くへ置く
- 同じ全体制約を各項目へ複製しない
- 局所 detail を冒頭へ引き上げない

## Reference pointer

詳細を artifact 外へ委譲する場合、pointer は次を持つ。

- 何の情報があるか
- どの条件で参照すべきか
- どこにあるか

artifact 内で完結する場合は pointer 自体を要求しない。
