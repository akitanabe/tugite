---
name: implementation-unit-design
description: >-
  impl-lead の同じ親 context 内だけで、関連成果候補群を受け入れ可能な Implementation Unit 集合へ正規化する internal skill。
user-invocable: false
---
<!-- Generated from shared/. Do not edit directly. -->

# implementation-unit-design

## 位置づけと発火

この Skill は新しい worker を起動するものではなく、呼び出し元の親が同じ context で従う判断手順書である。
ユーザーの直接要求、通常会話、`plan-agent` から暗黙に設計を始めず、`impl-lead` が選定した non-empty normalization target（単一候補を含む）を受け付ける工程としてだけ使う。正式な Implementation Unit normalization の入口は `impl-lead` だけであり、この Skill
自身は要求全体から成果を決めず、実装・委譲・後続工程を開始しない。normalization target が空のときは起動せず、raw request から成果候補を再抽出しない。

runtime で Skill 間起動が提供されない場合、親はこの本文を工程として直接参照する。発火条件、入力、
候補の裁定、blocking の扱い、採用・実行・保存を親が持つという責務は変えない。

## 入力と出力

親から、`normalization candidates`、grounding、invocation 固有の `partition_perspectives` の組を入力として受け取る。

- `impl-lead` が選定した non-empty normalization target。単一候補を含み、相互に境界判断が影響する関連成果候補群に限らない。
- grounding としての要求原文、AC の素材、constraints、既知の依存、repository の現状と既存調査。再正規化では
  既存 Implementation Unit 集合、accepted 状況、worker 返却も含む。
- invocation ごとに親が注入する `partition_perspectives`。これは確認順序と attention priority を示す transient execution Data であり、観点外の既存原則・全入力・既存 signal・candidate facts を取り除かない。

成果候補は意味上区別できる到達結果についての transient observation であり、この Skill の固定 input schema、必須 ID、
Implementation Unit Data field、provenance field、永続 artifact にしない。raw request を起点に成果候補を再抽出しない。

出力は会話内 execution data の候補であり、`implementation_units`、各単位の分割／統合 signal と理由・残存判断密度等の観測、
`blocking_gaps` で構成する。`blocking_gaps` は、与えられた関連成果候補群を安全に Implementation Unit 集合へ正規化できない不足、
矛盾、閉じていない scope に限定する。成果候補不足、要求解釈、run-wide coverage の問題を観測しても自身で修復せず、
既存の signal と理由により `impl-lead` へ返す。

`partition_perspectives` は invocation ごとの transient execution Data であり、用途名、split / merge の答え、Implementation Unit Data の field、出力 field、永続 ledger ではない。

`partition_perspectives` は確認順序と attention priority のみを与える。観点外の既存原則、全入力、既存 signal、candidate facts を維持し、観点で無効化または置換せず、固定 mode、threshold、solver、expected-output oracle を作らない。split / merge / absorb の最終判断はこの Skill が行い、partition_perspectives の優先度を答えや branch にしない。

remediation candidate は、同じ origin verified snapshot に束縛された親裁定済み selected finding obligation として入力でき、identity、obligation、AC、mutation oracle、disposition、既存 context を保持する。元の Skill 数や Implementation Unit 数を partition の根拠にしない。

入力された obligation と context は Implementation Unit Data の field や永続 artifact に昇格させない。
各 `implementation_units` 要素は、`impl-lead` の `Intake and Implementation Unit normalization` が定める canonical Implementation Unit Data に適合させる。field の意味や一覧はここで再定義しない。

`worker`、`base_snapshot`、`isolation`、route、order、実行結果、review、保存先、
後続 Skill の起動権限を出力へ含めない。
候補の採用、再検査、accept／stop-incomplete、委譲、実行、保存は必ず受け取り側の親が判断する。

## reality-model-observation-kernel v1 の parent mapping

caller context 成立後、boundary reasoning 直前に各 invocation 一度 load する。次の Loader Data が列挙値の唯一の正本である。

```text
path = ../../references/reality-model-observation-kernel.md
load_timing = after caller context is established and immediately before boundary reasoning
identity = reality-model-observation-kernel-v1
required_sections = [Contract, Observable Reality Model, Method, Reintegration, Target Membership Check, Consumer Responsibilities, Non-goals]
failure = blocking_gaps
owner = implementation-unit-design parent
delegate_path_resolution = false
```

loader / identity / required-section の不足・不一致では reasoning を開始せず、既存 `blocking_gaps` へ返す。これは Reality evidence の Uncertainty と区別する。推測で継続しない。

Target は、入力 normalization target が示す Implementation Unit boundary / semantic dependency / independent acceptability の実在関係とする。複数候補では candidate 間 relation を扱う。単一候補では、その提案 boundary が単一の independently acceptable outcome を囲むか、入力 candidate と authoritative context に既に現れる複数 purpose / AC / verification / accept-rollback boundary を隠しているかを扱う。raw request から別候補を再抽出しない。要求全体、solution design、Task Specification 自体を Target にしない。

authoritative context は request、repository contract / evidence、AC / verification reality、accept / rollback reality、dependency evidence、accepted state とする。authority / precedence が未解決なら一方を推測採用せず Uncertainty とする。安全な normalization を阻害するときだけ `blocking_gaps` で caller へ返す。

Target-relative Problem / constraint は既存 split / merge / dependency reasoning の grounded evidence とする。Incidental Finding は Unit / obligation へ昇格させない。Uncertainty は上記 bounded mapping に従う。RMO result を split / merge / dependency verdict または `blocking_gaps` へ直接変換せず、既存 semantics が判断する。new grounded evidence で Problem Derivation 前の derivation が無効になった場合だけ Reintegration する。Problem Derivation 後は STOP し、partition verdict を持たない。

RMO grounding trace は新 schema なしで既存 output へ保持する。split / merge / dependency の各 signal・reason・observation に、Target、authoritative evidence、observation / inference、discrepancy、mismatch attribution、membership、Model Sufficiency と Observed Evidence Sufficiency を区別可能に残す。Target-relative / Incidental / non-blocking Uncertainty も observation へ trace し、blocking Uncertainty だけを `blocking_gaps` へ、何が未確定か・必要 evidence とともに写す。`implementation_units` の field は増やさない。

## 判断の進め方

1. 関連成果候補群を grounding と照合し、各候補の purpose、AC、責任境界、依存、検証、accept と rollback の境界を確認する。
   新しい成果を発明せず、候補を暗黙に削除せず、意味を再定義しない。既存 Implementation Unit がある場合は accepted 状況、部分成果、
   worker の返却を現在の観測として扱う。
2. 各候補について「新しい Implementer がこの単位だけを読み、AC・責任境界・依存・分割を再定義せず、受け入れ候補の
   diff を返せるか」を判定する。否定ならその不足と影響を `blocking_gaps` に記録する。
3. 一つの候補内に独立した purpose、AC、verification、accept と rollback の境界が複数ある場合は split する。foundation は
   独立 capability または contract、単独 AC、単独 verification、accept boundary を持つ場合だけ単独化し、それ以外の共通依存は
   最初に振る舞い価値を生む単位が所有する。
4. merge / absorb の直前に一度だけ、分離維持では成立しない具体的 evidence を contrastive に確認する。具体的 evidence があり、同じ受入境界でしか Green / accept / revert が成立しない場合だけ lossy merge / absorb を選べる。evidence のない lossy merge は選ばず、正当な merge はこれで禁止しない。独立 purpose、accepted dependency 上の focused Green、単独 accept / revert、Implementer readiness が成立する候補は、shared file / generator / contract / generated surface / full gate / run-wide invariant / worker capability の共有だけでは消さない。
5. 同じ検証でしか成立しない候補、片方だけでは invariant が成立しない候補、または handoff が内部結合より複雑な候補を
   merge する。再正規化では統合、追加分割、部分成果の独立した再構成、依存 edge の再接続を候補として示す。
6. canonical `depends_on` definition を各候補に適用して semantic dependency を設計し、execution conflict で代替しない。
7. 返却前に既存 signal を使い、明らかな under-split、単独 Green／accept できない over-split、必要な semantic dependency の
   欠落を自己再検査する。安全に正規化できない理由は `blocking_gaps` にし、実行順、isolation、worker、dispatch で補わない。

## 分割を検討する signal

分割 signal は次の 7 項目であり、分割の根拠として個別に観測し、該当理由を候補に添える。

1. 独立した accept 目的が複数ある。
2. 先行単位の学習結果で後続の設計が変わる。
3. 複数の外部副作用、または異なる rollback 境界がある。
4. 検証方法または受入判断が異なる。
5. 旧仕様との parity と新規挙動が混在する。
6. Implementer が AC、責任境界、依存を再設計しないと着手できない。
7. 残す設計・推論判断が多すぎ、単位だけを読んでも受け入れ候補 diff を返せない。

## 過分割を示す signal

過分割 signal は次の 5 項目であり、該当すれば候補を統合する。

1. 同じ test でしか Green／invariant を確認できない。
2. 一方だけでは Green にならない、または invariant が成立しない。
3. 一方だけで accept／revert できない。
4. architecture layer の名前だけで横割りしている。
5. unit 間 handoff が統合内部の結合より複雑である。

単位化の非根拠は二つの軸に分けて記録する。

- 構造・工程の軸: file 数、行数、architecture layer、実装工程だけでは単位を決めない。
- 規模・接続の軸: file 数、行数、枝数、database を触るかどうかだけでは分割しない。

layer 固有の要求が独立検証できる場合だけ、結果として 1 unit を認める。判断密度、責任境界、観測可能な価値、依存、rollback、
検証を根拠にする。

## Relation-based Casebook

Casebook は relation を再確認するための invocation 内の判断補助であり、canonical Implementation Unit の正本や exact Implementation Unit 数の oracle ではない。

Relation-based Casebook は #249 initial over-merge、#210 kernel / caller、#249 remediation over-split を、input facts → forbidden shortcut → preserved relation → valid control の関係として扱う。Phase 2a の Shared Surface ≠ Semantic Dependency、Hidden Semantic Dependency、False Independent Verification、Foundation / Application、Incidental Repository Finding、および cardinality-one control を、input facts → authoritative reality → forbidden shortcut → preserved relation / valid control の関係として扱う。exact Implementation Unit 数を oracle にせず、新しい正本にも、canonical output や impl-lead 親の採否・coverage・ID・dispatch・accept 責務の代替にもならない。fixed Unit 数または outcome oracle は置かない。

- #249 initial over-merge: input facts は independent outcomes / AC / focused verification / accept-rollback と shared surfaces。forbidden shortcut は shared surfaces / run-wide gate だけで merge すること。preserved relation は independent acceptability と dependency / conflict の分離。valid control は本当に同じ受入境界でしか Green にならない候補の merge を許すこと。
- #210 kernel / caller: input facts は kernel foundation と proposal/review consumers、shared generator/registry。forbidden shortcut は shared surface だけで統合すること。preserved relation は foundation capability と consumer 別 AC / verification / rollback、および dependency。valid control は foundation が単独 capability / contract を持たなければ最初に価値を生む application が所有できること。
- #249 remediation over-split: input facts は同一 verified snapshot、同じ横断 invariant、親裁定済み findings。forbidden shortcut は元 Skill / Implementation Unit 境界の機械継承または一括のための identity collapse。preserved relation は coherent apply と finding identity / obligation / AC / mutation oracle / disposition。valid control は authority / external side effect / intermediate snapshot / failure isolation / independent promotion が異なる場合の split。
- Shared Surface ≠ Semantic Dependency: input facts は独立した AC / focused verification / accept-rollback と共有 file / generator / registry / generated output / verification surface。authoritative reality は independent acceptability と execution conflict。forbidden shortcut は shared surface だけで merge すること。preserved relation は Shared Surface ≠ Semantic Dependency。valid control は本当に同じ受入境界でしか Green にならない候補の merge を許すこと。
- Hidden Semantic Dependency: input facts は file / layer / test surface の見た目の分離と、B が A の capability / invariant なしでは Green / accept できない関係。authoritative reality は実在する semantic dependency。forbidden shortcut は見た目の分離だけで false split すること。preserved relation は Hidden Semantic Dependency。valid control は RMO が split bias を作らず、独立して成立する候補の split を許すこと。
- False Independent Verification: input facts は別 test の存在と、同一 invariant / shared state への依存。authoritative reality は一方だけでは成立しない independent Green / acceptability。forbidden shortcut は test が別という surface fact だけで independent Unit とすること。preserved relation は False Independent Verification。valid control は本当に独立した focused verification が成立する候補の分離を許すこと。
- Foundation / Application: input facts は foundation capability と application consumer、単独 contract / AC / verification / accept boundary の有無。authoritative reality は repository 上で独立成果として実在するか否か。forbidden shortcut は foundation を常に独立 Unit にすること、または常に application へ吸収すること。preserved relation は Foundation / Application の独立 boundary の有無。valid control は foundation が単独 capability / contract を持たなければ最初に価値を生む application が所有できること。
- Incidental Repository Finding: input facts は boundary 調査中に見つかる、candidate outcomes の boundary / dependency / acceptability に影響しない別箇所の repository problem。authoritative reality は current Target 外であること。forbidden shortcut は Incidental Finding を新 Unit / current obligation に昇格すること。preserved relation は Incidental Finding を obligation 化しないこと。valid control は Target-relative な repository defect を既存 semantics の grounded evidence として扱うこと。
- cardinality-one: input facts は単一の入力候補。authoritative reality は、提案 boundary が単一の independently acceptable outcome を囲むか、入力 candidate と authoritative context に既に現れる複数 purpose / AC / verification / accept-rollback boundary を隠しているか。forbidden shortcut は単一候補だから grounding せず通過すること、または単一 outcome なのに split すること。preserved relation は cardinality-one の Target が boundary / semantic dependency / independent acceptability に限定されること。valid control は単一 outcome なら不要 split しないこと。

common Observation Points は invocation 内の判断補助であり、schema や outward field にはしない。

- `before`: RMO 適用前の shortcut / abstract reasoning
- `observation`: authoritative reality / discrepancy / constraint
- `after`: split / merge / dependency reasoning の変化
- `boundary`: RMO 自身が partition verdict を出していないこと、Incidental Finding を obligation 化していないこと、unnecessary detail expansion が増えていないこと

## 親への返却境界

この Skill は候補と観測を返して終了する。直接起動を促さず、正式な normalization と実装の入口として `impl-lead` を案内する。
ユーザーの通常要求や `plan-agent` の自由形式成果物を正式な Implementation Unit Data へ変換しない。候補を採用したか、run-wide requirement
coverage と primary owner を確定したか、親が再検査したか、実装・委譲・worker 起動を実行したか、AC を確定したか、結果を保存したかを
主張しない。execution conflict、order、isolation、base_snapshot、worker selection、dispatch、final accept は `impl-lead` 親へ残す。
不足が解消されない場合は影響と必要な観測を `blocking_gaps` に残し、親が確認または stop-incomplete を選べるようにする。
