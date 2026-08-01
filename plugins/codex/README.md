# Tugite for Codex

実装を subagent へ委譲しながら、親 Codex エージェントが計画、受け入れ判断、QA、最終検証の責任を持つための Codex plugin です。

## 構成

- `skills/impl-lead/SKILL.md`
  - タスク分割、worktree 隔離、委譲、返却 diff とテストの QA、最終検証を定義します。
- `skills/impl-lead/references/*.md`
  - 実装枝、expert 選択、QA・統合の詳細を必要な段階で参照します。
- `skills/branch-design/SKILL.md`
  - 実装プランを委譲可能な Branch Plan へ正規化します。実装や委譲は行いません。
- `skills/branch-design/references/*.md`
  - Branch Plan スキーマ、枝分割判断、ユーザー確認の詳細を必要な段階で参照します。
- `skills/test-audit/SKILL.md`
  - 既存テストスイートを read-only で走査し、各テストの目的・分類を Test Inventory Data として棚卸しし、テスト設計技法の観点で不足を報告します。
- `skills/test-audit/references/*.md`
  - 棚卸しスキーマ、不足カタログ、走査手順、報告形式の詳細を必要な段階で参照します。
- `skills/plan-craft/SKILL.md`
  - ユーザー要求から実装プランを起草し、敵対的レビューループと過剰実装審査を経た Implementation Plan Data を返します。実装・委譲・枝分割は行いません。
- `skills/plan-craft/references/*.md`
  - Implementation Plan スキーマ、起草手順、レビューループ規約、過剰実装審査の詳細を必要な段階で参照します。
- `skills/feature-lead/SKILL.md`
  - `plan-craft` → `branch-design` → `impl-lead` を順に連結し、要求から実装完了までを一括で進めます。判断点は既定で停止し、`unattended` 明示時のみ自律解決します。
- `skills/install-custom-agents/SKILL.md`
  - 同梱 custom agent のインストール状況を確認し、安全に導入・更新します。
- `install/agents/*.toml`
  - Codex の user scope または project scope へコピーする custom agent 定義です。
- `install/install-agents.sh`
  - 既存ファイルを確認なしに上書きせず、custom agent の導入・更新を行います。

`impl-lead` skill と `install/agents/*.toml` はリポジトリの `shared/` から生成されています。生成済みファイルを直接編集せず、共通原稿を更新してください。開発方法は[ルート README](../../README.md)を参照してください。

## Plugin のインストール

GitHub repository を marketplace として登録し、plugin をインストールします。

```text
codex plugin marketplace add akitanabe/tugite
codex plugin add tugite@personal
```

ローカル checkout を使う場合は、repository root で次を実行します。

```text
codex plugin marketplace add .agents/plugins
codex plugin add tugite@personal
```

登録状態は次のコマンドで確認できます。

```text
codex plugin marketplace list
codex plugin list
```

Plugin の追加後は Codex session を再起動してください。Codex plugin の marketplace と構造については、[Codex の公式ドキュメント](https://developers.openai.com/codex/plugins/build)を参照してください。

## Custom agent のインストール

Codex plugin は skill を配布しますが、`install/agents/*.toml` を custom agent directory へ自動登録しません。Custom agent は利用範囲を選んで別途インストールします。

- user scope: `~/.codex/agents/`
- project scope: `<repo>/.codex/agents/`

Plugin をインストールした場合は、新しい Codex session で `$install-custom-agents` を使うのが基本です。user scope または対象 repository を指定して、状態確認からインストールまでを依頼してください。

ローカル checkout から直接実行する場合は、最初に現在の状態を確認します。

```text
plugins/codex/install/install-agents.sh --check --user
# or
plugins/codex/install/install-agents.sh --check --repo <repo>
```

未インストールまたは更新が必要な場合、`--check` は終了コード `3` を返します。新規インストールは同じ scope で `--check` を外して実行します。

```text
plugins/codex/install/install-agents.sh --user
# or
plugins/codex/install/install-agents.sh --repo <repo>
```

既存または古い定義がある場合は自動で上書きしません。内容を確認し、上書きしてよい場合だけ `--force` を付けます。

```text
plugins/codex/install/install-agents.sh --force --user
# or
plugins/codex/install/install-agents.sh --force --repo <repo>
```

インストール後は Codex session を再起動してください。再起動するまでは custom agent の導入後に委譲作業を続行しません。

Custom agent の配置と設定形式については、[Codex subagents の公式ドキュメント](https://developers.openai.com/codex/agent-configuration/subagents)を参照してください。

Branch Plan は `failure_impact` と `implementation_complexity` を独立して保持します。`adaptive` の枝 mode は
implementation complexity だけから導出し、`failure_impact` は adaptive mode の直接導出には使わず、
`{fixed, lite}` の `delegation_mode_proposal`（安全助言）にだけ使います。
complexity が high の枝は `strict` 候補です。

## Custom agent

| Agent | 担当 |
| --- | --- |
| `implementer` | implementation complexity が low / medium で残る判断が少ない通常実装 |
| `senior-implementer` | implementation complexity が high、または非自明な設計・algorithm・concurrency判断が残る実装 |
| `expert-implementer` | 事前審査を通過した、親相当の推論能力が必要な実装 |
| `expert-selection-reviewer` | expert の高い実行コストを正当化する選択理由の事前審査 |
| `responsibility-boundary-reviewer` | 責務混在、境界違反、副作用分散のレビュー |
| `test-quality-reviewer` | テストの仕様対応、振る舞い、網羅性のレビュー |
| `writing-principles-reviewer` | `How / What / Why / Why Not` の配置、命名、説明のread-onlyレビュー |
| `over-engineering-reviewer` | 取り除いても AC と制約を満たせるテストと実装のread-only検出 |
| `plan-adversarial-reviewer` | 起草済み実装プランの具体的な失敗経路のread-only探索 |
| `security-side-effect-reviewer` | 外部 I/O、破壊的操作、機密データ、セキュリティ影響のレビュー |
| `review-patch-refactorer` | 専門 reviewer が具体的に指摘した範囲の最小修正 |

## 使い方

Custom agent の登録を確認した新しい session で、実装委譲を明示して `$impl-lead` を使います。

```text
$impl-lead を使い、この実装を subagent に委譲して親が QA まで担当してください。
```

タスクが大きいという理由だけでは自動的に委譲しません。親 Codex エージェントは返却報告だけで受け入れず、diff、テスト内容、副作用、責務境界を確認してから統合します。

## Marketplace の更新

Git marketplace の snapshot は次のコマンドで更新できます。

```text
codex plugin marketplace upgrade personal
```

Plugin または custom agent を更新した場合は、custom agent の状態を再確認し、必要に応じて明示的に上書きした後で Codex session を再起動してください。
