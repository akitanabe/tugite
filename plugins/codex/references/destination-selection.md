<!-- Generated from shared/. Do not edit directly. -->

# Destination selection

Destination selection identity: `destination-selection-v1`.

この reference は、観測した candidate facts を比較して destination を選定する reusable procedure である。
Kernel ではない。Kernel identity と Kernel injection mapping を持たない。

正本はこのファイルであり、各 platform の配布物では `references/destination-selection.md` として生成される。
caller は選定 procedure を複製しない。

## 責務境界

```text
caller / harness integration
  candidate facts + storage_requirement + optional requested_destination
  + optional caller_owned_predicates
shared destination-selection
  Flow: qualification / resume resolution
  Agentic: unique-best comparison（正本はこの reference 本文のみ。explicit 成功時は起動しない）
caller-specific operation
  plan-family → publication_target 組み立て + programmatic-publication
  wayfind → persistent read/write/reopen
```

所有しない: staging / atomic write / no-clobber / cleanup、filename / collision retry、persistent state schema / lifecycle、harness 具体 path、migration、candidate 比較の第二正本。discovery HOW と具体 path も持たない。汎用 adapter / registry / plugin framework を持たない。

## Inputs / Outputs

selector 入力は次に限る。

```text
storage_requirement.persistence = transient | persistent_reopenable
requested_destination?
runtime_candidates[]
caller_owned_predicates?
```

`caller_owned_predicates` は適用範囲付きである。candidate 全体への無差別適用ではない。
caller 固有 enum は shared contract に入れない。

出力: explicit 確定 destination、auto unique destination、incomplete、または resume の resolved / relocation-required。

`persistent_reopenable` 成功時のみ `reopen_locator` を返す。`reopen_locator` は同じ storage scope / state object を再解決できる情報である。物理 path 自体を永続正本にしない。

## Candidate facts

selector が要求する fact kinds:

```text
physical_destination
scope_identity
persistence_evidence
reopen_resolution_evidence
accessibility_evidence
ownership_evidence
containment_evidence
creation_capability
usage_evidence
git_ignored_index_evidence?
predicate-referenced observations
```

discovery 出力に資格判定結果、推奨、最良候補を field として持たせない。
selector は directory 名や harness から用途を推測しない。

`usage_evidence` は caller が観測した「この destination の既存用途が、当該呼び出しの保存用途に該当する」事実である。次は usage_evidence ではない: 欠如、ignored であることだけ、caller 用途と無関係な用途。

auto-select される project-local は usage_evidence が必要である。欠如は当該 candidate の unqualified。

## caller_owned_predicates の適用範囲

caller は predicates を適用範囲付きで渡す。selector は範囲内 candidate にだけ評価し、範囲外 candidate には適用せず unqualified にしない。

plan-family の Git ignored/index predicates:

- 適用する: project-local candidate、および canonical path が repository 内に入る OS-temp candidate
- 適用しない: repository 外の verified OS-temp（資格は temp-root identity / containment / non-follow / exclusive creation intent）
- 不合格は当該 candidate の unqualified。repository 外 OS-temp を Git unknown で落とさない

「無言 fallback 禁止」は、Human explicit 不合格時と tie 時に別 destination を選ばないことを指す。Git 欠格で残った unique remaining（repository 外 OS-temp）を選ぶことは fallback ではない。

## Programmatic Flows

以下は、親が意味判断を完了して確定 Data を渡した後の局所的な deterministic procedure だけを持つ。
Flow の procedure、条件、outcome は固定であり、Agent は override、bypass、置換しない。unique-best 比較は Flow に入れない。

### destination-qualification

Trigger: 親が storage_requirement、optional requested_destination、runtime candidate facts、optional 適用範囲付き caller_owned_predicates を確定したとき。
Inputs: storage_requirement, requested_destination?, runtime_candidates, caller_owned_predicates?
Procedure: 各 candidate を独立に qualify する。unknown containment / symlink follow / 現在 inaccessible / ownership 不明は unqualified。`transient` は verified OS-temp を qualify し得る。`persistent_reopenable` は ephemeral OS-temp を unqualified。reopenable は persistence_evidence AND stable_scope_identity AND repeatable_resolution AND current_accessibility。caller_owned_predicates は上記適用範囲の candidate にだけ評価する。範囲外 candidate には適用せず unqualified にしない。`requested_destination` がある場合: それが requirement / safety / その destination に適用される predicates を満たす → その destination を確定結果として返し、qualified set 比較へ進まない。他 candidate へ fallback しない。満たさない → 全体 incomplete。他 candidate へ fallback しない。`requested_destination` が無い場合のみ qualified set を出力する。unique comparison は Flow 内でしない。未指定時に directory / ignore rule を新設する candidate は作らない。creation_capability を新設指示に使わない。
Outcomes: explicit 確定、qualified set（未指定時）、explicit-destination incomplete、または入力不足 incomplete。

### reopen-resolution

Trigger: 親が既存 state の reopen_locator を確定し、resume を要求したとき。
Inputs: reopen_locator
Procedure: selector を再実行しない。compatible resolver で同一 state を解決する。失敗は relocation-required / incomplete。migration しない。
Outcomes: resolved destination、または relocation-required / incomplete。

## Agentic unique selection

起動条件: qualification が qualified set を返したとき（explicit 確定、explicit incomplete、入力不足 incomplete では起動しない）。

正本はこの destination-selection 本文である。publication および skill は比較 procedure を持たない。

比較軸: storage requirement satisfaction、scope affinity（caller の現在 scope との結びつき。category 名による固定順位ではない）、reopenability evidence strength（persistent 時）、ownership / safety confidence。

一意な best だけ選ぶ。同順位または比較不能は incomplete。OS-temp を同順位解消に使わない。qualified 0 は incomplete。

固定 category 順位（`project-local > harness-managed > user area`）は持たない。

意図する観測（auto-select のみ）:

- qualified が 1 件 → それを選ぶ。
- project-scope に結びつく usage_evidence 付き candidate が 1 件、かつ repository 外 OS-temp も qualified → scope affinity が一意なら前者を選ぶ。OS-temp は fallback ではない。
- qualified が repository 外 OS-temp のみ → OS-temp を選ぶ。これは unique remaining であり tie-break fallback ではない。
- usage_evidence 付き project-local が複数で比較不能 → incomplete。共存する OS-temp へ進めない。

## wayfind 接続（seam only）

wayfind skill / Map schema / 保存 path / harness 固定 path はこの reference の責務ではない。

seam:

- 初回 Map / Decision Unit canonical state 作成時に `persistent_reopenable` を渡す。
- 成功時の reopen_locator を再開情報にする。
- resume で selector を再実行しない。
- Git predicates は wayfind が付けない想定で共有できる。
- explicit reference 基本、一意なら Agent が解決、複数候補なら Human 選択、と矛盾する出力を selector は持たない。

## destination-reselection

`destination-reselection-required` を受けた caller は、selector の入力契約を維持する。

- 元が Human explicit なら、同じ requested_destination を保持する。unique-best auto-select へ落とさない。同じ destination を再 qualification できなければ incomplete。
- 元が auto unique-best なら、別 destination を無言で選ばない。必要なら同じ inputs で selector を明示再実行するか incomplete。

## 非所有範囲

この reference は write safety、filename / retry、persistent state lifecycle、harness 具体 path、relocation / migration、自動 root 新設を所有しない。未指定時に独自 `.tugite/` を新設しない。unique-best 比較を Flow 化しない。
