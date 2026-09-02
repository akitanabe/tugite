<!-- Generated from shared/. Do not edit directly. -->

# Verification Topology
## Identity and boundary

`Verification Topology` は、Behavior / Context candidate の grounding と semantic precedence を解決し、bounded な Case / Evidence facts との
意味的な対応を構成する consumer-neutral shared Method である。結果は `Behavior → Expected Observation ↔ Case → Evidence` の many-to-many relation であり、
test report、test design、quality evaluation、Reality verification のいずれにも固有ではない。

## Inputs

caller は、同じ task-local Local Model から次の Data を渡す。

- bounded observed scope、resolved / observed membership、その completeness basis
- Behavior candidate と、その意味に authority を持ち得る Context、provenance、source location
- Case / Evidence candidate、test / config facts、各 provenance と source location
- caller と Method の authority / responsibility boundary

この Method は repository / source / test / config を取得または読解せず、caller が準備した Data の意味的な対応だけを扱う。

## Provenance and precedence

各 Behavior candidate の provenance と適用範囲を検証し、対応を調べる Case / Evidence candidate から独立した Context だけを grounding に採用して Resolved Behavior を構成する。

対象 test 自身は discovery signal、Case、Evidence、scope fact にはできるが、その test と照合する Behavior、Expected Observation、
またはそれらの authority にはしない。

authority を持ち得る Context が複数ある場合は、この Method が provenance と適用範囲を確認して semantic precedence を最終解決する。

未解決の precedence が Behavior または Expected Observation を変え得る場合は silent merge や任意選択をせず、affected correspondence と grounding limitation を保持する。

test-only で独立 grounding できない candidate は Case / Evidence、source location、grounding limitation を保持し、Behavior、Expected Observation、
absence observation を発明しない。

## Expected Observation derivation

独立 grounding と precedence を解決した Behavior ごとに、Resolved Behavior、Relevant Authoritative Context、authority / responsibility boundary を
Behavior Model Observation（BMO）へ渡す。

BMO が返す Expected Observations、meaningful variations / conditions、各 grounding、
Collective Sufficiency、Relevant Unresolved Viewpoints、uncovered semantics を consumer Data に保持する。

BMO の一般 Method と result contract は `Behavior Model Observation` の正本に従い、ここでは複製しない。`Insufficient` / `Indeterminate` の
grounded 部分は qualified topology に利用できる。

partial model を complete な Expected Observation 集合として扱わず、unresolved / uncovered semantics から absence observation を作らない。

追加 authoritative Context によって意味が変わる場合は affected Behavior だけ BMO を再適用し、stale result を置換する。

## Topology construction

各 Behavior、Expected Observation、Case、Evidence を many-to-many の `Behavior → Expected Observation ↔ Case → Evidence` として対応づけ、
condition、grounding、source location を node と relation から追跡可能にする。

Case は semantic scenario、Evidence は observer が spot-check できる最小参照単位である。test function や file を常に一つの
Case / Evidence と同一視せず、property-based、snapshot、invariant、relation 等を closed taxonomy へ写さない。

Expected Observation ごとに、usable corresponding Evidence、correspondence 確定かつ statically non-executed、bounded observed scope 内で
no corresponding Evidence observed、correspondence unresolved、execution state indeterminate を区別する。

- correspondence が確定し、statically executable な Evidence が一つでもあれば usable とする。

- correspondence が確定し、対応 Evidence がすべて statically non-executed なら、その config fact と理由を保持する。

- correspondence または execution state を静的 Data から確定できない場合は unresolved / indeterminate とし、absence へ変換しない。

- absence は完全に観測した bounded scope、または Human が了承した実観測 scope にだけ相対化する。未読 member が残る scope では生成しない。

## Result and stop boundary

Topology、Behavior、Expected Observation、Case、Evidence、condition、grounding、source location、execution state、unresolved correspondence、
scope-relative absence、derivation / grounding / completeness limits を、caller が用途固有の成果物へ投影できる Data として返す。

結果を返したら停止する。この Method は scope resolution、source / test / config の read、test / CI / target code の実行、report projection、
quality / coverage verdict、severity、Reality verification、Problem 構成、remediation、planning、implementation、後続 Action を所有・開始しない。
