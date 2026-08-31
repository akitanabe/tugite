<!-- @only claude -->
---
name: impl-lead
description: >-
  明示起動時だけ、implementation work を execution 前の Implementation Unit へ正規化し、
  Phase 8-1 の境界で execution を開始せず incomplete として返す public workflow。
disable-model-invocation: true
---
<!-- @/only -->
<!-- @only codex -->
---
name: impl-lead
description: >-
  明示起動時だけ、implementation work を execution 前の Implementation Unit へ正規化し、
  Phase 8-1 の境界で execution を開始せず incomplete として返す public workflow。
---
<!-- @/only -->
<!-- @only cursor -->
---
name: impl-lead
description: >-
  明示起動時だけ、implementation work を execution 前の Implementation Unit へ正規化し、
  Phase 8-1 の境界で execution を開始せず incomplete として返す public workflow。
disable-model-invocation: true
---
<!-- @/only -->

<!-- @anchor impl-lead-document-relation -->
# impl-lead

## Identity and current boundary

`impl-lead` は Human が明示的に起動した場合だけ、request、Plan、または established direction から implementation work を受け取る
public workflow である。自然言語の実装依頼だけから暗黙に起動せず、別 workflow からの自動遷移も行わない。

現在の責務は Phase 8-1 の Implementation Unit normalization までである。worker / reviewer の選択、direct / delegate、execution order、
parallelism、isolation、implementation continuation、親 QA、verification / acceptance workflow、persistence、Model Construction は所有しない。

## Intake and Implementation Unit normalization

<!-- @contract impl-lead-intake-ownership -->
<!-- @anchor impl-lead-intake-ownership-relation -->
親は implementation work から意味上区別できる implementation outcome candidates と grounding を構成し、outcome candidate の抽出、implementation scope、要求 coverage の最終責任を保持する。

grounding には、request / Plan / established direction、Acceptance Criteria の素材、scope / constraints、repository evidence、known dependency、
verification reality、accept / rollback reality を含める。候補は到達結果を表し、file 編集、generator、version 更新、verification command のような
実装手段を、それ自体が要求成果でない限り outcome candidate にしない。
<!-- @/contract -->

<!-- @contract impl-lead-unit-data -->
Implementation Unit Data は invocation 内の transient Data であり、`id`、`purpose`、`acceptance_criteria`、`scope`、`implementation_freedom`、`constraints`、`depends_on`、`verification` の8 fieldを持つ。

- `id`: run 内で一意な識別子。
- `purpose`: 単一の outcome purpose。
- `acceptance_criteria`: 外部から観測可能で検証可能な受入候補条件。
- `scope`: `change` と `exclude` を持つ実装境界。
- `implementation_freedom`: Implementer に委ねる局所判断。なければ空。
- `constraints`: established constraints と互換性・環境上の制約。
- `depends_on`: Unit 間の semantic dependency と、外部・repository・environment precondition。
- `verification`: Acceptance Criteria ごとの focused verification と必要な final gate。

worker、reviewer、route、order、isolation、execution result、finding、QA result、persistence は Unit identity ではなく、後続 Phase の
execution data である。Implementation Unit Data を persistent schema、canonical artifact、ledger にしない。
<!-- @/contract -->

親は outcome candidates と grounding を一つの non-empty normalization target として固定する。空 target は Method へ渡さない。
候補数や small / trivial という見かけから 1 Unit または N Units を先に決めない。

## Programmatic Flow

<!-- @contract impl-lead-pre-execution-flow -->
<!-- @anchor impl-lead-pre-execution-flow-relation -->
### pre-execution-unit-design-control

Trigger: 親が non-empty の implementation outcome candidates と grounding を確定し、implementation execution が未開始のとき。

Inputs: 固定済み outcome candidates / grounding、Method path `references/implementation-unit-design.md`、expected identity `impl-lead implementation-unit-design v1`、execution-not-started evidence。

Procedure:

1. generated Skill から Method path を解決して load し、identity と `Identity and responsibility boundary`、`Inputs and outputs`、`RMO loading and mapping`、`Partition judgment`、`Uncertainty and return boundary` の各 section を検証する。load、identity、required section の不足・不一致では Method judgment も execution も開始しない。
2. non-empty の候補集合を、single / trivial を含めて execution 前に exactly once Method へ渡す。empty target、候補ごとの個別 invocation、recursive invocation、execution 開始後の再 invocation を作らない。
3. Method から Implementation Unit candidates、判断理由 / qualification、blocking gaps を受け取る。blocking gap または required result の不足では Unit を確定せず `incomplete` とし、成立した result だけを親の返却後 integrity check へ渡す。

Outcomes: `unit-design-returned` と Method result、または material reason を伴う `incomplete`。どちらも implementation execution を開始しない。

この Flow は outcome extraction、split / merge、Unit boundary、semantic dependency、independent acceptability、blocking materiality、
coverage / scope integrity の意味判断を行わない。これらの判断は親または Method の Agentic responsibility に残す。
<!-- @/contract -->

## Method return integrity

<!-- @contract impl-lead-return-integrity -->
<!-- @anchor impl-lead-return-integrity-relation -->
Method 返却後、親は元の outcome candidates が暗黙に消えていないこと、要求 coverage、scope が拡張されていないこと、unresolved
blocking gap がないこと、Implementation Unit Data と後続 execution data が混在していないことを確認する。要求されていない outcome を
追加せず、Method の split / merge judgment を再設計しない。

親は採用する各 Implementation Unit candidate に run 内で一意な `id` を付与し、Method が返した semantic dependency relation を
その ID へ束縛して Implementation Unit Data を確定する。dependency の意味を再判断せず、ID schema や persistent ledger を導入しない。
<!-- @/contract -->

blocking uncertainty が Unit boundary、semantic dependency、independent acceptability を変え得る場合は Unit を確定しない。
non-blocking uncertainty は qualification として保持できる。Unit の設計前提が将来の execution 中に崩れた場合も Method へ戻る loop を
作らず、current execution を安全に継続しない上流境界へ返す。

## Phase 8-1 outcome

<!-- @contract impl-lead-phase-boundary -->
Unit Data を安全に確定できた場合も、その Unit Data と execution-not-started boundary を保持し、execution、verification、acceptance を開始せず `incomplete` を返す。
<!-- @/contract -->

完了済み implementation や accepted result を主張しない。Phase 8-2 の Implementer / Reviewer inventory、Phase 8-3 の execution、
Phase 8-4 の verification / acceptance が別途成立した後にだけ、その責務を current workflow へ接続できる。

## Non-goals

- raw request から scope 外の outcome を発明すること
- Implementation Unit Design の public / internal Skill 化または shared Method 化
- direct / delegate、worker / reviewer、order / parallelism / isolation の選択
- implementation-time correction、renormalization loop、parent QA、accept / rollback operation
- context token budget、overflow score、size threshold、固定 Unit 数の導入
- Model Construction、Issue / PR 更新、release、version 更新
