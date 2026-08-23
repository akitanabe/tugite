<!-- Generated from shared/. Do not edit directly. -->

# Plan artifact design

Plan artifact design reference identity: `plan-artifact-design-v1`.

この reference は `plan-agent` / `plan-interactive` が生成する plan / design artifact の意味と情報構造を定める Practice である。
Kernel ではなく、各 public workflow が選択して load する shared reference として扱う。Programmatic Flow は持たない。

## 適用範囲

対象は `plan-agent` / `plan-interactive` が生成する plan / design artifact である。

次は適用しない。

- skill 全体への Principle 適用
- impl-lead の Implementation Unit
- `plan-artifact-publication` の保存・publication procedure
- 上位 Philosophy / Principle 本文

上位の Agent-facing Documentation Philosophy / Principle は、設計根拠として何があるかを示す外部正本である。通常の plan 実行では読まない。設計根拠の確認が必要なときにだけ https://github.com/akitanabe/agentic-design-philosophies/blob/main/philosophies/agent-facing-documentation.md を読む。

## Projection model

Design Summary と Detailed Plan は、同じ current verified planning state / decisions から同一 artifact 内の異なる semantic projection として導出する。両 projection は互いを意味 source にせず、source にない新しい設計判断を追加せず、意味を矛盾させない。

`plan-agent` は Agent-resolved planning decisions、`plan-interactive` は clarify-it 後の verified Human-confirmed constraints / decisions を source authority とする。direction freeze は downstream authority を保護する constraint Data であり、Design Summary、Detailed Plan、または planning candidate ではない。

stdout の short Summary は Design Summary 全文ではなく、artifact から stdout 用にさらに圧縮した projection である。既存の stdout field 集合を変更せず、stdout を Design Summary または Detailed Plan の代替にしない。

## Human-facing Summary

artifact 冒頭に Human-facing Summary を置く。Human-facing Summary は、Human の理解、design review、共有、design reuse のための Design Summary である。単語数による機械的な短縮ではなく、設計判断を単独で理解できる抽象度へ投影する。

原則として次を含める。

- Goal
- Approach
- Scope
- Verification

Risk / Attention は該当事項がある場合のみ含める。Goal / Approach / Scope / Verification は原則必須とする。Context、Exclude、主要な responsibility boundary、important planning decisions、重要な rejected alternatives と理由も、該当する場合に保持する。

file 単位の変更 step、test command の網羅、internal workflow history、review / adoption ledger、fine-grained Completion Criteria、Agent が実装時にだけ必要とする詳細 dependency explanation は、原則として Design Summary へ流入させない。

固定 schema や固定見出しは強制せず、保持する内容は current verified planning state / decisions に対する必要性から決める。

## Agent-facing Detail

Agent-facing Detail は、Agent が実装と verification に使う Detailed Plan である。該当する Acceptance Criteria、concrete design、dependency / constraint、implementation-oriented scope、verification、局所 Completion Criteria、assumption / unresolved question、residual risk を保持する。Design Summary は Detailed Plan を置換せず、Human readability のために Detailed Plan の情報を削らない。

Detailed Plan の情報を Design Summary へ重複させることでも解決せず、既存の Information placement に従って必要な最小の共通 scope に置く。固定 schema / 固定見出しは要求しない。

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
