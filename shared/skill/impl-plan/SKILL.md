<!-- @only claude -->
---
name: impl-plan
description: >-
  明示起動時、与えられたプランの目的・範囲・設計意図を保ち、実装単位・担当・依存順序・検証を委譲文書へ具体化して終了する。
disable-model-invocation: true
---
<!-- @/only -->
<!-- @only codex -->
---
name: impl-plan
description: >-
  明示起動時、与えられたプランの目的・範囲・設計意図を保ち、実装単位・担当・依存順序・検証を委譲文書へ具体化して終了する。
---
<!-- @/only -->
<!-- @only cursor -->
---
name: impl-plan
description: >-
  明示起動時、与えられたプランの目的・範囲・設計意図を保ち、実装単位・担当・依存順序・検証を委譲文書へ具体化して終了する。
disable-model-invocation: true
---
<!-- @/only -->

# impl-plan

## 計画の責任

入力は元プラン、明示された制約・対象外・担当指定と、具体化に必要な repository・依存・検証環境の根拠である。
目的・範囲・設計意図を維持し、何を、誰が、どの順序で、どの条件まで実装するかを具体化する。
元プランの規模適否、再分割・縮小・拡張・改善を判断せず、全体規模と分担の最終採用は Human に残す。一単位・一担当で足りる場合も扱う。

根拠取得は具体化に必要な範囲に限る。元プランで未決の局所実装方法は担当の判断範囲へ明示するが、目的・受入条件・責務境界を変える未解決判断は担当へ丸投げしない。
意味を補わなければ具体化できない箇所は不足として示し、仮定を確定事項にしない。

## 実装単位の構成

元プラン上の対応と grounding から non-empty outcome candidates を構成し、`references/implementation-unit-design.md` を読む。
この Method が Unit boundary、split / merge、semantic dependency、independent acceptability を判断する唯一の正本である。
RMO の既存 semantics と loading contract を用い、モデル方式を独自に変更しない。impl-plan が要求 coverage、scope と不足を確認して ID を付与し、dependency をその ID に束縛する。

## Programmatic Flows

### unit-design-control

Trigger: 元プランと non-empty outcome candidates、grounding が確定し、Unit Design が未実施である。

Inputs: candidates、grounding、Method path `references/implementation-unit-design.md`、expected identity `impl-plan implementation-unit-design v1`。

Procedure:

1. Method identity と Identity and responsibility boundary、Inputs and outputs、RMO loading and mapping、Partition judgment、Uncertainty and return boundary の存在を確認する。不足・不一致なら Method を開始しない。
2. single / trivial を含む全候補を同じ計画作成内で一度 Method へ渡す。
3. candidates、判断理由、qualification、blocking gaps を受け取り caller へ返す。

Outcomes: caller による coverage / scope 確認を要する Unit candidates、または不足理由を伴う incomplete。

Flow の外で impl-plan が候補と元プランの対応を確認し、欠落・根拠のない追加を除く。blocking gap は隠さず文書へ残す。実行可能性が未確定なら ready と表現しない。

## Unit Data

<!-- @contract impl-plan-unit-data -->
Implementation Unit Data は 委譲文書と実行時に共有する意味 Data であり、`id`、`purpose`、`acceptance_criteria`、`scope`、`implementation_freedom`、`constraints`、`depends_on`、`verification` の8 fieldを持つ。worker、reviewer、route、execution result、finding、QA result、persistence は execution Data であり Unit identity に含めない。

- `id`: 文書内で Unit を識別し、実行時にも対応を保つ identity。
- `purpose`: 単一の outcome purpose。
- `acceptance_criteria`: 外部から観測可能で検証可能な受入候補条件であり、accept の確定結果ではない。
- `scope`: `change` と `exclude` からなる実装境界。
- `implementation_freedom`: Implementer に委ねる局所判断。
- `constraints`: Human 指定、互換性、依存、実行環境を含む established constraints。
- `depends_on`: Unit 間の semantic dependency と外部・repository・environment precondition を区別した記述。
- `verification`: Acceptance Criteria ごとの focused verification と必要な run-wide final gate。
<!-- @/contract -->

## 担当と実行計画

default は delegation である。責任境界と検証が狭く parent context から分離する利得がなく、delegation overhead が明白に上回る局所変更だけ direct execution を選べる。Human の route / model / agent constraint は優先する。

residual design judgment、reasoning difficulty、誤った場合の rework と他 branch への影響から `focused-implementer`、`implementer`、`senior-implementer`、`expert-implementer` を選ぶ。file 数、change size、迷いだけを tier 根拠にしない。通常の bounded Unit は `implementer`、狭く検証が明確なら `focused-implementer`、残存設計判断が多ければ `senior-implementer`、親の設計判断に依存する最高難度の局所実装だけ `expert-implementer` とする。senior / expert tier でも AC、Unit boundary、responsibility、semantic dependency の再設計を Implementer に補わせない。


担当、route、引き継ぐ context、実行順序・共有 surface の制約は Unit の意味 Data と分けて文書に示す。
依存順の直列実行を計画し、semantic dependency と同一 file 等の共有による実行制約を混同しない。
最初の実装と別 Unit・別責務・失効した前提・独立観測は fresh、同じ担当の同じ Unit 内の clarification / correction だけ continuation とする。
この文書は予定であり、実際の起動、現時点の担当・環境の可用性、Writable Scope assignment、authority は impl-lead が実行時に確認する。

## 委譲文書と停止

元プランの identity と対応箇所、各 Unit の8 field、担当・引継ぎ情報、依存順、先行成果・repository・環境の前提、共有 surface の制約、完了条件・検証方法を辿れる文書を返す。
全体規模と分担を Human が確認・変更できるよう理由を説明する。固定レイアウトや新しい永続台帳は要求しない。
`../../references/human-facing-projection.md` を適用し、意味保持を確認する。保存は明示された destination / write authority に従う。
文書を返して停止し、実装・実行管理・source / test / config の変更・公開を開始しない。Human が確認できる地点を作ることを毎回の固定承認手続きと混同しない。
文書の存在・名前・書式は実行許可でも有効性の証明でもない。impl-lead は実装依頼の authority と内容・前提を確認してこの計画を消費する。
