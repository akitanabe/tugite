# Repository Guidelines

## プロジェクト構成

Tugite は Claude Code と Codex 向けの agent・skill 定義を配布します。正本は `shared/` で、skill は
`shared/skill/`、agent は `shared/agents/` に置きます。v5 の workflow skill は `impl-lead`、`plan-craft`、
`review-loop`、`work-unit-design` の4つです。Gunte の project 設定は `gunte.toml`、決定論的な契約 registry は
`contracts.toml`、platform manifest と Codex skill metadata の宣言は `declarations/` が正本です。配布物は
`plugins/` に生成されます。自動テストは `tests/`、手動評価シナリオは `evals/` にあります。

## ビルド・テスト・開発コマンド

- `gunte emit`: `gunte.toml` の `sources.files` から Gunte 管理対象を生成します。
- `gunte check`: Gunte 管理対象の byte drift と契約違反を確認します。
- `python3 -B -m unittest discover -s tests -p 'test_v5_repository_contracts.py'`: v5 repository contract を実行します。
- `python3 -B -m unittest discover -s tests`: Python テスト一式を実行します。
- `bash tests/install-agents-test.sh`: Codex custom-agent installer と agent inventory を検証します。
- `git diff --check`: 提出前に空白エラーを検出します。

Gunte には Go 1.26.5 以上が必要です。公開版は `go install github.com/akitanabe/gunte/cmd/gunte@latest` で
導入します。生成物を伴う変更では、repository root で `gunte emit`、`gunte check`、focused test、full test、
installer、diff check の順に実行します。

## Gunte の運用

Gunte は `gunte.toml` の `sources.files` に列挙した agent、manifest、version、4 workflow skill、Codex metadata
を管理します。platform 差分は正本内の `@only claude` / `@only codex` marker で表現し、`plugins/` 以下の生成物を
直接編集しません。`contracts.toml` の `requires` / `forbids` / `order` は生成物上で決定論的に検査できる不変条件
だけに使います。未登録 source、unknown/stale declaration、必須 path、retired path は repository contract の
構造テストで保護し、LLM の判断品質は EVAL で扱います。

`slice` を持つ契約の ID は `<意味を表す prefix>-<8桁 hash>` とします。hash は `kind`、`slice`、`pattern`、辞書順に
並べた `applies_to` のカンマ区切り値をこの順に NUL で連結し、UTF-8 byte 列の SHA-256 先頭8桁を小文字16進数で表します。
列挙順の連番は使いません。`slice` を持たない単独の契約には、意味を表す安定した ID を使用できます。

Kernel の読み込み・検証・注入を親 Skill の責務とする共通規約は、CLAUDE.md の Kernel injection contract 節を正本とします。

## コーディングスタイルと命名

Python は4空白インデント、型ヒント、`pathlib.Path`、説明的な `snake_case` 名を使用します。Bash は既存スタイルに
従い、変数展開を引用符で囲みます。skill directory と agent file は小文字の kebab-case で命名します。原稿を複製せず、
platform 差分は `gunte.toml` の terms または明示的な `@only` marker で表現します。

## テスト指針

Red、Green、Refactor の順で進めます。テストには `unittest` を使い、実装詳細ではなく観測可能な CLI の振る舞いや
repository contract を記述します。Python のテスト名は `test_<behavior>` とし、構造テストは有限の inventory、
frontmatter、declaration scalar、retired path を確認します。Gunte の生成、projection、serialization、byte drift
自体をテストで再実装しません。関連する振る舞いと失敗経路を保護し、数値による coverage 基準は設けません。

## Version 更新指針

`shared/` の原稿、`gunte.toml`、`contracts.toml`、`declarations/`、または配布物が変わる変更では、必要な公開面を
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
