# 枝レビューの進行

## 目次

- 必須完了ゲート
- 枝レビューの3相
- reviewer 間の競合解消

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
振る舞いが検証されていることの確認へ絞ってよい mode であり（[親の QA](qa-and-integration.md) の冒頭を参照）、
除去許可の判定に必要な網羅性の確認（観点2: 境界値・異常系・例外経路・分岐・期待値の根拠）が課されない。
`lite` が課すのは AC と検証の対応の識別までであり、その検証が AC をどこまで支えているかの判断は
課さない。除去後も AC を検証する要素が残ることを親が確かめる前提を置けないため、`lite` では
過剰実装ゲートを課さない。

親が取得する `git diff`、`git status`、commit log、テスト結果を、Data として各必須完了ゲートの reviewer へ渡す。
対象は基準 commit からの diff が導入または悪化させた問題に限定し、既存問題を広く探索しない。
これらの情報は親が取得して渡すものであり、reviewer 自身に取得させない。
reviewer が read-only であることの担保は [Reviewer findings の共通契約](reviewer-findings.md) の「read-only の担保」に従う。
起動 prompt は[reviewer 起動テンプレート](reviewer-dispatch.md)の全欄を埋めて渡す。

reviewer は、指摘がある場合は指摘IDを含む構造化 Data を返す。
`no-change` は reviewer の指摘が0件である正常なゲート通過結果として扱う。
指摘がある場合、親は各指摘IDについて内容を確認し、修正先または不採用を判断して、その判断を記録する。
修正先 routing の正本は [修正先の選択](finding-routing.md) とする。

- 局所的で振る舞いを変えない修正は `review-patch-refactorer` へ渡す。
- テストケース追加、期待値の再検討、仕様判断、設計変更、振る舞い判断が必要な修正は元 Implementer へ差し戻す。
- 指摘を採用しない場合は、親が指摘IDと不採用理由を記録する。

`review-patch-refactorer` による修正後の親QAと reviewer 再確認は、元 Implementer による修正にも適用する。
`review-patch-refactorer` または元 Implementer による修正後は、親が変更後の diff とテスト結果を確認し、
[親の QA](qa-and-integration.md) の mode 別の適用範囲に従って親 QA を再実行する。再確認する reviewer は
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
  - 親が [修正先の選択](finding-routing.md) で `修正必須` として確定した指摘が解消されている。理由付き不採用だけでは `settled` にしない。
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
[未統合で終了する場合](run-closeout.md)へ進む。`standard` / `strict` の枝を過剰実装ゲート未実施のまま受け入れることはない。

### 枝の受け入れ点

枝を受け入れてよいのは次をすべて満たすときだけとする。受け入れ可否を決める条件はここだけに置き、他の節で
別内容を定義しない。

- レビューループが `settled` に到達している。
- その `settled` に対する最終レビュー群の実施が完了し、その指摘の採用による diff 変更が生じていない。
  `lite` の枝は最終レビュー群に起動対象がないため実施せず、`settled` がそのまま受け入れ点になる。
- 最終レビュー群のものを含む全指摘に採否が記録され、不採用には理由が記録されている。
- 未解決または判断未記録の指摘を残していない。
- 親が [修正先の選択](finding-routing.md) で `修正必須` として確定した指摘が解消されている。理由付き不採用だけでは受け入れ点を満たさない。

[責務境界](finding-routing.md) の判定区分ごとの列挙は修正先の routing だけを定める。受け入れ可否はこの受け入れ点に従う。

### initial レビュー群

親 QA の後、同一 diff snapshot へ次を一斉に起動する。

- その枝で適用される必須完了ゲートのうち、`over-engineering-reviewer` を除いたもの。
- [専門 reviewer](reviewer-dispatch.md) の起動条件により risk で選択した専門 reviewer。同節の起動条件は、この相の risk 選択と
  レビューループ round の「再起動対象」の第2類型の双方へ効く。risk による専門 reviewer の起動条件はこの1節だけが
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
  同一 snapshot を作成する。親はその snapshot で [親の QA](qa-and-integration.md) の mode 別の適用範囲に従って親QAを再実行し、
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
