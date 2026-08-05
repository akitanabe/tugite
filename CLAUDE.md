# CLAUDE.md

このリポジトリは Claude Code / Codex 向けの skill と agent 定義を配布します。正本は `shared/`、platform manifest と
Codex skill metadata の宣言は `declarations/`、Gunte の project 設定と契約 registry は `gunte.toml` と `contracts.toml` です。
配布物は `plugins/` に生成され、原稿は日本語で書かれています。

## コマンド

```bash
gunte emit
gunte check
python3 -B -m unittest discover -s tests -p 'test_v5_repository_contracts.py'
python3 -B -m unittest discover -s tests
bash tests/install-agents-test.sh
git diff --check
```

`plugins/` 以下の生成物を直接編集せず、正本または宣言を変更したら repository root で `gunte emit` と `gunte check` を
実行します。Gunte には Go 1.26.5 以上が必要で、公開版は次で導入します。

```bash
go install github.com/akitanabe/gunte/cmd/gunte@latest
```

## v5 の Gunte 運用

`gunte.toml` は project、source、target、出力 rule、platform terms を定義し、`contracts.toml` は `requires`、
`forbids`、`order` の決定論的契約を定義します。platform manifest は `declarations/`、Codex の4 workflow skill
metadata は `declarations/codex/skills/` に置きます。Gunte は `sources.files` に列挙した agent、manifest、version、
workflow skill、metadata を生成し、未登録 source や stale path は走査しないため、必須・retired path と exact inventory は
`test_v5_repository_contracts.py` で保護します。

契約は生成物から観測できる不変条件に限定します。Gunte の生成、projection、serialization、byte drift は `gunte check`
に任せ、LLM の判断品質や読みやすさは EVAL または editorial review で扱います。

## 追加・変更時に触れる場所

agent を追加・削除するときは `shared/agents/` の正本、Gunte の `sources.files`、repository contract、installer の
agent inventory を同じ変更で更新します。skill を追加・削除するときは通常、`shared/skill/<name>/SKILL.md`、対応する
declarations、Gunte の `sources.files`、exact inventory の構造テストを更新し、target rule は出力 path、profile、shape が
変わる場合だけ更新します。生成後は installer test で runtime inventory も確認します。

## VERSION の更新規約

配布物、正本、宣言、Gunte の契約が変わるときは `shared/VERSION` を更新し、`gunte emit` と `gunte check` で plugin
manifest と install version を同期します。README、CLAUDE、AGENTS、tests、evals だけの変更では version を更新しません。

semver は公開面が壊れるかで割り当てます。skill・agent 名、起動方法・発火条件、保存して後から渡す artifact 形式、CLI の
呼び出しが通らなくなる変更は major、skill・agent・契約の追加や内部契約変更は minor、モデル/effort 調整など契約の意味を
変えない修正は patch です。旧入力を安全な再起草や停止へ送れる場合は major とは扱いません。

## workflow と agent の surface

現行の workflow skill は `impl-lead`（親の受け入れと QA を保持する実装 loop）、`plan-craft`（実装を開始しない計画成果物）、
`review-loop`（不変 snapshot に対する bounded review）、`work-unit-design`（親 context 内の内部 Work Unit 設計）の4つです。
agent の正本は `shared/agents/`、Claude/Codex runtime の exact inventory は repository contract と installer test で確認します。

## コミット規約

コミットメッセージは日本語の要約1行にし、本文では変更理由を説明します。Pull Request には目的、scope、関連 Issue、検証結果、
生成物・version の変更を記載し、無関係な変更を含めません。
