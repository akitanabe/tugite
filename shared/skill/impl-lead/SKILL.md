<!-- @only claude -->
---
name: impl-lead
description: >-
  明示起動時だけ、implementation work を Implementation Unit へ正規化し、実装、Parent QA、受入、final verification、安全な統合まで所有する public workflow。
disable-model-invocation: true
---
<!-- @/only -->
<!-- @only codex -->
---
name: impl-lead
description: >-
  明示起動時だけ、implementation work を Implementation Unit へ正規化し、実装、Parent QA、受入、final verification、安全な統合まで所有する public workflow。
---
<!-- @/only -->
<!-- @only cursor -->
---
name: impl-lead
description: >-
  明示起動時だけ、implementation work を Implementation Unit へ正規化し、実装、Parent QA、受入、final verification、安全な統合まで所有する public workflow。
disable-model-invocation: true
---
<!-- @/only -->

<!-- @anchor impl-lead-document-relation -->
# impl-lead

## Identity and authority

`impl-lead` は Human が明示的に起動した場合だけ、request、Plan、または established direction から implementation work を受け取る public workflow である。自然言語の実装依頼だけから暗黙に起動せず、別 workflow から自動遷移しない。

<!-- @contract impl-lead-execution-ownership -->
<!-- @anchor impl-lead-execution-ownership-relation -->
親は Implementation Unit normalization、execution capability、execution orchestration、Parent QA、Unit acceptance、run-wide final verification、integration / closeout を一つの run として所有する。Model Construction は mandatory phase にしない。
<!-- @/contract -->

<!-- @contract impl-lead-authority-boundary -->
入力 Plan、request、established direction の outcome、Acceptance Criteria、scope、constraints、authority を input authority とし、run の上限にする。要求成果を成立させるために input authority 外の material work が必要なら、blocking authority gap として上流または Human へ返し、`stop-incomplete` とする。要求成果と独立した input authority 外の material finding は obligation へ昇格させず report-only incidental finding として保持し、run acceptance を阻止しない。
<!-- @/contract -->

`references/external-effects.md` が、implementation、verification、integration、cleanup を含む run 全体に適用する external Action の cross-cutting pre-action safety boundary と適用手順を所有する。親は各 Action に同 reference を適用し、実行 eligibility と result safety を裁定する。Git / worktree 固有の procedure は `references/run-owned-lifecycle.md`、post-diff specialized review は `references/risk-review.md` が所有する。

## Intake and Implementation Unit normalization

<!-- @contract impl-lead-intake-ownership -->
<!-- @anchor impl-lead-intake-ownership-relation -->
親は implementation work から意味上区別できる implementation outcome candidates と grounding を構成し、outcome candidate の抽出、implementation scope、要求 coverage の最終責任を保持する。
<!-- @/contract -->

<!-- @contract impl-lead-unit-data -->
Implementation Unit Data は invocation 内の transient Data であり、`id`、`purpose`、`acceptance_criteria`、`scope`、`implementation_freedom`、`constraints`、`depends_on`、`verification` の8 fieldを持つ。worker、reviewer、route、execution result、finding、QA result、persistence は execution Data であり Unit identity に含めない。

- `id`: run 内で Unit を識別する transient identity。
- `purpose`: 単一の outcome purpose。
- `acceptance_criteria`: 外部から観測可能で検証可能な受入候補条件であり、accept の確定結果ではない。
- `scope`: `change` と `exclude` からなる実装境界。
- `implementation_freedom`: Implementer に委ねる局所判断。
- `constraints`: Human 指定、互換性、依存、実行環境を含む established constraints。
- `depends_on`: Unit 間の semantic dependency と外部・repository・environment precondition を区別した記述。
- `verification`: Acceptance Criteria ごとの focused verification と必要な run-wide final gate。
<!-- @/contract -->

grounding には request / Plan / established direction、Acceptance Criteria の素材、scope / constraints、repository evidence、known dependency、verification reality、accept / rollback reality を含める。親は non-empty の initial outcome candidates を固定し、`references/implementation-unit-design.md` の `impl-lead implementation-unit-design v1` を load・検証して execution 前に exactly once 適用する。

<!-- @contract impl-lead-pre-execution-flow -->
<!-- @anchor impl-lead-pre-execution-flow-relation -->
### pre-execution-unit-design-control

Trigger: non-empty の initial outcome candidates と grounding が固定され、execution が未開始である。

Inputs: 固定済み target、Method path `references/implementation-unit-design.md`、expected identity `impl-lead implementation-unit-design v1`、execution-not-started evidence。

Procedure:

1. Method identity と required section を検証する。不足・不一致では judgment と execution を開始しない。
2. non-empty の initial outcome candidate 集合を、single / trivial を含めて execution 前に exactly once Method へ渡す。execution 後の再 invocation は作らない。
3. result の coverage、scope、blocking gap、Unit Data と execution Data の分離を親が確認する。
4. 各 candidate に run 内で一意の ID を付与し、返された semantic dependency をその ID に束縛する。

Outcomes: execution-ready な Unit 集合、または material reason を伴う `stop-incomplete`。

この Flow は split / merge、Unit boundary、semantic dependency、independent acceptability の意味判断を行わない。
<!-- @/contract -->

<!-- @contract impl-lead-return-integrity -->
<!-- @anchor impl-lead-return-integrity-relation -->
親は元の outcome candidates が暗黙に消えていないこと、要求 coverage、scope が拡張されていないこと、blocking gap がないことを確認し、Method の split / merge judgment を再設計しない。各 Unit に run 内で一意な `id` を付与し、Method が返した semantic dependency relation をその ID へ束縛する。
<!-- @/contract -->

## Run lifecycle

<!-- @contract impl-lead-isolation-selection -->
execution 前に integration target と selected isolation の repository / worktree identity、canonical path、base / current HEAD、tracked / untracked / ignored state、task path collision、ownership、single-writer 条件、integration / cleanup authority を確認する。Human の checkout / isolation constraint がある場合は、安全性を確認したうえでその指定を既定より優先する。指定された user-owned resource の作成、integration、cleanup は `impl-lead` の暗黙の所有範囲にせず、個別に与えられた authority の内側だけで扱う。Human の指定がない場合は `references/run-owned-lifecycle.md` の run-owned route を選ぶ。
<!-- @/contract -->

通常は Unit を dependency order で serial execution する。parallel implementation はこの workflow の policy に含めない。

各 Unit は次の順で閉じる。

1. `references/execution.md` により readiness、route、tier、context、Writable Scope、TDD、monitoring を確定して実装する。
2. `references/parent-qa.md` により mandatory Parent QA を行う。
3. concrete risk が判断を変え得る場合だけ `references/risk-review.md` により specialized review と correction を行う。
4. candidate commit を作り、`references/completion-gate.md` の mandatory Completion Gate を通す。
5. Parent QA と gate が Green の commit を Unit の accepted immutable baseline とする。

1 Unit は1 commitに対応する。accepted Unit を amend、reopen、renormalize しない。Unit acceptance は親が ownership、evidence、risk disposition、Completion Gate を裁定した時点でだけ成立する。

<!-- @contract impl-lead-final-verification -->
<!-- @anchor impl-lead-final-verification-relation -->
全 Unit の acceptance 後に run-wide final verification を実行する。全 accepted commit を含む selected execution tip を対象に、各 Unit の run-wide verification と repository-native required gate を実行する。結果は `passed`、`failed`、`not run`、`unverified` を区別し、external environment を利用できない結果は `unverified` とする。required gate が `failed`、`not run`、`unverified` のいずれかなら Green としない。親は累積 diff と commit range を一次情報として、accepted commit 全体で名称、comment、DocBlock、document の意味が相互に矛盾しないことを確認する。

accepted Unit は reopen、amend、renormalize しない。Final Correction Unit は run-wide final verification 後の bounded exception であり、Implementation Unit Design の軽量版ではない。次の8条件をすべて満たす場合だけ、親は Final Correction Unit を直接構成できる。

1. failure が一つの具体的な correction obligation に閉じている。
2. owner を一つの既存 accepted Unit に一意に帰属できる。
3. correction が input authority の内側にある。
4. owner Unit の purpose、Acceptance Criteria、responsibility boundary を変更しない。
5. owner Unit の既存 `scope.change` の内側だけで修正でき、`scope.exclude` に触れない。
6. owner Unit の semantic dependency、public contract、external effect、accept / rollback boundary を変更しない。
7. observable な correction postcondition に対応する focused verification と run-wide final verification を事前に確定できる。
8. split / merge、Unit boundary、semantic dependency、independent acceptability の再判断を必要としない。

Final Correction Unit の8 fieldは既存 boundary と failure evidence から一意に導出する。`id` は run 内一意、`purpose` は具体的な failure の局所解消、`acceptance_criteria` は failure observation の解消を証明する observable postcondition、`scope` は owner Unit の既存 `scope.change` 内、`implementation_freedom` は局所的な実装方法、`constraints` は owner Unit と input authority から継承する制約、`depends_on` は owner Unit への semantic dependency と全 accepted commit を含む selected execution tip の repository precondition、`verification` は確定済みの focused verification と run-wide final verification とする。Final Correction Unit 自体の accept / revert boundary は新しい correction commit とする。

Final Correction Unit は同じ run で1つだけ構成できる。fresh `focused-implementer` が新しい commit として実装し、Parent QA、必要な risk review、Completion Gate を通常どおり行う。accepted 後に run-wide final verification を再実行し、`passed` でなければ新しい Final Correction Unit を連鎖させず `stop-incomplete` とする。8条件の一つでも満たさない failure も `stop-incomplete` とする。
<!-- @/contract -->

final verification が Green の場合だけ、run-owned route では `references/run-owned-lifecycle.md` により integration と cleanup eligibility を別々に裁定し、Human 指定 route では明示された ownership / authority の内側だけで closeout する。external Action がある場合は `references/external-effects.md` を適用する。

## Completion and report

`accepted` は全 Unit accepted、run-wide final verification Green、要求された integration が確認済みで、必須 external Action が verified `実行済み` または Human により明示的に不要化され、blocking authority gap がない場合だけ返す。必須 external Action が `未実行` または `結果不明` なら evidence / retention state を保持して `stop-incomplete` とする。`stop-incomplete` となった run の accepted commits は selected execution ref に保持し、部分 integration しない。

conversation final report には Unit 状態、commit / branch / integration、Parent QA / verification、risk review disposition、Completion Gate、external effect state、final verification、residual risk、cleanup / retention、blocking authority gap、report-only incidental finding を記す。固定 ledger や persistent report schema は作らない。

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
