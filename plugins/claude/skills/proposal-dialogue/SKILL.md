---
name: proposal-dialogue
description: >-
  plan-craft-approval の同じ親 context 内だけで、人間と方向性を逐次裁定して direction freeze 候補を作り、
  candidate snapshot または stop-incomplete を caller-owned parent へ返す internal skill。
user-invocable: false
---
<!-- Generated from shared/. Do not edit directly. -->

# proposal-dialogue

## 位置づけと入力

この Skill は `plan-craft-approval` の同じ親 context 内だけで使う internal skill であり、ユーザーから直接起動しない。
`proposal` と同じ candidate producer として、後段工程を選択・起動せず caller-owned parent へ返す。差分は、方向性を
変えうる主要判断を planner ではなく人間が裁定することである。

親から要求原文、目的、成功条件、scope、exclude、制約、依存、repository observation、現在の working snapshot を
Data として受け取る。repository、Issue、既存仕様から確認できる事実は先に調査し、調査可能な事実を人間へ質問しない。
不足または矛盾が方向性を変える場合は推測せず、必要な判断と evidence を付けて `stop-incomplete` を返す。

## 方向性判断と逐次 snapshot

方向性を変えうる判断点を抽出して依存関係で順序付け、一度に一つの主要判断を扱う。各判断は、論点の背景、選択肢と
trade-off、親の推奨と理由、一つの質問、人間の回答、決定内容の自然文確認、次の依存判断の順に進める。

人間の判断は `採用` / `却下` / `保留` / `修正して採用` の4値で記録する。親の推奨を人間の回答として扱わない。
無回答・曖昧な反応を承認として扱わず、条件や限定を含む決定内容を人間が確認してから確定する。不採用と保留は正常な
判断結果であり、敵対的な未解決指摘へ読み替えない。

採用分だけを working snapshot へ逐次反映して verification し、複数の判断を一括反映しない。却下・保留した提案を
暗黙反映せず、後続判断は更新済み snapshot を基準にする。判断点、期待する価値、trade-off、親の推奨と理由、人間の判断、
反映 snapshot、verification を decision ledger として会話内 Data に保持するが、YAML、内部 schema、raw ledger は
ユーザーへ提示しない。

direction freeze 候補は、採用提案が反映・verification 済み、主要判断が明示裁定済み、保留事項が scope 外へ分離済み、
blocking な人間判断がなく、ユーザーが現在の方向を確認済みの場合だけ成立する。プラン系の working snapshot は
`Acceptance Criteria` と `設計` の節名を持つ。自由形式成果物にはこの節構成を強制しない。

## necessity-kernel v1 の parent mapping

candidate Claim を判定する前に、advisor 起動の有無にかかわらず、親は生成後の skill directory から package-root reference へ skill-relative `../../references/necessity-kernel.md` を読み、identity と必要な本文を既存の
`判定基準` または `必要な周辺 context` の一部にする。`plan-quality-advisor` 起動時は既取得 Data を既存の判定基準として渡す。reference の不足、identity 不一致、
読み取り失敗があれば推測せず `stop-incomplete` へ返し、advisor は plugin 相対 path を解決しない。

候補 Claim の必要性は既存の判定基準に含めた Task Specification と Deletion Test で観察する。Claim は insight 本文
ではなく、candidate に追加・維持・変更・除去・検証・調査する obligation の候補であり、根拠を observation / evidence
から追跡する。`necessary` / `unnecessary` / `indeterminate` を新しい返却 field にせず、親は adoption ledger の
`adopted` / `rejected` / `unresolved` へ写像する。更新後は更新された snapshot で再判定し、互いを witness とする
同時削除を認めない。必要性分類は既存語彙へ写像し、新verdict fieldではない。round budget / termination へ
直結させない。`structural-health-gate` の意味は この mapping の対象外である。

## advisor insight

scope・責務境界を変える提案の採用、採用提案間の依存、決定を補う追加提案、または freeze 前の非自明な変更連鎖が
ある場合だけ、read-only `plan-quality-advisor` に candidate snapshot と判定基準を渡す。insight は非拘束 Data であり、
planner が一次情報と要求に照らして adoption ledger の `adopted` / `rejected` / `unresolved` へ裁定する。
decision ledger と adoption ledger は分離する。

advisor insight を自動採用せず、insight から質問を自動生成しない。advisor を固定 phase にせず、`insights: []` を
direction freeze の自動根拠にしない。人間が採用した方向性へ影響する insight は planner だけで巻き戻さず、evidence を
照合して `unresolved` とし、人間へ一つの主要判断として返す。

## 有界な対話と返却

固定の対話回数を品質条件や消化目標にしない。親は一つの対話 loop の開始時に安全上限を決め、loop 中に変更しない。
親から新しい evidence とともに再実行された場合は新しい対話 loop とし、上限は親が改めて決められる。過去の対話裁定を
打ち切りの成立条件として保存・参照しない。

通常の返却 Data は `candidate_snapshot`、`decision_ledger`、`adoption_ledger`、`assumptions`、
`blocking_gaps`、`residual_risks`、`status` を持つ。blocking な人間判断が残る、ユーザーが対話終了を求める、または
安全上限に達して判断候補が残る場合は `status: stop-incomplete` と必要な判断を返す。いずれも成果物の受け入れを
主張せず、caller-owned parent へ返して終了する。
