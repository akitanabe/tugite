---
name: feature-lead
description: >-
  ユーザー要求から実装完了までを、`plan-craft` / `branch-design` / `impl-lead` の3段を
  順に連結して一括で進める orchestration skill。プランから実装までの一括実行を明示的に
  要求されたときに使う。各段の判断基準は再定義せず、段の遷移と判断点の処理だけを担う。
  既定では段が `blocked` を返した時点で停止し、`unattended` の明示時だけ自律解決して進む。
---
<!-- Generated from shared/. Do not edit directly. -->

# 要求から実装までの一括進行

ユーザー要求を `plan-craft` → `branch-design` → `impl-lead` の順に通し、実装完了までを
一括で進める。この Skill が担うのは段の連結と判断点の処理だけであり、プランの起草、枝分割、
実装と QA の中身はすべて各段の Skill が担う。

## この Skill の責務

- 出力は最終的に `impl-lead` の最終報告である。この Skill 自身はプラン、枝、diff を作らない。
- 各段の判断基準を再定義しない。AC の書き方、枝分割の基準、枝 mode の導出、QA の受け入れ判断は
  すべて各段の Skill の正本に従う。この Skill に判断表を複製しない。
- 判断点の扱いは `autonomy` に従う。既定の `attended` では、段が `blocked` を返した判断点を
  ユーザーへ返して確定を求める。`unattended` ではこの Skill が自律解決して進める。どちらの場合も
  判断点を黙って消さず、判断点台帳へ記録する。
- 段を飛ばさない。`branch-design` を省いて Implementation Plan を直接 `impl-lead` へ渡さない。

## 発火条件

- ユーザーがプラン作成から実装までの一括実行を明示的に要求したとき。

次の場合は発火しない。

- 単一の段だけの要求。プランのみは `plan-craft`、枝分割計画のみは `branch-design`、
  確定済み Branch Plan からの実装委譲のみは `impl-lead` の責務である。
- `direct` の明示時。委譲を伴わない経路であり、この Skill の対象外である。
- テストスイートの棚卸し要求（`test-audit` の責務）。

## 入力の確認

着手前に次を確認する。不足が blocking なら補完せず、`plan-craft` の `open_questions` として
扱わせる。

- 要求原文。言い換えず、`plan-craft` へそのまま渡す。
- 対象 repository と読み取り可能な現状。
- 既知の制約・依存。
- `autonomy` の明示指定。既定は `attended` とし、ユーザーが全面委任を明示した場合だけ
  `unattended` を選ぶ。タスク規模、段の停止回数、進行の停滞を理由にこの Skill 側で
  `unattended` へ切り替えない。
- mode 指定（`lite` / `standard(-adaptive)` / `strict(-adaptive)` / `strict-full`）。
  未指定の場合はこの Skill で補わず、`impl-lead` の既定（`adaptive` / `standard`）に委ねる。
- `rounds_limit` の明示指定。`plan-craft` へそのまま渡す。

## 全体の流れ

1. 上の入力を確認する。
2. `plan-craft` を `confirmation_mode: auto` で起動し、Implementation Plan Data を得る。
3. 「段の遷移と判断点の処理」に従い status を判定する。判断点があれば `autonomy` に従って処理する。
4. 確定した Implementation Plan を `branch-design` へ `confirmation_mode: auto` で渡し、
   Branch Plan Data を得る。
5. 「段の遷移と判断点の処理」に従い status を判定する。判断点があれば `autonomy` に従って処理する。
6. 「授権の根拠」に従い `delegation` を設定する。
7. Branch Plan と判断点台帳を `impl-lead` へ渡す。`impl-lead` は受け入れ口の再検証を通常どおり行う。
8. `impl-lead` の最終報告を提示する。段ごとの要約を先に置き、最終報告を末尾に置く。
   `unattended` では判断点台帳の全件を会話上の最終報告にも含める。

## 段の遷移と判断点の処理

各段は `confirmation_mode: auto` で起動する。この Skill の起動要求そのものが `auto` の明示指定に
相当する。`auto` は各段の承認だけを自動化するもので、判断点の自動解決ではない。判断点の扱いを
決めるのは `autonomy` であり、`confirmation_mode` と混同しない。

次のいずれかを判断点として検出する。

- `plan-craft` が `status: blocked` を返した（`open_questions` または `validation.blocking` が
  非空）。
- `plan-craft` が `termination: round-limit` で `resolution: unresolved` の指摘を残した。
- `branch-design` が `status: blocked` を返した（`unresolved_decisions` または
  `validation.blocking` が非空）。
- `impl-lead` が各 mode のゲートで停止した。停止条件は `impl-lead` の契約に従う。

### `attended`（既定）

判断点を検出した段で停止する。どの段のどの判断点で止まったかを明示してユーザーへ返す。ユーザーが
判断点を確定した後は停止した段から再開し、それより前の段の出力は破棄しない。

### `unattended`

停止せず、「自律解決の規律」に従って判断点を解決してから次段へ進む。解決は判断点の記録を伴い、
記録できない解決は行わない。

## 自律解決の規律

`unattended` の自律解決は次に従う。ユーザーへ判断を返さないことと、判断の根拠を持たないことは
別である。

- 根拠は要求原文と repository の観測可能な事実（既存 code、テスト、規約、設定）から取る。
  根拠を取れる場合は `basis_kind: observed` として記録する。
- 根拠を取れない判断点も停止せずに解決するが、`basis_kind: assumed` として仮定であることを
  記録する。仮定を観測事実として記録しない。
- 要求原文の scope を広げる方向で解決しない。判断点を解くために機能、対象範囲、成果物を足さない。
  scope に関する判断点は、要求原文が支持する最小の解釈を採る。
- 段の判断基準そのものを緩めて解決しない。AC を落とす、必須テストを省く、枝 mode を下げる、
  blocking violation を無視するといった手段で判断点を消さない。判断基準を満たす解を選ぶ。
- 複数の解が規律を満たす場合は、後から戻しやすい方を選ぶ。

不可逆な操作（外部への公開・送信、tracked file の削除、履歴の書き換え、外部状態の変更）は
`unattended` でも自律解決の手段に含めない。当該操作を伴わずに到達できる範囲まで進め、操作が
必要だった事実を判断点として台帳へ記録し、未実施のままユーザーへ返す。実行の可否は判断点ではなく
実行時の承認事項であり、`unattended` の授権はこれを含まない。

## 判断点台帳

判断点は検出時に台帳へ記録し、会話上の最終報告へ全件を記載する。台帳は `impl-lead` へも渡し、
[永続 QA レポート](../impl-lead/references/qa-report.md) を生成する場合は同じ台帳をその記録項目の
入力にする。

| field | 値 |
| --- | --- |
| `stage` | `plan-craft` / `branch-design` / `impl-lead` |
| `point` | 判断点。原文を言い換えずに保持する |
| `origin` | `open_questions` / `unresolved_decisions` / `validation.blocking` / `round-limit` / `impl-lead-gate` |
| `resolution` | 確定した内容 |
| `basis` | 根拠 |
| `basis_kind` | `observed` / `assumed` |
| `resolved_by` | `user`（`attended` での確定） / `autonomous`（`unattended` での自律解決） |

台帳の記載は `attended` / `unattended` の双方で必須とする。`unattended` では判断点をユーザーへ
返さないため、この記載が唯一の検分経路になる。記載できない判断点は解決したとみなさない。

`basis_kind: assumed` の項目は台帳内で区別して示し、観測事実に基づく解決と混ぜない。仮定の総数を
最終報告の冒頭要約にも出す。

## 授権の根拠

`branch-design` は `delegation.authorized: false` を返す。この Skill は親エージェントの役割で
`delegation.authorized: true` / `authorized_by: user` を設定する。根拠はこの Skill の起動要求
そのものであり、要求は plan から実装委譲までを含むものとして扱う。

段ごとの委譲要求の再取得は求めない。ただし `impl-lead` の受け入れ口が行う5項目の再検証は省略しない。
授権を設定するのは、`branch-design` が `status: approved` を返した場合だけである。

<!--
Why Not: この Skill が各段の判断表（枝 mode の決定表、blocking violation code、QA 基準）を
持たない理由。判断表を複製すると正本が二重化し、片方だけ改訂されたときに一括経路と単段経路で
挙動が食い違う。この Skill は遷移だけを持ち、判断は各段の正本へ委ねる。

Why Not: `unattended` を `confirmation_mode: auto` へ統合しない理由。`auto` は各段が自分の
出力を承認する範囲の自動化であり、判断点が残る場合は `auto` でも `blocked` を返す契約になって
いる。両者を同じ語彙にすると、段の承認自動化を求めただけの利用者が判断点の自律解決まで
受け取ることになる。
-->
