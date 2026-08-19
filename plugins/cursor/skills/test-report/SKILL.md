---
name: test-report
description: >-
  ユーザーが `test-report` を明示した場合、または指定範囲のテスト群の理解・把握を求める意図が明確な場合に使う。
  指定範囲の Verification Topology を、独立 grounding した Expected Observation を軸に観測事実として提示する。
  テスト・コードの編集、実行、品質評価、後続 Action は行わない。
---
<!-- Generated from shared/. Do not edit directly. -->

# test-report

`test-report` の明示指定、または指定範囲のテスト群の理解・把握を求める意図が明確な依頼で開始する。単なる曖昧な相談や、
テストに言及しただけの依頼では開始しない。他 workflow の工程としての自動起動はしない。

## 責務と境界

テスト・コード・成果物の編集、実装、委譲、Worker 起動、後続 Action を行わない。テスト・対象コードの実行も行わない。
観測は静的読解に限る。

十分性判定・品質評価をしない。report は観測事実だけを述べ、「不足している」「追加すべき」等の評価・推奨語彙を使わない。
構造的空白の意味判断（埋めるかどうか）は Human に残す。

report 生成は skill を読んだ親エージェントが直接行い、新しい agent を追加しない。report 提示後の Human の追質問は
skill 契約の外の通常対話として扱う。

## behavior-observation-kernel v1 の parent mapping

`test-report` 親（skill を読むエージェント）が consumer である。新 agent は追加しない。

次の Loader Data が列挙値の唯一の正本である。

```text
path = ../../references/behavior-observation-kernel.md
load_timing = after scope resolution and any Human confirmation that allows continuation, before report body construction
identity = behavior-observation-kernel-v1
required_sections = [Contract, Method, Reintegration, Consumer の責務, 非目標]
failure = Topology も経路3/4継続本文も出さない。Human 確認へ返す。了承しても Kernel 未検証のまま報告本文を構築しない。4経路へ写さない。stop-incomplete は新設しない
owner = test-report parent
delegate_path_resolution = false
```

注入先は既存の判定基準 / 必要な周辺 context である。Kernel 専用 channel と返却 field は増やさない。

継続を了承したあとの報告本文構築の前に `behavior-observation-kernel-v1` を load し、identity と required sections を検証する。
経路3/4の了承後も Kernel は load する。省略するのは独立 grounding / Expected Observation 導出 / Gap Overlay であり、load 自体ではない。
Kernel load / identity / required sections の失敗は既存4経路に写さない。Topology も経路3/4継続本文も出さない。Human 確認へ返す。
了承しても Kernel 未検証のまま報告本文を構築しない。

Collective Sufficiency は Expected Observation model の導出十分性であり、テスト十分性ではない。
Human 向け中心語にしない。`Insufficient` / `Indeterminate` は Observation Limits の材料になり得るが、評価語には変換しない。
Relevant Unresolved Viewpoints は Observation Limits へ圧縮し、独立内部語彙のまま中心概念にしない。

## 入力（指定範囲）

テスト path / directory の明示指定と、機能・領域の自然言語指定の両方を受け付ける。対象コード範囲は、指定された機能・領域
またはテスト群が属する構造単位（module / package / directory 等）からコード側を解決し、テストの存在を前提にしない。
テスト範囲を解決した結果として対象テストが 0 件であることは、範囲解決不能とは扱わず、有効な観測結果として継続する。
実際に観測した範囲（対象にしたテスト群と対応する対象コード範囲）を、ドメイン語彙の要約とともに report に明記する。

観測の完全性はテスト範囲と対象コード範囲で基準を分ける。テスト範囲の完全性は、解決済みテスト file 対 読解済みテスト file の一覧差とする。対象コード側は、指定範囲から repository / language / framework の既存構造で再構成できる対象コード単位とする。
単位の具体的解決方法は環境から復元し、framework 固有ルールを先回りして固定しない。観測済み極は、解決済み単位のうち、
その単位を識別する authoritative entry（export / public API / その単位の入口となる既存構造上の面）を実際に読解した単位とする。
一覧差は解決済み単位 − この読解済み単位であり、relevance の自己申告で宇宙を作らない。

公開面抽出を Gap または突合 Overlay の完了条件にしない。読解は「単位を見た」ことの観測極であり、公開面項目とテストの突合ではない。
Kernel への relevant Context 注入は、読解済み単位からのフィルタである。注入しなかった読解済み単位は経路2に載せない。
未読解単位だけが経路2の対象コード側である。

範囲の解決と観測の限界は次の各経路で扱う。限界情報の report 上の提示位置は全体像の必須要素に従う。source 種別ごとの確認経路は作らない。

- テスト範囲を解決できない場合は、推測で継続せず Human への確認へ返す。解決済み範囲の結果が 0 件である場合はこの経路に入らない。
- 部分観測は、解決済みテスト file のうち観測していない file が残ることを基準に判定する（解決済み一覧と観測済み一覧の差として
  観測可能であり、agent の自己申告に委ねない）。対象コード側は、解決済み単位と読解済み単位の一覧差でも部分観測とする。
  部分観測のまま空白を提示せず、Human へ範囲縮小または分割の確認へ返す。
  Human が部分観測での継続を了承した場合のみ継続する。
- 対象コード範囲の解決不能は観測可能な2条件（指定から対応する対象コード範囲を一意に特定できない、または対象コードが
  repository 外にある）に限って認め、Human へ確認を返す。  Human が了承した場合のみ独立 grounding / Expected Observation 導出 / Gap Overlay を省略し、観測できた Case / Evidence と Observation Limits だけ継続する。Kernel は load 済みであり、Kernel 未 load とは同一視しない。
- 指定範囲全体として、独立 grounding できる authoritative Context が成立しない場合は Human へ確認する。了承時は Observed Test Behavior と Observation Limits のみとし、Expected Observation / Gap は生成しない。Kernel は load 済みである。

## Behavior の独立 grounding

照合先の対象 test 自身を、その test と照合する Expected Observation の grounding に使わない。対象 test は discovery signal、
Case、Evidence、Observation Boundary facts に使える。

テストにしか現れ独立 grounding できないものは Observed Test Behavior（`grounding: unresolved`）として Observation Limits へ置く。
その Behavior に Kernel 由来の Expected Observation / Gap を生成しない。経路4にはしない。

relevant Context はファイル種別ではなく authority で判断する。public surface は grounding source の一つである。指定範囲の
Behavior 解決に必要な Context だけを Kernel へ注入し、指定範囲外へ取得を広げない。

独立 grounding は既定で行う。AC / docs を対象とする独立した突合チャンネル（文書項目対テスト）は作らない。指定範囲内で
authority を持つ specification / contract は、Behavior identity の relevant Context にしてよい。ファイル種別で自動除外しない。
Gap Overlay の入力は、独立 grounding した Behavior から Kernel が導出した Expected Observation であり、仕様文書の項目一覧ではない。
指定範囲外の AC / docs を探しに行かない。coverage 判定および「不足している」等の評価語彙に変換しない。

## report の意味内容

テスト群を振る舞い・シナリオ単位に再構成する。振る舞い名は対象ドメインの語彙で命名し、テスト実装用語（fixture、mock 名等）を
主語にしない。個々のテストケース・ファイルの列挙や要約を主目的にせず、ファイル単位の情報は補助として扱う。

report の中心は、独立 grounding した Expected Observation を軸とする Verification Topology である。意味モデルは graph / relation であり、
厳密な木にしない。

```text
Independently Grounded Behavior
        ↓
Expected Observations
        ↕ many-to-many
Cases
        ↓
Evidence
        └─ execution state

Cases / Evidence
        └─ Observation Boundary facts
```

Expected Observation と Case の many-to-many を意味上保持する。同じ Case が複数 Expected Observation に対応する場合の再掲は presentation projection であり、意味上の重複ではない。

Case は意味的シナリオ単位であり、test function 単位ではない。正常系 / 境界値 / 異常系は Topology の構造原理にせず、Human 向け presentation label に降ろす。worker が使う既存語彙は変更しない。property-based / snapshot / invariant / relation 等を
固定分類へ無理に写像しない。

Evidence は観測主張の最小参照可能単位であり、test function 全体と同一視しない。Observation Boundary facts は open-ended な静的事実とする。
Unit / Integration / E2E の閉じた enum にしない。Evidence と Observation Boundary facts が Case / Expected Observation から追跡可能である。

テストの実行状態を観測事実として提示する。execution state は `statically executable` / `statically non-executed` / `indeterminate` とする。
skip 指定や test runner の対象から外れている file など、静的に観測できる非実行をケース提示と区別し、非実行のケースを実行されるケースと同列に「検証されている」として数えない。
runner / test configuration は、この静的な実行状態を判定するために必要な範囲で補助観測してよい。この補助観測は対象コード範囲や
独立 grounding の範囲を拡張するものではない。実際の CI job での実行有無など静的に観測できない実行状態は断定しない。
executable がなく、corresponding evidence に `indeterminate` が含まれる場合（non-executed 混在を含む）、Gap にも Unresolved Mapping にもしない。
Observation Limits（execution state を静的に確定できない）とする。CI 断定しない。

Gap は、独立 grounding した Expected Observation に対して、指定範囲（または Human が了承した実観測範囲）内で対応する usable evidence が観測されない状態である。範囲外のテストや別手段の検証の不在を断定しない。品質評価・推奨へ変換しない。

判定順:

1. 対象 test をその Expected Observation の grounding に使わない。
2. Evidence が独立 grounding 済み Behavior identity に静的帰属でき、Expected Observation の条件が平坦化されずに保持されている場合、correspondence 確定とする。
3. correspondence 確定かつ `statically executable` な corresponding evidence が1つでもある場合、usable evidence observed とする。その Expected Observation は Gap ではない。他に non-executed / indeterminate があっても usable を優先する。
4. executable がなく、corresponding evidence がすべて `statically non-executed` の場合、Gap Overlay の提示差「non-executed evidence only」とする。Unresolved Mapping ではない。
5. executable がなく、corresponding evidence に `indeterminate` が含まれる場合（non-executed 混在を含む）、Gap にも Unresolved Mapping にもしない。Observation Limits（execution state を静的に確定できない）とする。CI 断定しない。
6. corresponding evidence がない場合、Gap Overlay「no corresponding evidence observed」とする。
7. correspondence を静的に確定できない場合、Unresolved Mapping とする。Gap にしない。candidate evidence を添える。

`usable` は correspondence 確定かつ `statically executable` である。Behavior 全体の evidence 欠落と、一部 Expected Observation だけの欠落は、同じ Gap model の異なる scope / presentation とする。

correspondence を静的に確定できない場合、Unresolved Mapping とする。Gap にしない。Unresolved Mapping は Observation Limits に匿名化しない。

空白の主張は常に指定範囲に相対で述べる（「指定範囲内では観測されない」）。部分観測を了承した実行では、指定範囲ではなく実際の
観測済み範囲に相対で述べる。範囲外のテストや別手段の検証の不在を断定しない。

振る舞い命名、ケース分類、検証手段、空白の全主張に test / code への参照（file 位置等）を付け、Human が report を読んだまま
spot-check できるようにする。実行状態を runner / test configuration から判断した主張には、その config への参照も付ける。

Change Overlay は実装しない。予約 field と未使用 schema は作らない。Verification Topology を、追加 overlay を禁止する閉じた schema にしない。

## 提示構造

全体像先行の階層提示とする: 圧縮した全体像 → 振る舞い別の詳細。Human 向け report は Expected Observation を主表示単位とした階層へ射影してよい。全体像には次を含める。

- 検証体系の見取り図（Verification Topology）
- Gap Overlay の全件（重要度による選別・省略はしない）
- 非実行の有無
- Unresolved Mapping（独立提示。Observation Limits に匿名化しない）
- Observation Limits（Kernel 未確定、scope / partial observation、test-only grounding unresolved、execution state indeterminate 等）
- 観測範囲のドメイン語彙要約
- report が静的観測に基づく旨

詳細側で Expected Observation → Case → Evidence / Boundary facts を展開する。

report は one-shot 生成とし、保存・資産化・再実行間の追跡は skill の責務にしない。
