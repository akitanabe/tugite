<!-- Generated from shared/. Do not edit directly. -->

# Run の終了処理

## 目次

- 未統合で終了する場合
- 統合済み diff review
- 後始末
- 最終報告

## 未統合で終了する場合

通常の `Needs revision` は [修正先の選択](finding-routing.md) へ差し戻し、top-level workflow を継続する。
親が未統合の枝について `Rejected` / `Needs revision` を最終判断とし、
top-level workflow を終了する場合だけ、実行可能な検証を行い、未実行の検証、未統合の理由、
worktree を保持する理由を Data として記録し、
main の手順9へ戻る。
## 統合済み diff review

全枝の統合と検証後、後始末より前に統合済み diff を review する。

親が統合済み diff、test、残存 risk を読み、最終受け入れ判断を記録する。
## 後始末

後始末は、受け入れ判断、最終検証、必要な統合済み diff review を含む最終ゲートをすべて通過した後にだけ行う。
差し戻しまたは再検証の可能性がある間は始めない。

親がこのタスク用に作成した、統合済みで未コミット変更のない worktree を `git worktree remove <worktree path>`
で削除する。削除できない worktree は理由と残った path を最終報告に含める。

この run に生成した diff artifact を[diff artifact の削除](reviewer-dispatch.md)の手順で削除する。永続 QA レポートと
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
