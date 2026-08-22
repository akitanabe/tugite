# impl-lead parent QA v1

この reference は、`impl-lead` の独立した親 QA、Red 観測の behavior-observation-kernel v1 mapping、run-owned closeout
前の QA を定義する。親は `SKILL.md` で指定された時点に全文を読み、判断と Action を自身の execution data として扱う。

## Parent QA and closeout

direct でも委譲でも、親は各単位の結果を受け取った時点の baseline diff、AC、scope、precondition、dirty state、
test、side effect、既知 risk を自分で確認する。親は worker の報告を鵜呑みにせず、Red/Green/Refactor の evidence、focused
test、repository-native verification を再実行し、変更が同じ Implementation Unit の責任境界内にあることを確認する。

<!-- @contract impl-parent-red-behavior-observation-kernel-loader -->
### Parent Red QA の behavior-observation-kernel v1 mapping

Red 証跡受領後かつ Red 受理前に、親は AC / resolved Behavior + relevant Context から独立に Expected Observations を導出し、提出 Red と照合する。提出 Red は評価対象であり grounding ではない。

見るものは次である。

- Red が AC / resolved Behavior の成立・不成立を区別できるか
- 必要な meaningful variation について片側だけの人工 test になっていないか
- Behavior 上必要な Boundary / Failure / Relation の意味が Red で観測可能か
- variation ごとの条件関係が平坦化されていないか
- mock / stub が本来確認すべき状態遷移や relation を隠していないか

次の Loader Data がこの load の唯一の正本である。

```text
path = ../../../references/behavior-observation-kernel.md
load_timing = after Red evidence received and before Red accept
identity = behavior-observation-kernel-v1
required_sections = [Contract, Method, Reintegration, Consumer の責務, 非目標]
failure = stop-incomplete
owner = impl-lead parent
delegate_path_resolution = false
```

親自身が consumer であり、Implementer へは注入しない。Kernel の導出結果、Expected Observations、meaningful variation、Exploration Lens を Implementer handoff に事前注入しない。親 QA の `判定基準` に載せた Kernel 本文を、Red 差し戻し後の Implementer handoff へコピーしない。差し戻し時も具体的な Expected Observation を答えとして渡さず、AC / Behavior に戻して再探索させる。Implementer / worker の Red 手順本文へ Kernel 利用を追加しない。

Green / Refactor / baseline self-QA / risk-directed review / final writing gate を置き換えない。Collective Sufficiency は Implementation Unit accept ではない。direct と委譲の両方で同じ親照合を行う。差し戻し handoff は既存の Implementation Unit Data / AC / constraints / relevant Context に閉じる。
<!-- @/contract -->

### Run-owned closeout

run-owned worktree を作成した run は、先に読み込んだ `references/run-owned-lifecycle.md` の `Closeout` に従う。親 QA、選択した
risk-directed review、final writing gate、final verification、必要な外部副作用の照合後に、親は観測 Data を
`run-owned-closeout` へ渡す。

追加作業の continuation route は `implementation-unit-continuation-routing` に従う。親が品質下限を満たし、全要求単位を accepted とし、
選択した review goal と finding の処理結果を確認し、AC、scope、制約、evidence、残存 risk を説明できる場合は、run accept 前に closeout の repository gate を含む final closeout verification を
実施する。その verification が Green なら run を accept する。新しい failure が出た場合は run を accept せず Adapt または
`stop-incomplete` へ戻す。品質下限等を満たせない場合は、未完了範囲、満たせない条件、判断点、evidence、残存 risk、未検証事項を明記して
`stop-incomplete` とする。固定状態機械や常時必須の永続化された実行成果を新設しない。
