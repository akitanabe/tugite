# Repository Guidelines

## プロジェクト構成

Tugite は、Claude Code と Codex 向けの agent・skill 定義を配布します。正本は `shared/` です。skill は `shared/skill/<skill-name>/`、agent は `shared/agents/`、platform ごとの用語は `shared/terms.toml`、bundle version は `shared/VERSION` で管理します。v5 開発では `gunte.toml` と `contracts.toml` を Gunte の project 設定と契約 registry として使い、platform ごとの manifest 正本は `declarations/` に置きます。v4 skill は Gunte へ移さず、v5 正本を作るまでは `scripts/build_plugin_assets.py` で生成します。generated warning のあるファイルを直接編集せず、対応する正本を変更して再生成してください。自動テストは `tests/`、手動評価シナリオは `evals/` にあります。

## ビルド・テスト・開発コマンド

- `python3 scripts/build_plugin_assets.py`: platform ごとの配布物と version を再生成します。
- `python3 scripts/build_plugin_assets.py --check`: ファイルを変更せず、生成物が最新か確認します。
- `gunte emit`: `gunte.toml` の `sources.files` から Gunte 管理対象の配布物を生成します。
- `gunte check`: Gunte 管理対象をメモリ上で生成し、既存配布物との byte drift と契約違反を検出します。
- `python3 -B -m unittest discover -s tests -p 'test_build_plugin_assets*.py'`: Python の CLI・repository contract テストを実行します。bytecode を残さないため `-B` を付けます。
- `bash tests/install-agents-test.sh`: Codex custom-agent installer を検証します。
- `git diff --check`: 提出前に空白エラーを検出します。

Gunte には Go 1.26.5 以上が必要です。公開版は `go install github.com/akitanabe/gunte/cmd/gunte@latest` で導入します。ローカルサーバーは不要です。

## Gunte の運用

`develop/v5` の初期基準では、Gunte は `gunte.toml` の `sources.files` に列挙した agent、manifest、version だけを管理します。v4 skill は Gunte へ移さず、v5 の正本を作るまで従来生成器の管理対象に残します。Gunte 管理対象を変更したら `gunte emit`、`gunte check`、`python3 -B scripts/build_plugin_assets.py --check` を順に実行してください。

`contracts.toml` の `requires` / `forbids` / `order` は、生成物上で決定論的に検査できる不変条件だけに使います。LLM の判断品質は EVAL で扱います。Gunte v1 は `gunte.toml` に未登録の source と生成対象外の stale file を検出しないため、必須 path と retired path は repository の構造テストでも保護してください。

## コーディングスタイルと命名

Python は4空白インデント、型ヒント、`pathlib.Path`、説明的な `snake_case` 名を使用します。Bash は既存スタイルに従い、変数展開を引用符で囲んでください。skill directory と agent file は、`shared/skill/branch-design/` や `shared/agents/test-quality-reviewer.md` のように小文字の kebab-case で命名します。原稿を複製せず、platform 差分は `shared/terms.toml` または明示的な platform marker で表現します。

## テスト指針

Red、Green、Refactor の順で進めます。テストには `unittest` を使い、実装詳細ではなく観測可能な CLI の振る舞いや repository contract を記述してください。Python のテスト名は `test_<behavior>` とし、共通 fixture は `tests/build_plugin_assets_test_support.py` に置きます。installer の振る舞いは `tests/install-agents-test.sh` に追加します。最初に対象テストを実行し、再生成後に上記の全コマンドを実行してください。数値による coverage 基準はありませんが、関連する振る舞いと失敗経路を保護します。

## Version 更新指針

`shared/` の原稿、`scripts/build_plugin_assets.py`、`plugins/` の生成物が変わる変更では、`shared/VERSION` を更新してから生成器を実行します。手で編集するのは `shared/VERSION` だけで、両 plugin の manifest と `plugins/codex/install/VERSION` へは生成器が同期します。公開面（skill・agent・mode の名前、起動方法と発火条件、ユーザーが保存して後から渡す `plan-craft` のプラン文書とレビュー状態の形式、CLI）を壊す変更は major、skill・agent や契約の追加と、同一 version 内で完結する skill 間 Data（Branch Plan の field 名など）の変更は minor、model/effort プロファイル調整のように契約の意味を変えない修正は patch を上げます。`README.md`・`AGENTS.md`・`CLAUDE.md`・`tests/`・`evals/` だけの変更は配布物が変わらないため、version は据え置きます。

公開面に載ることは major を意味しません。major の定義は「利用者の呼び出しが通らなくなる」ことなので、判定は旧入力を渡したときに停止するかで行います。たとえば `plan-craft` の出力を単一の Data からプラン文書とレビュー状態の2 artifact へ分けた 4.2.0 では、旧形式の Data を渡しても `feature-lead` は停止せず、2 artifact が揃わない入力として `plan-craft` から再起草へ落ちるだけで、skill・agent・mode の名前も変わらないため minor としました。

## Commit・Pull Request 指針

最近の commit は、`リポジトリとskillをTugiteへ改名する (#94)` のように、変更理由を表す簡潔な日本語件名へ PR 番号を付けています。`feat:`、`test:`、`docs:` などの prefix は必要に応じて使用できますが、必須ではありません。commit 本文では変更が必要な理由を説明してください。

Pull Request には目的と変更範囲、関連 Issue、検証コマンドと結果を記載し、生成物や version の変更を明示します。画像は視覚的な変更がある場合のみ添付し、無関係な変更を含めないでください。
