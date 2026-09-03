<!-- Generated from shared/. Do not edit directly. -->

# Destination Selection

## Purpose

`Destination Selection` は caller-neutral な shared Method として、caller/harness が観測した Data に対する `persistent_reopenable` destination の qualification と supplied resume reference / locator の same-state resolution result の deterministic 分岐だけを扱います。compatible resolver の実行や外部 state への接触は caller/harness の Action とし、この Method は実行しません。

## Programmatic Flow

### destination-selection-flow

Trigger: caller/harness が観測済み candidate facts または supplied resume resolution result を Destination Selection の deterministic branch へ渡せる。

Inputs: requested destination、runtime が観測した candidate facts（persistence、stable scope、repeatable resolution、current accessibility、ownership、containment evidence）、および supplied resume reference / locator に対する caller/harness-observed resolution result（resolved same-state identity / invalid / unavailable / unknown と evidence）。

Procedure:

1. supplied resume reference / locator がある場合、caller/harness が渡した resolution result を使い、Destination Selection は compatible resolver を実行せず、destination selector を再実行しない。

2. resolution result が resolved same-state identity ならそれを caller へ返す。invalid、unavailable、unknown なら reason と evidence を伴う `incomplete` を返し、relocation / migration をしない。

3. resume reference / locator がない場合、persistence、stable scope、repeatable resolution、current accessibility、ownership、containment evidence がすべて揃う candidate だけを qualified とする。

4. requested destination がある場合、その指定先が qualified ならそれだけを selected destination とし、不適格なら他の candidate へ silent fallback せず reason と evidence を伴う `incomplete` を caller へ返す。

5. requested destination がない場合、固定 category 順位や OS temp による tie-break をせず qualified set を caller へ返す。qualified set が1件ならその destination を確定し、0件なら `incomplete`、複数なら unresolved destination gap を caller へ返す。

Outcomes:

- selected destination、qualified set、unresolved destination gap、または reason と evidence を伴う `incomplete` を返す。

- resume resolution result は resolved same-state identity、invalid、unavailable、unknown と evidence の違いを保持して扱い、後三者は reason と evidence を伴う `incomplete` に投影する。

## State Ownership

compatible resolver の実行、外部 state への接触、resolution result の取得は caller/harness の Action とし、persistent state schema、state lifecycle、state write、retention / cleanup は caller-specific responsibility とする。Destination Selection は caller/harness が渡した resolution result Data を deterministic に分岐するだけで、これらを定義・所有・実行しない。

resume reference は caller が次 invocation の input として保持できる same-state identity の Data です。Destination Selection は state object の serialize、保存、read-back、または complete 後の physical persistence を行いません。
