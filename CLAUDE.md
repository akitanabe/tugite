# CLAUDE.md

このリポジトリは Claude Code / Codex 向けの skill と agent 定義を配布します。正本は `shared/`、platform manifest と
Codex skill metadata の宣言は `declarations/`、Gunte の project 設定と契約 registry は `gunte.toml` と `contracts.toml` です。
配布物は `plugins/` に生成され、原稿は日本語で書かれています。`Contract`、`Task Specification`、`Work Unit` など
近接する語の定義と正本の所在は `docs/ubiquitous-language.md` にまとめています。

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

`slice` を持つ契約の ID は `<意味を表す prefix>-<8桁 hash>` とします。hash は `kind`、`slice`、`pattern`、辞書順に
並べた `applies_to` のカンマ区切り値をこの順に NUL で連結し、UTF-8 byte 列の SHA-256 先頭8桁を小文字16進数で表します。
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
