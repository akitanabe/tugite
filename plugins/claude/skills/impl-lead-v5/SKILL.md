---
name: impl-lead-v5
description: >-
  明示起動時だけ、親が一つの目的と一つの Work Unit を正規化し、direct または一名の worker を選び、
  TDD と親 QA を経て accept または stop-incomplete で閉じる最小の v5 実装 loop。
disable-model-invocation: true
---
<!-- Generated from shared/. Do not edit directly. -->

# Active v5 main

この skill はユーザーが `$impl-lead-v5` を明示した場合だけ起動する。自然言語の作業内容、規模、現在の
context から暗黙に起動しない。起動後も、親が受け入れ判断と最終報告を保持する。

## Intake

親は実装を始める前に要求、対象 repository、現在の dirty state、基準状態を観測する。Issue または doc と
対象 file、その周辺、呼び出し元・先、関連 test を読み、次の Work Unit Data を一つだけ確定する。
ここでいう単一 purpose は一つの成果に閉じた目的であり、実行全体で単一 Work Unit（1 worker まで）を扱う。

- `purpose`: 単一の目的。
- `acceptance_criteria`: 外部から観測可能で検証可能な Acceptance Criteria。
- `scope` と `exclude`: 変更を許す範囲と変更しない範囲。
- `implementation_freedom`: worker に任せてよい局所判断。なければ空。
- `constraints`: ユーザー指定、互換性、依存、実行環境その他の制約。
- `depends_on`: 先に成立している必要がある入力または状態。
- `verification`: AC ごとの native test、focused test、必要な最終 gate。

不足、矛盾、または scope を閉じられない状態が品質に影響する場合、推測で補わず実装を開始しない。必要な
情報を親へ戻すか、理由・未完了範囲・evidence・残存 risk を含む `stop-incomplete` とする。要求と repository
の状態を観測せずに worker を起動しない。既存の dirty/untracked は scope に含めず、勝手に変更・削除しない。

Work Unit Data は目的、AC、scope、exclude、implementation_freedom、constraints、depends_on、verification だけを表す。worker、
base snapshot、選択理由、実行時の状態は別の execution data として親が保持し、Work Unit の意味を書き換えない。

## Route and execution data

ユーザーの direct または委譲の制約をそのまま execution constraint として扱う。制約が `direct` なら親が実装
し、委譲が指定されたら一つの Work Unit に対して一名の worker（1 worker）だけを選ぶ。指定が同時に存在して解決できない
場合、無断で経路を変えず `stop-incomplete` とする。

経路の指定がない場合、親は小さく仕様が明確で影響範囲が閉じ、親 direct の方が委譲より安いなら `direct` を選ぶ。
それ以外で単一 Work Unit として安全に委譲できるなら一名の worker へ委譲する。どちらも安全に確定できなければ
`stop-incomplete` とする。この判断に固定閾値や決定表を持ち込まない。

委譲時は v5 の候補から、実装自由度、実装後も残る判断、推論難度、誤実装時の手戻り、検証可能性、実行コストを
相対比較して一名を選ぶ。通常は仕様が明確で既存 pattern を適用できる `implementer` を選ぶ。scope が特に狭く
検証が明確なら `focused-implementer`、残存判断や手戻りが大きいなら `senior-implementer`、親相当の推論が
品質を左右するなら `expert-implementer` を選ぶ。単なる変更量、file 数、ラベルだけで上位 worker を選ばず、
迷った場合は `implementer` を選ぶ。選択した worker と理由、base snapshot、execution constraint を実行 data
に記録する。

worker の指定は execution constraint であり、品質上不十分だと判明しても無断で変更・続行しない。制約緩和を
確認するか、未完了範囲と判断点を付けて `stop-incomplete` とする。worktree、context、基準状態の扱いが依頼の
範囲に含まれていない場合も、暗黙に複数実行環境を作らない。

この loop は一つの Work Unit の direct または一名委譲だけを扱う。一回の実行で複数 Work Unit、fresh context、
再正規化、isolation の追加設計、直列・並列の複数実行、reviewer、finding、永続 artifact が必要になったら、先取り
せず安全に `stop-incomplete` とする。別の機構へ自動的に切り替えない。

## Implementation and TDD

親と worker は、確定した purpose、AC、scope、exclude、constraints、depends_on、verification を共有し、指定
範囲だけを編集する。既存 test の削除、skip、期待値の弱体化、未承認の依存追加、生成物の直接編集はしない。

observable な code behavior は Red → Green → Refactor で進める。

1. **Red** — AC から正常系、境界値、異常系、例外経路を導いた test を先に追加し、意味のある failing output を
   記録する。これを Red 証跡として返却 data に含める。意味のある failing test が成立しない場合は、変更前の evidence、成立しない理由、代替 verification
   を返す。形式的な mutation は行わない。
2. **Green** — 最小の実装で test を通し、focused test と必要な native verification の command と結果を記録する。
3. **Refactor** — AC、責任境界、error handling、命名を保ったまま重複を整理し、Green を再実行する。Refactor
   で意味が変わる場合は Green へ戻り、同じ Work Unit の範囲を越えない。

## Parent QA and continuation

direct でも委譲でも、親は結果を受け取った時点の baseline diff、AC、scope、exclude、dirty state、test、
副作用、既知 risk を自分で確認する。親は worker の報告を鵜呑みにせず、Red/Green/Refactor の evidence、focused
test、repository-native verification を再実行し、変更が同じ Work Unit の責任境界内にあることを確認する。

限定修正を続けられるのは、AC と責任境界が不変で、同じ Work Unit（same Work Unit）の実装上の不足だけである。修正後は baseline
diff、関連 test、影響する verification を更新して再確認する。新しい目的、AC、依存、scope、worker、または別の
実行環境が必要になったら続行せず `stop-incomplete` とする。

品質下限を全て満たし、AC、scope、exclude、制約、evidence、残存 risk を親が説明できる場合だけ `accept` とする。
それ以外は未完了範囲、満たせない条件、判断点、evidence、残存 risk、未検証事項を明記して `stop-incomplete` と
する。部分的に通った成果を完了として報告しない。

## Closeout

最終報告には変更 file、baseline からの diff summary、実行した verification command と結果、AC 対応、選択した
経路と、委譲した場合の worker 選択理由、前提、判断点、残存 risk、未検証事項、`git status --short` を含める。親は受け入れたか停止
したかを明示し、未承認の追加作業を残さない。
