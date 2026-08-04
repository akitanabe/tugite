# Tugite

実装作業をサブエージェントへ委譲しつつ、親エージェントがマネージャー兼 QA として品質責任を持つための Claude / Codex 向けスキル定義です。共通原稿から各 platform の plugin 配布物を生成します。

## 構成

編集元は `shared/` に集約しています。

- `shared/skill/impl-lead/`
  - `SKILL.md` に workflow の核、`references/*.md` に実装枝、expert 選択、QA・統合の詳細を分けた共通原稿です。
- `shared/skill/impl-delegate/`
  - `SKILL.md` に、明示指定時だけ1名へ委譲する軽量な TDD 実装手順と親 QA・reviewer 選択をまとめた共通原稿です。
- `shared/skill/branch-design/`
  - `SKILL.md` に実装プランを委譲可能な Branch Plan Set へ正規化する planning skill の核、`references/*.md` にスキーマ、枝分割判断、ユーザー確認の詳細を分けた共通原稿です。
- `shared/skill/test-audit/`
  - `SKILL.md` に既存テストスイートを read-only で走査し、各テストの目的・分類を Test Inventory Data として棚卸しし、テスト設計技法の観点で不足を報告する skill の核、`references/*.md` に棚卸しスキーマ、不足カタログ、走査手順、報告形式の詳細を分けた共通原稿です。
- `shared/skill/plan-craft/`
  - `SKILL.md` にユーザー要求から実装プランを起草し、敵対的レビューループと過剰実装審査を経たプラン文書とレビュー状態の2 artifact を返す planning skill の核、`references/*.md` にプラン artifact の規約、起草手順、レビューループ規約、過剰実装審査の詳細を分けた共通原稿です。
- `shared/skill/feature-lead/`
  - `SKILL.md` に `plan-craft` → `branch-design` → `impl-lead` の3段を連結し、要求から実装完了までを一括で進める orchestration skill の共通原稿です。references は持ちません。
- `shared/agents/*.md`
  - 通常実装、高難度実装、expert 実装、専門レビュー、指摘範囲の最小修正を担当する 11 種類の agent の共通原稿です。
- `shared/terms.toml`
  - Claude Code と Codex で異なる用語を定義します。
- `shared/VERSION`
  - 両 plugin と Codex custom agent インストール素材の共通 version です。

`scripts/build_plugin_assets.py` が共通原稿を platform ごとに変換し、次の配布物を生成します。

- `plugins/claude/skills/impl-lead/SKILL.md`
- `plugins/claude/skills/impl-lead/references/*.md`
- `plugins/claude/skills/impl-delegate/SKILL.md`
- `plugins/claude/skills/branch-design/SKILL.md`
- `plugins/claude/skills/branch-design/references/*.md`
- `plugins/claude/skills/test-audit/SKILL.md`
- `plugins/claude/skills/test-audit/references/*.md`
- `plugins/claude/skills/plan-craft/SKILL.md`
- `plugins/claude/skills/plan-craft/references/*.md`
- `plugins/claude/skills/feature-lead/SKILL.md`
- `plugins/claude/agents/*.md`
- `plugins/codex/skills/impl-lead/SKILL.md`
- `plugins/codex/skills/impl-lead/references/*.md`
- `plugins/codex/skills/impl-delegate/SKILL.md`
- `plugins/codex/skills/branch-design/SKILL.md`
- `plugins/codex/skills/branch-design/references/*.md`
- `plugins/codex/skills/test-audit/SKILL.md`
- `plugins/codex/skills/test-audit/references/*.md`
- `plugins/codex/skills/plan-craft/SKILL.md`
- `plugins/codex/skills/plan-craft/references/*.md`
- `plugins/codex/skills/feature-lead/SKILL.md`
- `plugins/codex/install/agents/*.toml`
- 両 plugin の manifest version と `plugins/codex/install/VERSION`

`plugins/` 以下の生成対象ファイルには generated warning が付いています。これらを直接編集せず、対応する `shared/` の原稿を変更してください。

## 基本方針

このリポジトリの中心方針は、委譲しても品質責任を親エージェントが持つことです。サブエージェントは実装を担当し、親エージェントは分割、指示、受け入れ条件、テスト品質、最終検証を主導します。

## workflow mode の選択

委譲の決定は次の3層に分けて選びます。層をまたいで並列に選びません。

1. **経路の選択** — `direct`(この skill の外)か、委譲(この skill)か。
2. **配分方針の選択** — 委譲する場合に、配分方針 `policy`(`fixed` / `adaptive`)と基準 `baseline`(`lite` / `standard` / `strict`)を決めます。
3. **枝 mode の導出** — `policy`、`baseline`、枝の `implementation_complexity.level` から枝ごとの mode(`lite` / `standard` / `strict`)を導きます。

`direct` は委譲 mode ではなく、親エージェントが直接処理する、この skill の外にある route です。委譲要求がなく、仕様が明確で影響範囲が閉じる変更に選び、配分方針や枝 mode と同じ層に並べて選びません。委譲する場合は、まず配分方針を選び、次に枝ごとの mode を導出します。

### 入力語彙と配分方針の対応

| ユーザー入力 | policy | baseline | 選択条件 |
| --- | --- | --- | --- |
| `direct` | — | — | 委譲要求がなく、仕様が明確で影響範囲が閉じる変更。 |
| 指定なし | `adaptive` | `standard` | 通常利用のデフォルト。mode 未指定の明示的な委譲でもこれを選ぶ。 |
| `standard` / `standard-adaptive` | `adaptive` | `standard` | 通常の実装委譲。 |
| `strict` / `strict-adaptive` | `adaptive` | `strict` | 全体として厳格な確認を要求するが、明らかに low complexity の枝まで一律 `strict` にしない。 |
| `strict-full` | `fixed` | `strict` | 全枝へ `strict` を固定適用する。枝ごとの導出を行わない。 |
| `lite` | `fixed` | `lite` | 全枝を軽量フローで処理する。ユーザーが明示し、仕様が明確で影響範囲が局所的、容易に戻せる変更にだけ選ぶ。 |

### 枝 mode の決定表

各枝は、失敗範囲・可逆性・外部副作用・security・data整合性・後方互換性を表す
`failure_impact` と、仕様明確さ・既存pattern・残存判断・依存複雑性・調査を表す
`implementation_complexity` を独立して持ちます。`policy: adaptive` では、`baseline` と枝の
`implementation_complexity.level` から次の決定表で枝ごとの mode を導出します。
`failure_impact` は adaptive mode の直接導出には使わず、`{fixed, lite}` の `delegation_mode_proposal`（安全助言）にだけ使います。
`policy: fixed` では導出を行わず、全枝へ `baseline` をそのまま適用します。

| policy | baseline | `implementation_complexity.level: low` | `medium` | `high` |
| --- | --- | --- | --- | --- |
| `fixed` | `lite` | `lite` | `lite` | `lite` |
| `fixed` | `strict` | `strict` | `strict` | `strict` |
| `adaptive` | `standard` | `lite` | `standard` | `strict` |
| `adaptive` | `strict` | `standard` | `strict` | `strict` |

委譲 mode の強度は `lite < standard < strict` です。導出結果より高い mode で枝を実行する場合、具体的なリスクをユーザーへ報告します。ユーザーが明示した `baseline` を親都合で引き下げません。`direct` から委譲への変更は強度の変更ではなく責務境界の変更であるため、ユーザーに確認します。

詳細な選択条件と委譲手順は、共通原稿の正本である [shared/skill/impl-lead/SKILL.md](shared/skill/impl-lead/SKILL.md) と [shared/skill/impl-lead/references/branch-plan-intake.md](shared/skill/impl-lead/references/branch-plan-intake.md) を参照してください。

### impl-delegate: 明示指定時の軽量な委譲

`impl-delegate` は、ユーザーが skill 名を明示した場合だけ発火します。自然言語やタスク規模から推測して発火せず、
明示時は `impl-lead` を発火しません。Intake 後に親が基準 commit から専用 worktree を作成し、1名の `worker`（通常は `implementer`、必要時は `senior-implementer`）
がその worktree だけを編集します。TDD の Red → Green → Refactor と親 QA は必須ですが、Branch Plan、永続 QA
report、独立した diff artifact は要求しません。

通常は `implementer` を選びます。事前整理後も残る設計・推論判断、誤実装時の手戻り・rollback 負担、周辺機能や
外部副作用への影響を評価し、上位 model で誤実装リスクを具体的に減らせる場合だけ `senior-implementer` を選べます。
変更量・ファイル数・高い失敗コストというラベルだけでは昇格せず、親は選択理由を最終報告します。

専門 reviewer は `impl-lead` と同じ具体的リスク選択で必要なものだけを起動し、該当なしは 0名で構いません。
修正後に追加確認する場合も影響 reviewer だけに限定し、固定 round や全 reviewer の再起動は行いません。
最終 diff では `writing-principles-reviewer` を1回実行し、採用指摘だけを `review-patch-refactorer` に渡してから、
親 QA と Green 確認で終了します。commit・push・PR は明示依頼時だけ行います。

Closeout では、明示された commit/push/PR と最終確認を先に実行し、安全に回収済みの場合だけ専用 worktree を cleanup
します。commit 未依頼で変更が worktree に残る場合は cleanup せず、path/status を報告します。force 削除は行いません。

### v1 からの移行

v2.0.0 で `strict` の意味が変わりました。旧 `strict`(全枝固定)は新語彙の `strict-full` に対応します。新しい `strict` / `strict-adaptive` は、枝の実装複雑度に応じて枝ごとに mode を導出する配分方針を指し、旧 `strict` より枝単位では軽くなり得ます。

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

通常の小機能、validation rule の追加、test を伴う振る舞い変更を明示的に委譲する場合、または mode 未指定で委譲する場合は `standard`(配分方針は `{adaptive, standard}`)を使います。枝の `implementation_complexity.level` が `high` なら `strict`、`low` なら `lite` へ枝ごとに導出されます。親は AC と境界値・異常系を具体化し、専用 worktree で実装させます。Implementer は Red 証跡と AC → test → 期待値の根拠の対応を返し、親は diff と test を確認して、統合後の green と最終判断まで担います。

### strict / strict-adaptive: 実装複雑度が高い変更

仕様や責務境界に重要な判断が残る、非自明なalgorithm・concurrencyを含む、または調査・仮説検証が必要な場合に `strict`(配分方針は `{adaptive, strict}`)を使います。`medium` / `high` complexity の枝は `strict` に、`low` complexity の枝は(`lite` ではなく)`standard` に導出されます。各枝は同じ実装枝、Implementer context、worktree でテスト計画 → Red → Green → Refactor を段階 gate に分け、親が各段階と統合後の green を確認します。高い failure impact だけでは adaptive mode を strict にしません。

### strict-full: 全枝を一律 strict にする変更

枝ごとの implementation complexity 差を問わず全枝を `strict` で固定したい場合だけ `strict-full`(配分方針は `{fixed, strict}`)を使います。`strict-full` は枝数に比例してコストが増えるため、実行前に枝数を明示したユーザー確認を委譲開始条件とし、確認が得られるまで委譲を開始しません。low complexity 枝まで一律 `strict` にするコストを避けたい通常の場合は `strict-adaptive` を優先します。

### 専門 reviewer を選ぶとき

責務境界、test 品質、security / side-effect の専門 reviewer は、`strict` であることだけを理由に一律で選びません。返却 diff に対応する具体的なリスクがある場合、またはユーザーが明示した場合だけ選び、reviewer に最終判断を委ねません。記述原則をread-onlyで確認する `writing-principles-reviewer` は、これらの専門 reviewer とは別の役割です。

read-only reviewer の tool contract は、対象 repository への書き込み禁止と、判定に必要な探索手段を分けて設計しています。全 reviewer で書き込み系 tool を禁止する一方、repository-native command、基準 commit の参照、test や mutation の実行が evidence の質を左右する reviewer には Bash を許可します。渡された Data と原稿だけで判定する reviewer には Bash を許可しません。各 reviewer の群への割り当ては `shared/agents/` を正本とし、一覧をここへ複製しません。

この分割は [Issue #114](https://github.com/akitanabe/tugite/issues/114) で、23回の reviewer 実行を調べた結果に基づいています。`test-quality-reviewer` は検出力を mutation で実測し、`responsibility-boundary-reviewer` は基準 commit を `git show` / `git grep` で参照して、diff 由来の問題と既存問題を切り分けていました。Bash を一律に外すと、read-only の形式は揃っても、これらの reviewer が根拠を検証できず判断品質が下がります。

Bash を許可する reviewer も対象 repository では読み取りと検証だけを行い、書き込みが必要な検証は対象外の一時複製へ隔離します。Claude では Bash の内部操作を tool metadata だけで制限できないため、これは既知の制約です。tool policy を変更する場合は、review goal と必要な evidence が変わった根拠、および同等の判断品質を維持できる代替手段を示してください。

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
