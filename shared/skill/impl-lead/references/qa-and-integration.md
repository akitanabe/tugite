# QA・修正・統合

## 目次

- 返却と統合
- 親の QA
- 専門 reviewer
- reviewer 起動テンプレート
- diff artifact の作成
- diff artifact の受け渡しと停止条件
- diff artifact の削除
- 必須完了ゲート
- 枝レビューの3相
- reviewer 間の競合解消
- 修正先の選択
- 未統合で終了する場合
- 責務境界
- 統合済み diff review
- 後始末と最終報告

## 返却と統合

ここでは Green / Refactor まで完了した枝の最終返却を扱う。`strict` のテスト計画、Red、Green の
中間ゲートは [実装枝の準備と委譲](implementation-branches.md) に従い、未完成の枝を統合しない。
直列受け入れは、commit 単位で返し、親が diff を読んでから1枝ずつ取り込む。

1. Implementer は worktree path、git branch、基準 commit、返却 commit SHA range、変更ファイル、
   実行した command と結果、未コミット変更を返す。
2. 親は `git -C <worktree> status --short` と `git -C <worktree> diff <base>...HEAD` を確認する。
   併せて親の checkout を `git -C <親 checkout> status --short` で確認し、worker の変更が worktree の外へ
   混入していないことを確かめる。親の統合 checkout に生成した diff artifact
   (`.tugite/diffs/<slug>-diff.patch`)は親自身が書き出した既知の untracked file であり、
   この確認によって worker の変更の混入と誤認しない。作成規約は「diff artifact の作成」節に従う。
3. 報告だけで受け入れず、対象 test と実装 diff を開く。
4. QA hard reject は同じ枝へ {{continuation_mechanism}} で差し戻し、修正 commit を追加させる。
5. 専門 reviewer へは task、AC、commit 範囲、変更ファイル、diff text、対象 risk を渡す。
   起動するかどうかは「専門 reviewer」節の起動条件だけで決まり、この手順は渡す Data と diff の
   受け渡しだけを定める。
   周辺コンテキストの追加は「reviewer へ渡すコンテキスト」の選択基準に従う。
   {{new_worker}} は別 worktree で始まり枝の変更を見ないため、作業 tree の存在を前提にさせない。
   ここでの作業 tree は worker worktree を指し、親の統合 checkout に保存した diff artifact を
   reviewer が Read することとは矛盾しない。diff の受け渡しは「reviewer 起動テンプレート」に従い、
   diff artifact の絶対 path を渡すことを既定とし、artifact を生成できない場合だけ diff text 欄へ
   本文を直接記入する。
6. 受け入れ後は統合先の git branch で `git cherry-pick <sha>` または commit range を取り込み、focused test と
   関連する build、typecheck、lint を再実行する。
7. 統合後の green commit を次の枝の基準にする。枝 worktree の green と統合後の green の片方を省略しない。

## 親の QA

`standard` と `strict` では全観点を手を動かして確認する。`lite` では観点0（diff を読む）、観点5
（自分で green を確認）、Acceptance Criteria に対応する振る舞いが検証されていることの確認へ絞ってよい。
`lite` のこの確認は親が diff と検証結果から行うものであり、Implementer への AC 対応表や
Red 証跡の要求に置き換えない。`lite` の前提が崩れた場合は mode を引き上げる。

委譲 mode によらず、次を判定原則とする。

- 検証手段はテストに限定せず、プロジェクトまたはタスクで指定された成功条件（自動テスト、type check、
  lint、build、静的解析、実行結果の確認、手動確認手順、snapshot 比較、API レスポンス確認など）を使う。
- 検証 command が成功したことだけを完了根拠にしない。
- 親は「どの Acceptance Criteria を」「どのテストまたは確認手順で」「どの結果によって」満たしたと
  判断したかを説明できる状態にする。

0. **実装 diff** — 基準 commit からの diff を開き、物理的な scope 逸脱に加えて、枝の
   `out_of_scope` に列挙された責務・作業を含まないことを確認する。既存設計からの逸脱、公開契約の破壊、
   既存 test の弱体化、未承認依存、error handling、resource 解放、concurrency、security も確認する。
1. **振る舞い** — test が private API や実装手順ではなく、外部から観測可能な振る舞いを検証しているか。
2. **網羅性** — AC、境界値、異常系、例外経路、分岐、期待値の根拠が実際の test と一致するか。
3. **TDD** — 新機能または未実装仕様なら Red 出力または段階 commit を確認し、test を実装へ合わせて
   弱めていないか。既存挙動を固定する regression test が追加時点で Green なら、親は AC、test、期待値の
   根拠、既存挙動の対応を実際の test と実装から確認し、既存実装がすでに仕様を満たすという返却根拠が
   妥当か判断する。形式的な Red のための本番 code 変更がなく、mutation を使った場合は親が明示した
   一時検証だけであること、mutation が commit されておらず、変更禁止範囲や本番 code に接触していない
   ことも確認する。
4. **記述原則** — Code=How、test=What、commit=Why、comment=Why Not の配置になっているか。
5. **親の実行** — focused test と関連する全体検証を親が実行し、green を確認する。

## 専門 reviewer

専門 reviewer は特定の risk を深く確認する役割であり、専門 reviewer を汎用コードレビューの代替にしない。
専門 reviewer は mode 名だけを理由に一律起動しない。原則として次の場合だけ使用する。

- ユーザーが専門 reviewer を明示的に要求した場合。
- 親が reviewer の責務と一致する具体的なリスクを特定した場合。

| Reviewer | 対象リスク |
| --- | --- |
| `responsibility-boundary-reviewer` | 責務混在、設計境界、分散した副作用 |
| `test-quality-reviewer` | 弱いテスト、欠けているケース、実装詳細に依存したテスト |
| `security-side-effect-reviewer` | 外部 I/O、破壊的操作、機密データ、セキュリティ影響 |

`responsibility-boundary-reviewer` の対象リスクは、複数層、複数の外部 I/O、新しい abstraction・adapter・service、
責務混在の疑いのいずれかを認めたときに成立する。この具体例は「責務境界」節の軽量確認から持ち込まれる。

対象リスクがない専門 reviewer を無条件で起動しない。起動する場合は対象リスクと review 範囲を明示する。
reviewer は最終的な受け入れ判断を行わない。親が diff、テスト、検証結果を確認し、最終的な受け入れを判断する。

専門 reviewer の起動条件はこの節だけが定める。他の節は、この節の起動条件の具体化、または起動時に渡す
Data の受け渡し規約として書き、独立した起動条件を持たない。

### reviewer へ渡すコンテキスト

親は、レビュー対象とリスクに応じて、必要な周辺コンテキストを選択して reviewer へ渡す。
各 reviewer には原則として次の基本情報を渡す。

- タスクの目的と Acceptance Criteria
- 変更対象と commit 範囲
- 変更ファイル一覧と diff text
- reviewer に確認させる具体的な観点

この基本情報は「reviewer 起動テンプレート」の各欄に対応する。diff の受け渡しは同テンプレートに従い、
diff artifact の絶対 path を渡すことを既定とする。

diff だけでは関連する既存設計や利用箇所を判断できない場合は、次を必要に応じて追加する。

- 関連する interface、type、schema
- 主要な呼び出し元
- 関連する既存テスト
- 周辺の directory 構造
- generated file とその生成元
- 変更対象に関係する既存実装
- 外部指示と、`AGENTS.md`、`CLAUDE.md`、`README.md` の関連部分

コンテキストの選択では次を守る。

- repository 全体を無条件に渡さない。
- reviewer の役割に関係しない情報を過剰に渡さない。
- 親の結論だけを渡さず、reviewer が独立して判断できる一次情報を渡す。
- 周辺コードを渡す場合は、なぜ必要なのかを明示する。
- 外部指示と repository 内の指示が競合する場合は、優先関係を明示する。

## reviewer 起動テンプレート

必須完了ゲートの reviewer と専門 reviewer のどちらを起動する場合も、次のテンプレートの全欄を
1項目ずつ埋めて渡す。該当がない欄は「なし」と記入する。欄を空欄のまま残すことと、欄自体を
削除することを禁じる。

```text
- 対象 reviewer: <reviewer 名>
- 確認させる観点: <reviewer に確認させる具体的な観点>
- 対象リスク: <この reviewer が確認すべき対象リスク>
- review 範囲: <対象ファイル・commit 範囲>
- タスクの目的: <実装枝の目的>
- Acceptance Criteria: <AC>
- 親が明示した制約: <なければ「なし」>
- 基準 commit: <SHA>
- 対象 commit 範囲: <SHA range>
- commit log: <対象 commit 範囲の commit log>
- 変更ファイル一覧: <変更ファイル一覧>
- diff artifact の絶対 path: <path。渡さない場合は「なし」>
- diff text（artifact を生成できない場合）: <本文。artifact を渡す場合は「なし」>
- `git status` の結果: <`git status --short` の結果>
- テスト結果: <検証 command の結果>
- 親が選択した周辺コンテキスト: <選択した context。なければ「なし」>
- そのコンテキストを渡す理由: <理由。なければ「なし」>
- 返却してほしい判定: <reviewer に返してほしい判定区分>
- 前回の指摘と親の採否（再起動時）: <前回指摘IDと採否。初回起動なら「なし」>
```

artifact の作成手順は「diff artifact の作成」節に、受け渡し・確認・停止条件は「diff artifact の
受け渡しと停止条件」節に従う。

「専門 reviewer」節の対象リスクと review 範囲、「返却と統合」手順5 の task・AC・commit 範囲・
変更ファイル・diff text・対象 risk を含め、reviewer 起動時に渡す Data はすべてこのテンプレートの
欄として吸収する。テンプレート外に残る起動時 Data はない。

## diff artifact の作成

reviewer 起動テンプレートの diff artifact 欄へ渡す本文は、基準 commit からの diff をあらかじめ
file へ書き出しておく。

保存先は repository root 相対の `.tugite/diffs/<slug>-diff.patch` に固定する。slug の base の
候補順と正規化手順、Windows 予約名の扱い、衝突時の suffix 選択、ancestor 検査、削除時の再検査、Git
管理は [永続 QA レポート](qa-report.md) の規約を正本として同じ手順に従う。ancestor 検査の対象
component は `.tugite` と `diffs` に読み替える。Markdown file を前提とする path 制約は継承しない。
保持と削除の規約も継承せず、「diff artifact の削除」節で定義する。artifact の path 制約は次のとおり
本 manuscript で定義する。

- target は `.tugite/diffs/` 直下の単一 file に限る。
- 固定の `.tugite/diffs/` prefix を除く file name component に path separator を許可しない。
- `.` または `..` を許可しない。
- 絶対 path を許可しない。

report と別 directory に分けるのは、永続 QA レポートが明示的な削除まで保持される成果物であるのに対し、
diff artifact は reviewer へ diff を渡すためだけの中間物で run 完了時に削除するためである。保持規約の
異なる file を同じ directory へ混在させない。

衝突時は `-diff` を保持したまま `<slug>-diff-2.patch` の順に最初の空きを選ぶ。

本文は worker worktree で取得した `git -C <worktree> diff <base>...HEAD` の出力を、親が転記・要約
せず1回の書き出しでそのまま保存する。保存先 path は親の統合 checkout の repository root を基準に
解決し、ancestor 検査も同じ root で行う。

同一の diff 状態（同じ実装枝、同じ commit 範囲、修正 commit の追加なし）に対する複数 reviewer の
起動では同じ artifact を渡してよい。diff 状態が変わったとき（修正後の再起動、別の実装枝）は
新しい artifact を生成し、変化後に古い artifact を渡さない。

書き出しには、候補 path が既存の場合に上書きせず失敗する Action（例: noclobber を有効にした
redirect）を使う。候補 path の衝突による失敗は次の suffix を選び直す。衝突以外の書き出し失敗は
「diff artifact の受け渡しと停止条件」の確認手順に従い、reviewer へ渡さず再生成するか diff text
経路へ落ちる。artifact 経路を既定とし、diff text の直接受け渡しは同節の停止条件に該当する場合の
例外とする。

保存先 directory が存在しない場合は、ancestor 検査を行ったうえで作成し、作成後に同じ検査を再実行
してから書き出す。

## diff artifact の受け渡しと停止条件

起動 prompt の diff artifact 欄には絶対 path を書く。永続 QA レポートと会話上の報告へ path を
記録する場合は repository 相対 path だけを使う。verbatim 保存される diff 本文はこの記録規則の
適用対象にしない。

diff artifact の欄に path を記入した場合は、reviewer がその file を Read し全文を diff text として
判定根拠にする旨の指示を添える。artifact を生成せず diff text 欄へ本文を直接記入した場合は、その
text を判定根拠にする旨を添える。2つの欄は排他とし、採らなかった側の欄には「なし」と記入して、
両方を同時に有効な指示として残さない。

本文が token、password、cookie、Authorization、private key、`.env` の値、credential 付き URL、
個人情報のいずれかを含む場合、または作成 Action を保証できない場合は artifact を生成せず、diff
text 欄へ本文を直接記入して渡し、生成しなかった理由を記録する。repository 相対 path、コード中の
文字列リテラル、prompt テンプレートの原稿は、diff が構造上含む要素として停止条件に該当しない。

artifact の path を reviewer へ渡す前に、親は diff 全文を自分の context へ読み込まずに書き出し
結果を確認する。確認は書き出し command の exit status が 0 であることと、artifact が空でないこと
の2点で行う。commit を持つ実装枝に対して artifact が空になった場合は、取得元 worktree または基準
commit の指定誤りとして扱う。満たさない artifact は reviewer へ渡さず、「diff artifact の削除」の
手順で削除したうえで再生成し、再生成できない場合は diff text 経路へ落ちる。

## diff artifact の削除

diff artifact は run 完了時に削除する。削除は次の2つの契機で行う。

- 「diff artifact の受け渡しと停止条件」の確認を満たさない artifact を破棄するとき。
- 「後始末」で、この run に生成した diff artifact をすべて破棄するとき。

削除の前に [永続 QA レポート](qa-report.md) の削除時の再検査を行い、対象が `.tugite/diffs/` 配下の
通常 file であることを確認する。symlink、directory、非通常 file は削除しない。削除後に
`.tugite/diffs/` が空になった場合は directory も削除する。空でない場合は残す。

差し戻しまたは再検証の可能性がある間は後始末の削除を始めない。削除できない artifact は理由と
repository 相対 path を最終報告に含める。

## 必須完了ゲート

| ゲート | reviewer | 適用 mode | 対象 |
| --- | --- | --- | --- |
| 記述原則 | `writing-principles-reviewer` | `lite` / `standard` / `strict` | How/What/Why/Why Not の配置、命名、説明 |
| 過剰実装 | `over-engineering-reviewer` | `standard` / `strict` | 除去しても AC と制約を満たせるテストと実装 |

この表の2本は必須の完了ゲートであり、上記の任意起動条件の対象外とする。適用 mode の正本はこの表とする。
`writing-principles-reviewer` は `lite` / `standard` / `strict` のすべてで、各実装枝を受け入れる前に必ず起動する。
`over-engineering-reviewer` は `standard` / `strict` の枝でだけ、受け入れる前に必ず起動し、`lite` では起動しない。
各ゲートを起動する相は「枝レビューの3相」で定める。この節は適用 mode の正本であり、相への割り当てを持たない。

`lite` は親 QA を観点0（diff を読む）、観点5（自分で green を確認）、Acceptance Criteria に対応する
振る舞いが検証されていることの確認へ絞ってよい mode であり（`## 親の QA` の冒頭を参照）、
除去許可の判定に必要な網羅性の確認（観点2: 境界値・異常系・例外経路・分岐・期待値の根拠）が課されない。
`lite` が課すのは AC と検証の対応の識別までであり、その検証が AC をどこまで支えているかの判断は
課さない。除去後も AC を検証する要素が残ることを親が確かめる前提を置けないため、`lite` では
過剰実装ゲートを課さない。

親が取得する `git diff`、`git status`、commit log、テスト結果を、Data として各必須完了ゲートの reviewer へ渡す。
対象は基準 commit からの diff が導入または悪化させた問題に限定し、既存問題を広く探索しない。
これらの情報を取得するために reviewer 自身へ Bash や編集 tool を与えない。
起動 prompt は「reviewer 起動テンプレート」の全欄を埋めて渡す。

reviewer は、指摘がある場合は指摘IDを含む構造化 Data を返す。
`no-change` は reviewer の指摘が0件である正常なゲート通過結果として扱う。
指摘がある場合、親は各指摘IDについて内容を確認し、修正先または不採用を判断して、その判断を記録する。

- 局所的で振る舞いを変えない修正は `review-patch-refactorer` へ渡す。
- テストケース追加、期待値の再検討、仕様判断、設計変更、振る舞い判断が必要な修正は元 Implementer へ差し戻す。
- 指摘を採用しない場合は、親が指摘IDと不採用理由を記録する。

`review-patch-refactorer` による修正後の親QAと reviewer 再確認は、元 Implementer による修正にも適用する。
`review-patch-refactorer` または元 Implementer による修正後は、親が変更後の diff とテスト結果を確認し、
`## 親の QA` の mode 別の適用範囲に従って親 QA を再実行する。再確認する reviewer は
「枝レビューの3相」の「再起動対象」で定める。

枝の受け入れ可否は「枝レビューの3相」の「枝の受け入れ点」で定める。この節では受け入れ条件を重ねて定義しない。

## 枝レビューの3相

親 QA を通過した返却 diff のレビューは、initial レビュー群・レビューループ・最終レビュー群の3相で進める。
どの相でどのゲートと reviewer を起動するかはこの節で定める。適用 mode の正本は「必須完了ゲート」の表であり、
この節では適用 mode の値の組み合わせを再掲しない。

### 1 round の数え方

1 round は相の1回の実施とする。initial レビュー群の実施、レビューループ round の実施、最終レビュー群の実施、
および差し戻しによる再設計後 snapshot への再構成起動が、それぞれ1 round である。起動対象の reviewer が0名でも
実施があれば1 round と数え、起動件数には依存しない。枝の mode により相の起動対象がないため実施しない場合
（`lite` の最終レビュー群）は round を消費しない。起動対象が空でも実施される復帰 round と、起動対象がないため
実施しない相は、この語で区別する。

通番は枝あたりとし、枝の最初の initial レビュー群の実施を round 1 とする。以降の各相の実施を同じ通番で合算し、
枝の途中でリセットしない。同一 snapshot に対して複数の相が実施される場合も、相ごとに別の round として数える。

### 打ち切り条件

次のいずれかでレビューを打ち切る。

- `settled`: レビューループが収束した状態。次をすべて満たす。
  - その時点までに受け取った全指摘に採否が記録されている。
  - 採用した指摘に起因する diff 変更と、それに対する「再起動対象」の実施が完了している。
  - 親が `修正必須` として確定した指摘が解消されている。理由付き不採用だけでは `settled` にしない。
- `rounds-exhausted`: 通番が `branch_review_rounds` に到達した状態。

`branch_review_rounds` は枝あたりの round 上限で、既定は 12 とする。ユーザーが明示した場合だけ変更する。
値はこの節に閉じて持ち、Branch Plan その他の外部 Data へ field を追加しない。

上限判定は通番に対して行い、レビューループ round・最終レビュー群の round・再構成起動・起動対象が空の復帰 round を
すべて算入する。上限規則が発火するのは、枝の受け入れ点が未達のまま新たな round が必要になった場合だけである。
受け入れ点を満たした時点で枝は完了し、通番が上限に達していることを理由に打ち切らない。

`rounds-exhausted` に到達した後は、`settled` 済み snapshot への最終レビュー群の実施が未了である場合のその1回だけを
例外として、通番を消費するいかなる round も開始しない。この上界は round の種類を問わず一様に掛かり、再構成起動も
これに従う。未対応の指摘は未解決として記録する。この上界により、枝あたりの総 round 数は上限＋1 で有界になる。

`rounds-exhausted` で打ち切った枝は受け入れない。親は `Rejected` / `Needs revision` を最終判断とし、
「未統合で終了する場合」へ進む。`standard` / `strict` の枝を過剰実装ゲート未実施のまま受け入れることはない。

### 枝の受け入れ点

枝を受け入れてよいのは次をすべて満たすときだけとする。受け入れ可否を決める条件はここだけに置き、他の節で
別内容を定義しない。

- レビューループが `settled` に到達している。
- その `settled` に対する最終レビュー群の実施が完了し、その指摘の採用による diff 変更が生じていない。
  `lite` の枝は最終レビュー群に起動対象がないため実施せず、`settled` がそのまま受け入れ点になる。
- 最終レビュー群のものを含む全指摘に採否が記録され、不採用には理由が記録されている。
- 未解決または判断未記録の指摘を残していない。
- 親が `修正必須` として確定した指摘が解消されている。理由付き不採用だけでは受け入れ点を満たさない。

「責務境界」節の判定区分ごとの列挙は修正先の routing だけを定める。受け入れ可否はこの受け入れ点に従う。

### initial レビュー群

親 QA の後、同一 diff snapshot へ次を一斉に起動する。

- その枝で適用される必須完了ゲートのうち、`over-engineering-reviewer` を除いたもの。
- 「専門 reviewer」節の起動条件により risk で選択した専門 reviewer。同節の起動条件は、この相の risk 選択と
  レビューループ round の「再起動対象」の第2類型の双方へ効く。専門 reviewer の起動条件はこの1節だけが
  定めるため、この相では他の節の起動指示を数え上げない。

`writing-principles-reviewer` はこの相で枝あたり最低1回実施する。これは下限の保証であり、以降のループ round で
「再起動対象」により再起動されることを排除しない。

全 findings の収集 barrier は「reviewer 間の競合解消」節に従う。

### レビューループ

initial レビュー群の findings を起点に、競合解消 → 採否判断 → 修正 routing → 新しい同一 snapshot の生成を
1 round として繰り返し、`settled` または `rounds-exhausted` に到達するまで進める。各 round にも全 findings の
収集 barrier が掛かる。

#### 再起動対象

レビューループ round で起動する reviewer は、次の1つの規約だけで決まる。この規約はレビューループ round の
起動対象を定める唯一の規約であり、他の節に別内容の列挙を置かない。

- 第1類型 — 直前の diff 変更のきっかけとなった指摘を出した reviewer、および同じ競合解消で修正案が採用され
  なかった競合当事者。指摘が出た相は問わず、initial レビュー群・レビューループ・最終レビュー群のいずれで
  出た指摘にも適用する。競合当事者を含めるのは、採用されなかった側が反対した折衷案を、その reviewer が
  一度も再確認しないまま受け入れ点へ到達させないためである。
- 第2類型 — 変更後に対象 risk が新たに成立する reviewer。この判定は専門 reviewer だけでなく必須完了ゲートにも
  適用し、修正が記述原則の対象（命名、コメント、テスト名、説明）へ触れた場合は `writing-principles-reviewer` が
  これに当たる。

この2類型は起動し、これ以外は起動しない。唯一の例外は `over-engineering-reviewer` で、レビューループ round の
起動対象に含めない。その再確認は最終レビュー群の実施だけが担う。したがって最終レビュー群から復帰した round では
`over-engineering-reviewer` を起動せず、上の2類型に当たる reviewer だけを起動する。

第2類型の「新たに成立する」は、元 Implementer への差し戻しによる再設計のように、変更が局所修正の域を超える
snapshot には適用しない。その snapshot では initial レビュー群の起動集合を再構成し、変更後も対象 risk が成立する
専門 reviewer を起動する。局所修正の round と再設計後の snapshot は、変更が指摘範囲に閉じているかで区別する。
再構成起動は同一通番の1 round として数え、この義務は `rounds-exhausted` 未到達である限りで成立する。

### 最終レビュー群

レビューループが `settled` に到達した確定 snapshot に対して `over-engineering-reviewer` を実施する。この相の
起動対象はこのゲートだけである。

実施の計数単位は収束ごとに1回とする。指摘を採用して diff が変わった場合はレビューループへ戻り、再び `settled` に
到達したらこの相を再度実施する。復帰した round の起動対象は「再起動対象」に従う。

最終レビュー群の指摘とレビューループ中に採用済みの指摘が衝突する場合、親が比較するのは前の snapshot の finding
ではなく、親自身が記録した採用判断とその根拠である。前の snapshot の finding を新しいものとして混ぜない規約は
そのまま掛かる。

過剰実装ゲートをこの相に置くのは、起動回数の削減のためではない。判定軸「取り除いても AC を満たす実装と検証が
残るか」は diff の最終形に対してのみ安定して成立し、中間 snapshot での判定は後続の修正で無効化されうる。判定が
成立する snapshot がこの相にしかないため、ここに置く。

## reviewer 間の競合解消

複数の reviewer が同じ diff に対して異なる指摘または修正方針を返した場合、親は修正先の routing 前に
競合を解消する。ここでいう同一 diff snapshot は、同じ基準 commit から同じ commit 範囲で作成した diff artifact
（artifact を使えない場合は同じ diff text）を指す。snapshot が変わった場合は、変更後の snapshot として扱い、
前の snapshot の finding を新しいものとして混ぜない。

### 全 findings の収集 barrier

- 親は、その相で起動対象となる reviewer を、修正前に同一 diff snapshot へ起動する。initial レビュー群では
  「枝レビューの3相」の initial レビュー群が定める集合、レビューループ round では同節の「再起動対象」が定める
  集合を対象とする。全対象 reviewer から `no-change` を含む全 findings と evidence を収集するまで、修正 routing を
  開始しない。
- 全 findings を収集するまで、差し戻し、finding の採否、受入判断も開始しない。reviewer の起動順や返却順にかかわらず、
  一部の reviewer の提案だけで作業を進めない。
- 各 reviewer へ渡す snapshot の基準 commit、対象 commit 範囲、diff artifact または diff text、変更ファイル、テスト
  結果は同一でなければならない。親は起動順にかかわらず、全対象 reviewer の返却 Data を同じ一覧へ集約する。

### 問題と修正案の比較

親は reviewer の人数や多数決を使わず、各 finding の問題と修正案を分け、evidence と問題の妥当性を確認して比較する。

- 問題: reviewer 名、指摘を識別できる情報と内容、対象箇所、evidence、影響する AC と対象 risk。
- 修正案: reviewer が提案した方針、代替解法、想定する変更主体、変更範囲、検証方法。

親は各問題の妥当性を evidence と repository の一次情報から確認し、提案された修正案を問題そのものと同一視しない。
競合する finding の問題が共に成立する場合は、代替解法を含めて次の判断軸を比較する。

- Acceptance Criteria（AC）と、適用される外部／repository 指示の優先順位
- 具体的失敗リスク、影響、発生可能性、対象 risk の残存
- 検証可能性、scope、rollback
- 最小修正と保守性

親は比較結果、採用した解消方針、採用しなかった修正案と各理由、各 finding の最終状態を記録する。方針は最小かつ
検証可能でなければならず、reviewer の判定を親の最終受入判断に置き換えない。

### 不採用・変更後の再実行

- diff 変更なしで finding を不採用とする場合は、finding ごとに問題を採用しない理由を記録する。その理由記録で完了
  できるが、未解決または判断未記録の finding を残してはならない。
- diff 変更ありの場合、変更主体が元 Implementer または `review-patch-refactorer` のどちらであっても、変更後に新しい
  同一 snapshot を作成する。親はその snapshot で `## 親の QA` の mode 別の適用範囲に従って親QAを再実行し、
  「枝レビューの3相」の「再起動対象」が定める reviewer を起動して、結果を再び全 findings 一覧へ収集する。
  受け入れ可否は同節の「枝の受け入れ点」に従う。
- 再実行では、前の snapshot の finding を自動的に解消済みとみなさない。前回の採否、変更後の evidence、新しい reviewer
  結果を対応付ける。

### 安全に解消できない場合の差し戻し

親だけでは reviewer 競合を安全に解消できない場合（AC、優先指示、許容不能リスク、scope、rollback、検証可能性について、
これらすべてを同時に満たす方針を説明できない場合）は、review-patch-refactorer ではなく元 Implementer へ差し戻す。
差し戻し Data には、少なくとも次を含める。

- 競合している reviewer 名、指摘を識別できる情報および内容、evidence
- 守る AC、適用される優先指示、許容不能リスク
- 必要な検証、rollback 条件、再設計条件、親が安全に決められない判断点

元 Implementer はこの Data をもとに再設計・実装し、親は上記の変更後 snapshot 再実行契約に従う。再設計後も安全に解消できない場合は、同じ
Data と未解決理由を更新して、ユーザー確認または計画の再確定へ停止する。

## 返却 diff の変更単位判定

親は、返却 diff を専門 reviewer 起動や受入の前に読み、1変更単位として渡せるかを判定する。判定は
固定行数やファイル数ではなく、変更理由・Acceptance Criteria (AC)・責務・依存・受入・rollback・検証単位を
対応付けて行う。次のいずれかがある場合は、混在した diff のまま reviewer へ渡したり受け入れたりせず、
「再分割・再承認ゲート」へ進む。

- 独立した変更理由、AC 無関係変更、または異なる責務・依存が混ざっている。
- 異なる rollback・review・前提知識・責務・受入単位・検証単位があり、reviewer が一変更単位として判断しにくい。
- 計画 scope の大幅超過、または承認済み scope と目的の対応を説明できない。

これらが混在し reviewer が一変更単位として判断困難な場合も、同じ停止条件を適用する。

diff が大きいだけでは分割しない。固定行数だけでは分割しない。分割すると依存が不自然になったり、外部から観測可能な検証が成立しなく
なったりする場合は、複数の層や作業種別を無理に枝へ分けず、1変更として扱い、必要な reviewer context と
検証単位を明示する。

## 再分割・再承認ゲート

混在 diff をそのまま reviewer へ渡したり受け入れたりしない。親は次のうち、承認済み契約を保つ整形、
差戻し、または再計画のいずれかを選び、選択理由を記録する。

- scope 逸脱の差戻しを選ぶ。
- 承認済み実装枝の purpose、AC 文言、AC ownership、scope、依存、risk を保てる場合は、commit を分離する、
  最小範囲だけを残す、または別タスク化する。この整形では、既存枝の契約と承認を変更しない。
- 独立した実装枝への分離、または AC ownership・依存・risk の変更が必要な場合は Branch Plan を再生成する。
  blocking violation と Executor 再検証5項目を再計算し、必要なユーザー再承認を得るまで新枝を委譲しない。
- AC 文言自体の分解・再定義が必要な場合は Implementation Plan の AC 確定とユーザー確認へ戻る。その後
  Branch Plan を再生成・再検証・再承認する。再承認後に初めて新枝の委譲を開始する。

分割で依存が不自然または検証不能になる場合は1変更として扱う。この場合も、固定行数を根拠に分割を強制せず、
親が reviewer 起動前に判断を記録する。承認済み契約を保つ整形と、契約・AC の再確定を要する再計画を混同しない。

### evidence を欠く指摘の扱い

reviewer が示す evidence は [Reviewer findings の共通契約](reviewer-findings.md) の
「指摘ごとの evidence」に従う。
evidence を欠く指摘は、単独でゲート通過の根拠にしない。

親が該当ファイルと行の引用・再現手順・参照した Data の path と id のいずれかを、自分が読んだ diff・
テスト結果・repository の現状から特定できる場合は、親が evidence を補って通常の判断へ戻す。
この扱いは必須完了ゲートの reviewer に限らず、「専門 reviewer」節の reviewer を含む指摘全般に適用する。

### 過剰実装ゲートの除去許可

除去を許可する場合、親は指摘IDごとに次をすべて確認する。

- 除去後も対象 AC を満たす実装と検証が残ること
- 除去しても外部から観測可能な振る舞いと公開契約が変わらないこと
- 除去する操作が局所的で、周辺の再設計を必要としないこと

1つでも満たさない場合は元 Implementer へ差し戻す。

除去後も対象 AC を検証する要素が残るかを親が判定できず、1つ目の条件をそもそも確認できないため、
類型 C（残る検証を特定できないテスト）は `review-patch-refactorer` へ渡さず、元 Implementer へ差し戻す。

重複テストの除去では、削除する側と残す側をファイルとテスト名で特定し、起動 prompt へ明示する。
個別許可のない除去を行わせない。

## 修正先の選択

すべての reviewer の finding は、修正先または不採用のいずれを判断するより前に、親が重要度を確定する。
この適用範囲とタイミングは、以下に列挙する起動条件など本節内の他の記述の適用有無に関わらず成立する。

親は reviewer が申告した重要度をそのまま採用しない。親が確定する根拠は、finding の evidence と、その
finding が影響する Acceptance Criteria・対象 risk への影響である。reviewer 原稿が `軽微` / `修正推奨` /
`修正必須` の意味を定めている範囲については、その記述を正本として照合する。現状、`impl-lead` が起動する
reviewer に限れば、この範囲は「責務境界」節が起動する reviewer の「修正コストに見合わない指摘は `軽微`
として扱う」だけである。`Pass` / `Needs
attention` / `Blocker` のように3区分と異なる語彙で申告する reviewer の finding は、申告語彙から3区分への
写像規則を定義しないため、evidence と AC・対象 risk への影響だけから確定する。判定区分に相当する項目を
持たない reviewer の finding も同じ扱いとする。

親が確定する値は、重要度に相当する項目を持たない finding を含め、常に `軽微` / `修正推奨` / `修正必須` の
いずれかとする。原稿の他の記述が `軽微` / `修正推奨` / `修正必須` で分岐する場合、その分岐は reviewer の
申告値ではなく親が確定したこの値を指す。「責務境界」節の routing はこれに当たる。

次の条件をすべて満たす場合に限り `review-patch-refactorer` を起動する。

- 専門 reviewer（必須完了ゲートの reviewer を含む）の具体的な指摘が存在する。
- 親が指摘を確認し、修正対象として採用している。
- Acceptance Criteria は満たされている。
- Acceptance Criteria を変更する必要がない。
- 機能的なテストは green である。
- 修正範囲が局所的である。
- 仕様の再解釈を必要としない。
- 新機能追加ではない。
- 振る舞いを維持したまま修正できる。
- reviewer が修正方針または問題箇所を明示している。
- evidence を欠く指摘は、「必須完了ゲート」の evidence を欠く指摘の扱いに従い、親が evidence を補って
  通常の判断へ戻している。

起動 prompt には少なくとも次の Data を含める。

- 指摘元 reviewer、対象となる指摘ID、指摘本文
- 親が採用した修正条件
- 対象 worktree、git branch、基準 commit、対象 commit 範囲
- Acceptance Criteria
- 変更を許可するファイルと変更を禁止するファイル
- 削除・移動・新規作成の可否と commit の要否
- 必須検証 command
- 除去を許可する場合の、指摘IDごとの除去対象と残す対象。pass-through 層の除去では、付け替えが必要な
  呼び出し箇所のファイルを変更許可リストへ含める

入力が不足する場合、`review-patch-refactorer` は推測で補わず、ファイルを変更せず親へ返す。

`review-patch-refactorer` は指摘範囲だけを修正し、新しい問題を探索しない。仕様変更、ついで修正、
大規模再設計、新規依存追加、通常実装の代行をさせない。親が個別に許可しない限り、ファイルの
新規作成・削除・移動、指摘外のテストケース追加、テストケースの削除、fixture や helper の追加をさせない。

返却後、親は自己申告だけを信用せず、次を再確認する。

- `git -C <worktree> status --short`
- 基準 commit からの変更ファイル一覧と diff
- 許可範囲外の変更がないこと
- 親が個別に許可していないファイルの追加・削除・移動がないこと
- reviewer 指摘外の変更がないこと
- 親が個別に許可していないテストケースの削除がないこと
- テストケースの追加・変更、期待値、skip 設定の変更がないこと
- 除去を許可した場合は、除去対象が許可した指摘IDと一致し、対象 AC を満たす実装と検証が残っていること
- Acceptance Criteria と外部から観測可能な振る舞いが維持されていること
- focused test と関連する全体検証が green であること

次は元 Implementer へ差し戻す。

- Acceptance Criteria 未達
- 仕様誤解
- 機能欠落
- テスト失敗
- 正常系・異常系・境界値不足
- security や副作用の修正に振る舞い変更が必要
- test 品質の修正にケース追加や期待値の再検討が必要
- 過剰要素の除去に仕様判断、AC の再解釈、振る舞い変更が必要
- 失う AC が特定できないテストの除去
- `strict` mode の Red / Green / Refactor 継続
- 元の調査・実装判断が必要

親がその場で直してよいのは、返却後の import 整理と formatter 適用だけとする。共有土台の作成は
委譲前の明示的な例外であり、返却後の仕様判断、case 追加、命名、comment、test 名、設計修正を親が
引き取る理由にはしない。

## 未統合で終了する場合

通常の `Needs revision` は上の修正先へ差し戻し、top-level workflow を継続する。
親が未統合の枝について `Rejected` / `Needs revision` を最終判断とし、
top-level workflow を終了する場合だけ、実行可能な検証を行い、未実行の検証、未統合の理由、
worktree を保持する理由を Data として記録し、
main の手順9へ戻る。

## 責務境界

返却物 QA を通過した diff は、最終検証前に親が次を軽量確認する。

- 1つの function、class、module に複数の変更理由が混ざっていないか。
- input validation、業務判断、永続化、外部 I/O、表示整形が同じ場所に詰め込まれていないか。
- DB、API、HTTP、file、framework の具体実装を上位層が知りすぎていないか。
- 副作用が分散し、再実行、test、失敗時の扱いが難しくなっていないか。
- boolean flag や mode 引数で大きく責務を切り替えていないか。
- 既存の責務配置、命名、directory 構成から不自然に外れていないか。
- 分割や抽象化が過剰になっていないか。

この軽量確認で複数層、複数の外部 I/O、新しい abstraction・adapter・service、責務混在の疑いを認めた場合は、
`responsibility-boundary-reviewer` の対象リスクが成立したものとして「専門 reviewer」節の起動条件に従って
起動する。この節は専門 reviewer の起動条件を独自に定義しない。以下は起動した場合の判定区分ごとの
修正先 routing である。

- `問題なし`: 通過。
- `軽微` / `修正推奨`: 局所的で全起動条件を満たす場合だけ `review-patch-refactorer`、それ以外は元 Implementer。
- `修正必須`: 解消するまで完了しない。振る舞い変更や AC 再解釈が必要なら元 Implementer。

`responsibility-boundary-reviewer` は修正しない。{{reviewer_invocation}} として diff text を渡し、
全体判定と、指摘ごとの問題箇所、種類、理由、影響範囲、最小修正方針を返させる。
diff にない既存問題は「既存課題」として判定から分ける。
起動時は「reviewer 起動テンプレート」の全欄を埋め、diff artifact の絶対 path を渡すことを既定とする。

## 統合済み diff review

全枝の統合と検証後、後始末より前に統合済み diff を review する。

<!-- claude-only:start -->
親が統合済み diff、test、残存 risk を読み、最終受け入れ判断を記録する。
<!-- claude-only:end -->
<!-- codex-only:start -->
環境が提供する場合は `/review` を実行し、利用できない場合は同等の統合済み diff review を親が行う。
結果と対応内容を最終報告へ含める。
<!-- codex-only:end -->

## 後始末

後始末は、受け入れ判断、最終検証、必要な統合済み diff review を含む最終ゲートをすべて通過した後にだけ行う。
差し戻しまたは再検証の可能性がある間は始めない。

<!-- codex-only:start -->
親がこのワークフローで起動した agent を停止する。停止後は、後始末の対象にした agent が継続待機していないことを確認する。
<!-- codex-only:end -->
親がこのタスク用に作成した、統合済みで未コミット変更のない worktree を `git worktree remove <worktree path>`
で削除する。削除できない worktree は理由と残った path を最終報告に含める。

この run に生成した diff artifact を「diff artifact の削除」の手順で削除する。永続 QA レポートと
`<slug>-tests.md` は削除しない。

## 最終報告

- 変更内容
- Implementer が検証したこと
- 統合後に親が検証したこと
- 統合済み diff review で確認したこと
- 追加・変更したテストの一覧
- 未検証の残り

追加・変更したテストの一覧は、追加されたテストを全て読まなくても何が検証されたかを確認できる
ように、次の表で提示する。

| テスト名 | 対象 | 分類 | 検証している振る舞い | 対応 AC |
| --- | --- | --- | --- | --- |

- 行は workflow が追加・変更したテストに限り、スイート全体は走査しない。既存スイートの棚卸しは
  `test-audit` skill の責務であり、この表は語彙(対象・分類・検証している振る舞い)だけを
  揃える。
- 親が QA で読んだ diff から記入する。分類は `正常系` / `境界値` / `異常系` とし、判別できない
  場合はその旨を記す。
- 対象テストがない run は表を出さず `該当なし` と明記する。

会話上の提示に加えて、同じ表を Markdown file としても保存する。会話ログが流れても一覧を後から
参照できるようにするためであり、永続 QA レポートと異なり既定で生成する。

- 保存先は `.tugite/reports/<slug>-tests.md` とする。slug の正規化、衝突時の suffix 選択、
  安全な作成 Action、untrusted field の sanitize、Git 管理と保持は
  [永続 QA レポート](qa-report.md) の規約を正本として同じ手順に従う。衝突時の suffix は
  `-tests` を保持したまま `<slug>-tests-2.md` の順に選ぶ。
- file には見出しと上の表と同じ Data だけを記入し、それ以外の証跡を含めない。
- 対象テストがない run は file を生成しない。
- sanitize できない、または安全な作成 Action を保証できない場合は生成せず、理由を会話上の
  最終報告へ含める。
