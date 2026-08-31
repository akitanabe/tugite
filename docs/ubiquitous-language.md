# Tugite ユビキタス言語

Tugite の Skill、Agent、Issue、実装で同じ語を同じ意味で使うための辞書です。各語の規範は正本にあり、この辞書は
定義と正本の所在だけを示します。正本の項目一覧をここへ写すと、正本より狭い定義が第二の source of truth として
固定されるため、項目の列挙は載せません。

## Contract

システムが機械的に検証する構造・不変条件です。`contracts/*.toml` に text/structure contract として宣言し、
`gunte check` が生成物に対して検証します。Skill と Agent の定義そのものを対象とする definition-time の保証であり、
内容の妥当性は判断しません。

- 正本: `contracts/*.toml`（選択順は `gunte.toml` の `[contracts].files`）
- 契約 ID の規約と運用: `AGENTS.md`

## Task Specification

Task または Implementation Unit が何を達成すべきかを、LLM が意味的に解釈するための定義です。具体的な
acceptance boundary は current request と current workflow source が所有します。この辞書は general admission
checker ではありません。issue #193 は略記 `Task Spec` も候補に挙げていますが、正本本文と `contracts/*.toml` の
pattern では正式名だけを使います。

- 正本: current request と、適用中の workflow source

## Implementation Unit

親エージェントが要求を正規化し、worker へ委譲する実装単位です。単位が持つ情報の構成は正本が定めます。

- 正本: `shared/skill/impl-lead/SKILL.md` の `Intake and Implementation Unit normalization`

## Programmatic Flow

Agentic workflow 内の局所的な deterministic procedure です。共通の意味と境界は
`AGENTS.md` の `Programmability Boundary contract`、個別の procedure は各 Skill の
`Programmatic Flows` sectionを、共有 publication procedure は `shared/plan-artifact-publication.md` を正本とします。

## Resolution Point

caller が Resolution Transaction で裁定対象として供給する個々の論点です。

- 正本: `shared/batch-resolve-kernel.md` の `## Resolution の語彙`

## Resolution Batch

一つの origin verified snapshot に束縛され、Resolution Transaction 開始時までに観測済みである Resolution Point の
固定集合です。

- 正本: `shared/batch-resolve-kernel.md` の `## Resolution の語彙`

## Resolution Transaction

一つの Resolution Batch を adjudication から verified snapshot promotion または caller boundary への返却まで扱う規範上の
実行単位です。

- 正本: `shared/batch-resolve-kernel.md` の `## Resolution の語彙`

## 3 者の関係

`Task Specification` は、Implementation Unit が何を達成すべきかを意味的に定める側面を指します。LLM が解釈する対象です。

`Contract` はこれとは別の軸にあり、Skill と Agent の定義に対する機械検証です。`Task Specification` の上位でも
下位でもありません。

意味の判断は LLM が行い、境界の保証は Contract が行う、という分担になります。

## 命名の経緯

`Task Specification` は issue #193 以前は `Task Contract` と呼んでいました。`Contract` が機械検証される不変条件を
指す語として既に定着していたため、意味の異なる 2 つの概念が同じ語を共有していました。issue #193 でこの衝突を解消し、
`Contract` の意味を維持したうえで、意味的な受入境界を指す側を `Task Specification` へ改名しました。`Task Contract`
は廃止された語であり、新しい記述では使いません。
