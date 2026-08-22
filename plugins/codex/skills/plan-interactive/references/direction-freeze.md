<!-- Generated from shared/. Do not edit directly. -->

# plan-interactive direction-freeze v1

この reference は `plan-interactive` の direction freeze phase が所有する freeze source construction、verification
derivation の HOW、`direction-freeze-projection` Flow を定義する。Human-confirmed meaning の保護、全 source item の投影、
未解決 Human Decision の禁止、全件 constraint 化という意味の正本は root `SKILL.md` である。

## direction freeze Data

親は要求原文、verified decision ledger、raw source と evidence から、Human-confirmed な価値、重要な scope / exclude、責務、
意図的な非採用、判断点にならなかった raw specification を含む `freeze_source_snapshot` を入力として固定する。
projection の identity／bijection／meaning-evidence 対応は `direction-freeze-projection` Flow に渡し、Human の価値判断と evidence の意味評価は親に残す。
verified freeze 全件を immutable `authority_constraints` とし、direction freeze 自体を existing verified candidate または初期 S0 として扱わない。
未解決 Human Decision が残る freeze は producer へ渡さない。

## freeze 前 verification derivation の親 Data

```text
timing = before direction freeze and after each updated snapshot
owner = plan-interactive parent Calculation
input = Task Specification + verified workflow Data
coverage = normal | boundary | failure path | side effect | prohibition | responsibility boundary | scope exclude
output = how each obligation will be observed after implementation
clarify_it = do not add this derivation or its schema to clarify-it
blocking_gap = incomplete before direction freeze
```

親はこの Calculation の結果を direction freeze の verified workflow Data に反映する。Human へは必要な判断材料だけを
`clarify-it` の既存規範で提示し、verification schema 自体を流入させない。

## Programmatic Flows

### direction-freeze-projection

Trigger: clarify-it `Completed` の verified Data comparison が一意の direction freeze candidate projection を許可したとき。
Inputs: initial Calculation 実行前 Data として、要求原文、verified decision ledger、全意味単位を含む raw `freeze_source_snapshot`、source evidence、workflow-local opaque ID generation input。direction freeze candidate は含めない。
Procedure: source item ごとに非空で一意な ID を一度だけ付与し、source から projection した direction freeze candidate と exact comparison result を中間 Data として扱う。source ID 集合と constraint ID 集合の exact bijection、未投影・重複・余分・meaning mismatch の不在を全数照合し、照合済み `{id, frozen_meaning, source_evidence}` だけを candidate Outcome へ projection する。新しい meaning、condition、decision は加えず、不完全・空・再生成・曖昧な投影は producer 前に `stop-incomplete` とする。
Outcomes: verified Data comparison に対応した unique direction freeze candidate projection、または producer を禁止する `stop-incomplete`。Human Decision、clarification 内容、evidence の意味評価、candidate の採否は親が保持し expected oracle にしない。
