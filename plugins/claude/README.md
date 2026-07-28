# Tugite for Claude Code

実装をサブエージェントへ委譲しながら、親エージェントが計画、受け入れ判断、QA、最終検証の責任を持つための Claude Code plugin です。

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
- `agents/implementer.md`
  - 仕様が明確で範囲が閉じた通常実装を担当します。
- `agents/senior-implementer.md`
  - 設計判断や広い影響範囲を伴う高難度実装を担当します。
- `agents/expert-implementer.md`
  - 事前審査を通過した、親相当の推論能力が必要な実装を担当します。
- `agents/expert-selection-reviewer.md`
  - expert の高い実行コストを正当化する選択理由が揃っているか、起動前に審査します。
- `agents/responsibility-boundary-reviewer.md`
  - 実装済み diff の責務混在、境界違反、副作用分散を確認します。
- `agents/test-quality-reviewer.md`
  - 追加・変更されたテストの仕様対応、振る舞い、網羅性を確認します。
- `agents/writing-principles-reviewer.md`
  - `How / What / Why / Why Not` の配置、命名、説明をread-onlyで確認し、ID付きの指摘Dataを返します。
- `agents/over-engineering-reviewer.md`
  - 基準 commit からの diff のうち、取り除いても AC と制約を満たせるテストと実装をread-onlyで特定し、ID付きの指摘Dataを返します。
- `agents/plan-adversarial-reviewer.md`
  - 起草済みの実装プランに対し、AC 充足・検証可能性・実現可能性を壊す具体的な失敗経路をread-onlyで探索し、ID付きの指摘Dataを返します。
- `agents/security-side-effect-reviewer.md`
  - 外部 I/O、破壊的操作、機密データ、セキュリティ影響を確認します。
- `agents/review-patch-refactorer.md`
  - 専門 reviewer が具体的に指摘した範囲だけを、振る舞いを変えずに最小修正します。

これらの skill と agent 定義はリポジトリの `shared/` から生成されています。生成済みファイルを直接編集せず、共通原稿を更新してください。開発方法は[ルート README](../../README.md)を参照してください。

## インストール

Claude Code で次のコマンドを実行します。

```text
/plugin marketplace add akitanabe/tugite
/plugin install tugite@tugite-marketplace
/reload-plugins
```

`/plugin marketplace add` は GitHub 上の marketplace catalog を登録し、`/plugin install` はそこから plugin をインストールします。導入前に repository と plugin の内容を確認してください。

Claude Code の marketplace と plugin scope の詳細は、[Claude Code の公式ドキュメント](https://code.claude.com/docs/en/discover-plugins)を参照してください。

## 使い方

実装委譲を明示して、skill を呼び出します。

```text
/tugite:impl-lead <実装タスク>
```

または「この実装をサブエージェントに委譲し、親が QA まで担当してください」のように依頼します。タスクが大きいという理由だけでは自動的に委譲しません。

Skill はタスクの難易度と責務に応じて agent を選択します。親エージェントは返却報告だけで受け入れず、diff、テスト内容、副作用、責務境界を確認してから統合します。

## 更新

Marketplace の情報を更新します。

```text
/plugin marketplace update tugite-marketplace
```

Plugin の更新が適用された場合は `/reload-plugins` を実行します。インストール状態や自動更新の設定は `/plugin` の Installed、Marketplaces 画面で確認できます。
