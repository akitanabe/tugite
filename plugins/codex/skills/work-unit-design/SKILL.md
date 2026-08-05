---
name: work-unit-design
description: >-
  plan-craft または impl-lead の同じ親 context 内だけで使う internal Work Unit 設計手順。
---
<!-- Generated from shared/. Do not edit directly. -->

# work-unit-design

## 位置づけと発火

この Skill は新しい worker を起動するものではなく、呼び出し元の親が同じ context で従う判断手順書である。
ユーザーの直接要求や通常会話から暗黙に設計を始めず、Work Unit の候補が必要な `plan-craft` の工程、または
実装単位の境界・依存・分割が非自明な `impl-lead` の工程としてだけ使う。Work Unit の設計を求める入口は
plan-craft、実装の入口は impl-lead であり、この Skill 自身は実装・委譲・後続工程を開始しない。

Codex runtime で Skill 間起動が提供されない場合、親はこの本文を工程として直接参照する。発火条件、入力、
候補の裁定、blocking の扱い、採用・実行・保存を親が持つという責務は変えない。

## 入力と出力

親から、次の入力 Data を受け取る。

- `request`: 要求原文、AC の素材、constraints、既知の依存。
- `caller_observation`: repository の現状、既存 plan・調査、再正規化なら既存 Work Unit 集合、accepted 状況、worker 返却。

親が要求、対象、成功条件、scope、exclude、依存、制約、current state を観測できていない場合は推測せず、
不足を `blocking_gaps` に返す。

出力は会話内 execution data の候補であり、`work_units`、各単位の分割／統合 signal と理由・残存判断密度等の観測、
`blocking_gaps`（blocking不足一覧）で構成する。
各 `work_units` 要素は、次の fields を自己完結に持つ。

- `id`
- `purpose`
- `acceptance_criteria`
- `scope`: `change` と `exclude`
- `implementation_freedom`
- `constraints`
- `depends_on`: Work Unit ID 依存と、外部・repository・environment の precondition を別々に記録する。
- `verification`

`acceptance_criteria` は候補単位が満たすべき観測可能な条件であり、accept の確定ではない。`worker`、
`base_snapshot`、`isolation`、route、order、実行結果、review、保存先、後続 Skill の起動権限を出力へ含めない。
候補の採用、再検査、accept／stop-incomplete、委譲、実行、保存は必ず受け取り側の親が判断する。

## 判断の進め方

1. 要求と caller observation を照合し、対象、責任境界、依存、検証可能な成果を抽出する。既存 Work Unit がある場合は
   accepted 状況、部分成果、worker の返却を現在の観測として扱う。
2. 各候補について「新しい Implementer がこの単位だけを読み、AC・責任境界・依存・分割を再定義せず、受け入れ候補の
   diff を返せるか」を判定する。否定ならその不足と影響を `blocking_gaps` に記録する。
3. 独立した目的、検証、rollback 境界がある候補を分け、共通依存は独立価値がある場合だけ単独化する。それ以外は最初に
   振る舞い価値を生む単位が所有し、後続は accepted 基準に依存させる。
4. 同じ検証でしか成立しない候補、片方だけでは invariant が成立しない候補、または handoff が内部結合より複雑な候補を
   統合する。再正規化では統合、追加分割、部分成果の独立した再構成、依存 edge の再接続を候補として示す。
5. 受け取り側の親が安全に設計を採用できない不足・矛盾・閉じていない scope を列挙し、影響と追加観測を添えて返す。安全な
   設計不能の差し戻し、fresh context での再委譲、再配車、stop-incomplete の確定は親の責務である。

## 分割を検討する signal

分割 signal は次の 7 項目であり、分割の根拠として個別に観測し、該当理由を候補に添える。

1. 独立した accept 目的が複数ある。
2. 先行単位の学習結果で後続の設計が変わる。
3. 複数の外部副作用、または異なる rollback 境界がある。
4. 検証方法または受入判断が異なる。
5. 旧仕様との parity と新規挙動が混在する。
6. Implementer が AC、責任境界、依存を再設計しないと着手できない。
7. 残す設計・推論判断が多すぎ、単位だけを読んでも受け入れ候補 diff を返せない。

## 過分割を示す signal

過分割 signal は次の 5 項目であり、該当すれば候補を統合する。

1. 同じ test でしか Green／invariant を確認できない。
2. 一方だけでは Green にならない、または invariant が成立しない。
3. 一方だけで accept／revert できない。
4. architecture layer の名前だけで横割りしている。
5. unit 間 handoff が統合内部の結合より複雑である。

単位化の非根拠は二つの軸に分けて記録する。

- 構造・工程の軸: file 数、行数、architecture layer、実装工程だけでは単位を決めない。
- 規模・接続の軸: file 数、行数、枝数、database を触るかどうかだけでは分割しない。

layer 固有の要求が独立検証できる場合だけ、結果として 1 unit を認める。判断密度、責任境界、観測可能な価値、依存、rollback、
検証を根拠にする。

## 親への返却境界

この Skill は候補と観測を返して終了する。直接起動を促さず、正しい入口を案内して終了する。ユーザーの通常要求を設計へ変換しない。候補を採用したか、
親が再検査したか、実装・委譲・worker 起動を実行したか、AC を確定したか、結果を保存したかを主張しない。不足が解消されない場合は
不足、影響、残存 risk、必要な観測を `blocking_gaps` に残し、親が確認または stop-incomplete を選べるようにする。
