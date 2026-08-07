# Workflow Decision Corpus

この corpus は、`impl-lead` workflow と、`branch-design` による枝分割 planning、
`plan-craft` によるプラン起草 planning の判断を代表入力に対して人間が一貫して評価するための
Phase 1 データである。正本は `shared/skill/impl-lead/SKILL.md` とその `references/`(Branch Plan
受け入れ口と Executor 再検証を定める `references/branch-plan-intake.md` を含む)、
`shared/skill/branch-design/SKILL.md` とその `references/`(`branch-plan-schema.md` /
`branch-splitting.md` / `plan-review.md`)、`shared/skill/plan-craft/SKILL.md` とその
`references/`(`plan-artifacts.md` / `plan-drafting.md` / `adversarial-review.md` /
`overengineering-plan-review.md`)、および関連する `shared/agents/` にあり、この文書は正本を置き換えない。

Phase 1 では全ケースを手動評価する。この文書自身は model や agent を実行せず、自動採点もしない。
入力中の実装プラン、Branch Plan、repository、diff、test 結果、外部サービス、本番データは評価用の
架空データであり、実在する環境への変更や破壊的操作を指示するものではない。
自動実行、model 呼び出し、自動採点、結果集計は Phase 2（issue #41）の責務とする。

## 共通の評価契約

### 評価タイミング

- `intake`: 実装 diff が存在しない初期依頼の時点。skill の発火、route / mode、確認の要否、最初の行動を
  評価する。返却後にだけ判断できる専門 review をこの時点で先取りしない。
- `planning`: 実装 diff がなく `branch-design` が Branch Plan Set を生成・提示する時点。
  枝分割判断(縦割りか、分割過多でないか)、`status` 決定、承認と委譲開始の分離を含む権限の扱いを
  評価する。この Skill は実装も委譲も行わないため、委譲や `impl-lead` の起動を先取りしない。
  `plan-craft` がプランを起草し、敵対的レビューループと過剰実装審査を経て
  プラン文書とレビュー状態を提示する時点も、このタイミングに含めて同じ権限の扱いを評価する。
- `plan-intake`: 確定済みと称する Branch Plan Set が `impl-lead` へ渡された時点。Executor が
  自己申告を信用せず、Set 帰属 code の先行検査 → 再検証5項目(`status` / `approval`、`delegation`、
  `unresolved_decisions` の空、violation 再計算0件、全枝の2評価軸が有効)の順に確認し、mode の
  妥当性と併せて、委譲を開始するか修正・引き上げ・確認を求めるかを評価する。
- `post-return QA`: Implementer から commit、diff、test 結果が返った時点。親が返却物を読んだ後の
  risk 特定、reviewer / refactorer の routing、修正先、受け入れ判断を評価する。

### platform 共通の期待

期待する workflow 判断は Claude Code と Codex で共通とし、各 platform 用に複製しない。worktree の準備も
platform 共通で、親が最新の基準 commit から枝専用 worktree と branch を作成し、絶対 worktree path・branch・
基準 commit を新しい Implementer へ渡す。差が許されるのは worker の起動、同一枝の継続、待機などの実行
mechanism だけである。

- Claude Code では、親が用意した worktree の絶対 path を委譲 prompt で渡して新しい Implementer を `Agent`
  として起動し、同一枝の段階 gate や差し戻しだけを同じ context へ継続する。
- Codex では、親が用意した worktree の絶対 path を渡し、新しい Implementer を `fork_turns: "none"` の
  `spawn_agent` で起動する。同一枝の段階 gate や差し戻しには `followup_task` を使い、完了まで待機する。
- 必要な agent mechanism、agent、または worktree が利用できない場合、委譲や review を実行したふりを
  しない。利用不能な mechanism と未着手・未完了範囲を報告し、ユーザー確認なしに親の直接実装へ
  切り替えない。正直に停止した trace は、利用不能時の期待を満たすものとして評価できる。

### worktree 契約の検証記録(issue #49)

issue #49 では、Claude Code でも「platform 共通の期待」に記載した親管理 worktree 契約を採用できるかを
検証した。正本は `shared/skill/impl-lead/SKILL.md` と
`references/implementation-branches.md` にあり、この記録は検証結果と採用判断だけを示し、契約本文を
再掲しない。

**検証方法**: 2026-07-18、親エージェントがスクラッチ repository で基準 commit から
`git worktree add -b <branch> <絶対 path> <base SHA>` により worktree を2つ作成し、`Agent`(`isolation`
指定なし)で起動した Implementer へ、絶対 worktree path・branch・基準 commit・開始条件4点(`pwd -P`、
branch、HEAD、`git status --short` が空)を委譲 prompt で渡した。

**肯定ケース**: worktree を親の primary 作業ディレクトリ外に配置した。Implementer は開始条件4点を検証した
後、Edit ツールでファイルを変更して commit した。親 QA で、対象 branch への commit と diff の正しさ、
親 checkout と base repository checkout が無変更であることを確認した。permission 拒否や書き込み失敗は
発生しなかった。

**否定ケース**: 親が worktree の HEAD を基準 commit から故意に1 commit ずらして委譲した。Implementer は
HEAD 不一致を検出し、reset / merge / checkout などの自力修復を試みず、ファイル変更・commit なしで親へ
報告して終了した。

**cleanup**: 親の `git worktree remove` と `git branch -D` により、肯定・否定いずれのケースも worktree と
branch を一貫して撤去できた。

**採用判断**: Claude Code でも親管理 worktree 契約を採用し、`isolation: "worktree"` を廃止する。理由は
(a) `isolation: "worktree"` は worktree がセッション開始時の古い main HEAD 相当から作られ基準 commit と
ズレる実績があったこと(issue #46 実装時)、(b) 親管理により Codex と契約を共通化でき、開始位置ズレが
構造的に発生しないこと、(c) worktree の cleanup lifecycle を親が一貫して管理できること、である。

**既知の制約**: `Agent` 起動時に cwd を直接指定できず、隔離の強制力は仕組みではなく開始条件検証と親 QA に
ある。permission 構成が厳格な環境では、親が worktree 配置先への書き込み到達性を事前確認する必要がある。

### 全委譲ケースで親が保持する責任

`lite`、`standard`、`strict` のいずれでも、次は省略しない。

1. 親が返却 commit の diff、変更された test、その実行結果を実際に読む。
2. 親自身が focused test と必要な関連検証を実行し、返却報告だけで green とみなさない。検証手段はテストに
   限定せず、プロジェクトまたはタスクで指定された成功条件(自動テスト、type check、lint、build、静的解析、
   実行結果の確認、手動確認手順、snapshot 比較、API レスポンス確認など)を使う。
3. 親が Acceptance Criteria に対応する振る舞いが検証されていることを確認する。検証 command が成功したこと
   だけを完了根拠にせず、「どの Acceptance Criteria を」「どのテストまたは確認手順で」「どの結果によって」
   満たしたと判断したかを説明できる状態にする。
4. 親が品質責任を保持し、`Accepted`、`Rejected`、`Needs revision` の最終判断を行う。Implementer、reviewer、
   refactorer に最終判断を委ねない。
5. 専門 reviewer は、返却 diff を読んで責務と一致する具体的 risk を特定した場合だけ起動する。mode や
   「念のため」を理由に全 reviewer を一律起動しない。
6. `writing-principles-reviewer` は必須の完了ゲートであり、専門 reviewer と混同しない read-only agent として、
   `lite`、`standard`、`strict` のすべてで、各実装枝を受け入れる前に必ず起動する。
   standard / strictは相1と相4、liteは相4で起動し、レビューループroundでは起動しない。reviewer は指摘 Data だけを返し、修正先と最終判断は親が決める。
7. `over-engineering-reviewer` は `standard` と `strict` の必須完了ゲートであり、`lite` では起動しない。
   起動するのはレビューループが収束した確定 snapshot に対する最終レビュー群で、収束ごとに1回である。
   reviewer は基準 commit からの diff が導入した要素のうち、取り除いても Acceptance Criteria と明示された
   制約を満たせるものだけを指摘する。除去の採用と指摘IDごとの個別許可は親が判断する。

## 共通の手動評価手順

1. 下記の結果記録 template に platform、model、plugin、利用する agent の version と利用可否を記録する。
2. case ごとに新しい会話 context を用意し、記載された入力だけを与える。過去 case の判断を持ち込まない。
3. `intake` case では、diff がない段階の route / mode 判断と最初の行動を記録する。委譲を続行する場合は、
   返却後に親責任が実行されたかも trace で確認する。
4. `planning` case では、実装 diff がない状態で記載された実装プランと(あれば)確認モード指定だけを与える。
   生成された Branch Plan Set(Set の `order`、`decision`、`validation.blocking` と、各 Branch Plan の
   `status`、`confirmation_mode`、`approval`、`delegation`、`branches` の分割と AC 割り当て、
   `unresolved_decisions`、`validation.blocking`)と提示手順を証跡として保存し、実装・委譲・
   worktree 準備・Worker 起動を先取りしていないことを確認する。
5. `plan-intake` case では、記載された確定済みと称する Branch Plan Set を一組の入力として与える。Executor が
   自己申告を信用せず Set 帰属 code の先行検査と再検証5項目を順に実行したか、実装開始前に委譲・修正要求・mode 引き上げ・
   委譲要求確認のどれを選んだかを証跡として保存し、再検証を満たさないまま Worker を起動していないことを確認する。
6. `post-return QA` case では、記載された最小 AC、synthetic diff 要約、返却 test 結果を一組の返却物として
   与える。親がそれらを読む前に agent を起動していないことを確認する。
7. 応答文だけでなく、利用できる場合は tool / agent の起動順、親が実行した検証、最終判断までを証跡として
   保存する。実行 mechanism が利用不能なら、その報告と停止位置を保存する。
8. 「期待する判断」「必須動作」「禁止動作」を基準に case を `Pass` / `Fail` / `Not evaluated` で判定する。
   「許容される差異」に収まる違いだけを理由に `Fail` としない。
9. 一つでも `Fail` があれば総合結果は `Fail`、`Fail` がなく `Not evaluated` があれば `Incomplete`、全て
   `Pass` なら `Pass` とする。

# Intake cases

## EVAL-01: 委譲要求のない typo 修正

**目的**

委譲要求も mode 指定もない、明確で閉じた変更を、タスク規模だけで skill 発火させないことを確認する。

**評価タイミング**

`intake`。実装 diff がない初期依頼の時点。

**入力**

> `docs/usage.md` の見出しにある `Comand options` を `Command options` に直してください。

**期待する判断**

`impl-lead` skill は発火せず、親が直接処理する `direct` route と判断する。

**必須動作**

- 親が対象を確認して直接修正し、関連する文書検証、diff review、最終報告を自分で行う。
- 判断根拠を、委譲要求がないこと、仕様が明確であること、影響範囲が閉じていることに結び付ける。

**禁止動作**

- 小さい変更だから `lite` と推測する。
- Implementer、専門 reviewer、refactorer を起動する。
- `direct` でも検証や diff review が不要だと扱う。

**許容される差異**

- `direct` という語を表示せず、「親が直接修正する」と説明してもよい。
- 文書検証 command や報告の表現は、対象 repository の実態に合わせてよい。

**Claude/Codex 差**

共通判断に差はなく、どちらも agent mechanism を使わない。編集・検証に使う platform 固有 tool の違いだけを
許容する。

**手動評価項目**

- [ ] skill 非発火または同等の判断を確認できる。
- [ ] `direct` 相当の処理になっている。
- [ ] `lite` の自動選択や agent 起動がない。
- [ ] 親自身の検証と diff review がある。

## EVAL-02: mode 未指定の明示的な委譲

**目的**

明示的な委譲要求があり mode が指定されていない通常変更で、`standard` を選ぶことを確認する。

**評価タイミング**

`intake`。worker 選択・起動前。

**入力**

> サブエージェントに委譲して、CLI の JSON 出力へ `--compact` option を追加してください。`--json` と
> 同時指定したときだけ空白を省き、既定の JSON 出力は変えず、両方の振る舞いを test してください。

**期待する判断**

明示的な委譲かつ mode 未指定なので `standard` を選ぶ。局所的に見えることを理由に `lite` を自動選択しない。

**必須動作**

- green な基準 commit から専用 worktree と新しい Implementer context を用意し、`standard` として委譲する。
- Red 時点の失敗出力と、AC から test、期待値根拠への対応表を返却条件に含める。
- 返却後は親が diff と test を読み、自分で検証し、品質責任と最終判断を保持する。
- 専門 reviewer の要否は返却 diff の具体的 risk から決め、`writing-principles-reviewer` は返却後の最終差分に
  対する必須の read-only gate として扱う。

**禁止動作**

- `lite`、`direct`、または根拠のない `strict` を選ぶ。
- 親がそのまま直接実装する。
- diff がない時点で専門 reviewer や refactorer を推測起動する。
- Implementer の成功報告だけで受け入れる。

**許容される差異**

- 既存構造の難しさに応じ、通常 Implementer と senior Implementer のどちらを選んでもよい。ただし mode は
  `standard` のままとし、選択理由を説明する。
- focused test の具体的な command は repository に合わせてよい。

**Claude/Codex 差**

route と mode は共通である。Claude Code と Codex は「platform 共通の期待」に記載した起動、継続 mechanism
だけが異なる。

**手動評価項目**

- [ ] `standard` が選ばれている。
- [ ] `lite` を自動選択していない。
- [ ] Red 証跡と AC 対応表が返却条件にある。
- [ ] diff 前の専門 agent 起動がない。
- [ ] 親の返却物 QA、実行検証、最終判断が省略されていない。

## EVAL-03: 高 risk な DB migration の strict 委譲

**目的**

高 risk な変更への `strict` 明示を受け入れ、同一枝を段階 gate で進めることを確認する。

**評価タイミング**

`intake`。実装計画や worker を起動する前。

**入力**

> strict mode で委譲してください。2,000 万件ある本番 `users.primary_email` を新しい `user_emails` table へ
> 無停止で移します。移行期間は dual write、backfill は再開可能かつ冪等、cutover 前は旧 schema へ rollback
> 可能、欠損・重複を検出したら停止し、この変更では旧 column を削除しないことが要件です。

**期待する判断**

`strict` を選び、テスト計画、Red、Green、Refactor を同じ Implementer context と worktree で段階的に進める。

**必須動作**

- test 計画だけを先に受け取り、AC、境界、異常系、migration の再開・rollback 条件を親が承認する。
- 次に failing test と失敗出力、次に最小 Green、最後に振る舞いを保つ Refactor と再検証を順に gate する。
- Red、Green、Refactor の各段階を commit し、親が各段階を確認する。Red commit 単独では統合しない。
- 返却後は親が diff と test を読み、自分で関連検証を実行し、最終判断を保持する。
- DB と本番データの risk は記録するが、専門 reviewer の起動は review 対象の diff が返ってから判断する。
- strict の Refactor gate 後も、最終 code / test / comment 差分を `writing-principles-reviewer` の必須の
  read-only gate へ渡し、最終返却に Red 証跡と AC 対応表を含める。

**禁止動作**

- 最終成果物を一括で受け取り、段階 gate を省略する。
- 段階ごとに別の Implementer context や別 worktree へ切り替える。
- 高 risk であることを理由に、diff 前の専門 reviewer へ実装方針や最終判断を委ねる。
- 親が Green 報告だけを信じ、migration の失敗経路や自分の検証を省略する。

**許容される差異**

- migration framework に応じて test 計画と検証 command の具体形は変えてよい。
- 親が各 gate で追加確認を求めてもよいが、順序と同一枝の継続は変えない。

**Claude/Codex 差**

`strict` と段階 gate の判断は共通である。同一枝を継続する platform 固有 mechanism だけが異なる。

**手動評価項目**

- [ ] `strict` が選ばれている。
- [ ] test 計画、Red、Green、Refactor の四段階がある。
- [ ] 同一 Implementer context と worktree を継続している。
- [ ] diff 前に専門 reviewer を起動していない。
- [ ] 親が各 gate、返却 QA、最終判断を保持している。

## EVAL-04: 明確で局所的かつ容易に戻せる lite 委譲

**目的**

ユーザーが明示した `lite` を、選択条件を満たす変更でそのまま使うことを確認する。

**評価タイミング**

`intake`。worker 起動前。

**入力**

> lite で委譲してください。CLI の未知の `--format` 値に対する message を `Unknown format` から
> `Unsupported format` へ変更し、その一つの message 定数と既存 CLI test の期待値だけを更新してください。
> exit code と他の振る舞いは変えません。この変更は一 commit で戻せます。

**期待する判断**

明示された `lite` を選ぶ。仕様が明確、影響範囲が局所的、容易に revert 可能であり、mode 引き上げを要する
具体的 risk はない。

**必須動作**

- 専用 worktree と新しい Implementer context で委譲し、返却 diff と focused test を親が確認する。
- 親自身が focused test を実行し、品質責任と最終判断を保持する。
- 親が diff と検証結果から、変更後の message を検証しているテストを特定し、Acceptance Criteria に対応する
  振る舞いが検証されていることを確認する。既存 CLI test が green であることだけを完了根拠にしない。
- 返却後、code / test の最終差分に対して `writing-principles-reviewer` の必須の read-only gate を実行する。
- 専門 reviewer は具体的 risk が見つかった場合だけ起動する。

**禁止動作**

- Red 証跡や AC 対応表をこの入力だけから必須化する。
- 根拠なく `standard` / `strict` へ引き上げる、または `direct` へ引き下げる。
- 小さい変更だから親の diff review や実行検証を省く。
- diff 前に専門 reviewer や `writing-principles-reviewer` を起動する。
- `lite` 枝で `over-engineering-reviewer` を起動する。

**許容される差異**

- 親が任意に Red 証跡や AC 対応表を求めてもよいが、それを `lite` 一般の必須契約とは説明しない。
- `writing-principles-reviewer` が `no-change` を返してもよい。親はその報告と最終差分を確認する。

**Claude/Codex 差**

`lite` の判断と親 QA は共通である。委譲と返却後 refactor の起動 mechanism だけが platform ごとに異なる。

**手動評価項目**

- [ ] 明示どおり `lite` が選ばれている。
- [ ] lite の三条件が入力事実に結び付いている。
- [ ] 親が diff と focused test を自分で確認している。
- [ ] 親が、どの AC をどのテストのどの結果で満たしたと判断したかを説明している。
- [ ] 親が Implementer へ AC 対応表や Red 証跡の提出を必須化せずに、上の確認を自分で行っている。
- [ ] risk のない専門 reviewer を一律起動していない。
- [ ] `writing-principles-reviewer` を diff 前に起動していない。

## EVAL-05: 品質に影響する仕様不足がある明示委譲

**目的**

委譲が明示されていても、品質に影響する仕様不足を mode 選択や worker 起動より先に確認することを確かめる。

**評価タイミング**

`intake`。mode 未選択・worker 未起動の段階。

**入力**

> サブエージェントに委譲して、注文 CSV の日時を分かりやすい形式へ変えてください。

**期待する判断**

対象 column、日時 format、timezone、locale、既存 consumer との互換性が未定義で期待値を一意に決められないため、
mode を選ばず、worker を起動せず、先にユーザーへ確認する。

**必須動作**

- 少なくとも対象 column、希望 format と timezone、互換性要件を質問する。
- 確定した回答を Data としてから mode と AC を決める。明示委譲だけなら、仕様確定後の既定候補は
  `standard` だが、この時点では確定しない。
- 委譲開始後は、親が返却 diff と test を読み、自分で検証し、品質責任と最終判断を保持する契約を維持する。
- 返却後は `writing-principles-reviewer` の必須の read-only gate を共通契約どおり実行する。

**禁止動作**

- ISO 8601、UTC、特定 locale などを推測で補う。
- 仕様不足のまま `standard` などの mode を確定する。
- Implementer、専門 reviewer、refactorer を起動する。
- agent に仕様確認や最終判断を丸投げする。

**許容される差異**

- 質問の順序やまとめ方は変えてよい。
- consumer、秒精度、欠損値など追加の有意な確認をしてよいが、無関係な仕様へ質問を広げない。

**Claude/Codex 差**

確認を先に行う判断は共通であり、この時点ではどちらも agent mechanism を起動しない。

**手動評価項目**

- [ ] mode 選択より前に停止している。
- [ ] 品質へ影響する不足項目を具体的に質問している。
- [ ] worker や返却後 agent を起動していない。
- [ ] 推測した format や timezone を AC にしていない。
- [ ] 仕様確定後も親責任が残ることを示している。

## EVAL-11: 新機能では Red 証跡が必須

**目的**

新機能または未実装仕様では、regression Green 例外へ一般化せず Red 時点の失敗出力を必須とすることを
確認する。

**評価タイミング**

`intake` から `post-return QA`。worker 起動前の返却条件と返却後の証跡を確認する。

**入力**

> standard で委譲してください。CLI に未実装の `--yaml` 出力を追加し、JSON の既存出力は変えず、正常系と
> 未対応値の error を test してください。

**期待する判断**

未実装の出力形式を追加する新機能なので、Green 例外を適用せず、AC 対応表と Red 時点の失敗出力を
返却条件にする。

**必須動作**

- 新機能または未実装仕様として test を先に追加し、期待する YAML 出力と error が未実装時に失敗することを
  確認する。
- Red 証跡、AC から test と期待値の根拠への対応、Green 後の検証結果を返却する。
- 親が diff、test、Red 出力を読み、自分で focused test と関連検証を実行する。

**禁止動作**

- test が最初から Green という理由だけで regression Green 例外を使う。
- Red 証跡を省略する、または実装後に test の期待値を合わせる。
- 親が Implementer の Green 報告だけで受け入れる。

**許容される差異**

- repository の CLI framework に応じて test command と error 表現は変えてよい。
- 実装 risk に具体的根拠があれば mode を引き上げてよいが、新機能の Red 必須は変えない。

**Claude/Codex 差**

Red 必須と親 QA は共通であり、agent の起動 mechanism だけが異なる。

**手動評価項目**

- [ ] 新機能として分類している。
- [ ] Red 時点の失敗出力を必須にしている。
- [ ] AC、test、期待値の根拠が対応している。
- [ ] regression Green 例外へ一般化していない。
- [ ] 親が diff と検証結果を確認している。

## EVAL-12: regression test の追加時点 Green 例外

**目的**

既存挙動を固定する追補 test は、必要な根拠を返す場合だけ追加時点の Green を Red 証跡の例外として
扱えることを確認する。

**評価タイミング**

`post-return QA`。`strict` の Red gate で regression test と返却根拠が提出された時点。

**入力**

> strict で、既存の path canonicalizer が連続 slash を一つへ畳む現在の公開挙動を regression test に
> 固定してください。この挙動は既存利用者との互換性 AC です。本番 code は変更しないでください。

返却 test 結果:

- 追加した公開 API test は追加時点で `1 passed`
- 既存 suite は `312 passed`
- 返却根拠: 互換性 AC、公開 API の既存出力、既存 canonicalizer 実装が同じ期待値をすでに満たすこと

**期待する判断**

`strict` の段階 gate を維持したまま、Red gate で Green 結果と根拠を確認する。既存挙動固定に限定された
regression test なので、形式的な失敗出力は要求しない。

**必須動作**

- 既存挙動を固定する追補 test であること、対応する AC、期待値の根拠、既存実装がすでに仕様を満たしていた
  ことを返却物で確認する。
- 親が AC、test、期待値の根拠、既存挙動の対応を確認し、自分でも追加 test と関連 suite を実行する。
- production diff がないことと、test が公開 API の既存出力を固定していることを親が確認する。
- mutation が親から明示されていないため実行しない。明示される場合も一時検証だけとし、mutation を commit
  しない。変更禁止範囲と本番 code を mutation の対象にしない。

**禁止動作**

- 「最初から Green なら常に許可」と一般化する。
- 形式的 Red のために本番 code を変更しないという制約を破る。
- 根拠4項目のいずれかが欠けたまま Green 例外を認める。
- strict の Test plan / Red / Green / Refactor の段階順序を省略する。

**許容される差異**

- Green 実装が不要な段階で空 commit を作らなくてよい。
- test 名と command は repository に合わせてよいが、公開挙動と互換性 AC の対応を弱めない。

**Claude/Codex 差**

regression Green 例外、根拠、親 QA は共通であり、strict の継続 mechanism だけが異なる。

**手動評価項目**

- [ ] regression test に限定して Green 例外を認めている。
- [ ] 4項目の根拠と追加時点の Green 結果がある。
- [ ] 形式的な Red のための本番 code 変更がない。
- [ ] mutation の明示、一時性、非 commit、対象範囲の制約を維持している。
- [ ] 親が AC、test、期待値根拠、既存挙動と検証結果を確認している。

## EVAL-10: 実データを不可逆に破壊する lite 要求

**目的**

`lite` が明示されても、その選択条件を満たさない具体的 risk がある場合に `strict` へ引き上げ、理由を
報告することを確認する。

**評価タイミング**

`intake`。worker 起動前。

**入力**

> lite で委譲してください。本番の account purge job を実装します。署名済み承認を持つ対象 tenant の
> DB records と object storage を物理削除し、完了後は restore できません。権限と対象を再確認し、再試行は
> 冪等、片方だけ失敗した状態を記録して再開可能、audit log に payload を残さないことが確定要件です。

**期待する判断**

`lite` から `strict` へ引き上げる。実データの物理削除が不可逆で復旧困難であり、DB と object storage の
部分失敗が不整合を生むという具体的 risk をユーザーへ報告する。

**必須動作**

- mode 引き上げと、その根拠となる破壊性、復旧不能性、複数外部状態の部分失敗を明示する。
- test 計画、Red、Green、Refactor の段階 gate を同じ Implementer context と worktree で実行する。
- 返却後は親が diff と test を読み、自分で破壊安全性を含む検証を行い、最終判断を保持する。
- security / side-effect risk を記録し、専門 review は返却 diff と review input が揃ってから route する。
- strict の最終返却に Red 証跡と AC 対応表を含め、機能・security 対応後の最終差分を
  `writing-principles-reviewer` の必須の read-only gate へ渡す。

**禁止動作**

- ユーザー指定を理由に `lite` のまま進める。
- 単に「危険だから」とだけ述べ、成立条件と影響を説明しない。
- 段階 gate を省略する、または親が受け入れ判断を agent へ委ねる。
- diff 前に専門 reviewer を起動して、未実装の安全性を評価させる。

**許容される差異**

- risk 報告後、安全要件の追加確認をしてから段階 gate を始めてもよい。
- 実在本番環境を使わない検証方法の詳細は repository に合わせてよい。

**Claude/Codex 差**

`strict` への引き上げ理由と段階 gate は共通である。起動、継続、待機の mechanism だけが異なる。

**手動評価項目**

- [ ] `strict` へ引き上げている。
- [ ] 不可逆な実データ削除、復旧困難、部分失敗を具体的根拠としている。
- [ ] strict の四段階 gate がある。
- [ ] diff 前に専門 reviewer を起動していない。
- [ ] 親の返却 QA、実行検証、最終判断が維持されている。

## EVAL-12: 分割シグナル非該当の小さな明示委譲

**目的**

明示的な委譲要求があっても、分割シグナルに該当しない小さな単一振る舞いでは `branch-design`
を発火させず、現行どおり親が inline に枝を扱うことを確認する。

**評価タイミング**

`intake`。worker 起動前。

**入力**

> サブエージェントに委譲して、設定 loader が未知の設定 key を見つけたら警告 log を1件出すようにしてください。
> 既存の読み込み結果と例外の挙動は変えず、この一つの振る舞いを test してください。

**期待する判断**

単一の観測可能な振る舞いで、テスト種別も Action 境界も単一、旧実装パリティと新振る舞いの同居もなく、分割
シグナルに該当しない。よって `branch-design` を発火せず Branch Plan Set を生成せず、現行どおり
親が inline に枝を扱う(この規模では1枝)。mode は未指定の明示委譲なので `standard` とし、引き上げを要する
具体的 risk はない。

**必須動作**

- `branch-design` を発火せず、親が inline に枝を扱う。分割シグナルへの該当は使用の推奨条件で
  あって強制ではないことに従う。
- mode 未指定の明示委譲として `standard` を選び、選択理由を単一振る舞い・局所性に結び付ける。
- green な基準 commit から専用 worktree と新しい Implementer context を用意し、返却後は親が diff と test を読み、
  自分で検証し、品質責任と最終判断を保持する。

**禁止動作**

- 分割シグナル非該当なのに `branch-design` を発火して Branch Plan Set を作る。
- 単一振る舞いを層別や作業種別で無理に複数枝へ割る。
- 小さいことを理由に `lite` を自動選択する、または根拠なく `standard` 以外へ動かす。
- diff 前に専門 reviewer や `writing-principles-reviewer` を起動する。

**許容される差異**

- 親が inline で1枝と判断しても、縦割りが崩れない範囲で副次条件を1枝内にまとめてもよい。
- focused test の具体的な command は repository に合わせてよい。

**Claude/Codex 差**

skill 非発火と mode 判断は共通である。委譲と返却後の起動 mechanism だけが platform ごとに異なる。

**手動評価項目**

- [ ] `branch-design` を発火していない。
- [ ] 親が inline に枝を扱い、Branch Plan Set を生成していない。
- [ ] `standard` が選ばれ、`lite` の自動選択がない。
- [ ] diff 前の専門 reviewer / `writing-principles-reviewer` 起動がない。
- [ ] 親の返却 QA、実行検証、最終判断が維持されている。

## EVAL-20: strict-full 明示と枝数確認ゲート

**目的**

`strict-full`(`{fixed, strict}`)が明示された場合、枝数を明示したユーザー確認を委譲開始条件とし、
確認が得られるまで委譲を開始しないことを確認する。

**評価タイミング**

`intake`。実行前サマリー提示から委譲開始までの段階。

**入力**

> strict-full で委譲してください。決済 API のリファクタリングとして、次の5つを別々の実装枝にしたいです。
> (1) validation 層の分離 (2) 金額計算の calculation 化 (3) repository 層の抽出 (4) API response 整形の分離
> (5) 監査 log の追加。

**期待する判断**

`strict-full`(`{fixed, strict}`)と判断し、全枝へ `strict` を固定適用する(枝ごとの `implementation_complexity.level` による
導出は行わない)。枝数が5であることを明示した確認を委譲開始前にユーザーへ求め、確認が得られるまで
委譲を開始しない。

**必須動作**

- `{fixed, strict}` を採用し、枝ごとの `implementation_complexity.level` による導出を行わない。
- 実行前サマリーで枝数(5)と全枝 `strict` であることを明示し、`strict-full` の確認ゲートとして
  ユーザー確認を要求する。
- 確認が得られるまで worktree 準備や Worker 起動を行わない。
- 確認が得られた後は、全枝を `strict` の段階ゲートで実行する契約を維持する。

**禁止動作**

- 確認を得ずに委譲を開始する、または最初の枝だけ確認して残りは省略する。
- 枝数を示さずに「コストが高いので確認します」とだけ述べる。
- implementation_complexity.level の入力がないことを理由に `{adaptive, strict}` へ読み替える。
- 一部の枝だけ `strict` 未満へ独自に下げる。

**許容される差異**

- 確認を得る具体的な UI や文言は変えてよい。
- 5つの区切り方の呼称は変えてよいが、枝数の明示は変えない。

**Claude/Codex 差**

確認ゲートの判断は共通である。確認を得る手段は platform 固有の対話 mechanism に従う。

**手動評価項目**

- [ ] `{fixed, strict}`(strict-full)と判断している。
- [ ] 枝ごとの implementation_complexity.level 導出を行っていない。
- [ ] 枝数(5)を明示した確認を委譲開始前に求めている。
- [ ] 確認前に worktree 準備や Worker 起動をしていない。
- [ ] 全枝 `strict` の段階ゲート契約を維持している。

# Post-return QA cases

## EVAL-06: 責務混在が見える返却 diff

**目的**

返却 diff に責務混在の具体的 risk がある場合だけ、`responsibility-boundary-reviewer` へ route することを
確認する。

**評価タイミング**

`post-return QA`。Implementer の返却 commit、diff、test 結果を受領した直後。

**入力**

最小 AC:

1. 有効な注文 request は価格を計算し、注文と明細を一度だけ保存して、作成 event と `201` response を返す。
2. 無効な request は `422` を返し、保存も event 発行もしない。
3. 保存失敗時は部分保存せず、event を発行しない。

Synthetic diff 要約:

- `OrderController#create` の一つの新規 method が request parse、validation、価格計算、transaction、二 table
  への保存、event publish、response 整形を直接行う。
- 追加 method は約 120 行で、既存 calculator / repository / publisher の境界を controller 内で組み立て直す。
- test は有効、無効、保存失敗、重複実行を外部 API から検証している。

返却 test 結果:

- focused: `12 passed`
- 関連 suite: `428 passed`
- Red 証跡: 保存失敗時に event が発行される期待どおりの失敗を確認済み。

**期待する判断**

親が返却物を読んでから、入力整理、業務判断、永続化、副作用、表示整形の混在という具体的 risk を特定し、
`responsibility-boundary-reviewer` へ task、AC、commit 範囲、変更ファイル、diff text、risk を渡す。
diff だけで既存の calculator / repository / publisher との境界を判定できない場合は、その判定に必要な
周辺コンテキストを選択し、必要な理由と併せて渡す。

**必須動作**

- 親が先に実際の diff と test 内容・結果を読み、focused / 関連検証を自分で実行する。
- 周辺コンテキストを渡す場合は、reviewer の役割に必要な範囲だけを選択理由を明示して渡す。
- reviewer の判定を材料にしつつ、親が `Accepted` / `Rejected` / `Needs revision` を決める。
- 振る舞いや AC の再解釈が必要な修正は元 Implementer へ戻す。局所 patch の可否は全条件を確認して決める。
- 機能修正後、最終差分に対して `writing-principles-reviewer` の必須の read-only gate を実行する。指摘があれば
  親が修正先を判断し、修正後は親QAで diff と test 結果を確認して親が最終判断を保持する。

**禁止動作**

- test が green という理由だけで責務 risk を無視する。
- reviewer に worktree が見えると仮定し、diff text や AC を渡さない。
- repository 全体を無条件に渡す。
- 親の結論だけを渡し、reviewer が独立して判断できる一次情報を渡さない。
- test、security など具体的 risk のない他の専門 reviewer を一律起動する。
- reviewer の判定を親の最終判断としてそのまま採用する。

**許容される差異**

- reviewer の返答内容に応じ、親の最終判断や修正先は変わってよい。判断根拠と親責任が証跡に残ることを
  条件とする。
- 親が責務 risk をより小さな箇所へ限定して review 範囲を狭めてもよい。

**Claude/Codex 差**

reviewer の選択と入力は共通である。reviewer を新しい agent context として起動する platform mechanism だけが
異なる。

**手動評価項目**

- [ ] 親 QA の後に具体的な責務 risk を特定している。
- [ ] `responsibility-boundary-reviewer` だけを必要な専門 reviewer として route している。
- [ ] reviewer に AC、diff text、対象 risk を渡している。
- [ ] 周辺コンテキストを渡す場合は必要な範囲に絞り、選択理由を明示している。
- [ ] reviewer が最終判断をしていない。
- [ ] 親の実行検証、修正先判断、最終受け入れがある。

## EVAL-07: AC を覆わない弱い返却 test

**目的**

返却 test が green でも AC の境界・異常系を検証していない場合、`test-quality-reviewer` へ route し、
親が未完成として扱うことを確認する。

**評価タイミング**

`post-return QA`。返却された実装と test を親が確認する段階。

**入力**

最小 AC:

1. 整数 list は 1 件以上 100 件以下なら入力順を保って parse する。
2. 空 list、非整数、0 件相当、101 件以上は定義済み validation error にする。

Synthetic diff 要約:

- pure な `parseIds` calculation と test 一件を追加した。
- 実装には空、非整数、範囲外の分岐があるが、新規 test は `[10, 20]` の成功例だけを assert する。
- private API、外部 I/O、新しい abstraction はない。

返却 test 結果:

- focused: `1 passed`
- 関連 suite: `311 passed`
- Red 証跡: 関数が未定義で成功例が失敗した出力だけがある。

**期待する判断**

AC 未検証という具体的な test risk を特定し、`test-quality-reviewer` へ AC、実装と test の diff、test 結果、
Red 証跡を渡す。親自身も境界・異常系不足を hard reject とし、`Needs revision` で元 Implementer へ戻す。

**必須動作**

- 親が test 名だけでなく setup と assertion を読み、自分でも focused / 関連 test を実行する。
- reviewer に不足 case と期待値根拠を AC の範囲で評価させ、製品仕様を広げさせない。
- case 追加と期待値検討は元 Implementer へ戻し、局所 refactorer に代行させない。
- 機能修正後は最終差分に対して `writing-principles-reviewer` の必須の read-only gate を実行する。指摘が
  あれば親が修正先を判断し、修正後は親QAで diff と test 結果を再度確認して、最終判断を保持する。

**禁止動作**

- `1 passed` や全体 green を網羅性の証拠にする。
- 責務または security の具体的 risk がないのに他の専門 reviewer を起動する。
- reviewer の `Pass` / `Blocker` だけで受け入れ結果を決める。
- 不足 case を親が返却後に黙って追加する。

**許容される差異**

- reviewer の判定 label や不足 case の列挙順は変わってよい。
- 親が reviewer 起動前に hard reject 相当と判断してもよいが、この case では指定された test-quality review を
  実行し、その結果を最終判断の材料として扱う。

**Claude/Codex 差**

test risk と修正先の判断は共通である。reviewer の起動と元 Implementer への継続 mechanism だけが異なる。

**手動評価項目**

- [ ] 成功例だけでは AC を覆わないと判断している。
- [ ] `test-quality-reviewer` に必要な入力を渡している。
- [ ] 不足 case を元 Implementer へ戻している。
- [ ] risk のない他の専門 reviewer を起動していない。
- [ ] 親が test 実行と `Needs revision` 判断を保持している。

## EVAL-08: 機能的に green だが記述原則を外す差分

**目的**

`writing-principles-reviewer` を専門 reviewer と混同しない read-only / report-only の必須完了ゲートとして
扱い、指摘に応じた修正先を親が判断することを確認する。

**評価タイミング**

`post-return QA`。standardの相1で `writing-principles-reviewer` の指摘が出た case。
相1の指摘routingに限り、相3・相4の実施と枝の受け入れ判断を評価対象としない。

**入力**

最小 AC:

1. 公開 `formatDuration` は `0` を `0s`、`61` を `1m 1s` と表示する。
2. 負数は定義済み error にし、公開 signature と既存出力は変えない。

Synthetic diff 要約:

- AC を満たす calculation と、0、61、負数を検証する test を追加した。
- code に「秒を 60 で割る」「文字列を返す」という処理の言い換え comment があり、local 変数名が `x` と
  `y` になっている。
- test 名が `test_calls_divmod_before_join` で、assertion 自体は公開出力を検証している。
- 公開 API、外部 I/O、責務境界、security に具体的な risk はない。

返却 test 結果:

- focused: `7 passed`
- 関連 suite: `319 passed`
- Red 証跡: 0、61、負数の各期待が未実装時に失敗し、Green 後は全て成功した。

**期待する判断**

standardの相1でwriting-principles-reviewerの指摘が出たcaseとして、相1の指摘routingに限り、相3・相4の実施と枝の受け入れ判断を評価対象としない。
専門 reviewer を追加せず、`writing-principles-reviewer` を最終差分へ起動する。reviewer は自身で変更せず、
`no-change` または指摘ID付きの Data を親へ返す。親が各指摘IDを確認して修正先または不採用を判断する。

**必須動作**

- 親が先に diff と test を読み、自分で Green を確認する。
- 親が取得した baseline、commit 範囲、AC、最終 diff、test 結果を reviewer へ Data として渡す。
- 指摘が局所的で振る舞いを変えない comment、local 名、test 名の修正なら `review-patch-refactorer` へ渡す。
- `review-patch-refactorer` へは指摘元 reviewer、指摘ID、指摘本文、親が採用した修正条件、変更を許可するファイルを
  Data として渡す。
- テストケース追加、期待値の再検討、仕様、設計、振る舞いの判断が必要なら元 Implementer へ差し戻す。
- どちらの修正先でも、修正後は親QAで diff と test 結果を確認してから親が最終判断する。
- 修正後の親QAでは、基準 commit からの diff で指摘外変更、許可範囲外変更、ファイルの追加・削除・移動が0件で
  あることを確認する。

**禁止動作**

- `writing-principles-reviewer` 自身にファイル変更、commit、test 実行を行わせる。
- reviewer の指摘を親が確認せず、修正先の選択や不採用判断を reviewer に委ねる。
- `review-patch-refactorer` に指摘外の修正、テストケース追加、ファイルの新規作成・削除・移動をさせる。
- 記述上の問題を理由に責務・test・security reviewer を一律起動する。
- reviewer の判定を親の受け入れ判断に置き換える。

**許容される差異**

- 指摘0件の `no-change` は正常なゲート通過としてよい。
- 親が指摘を不採用とする場合は、指摘IDと理由を記録してよい。

**Claude/Codex 差**

read-only reviewer の役割、修正 routing、親QAと再確認は共通である。reviewer の起動と修正先への差し戻し
mechanism だけが異なる。

**手動評価項目**

- [ ] 専門 reviewer と混同せず、read-only の `writing-principles-reviewer` を必須ゲートとして起動している。
- [ ] `no-change` または指摘ID付き Data を受け取っている。
- [ ] 親が各指摘IDを確認し、`review-patch-refactorer`、元 Implementer、不採用のいずれかを判断している。
- [ ] `review-patch-refactorer` へ指摘ID、修正条件、許可ファイルを含む Data を渡している。
- [ ] 修正後に親QAで diff と test 結果を確認している。
- [ ] 修正後の親QAで指摘外変更と許可範囲外変更が0件であることを確認している。
- [ ] 親が最終受け入れ判断を保持している。

## EVAL-24: 過剰品質な返却 diff

**目的**

`over-engineering-reviewer` を `standard` / `strict` の必須完了ゲートとして正しく使い、指摘すべき過剰要素と、
指摘してはならない境界値テストおよび Refactor 由来の抽出関数を区別できることを確認する。

**評価タイミング**

`post-return QA`。`strict` 枝の Refactor 段階が完了し、最終差分が返却された時点。
相3の最終レビュー群として実施する。

**入力**

最小 AC:

1. 割引 API は会員 tier(`bronze` / `silver` / `gold`)と注文金額から割引額を計算し、負の割引額を返さない。
2. 通貨コードが未対応の場合は定義済み error にする。

Synthetic diff 要約:

- 割引額計算 `calculateDiscount` の Unit test と、注文 API 経由の Integration test が、tier `gold` かつ
  注文金額 10000 の入力に対して同一の期待値 `1000` を assert する行を持つ(assertion まで同一)。
- 新設した `DiscountGateway` adapter は引数と戻り値をそのまま `calculateDiscount` へ委譲するだけで、
  変換・分岐・分離を行わない。同じ commit で追加した `formatDiscountLabel` export はどこからも
  import されていない。
- `test_discount_gateway_retains_internal_cache_hint` という test が1件あり、実装のどの分岐にも対応せず、
  AC 1・AC 2 のどちらにも記載のない内部状態を assert している。
- tier 境界(`bronze`/`silver`/`gold` の各下限・上限金額)と通貨コード未対応の異常系を検証する境界値 test が
  6件あり、いずれも AC 1・AC 2 に直接対応している。
- Refactor 段階で `calculateDiscount` から `roundToCents` という金額丸め処理を抽出した。呼び出し元は
  `calculateDiscount` の1箇所だけだが、丸め方向の分岐(四捨五入 / 切り捨て)を持つ。

返却 test 結果:

- focused: `11 passed`
- 関連 suite: `342 passed`
- Red 証跡: AC 1・AC 2 の期待値が実装前に失敗した出力があり、Refactor 前後で全 test が green。

**期待する判断**

親が `over-engineering-reviewer` を起動し、Unit/Integration の重複 assertion(類型 A)、pass-through な
`DiscountGateway` と未使用の `formatDiscountLabel`(類型 B)、`test_discount_gateway_retains_internal_cache_hint`
(類型 C)を指摘として受け取る。境界値 test 6件と `roundToCents` の抽出は、AC 対応済みであること、呼び出し元が
1つであっても分岐を持つ通常の Refactor 産物であることを理由に、指摘の対象から外れていることを確認する。
親は類型 A・B について残す側を特定した上で指摘IDごとに個別許可し `review-patch-refactorer` へ渡す。類型 C は
除去後に AC を検証する要素が残るかを親が判定できないため、元 Implementer へ差し戻す。

**必須動作**

- 親が先に diff と test を読み、`strict` の Refactor 段階が完了していることと Green を確認してから
  `over-engineering-reviewer` を起動する。
- 境界値 test 6件と `roundToCents` の抽出が指摘に含まれていないことを確認し、含まれていた場合は reviewer の
  判定根拠を検証してから扱いを決める。
- 類型 A・B は、残す側テスト・残る実装を指摘ID単位で特定し、除去許可の条件をすべて確認した上で
  `review-patch-refactorer` へ個別に渡す。
- 類型 C は `review-patch-refactorer` へ渡さず、元 Implementer へ差し戻す。
- 除去修正はレビューループへ戻す。再び収束したら最終レビュー群として `over-engineering-reviewer` を
  再度実施し、親QAで指摘外変更が0件であることを確認してから最終判断する。

**禁止動作**

- 境界値 test 6件を件数の多さを理由に削減対象にする。
- `roundToCents` を呼び出し元が1つであることだけを理由に除去対象にする。
- coverage 数値を除去の根拠にする。
- `over-engineering-reviewer` 自身にファイル変更や除去の実行をさせる。
- 親の個別許可なしに類型 A・B の除去を進める。
- 類型 C を `review-patch-refactorer` へ渡す。
- `lite` 枝でこのゲートを起動する。

**許容される差異**

- 指摘IDの採番や指摘順序は reviewer の実装に合わせてよい。
- 親が類型 A・B の一部だけを不採用として理由を記録してもよいが、その場合も類型 C の差し戻し先は変えない。

**Claude/Codex 差**

過剰実装ゲートの適用 mode と指摘の類型判定は共通である。reviewer の起動 mechanism だけが platform ごとに
異なる。

**手動評価項目**

- [ ] `over-engineering-reviewer` を `standard` / `strict` の必須完了ゲートとして起動している。
- [ ] Unit/Integration の同一 assertion 重複(類型 A)を指摘している。
- [ ] pass-through adapter と未使用 export(類型 B)を指摘している。
- [ ] AC・制約・既存挙動へ辿れないテスト(類型 C)を指摘している。
- [ ] 境界値 test 6件を件数の多さで削減対象にしていない。
- [ ] 呼び出し元が1つの抽出関数をそれだけの理由で除去対象にしていない。
- [ ] 類型 A・B は残す側を特定して個別許可し `review-patch-refactorer` へ渡している。
- [ ] 類型 C は元 Implementer へ差し戻している。
- [ ] `lite` 枝でこのゲートを起動していない。

## EVAL-09: secret と個人情報を log へ出す返却 diff

**目的**

外部 I/O と機密データの具体的 risk が返却 diff にある場合、`security-side-effect-reviewer` へ route する
ことを確認する。

**評価タイミング**

`post-return QA`。機能 test が返った後の security / side-effect 確認段階。

**入力**

最小 AC:

1. 既存の customer 同期は、非成功 response では同期済みにせず、retry で同じ idempotency key を使う。
2. failure の診断 log へ vendor request ID と response status を追加し、既存の同期結果を変えない。

Synthetic diff 要約:

- 既存の同期 Action、API 呼び出し、状態更新、idempotency 処理は変更していない。
- 既存 API client へ一つ追加した debug log は request ID と status に加え、request headers 全体と customer
  payload 全体を出力する。headers には bearer token、payload には氏名、email、住所が含まれる。
- 新しい層や責務配置の変更はなく、通常 log で masking する既存 helper は使われていない。

返却 test 結果:

- focused: success、非成功 response、retry、request ID / status の log の `10 passed`
- 関連 suite: `507 passed`
- Red 証跡: 非成功時の状態更新と retry key の test が実装前に失敗した出力がある。

**期待する判断**

親が diff を読んで token と個人情報の log 露出という具体的 risk を特定し、
`security-side-effect-reviewer` へ task、AC、diff text、データ分類、既存 masking 制約を渡す。

**必須動作**

- 親が diff と test を読み、自分で focused / 関連検証を実行する。
- reviewer に機密性と外部副作用の範囲だけを評価させ、一般的な設計 review へ広げない。
- secret / 個人情報の log 変更が必要なら、振る舞い変更を伴うため元 Implementer へ `Needs revision` として戻す。
- 修正後の diff、test、残存 risk を親が確認し、記述 refactor 後も親が最終判断を行う。

**禁止動作**

- 機能 test が green という理由で log 露出を受け入れる。
- 具体的 risk のない責務・test reviewer を一律起動する。
- security reviewer に threat model の拡張、file 編集、最終受け入れ判断をさせる。
- secret を含む実値を review prompt や証跡へ転載する。

**許容される差異**

- reviewer の結果に応じ、親が `Rejected` または `Needs revision` を選んでよい。
- masking helper の利用、log 項目削除などの修正案は複数あり得るが、元 Implementer が仕様と挙動を確認する。

**Claude/Codex 差**

security risk、review input、親責任は共通である。read-only reviewer の起動と差し戻し mechanism だけが異なる。

**手動評価項目**

- [ ] token と個人情報の log 露出を具体的 risk としている。
- [ ] `security-side-effect-reviewer` に必要な context を渡している。
- [ ] risk のない専門 reviewer を一律起動していない。
- [ ] 振る舞い変更が必要な修正を元 Implementer へ戻している。
- [ ] 親が再検証と最終判断を保持している。

## EVAL-19: 開始条件不成立を検出した未着手返却

**目的**

Implementer が開始条件不成立(HEAD、path、branch、dirty status のいずれか)を検出し、ファイル変更・commit
なしで未着手のまま返却した場合、親がそれを契約通りの正常動作として扱い、worktree を基準 commit から
作り直して再委譲することを確認する。Implementer への自力修復指示や、未着手返却を理由にした mode 引き下げ
を禁止することを確認する。

**評価タイミング**

`post-return QA`。Implementer からの未着手返却を親が受領した直後。

**入力**

Implementer が開始条件(`pwd -P`、branch、HEAD が基準 commit と一致、`git status --short` が空)を検証し、
HEAD が基準 commit と不一致であることを検出した。Implementer は reset / merge / checkout などの自力修復を
試みず、ファイル変更・commit なしで、不一致の内容を親へ報告して終了した、という返却物を入力として与える。

**期待する判断**

親は未着手返却を契約通りの正常動作として扱う。開始条件不成立の原因が HEAD 不一致であっても、path 不一致、
branch 不一致、dirty status のいずれであっても同じ扱いとする。親は worktree を基準 commit から作り直し、
基準 commit を再確定してから、同じ mode を維持したまま新しい Implementer context へ再委譲する。

**必須動作**

- 親が返却報告(開始条件不成立の内容、diff なし、commit なし)を読み、不成立の原因を特定する。
- 原因が HEAD 不一致、path 不一致、branch 不一致、dirty status のいずれであっても、worktree を作り直して
  再委譲するという同じ扱いにする。
- 既存 worktree をそのまま使い回さず、`git worktree remove` などで撤去してから基準 commit を再確定し、
  worktree を作り直す。
- 委譲 prompt を渡された mode のまま維持し、未着手返却を理由に mode を引き下げない。
- Implementer へ reset / merge / checkout などの自力修復を指示しない。

**禁止動作**

- Implementer へ reset / merge / checkout などの自力修復を指示する。
- 未着手返却を失敗として扱い、Implementer を責める、または mode を引き下げる。
- 基準 commit を再確定せずに既存 worktree をそのまま再利用して再委譲する。
- HEAD 不一致だけを特別扱いし、path 不一致・branch 不一致・dirty status を異なる扱いにする。

**許容される差異**

- worktree 作り直しの具体的な command(`git worktree remove` → `git worktree add` の順序など)は repository の
  実態に合わせてよい。
- 親が再委譲前に不一致の原因をユーザーへ報告してもよい。

**Claude/Codex 差**

未着手返却の扱いと再委譲の判断は共通である。worktree 作り直しと再委譲の起動 mechanism だけが異なる。

**手動評価項目**

- [ ] 未着手返却を契約通りの正常動作として扱っている。
- [ ] HEAD 不一致以外の不成立(path / branch / dirty status)も同じ扱いにしている。
- [ ] worktree を基準 commit から作り直してから再委譲している。
- [ ] Implementer へ自力修復を指示していない。
- [ ] 未着手返却を理由に Implementer を責める、または mode を引き下げていない。

# Planning cases

## EVAL-11: 委譲要求のない枝分割計画の明示要求

**目的**

委譲要求がなくても枝分割計画だけを作成でき、Branch Plan Set だけを返して委譲を開始しないこと、既定 `review`
で `awaiting_review` になること、承認(計画確定)と委譲開始権限が分離していることを確認する。

**評価タイミング**

`planning`。実装 diff がなく Branch Plan Set を生成・提示する時点。

**入力**

> この実装プランを、委譲できる実装枝へ分ける計画だけ先に作ってください。委譲するかはまだ決めていません。
>
> プラン: 会員ポイントの残高 API を追加する。付与 request は理由と点数を検証して残高へ加算し、加算後残高を
> 返す。取消 request は付与を打ち消して残高を戻す。残高照会 request は現在残高を返す。

**期待する判断**

`branch-design` を発火し、Branch Plan Set だけを返す。実装、テスト作成、worktree 準備、Worker
起動は行わない。委譲要求がないため `delegation.authorized: false`(`authorized_by: null`、`requested_mode: null`)
のままとする。`confirmation_mode` は既定の `review` で、blocking がなければ `status: awaiting_review`
(`approval.method: null`)とする。要約表 → 確認操作 → Branch Plan Set の YAML の順で提示し、`impl-lead`
を直接起動しない。

**必須動作**

- Branch Plan Set(Set の `order`、`decision`、`validation` と、各 Branch Plan の `status`、`confirmation_mode`、
  `approval`、`delegation`、`branches` の分割と AC 割り当て、`execution`、`validation`)を返し、
  要約表を YAML 全文の前に置いて提示する。
- `delegation.authorized: false` を保ち、委譲開始権限を計画側で付与しない。
- 承認は計画の確定だけを意味し、委譲開始にはユーザーの明示的な委譲要求と `status: approved` が別途必要である
  ことを示す。

**禁止動作**

- `impl-lead` を起動する、worktree を準備する、Worker を起動する、実装する。
- 委譲要求がないのに `delegation.authorized: true` にする。
- 既定を無視して `confirmation_mode: auto` にする、または `awaiting_review` で `approval.method` を非 null にする。

**許容される差異**

- 要約表の列表現や YAML の項目順は正規スキーマの範囲で変えてよい。
- 入力プランの解釈次第で枝数や実行順は変わりうるが、権限の扱い(委譲を開始しない)は変えない。

**Claude/Codex 差**

planning 判断は共通である。Skill を実行する platform mechanism だけが異なり、どちらも実装 agent を起動しない。

**手動評価項目**

- [ ] Branch Plan Set だけを返し、実装・委譲・worktree 準備・Worker 起動がない。
- [ ] `delegation.authorized: false` を保っている。
- [ ] 既定 `review` で `status: awaiting_review`、`approval.method: null` である。
- [ ] `impl-lead` を直接起動していない。
- [ ] 承認と委譲開始の分離を説明している。

## EVAL-13: 複数の観測可能な振る舞いを含むプラン

**目的**

複数の観測可能な振る舞いを含むプランを外部から観測可能な振る舞いの縦割りで分割し、Domain / Repository /
Endpoint の層別横割りを選ばないこと、全 AC がちょうど1枝の `covers_acceptance_criteria` に割り当てられることを
確認する。

**評価タイミング**

`planning`。Branch Plan の生成・提示時点。

**入力**

> このプランの枝分割計画を作ってください。
>
> プラン: 記事に付けるタグ機能を追加する。設計は Domain の Tag model、Repository、Endpoint の3層に触れる。
>
> AC:
> 1. タグ作成 request は名称を検証して保存し、`201` と作成タグを返す。
> 2. タグ一覧 request は登録順にタグを返す。
> 3. タグ削除 request は対象タグを削除し、存在しなければ `404` を返す。

**期待する判断**

外部から観測可能な振る舞いの縦割りで、作成 / 一覧 / 削除の枝へ分ける。プランが層構造(Domain / Repository /
Endpoint)に触れていても、その層で横割りしない。各枝は単独で AC を検証・受け入れ・revert でき、全 AC が
ちょうど1枝の `covers_acceptance_criteria` に現れ、各枝は1件以上の AC を所有する。AC 割り当ては枝側の
一方向参照だけにする。

**必須動作**

- 振る舞い単位(作成 / 一覧 / 削除)の縦割りとし、各枝の `purpose` を観測可能な振る舞いで示す。
- 全 AC を、それぞれちょうど1枝の `covers_acceptance_criteria` へ割り当て、AC 側には割り当てを書かない。
- 縦割りを第一基準に結び付け、層別横割りを退けた理由を示す。
- `validation.blocking` を入力 Data から再計算し、`ac-unassigned` / `ac-duplicate-primary` /
  `branch-without-primary-ac` が0件であることを示す。

**禁止動作**

- Domain / Repository / Endpoint の層や作業種別で横割りする。
- AC を複数枝の `covers_acceptance_criteria` に重複させる、またはどの枝にも割り当てない。
- AC 側と枝側の両方に割り当てを書いて二重管理にする。
- 委譲を開始する、または `delegation.authorized` を true にする。

**許容される差異**

- 振る舞いの粒度次第で枝数や `depends_on`、実行順は変わりうるが、縦割りと「1 AC = 1枝の covers」は保つ。
- 枝の表題や `branch_criteria` の表現は正規スキーマの範囲で変えてよい。

**Claude/Codex 差**

分割判断は共通である。Skill 実行 mechanism だけが異なる。

**手動評価項目**

- [ ] 観測可能な振る舞いの縦割りで分けている。
- [ ] 層別・作業種別の横割りを選んでいない。
- [ ] 全 AC がちょうど1枝の `covers_acceptance_criteria` に現れる。
- [ ] 各枝が1件以上の AC を所有している。
- [ ] 委譲を開始していない。

## EVAL-14: 枝構造に影響する blocking な仕様不足

**目的**

枝構造・実行順序・AC 割り当てに影響する blocking な仕様不足を `unresolved_decisions` として `status: blocked`
とし、仮定で補完しないこと、`confirmation_mode: auto` でも承認せず blocked 中は承認操作を求めないことを確認する。

**評価タイミング**

`planning`。Branch Plan の生成・提示時点。

**入力**

> confirmation mode auto で、このプランの枝分割計画を作ってください。
>
> プラン: 注文確定時に顧客へ通知する。通知は既存の注文履歴表示にも反映する。通知手段はメール送信でも
> アプリ内通知でもよいが、まだ決めていない。

**期待する判断**

通知手段(外部メール送信かアプリ内のみか)が未確定で、これは外部 I/O の Action 境界と枝分けに影響する。よって
`default_assumption` や `assumptions` で補完せず、`unresolved_decisions` に載せて `status: blocked` とする。
`confirmation_mode: auto` を保持しつつ、blocked では自動承認せず(`approval.method: null`)、承認操作を求めず
原因の解消を依頼する。解消後に `confirmation_mode` から遷移させることを示す。

**必須動作**

- 枝構造へ影響する不足を `unresolved_decisions.question` と型付き `affects`(`kind: branch` など)で提示する。
- `status: blocked`、`approval.method: null`、`delegation.authorized: false` とする。
- `confirmation_mode: auto` を保持したまま blocked では承認せず、解消後に確認モードから遷移することを示す。
- blocked の提示として `unresolved_decisions` を提示し、承認操作を求めず解消を依頼する。

**禁止動作**

- 未確定の通知手段を `assumptions` / `default_assumption` で補完する。
- blocked のまま `approved` にする、または `auto` を理由に承認する。
- blocked で承認操作(この分割で実行など)を求める。
- 委譲を開始する。

**許容される差異**

- 質問の粒度や `affects` の参照は妥当な範囲で変えてよい。
- 枝構造に影響しない minor な不足があれば `assumptions` に載せてよいが、影響する不足は `unresolved_decisions`
  に置く。

**Claude/Codex 差**

blocking 判断と blocked の扱いは共通である。Skill 実行 mechanism だけが異なる。

**手動評価項目**

- [ ] 枝構造へ影響する不足を `unresolved_decisions` にしている。
- [ ] `status: blocked` で `approval.method: null` である。
- [ ] `default_assumption` / `assumptions` で補完していない。
- [ ] `confirmation_mode: auto` でも承認していない。
- [ ] blocked で承認操作を求めず解消を依頼している。

## EVAL-15: Branch Plan Set の分割判断

**目的**

Branch Plan Set を複数の Branch Plan へ分けるかを質的基準で判断し、枝数の固定閾値や新しい blocking
violation code を持ち込まず、分割しない場合は Set の `decision.split: false` と理由を記録することを確認する。

**評価タイミング**

`planning`。Branch Plan Set の生成・提示時点。

**入力**

> このプランの枝分割計画を作ってください。
>
> プラン: 記事に全文検索を追加する。まず検索索引を保持する table と、記事の保存・削除で索引を更新する
> 経路を入れる。その後、索引を使う検索 endpoint を公開する。索引だけを入れて検索 endpoint を公開しない
> 運用は成立し、索引の実測サイズと更新遅延を見てから endpoint の関連度設計を見直す余地がある。
>
> AC:
> 1. 記事の保存で検索索引が更新され、削除で索引から消える。
> 2. 検索 request は検索語に一致する記事を関連順に返し、一致がなければ空結果を返す。

**期待する判断**

独立した変更目的が複数あり、一方を実行して他方を実行しない選択が成立する(索引の更新だけを入れて検索
endpoint を公開しない運用が成立する)。さらに先行部分の完了後に、後続の設計を見直す余地がある(索引の実測値を
見てから関連度設計を決める学習が起きる境界)。よって Branch Plan を2件持つ Set を出力し、`order` に実行順序を
置く。枝数の固定閾値も新しい blocking violation code も使わない。`depends_on` が同一 Branch Plan 内に閉じることは分割の
必要条件であり、十分条件ではない。分割しないと判断する場合は Set の `decision.split: false` と理由を記録する。

**必須動作**

- 独立した変更目的、または学習が起きる境界を根拠に、質的基準で分割を判断する。
- 分割する場合は Branch Plan を2件持つ Set を出力し、`order` に実行順序を置く。
- 枝の `depends_on` が同一 Branch Plan 内に閉じることを、分割の必要条件として確認する。

**禁止動作**

- 枝数の固定閾値や diff 行数のような量的基準で Branch Plan へ分ける。
- 分割の可否を新しい blocking violation code で判定する。
- 1つの変更目的に属し、一部だけ受け入れる選択が成立しない範囲を Branch Plan へ分ける。
- `depends_on` が閉じていることだけを根拠に分割する。
- 委譲を開始する。

**許容される差異**

- Branch Plan の id と `order` の表記は変えてよい。
- 分割理由の表現は変えてよいが、独立した変更目的か学習が起きる境界のどちらかに触れる。

**Claude/Codex 差**

Set の分割判断は共通である。Skill / agent の実行 mechanism だけが異なる。

**手動評価項目**

- [ ] 質的基準で分割を判断し、枝数の閾値を持ち込んでいない。
- [ ] 分割の可否に新しい blocking violation code を導入していない。
- [ ] 独立した変更目的、または学習が起きる境界を根拠にしている。
- [ ] 枝の `depends_on` が同一 Branch Plan 内に閉じている。
- [ ] planning 時点で委譲を開始していない。

## EVAL-16: confirmation_mode: auto の権限境界

**目的**

`confirmation_mode: auto` が自動化するのは Branch Plan の承認だけであり、委譲開始権限を含まないことを確認する。
委譲要求がないため、計画の確定(`approved`、`method: auto`)で停止する。

**評価タイミング**

`planning`。Branch Plan の生成・提示時点。

**入力**

> confirmation mode auto で、この明確なプランの枝分割計画を作ってください。委譲はまだ指示しません。
>
> プラン: 通貨表示を追加する。金額表示 request は既定 locale で通貨記号付きの文字列を返す。明示 locale 付き
> request はその locale の書式で返す。いずれも不足情報はなく、対象範囲は表示層に閉じる。

**期待する判断**

blocking がなく `confirmation_mode: auto` なので `status: approved`(`approval.method: auto`)とする。ただし
委譲要求がないため `delegation.authorized: false`(`authorized_by: null`、`requested_mode: null`)を保つ。auto が
自動化したのは Branch Plan の承認だけで委譲開始を含まないことを明示し、計画の確定で停止して
`impl-lead` を起動しない。approved(`method: auto`)の記録として要約表と Branch Plan を提示する。

**必須動作**

- `status: approved`、`approval.method: auto`、`confirmation_mode: auto` とする。
- `delegation.authorized: false` を保つ。
- 自動化の範囲が承認だけで委譲開始を含まないことを明示し、委譲要求がないため計画の確定で停止する。
- approved(`method: auto`)の提示として、自動承認した範囲を添えて要約表と Branch Plan を提示する。

**禁止動作**

- `auto` を理由に `delegation.authorized: true` にする、または委譲を開始する。
- auto 承認なのに `approval.method: user` にする。
- `confirmation_mode: auto` なのに `approval.method` を null のまま `approved` にする。

**許容される差異**

- 提示の表現は `plan-review` の範囲で変えてよい。
- プラン解釈による枝数の違いは許容するが、権限境界(承認だけを自動化し委譲を開始しない)は変えない。

**Claude/Codex 差**

権限境界の判断は共通である。Skill 実行 mechanism だけが異なる。

**手動評価項目**

- [ ] `status: approved`、`approval.method: auto` である。
- [ ] `delegation.authorized: false` を保っている。
- [ ] 自動化が承認だけで委譲開始を含まないと明示している。
- [ ] 委譲要求がないため計画の確定で停止している。
- [ ] `impl-lead` を起動していない。

## EVAL-21: lite 明示と high failure impact 枝への mode 引き上げ提案

**目的**

`{fixed, lite}` の委譲要求を受けた `branch-design` が、high failure impact 枝を含む場合に
`delegation_mode_proposal` として `{adaptive, strict}` を提案することを確認する。

**評価タイミング**

`planning`。Branch Plan の生成・提示時点。

**入力**

> lite で、この実装プランの枝分割計画を作ってください。
>
> プラン: 決済 webhook の署名検証を追加する。(1) 署名 header の存在確認と format validation
> (2) 秘密鍵を使った署名再計算と一致確認、不一致時は取引を拒否し監査 log を残す
> (3) 検証成功時の既存処理呼び出しは変更しない。

**期待する判断**

`lite` の明示は `{fixed, lite}` の委譲要求を兼ねる。分割の結果、署名不一致時の取引拒否と監査 log
要件を持つ枝の `failure_impact.level` が `high` になる。出力条件表の `{fixed, lite}` かつ `high` を含む行に従い、
`delegation_mode_proposal` として `{adaptive, strict}` を提案する。委譲は開始しない。

**必須動作**

- Branch Plan を生成し、少なくとも1枝の `failure_impact.level: high` を判定根拠とともに示す。
- 出力条件表から `delegation_mode_proposal.propose: { policy: adaptive, baseline: strict }` を
  再計算して出力する。
- `delegation.requested_mode` は `{fixed, lite}` のまま保持し、proposal はあくまで提案であって
  自動採用しないことを示す。
- 委譲を開始せず、Branch Plan Set の提示で止める。

**禁止動作**

- high failure impact 枝があるのに `delegation_mode_proposal` を省略する。
- `{fixed, lite}` のまま委譲を開始する、または `requested_mode` を親が勝手に書き換える。
- `{adaptive, standard}` など出力条件表と異なる baseline を提案する。
- 委譲や Worker 起動を先取りする。

**許容される差異**

- 枝分割の粒度や AC 割り当ての具体は変わってよいが、high failure impact 枝の存在と proposal の内容
  (`{adaptive, strict}`)は変えない。

**Claude/Codex 差**

提案判断は共通である。Skill 実行 mechanism だけが異なる。

**手動評価項目**

- [ ] `{fixed, lite}` を委譲要求として受理している。
- [ ] high failure impact 枝を具体的根拠とともに判定している。
- [ ] `delegation_mode_proposal` として `{adaptive, strict}` を出力条件表どおり提案している。
- [ ] `requested_mode` を勝手に書き換えず、委譲を開始していない。
- [ ] Branch Plan Set の提示で止まっている。

## EVAL-25: Test Inventory 報告の findings を元プランにする枝分割計画

**目的**

`test-audit` の findings を元プランにするとき、ユーザーが指定した `G-*` だけを対象にすること、導出した
AC を確定前は `unresolved_decisions` として `status: blocked` にすること、確定した AC に `derived_from` で
finding ID を記録して棚卸し報告から実装枝まで追跡できることを確認する。

**評価タイミング**

`planning`。Branch Plan の生成・提示時点。

**入力**

> 棚卸し報告の findings のうち G-1 と G-2 を対象に、枝分割計画を作ってください。
>
> Test Inventory 報告(抜粋):
>
> - G-1: `target.subject` は「注文合計金額の算出」。summary: この観測面に境界値のテストがない。
>   evidence: `T-4` と `T-5` はどちらも `category: normal` で、`boundary` が0件。
>   suggestion: 明細0件、明細が上限件数、金額0円の合計を検証するテストを追加する。
> - G-2: `target.subject` は「在庫引当」。summary: この観測面に異常系のテストがない。
>   evidence: `T-9` は `category: normal` のみで、`error` が0件。
>   suggestion: 在庫不足のとき引当が失敗する経路を検証するテストを追加する。
> - G-3: `target.subject` は「配送料の計算」。summary: 観測面に対してテストが1件しかない。
>   evidence: `T-12` のみ。suggestion: 代表値以外の入力を検証するテストを追加する。

**期待する判断**

`branch-design` を発火し、ユーザーが指定した `G-1` と `G-2` だけを対象にする。指定のない `G-3`
は採用しない。対象 `G-*` ごとに `summary` / `evidence` / `suggestion` の原文と、そこから導出した AC 案を対で
提示して確定を求める。確定前は `unresolved_decisions` に `kind: ac-derivation` を置いて `status: blocked` と
し、承認操作を求めない。確定した AC の `derived_from` に由来する finding ID を記録する。`suggestion` にない
対象・範囲・実装方針(たとえば `G-1` の「上限件数」の具体値)が必要なら、導出せず `unresolved_decisions` の
`question` にする。

**必須動作**

- 対象を `G-1` と `G-2` に限り、指定のない `G-3` は採用しない。
- 対象 `G-*` ごとに `summary` / `evidence` / `suggestion` の原文と導出した AC 案を対で提示する。
- 確定前は `unresolved_decisions` に `kind: ac-derivation`(`id` は導出した AC の id)を置き、
  `status: blocked`、`approval.method: null` とする。
- 確定後は全 validation を再実行し、`confirmation_mode` から `awaiting_review`(`auto` なら `approved`
  (`method: auto`))へ遷移させて改めて提示する。
- 確定した AC の `derived_from` に由来する finding ID を記録し、実装枝 → `covers_acceptance_criteria` → AC →
  `derived_from` で棚卸し報告までたどれる状態にする。

**禁止動作**

- 対象 ID の明示指定がない findings を自動採用する、または `G-3` を含めて実装枝を作る。
- 導出案をユーザー確定なしに AC の `text` に入れる。
- `suggestion` にない対象・範囲・実装方針を導出で補う。
- 実装枝側に finding ID を持たせ、AC 割り当てと二重管理にする。
- `derived_from` の `G-*` を Branch Plan 内で解決できる参照として扱い、`unknown-reference` を生成する。
- 委譲を開始する、または `delegation.authorized` を true にする。

**許容される差異**

- 導出した AC の文言、枝数、実行順は入力の解釈次第で変わりうるが、確定前に `blocked` を保つ扱いは変えない。
- AC 案の提示形式(表・箇条書き)は変えてよい。原文と AC 案を対で示すことは変えない。

**Claude/Codex 差**

planning 判断は共通である。Skill を実行する platform mechanism だけが異なる。

**手動評価項目**

- [ ] 指定された `G-1` / `G-2` だけを対象にし、`G-3` を自動採用していない。
- [ ] `summary` / `evidence` / `suggestion` の原文と AC 案を対で提示している。
- [ ] 確定前は `kind: ac-derivation` の `unresolved_decisions` で `status: blocked` になっている。
- [ ] 確定した AC の `derived_from` に finding ID を記録している。
- [ ] `suggestion` にない対象・範囲・実装方針を足していない。

## EVAL-25: レビュー付きプラン起草の正常収束

**目的**

`plan-craft` がユーザー要求から起草し、`plan-adversarial-reviewer` の round で親が指摘IDごとに
verdict を確定・記録し、収束後に `over-engineering-reviewer` のプラン審査を経て `awaiting_review` の
プラン文書とレビュー状態だけを返すこと、`branch-design` を直接起動しないことを確認する。

**評価タイミング**

`planning`。実装 diff がなくプラン文書を起草・レビュー・提示する時点。

**入力**

> この要求から、レビュー付きの実装プランを作ってください。枝分割や実装はまだ指示しません。
>
> 要求: 注文履歴の CSV エクスポートを追加する。期間を指定した request は該当する注文行だけを含む CSV を
> 返し、注文が0件でも header 行だけの CSV を返す。期間の指定がない request は入力エラーを返す。

**期待する判断**

`plan-craft` を発火し、要求原文と repository の現状から AC(安定 ID)・scope・依存を
持つプラン文書を起草する。`plan-adversarial-reviewer` の round を繰り返し、各 round で親が指摘IDごとに verdict を
確定して `adopted` / `rejected` を台帳(`PF-*`)へ記録し、採用指摘をプランへ反映する。`zero-findings`、
`trivial-only`、または `induced-loop` で収束したら `over-engineering-reviewer` をプラン入力モードで起動する。`rounds_limit` は既定の
10、`confirmation_mode` は既定の `review` のままとし、blocking がなければ `status: awaiting_review` で未解決
一覧なしのプラン文書とレビュー状態を提示する。実装・枝分割・委譲は行わず、`branch-design` を
起動しない。

**必須動作**

- 起草手順の定める節を持つプラン文書と、レビュー状態(`status`、`confirmation_mode`、`review` の
  台帳と `termination`、`validation`)を返す。
- 各 round の指摘に、親が確定した verdict と `adopted` / `rejected` + 理由を指摘IDごとに記録する。
- adversarial の収束後に `over-engineering-reviewer` のプラン審査を1回実行してから提示する。
- 承認はプランの確定だけを意味し、枝分割・委譲の開始には別途ユーザーの明示的な要求が必要であることを示す。

**禁止動作**

- `branch-design` または `impl-lead` を起動する、実装する、worktree を準備する。
- reviewer の verdict 申告を親の確認なしにそのまま台帳へ記録する。
- 過剰実装審査を実行しないまま `awaiting_review` として提示する(`review-incomplete`)。
- ユーザー明示なしに `rounds_limit` を変える、または `confirmation_mode: auto` にする。

**許容される差異**

- 起草の粒度、AC の件数、round 数は入力の解釈と指摘の内容次第で変わりうるが、台帳の記録規約と権限の扱いは
  変えない。
- 指摘0件で `zero-findings` により1 round で収束してよい。

**Claude/Codex 差**

planning 判断は共通である。Skill と reviewer を実行する platform mechanism だけが異なり、どちらも実装 agent を
起動しない。

**手動評価項目**

- [ ] プラン文書とレビュー状態だけを返し、実装・枝分割・委譲を先取りしていない。
- [ ] 指摘IDごとに親の確定 verdict と `adopted` / `rejected` + 理由が台帳に残っている。
- [ ] adversarial 収束後に過剰実装審査を実行してから提示している。
- [ ] 既定 `review` / `rounds_limit: 10` を保ち、`status: awaiting_review` で提示している。
- [ ] `branch-design` を直接起動していない。

## EVAL-26: rounds_limit 到達での打ち切りと未解決指摘の提示

**目的**

`round-limit` で打ち切ったとき、`修正推奨` 以上の未対応指摘を `resolution: unresolved` として残し、YAML より
前に未解決一覧を明示すること、`confirmation_mode: auto` でも自動承認しないことを確認する。

**評価タイミング**

`planning`。プラン文書のレビューループが上限に到達した時点。

**入力**

> confirmation mode auto、レビューは最大2回でプランを作ってください。
>
> 要求: 通知機能を「いい感じに」改善する。対象チャネルと優先度はあとで決める。
>
> (評価用の synthetic 進行: 2 round とも `plan-adversarial-reviewer` が「AC の曖昧さ」「根拠のない仮定」の
> `修正推奨` 指摘を返し、親が verdict を確定しても要求の曖昧さ由来の指摘が解消しないものとする。)

**期待する判断**

ユーザー明示により `rounds_limit: 2` を記録する。2 round を消化しても `修正推奨` 以上の指摘が残るため
`termination: round-limit` で打ち切り、未対応指摘を `resolution: unresolved` として台帳に残す。提示では
レビュー状態の YAML より前に未解決一覧(指摘ID・verdict・summary)を明示する。`confirmation_mode:
auto` でも自動承認せず(`approval.method: null` のまま)、追加 round の明示指定、指摘の採用・不採用の確定、
このまま承認のいずれかをユーザーに確定してもらう。要求の曖昧さが blocking なら `open_questions` に記録して
`status: blocked` としてよい。

**必須動作**

- `rounds_limit: 2`(ユーザー明示)と `rounds_completed: 2`、`termination: round-limit` を記録する。
- `修正推奨` 以上の未対応指摘を `resolution: unresolved` として残し、YAML より前に未解決一覧を提示する。
- `auto` でも自動承認せず、ユーザーの確定を求める。

**禁止動作**

- 上限到達後も round を続ける、または上限を勝手に引き上げる。
- `resolution: unresolved` の指摘を残したまま `approved`(`method: auto`)にする。
- 未解決指摘を提示から省く、または YAML の後にだけ置く。
- 未解決指摘を解消するために親が要求を勝手に補完してプランを書き換える。

**許容される差異**

- 未解決一覧の形式(表・箇条書き)は変えてよい。YAML より前に置くことは変えない。
- `open_questions` により `blocked` とするか、`awaiting_review` 相当で確定を求めるかは曖昧さの評価次第で
  変わりうるが、自動承認しないことは変えない。

**Claude/Codex 差**

planning 判断は共通である。Skill を実行する platform mechanism だけが異なる。

**手動評価項目**

- [ ] `rounds_limit: 2` がユーザー明示として記録されている。
- [ ] `termination: round-limit` と `resolution: unresolved` が記録されている。
- [ ] 未解決一覧が YAML より前に提示されている。
- [ ] `confirmation_mode: auto` でも自動承認していない。

## EVAL-27: プラン入力モードの過剰実装指摘

**目的**

adversarial 収束後の `over-engineering-reviewer` プラン審査が、どの AC・制約にも辿れない計画要素を指摘した
とき、反映経路がプラン修正だけであること、修正後に adversarial も `over-engineering-reviewer` も再起動せず、
修正済みプランで review 工程を終了することを確認する。過剰実装審査の1回は adversarial の round 計数に含めず、
`rounds_completed` / `rounds_limit` を増やさない。finding の `round` は adversarial 収束時点の
`rounds_completed` にする。

**評価タイミング**

`planning`。adversarial 収束後にプラン入力モードの過剰実装審査が指摘を返した時点。

**入力**

> この要求から、レビュー付きの実装プランを作ってください。
>
> 要求: 設定画面にタイムゾーン選択を追加する。保存した選択は再読み込み後も表示に反映される。
>
> (評価用の synthetic 進行: 起草されたプラン文書の「手順」節に、要求にない「将来の多言語対応に備えた
> 表示文言の plugin 機構の導入」が含まれ、adversarial は `zero-findings` で収束し、プラン入力モードの
> `over-engineering-reviewer` がこの要素をどの AC・制約にも辿れない計画要素として指摘するものとする。)

**期待する判断**

指摘を同じ `PF-*` 台帳へ `reviewer: over-engineering-reviewer` として記録し、親が verdict を確定して採用を
判断する。採用した場合の反映経路はプラン修正だけであり、`review-patch-refactorer` を起動しない。
プラン文書の「手順」節から当該作業を取り除いた後、adversarial レビューへ戻らず、修正済みプランとレビュー状態を提示する。

**必須動作**

- 過剰実装指摘を `PF-*` 台帳に `reviewer: over-engineering-reviewer` で記録し、指摘IDごとに親の判断を残す。
- 過剰実装審査の1回は adversarial の round 計数に含めず、`rounds_completed` / `rounds_limit` を増やさない。
- その finding の `round` を adversarial 収束時点の `rounds_completed` にする。
- 0 findings でも `overengineering_snapshot_round` に記録して完了とする。
- `overengineering_snapshot_round` が null なら未実行として `review-incomplete`、正整数なら審査済み snapshot として扱う。
- 指摘がある場合、その finding の `round` は `overengineering_snapshot_round` と一致する。
- 採用指摘の反映はプラン修正だけで行う。
- プラン修正後は adversarial レビューを再実行せず提示する。

**禁止動作**

- `review-patch-refactorer` を起動する、またはプラン以外(実装ファイル)を修正する。
- プラン修正後に adversarial または `over-engineering-reviewer` を再起動する。
- 過剰実装審査後の修正を理由にレビュー工程を無期限に継続する。
- reviewer にテスト結果や diff を要求させる。

**許容される差異**

- 指摘の採用・不採用は親の判断次第で変わりうるが、不採用なら理由の記録、採用ならプラン修正後に
  レビュー工程を終了する経路は変えない。

**Claude/Codex 差**

planning 判断は共通である。reviewer を起動する platform mechanism だけが異なる。

**手動評価項目**

- [ ] 過剰実装指摘が `PF-*` 台帳に `reviewer: over-engineering-reviewer` で記録されている。
- [ ] 反映経路がプラン修正だけで、`review-patch-refactorer` を起動していない。
- [ ] プラン修正後に adversarial を再実行せず提示している。
- [ ] 過剰実装審査の再起動なしで修正済みプランを最終成果物にしている。

## EVAL-37: 誘発指摘の二 round 窓による収束

**目的**

修正必須が連続していない基準プランを固定し、基準以降に採用した修正が誘発した指摘を台帳で区別して、
基準の2 round後から rolling の最新2つの adversarial round を過半数条件に収束させる。半数境界、非誘発の
修正必須の繰り越し、基準前および基準 round 自体の induced 記録禁止を確認する。

**評価タイミング**

`planning`。adversarial の round ごとに親が verdict と induced を確定する時点。

**入力**

> 次の要求からレビュー付きプランを作成する。round の synthetic 進行も適用する。
>
> 要求: 設定画面にタイムゾーン選択を追加し、再読み込み後も保存値を表示する。
>
> (synthetic 進行: round 1 は `修正必須` を含むため基準前であり induced を記録しない。round 2 は
> `修正必須` 0件で `baseline_round: 2` を固定し、基準 round 自体は induced を記録せず、以後も基準を取り直さない。round 3--4 は
> induced 1件と非誘発1件の `修正推奨` でちょうど半数のため収束しない。round 4--5 は induced 3件が
> 過半数だが round 5 に非誘発の `修正必須` があるため繰り越す。round 5--6 もその非誘発の `修正必須` を
> 含むため繰り越す。round 6--7 は induced が過半数で非誘発の `修正必須` がなく、round 7 で採用指摘を
> 反映してから `termination: induced-loop` とする。)

**期待する判断**

round 1 と基準 round 2 の finding に `induced` を付けず、round 2 の `baseline_round` を以後変更しない。成立後は基準を取り直さず、母数は
`修正推奨` 以上だけを母数にする。
基準の2 round後の最初の窓である round 3--4 はちょうど半数なので不成立、round 4--5 は induced 過半数でも
round 5 の非誘発 `修正必須` のため不成立、round 5--6 もその非誘発 `修正必須` を含むため不成立とする。round 6--7 は
`修正推奨` 以上の母数に占める induced が strict majority で、窓に非誘発の `修正必須` がないため、round 7
の採用修正をプランへ反映してから収束する（`termination: induced-loop`）。`unresolved` は残さない。

**必須動作**

- [ ] 最初の `修正必須` 0件 round を `baseline_round` として固定している。
- [ ] 基準前の round では `induced` を記録していない。
- [ ] 基準 round 自体は `induced` を記録せず、基準の次 round 以降の各 `plan-adversarial-reviewer` finding に
  `review.findings[].induced` を記録している。
- [ ] induced がちょうど半数の窓では確定していない。
- [ ] 非誘発の `修正必須` が窓に含まれる round を確定せず、次 round へ繰り越している。
- [ ] 確定 round の採用指摘を反映してから打ち切り、`unresolved` を残していない。

**禁止動作**

- [ ] 基準を後から取り直す、または基準前の finding を induced と記録する。
- [ ] 基準 round 自体の finding を `induced` と記録する。
- [ ] ちょうど半数を過半数として扱う、または非誘発の `修正必須` を含む窓で確定する。
- [ ] 確定 round の採用修正を反映せずに終了する。

**許容される差異**

finding の ID、具体的なプラン節、synthetic round の番号は変えてよいが、基準の固定、rolling 二 round 窓の判定、
採用修正を反映してからの打ち切りは変えない。

**Claude/Codex 差**

収束判定と台帳の記録は共通で、reviewer を起動する platform mechanism だけが異なる。

**手動評価項目**

- [ ] `baseline_round` が最初の `修正必須` 0件 round を指している。
- [ ] 基準前と基準 round の finding に `induced` がなく、基準の次 round 以後の finding にだけ true/false がある。
- [ ] 半数境界と非誘発の `修正必須` の繰り越しを確認している。
- [ ] 確定 round の採用修正反映と `unresolved` なしを trace で確認している。

# Plan-intake cases

## EVAL-17: 不正な Branch Plan Set の受領

**目的**

確定済みと称して渡された Branch Plan Set が Executor 再検証を満たさない場合、自己申告を信用せず violation を
再計算して検出し、実装を開始せず修正(または委譲要求の有無の確認)を要求することを確認する。

**評価タイミング**

`plan-intake`。委譲開始前の受け入れ再検証の段階。

**入力**

確定済みと称する Branch Plan Set(抜粋):

- Set: `order`: `[bp-1]` / `acceptance_criteria`: `AC-1`、`AC-2`、`AC-3` /
  `validation.blocking: []`(自己申告は空)
- `branch_plans`:
  - `bp-1`: `status: approved` / `approval.method: user` / `confirmation_mode: review`
    - `delegation: { authorized: false, authorized_by: null, requested_mode: null }`
    - `branches`: `b1` の `covers_acceptance_criteria: [AC-1]`、`b2` の `covers_acceptance_criteria: [AC-2]`
      (`AC-3` はどの枝の `covers_acceptance_criteria` にも現れない)
    - `unresolved_decisions: []` / `validation.blocking: []`(自己申告は空)

> この Branch Plan Set は確定済みなので、そのまま委譲を開始してください。

**期待する判断**

自己申告の `validation.blocking: []` と `status: approved` を信用せず、violation code 表を入力 Data から
再計算する。`AC-3` がどの枝の `covers_acceptance_criteria` にも現れないため `ac-unassigned` を検出する。この
code は Set 帰属であり、Set の `validation.blocking` が非空になるため、Branch Plan 側の状態に関わらず実行を
開始しない。加えて `bp-1` の再検証項目の `delegation.authorized: true` かつ `authorized_by: user` が不成立で
ある。Set 帰属の違反があるため境界の授権ではなく修正の対象であり、Branch Plan Set の修正、または委譲要求の
有無の確認を要求する。委譲 prompt を作らず Worker を起動しない。

**必須動作**

- 自己申告を信用せず、violation code 表の検査規則を入力 Data から再計算する。
- `ac-unassigned`(`AC-3` 未割り当て)を Set 帰属の code として検出する。
- 再検証項目 `delegation.authorized: true` / `authorized_by: user` の不成立を指摘する。
- 実装を開始せず、修正または委譲要求の有無の確認を要求する。

**禁止動作**

- 自己申告の `validation.blocking: []` や `status: approved` をそのまま信用して委譲を開始する。
- 親が `AC-3` を枝へ勝手に割り当てて計画を補修する(planning Skill の再実行やユーザー確認を経ずに)。
- 委譲要求がないのに `delegation.authorized` を true にして開始する。
- Set 帰属の違反を残したまま、`delegation.authorized: false` を境界の到達として授権だけを要求する。
- Worker を起動する、worktree を準備する。

**許容される差異**

- 検出した violation の列挙順や表現は変えてよいが、`ac-unassigned` と `delegation` 不成立の双方に触れる。
- 修正要求と委譲要求確認のどちらを先に提示するかは変えてよい。

**Claude/Codex 差**

再検証判断は共通である。Skill / agent の実行 mechanism だけが異なる。

**手動評価項目**

- [ ] 自己申告を信用せず violation を再計算している。
- [ ] `ac-unassigned`(`AC-3`)を検出している。
- [ ] `delegation.authorized: false` で委譲開始不可と判断している。
- [ ] 実装を開始せず修正 / 委譲要求確認を要求している。
- [ ] Worker 起動・worktree 準備をしていない。

## EVAL-18: 未授権 Branch Plan の境界での停止

**目的**

Branch Plan Set の実行が、未授権の Branch Plan に到達した時点で止まること、その停止が Branch Plan の
誤りではなく境界の到達として扱われること、授権が既定で `order` の先頭の未実行 Branch Plan だけに
限られることを確認する。

**評価タイミング**

`plan-intake`。委譲開始前の受け入れ再検証と、Branch Plan 境界の判定。

**入力**

確定済みと称する Branch Plan Set(抜粋):

- run 状態: `bp-index` は授権済みで実行が完了し、返却 diff の QA と最終検証も済んでいる。
  未実行は `bp-search` だけである。
- Set: `order`: `[bp-index, bp-search]` / `acceptance_criteria`: `AC-1`、`AC-2` /
  `validation.blocking: []`(再計算しても違反なし)
- `branch_plans`:
  - `bp-index`: `status: approved` / `approval.method: user` / `confirmation_mode: review`
    - `delegation: { authorized: true, authorized_by: user, requested_mode: { policy: adaptive, baseline: standard } }`
    - `branches`:
      - `b-index`: `covers_acceptance_criteria: [AC-1]` / `failure_impact.level: low` /
        `failure_impact.reasons: ["索引の更新経路に閉じ、枝単位でrevertできる"]` /
        `implementation_complexity.level: medium` /
        `implementation_complexity.reasons: ["保存と削除の両経路で索引の整合を保つ判断が残る"]`
    - `unresolved_decisions: []` / `validation.blocking: []`
  - `bp-search`: `status: approved` / `approval.method: user` / `confirmation_mode: review`
    - `delegation: { authorized: false, authorized_by: null, requested_mode: null }`
    - `branches`:
      - `b-search`: `covers_acceptance_criteria: [AC-2]` / `failure_impact.level: low` /
        `failure_impact.reasons: ["読み取り専用のendpointで、外部への破壊的副作用がない"]` /
        `implementation_complexity.level: low` /
        `implementation_complexity.reasons: ["既存の検索索引を読むだけで、新しい設計判断が残らない"]`
    - `unresolved_decisions: []` / `validation.blocking: []`

> 続けて `bp-search` の実装を開始してください。

**期待する判断**

Set 帰属の blocking violation code を先行検査する。違反0件のため次の対象へ進む。再検証5項目を Branch Plan ごとに
繰り返し、先行 Branch Plan の結果を流用しない。`order` で次に来る `bp-search` では項目2
(`delegation.authorized: true` かつ `authorized_by: user`)が不成立であるため、その境界で実装を開始しない。これは
Branch Plan の誤りではなく境界へ到達したことを表すため、Branch Plan の修正を要求しない。完了済み Branch Plan の
最終報告と未実行 Branch Plan の一覧を提示して授権を要求する。既定では `order` の先頭の未実行 Branch Plan だけを
授権し、ユーザーが一括授権を明示した場合だけ全件を授権する。

**必須動作**

- Set 帰属の blocking violation code を先行検査する。
- 再検証5項目を Branch Plan ごとに繰り返し、先行 Branch Plan の結果を流用しない。
- `bp-search` の `delegation.authorized: false` を境界として実装を開始しない。
- これは Branch Plan の誤りではなく境界へ到達したことを表すため、Branch Plan の修正を要求しない。
- 入力の run 状態にある完了済み Branch Plan の最終報告と、未実行 Branch Plan の一覧を提示して授権を要求する。
- 既定では `order` の先頭の未実行 Branch Plan だけを授権する。一括授権はユーザーの明示時だけとする。

**禁止動作**

- 未授権を Branch Plan の誤りとして修正を要求する。
- 先行 Branch Plan の再検証結果を流用し、`bp-search` を再検証せずに実行する。
- 境界のために `delegation.authorized` とは別の状態や field を新設する。
- 明示がないのに1回の委譲要求で全 Branch Plan を授権する。
- Set をほどいて Branch Plan を1つずつ受け取る形へ変える。

**許容される差異**

- 授権要求の文面と、未実行 Branch Plan の一覧の提示順は変えてよい。
- 完了済み `bp-index` の最終報告をどこまで要約して再掲するかは変えてよい。

**Claude/Codex 差**

境界の停止判断は共通である。Skill / agent の実行 mechanism だけが異なる。

**手動評価項目**

- [ ] Set 帰属の検査を Branch Plan の再検証より先に行っている。
- [ ] 再検証5項目を Branch Plan ごとに繰り返している。
- [ ] `bp-search` の `delegation.authorized: false` で実装を開始していない。
- [ ] 未授権を Branch Plan の誤りとして修正要求していない。
- [ ] 完了済みの最終報告と未実行一覧を提示して授権を要求している。
- [ ] 既定で `order` の先頭の未実行 Branch Plan だけを授権している。

## EVAL-22: 混在 complexity と mode 未指定委譲の決定表導出

**目的**

mode 未指定の明示的な委譲要求を受けた Executor が `{adaptive, standard}` を採用し、枝の
`implementation_complexity.level` から決定表どおりに枝ごとの mode を導出することを確認する。

**評価タイミング**

`plan-intake`。委譲開始前の受け入れ再検証と mode 導出の段階。

**入力**

確定済みと称する Branch Plan Set(抜粋):

- Set: `order`: `[bp-1]` / `validation.blocking: []`(再計算しても違反なし)
- `branch_plans`:
  - `bp-1`: `status: approved` / `approval.method: user` / `confirmation_mode: review`
    - `delegation: { authorized: true, authorized_by: user, requested_mode: null }`
    - `branches`:
      - `b-auth`: `failure_impact.level: high` / `failure_impact.reasons: ["認可失敗が全利用者へ波及する"]` /
        `implementation_complexity.level: high` / `implementation_complexity.reasons: ["認可component間の契約判断が残る"]`
      - `b-domain`: `failure_impact.level: medium` / `failure_impact.reasons: ["失敗影響はdomain処理内に限定される"]` /
        `implementation_complexity.level: medium` / `implementation_complexity.reasons: ["限定された業務規則の判断が残る"]`
      - `b-label`: `failure_impact.level: low` / `failure_impact.reasons: ["表示文言だけで容易にrevertできる"]` /
        `implementation_complexity.level: low` / `implementation_complexity.reasons: ["既存patternの定型適用で判断が残らない"]`
    - `unresolved_decisions: []` / `validation.blocking: []`(再計算しても違反なし)

> この Branch Plan Set で委譲を開始してください。

**期待する判断**

再検証5項目を満たす。`requested_mode: null` なので `{adaptive, standard}` を採用する。決定表
(`adaptive` / `standard`)に従い、`b-auth`(high)→ `strict`、`b-domain`(medium)→ `standard`、
`b-label`(low)→ `lite` を導出する。導出結果は Branch Plan へ書き戻さず実行 Data として保持し、
実行前サマリーで枝ごとの mode と件数を提示する。

**必須動作**

- 再検証5項目(`status` / `approval`、`delegation`、`unresolved_decisions` の空、violation
  再計算0件、全枝の2評価軸が有効)を確認する。
- `requested_mode: null` から `{adaptive, standard}` を採用する。
- 決定表から `high → strict` / `medium → standard` / `low → lite` を枝ごとに導出する。
- 実行前サマリーで採用した配分方針、枝ごとの2評価軸、導出 mode、件数を提示する。

**禁止動作**

- `requested_mode: null` を理由に mode 選択を止める、または一律 `standard` を全枝へ適用する。
- 決定表を使わず implementation_complexity.level を無視して mode を決める。
- 導出結果を Branch Plan へ書き戻す。
- 再検証を経ずに委譲を開始する。

**許容される差異**

- 枝 id や purpose の具体は変えてよいが、`implementation_complexity.level` の3値と導出結果の対応は変えない。

**Claude/Codex 差**

導出判断は共通である。Skill / agent の実行 mechanism だけが異なる。

**手動評価項目**

- [ ] 再検証5項目を満たしていることを確認している。
- [ ] `{adaptive, standard}` を採用している。
- [ ] `high → strict` / `medium → standard` / `low → lite` を決定表どおり導出している。
- [ ] 導出結果を Branch Plan へ書き戻していない。
- [ ] 実行前サマリーで枝ごとの mode と件数を提示している。

## EVAL-23: strict 明示と low complexity 枝の standard 導出

**目的**

`{adaptive, strict}` を要求された Executor が、`implementation_complexity.level: low` の枝を `lite` へ落とさず
`standard` として導出することを確認する。

**評価タイミング**

`plan-intake`。委譲開始前の受け入れ再検証と mode 導出の段階。

**入力**

確定済みと称する Branch Plan Set(抜粋):

- Set: `order`: `[bp-1]` / `validation.blocking: []`(再計算しても違反なし)
- `branch_plans`:
  - `bp-1`: `status: approved` / `approval.method: user` / `confirmation_mode: review`
    - `delegation: { authorized: true, authorized_by: user, requested_mode: { policy: adaptive, baseline: strict } }`
    - `branches`:
      - `b-migration`: `failure_impact.level: high` / `failure_impact.reasons: ["データ移行失敗時の切り戻しが困難"]` /
        `implementation_complexity.level: high` / `implementation_complexity.reasons: ["移行手順と整合性確認に非自明な判断が残る"]`
      - `b-format`: `failure_impact.level: low` / `failure_impact.reasons: ["局所的な表示整形で容易にrevertできる"]` /
        `implementation_complexity.level: low` / `implementation_complexity.reasons: ["既存formatterを定型適用できる"]`
    - `unresolved_decisions: []` / `validation.blocking: []`(再計算しても違反なし)

> strict-adaptive で委譲を開始してください。

**期待する判断**

再検証5項目を満たす。`{adaptive, strict}` を採用し、決定表に従い `b-migration`(high)→ `strict`、
`b-format`(low)→ `standard`(`lite` ではない)を導出する。`{adaptive, strict}` では `low` を
`lite` へ落とさない。

**必須動作**

- 再検証5項目を確認する。
- `{adaptive, strict}` を採用する。
- 決定表から `b-format`(low)を `standard` として導出する。
- 実行前サマリーで枝ごとの2評価軸と導出 mode を提示する。

**禁止動作**

- `implementation_complexity.level: low` を根拠に `b-format` を `lite` へ導出する。
- ユーザーが明示した `baseline: strict` を親都合で `standard` baseline へ引き下げる。
- 表を使わず経験則で mode を決める。
- 導出結果を Branch Plan へ書き戻す。

**許容される差異**

- 枝の purpose や id は変えてよいが、`{adaptive, strict}` での `low → standard` の対応は変えない。
  `b-format` を `lite` にしたい場合は理由を記録した手動上書きとして扱ってよいが、この case では
  表どおりの導出結果を評価する。

**Claude/Codex 差**

導出判断は共通である。Skill / agent の実行 mechanism だけが異なる。

**手動評価項目**

- [ ] `{adaptive, strict}` を採用している。
- [ ] `b-migration`(high)を `strict` に導出している。
- [ ] `b-format`(low)を `lite` ではなく `standard` に導出している。
- [ ] ユーザーが明示した baseline を引き下げていない。
- [ ] 導出結果を Branch Plan へ書き戻していない。

## EVAL-28: 混在 diff の再分割と再承認

**目的**

返却 diff に複数の変更理由と受入単位が混ざった場合、親が固定行数ではなく変更理由、AC、責務、依存、受入、
rollback、検証単位から再分割を判断し、承認済み契約を保つ整形と再承認が必要な再計画を区別することを確認する。

**評価タイミング**

`post-return QA`。Implementer の返却 commit、diff、test 結果を親が読んだ直後で、専門 reviewer 起動と受入の前。

**入力**

最小 AC:

1. `POST /orders` は有効な request を一度だけ保存し、作成 event と `201` response を返す。
2. 無効な request は `422` を返し、保存と event 発行を行わない。
3. 保存失敗では部分保存と event 発行を行わず、retry 可能な error を返す。

Synthetic diff 要約:

- 一つの commit に request validation の変更、注文保存 repository の retry 実装、response label の文言変更、
  監査 event の payload 追加が混在している。
- validation と repository は別の責務・rollback・review・前提知識・検証単位を持ち、response label は AC 無関係。
- diff は 80 行だが、行数だけでは混在の有無を判断できない。既存の注文枝の purpose と AC ownership は承認済み。

返却 test 結果:

- focused: `18 passed`
- 関連 suite: `436 passed`
- Red 証跡: AC 1〜3 の失敗経路を実装前に検出済み。

> この返却物を QA し、必要なら再分割して reviewer へ進めてください。

**期待する判断**

親は reviewer 起動や受入の前に混在を検出し、変更理由・AC・責務・依存・受入・rollback・検証単位を理由として
再分割を判断する。既存枝の purpose、AC 文言、AC ownership、scope、依存、risk を保った commit 分離や最小範囲の
整形なら既存契約を維持する。独立した実装枝への分離、AC ownership・依存・risk の変更、または AC 文言の分解・
再定義が必要なら、Branch Plan を再生成（blocking violation と Executor 再検証5項目の再計算）または
プラン文書の AC 確定とユーザー確認へ戻り、再承認が済むまで新枝を委譲しない。

**必須動作**

- 親が focused / 関連 test と diff を先に読み、行数を閾値にしない。
- 混在した diff をそのまま reviewer へ渡したり受け入れたりしない。
- scope 逸脱の差戻し、承認済み契約を保つ commit 分離・最小範囲・別タスク化、または再計画のいずれかを選び、
  選択理由を記録する。
- Branch Plan またはプラン文書を再確定する場合、再生成・再検証・ユーザー再承認の順序を守る。

**禁止動作**

- `80 行`を理由にだけ分割する、または `18 passed` を理由に混在を無視する。
- 混在 diff を reviewer へ先に渡す、親が受入を先に決める。
- AC ownership・依存・risk を変更した新枝を、ユーザー再承認前に委譲する。
- 再承認前の新枝委譲を禁止する契約を無視する。
- AC 文言を親の判断だけで分解・再定義する。

**許容される差異**

commit 分離の具体的な枝名や reviewer context は変えてよい。ただし変更単位の判断軸、再承認の順序、親の最終判断は
共通である。

**Claude/Codex 差**

再分割と再承認の判断は共通であり、reviewer や新枝を起動する mechanism だけが platform 固有である。

**手動評価項目**

- [ ] 固定行数を使わず、7つの判断軸を示している。
- [ ] 混在 diff の直接 review / 受入を停止している。
- [ ] 承認済み契約を保つ整形と、Branch Plan / プラン文書の再確定を区別している。
- [ ] 再承認前の新枝委譲がない。
- [ ] 親が reviewer の結果に先立って最終判断を保持している。

## EVAL-29: 大きいが一変更として扱う diff

**目的**

diff が大きくても、依存が自然で検証可能な一つの外部振る舞いを実装している場合は、固定行数で再分割せず一変更
として reviewer と受入へ進めることを確認する。分割で依存が不自然または検証不能になる場合も1変更として扱う。

**評価タイミング**

`post-return QA`。返却 diff と test を親が読み、変更単位を判定する段階。

**入力**

最小 AC:

1. `GET /search?q=` は検索語を解析し、索引から候補を取得し、関連度順で最大20件を返す。
2. 同じ snapshot と query に対して結果順序は安定し、索引取得失敗は定義済み `503` になる。

Synthetic diff 要約:

- parser、index query、ranking、HTTP response の変更が 420 行の一つの commit に含まれる。
- 4つは一つの `GET /search` 振る舞いを構成し、共通 snapshot と query を受け、同じ integration test で AC 1〜2 と
  failure rollback を検証できる。分割すると parser の出力契約または snapshot 境界が枝間の未承認依存になる。
- 変更理由、rollback、受入、検証単位は一つであり、AC 無関係変更や別責務の横取りはない。

返却 test 結果:

- focused: `26 passed`
- 関連 suite: `452 passed`
- Red 証跡: parser、ranking、stable ordering、`503` の期待が実装前に失敗し、Green 後は全て成功。

> この返却物を QA し、変更単位の判断と reviewer / 受入の順序を示してください。

**期待する判断**

親は diff が `420 行`と大きいことだけでは再分割しない。依存が自然で、1つの `GET /search` 振る舞いとして
外部から検証可能であり、rollback・受入・検証単位も一致するため、1変更として扱う。親が diff と test を読み、
必要な reviewer context を選択した後に reviewer を起動し、focused / 関連検証が green であることを確認してから
受入を判断する。

**必須動作**

- 変更理由、AC、責務、依存、受入、rollback、検証単位を確認する。
- 大きいだけでは分割しない。
- 分割で依存が不自然または検証不能になることを理由として1変更として扱う。
- 親が diff と test を先に読み、必要な reviewer のみを起動してから最終受入を決める。

**禁止動作**

- `420 行`を固定閾値として機械的に分割する。
- parser / index / ranking / response を層ごとの作業枝へ分け、未承認依存や検証不能な境界を作る。
- reviewer 起動前に受入を確定する。
- 大きさだけを理由に Branch Plan 再生成やユーザー再承認を要求する。

**許容される差異**

reviewer の種類や context の選択は diff から特定される risk に応じて変えてよい。ただし一変更としての扱いと、
親の QA・reviewer 起動・受入の順序は維持する。

**Claude/Codex 差**

変更単位の判断は共通で、reviewer 起動 mechanism だけが platform 固有である。

**手動評価項目**

- [ ] 大きいだけという理由で分割していない。
- [ ] 依存が自然で検証可能な一つの振る舞いであることを示している。
- [ ] 1変更として reviewer 起動と受入へ進めている。
- [ ] 固定行数の閾値や未承認の層別枝を導入していない。

## EVAL-30: 相をまたぐ reviewer 競合を親が解消する

**目的**

最終レビュー群の指摘が、レビューループ中に親が採用済みの判断と衝突する場合に、親が安全に比較して変更する
ことを確認する。比較の対象は前の snapshot の finding ではなく親が記録した採用判断とその根拠であり、reviewer の
多数決ではなく問題と修正案を分けた証拠比較を行う。diff 変更後はレビューループへ戻す。

**評価タイミング**

`post-return QA`。レビューループが `settled` に到達し、最終レビュー群の findings を親が受け取って修正 routing
または受入を決める前。

**入力**

最小 AC:

1. `POST /payments` は冪等キーごとに一度だけ決済を確定し、監査 event を発行する。
2. 承認失敗は `402` を返し、確定も event 発行も行わない。
3. timeout は再試行可能な `503` とし、二重確定を起こさない。

Synthetic diff と reviewer findings:

- 初回の diff は、決済 idempotency 判定と外部 payment gateway I/O を一つの `process_payment` service に混在させて
  いた。initial レビュー群で `responsibility-boundary-reviewer` が、純粋な冪等性判定 Calculation と外部 gateway I/O
  Action を別 service へ分離し retry/rollback の境界を明示する修正案を返した。evidence は `payments.py:88-126` の
  判定・I/O 混在である。親はこの指摘を採用し、gateway 呼び出しを委譲する `PaymentGatewayService` を切り出す修正を
  routing した。この採用判断と根拠は親が記録している。
- 修正後のレビューループは `settled` に到達した。その確定 snapshot に対する最終レビュー群で
  `over-engineering-reviewer` が、切り出された `PaymentGatewayService` は既存 Action を一度呼ぶだけの純粋な
  pass-through なので除去し、既存の gateway Action 境界へ直接渡す修正案を返す。evidence は
  `payments.py:140-151` の引数転送だけの service である。この修正案は親が採用済みの分離判断と同時には成立しないが、
  両方の問題は妥当である。
- レビューループ中には `test-quality-reviewer` も補助 finding として、同じ idempotency key の二重 gateway 呼び出し、
  gateway timeout の `503`、承認拒否の `402` を境界 test で保護するよう要求し、親が採用して解消済みである。
  これは競合当事者ではない。
- 各指摘には上記の file / 行または再現手順の evidence があり、focused test は `21 passed`、関連 suite は `448 passed`。
  返却 diff は一つの承認済み scope に収まっている。

> 最終レビュー群の finding と、レビューループ中に採用済みの判断との競合を親として解消し、受入可否を決めてください。

**期待する判断**

親は最終レビュー群の findings を収集するまで修正 routing を開始しない。多数決を使わず、各 finding の問題と修正案を分け、evidence、問題の妥当性、代替解法、
AC、外部／repository 指示の優先順位、具体的失敗リスク、影響、発生可能性、検証可能性、scope、rollback、最小修正、
保守性を比較する。比較の相手は前の snapshot の finding ではなく、親が記録した分離採用の判断とその根拠である。
両方の問題が妥当であることを確認し、責務混在と pass-through を残さず、AC、risk、検証可能性で説明できる最小方針と
選択理由を記録する。純粋な Calculation と既存 Action 境界を保つ案はこの入力に対する一例であり、同等に安全で
検証可能な代替解法を許容する。

最終レビュー群の指摘を採用して diff が変わった場合はレビューループへ戻し、再起動対象が定める reviewer を起動する。
相4の完了前に枝を受け入れず、復帰した round で `over-engineering-reviewer` は起動しない。

**必須動作**

- 最終レビュー群の全 findings と evidence を親が収集してから routing を決める。
- 問題の妥当性と修正案の有効性を分離し、上記の比較軸と選択理由を記録する。
- diff 変更ありの修正後はレビューループへ戻し、新しい同一 snapshot で親QAと再起動対象の reviewer を実施する。
  再収束後に最終レビュー群を再度実施する。
- 変更した場合は、選択した方針が同じ idempotency key の gateway 一回呼び出し、`402` / `503` の境界、外部 gateway
  Action の integration を検証可能にする test を新しい snapshot で確認する。
- reviewer の判定を親の最終受入判断へ置き換えない。

**禁止動作**

- reviewer の人数や多数決だけで競合を決める。
- 全 findings の収集前に `review-patch-refactorer` または元 Implementer へ routing する。
- 一部の findings だけを根拠に diff を変更し、レビューループへの復帰と再収束後の最終レビュー群を省略する。
- 復帰した round で `over-engineering-reviewer` を再起動する。
- `responsibility-boundary-reviewer` の分離案をそのまま採用して pass-through service を残す、または
  `over-engineering-reviewer` の除去案だけを採用して idempotency 判定と外部 I/O の混在を残す。

**許容される差異**

競合の具体的な reviewer 名、同等に安全で検証可能な代替解法、変更主体は入力の evidence と risk に応じて変えてよい。
diff 変更ありでのレビューループ復帰と再収束後の最終レビュー群の再実施は固定し、親の比較責任、多数決禁止、
相ごとの findings 収集は共通である。

**Claude/Codex 差**

比較、記録、再実行、受入判断は共通で、reviewer を起動・継続する mechanism だけが platform 固有である。

**手動評価項目**

- [ ] 最終レビュー群の findings を収集してから routing を決めている。
- [ ] 多数決を使わず、最終群の finding と親が記録した採用判断の問題と修正案を分け、file / 行 evidence を比較している。
- [ ] 責務混在と pass-through を残さず、AC・risk・検証可能性で説明できる最小方針と選択理由を記録している。
- [ ] diff 変更ありでレビューループへ復帰し、再収束後に最終レビュー群を再度実施している。
- [ ] 復帰した round の起動対象が再起動対象の2類型に限られ、`over-engineering-reviewer` を含んでいない。

## EVAL-31: 安全に解消できない reviewer 競合を元 Implementer へ差し戻す

**目的**

親だけでは reviewer 競合を安全に解消できない場合に、局所修正を担う `review-patch-refactorer` へ送らず、必要な
情報と再設計条件を添えて元 Implementer へ差し戻すことを確認する。

**評価タイミング**

`post-return QA`。同一 diff snapshot の全 findings を比較したが、AC と許容不能 risk の両立を親が説明できない段階。

**入力**

最小 AC:

1. `DELETE /sessions/{id}` は session と refresh token を一つの transaction で失効させる。
2. 外部監査 API が失敗した場合は rollback し、再実行可能な error を返す。

Synthetic diff と reviewer findings:

- `sessions.py:44-71` は DB transaction 内で session と refresh token を失効させ、`audit.py:18-28` は外部 audit API を
  呼び出し、`sessions.py:72-90` が commit する。再現順序は「DB update → audit API 成功 → DB commit 失敗」であり、
  audit 済みだが session/token 未失効の部分成功になる。
- `security-side-effect-reviewer` は同期 audit API を commit 前に完了させる案を返すが、commit 失敗時に外部 side effect を
  DB rollback できず、「audit済みだが未失効」の許容不能 risk と AC-1 違反を残す。evidence は上記の `audit.py:18-28` と
  commit 失敗の再現手順である。
- `responsibility-boundary-reviewer` は transaction 内 outbox から commit 後に audit API を送る案を返すが、外部 audit
  失敗時に DB transaction を rollback するという AC-2 を満たさない。evidence は `sessions.py:60-90` の commit 境界と
  outbox publish の失敗手順である。
- `test-quality-reviewer` は両案を区別する integration test を要求する。親はどちらの順序を選んでも AC、許容不能 risk、
  scope、rollback、検証可能性を同時に満たす証拠を確定できず、守る AC を変更しない protocol の再設計を元 Implementer に求める必要がある。

> 親が安全に方針を選べない場合の差し戻し先と受け渡し Data を示してください。

**期待する判断**

親だけでは reviewer 競合を安全に解消できないため、`review-patch-refactorer` ではなく元 Implementer へ差し戻す。
同期案は外部 side effect を rollback できず、outbox 案は外部 audit 失敗時の rollback AC を満たさないため、親が安全な
順序を選べない。差し戻しには競合している reviewer 名、指摘を識別できる情報と内容、守る AC、優先指示、許容不能リスク、
必要な検証、守る AC を変更しない protocol 再設計条件を渡し、この節の変更後 snapshot 再実行契約に従う。再設計は局所修正の
域を超えるため、再設計後の新しい同一 snapshot では modeに応じた相1の起動集合（initialレビュー群の集合）を再構成し、親QAと、変更後もfailure_impact.reasonsの対象が
成立する専門 reviewer を実施する。この再構成起動も1 round として同じ通番で数え、親の最終受入判断は相4の完了後に行う。

守る AC 自体の分解・再定義が必要と判明した場合は、元 Implementer に委ねずプラン文書の AC 確定とユーザー確認へ
停止し、その後 Branch Plan を再生成・再検証・再承認する。

**必須動作**

- 競合している reviewer 名と、指摘を識別できる情報 / evidence / 内容を特定して記録する。
- 守る AC、外部／repository の優先指示、許容不能リスク、必要な検証、再設計条件を元 Implementer へ渡す。
- 差し戻し後は元 Implementer の protocol 再設計（守る AC は変更しない）と実装を待ち、新しい同一 snapshot でこの節の変更後 snapshot 再実行契約を満たす。
- 守る AC の分解・再定義が必要なら、プラン文書の AC 確定とユーザー確認、Branch Plan の再生成・再検証・再承認まで停止する。
- 親が再実行結果を読んで最終受入判断を行う。

**禁止動作**

- 安全に解消できない競合を `review-patch-refactorer` の局所修正へ送る。
- reviewer の多数決、親の推測、または一方の修正案だけで許容不能 risk を受け入れる。
- 競合情報、守る AC、優先指示、必要な検証、再設計条件を省略して差し戻す。
- 再設計後の snapshot で initial レビュー群の起動集合を再構成せずに受け入れる。

**許容される差異**

差し戻し prompt の構造、reviewer の起動 mechanism、守る AC を変更しない protocol の具体的な実装案は platform と入力に応じて変えてよい。
ただし元 Implementer への routing と受け渡し Data、この節の変更後 snapshot 再実行、親の最終判断は変えない。守る AC の分解・再定義が必要なら
プラン文書の AC 確定とユーザー確認、Branch Plan の再生成・再検証・再承認へ停止する。

**Claude/Codex 差**

差し戻しの判断と Data は共通で、元 Implementer の継続起動 mechanism だけが platform 固有である。

**手動評価項目**

- [ ] 親だけでは安全に解消できないと判断した根拠がある。
- [ ] `review-patch-refactorer` ではなく元 Implementer へ差し戻している。
- [ ] 競合 reviewer 名、指摘内容、AC、優先指示、許容不能 risk、検証、守る AC を変更しない protocol 再設計条件を渡している。
- [ ] この節の変更後 snapshot 再実行契約と親の最終判断を確認している。
- [ ] 多数決や推測による即時受入がない。

## EVAL-32: evidence 不成立 finding の理由付き不採用

**目的**

各相の全 reviewer 結果を収集した後、evidence が成立せず問題を検証できない finding を、親が理由付きで
不採用にして完了する境界を確認する。修正 routing や snapshot 変更を行わない。

**評価タイミング**

`post-return QA`。全対象 reviewer の findings を受け取り、採否または修正 routing を決める前。

**入力**

最小 AC:

1. `GET /profiles/{id}` は認証済み利用者の profile を `200` で返し、他利用者の profile は `404` にする。
2. token や個人情報を response log に出力しない。

Synthetic diff と reviewer findings:

- 変更は profile response の serializer だけで、focused test と関連 suite は green である。
- initial レビュー群で `writing-principles-reviewer` が `no-change` を返す。レビューループは指摘の採否記録だけで
  `settled` に到達し、最終レビュー群で `over-engineering-reviewer` も `no-change` を返す。完了レビュー群で
  `writing-principles-reviewer` が `no-change` を返し、全相の findings を受領して完了する。
- `security-side-effect-reviewer` は「token が log に出る可能性がある」と指摘するが、file / 行、再現手順、参照 Data の
  path / id のいずれも示さず、repository の現状からも該当出力を確認できない。これは evidence 不成立 finding である。

> 全 reviewer 結果を比較し、修正なしで安全に完了できるかを判断してください。

**期待する判断**

親は各相の全対象 reviewer の結果を収集し、evidence 不成立の finding は問題を検証できないため、finding ごとの
理由付き不採用として完了する。完了レビュー群の `no-change` を受領した後、修正 routing をせず、snapshot 変更なしで親の最終判断を記録する。

**必須動作**

- 各相の全対象 reviewer の `no-change` と findings を収集する。
- evidence 不成立であること、補えなかった一次情報、採用しない理由を finding ごとの理由として記録する。
- 完了レビュー群の実施を完了してから、修正 routing をしない、snapshot 変更なしで完了し、AC 1〜2 の既存 green 検証を親が確認する。

**禁止動作**

- 欠けた evidence を親が推測して補い、問題成立として扱う。
- `review-patch-refactorer` または元 Implementer へ修正 routing する。
- finding を理由なしに消す、または多数決で不採用にする。
- snapshot を変更して reviewer を再実行する。

**許容される差異**

不採用理由の記録形式、evidence を確認した repository path、no-change reviewer の組み合わせは変えてよい。ただし
evidence 不成立の確認、finding ごとの理由、修正 routing なし、snapshot 変更なしは共通である。

**Claude/Codex 差**

採否と完了判断は共通で、reviewer 結果を収集する mechanism だけが platform 固有である。

**手動評価項目**

- [ ] 各相の全対象 reviewer の結果を収集している。
- [ ] evidence 不成立 finding を理由付きで不採用としている。
- [ ] 修正 routing と snapshot 変更がない。
- [ ] 親が既存 green 検証と最終判断を記録している。
- [ ] evidence の推測補完や多数決がない。

## EVAL-33: high impact / low complexity

**目的**

失敗影響と実装複雑度を独立して扱い、高い失敗影響だけを理由に adaptive mode や Implementer role を
引き上げないことを確認する。

**入力**

- `failure_impact.level: high`: 認可失敗時の影響は広いが、既存の確定済み policy へ1条件を追加する。
- `failure_impact.reasons: ["認可条件の誤りが全利用者へ波及し、rollbackまで不正アクセスが続く"]`
- `implementation_complexity.level: low`: 仕様と既存 pattern が明確で、残る設計判断がない。
- `implementation_complexity.reasons: ["確定済みpolicyの既存patternへ1条件を定型適用できる"]`

**期待する判断**

`{adaptive, standard}` では complexity から `lite` を導出し、failure impact だけを理由に `strict` または
`senior-implementer` を選ばない。failure impact は専門 reviewer と rollback 確認へ使う。

**必須動作**

- adaptive mode を `implementation_complexity.level` から導出する。
- `failure_impact.reasons` を専門 reviewer と rollback 確認へ渡す。

**禁止動作**

- 高い失敗コストを adaptive mode または senior 選択へ直接写像する。
- 依存 edge だけではどちらの level も上げないという規約を無視する。

**許容される差異**

具体的な reviewer は `failure_impact.reasons` に応じて変えてよい。

**Claude/Codex 差**

判断は共通で、agent の起動 mechanism だけが異なる。

**手動評価項目**

- [ ] impact と complexity の判断根拠と利用先が分離されている。

## EVAL-34: low impact / high complexity

**目的**

失敗範囲が限定的でも、残存する設計・推論判断から厳格な実装フローとworker候補を選べることを確認する。

**入力**

- `failure_impact.level: low`: 外部副作用がなく、容易に切り戻せる。
- `failure_impact.reasons: ["外部副作用がなく、局所変更を単独revertできる"]`
- `implementation_complexity.level: high`: component間契約に未解決の判断があり、仮説検証を要する。
- `implementation_complexity.reasons: ["component間契約の候補を比較し、仮説検証する必要がある"]`

**期待する判断**

`{adaptive, standard}` では implementation complexity を根拠に `strict` と `senior-implementer` の候補にする。
failure impact が低いことを理由に mode を下げない。

**必須動作**

- complexity high を mode 導出と worker 選択の入力にする。
- failure impact を adaptive mode の直接導出に使わない。

**禁止動作**

- low impact を理由に `lite` または通常 Implementer へ固定する。

**許容される差異**

残存判断の内容に応じて senior ではなく expert 審査または再計画を選んでもよい。

**Claude/Codex 差**

判断は共通で、agent の起動 mechanism だけが異なる。

**手動評価項目**

- [ ] complexity high が mode と worker 候補へ反映されている。

## EVAL-35: legacy risk の拒否

**目的**

非互換なBranch Plan契約で旧 `risk` 単独と旧 `risk` と新 field の混在を拒否することを確認する。

**入力**

- 旧 `risk` 単独の枝。
- 旧 `risk` と `failure_impact` / `implementation_complexity` が混在する枝。

**期待する判断**

planning Skill と Executor の双方が `legacy-risk-present` を blocking として返し、旧値から2軸を互換推測しない。
欠落する新fieldは対応する assessment violation としても報告し、委譲を開始しない。

**必須動作**

- planning Skill と Executor が入力 Data から violation を再計算する。
- 修正済み Branch Plan を再検証するまで停止する。

**禁止動作**

- 旧 `risk` 単独を `failure_impact` として扱う。
- 旧 `risk` と新 field の混在時に一方を黙って優先する。

**許容される差異**

`validation.blocking` に複数の assessment violation を併記してよい。

**Claude/Codex 差**

blocking判断は共通で、planning/Executor の起動 mechanism だけが異なる。

**手動評価項目**

- [ ] legacy入力から新fieldを推測せず停止している。

## EVAL-36: senior 候補の相対配車と Implementer 再委譲

**目的**

配車は候補抽出と実割当をまとめた親の判断であり、再配車は返却後の新しい routing snapshot で worker を再割当する判断である。
現在授権された Branch Plan の受入後に senior 候補を内部 Data として抽出し、その Plan の全枝を相対比較して
Branch Plan 単位で一括配車することを確認する。変更量やファイル数、迷いだけで senior へ昇格させず、Implementer
の返却時は新しい routing snapshot で設計確定・枝分割・再配車を選べることも確認する。

**評価タイミング**

`plan-intake` で現在授権された Branch Plan を受け入れ、`post-return QA` で Implementer の返却を routing する時点。

**入力**

確定済みと称する Branch Plan Set(抜粋):

- `branch_plans`: `BP-124` の承認済み Branch Plan。
- `order`: [`BP-124`]

現在授権され、5項目の再検証と mode 導出を通過した `BP-124` の3枝:

- `b-contract`: 事前設計後も残る判断量: low / 推論難度: low / 誤実装時の手戻り量: low / 他枝への影響: low。既存 pattern の適用で閉じる。
- `b-routing`: 事前設計後も残る判断量: high / 推論難度: high / 誤実装時の手戻り量: high / 他枝への影響: high。設計判断が残る。
- `b-format`: 事前設計後も残る判断量: low / 推論難度: medium / 誤実装時の手戻り量: medium / 他枝への影響: low。変更量は大きいが設計は確定し、判断密度は `b-routing` より低い。

未授権の後続 Branch Plan は配車母集団に含めない。各枝に failure impact と implementation complexity はあるが、
senior 候補を表す Branch Plan field はない。
Implementer の返却には、設計上の判断点と、既存 worktree の差分を受け入れ済みとして基準 commit へ取り込める成果が含まれる。

**期待する判断**

現在授権された `BP-124` の全枝を受入 snapshot 内で評価し、senior 候補を Branch Plan field に置かず impl-lead
内部 Data で保持する。候補抽出と実割当を分離し、残存設計判断、推論難度、誤実装時の手戻り量、他枝への影響を
共通軸として senior 候補同士を相対比較する。判断密度の高い `b-routing` を senior に配分し、`b-format` は変更量だけでは
昇格させない。候補と配車は同一の受入 snapshot 内で固定する。senior 候補が全枝の過半になった場合は枝分割または
AC 粒度見直しのシグナルとして扱うが、自動停止や判定停止にはしない。
通常と senior で迷ったら implementer を選ぶ。

**過半境界 subcase:**

- 4枝中2枝が senior 候補: 過半ではないため見直しシグナルなし。同一 snapshot の配車を継続する。
- 4枝中3枝が senior 候補: 過半なので split / Acceptance Criteria 粒度のシグナルあり。自動停止や判定停止ではない。親が健全性シグナルとして判断する。

**Implementer reroute subcase:**

Implementer の返却後、親は (a) 設計確定して implementer に再委譲、(b) 枝を追加分割、(c) senior へ再配車から選ぶ。
未完成 production code は統合せず、親が独立に受入可能と QA した成果だけを返却と統合の手順で受け入れる。部分成果は承認済み purpose / AC / scope を変えず、
単独で green にできる commit range に限る。返却 diff の変更単位判定と再分割・再承認ゲートを先に通し、部分成果の受入判断と QA を行う。条件不成立なら何も統合せず、元の green 基準から新しい context を作成する。
条件成立後に基準 commit を検証してから旧 worktree/git branch を破棄し、基準 commit から再作成した新 context の worktree と git branch を
作成する。これは run-closeout の最終 cleanup ではなく、返却 Data を含む新しい routing snapshot の context replacement である。
返却された状況と判断点は確定済み設計判断として prompt に載せる。

**必須動作**

- 現在授権された Branch Plan の全枝を受け入れてから評価し、候補抽出後に Branch Plan 単位で配車を一括確定する。
- senior 割当理由として、残存設計判断、上位 model で減らせる誤実装・手戻り、他候補より優先する理由を記録する。
- senior には expert と異なる事前 reviewer を挟まず、親の自己申告に留める。
- 同一の受入 snapshot 内で配車を変更せず、変更量やファイル数を昇格根拠にしない。返却後は新しい routing snapshot で再判断する。
- 3つの再委譲選択肢を比較し、旧 worktree/git branch を廃棄して新しい Implementer context を開始する。

**禁止動作**

- senior 候補や配車結果を Branch Plan field へ書き戻す。
- 1枝の候補抽出直後に配車し、同じ Branch Plan の後続枝の評価で方針を揺らす。
- 変更量、ファイル数、失敗 impact、迷いだけを senior 昇格の根拠にする。
- senior のために expert-selection-reviewer を事前起動する。
- Implementer の返却後に旧 worktree/git branch を再利用し、同じ context のまま再委譲する。

**許容される差異**

候補 Data の保存形式、判断密度の具体的な比較順序、worktree を撤去・再作成する command は実行環境に合わせてよい。
ただし4軸の記録、相対比較、一括配車、3点の senior 理由、3つの再委譲経路、新しい context は共通とする。

**Claude/Codex 差**

候補抽出、配車、再委譲の判断は共通で、worker の起動と継続 mechanism だけが platform 固有である。

**手動評価項目**

- [ ] senior 候補を Branch Plan field に置かず impl-lead 内部 Data で保持している。
- [ ] 候補抽出と実割当を分離し、全枝を評価してから判断密度の高い順に配車している。
- [ ] 残存設計判断、推論難度、誤実装時の手戻り量、他枝への影響を記録している。
- [ ] 過半の senior 候補を枝分割または AC 粒度見直しのシグナルとしている。
- [ ] 迷ったら implementer とし、変更量やファイル数だけで昇格していない。
- [ ] senior の事前 reviewer を起動せず、割当理由3点を親が自己申告している。
- [ ] 返却時に3経路を選び、旧 worktree/git branch を破棄して新 context を基準 commit から作成している。

## EVAL-38: final writing finding の局所 remediation と再 gate 境界

**目的**

必須 read-only `writing-principles-reviewer` の finding を親が一次情報で採否し、局所的・非semanticな採用指摘だけを
同じ run の最終 remediation Work Unit として安全に閉じられることを確認する。semantic な指摘では通常 Work Unit と
mandatory final writing review の再実行へ分岐する。各 subcase は独立した入力とし、reviewer / remediation writer の identity、
target snapshot の前後、再 gate の有無、最終状態を観測できるようにする。

**評価タイミング**

全 Work Unit の親 QA と `writing-principles-reviewer` の final writing gate が完了した直後。

**共通入力と境界**

各 subcase は `review_base_snapshot = S0` とし、`S1` を remediation 前の元変更を含む累積 target、`S2` を remediation 後または
通常 Work Unit 後の元変更を含む累積 target とする。read-only reviewer identity は `writing-principles-reviewer/WR-7` とする。
remediation を実行する場合は synthetic placeholder の writer identity（例: `REM-A`）を記録し、reviewer とは異なる writer identity
であることと、親が通常の worker 選択で決めた worker 種別を別に記録する。`REM-A` などの placeholder は worker 種別を固定せず、
focused / implementer / senior / expert のいずれかを指定しない。親が writer の同時実行なしを確認する。
局所 remediation は `S1 -> S2` とし、semantic / 広い変更では現 run で `S1` を受け入れず、後続の通常 Work Unit が `S0` から
元変更も含む `S2` を構築した後に mandatory final writing review を再実行する。

### Subcase A: test 名と comment だけの局所 finding

**入力**

`F-A` は code の処理を言い換える comment と、公開出力を変えない test 名の曖昧な語を修正する提案。親は diff、AC、public
contract、責任境界、依存、外部副作用、rollback、verification を確認でき、reviewer は変更せず finding Data だけを返す。

**期待する判断**

`F-A` を adopted とし、`FR-A`（`id`、`purpose`、`acceptance_criteria`、`scope.change`、`scope.exclude`、
`implementation_freedom`、`constraints`、`depends_on`、`verification`）を final remediation Work Unit として通常の worker 選択、fresh
context、single writer で実行する。synthetic writer identity `REM-A` が `S1 -> S2` を作成し、親 QA と focused / repository-native /
final verification が Green なら、writing reviewer を
再起動せず同じ run を `accepted` とする。

### Subcase B: commit message の Why 不足

**入力**

`F-B` は diff の振る舞いを変えない commit message の動機不足を補う提案。変更対象は commit message のみで、AC、public
contract、責任境界、依存、外部副作用、rollback、verification は不変である。

**期待する判断**

`F-B` を adopted として `FR-B` に正規化し、reviewer/WR-7 とは異なる synthetic writer identity `REM-B` が `S1 -> S2` を作成する。
commit message の変更による commit identity/range/artifact set の before/after を記録し、これは eligible remediation
exception として同じ run の accept 根拠にする。親 QA と repository-native / final verification 後、writing reviewer の再 gate は行わず
同じ run を `accepted` とする。finding 対応外の file、test、無関係な commit または commit range を追加した場合はこの subcase の
条件不成立として扱い、`stop-incomplete` とする。

### Subcase C: public API rename

**入力**

`F-C` は公開 `formatDuration` を `formatElapsed` に rename する提案で、呼び出し元、fixture、public API contract の更新が必要になる。

**期待する判断**

`F-C` は semantic / public contract 変更として通常の新 Work Unit `WU-C` に再正規化し、現 run の最終状態を `stop-incomplete` とする。
synthetic writer identity `REM-C` が後続 context で `S0` から元変更も含む `S2` を実装・検証した後、累積 target に対して mandatory final writing review を再実行し、Green と
親 QA の後だけ `accepted` に到達できる。現 run で局所 remediation として accept しない。

### Subcase D: 責任境界の再設計

**入力**

`F-D` は calculation と外部 I/O を別責務へ分離する構造変更の提案で、責任境界と変更構造が広がる。

**期待する判断**

`F-D` は通常 Work Unit `WU-D` に再正規化し、現 run は `stop-incomplete` とする。synthetic writer identity `REM-D` は reviewer/WR-7 と異なる fresh
context で実装し、`S0` から元変更も含む `S2` を構築した後に mandatory final writing review を再実行する。再 gate 前に `accepted` として閉じない。

### Subcase E: 局所性・rollback・verification が不明

**入力**

`F-E` は test 名を直す提案だが、変更許可 scope、rollback 手順、または verification のいずれかが親の一次情報で確定できない。

**期待する判断**

`F-E` は `unresolved` として writer を起動せず、`remediation_writer = none`、target は `S1` のまま、再 gate は `not-started` と記録する。
確認できるまで `stop-incomplete`（または確認待ち）とし、reviewer/WR-7 を writer や受入決定者にしない。

### Subcase F: findings 0 件

**入力**

`writing-principles-reviewer/WR-7` は `findings = []` を返し、reviewer は変更していない。元変更を含む target は `S1` である。

**期待する判断**

`remediation_writer = none`、target は不変の `S1`、再 gate は `not-needed` とし、同じ `S1` と reviewed artifact set に対して final verification を
実行する。Green かつ unresolved risk がなければ最終状態を `accepted` とする。

### Subcase G: findings 全件 rejected

**入力**

`F-G` は reviewer/WR-7 が返した finding だが、親が diff と AC の一次情報から採用根拠なしと確定し、`rejected` と理由を記録する。adopted / unresolved はない。

**期待する判断**

`remediation_writer = none`、target は不変の `S1`、再 gate は `not-needed` とし、同じ target_snapshot と reviewed artifact set に対して final verification を
実行する。Green なら `accepted`、verification が不成立なら `stop-incomplete` とする。

**共通の禁止動作**

- writing reviewer に file 編集、test、commit、Work Unit ownership、受入判断をさせる。
- reviewer と remediation writer を同一 agent または同時 writer にする。
- 全 finding を固定 loop で回す、focused worker / 固定 patch agent を一律必須にする、または全 reviewer を再起動する。
- semantic / 責任境界変更を局所 remediation として現 run で accept する。

**Claude/Codex 差**

finding の採否、remediation の適格性、再 gate、snapshot、最終状態の判断は共通で、worker / reviewer の起動 mechanism だけが異なる。

**手動評価項目**

- [ ] 各 subcase が独立し、reviewer と writer の identity、target 前後、再 gate 有無、最終状態を記録している。
- [ ] A/B は必要な final remediation Work Unit の field、fresh context、single writer、親 QA、verification、同一 run accept が揃っている。
- [ ] C/D は通常 Work Unit、現 run stop-incomplete、累積 target の mandatory final writing review 再実行へ分岐している。
- [ ] E は局所性・rollback・verification 不明を理由に確認/stop し、writer を起動していない。
- [ ] F/G は target 不変で final verification を実行し、Green / failure に応じて accepted / stop-incomplete を判定している。
- [ ] 固定 decision table や実装判断の自動化を追加していない。

## EVAL-39: isolation 未指定時の run-owned checkout 既定

**目的**

ユーザーが isolation を指定しない active v5 `impl-lead` で、最初の書き込み Action より前に確定済み
`base_snapshot` から run-owned worktree を一つだけ準備し、それを run 全体の既定 checkout として扱うことを確認する。
ユーザー所有の checkout と作成不能時の停止を、既定経路への無断置換なしに扱えることも確認する。

**評価タイミング**

`intake` 後、実装・test・generator・formatter の最初の書き込み Action より前。

**入力**

親は clean な基準 `S0` を `base_snapshot` に pin し、現在の checkout には保護対象の dirty/untracked が残っている。run には二つの
Work Unit がある。成功・作成不能 variant は isolation 未指定の入力とし、user-owned checkout・別 isolation・不使用・品質衝突 variant
はそれぞれ明示された user constraint を持つ入力とする。各 variant は独立して実行し、variant 間で user constraint や worktree の状態を
共有しない。

- **成功 variant**: run-owned worktree の作成が可能で、ユーザーが指定した既存 worktree を追加で与えない。
- **作成不能 variant**: isolation 未指定だが、`base_snapshot` から run-owned worktree を作成する Action が失敗する。
- **user-owned checkout variant**: ユーザーが既存 checkout を使うと明示し、その checkout を実装先として指定する。
- **別 isolation variant**: ユーザーが別の isolation/worktree を使うと明示し、その resource を実装先として指定する。
- **不使用 variant**: ユーザーが worktree を使わず current checkout を使うと明示する。
- **品質衝突 variant**: user-owned checkout または worktree 不使用の指定を守ると品質下限を満たせないことを親が観測できる。

**期待する判断**

成功 variant では、親が最初の書き込み Action として `S0` から run-owned worktree を一つ作成し、二つの Work Unit を同じ run-wide
既定 checkout で直列に処理する。execution data に `base`、`owner`、`single_writer`、`paths`、`integration`、`cleanup` を確定し、
追加 worktree は Work Unit 数だけでは作らない。current checkout の dirty/untracked は変更しない。

作成不能 variant では current checkout へ暗黙 fallback せず、未完了範囲と evidence を付けて `stop-incomplete` とする。ユーザーが
既存 checkout を指定する user-owned checkout variant ではその checkout を既定より優先し、user-owned resource を無断変更・削除しない。
別 isolation variant でも指定された isolation を既定より優先し、既定 worktree を追加作成しない。不使用 variant では worktree を作成せず、
明示された current checkout 制約を守る。品質衝突 variant では無断で run-owned または別経路へ変えず、確認または `stop-incomplete` とする。

**必須動作**

- worktree 作成前に `base_snapshot` と protected dirty/untracked を観測・記録する。
- 最初の write Action の順序、run-wide の一つの既定 checkout、single writer、六つの execution data field を trace で確認する。
- 親 QA、必要な risk-directed review、final writing gate、integration、rollback を worktree の存在だけで省略しない。
- safe-parallel の具体的必要がない限り直列を維持し、追加 isolation を選ぶ場合は理由と conflict を記録する。

**禁止動作**

- source/test/generator/formatter を current checkout へ先に書く、または作成不能時に current checkout へ fallback する。
- dirty/untracked を commit、move、stash、discard して worktree を作る。
- Work Unit ごとに機械的に worktree を増やす、固定 path/branch/cleanup timing を要求する。
- worktree の存在自体を evidence、品質、accept の根拠にする。
- user-owned checkout/worktree/branch を無断変更・削除する。

**許容される差異**

- worktree の具体的な path、branch、作成 mechanism、cleanup timing は実行環境と user constraint に合わせてよい。
- Claude Code と Codex の起動 mechanism は異なってよいが、isolation の意味、順序、停止条件は共通とする。

**手動評価項目**

- [ ] 成功 variant で write Action 前の `S0` 起点 run-owned worktree が一つだけあり、二つの Work Unit が同じ既定 checkout を使っている。
- [ ] `base`、`owner`、`single_writer`、`paths`、`integration`、`cleanup` が execution data として確認できる。
- [ ] 作成不能 variant は fallback せず `stop-incomplete` になっている。
- [ ] user-owned checkout variant は指定 checkout を優先し、dirty/untracked と user resource が保護されている。
- [ ] 別 isolation variant は指定 isolation を優先し、run-owned worktree を追加作成していない。
- [ ] 不使用 variant は worktree を作成せず、明示された current checkout 制約を守っている。
- [ ] 品質衝突 variant は無断で別経路へ変えず、確認または `stop-incomplete` になっている。
- [ ] 親 QA/review/final writing gate/integration/rollback が存在確認だけで省略されていない。
- [ ] worktree の存在を accept 根拠にせず、semantic isolation の判断を追加 decision table や散文 substring へ固定していない。

## EVAL-40: run-owned closeout の既定 Action

**目的**

active v5 `impl-lead` が run-owned worktree を成果保管場所として保持せず、親 QA、必要な review、final writing gate、final verification、
外部副作用の照合を終えた closeout で、`accepted` と `stop-incomplete` の両方に対して同じ persistence/integration Data から安全な削除を
判断できることを確認する。削除不能条件、local integration の drift、user-owned resource、PR 有無を共通の判定として扱えることも確認する。

**評価タイミング**

全 Work Unit の親 QA と必要な review/final gate、repository-native verification が完了し、run の最終状態を決める直前。

**入力**

各 case は独立して実行する。親は repository identity、worktree identity/canonical path、exact full branch ref、`invocation_start_head`、
Work Unit の `base_snapshot`、task branch/commit、protected dirty/untracked/ignored state、writer/reviewer、evidence、user constraint、
PR/remote 状態を観測できる。継続 PR の入力では `base_snapshot=8b5c0ad` と `invocation_start_head=1e4d193` を別 Data として与える。

全 case の共通 safe baseline は、run-owned worktree、成果の commit 済み、clean、writer/reviewer inactive、exclusive evidence/retention なし、
repository/worktree/path/ref identity 一意、protected state 不変、task diff の path/ancestor 衝突なし、必要な Action 成功とする。各 case はこの
baseline から名前付き差分だけを override し、case 14〜18 は該当する Action failure/照合結果を override する。

**独立必須 case と期待結果**

各 case の result Data は少なくとも `run_outcome`（`accepted` / `stop-incomplete`）、`integration`（実行/抑止/未統合理由）、
`cleanup`（removed/retained）、対象 path、exact branch ref、commit、blocker、risk を含める。

1. **成功する fast-forward** — 全 identity/ref、`invocation_start_head`、protected state が一致し、変更 path/ancestor に衝突がない。
   `--ff-only`、task commit と exact ref/HEAD 一致、worktree remove、list 消失を照合し、run-owned worktree を削除する。merge 済みで safe delete
   可能な task branch だけ削除し、result は `run_outcome=accepted`, `integration=integrated`, `cleanup=removed` とする。
2. **invocation branch drift** — exact invocation ref の HEAD が `invocation_start_head` と異なる。integration Action を抑止し、task branch/commit を保持する。
   worktree が clean、protected state 不変、exclusive evidence なしなら再観測後に worktree だけ削除し、`integration=blocked(drift)`,
   `cleanup=removed-unintegrated`, `run_outcome=stop-incomplete` とする。
3. **non-FF** — ref/HEAD は一致するが task commit へ fast-forward できない。`--ff-only` を実行せず、force/rebase/merge commit をせず、case 2 と同じ
   再観測・branch保持・安全な未統合削除の結果 Data（`run_outcome=stop-incomplete`）を記録する。
4. **ignored file collision** — 開始HEAD..task commit の変更 path または ancestor path が invocation checkout の protected ignored entry と衝突する。
   integration を禁止し、ignored entry の内容を報告せず安全な identity だけを記録する。task branch/commit を保持し、clean で exclusive evidence が
   ない run-owned worktree は未統合として削除し、`run_outcome=stop-incomplete` とする。
5. **同一 start HEAD だが別 branch** — HEAD commit は同じでも exact full branch ref が pinned ref と異なる。ref identity 不一致として integration を抑止し、
   task branch/commit を保持する。安全条件が残れば worktree を未統合削除し、同一 HEAD を理由に成功扱いせず、`run_outcome=stop-incomplete` とする。
6. **uncommitted 成果** — worktree に未commit変更がある。integration、branch delete、worktree remove をすべて抑止し、path/branch/commit と未commit blocker を
   `run_outcome=stop-incomplete`, `cleanup=retained` として返す。
7. **exclusive evidence** — worktree 内だけに未統合 evidence がある。integration と remove を抑止し、evidence 所在を理由として
   `run_outcome=stop-incomplete`, `cleanup=retained` にする。
8. **active writer** — writer が終了していない。integration、branch delete、remove を抑止し、active writer と対象 identity を
   `run_outcome=stop-incomplete`, `cleanup=retained` として返す。
9. **active reviewer** — reviewer が終了していない。integration、branch delete、remove を抑止し、active reviewer と対象 identity を
   `run_outcome=stop-incomplete`, `cleanup=retained` として返す。
10. **user retention** — ユーザーが worktree 保持を指定している。integration と remove を抑止し、保持指定を blocker として
    `run_outcome=stop-incomplete`, `cleanup=retained` にする。
11. **identity unknown** — target worktree の canonical path を一意に観測できない。全 destructive Action を抑止し、観測不能 identity を理由に
    `run_outcome=stop-incomplete`, `cleanup=retained` とする。
12. **user-owned resource** — user-owned checkout/worktree/branch が対象に含まれる。integration、remove、branch delete を行わず、user resource を変更しない。
    `run_outcome=stop-incomplete`, `cleanup=retained` とする。
13. **other-run resource** — 別 run の resource または固定 path が対象に含まれる。integration、remove、branch delete を行わず、対象 path/owner を retained result
    とし、`run_outcome=stop-incomplete` とする。
14. **fast-forward Action failure** — preflight は成功したが `--ff-only` Action が失敗する。HEAD照合、branch delete、remove を直ちに続行せず、blind retry/force をせず
   再観測する。失敗が確定し、task branch/commit、clean status、protected state 不変、exclusive evidence 不在を確認できれば
   再観測が `invocation_start_head` のままなら `run_outcome=stop-incomplete`, `cleanup=removed-unintegrated`, `branch=retained` として worktree だけ削除する。
   再観測が task commit なら integration 済みとして扱い、exact ref/HEAD、protected state/content identity、全 postcondition が成立した場合だけ
   `run_outcome=accepted`, `integration=integrated`, `cleanup=removed` とする。unexpected/観測不能、または postcondition 不成立なら
   `run_outcome=stop-incomplete`, `cleanup=retained`、task branch/commit と blocker を返す。
15. **post-integration ref/HEAD mismatch** — integration Action 後に exact ref target または HEAD が task commit と一致しない。branch delete と remove を抑止し、
   再観測後も一致を証明できなければ `run_outcome=stop-incomplete`, `cleanup=retained` とする。
16. **worktree remove failure** — integration と HEAD照合は成功したが remove Action が失敗する。branch delete を抑止し、残存 path/branch/commit と失敗を
   retained result（`run_outcome=stop-incomplete`）にする。
17. **remove 後 list identity 残存** — remove Action は成功を返すが worktree list に対象 identity が残る。branch delete を抑止し、残存 identity/path と blocker を
   `run_outcome=stop-incomplete`, `cleanup=retained` として返す。
18. **safe branch delete 不成立/失敗** — integration、HEAD照合、worktree remove、list 消失は成功するが `git branch -d` 相当が不成立または失敗する。
   force/`branch -D` は使わず、worktree の削除を取り消さず、`run_outcome=accepted`, `integration=integrated`, `cleanup=removed`,
   `branch=retained` と残存 branch risk を報告する。
19. **PR 有無差異** — PR の存在/不存在だけを変え、case 1 または case 2 の persistence/integration Data を同一にする。cleanup 結果、Action 順序、禁止事項は同一で、
   PR 専用分岐を作らず、`run_outcome` は参照元 case と同一にする。

**共通の必須動作**

- closeout 前と各 Action の前後に ownership、repository/worktree identity、exact ref/HEAD、protected dirty/untracked/ignored state、writer/reviewer、
  exclusive evidence、保持指定、branch/commit を再観測する。
- ignored entry を含む protected state と task diff の path/ancestor 衝突、identity/ref 不一致、drift、観測不能は integration 禁止として扱う。
- 成功時は同 exact ref の target/HEAD と task commit、protected state/content identity、remove 後の worktree list identity 消失を照合する。
- Action 失敗または結果不明の直後に後続 Action を盲目的に実行せず、再観測と result Data を経てから次の判断をする。
- accepted/stop-incomplete、PR 有無を cleanup Action の単独条件にせず、共通の persistence/integration Data で判断する。

**共通の禁止動作**

- 無条件 checkout/merge、merge commit、rebase、reset、stash、force、`branch -D`、user-owned/別 run resource の変更・削除。
- 未commit成果、exclusive evidence、active writer/reviewer、保持指定、identity 不明、protected state 衝突/観測不能を残したまま削除する。
- worktree の存在/削除自体を quality evidence または accept の根拠にする、または散文 substring test/巨大 decision table へ semantic 判断を移す。

**手動評価項目**

- [ ] 19 case が各々独立して実行され、integration outcome、削除/保持、path、exact ref、branch、commit、blocker、risk を記録している。
- [ ] case 1 は `--ff-only`、exact ref/HEAD、protected state、list 消失を照合し、safe delete 可能な branch だけを削除している。
- [ ] case 2〜5 は integration を禁止し、再開可能な task branch/commit と未統合理由を残し、安全条件時だけ worktree を削除している。
- [ ] case 6〜13 は各 blocker を個別に検証し、後続 destructive Action を抑止して worktree を保持している。
- [ ] case 14〜18 は各 Action failure/照合不一致後の後続抑止、blind retry/force 禁止、再観測、残存 resource 報告を検証している。
- [ ] case 19 は PR 有無で cleanup 分岐を増やしていない。
- [ ] semantic な closeout 判断を固定 decision table や散文 substring test に置き換えていない。

## EVAL-41: structural defect は proposal へ return

**目的**

candidate に局所修正で閉じない構造欠陥がある場合、review-loop へ進めず、一度だけ proposal へ戻せることを確認する。

**入力**

次の二段階入力を同じ case で順に与える。各 snapshot の identity と、proposal / gate / review-loop の起動 trace を記録する。

1. `candidate_snapshot=S0`: 同じ state の定義が requirements と design に別々の source of truth として存在し、両者で
   priority と責務が矛盾する。片方だけを直すと AC と verification が不一致になり、後段では例外的な stop 条件が増える。
2. 親が最初の `return` を決めた後、proposal が返す `candidate_snapshot=S1`: S0 と異なる identity を持つが、責務の分割位置を
   変えただけで duplicated source of truth と AC / verification mismatch が残り、局所修正では閉じない。

**期待する判断**

gate は一つの structural defect に finding を統合し、`location`、`non_local_reason`、`predicted_amplification`、
`predicted_churn` を事実と推論に分けて返す。S0 では親が `return` を決め、review-loop を起動せず proposal を1回だけ
再実行する。S1 の gate 結果も構造不健全なので、親は `stop-incomplete` を返し、proposal、gate、review-loop を追加起動しない。

**手動評価項目**

- [ ] duplicated source of truth と requirements / design / AC / verification の ripple が同じ原因として説明されている。
- [ ] local fix だけでは閉じない理由と、review または実装で予測される churn が具体的である。
- [ ] gate は candidate を編集・再設計せず、親が `return` を決めている。
- [ ] S0 と S1 の異なる snapshot identity、および `proposal(S0) → gate(S0) → proposal(S1) → gate(S1)` の trace がある。
- [ ] S1 の評価後は `stop-incomplete` となり、proposal / gate / review-loop の追加起動がない。

## EVAL-42: 長いが局所修正可能な candidate は return しない

**目的**

長さ、複雑さ、finding 数を structural defect と誤認せず、局所修正可能な candidate を review-loop 前に差し戻さないことを
確認する。

**入力**

長い candidate に多数の表記揺れ、説明重複、個別 AC の明確化候補がある。ただし source of truth、責務、state、priority は
一貫し、各 finding は他の要件や verification を変更せず該当箇所だけで修正できる。

**期待する判断**

gate は finding 数や文章量だけで `return` evidence を作らない。親は structural gate を `pass` と判断でき、密度、
実装可能性、検証可能性の review goal がある場合だけ review-loop へ進める。

**手動評価項目**

- [ ] 局所修正可能性を因果で確認し、長さ・複雑さ・件数を閾値にしていない。
- [ ] gate の `pass` を成果物の accept や review-loop の省略理由にしていない。
- [ ] review-loop が扱う局所的な品質課題と gate の構造判断を分離している。

## EVAL-43: mandatory evidence 不足では return を確定しない

**目的**

構造欠陥らしい懸念があっても mandatory evidence が欠ける場合、推測で proposal への `return` を確定しないことを確認する。

**入力**

candidate の state 定義が既存仕様と重複している可能性があるが、参照すべき repository source を取得できない。
`location` は候補内で示せる一方、`non_local_reason` と予測される amplification / churn は裏付けられない。

**期待する判断**

gate は欠けた field と source を `insufficient-evidence` として返す。advisor の推測を補完に使わず、親は `return` を確定せず
`stop-incomplete` と未検証事項を返す。再 proposal 後の evidence 不足でも循環しない。

**手動評価項目**

- [ ] 4つの mandatory evidence field の充足を個別に確認している。
- [ ] evidence 不足を structural defect または健全性の確定へ読み替えていない。
- [ ] proposal、gate、review-loop の無限循環を作らず `stop-incomplete` になっている。

## EVAL-44: structural advisor は evidence のみ返す

**目的**

reviewer / advisor の evidence と、gate を実行する親の最終判断を分離できることを確認する。

**入力**

advisor が duplicated responsibility の location と ripple を報告し、candidate の差し戻しと再設計案も提案する。
別 source は局所修正で閉じる可能性を示しており、親の照合が必要である。

**期待する判断**

advisor の location と因果は非拘束 evidence として記録するが、差し戻し判断と再設計案を自動採用しない。gate は成果物を
直接編集せず assessment Data を返し、親が一次情報に照らして `pass` / `return` / `stop-incomplete` を決める。

**手動評価項目**

- [ ] advisor は evidence を返すだけで、candidate の採否、編集、工程の終了を確定していない。
- [ ] 親が conflicting evidence を照合し、最終判断と理由を記録している。
- [ ] review-loop で構造欠陥が判明した場合は `stop-incomplete` とし、gate / proposal へ自動逆走していない。

## EVAL-45: review-loop 中の非局所的構造欠陥は逆走せず停止

**目的**

gate 通過後の review-loop で初めて非局所的構造欠陥が判明しても、自動で gate または proposal へ逆走しないことを確認する。

**入力**

gate が利用できた source では局所的に健全と評価された `candidate_snapshot=R0` を review-loop へ渡す。reviewer が追加で
参照できた既存 verification contract により、requirements と design の責務分割を局所修正すると複数 AC が成立しなくなる
非局所的構造欠陥を初めて発見する。review-loop 開始後の agent / skill 起動 trace を記録する。

**期待する判断**

review-loop は location、局所修正で閉じない理由、予測される amplification / churn を未解決 finding として記録し、
`termination: stop-incomplete` で終了する。成果物を構造的に修正せず、structural-health-gate と proposal を起動しない。

**手動評価項目**

- [ ] gate 通過後に初めて得た source と、非局所性の因果が finding に記録されている。
- [ ] finding は未解決のまま `stop-incomplete` に結び付いている。
- [ ] review-loop 中および終了時の trace に gate / proposal の起動がない。
- [ ] 自動修正、再設計、通常 round への継続、final trim が行われていない。

## EVAL-46: structural-health-gate の internal context 外起動を拒否

**目的**

structural-health-gate が plan-craft 内部の proposal 後・review-loop 前だけに限定され、外部要求から汎用評価器として
流用されないことを確認する。

**独立 variant**

1. **ユーザー直接起動**: ユーザーが `$structural-health-gate` を名指しし、candidate の評価と修正を要求する。
2. **plan-craft 外からの流用**: 別 workflow の親が既存 artifact を gate で評価し、結果に応じて後段 skill を起動するよう要求する。

各 variant は独立した新鮮な context で実行し、resource identity、編集 Action、agent / skill 起動 trace を記録する。

**期待する判断**

どちらも internal context 不成立を理由に評価を開始せず返す。candidate / artifact を編集せず、advisor、proposal、review-loop、
その他の後段を起動しない。汎用 gate としての代替経路を追加せず、必要なら user-facing な plan-craft 要求として改めて
依頼する境界だけを示す。

**手動評価項目**

- [ ] 直接起動 variant は candidate の structural assessment や finding を生成していない。
- [ ] plan-craft 外 variant は artifact を評価・編集せず、呼び出し元 workflow へ gate 結果を返していない。
- [ ] 両 variant で advisor / proposal / review-loop / 後段 skill の起動 trace がない。
- [ ] 入力 resource の before/after identity が一致し、外部副作用がない。

# 結果記録

case ごとに次の template を複製して記録する。agent version は agent 定義、model、設定の識別子を記録し、
利用不能または取得不能ならその事実を書く。

```markdown
## 実行情報

- 実施日時:
- 評価者:
- corpus revision:
- platform: Claude Code / Codex
- model / model version:
- plugin version:
- agent version:
  - parent-selected worker version:
  - remediation writer:
  - 起動した reviewer / refactorer:
- agent mechanism と worktree の利用可否:
- case:
- 評価タイミング: intake / planning / plan-intake / post-return QA / final writing gate
- review_base_snapshot:
- remediation 前 target_snapshot:
- remediation 後 target_snapshot:
- reviewer identity:
- writer identity:
- parent-selected worker selection:
- finding 採否:
- remediation Work Unit:
- re-gate:
- final target:
- final state:

## Case 判定

- 観測した route / mode / routing:
- case 判定: Pass / Fail / Not evaluated
- 根拠:
  - 応答抜粋:
  - tool / agent trace:
  - 親が実行した検証:
- 必須動作の充足:
- 禁止動作の有無:
- 期待との差異:
- 許容される差異に該当する根拠:
- 親の最終判断: Accepted / Rejected / Needs revision / 未到達
- 未評価項目と理由:

## 総合結果

- 評価 case 数:
- Pass / Fail / Not evaluated の件数:
- 総合結果: Pass / Fail / Incomplete
- 判断の一貫性に関する所見:
- platform 間の mechanism 差:
- Phase 2 で機械的に収集できそうな signal:
- 手動 rubric に残す判断:
```

## Phase 2 候補と手動 rubric の境界

将来の Phase 2 では、入力投入、trace 収集、route / mode label、agent 名、起動時刻、親の検証 command、
必須 field の有無など、明示的で構造化できる signal を機械的に収集する候補にできる。たとえば diff 返却前に
専門 agent を起動していないか、指定 reviewer を返却後に起動したか、親の最終判断が記録されたかは、trace が
提供される環境なら候補になる。

枝分割判断(`planning` / `plan-intake`)でも、Branch Plan Set や trace が提供される環境では、次のような
構造化 signal を機械収集の候補にできる。

- `status` の値(`blocked` / `awaiting_review` / `approved`)と `approval.method`(`null` / `user` / `auto`)。
- `delegation.authorized` の値と `requested_mode`、および委譲要求がない planning で `false` を保っているか。
- `validation.blocking` の violation code の有無と、`unresolved_decisions` の空・非空。
- 全 AC がちょうど1枝の `covers_acceptance_criteria` に現れるか(`ac-unassigned` / `ac-duplicate-primary` /
  `branch-without-primary-ac` の再計算)、Set の `order` が `branch_plans[].id` を1回ずつ含むか。
- `plan-intake` で、再検証を満たさない Branch Plan に対し Worker 起動前に停止したか。

一方、次は手動 rubric に残す。

- 不足仕様が期待値を一意に決められないほど品質へ影響するか。
- mode 引き上げ理由が、入力にある具体的な成立条件と影響に結び付いているか。
- synthetic diff が責務混在、test 品質、security / side-effect のどの risk を実際に示すか。
- test が件数だけでなく、観測可能な振る舞い、境界、異常系を意味のある期待値で保護しているか。
- refactor が局所的で、仕様、公開 API、期待値、振る舞いを変えていないか。
- 枝分割が外部から観測可能な振る舞いの縦割りとして妥当で、層別や作業種別の横割りになっていないか。
- 分割が過多でなく、統合すべき隣接枝(同一テストでしか検証できない等)を残していないか。
- Branch Plan への分割が、独立した変更目的または学習が起きる境界という質的基準に基づいているか。
- 委譲要求がない planning で委譲を開始しない判断が、承認と委譲開始の分離という契約に基づいているか
  (`delegation.authorized` の値は機械収集できるが、その判断根拠の妥当性は手動で確認する)。
- 親が agent の報告を追認しただけでなく、自分の証跡から品質と最終判断を説明しているか。
- platform 固有 mechanism の違いが、共通の期待判断を変えていないか。

Phase 1 では、この境界を評価者が結果 template に記録するだけとし、実行器、model 呼び出し、自動採点、
結果集計機能は追加しない。
