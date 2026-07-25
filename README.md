# agentic-qa-workflow

実装作業をサブエージェントへ委譲しつつ、親エージェントがマネージャー兼 QA として品質責任を持つための Claude / Codex 向けスキル定義です。共通原稿から各 platform の plugin 配布物を生成します。

## 構成

編集元は `shared/` に集約しています。

- `shared/skill/delegate-implementation/`
  - `SKILL.md` に workflow の核、`references/*.md` に実装枝、expert 選択、QA・統合の詳細を分けた共通原稿です。
- `shared/skill/plan-implementation-branches/`
  - `SKILL.md` に実装プランを委譲可能な Branch Plan へ正規化する planning skill の核、`references/*.md` にスキーマ、枝分割判断、ユーザー確認の詳細を分けた共通原稿です。
- `shared/agents/*.md`
  - 通常実装、高難度実装、expert 実装、専門レビュー、指摘範囲の最小修正を担当する 9 種類の agent の共通原稿です。
- `shared/terms.toml`
  - Claude Code と Codex で異なる用語を定義します。
- `shared/VERSION`
  - 両 plugin と Codex custom agent インストール素材の共通 version です。

`scripts/build_plugin_assets.py` が共通原稿を platform ごとに変換し、次の配布物を生成します。

- `plugins/claude/skills/delegate-implementation/SKILL.md`
- `plugins/claude/skills/delegate-implementation/references/*.md`
- `plugins/claude/skills/plan-implementation-branches/SKILL.md`
- `plugins/claude/skills/plan-implementation-branches/references/*.md`
- `plugins/claude/agents/*.md`
- `plugins/codex/skills/delegate-implementation/SKILL.md`
- `plugins/codex/skills/delegate-implementation/references/*.md`
- `plugins/codex/skills/plan-implementation-branches/SKILL.md`
- `plugins/codex/skills/plan-implementation-branches/references/*.md`
- `plugins/codex/install/agents/*.toml`
- 両 plugin の manifest version と `plugins/codex/install/VERSION`

`plugins/` 以下の生成対象ファイルには generated warning が付いています。これらを直接編集せず、対応する `shared/` の原稿を変更してください。

## 基本方針

このリポジトリの中心方針は、委譲しても品質責任を親エージェントが持つことです。サブエージェントは実装を担当し、親エージェントは分割、指示、受け入れ条件、テスト品質、最終検証を主導します。

## workflow mode の選択

委譲の決定は次の3層に分けて選びます。層をまたいで並列に選びません。

1. **経路の選択** — `direct`(この skill の外)か、委譲(この skill)か。
2. **配分方針の選択** — 委譲する場合に、配分方針 `policy`(`fixed` / `adaptive`)と基準 `baseline`(`lite` / `standard` / `strict`)を決めます。
3. **枝 mode の導出** — `policy`、`baseline`、枝の `risk.level` から枝ごとの mode(`lite` / `standard` / `strict`)を導きます。

`direct` は委譲 mode ではなく、親エージェントが直接処理する、この skill の外にある route です。委譲要求がなく、仕様が明確で影響範囲が閉じる変更に選び、配分方針や枝 mode と同じ層に並べて選びません。委譲する場合は、まず配分方針を選び、次に枝ごとの mode を導出します。

### 入力語彙と配分方針の対応

| ユーザー入力 | policy | baseline | 選択条件 |
| --- | --- | --- | --- |
| `direct` | — | — | 委譲要求がなく、仕様が明確で影響範囲が閉じる変更。 |
| 指定なし | `adaptive` | `standard` | 通常利用のデフォルト。mode 未指定の明示的な委譲でもこれを選ぶ。 |
| `standard` / `standard-adaptive` | `adaptive` | `standard` | 通常の実装委譲。 |
| `strict` / `strict-adaptive` | `adaptive` | `strict` | 全体として厳格な確認を要求するが、明らかに低リスクの枝まで一律 `strict` にしない。 |
| `strict-full` | `fixed` | `strict` | 全枝へ `strict` を固定適用する。枝ごとの導出を行わない。 |
| `lite` | `fixed` | `lite` | 全枝を軽量フローで処理する。ユーザーが明示し、仕様が明確で影響範囲が局所的、容易に戻せる変更にだけ選ぶ。 |

### 枝 mode の決定表

`policy: adaptive` では、`baseline` と枝の `risk.level` から次の決定表で枝ごとの mode を導出します。`policy: fixed` では導出を行わず、全枝へ `baseline` をそのまま適用します。

| policy | baseline | `risk.level: low` | `medium` | `high` |
| --- | --- | --- | --- | --- |
| `fixed` | `lite` | `lite` | `lite` | `lite` |
| `fixed` | `strict` | `strict` | `strict` | `strict` |
| `adaptive` | `standard` | `lite` | `standard` | `strict` |
| `adaptive` | `strict` | `standard` | `strict` | `strict` |

委譲 mode の強度は `lite < standard < strict` です。導出結果より高い mode で枝を実行する場合、具体的なリスクをユーザーへ報告します。ユーザーが明示した `baseline` を親都合で引き下げません。`direct` から委譲への変更は強度の変更ではなく責務境界の変更であるため、ユーザーに確認します。

詳細な選択条件と委譲手順は、共通原稿の正本である [shared/skill/delegate-implementation/SKILL.md](shared/skill/delegate-implementation/SKILL.md) と [shared/skill/delegate-implementation/references/branch-plan-intake.md](shared/skill/delegate-implementation/references/branch-plan-intake.md) を参照してください。

### v1 からの移行

v2.0.0 で `strict` の意味が変わりました。旧 `strict`(全枝固定)は新語彙の `strict-full` に対応します。新しい `strict` / `strict-adaptive` は、枝の `risk.level` に応じて枝ごとに mode を導出する配分方針を指し、旧 `strict` より枝単位では軽くなり得ます。

| 指定 | 変更前(v1) | 変更後(v2) |
| --- | --- | --- |
| 指定なし | 全枝 `standard` | `{adaptive, standard}` |
| `lite` | 全枝 `lite` | 変更なし |
| `standard` | 全枝 `standard` | `{adaptive, standard}` |
| `strict` | 全枝 `strict` | `{adaptive, strict}` |
| `strict-full` | (存在しない) | 全枝 `strict` = 旧 `strict` |
| `direct` | 親が直接実装 | 変更なし |

## 配布

導入方法と platform 固有の構成は、それぞれの README を参照してください。

- [Claude Code plugin](plugins/claude/README.md)
- [Codex plugin](plugins/codex/README.md)

## workflow の利用例

次の例は、変更名ではなく、具体的な作業内容とリスクから必要な QA を判断するための代表例です。

### direct: typo・文書・小さく閉じた設定修正

委譲要求がなく、仕様が明確で影響範囲が閉じている typo、文書、小さな設定修正は、委譲 mode ではなく skill 外の `direct` route で親が直接処理します。不要な委譲を避けつつ、親が変更に必要な検証、diff review、最終報告を行います。

### standard / standard-adaptive: 小機能・validation rule・振る舞い変更

通常の小機能、validation rule の追加、test を伴う振る舞い変更を明示的に委譲する場合、または mode 未指定で委譲する場合は `standard`(配分方針は `{adaptive, standard}`)を使います。枝の `risk.level` が `high` なら `strict`、`low` なら `lite` へ枝ごとに引き下げ/引き上げられます。親は AC と境界値・異常系を具体化し、専用 worktree で実装させます。Implementer は Red 証跡と AC → test → 期待値の根拠の対応を返し、親は diff と test を確認して、統合後の green と最終判断まで担います。

### strict / strict-adaptive: 失敗コストが高い変更

本番 data migration、file import / export、認証、破壊的操作のような変更でも、名前だけで一律に決めません。失敗コスト、復旧の難しさ、部分失敗時の整合性、認可の誤りという具体的なリスクが高い場合に `strict`(配分方針は `{adaptive, strict}`)を使います。`medium` / `high` risk の枝は `strict` に、`low` risk の枝は(`lite` ではなく)`standard` に導出されます。各枝は同じ実装枝、Implementer context、worktree でテスト計画 → Red → Green → Refactor を段階 gate に分け、親が各段階と統合後の green を確認します。

### strict-full: 全枝を一律 strict にする変更

枝ごとの risk 差を問わず全枝を `strict` で固定したい場合だけ `strict-full`(配分方針は `{fixed, strict}`)を使います。`strict-full` は枝数に比例してコストが増えるため、実行前に枝数を明示したユーザー確認を委譲開始条件とし、確認が得られるまで委譲を開始しません。低リスク枝まで一律 `strict` にするコストを避けたい通常の場合は `strict-adaptive` を優先します。

### 専門 reviewer を選ぶとき

責務境界、test 品質、security / side-effect の専門 reviewer は、`strict` であることだけを理由に一律で選びません。返却 diff に対応する具体的なリスクがある場合、またはユーザーが明示した場合だけ選び、reviewer に最終判断を委ねません。記述原則をread-onlyで確認する `writing-principles-reviewer` は、これらの専門 reviewer とは別の役割です。

## 編集と生成

共通原稿を編集したら、配布物を再生成します。

```text
python3 scripts/build_plugin_assets.py
```

生成物が共通原稿と一致しているかは、ファイルを書き換えない `--check` で確認できます。

```text
python3 scripts/build_plugin_assets.py --check
python3 -B -m unittest discover -s tests -p 'test_build_plugin_assets*.py'
```

## License

MIT License. See [LICENSE](LICENSE).
