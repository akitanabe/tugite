---
name: impl-lead
description: >-
  明示起動時だけ、implementation work を Implementation Unit へ正規化し、実装、Parent QA、受入、final verification、安全な統合まで所有する public workflow。
---
<!-- Generated from shared/. Do not edit directly. -->

# impl-lead

## Identity and authority

`impl-lead` は Human が明示的に起動した場合だけ、request、Plan、または established direction から implementation work を受け取る public workflow である。自然言語の実装依頼だけから暗黙に起動せず、別 workflow から自動遷移しない。

親は Phase 8-1 の Implementation Unit normalization、Phase 8-2 の execution capability、Phase 8-3 の execution orchestration、Parent QA、Unit acceptance、run-wide final verification、integration / closeout を一つの run として所有する。Model Construction は mandatory phase にしない。

入力 Plan、request、established direction の outcome、Acceptance Criteria、scope、constraints、authority を run の上限とする。execution evidence や finding から Plan 外の material work を追加しない。Plan 内で閉じない material item は実装せず、上流または Human へ返して `stop-incomplete` とし final report に残す。

`references/external-effects.md` が、implementation、verification、integration、cleanup を含む run 全体に適用する external Action の cross-cutting pre-action safety boundary と適用手順を所有する。親は各 Action に同 reference を適用し、実行 eligibility と result safety を裁定する。Git / worktree 固有の procedure は `references/run-owned-lifecycle.md`、post-diff specialized review は `references/risk-review.md` が所有する。

## Intake and Implementation Unit normalization

親は implementation work から意味上区別できる implementation outcome candidates と grounding を構成し、outcome candidate の抽出、implementation scope、要求 coverage の最終責任を保持する。

Implementation Unit Data は invocation 内の transient Data であり、`id`、`purpose`、`acceptance_criteria`、`scope`、`implementation_freedom`、`constraints`、`depends_on`、`verification` の8 fieldを持つ。worker、reviewer、route、execution result、finding、QA result、persistence は execution Data であり Unit identity に含めない。

grounding には request / Plan / established direction、Acceptance Criteria の素材、scope / constraints、repository evidence、known dependency、verification reality、accept / rollback reality を含める。親は non-empty target を固定し、`references/implementation-unit-design.md` の `impl-lead implementation-unit-design v1` を load・検証して execution 前に exactly once 適用する。

### pre-execution-unit-design-control

Trigger: non-empty の outcome candidates と grounding が固定され、execution が未開始である。

Inputs: 固定済み target、Method path `references/implementation-unit-design.md`、expected identity `impl-lead implementation-unit-design v1`、execution-not-started evidence。

Procedure:

1. Method identity と required section を検証する。不足・不一致では judgment と execution を開始しない。
2. non-empty の候補集合を、single / trivial を含めて execution 前に exactly once Method へ渡す。execution 後の再 invocation は作らない。
3. result の coverage、scope、blocking gap、Unit Data と execution Data の分離を親が確認する。
4. 各 candidate に run 内で一意の ID を付与し、返された semantic dependency をその ID に束縛する。

Outcomes: execution-ready な Unit 集合、または material reason を伴う `stop-incomplete`。

この Flow は split / merge、Unit boundary、semantic dependency、independent acceptability の意味判断を行わない。

親は元の outcome candidates が暗黙に消えていないこと、要求 coverage、scope が拡張されていないこと、blocking gap がないことを確認し、Method の split / merge judgment を再設計しない。各 Unit に run 内で一意な `id` を付与し、Method が返した semantic dependency relation をその ID へ束縛する。

## Run lifecycle

execution 前に integration target の start identity と current identity、tracked state、collision reality を capture し、run 全体で一つの task-owned branch と run-owned worktree を使う。通常は Unit を dependency order で serial execution する。parallel implementation はこの workflow の policy に含めない。

各 Unit は次の順で閉じる。

1. `references/execution.md` により readiness、route、tier、context、Writable Scope、TDD、monitoring を確定して実装する。
2. `references/parent-qa.md` により mandatory Parent QA を行う。
3. concrete risk が判断を変え得る場合だけ `references/risk-review.md` により specialized review と correction を行う。
4. candidate commit を作り、`references/completion-gate.md` の mandatory Completion Gate を通す。
5. Parent QA と gate が Green の commit を Unit の accepted immutable baseline とする。

1 Unit は1 commitに対応する。accepted Unit を amend、reopen、renormalize しない。Unit acceptance は親が ownership、evidence、risk disposition、Completion Gate を裁定した時点でだけ成立する。

全 Unit の acceptance 後に run-wide final verification を実行する。failure が入力 authority の内側で8 fieldすべてを閉じられる単一の minor / local correction なら、run 内一意 ID と既存 Unit ID への dependency を持つ new Unit として fresh `focused-implementer` に渡し、新 commit、Parent QA、必要な risk review、Completion Gate、final verification を通常どおり行う。それ以外、または進展しない failure は `stop-incomplete` とする。

final verification が Green の場合だけ `references/run-owned-lifecycle.md` により integration と cleanup eligibility を別々に裁定する。external Action がある場合は `references/external-effects.md` を適用する。

## Completion and report

`accepted` は全 Unit accepted、run-wide final verification Green、要求された integration が確認済みで、必須 external Action が verified `実行済み` または Human により明示的に不要化され、Plan 外 material item がない場合だけ返す。必須 external Action が `未実行` または `結果不明` なら evidence / retention state を保持して `stop-incomplete` とする。`stop-incomplete` となった run の accepted commits は task-owned branch に保持し、部分 integration しない。

conversation final report には Unit 状態、commit / branch / integration、Parent QA / verification、risk review disposition、Completion Gate、external effect state、final verification、residual risk、cleanup / retention、Plan 外 material item を記す。固定 ledger や persistent report schema は作らない。

## Reference ownership

- `references/implementation-unit-design.md`: execution 前の Unit boundary / split / merge / dependency judgment
- `references/execution.md`: implementation dispatch と monitoring
- `references/parent-qa.md`: mandatory Parent QA と Test QA baseline
- `references/risk-review.md`: risk-directed specialized review
- `references/completion-gate.md`: final writing review と Unit commit closure
- `references/run-owned-lifecycle.md`: worktree、integration、cleanup
- `references/external-effects.md`: repository 外も含む side-effect safety

## Non-goals

- scope 外 outcome、Acceptance Criteria、authority の追加
- execution-time renormalization、parallel implementation、persistent execution ledger
- Model Construction、Issue / PR 更新、release、version 更新の暗黙実行
