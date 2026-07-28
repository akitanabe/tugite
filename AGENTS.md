# Repository Guidelines

## プロジェクト構成

Tugite は、Claude Code と Codex 向けの agent・skill 定義を配布します。正本は `shared/` です。skill は `shared/skill/<skill-name>/`、agent は `shared/agents/`、platform ごとの用語は `shared/terms.toml`、bundle version は `shared/VERSION` で管理します。`scripts/build_plugin_assets.py` は、これらを `plugins/claude/` と `plugins/codex/` の配布物へ変換します。generated warning のあるファイルを直接編集せず、対応する `shared/` の原稿を変更して再生成してください。自動テストは `tests/`、手動評価シナリオは `evals/` にあります。

## ビルド・テスト・開発コマンド

- `python3 scripts/build_plugin_assets.py`: platform ごとの配布物と version を再生成します。
- `python3 scripts/build_plugin_assets.py --check`: ファイルを変更せず、生成物が最新か確認します。
- `python3 -B -m unittest discover -s tests -p 'test_build_plugin_assets*.py'`: Python の CLI・repository contract テストを実行します。bytecode を残さないため `-B` を付けます。
- `bash tests/install-agents-test.sh`: Codex custom-agent installer を検証します。
- `git diff --check`: 提出前に空白エラーを検出します。

外部依存のインストールやローカルサーバーは不要です。ツールは Python 標準ライブラリと Bash を使用します。

## コーディングスタイルと命名

Python は4空白インデント、型ヒント、`pathlib.Path`、説明的な `snake_case` 名を使用します。Bash は既存スタイルに従い、変数展開を引用符で囲んでください。skill directory と agent file は、`shared/skill/branch-design/` や `shared/agents/test-quality-reviewer.md` のように小文字の kebab-case で命名します。原稿を複製せず、platform 差分は `shared/terms.toml` または明示的な platform marker で表現します。

## テスト指針

Red、Green、Refactor の順で進めます。テストには `unittest` を使い、実装詳細ではなく観測可能な CLI の振る舞いや repository contract を記述してください。Python のテスト名は `test_<behavior>` とし、共通 fixture は `tests/build_plugin_assets_test_support.py` に置きます。installer の振る舞いは `tests/install-agents-test.sh` に追加します。最初に対象テストを実行し、再生成後に上記の全コマンドを実行してください。数値による coverage 基準はありませんが、関連する振る舞いと失敗経路を保護します。

## Version 更新指針

`shared/` の原稿、`scripts/build_plugin_assets.py`、`plugins/` の生成物が変わる変更では、`shared/VERSION` を更新してから生成器を実行します。手で編集するのは `shared/VERSION` だけで、両 plugin の manifest と `plugins/codex/install/VERSION` へは生成器が同期します。既存の workflow 契約を壊す変更は major、skill・agent や契約の追加は minor、model/effort プロファイル調整のように契約の意味を変えない修正は patch を上げます。`README.md`・`AGENTS.md`・`CLAUDE.md`・`tests/`・`evals/` だけの変更は配布物が変わらないため、version は据え置きます。

## Commit・Pull Request 指針

最近の commit は、`リポジトリとskillをTugiteへ改名する (#94)` のように、変更理由を表す簡潔な日本語件名へ PR 番号を付けています。`feat:`、`test:`、`docs:` などの prefix は必要に応じて使用できますが、必須ではありません。commit 本文では変更が必要な理由を説明してください。

Pull Request には目的と変更範囲、関連 Issue、検証コマンドと結果を記載し、生成物や version の変更を明示します。画像は視覚的な変更がある場合のみ添付し、無関係な変更を含めないでください。
