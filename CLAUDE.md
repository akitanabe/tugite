# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## このリポジトリの性質

アプリケーションコードのリポジトリではありません。成果物は Claude Code / Codex 向けの **skill と agent の定義文（プロンプト原稿）** であり、`shared/` の共通原稿から `plugins/claude/` と `plugins/codex/` の配布物を生成します。Python コードは生成器 `scripts/build_plugin_assets.py` とそのテストだけです。

原稿は日本語で書かれています。README・コミットメッセージ・原稿本文はすべて日本語です。

## コマンド

```bash
# 配布物を生成（shared/ を編集したら必ず実行）
python3 scripts/build_plugin_assets.py

# 生成物が共通原稿と一致するか確認（ファイルを書き換えない）
python3 scripts/build_plugin_assets.py --check

# Python テスト一式
python3 -B -m unittest discover -s tests -p 'test_build_plugin_assets*.py'

# 単一テスト（tests/ を sys.path に載せる必要があるため tests/ で実行する）
cd tests && python3 -B -m unittest test_build_plugin_assets_cli.BuildPluginAssetsCliTest.test_build_generates_all_assets_and_syncs_versions

# Codex custom agent インストーラのテスト
bash tests/install-agents-test.sh
```

`plugins/` 以下の生成対象ファイルを直接編集しないでください。対応する `shared/` の原稿を変更してから生成器を実行します。生成物には generated warning が付いています。

## 生成パイプライン

`scripts/build_plugin_assets.py` は「検証 → レンダリング → 比較または書き込み」の一方向処理です。入力に1つでもエラーがあれば何も書き込まず、`path:line: message` 形式の診断を stderr に出して終了コード 1 を返します。

入力（`shared/`）から出力（`plugins/`）への変換は次の4段階です。

1. **platform marker の選択** — `<!-- claude-only:start -->` / `<!-- codex-only:start -->` で囲んだ範囲は、その platform の出力にだけ残ります。marker はネスト不可・行単独必須で、対応が崩れると生成が失敗します。
2. **placeholder 置換** — `{{parent_agent}}` のような placeholder を `shared/terms.toml` の platform 別の語で置き換えます。置換は1回限りで、挿入した値を再走査しません。marker 選択の**後**に行うため、片側 platform の分岐に marker で書いた語が反対側へ漏れません。
3. **frontmatter 変換** — agent 原稿は TOML frontmatter（`+++` 区切り）で、Claude 向けには YAML frontmatter の `.md`、Codex 向けには本文を `developer_instructions` に埋めた `.toml` として出力されます。skill 原稿は YAML frontmatter 込みでそのまま各 platform へ出力されます。
4. **version 同期** — `shared/VERSION`（現在 3.0.0）を両 plugin の `plugin.json` の `version` と `plugins/codex/install/VERSION` へ書き込みます。manifest は version 以外のバイト列を保存します。

## 閉じたスキーマという設計方針

生成器は「未知のもの」をすべてエラーにします。この性質が、原稿の追加漏れや置き忘れを検出する主要な仕組みです。

- `shared/agents/` に `AGENT_NAMES` 以外の `.md` があればエラー
- `shared/skill/` に `SKILL_REFERENCE_NAMES` に登録されていない directory があればエラー
- reference directory に登録外の `.md` があればエラー
- agent frontmatter に未知のキーがあればエラー（`[claude]` / `[codex]` それぞれ許可キーが固定）
- `terms.toml` に定義されていて一度も使われない term があればエラー

したがって、skill や agent を**追加・削除するときは生成器の定数を必ず更新**します。

## 追加・変更時に触れる場所

新しい agent を追加する場合:

1. `shared/agents/<name>.md` を作成
2. `scripts/build_plugin_assets.py` の `AGENT_NAMES` に追加
3. `tests/build_plugin_assets_test_support.py` の `AGENT_NAMES`、必要に応じて `REVIEWER_NAMES` / `READ_ONLY_TOOL_AGENT_NAMES` / `REFACTORER_NAMES`、`CLAUDE_MODEL_PROFILES` / `CODEX_MODEL_PROFILES` に追加
4. `tests/install-agents-test.sh` の `required_agents` に追加
5. 両 platform の README（`plugins/claude/README.md` / `plugins/codex/README.md`）に記載（契約テストが全 agent の記載を要求します）

新しい skill を追加する場合は、`shared/skill/<name>/SKILL.md` と `references/*.md` を作り、生成器と test support 双方の `SKILL_REFERENCE_NAMES` に skill 名と reference 名の並びを登録します。空タプルは SKILL.md のみの skill を表します。

## VERSION の更新規約

配布物が変わる変更では、`shared/VERSION` を更新してから生成器を実行します。手で書き換えるのは `shared/VERSION` だけで、両 plugin の `plugin.json` と `plugins/codex/install/VERSION` へは生成器が同期します。

- **更新が必要** — `shared/` の原稿、`scripts/build_plugin_assets.py`、`plugins/` の生成物が変わる変更
- **更新は不要** — `README.md` / `CLAUDE.md` / `AGENTS.md` / `tests/` / `evals/` だけの変更

semver の割り当ては次のとおりです。

- **major** — 既存の workflow 契約を壊す変更（mode や skill・agent の改名・削除など、利用者の呼び出しが通らなくなるもの）
- **minor** — skill・agent の追加、契約の追加や拡張
- **patch** — model/effort プロファイルの調整など、契約の意味を変えない修正

## テストの二層構造

- **`tests/test_build_plugin_assets_cli.py`** — 生成器を CLI としてのみ扱う振る舞いテスト。tempdir に fixture repository を組み立てて実行するため、実リポジトリの原稿内容には依存しません。
- **`tests/test_build_plugin_assets_repository_contracts.py`** — 実リポジトリの原稿本文そのものを検査する契約テスト。日本語の具体的な文言、model/effort プロファイル、reviewer の出力形式、`evals/workflow-decision-corpus.md` の記述、README の記載までを固定しています。

原稿の文言を変えると契約テストが落ちるのは**意図された設計**です。ワークフロー契約の変更なので、テスト側の期待値も同じ意図で更新します。テストの定数付近には「なぜその文字列で切り詰めているか」を説明する Why Not コメントが付いているので、変更前に読んでください。

## workflow の中身（原稿を読むときの地図）

配布する skill は5つで、責務が分離されており、`feature-lead` が自身の段として `plan-craft` /
`branch-design` / `impl-lead` を連結して起動する場合を除き、互いを直接起動しません。

| skill | 責務 | 起動しないもの |
| --- | --- | --- |
| `plan-craft` | 要求から実装プランを起草し、敵対的レビューと過剰実装審査を通す | 実装・委譲・枝分割 |
| `branch-design` | 実装プランを委譲可能な Branch Plan Data へ正規化する | 実装・委譲・`impl-lead` |
| `impl-lead` | 枝を worktree 隔離して委譲し、親が QA と最終検証を担う | — |
| `test-audit` | 既存テストスイートを read-only で棚卸しし gap を報告する | 修正・テスト実行・受け入れ判断 |
| `feature-lead` | `plan-craft` → `branch-design` → `impl-lead` を連結し、要求から実装完了までを一括で進める | 各段の判断基準の再定義・プラン起草・枝分割・実装自体 |

`impl-lead` の mode は3層構造で決まります。`direct`（skill の外・親が直接実装）か委譲かをまず選び、委譲なら配分方針 `policy`（`fixed` / `adaptive`）と `baseline`（`lite` / `standard` / `strict`）を決め、枝ごとの `risk.level` から枝 mode を導出します。v2.0.0 で旧 `strict`（全枝固定）は `strict-full` へ改名され、`strict` は adaptive 配分を指すようになりました。詳細は README と `shared/skill/impl-lead/SKILL.md` を正本とします。

`evals/workflow-decision-corpus.md` は、これらの判断を代表入力に対して人間が評価するための Phase 1 データです。正本ではなく評価用であり、自動採点は行いません。

## コミット規約

コミットメッセージは日本語の要約1行で、末尾に PR 番号を付けます（例: `reviewer起動を穴埋めテンプレート化しdiffをartifactのpathで渡す (#91)`）。
