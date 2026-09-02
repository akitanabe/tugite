---
name: test-report
description: >-
  ユーザーが `test-report` を明示した場合、または指定範囲のテスト群の理解・把握を求める意図が明確な場合に使う。
  静的観測から Verification Topology を再構成し、実行・品質評価・remediation を行わず適応的に報告する。
---
<!-- Generated from shared/. Do not edit directly. -->

# test-report

`test-report` の明示指定、または bounded test scope のテスト群を理解・把握したいことが明確な request で開始します。

静的 evidence から Verification Topology を再構成する public Skill です。他 workflow の工程として自動起動しません。

## Ownership and inputs

入力は invocation request、利用可能な context、repository / source、test scope、requested report、明示された destination / write authority
です。path / directory の指定と機能・領域の自然言語指定を受け付けます。

一回の invocation に対して exactly one の task-local Local Model を所有し、scope resolution、static read、input preparation、static interpretation、report projection は同じ Local Model の bounded projection を利用します。

生成された Skill から参照する既存の正本は、各 platform の generated path を基準に解決します。

- `../../references/model-construction.md`
- `../../references/agentic-model-construction.md`
- `../../references/interactive-model-construction.md`
- `../../references/behavior-model-observation.md`
- `../../references/verification-topology.md`

## Model Construction route

Agentic Model Construction を first route とし、repository / source の静的観測、scope resolution、Behavior / Context candidate と provenance の acquisition scope を Agent-side で先に決めます。

Agent-side で bounded な分解・再観測を行っても material gap が残る場合、その gap が report の方向・範囲・意味を実質的に変えるか、
resolution source と authority を確認します。

残る material gap の fact、scope intent、authority、または部分観測で継続する判断が Human-owned の場合だけ、同じ Local Model のまま Interactive Model Construction を composition します。

Human-owned でない evidence limitation、取得不能な source、execution capability の不足、または単なる Agent の不確かさは Human への
質問で埋めず、current understanding、試した解消経路、limitation、qualification を返して停止します。

## Static scope observation

最初の Action は invocation request と repository / config の静的構造から、test scope candidate、対応し得る target-code unit candidate、
authority を持ち得る Context、runner / config evidence surface と各 source basis を取得します。この Action では candidate の採否を
決めず、test、source、CI を実行しません。

scope resolution Calculation は candidate Data から bounded test membership、対応する target-code units、Context candidate の acquisition / read scope、
必要な observation surface を決め、その根拠を resolved-scope Data として保持します。これは取得範囲の決定であり、Behavior grounding や
authority を持つ Context 間の semantic precedence の解決ではありません。

read Action は決定済み membership に従って全 member を静的に読み、resolved / observed test files、resolved / observed target-code units、
Context candidates、Case / Evidence / config facts、source locations を observation Data として返します。

completeness Calculation は resolved set と observed set の一覧差から判定し、resolved membership とその basis を report の traceability まで保持します。

除外済み candidate や Agent の relevance 自己申告を母集団にしません。未読 member がある場合は bounded decomposition と再観測を先に
試します。Human-owned decision による scope reduction、decomposition、または qualified continuation が成立した場合だけ、実際に観測した
scope に相対化して継続します。未読 member が残る間は absence observation を生成しません。

解決済み test scope が zero tests であることは有効な観測結果であり、scope 自体を解決できない結果と区別して報告します。

## Verification Topology Method mapping

Behavior candidate、authority を持ち得る Context、Case / Evidence / config facts、resolved / observed membership と completeness basis、各 provenance / source location を
consumer input として準備します。対象 test は discovery signal、Case、Evidence、scope fact としてだけ渡します。

acquisition scope 内で観測した Behavior / Context candidate は semantic authority の採否を決めず、provenance と適用範囲を失わずに渡します。

準備した consumer input を `Verification Topology` Method に渡し、返された Topology Data を同じ Local Model へ reintegrate します。

static interpretation は返された relation、state、limits、traceability を report の読者と requested scope に合わせて整理します。Method の grounding、
precedence、Expected Observation、correspondence、execution state、absence の意味は変更しません。BMO の内部分類は Human 向け report の中心語にせず、
Observation Limits と evidence traceability に投影します。

## Report boundary

test、target code、source、CI を実行せず、quality verdict、coverage verdict、severity、remediation、planning、implementation、後続 Action を開始しません。

observed scope、Topology、Behavior、Expected Observation、Case、Evidence、execution state、unresolved correspondence、scope-relative absence、BMO derivation limits を含む Observation Limits、source / config traceability を、request に適応した report へ投影します。

固定 heading、table、tree、report schema は要求しません。

明示された destination と write authority がある場合だけ report artifact をその範囲へ書きます。report のために source、test、config、無関係 artifact を変更しません。

既定では one-shot response を返します。

`visualize-that` その他の Skill は依存要件ではありません。

## Non-goals

- test execution、CI observation、runtime compliance の検証
- test quality / sufficiency / coverage の評価、改善提案、remediation
- fixed report tree、closed Case taxonomy、single-parent topology
- BMO / Model Construction の意味や result contract の複製
- RMO consumer、Reality verification、EVAL
