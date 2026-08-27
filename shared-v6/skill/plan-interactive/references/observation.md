# plan-interactive observation v1

この reference は `plan-interactive` が同じ decision context に追加の technical evidence を必要とした場合だけ実行する
observation Action の HOW を定義する。親が trigger を確定した後に読み、判断と Action を自身の execution data として扱う。
technical fact 取得が親 authority であること、この context が conditional であることの意味の正本は root `SKILL.md` である。

## 観測 Action

親は current decision model、parent context、必要な runtime behavior、最小 observation request / criteria を Action 実行前 Data として準備する。
`observation-reapply` Flow が最小 Observation Action の実行と technical evidence gap の返却を唯一の詳細 witness とする。
観測の意味評価、decision-model への再適用、Human clarification、contradictory Action の裁定は Flow 外の親責務である。

## Programmatic Flows

<!-- @contract plan-interactive-observation-reapply-flow -->
### observation-reapply

Trigger: 親の最小観測後も同じ decision model に追加の技術 evidence が必要、または既存 evidence と runtime behavior の不一致が観測されたとき。
Inputs: initial Action 実行前 Data として、同じ current decision model、親確定の最小 observation request / criteria、required runtime behavior、同じ clarify-it parent context、current verified context。observation result と action evidence は含めない。
Procedure: 親確定の最小 Observation Action を一度だけ実行し、result と provenance / evidence を中間 Data として freeze して Agentic 親へ返す。technical evidence gap は親境界へ返し、Human Decision Point や clarify-it Stopped に変換しない。contradictory Action、新しい status、固定 output schema、別 context は導入しない。decision-model への再適用は Flow に置かない。
Outcomes: observation result と provenance / evidence、または親へ返す technical evidence gap。Flow は observation の意味評価、decision-model への再適用、Human の clarification 内容を expected oracle にしない。
<!-- @/contract -->
