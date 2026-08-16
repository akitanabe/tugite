# Repository Guidelines

## プロジェクト構成

Tugite は Claude Code、Codex、Cursor 向けの agent・skill 定義を配布します。正本は `shared/` で、skill は
`shared/skill/`、agent は `shared/agents/` に置きます。Gunte の project 設定は `gunte.toml`、決定論的な契約 registry は
`contracts/*.toml`、platform manifest と platform 固有 metadata の宣言は `declarations/` が正本です。配布物は
`plugins/` に生成され、原稿は日本語で書かれています。自動テストは `tests/` にあります。`Contract`、
`Task Specification`、`Work Unit` など近接する語の定義と正本の所在は `docs/ubiquitous-language.md` にまとめています。

## ビルド・テスト・開発コマンド

- `gunte emit`: `gunte.toml` の `sources.files` から Gunte 管理対象を生成します。
- `gunte lock`: 全 source、contract、declaration の検証後に lock を更新します。
- `gunte check`: Gunte 管理対象の byte drift と契約違反を確認します。
- `bash tests/install-agents-test.sh`: Codex custom-agent installer と agent inventory を検証します。
- `git diff --check`: 提出前に空白エラーを検出します。

Gunte には Go 1.26.5 以上が必要です。公開版は `go install github.com/akitanabe/gunte/cmd/gunte@latest` で
導入します。生成物を伴う変更では、repository root で `gunte emit`、`gunte lock`、target/full `gunte check`、installer、diff check の順に実行します。

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

## Kernel injection contract

Kernel は複数の role が共有する判断原則を定義する正本です。Kernel の選択、読み込み、検証、注入は親 Skill の責務とし、
Agent は注入された Kernel を自分の責務内で適用するだけとします。Agent は Kernel の package / plugin 相対 path を
自分で解決しないこととし、Kernel の探索・読み込み・更新も行いません。

- 親 Skill はその実行に必要な Kernel を読み、identity と必要本文を検証してから使います。
- 注入は Agent の既存入力（`判定基準`、`必要な周辺 context` など）へ行うのを基本形とし、Kernel 専用の channel や
  返却 field を増やしません。
- 読み込み失敗、identity 不一致、必要本文不足では推測で継続せず、親の既存停止経路（呼び出し元へ返す、producer では
  `stop-incomplete`）へ返します。
- 複数 Kernel を使う場合の依存解決、競合処理、注入順序も親責務とし、Agent 側で個別に参照させません。
- Kernel の適用結果による最終的な採否・裁定が親責務である既存 workflow では、その責務境界を維持します。
- Kernel は親が持つ round budget、termination、verdict field の責務へ踏み込みません。

`necessity-kernel-v1`（正本は `shared/necessity-kernel.md`、配布物では `references/necessity-kernel.md`）がこの
contract の標準例です。

## 追加・変更時に触れる場所

agent を追加・削除するときは `shared/agents/` の正本、Gunte の `sources.files`、repository contract、installer の
agent inventory を同じ変更で更新します。skill を追加・削除するときは通常、`shared/skill/<name>/SKILL.md`、対応する
declarations、Gunte の `sources.files`、managed inventory を更新し、target rule は出力 path、profile、shape が
変わる場合だけ更新します。生成後は installer test で runtime inventory も確認します。

## workflow と agent の surface

現行の public workflow skill は `impl-lead`（親の受け入れと QA を保持する実装 loop）、`plan-craft`（実装を開始しない計画成果物）、
`plan-craft-approval`（人間参加型の計画成果物）、`review-loop`（不変 snapshot に対する bounded review）、`clarify-it`（段階的な
意思決定の明確化）の5つです。internal skill は `proposal`、`structural-health-gate`、`work-unit-design` の3つです。
agent の正本は `shared/agents/`、各 runtime の exact inventory は repository contract で確認し、Codex custom-agent installer の inventory は installer test でも確認します。

## コーディングスタイルと命名

Python は4空白インデント、型ヒント、`pathlib.Path`、説明的な `snake_case` 名を使用します。Bash は既存スタイルに
従い、変数展開を引用符で囲みます。skill directory と agent file は小文字の kebab-case で命名します。原稿を複製せず、
platform 差分は `gunte.toml` の terms または明示的な `@only` marker で表現します。

## テスト指針

Red、Green、Refactor の順で進めます。Python test を追加する場合は `unittest` を使い、実装詳細ではなく観測可能な
CLI の振る舞いを記述します。repository の inventory、frontmatter、declaration scalar、retired path は Gunte contract で確認し、
生成、projection、serialization、byte drift を別のテストで再実装しません。関連する振る舞いと失敗経路を保護し、
数値による coverage 基準は設けません。

<!-- @contract repository-plan-verification-default -->
計画成果物の既定 verification は、この repository で実行できる native 手段に限り、EVAL を含めない。
Gunte が保証しない点は残存 risk / 未検証とし、受け入れを EVAL 実行に依存させない。
EVAL は Human が明示したとき、または既存 EVAL 成果物の変更自体が要求対象のときだけ使う。
<!-- @/contract -->

## Version 更新指針

`shared/` の原稿、`gunte.toml`、`contracts/*.toml`、`declarations/`、または配布物が変わる変更では、必要な公開面を
確認して `shared/VERSION` を更新し、`gunte emit` と `gunte check` で宣言・生成物・version を同期します。README、
AGENTS、CLAUDE、tests、evals だけの変更では version を更新しません。

公開面（skill・agent の名前、起動方法と発火条件、保存して後から渡す artifact の形式、CLI）の呼び出しが通らなくなる
変更は major、skill・agent・契約の追加や同一 version 内の内部契約変更は minor、契約の意味を変えないモデル/effort
調整は patch です。旧入力を渡しても再起草などの安全な停止へ進める場合は、呼び出しが壊れていないため major とは扱いません。

## Commit・Pull Request 指針

コミットメッセージは変更理由を表す簡潔な日本語件名にします。必要に応じて `feat:`、`test:`、`docs:` などの prefix を
使い、本文では変更が必要な理由を説明します。Pull Request には目的、変更範囲、関連 Issue、検証コマンドと結果を記載し、
生成物や version の変更を明示します。無関係な変更を含めません。

## 変更報告

完了時には変更内容、実行した検証と結果、未検証事項または残存 risk を簡潔に報告します。無関係な dirty state や
untracked artifact は保持します。

## Programmability Boundary contract

<!-- @contract repository-programmability-boundary -->
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
```

deterministic rule は意味の正本と assurance plane を明確にし、未機械化なら owner Action、必要入力、利用可能な
interception point、現在の非機械保証理由、延期または不能の理由、自然言語の正本を維持します。programmable で
あることは即時の機械化義務を意味しません。direct / delegate、worker / reviewer の選択、finding の意味的な採否、
実装 approach、risk 評価など autonomous side の特定結果を expected-output oracle で唯一の正解に固定しません。
必要な反復は consumer と、重複を除いた後も obligation を担う remaining witness を追跡し、独立した意味の正本にしません。
Gunte predicate の成功が保証するのは policy identity、required fields、その coherent relation までです。runtime の意味遵守や
autonomous outcome oracle の不存在を保証したとは扱いません。
<!-- @/contract -->

## Test QA baseline contract

<!-- @contract repository-test-qa-baseline -->
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
<!-- @/contract -->
