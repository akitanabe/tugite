<!-- @only claude -->
---
name: structural-health-gate
description: >-
  plan-craft の proposal 後かつ review-loop 前だけ、candidate の構造的局所性を evidence として評価する
  internal gate。成果物を再設計・直接編集せず、最終判断を親へ残す。
user-invocable: false
---
<!-- @/only -->
<!-- @only codex -->
---
name: structural-health-gate
description: >-
  plan-craft の proposal 後かつ review-loop 前だけ、candidate の構造的局所性を evidence として評価する
  internal gate。成果物を再設計・直接編集せず、最終判断を親へ残す。
---
<!-- @/only -->

# structural-health-gate

この Skill は、`proposal` が返した candidate snapshot を `review-loop` へ渡す前に、局所修正で review 可能な
構造かを評価する。plan-craft と同じ親 context 内だけで使い、単独起動、ユーザーからの直接起動、別 workflow
からの流用はしない。

## 入力

親は不変な `candidate_snapshot`、要求原文、requirements、design、Acceptance Criteria、verification、scope、
既知の repository evidence、proposal の判断台帳と assumptions を渡す。必要な source や既存仕様を観測できない
場合は、欠けた evidence を Data として記録し、構造欠陥だと推測しない。

<!-- @contract structural-health-gate-boundary -->
## 観測

次を、表現上の指摘ではなく構造上の因果として確認する。

- duplicated source of truth と、同じ判断が複数箇所で独立に更新される責務。
- 未解決の方向性または責務が、新しい設計判断を後段へ要求していないか。
- requirements、design、Acceptance Criteria、verification の対応漏れまたは矛盾。
- 用語、state、priority、responsibility の定義または遷移の不整合。
- 局所修正が他の要件、責務、成果物全体へ広く波及する ripple。
- 複数 finding に見える問題が、一つの structural defect から派生していないか。
- 例外、停止条件、stop contract の追加が増殖し、共通責務の欠落を覆っていないか。

長さ、複雑さ、finding 数だけを理由に `return` しない。局所修正で閉じる密度、詳細不足、文章上の重複は
review-loop で扱えるため、構造欠陥の evidence と混同しない。

## evidence Data

finding は同じ原因を統合し、少なくとも次を返す。

- `location`: candidate 内の箇所と、照合した要求または source。
- `non_local_reason`: local fix だけでは閉じない理由と、影響する責務または判断。
- `predicted_amplification`: review や実装で同じ欠陥が増幅すると予測する因果。
- `predicted_churn`: 修正の反復、例外増加、AC や verification の再変更として予測される churn。

各 finding は観測事実と推論を分ける。必須 field のいずれかを根拠付きで埋められない場合は
`insufficient-evidence` とし、`return` の根拠にしない。reviewer または advisor を使う場合、その出力は
evidence のみであり、candidate の採否、修正、再起草、工程の終了を決めさせない。

## 責務境界

この gate は成果物を再設計・直接編集しない。構造的に健全、不健全、または evidence 不足という assessment
Data と finding を返し、親が最終的な `pass` / `return` / `stop-incomplete` を決める。`pass` は review-loop
の品質判断や成果物の受け入れを意味しない。
<!-- @/contract -->

## 出力

`candidate_snapshot` の identity、`assessment`、finding 一覧、insufficient evidence、観測した source、未検証事項を
返す。Action は親が行い、この Skill は proposal や review-loop を起動せず、resource へ書き戻さない。
