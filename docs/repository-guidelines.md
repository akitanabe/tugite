<!-- Generated from shared/. Do not edit directly. -->

# Repository Guidelines

## プロジェクト構成

Tugite は Claude Code、Codex、Cursor 向けの agent・skill 定義を配布します。正本は `shared/` で、skill は
`shared/skill/`、agent は `shared/agents/` に置きます。Gunte の project 設定は `gunte.toml`、決定論的な契約 registry は
`contracts/*.toml`、platform manifest と platform 固有 metadata の宣言は `declarations/` が正本です。配布物は
`plugins/` に生成され、原稿は日本語で書かれています。自動テストは `tests/` にあります。

## ビルド・テスト・開発コマンド

- `gunte emit`: `gunte.toml` の `sources.files` から Gunte 管理対象を生成します。
- `gunte lock`: 全 source、contract、declaration の検証後に lock を更新します。
- `gunte check`: Gunte 管理対象の byte drift と契約違反を確認します。
- `bash tests/install-agents-test.sh`: Codex custom-agent installer と agent inventory を検証します。
- `git diff --check`: 提出前に空白エラーを検出します。

実装の最後には、変更した対象ファイルに対する適切な lint（Skill 文書などでは `npm run lint:skills -- <対象ファイル>`）を実行し、
Gunte 管理対象の整合性を `gunte check` で確認します。

Gunte は [Gunte Releases](https://github.com/akitanabe/gunte/releases/latest) から release binary を取得して導入します。導入後は `gunte check` で確認します。生成物を伴う変更では、repository root で `gunte emit`、`gunte lock`、target/full `gunte check`、installer、diff check の順に実行します。

## Gunte の運用

`gunte.toml` は project、source、target、出力 rule、platform terms と managed inventory を定義し、`contracts/*.toml` は
text/structure contract を定義します。Gunte は `sources.files` に列挙した agent、manifest、version、workflow skill、
platform 固有 metadata を管理します。Codex skill metadata は `declarations/codex/skills/` に置きます。platform 差分は
正本内の `@only claude` / `@only codex` / `@only cursor` marker で表現し、`plugins/` 以下の生成物を直接編集しません。

契約は生成物または source frontmatter から決定論的に観測できる不変条件に限定します。未登録 source、unknown/stale
declaration、必須 path、retired path、metadata policy は `gunte check` で保護します。Gunte の生成、projection、
serialization、byte drift は `gunte check` に任せます。LLM の判断品質や読みやすさは、計画および実装の既定
verification にせず、残存 risk または editorial review として扱います。

`slice` を持つ契約の ID は `<意味を表す prefix>-<12桁 hash>` とします。hash は `kind`、`slice`、`pattern`、
宣言順の `applies_to` を固定 key 順の compact canonical JSON と LF にし、UTF-8 byte 列の SHA-256 先頭12桁で表します。
列挙順の連番は使いません。`slice` を持たない単独の契約には、意味を表す安定した ID を使用できます。

## 開発時のコーディングルール

Skill、shared component、contract、test、lint rule を作成・変更するときは、
`docs/skill-coding-rules.md` を正本として適用します。規範本文を `AGENTS.md`、contract、lint rule へ複製しません。

platform 差分は `gunte.toml` の terms または明示的な `@only` marker で表現します。

`SKILL.md`、または Programmatic Flow を含む Skill-local reference Markdown を作成・変更した場合は、対象ファイルを明示して `lint:skills` を実行します。

```text
npm ci
npm run lint:skills -- path/to/SKILL.md path/to/references/flow.md
```

`lint:skills` は共通 `skill-lint` rule と Tugite 専用 Programmatic Flow rule で機械判定可能なリスクを検出する補助層であり、shared component、contract、test の保証や、
repository-wide な lint の成功を意味しません。変更していない既存 artifact の lint finding は、明示的に要求されない限り変更 scope へ取り込みません。

Python は4空白インデント、型ヒント、`pathlib.Path`、説明的な `snake_case` 名を使用します。Bash は既存スタイルに
従い、変数展開を引用符で囲みます。skill directory と agent file は小文字の kebab-case で命名します。原稿を複製しません。

## 追加・変更時に触れる場所

agent を追加・削除するときは `shared/agents/` の正本、Gunte の `sources.files`、repository contract、installer の
agent inventory を同じ変更で更新します。`code-review` の SKILL.md は対象 reviewer の名前集合を持つため、reviewer
agent の追加・削除時は同じ変更でこの skill も更新します。skill を追加・削除するときは通常、`shared/skill/<name>/SKILL.md`、対応する
declarations、Gunte の `sources.files`、managed inventory を更新し、target rule は出力 path、profile、shape が
変わる場合だけ更新します。生成後は installer test で runtime inventory も確認します。

## workflow と agent の surface

現行の public workflow skill は `how-it`（Human と進め方を構築して requested output へ接続）、`explorer-this`（Agentic-first の探索を requested output へ接続）、
`impl-lead`（Implementation Unit normalization から実装、Parent QA、受入、final verification、安全な integration / closeout まで）、`plan-agent`（normal context から自由形式の planning / design artifact を作り、実装を開始しない計画成果物）、
`wayfind`（Destination 全体の Planning Fog と Decision blocker を self-contained な Work Units へ解像する pre-planning workflow）、`test-report`（静的観測から Verification Topology を再構成する非評価 report）、`test-verify`（grounded runtime evidence により bounded test target を検証・因果修復する明示起動 workflow）、`review-refine`（不変 snapshot に対する bounded review）の8つです。Implementation Unit Design は `impl-lead` 配下の consumer-specific Method です。
agent の正本は `shared/agents/`、各 runtime の exact inventory は repository contract で確認し、Codex custom-agent installer の inventory は installer test でも確認します。

## テスト指針

Red、Green、Refactor の順で進めます。Python test を追加する場合は `unittest` を使い、実装詳細ではなく観測可能な
CLI の振る舞いを記述します。repository の inventory、frontmatter、declaration scalar、retired path は Gunte contract で確認し、
生成、projection、serialization、byte drift を別のテストで再実装しません。関連する振る舞いと失敗経路を保護し、
数値による coverage 基準は設けません。

TDDを通すことだけを目的として、契約の意味的な改変を一時コピーへ適用し `gunte emit` の拒否を確認する個別の契約 mutation test ファイル（例: `tests/*-contract-test.sh`）を作成・コミットしてはなりません。契約の保証は `contracts/` と Gunte の標準検証に委ねます。
契約で保証すべき不変条件には Gunte contract を必須とし、正本・生成物から決定論的に観測できる不変条件を個別テストで代替してはなりません。

計画成果物の既定 verification は、この repository で実行できる native 手段に限り、EVAL を含めない。
Gunte が保証しない点は残存 risk / 未検証とし、受け入れを EVAL 実行に依存させない。
EVAL は Human が明示したとき、または既存 EVAL 成果物の変更自体が要求対象のときだけ使う。

## Version 更新指針

v6 以降の version は個々の change ではなく release snapshot の属性です。通常の change、PR、main 統合では
`shared/VERSION` を更新しません。Human が release を明示した場合だけ、恒久正本の
`docs/version-release-policy.md` を読み、release Action を開始します。

```toml
policy_id = "version-release-policy-v1"
applies_from = "v6.0.0"
ordinary_change = "通常の change、PR、main 統合では shared/VERSION を更新しない"
release_trigger = "Human が release を明示した場合だけ release Action を開始する"
canonical_policy = "docs/version-release-policy.md"
```

## Commit・Pull Request 指針

コミットメッセージは変更理由を表す簡潔な日本語件名にします。必要に応じて `feat:`、`test:`、`docs:` などの prefix を
使い、本文では変更が必要な理由を説明します。Pull Request には目的、変更範囲、関連 Issue、検証コマンドと結果を記載し、
生成物や version の変更を明示します。無関係な変更を含めません。

## 変更報告

完了時には変更内容、実行した検証と結果、未検証事項または残存 risk を簡潔に報告します。無関係な dirty state や
untracked artifact は保持します。

## Programmability Boundary contract

横断的な workflow rule は、明示入力から結果が一意に決まる deterministic side と、複数の受容可能な結果から
意味や価値を判断する autonomous side に分けます。次の stable Data は分類と保証の選択境界を定めます。

```toml
policy_id = "programmability-boundary-v1"
classifications = ["deterministic-mechanized", "deterministic-contract-only", "autonomous", "derived-duplicate"]
rule_source = "current workflow source owns meaning; point-in-time audit is evidence only"
programmable_assurance_planes = ["runtime mechanism", "ordinary test", "Gunte predicate/contract", "natural-language Contract"]
implementation_policy = "programmable does not imply immediate mechanization"
autonomous_oracle_policy = "do not fix one acceptable autonomous outcome as the expected-output oracle"
gunte_assurance_limit = "policy identity, required fields, and coherent relation only; not runtime semantic compliance or oracle absence"
programmatic_flow = "local deterministic procedure inside an Agentic workflow"
programmatic_flow_fields = ["Trigger", "Inputs", "Procedure", "Outcomes"]
programmatic_flow_discretion = "fixed procedure, decision conditions, and outcomes; agent override, bypass, or replacement prohibited"
programmatic_flow_return = "after Outcomes, return semantic judgment to the Agentic workflow when multiple acceptable actions remain"
programmatic_flow_non_goals = ["single invariant/prohibition/validation need not become a Flow", "autonomous judgment must not enter a Flow"]
programmatic_flow_skills = ["impl-lead", "plan-agent", "plan-candidate-producer", "review-refine", "test-verify", "wayfind"]
programmatic_flow_excluded_skills = ["code-review", "structural-health-gate", "test-report"]
sole_source_policy = "one deterministic procedure has one canonical witness; Flow pointers do not duplicate procedure text"
```

deterministic rule は意味の正本と assurance plane を明確にし、未機械化なら owner Action、必要入力、利用可能な
interception point、現在の非機械保証理由、延期または不能の理由、自然言語の正本を維持します。programmable で
あることは即時の機械化義務を意味しません。direct / delegate、worker / reviewer の選択、finding の意味的な採否、
実装 approach、risk 評価など autonomous side の特定結果を expected-output oracle で唯一の正解に固定しません。
必要な反復は consumer と、重複を除いた後も obligation を担う remaining witness を追跡し、独立した意味の正本にしません。
Gunte predicate の成功が保証するのは policy identity、required fields、その coherent relation までです。runtime の意味遵守や
autonomous outcome oracle の不存在を保証したとは扱いません。

## Test QA baseline contract

この section は、実装の入口や reviewer の有無に依存しない親 QA の共通下限を定義します。次の stable Data がこの
section の判断基準であり、Gunte の URL は provenance の参照だけに使います。
`test_artifacts` は適用対象、`qa_inputs` は全 route/reviewer variant で固定する判断 packet、`common_evidence` は input
variant 内で固定する evidence identity と、全 input variant に共通する parent oracle を表します。

```toml
policy_id = "test-qa-baseline-v1"
test_artifacts = ["automated test", "Gunte predicate/contract", "fixture/oracle", "EVAL"]
qa_inputs = ["Task Spec", "base", "acceptance criteria", "diff", "evidence", "surrounding context"]
common_evidence = ["evidence identity is fixed within each input variant", "parent oracle is common across input variants"]
owner = "parent QA"
routes = ["impl-lead", "non-impl-lead"]
baseline_self_qa = "required on every route"
reviewer = "optional additional observation"
reviewer_handoff = "pass baseline and reason in existing context; parent adjudicates findings"
parent_responsibility = "obligation, oracle, validation plane, final adjudication"
reviewer_scope = "changed mutation, structural test, EVAL case quality only"
gunte_antipattern_url = "https://github.com/akitanabe/gunte/blob/main/docs/gunte-antipatterns.md"
gunte_antipattern_url_use = "provenance only; runtime retrieval is not required"
minimum_checks = [
  "obligation/oracle owner = parent QA",
  "appropriate validation plane is explicit",
  "do not infer semantics from prose layout",
  "reject empty or overbroad slice, decoy, custom parser, and duplicate Gunte guarantee",
  "applicable mutation evidence is present",
]
accept_prohibition = [
  "reviewer Pass is never an accept basis",
  "reviewer observation is additive and never replaces baseline self-QA",
  "missing evidence prohibits accept",
]
```

全 route で親が `qa_inputs` の `Task Spec`、`base`、`acceptance criteria`、`diff`、`evidence`、`surrounding context` と
`common_evidence` の input-variant identity / common parent oracle を固定し、baseline self-QA を実行してから受入を裁定します。適用対象の
`test_artifacts` は automated test、Gunte predicate/contract、fixture/oracle、EVAL であり、qa input と混同しません。
EVAL を test_artifact に含むことは、計画へ EVAL corpus を追加する既定義務ではありません。
reviewer を使う場合も baseline と起動理由を既存の確認観点・周辺
context と一緒に渡し、reviewer は追加観測だけを返します。`obligation`、`oracle`、`validation plane` の責任と最終
adjudication は親に残し、`test-quality-reviewer` は既存 scope 内の changed mutation、structural test、EVAL case の
品質だけを見ます。baseline 不適用の failure を再現できない限り、`test-quality-reviewer` の原稿・contracts は変更しません。
reviewer の Pass、Gunte check の結果、または文章の配置そのものを受入根拠にせず、applicable mutation
evidence を含む親 evidence が不足する場合は accept せず `stop-incomplete` とします。
