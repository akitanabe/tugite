<!-- Generated from shared/. Do not edit directly. -->

# Finding の修正 routing

## 目次

- evidence を欠く指摘の扱い
- 過剰実装ゲートの除去許可
- 修正先の選択
- 責務境界

## evidence を欠く指摘の扱い

reviewer が示す evidence は [Reviewer findings の共通契約](reviewer-findings.md) の
「指摘ごとの evidence」に従う。
evidence を欠く指摘は、単独でゲート通過の根拠にしない。

親が該当ファイルと行の引用・再現手順・参照した Data の path と id のいずれかを、自分が読んだ diff・
テスト結果・repository の現状から特定できる場合は、親が evidence を補って通常の判断へ戻す。
この扱いは [必須完了ゲート](branch-review.md) の reviewer に限らず、
[専門 reviewer](reviewer-dispatch.md) の reviewer を含む指摘全般に適用する。
## 過剰実装ゲートの除去許可

除去を許可する場合、親は指摘IDごとに次をすべて確認する。

- 除去後も対象 AC を満たす実装と検証が残ること
- 除去しても外部から観測可能な振る舞いと公開契約が変わらないこと
- 除去する操作が局所的で、周辺の再設計を必要としないこと

1つでも満たさない場合は元 Implementer へ差し戻す。

除去後も対象 AC を検証する要素が残るかを親が判定できず、1つ目の条件をそもそも確認できないため、
類型 C（残る検証を特定できないテスト）は修正経路を選ばず、未完了として停止する。

重複テストの除去では、削除する側と残す側をファイルとテスト名で特定し、停止時の Data へ明示する。
個別許可のない除去を行わせない。
## 修正先の選択

すべての reviewer の finding は、修正先または不採用のいずれを判断するより前に、親が重要度を確定する。
この適用範囲とタイミングは、本節内の他の記述の適用有無に関わらず成立する。

親は reviewer が申告した重要度をそのまま採用しない。親が確定する根拠は、finding の evidence と、その
finding が影響する Acceptance Criteria・対象 risk への影響である。reviewer 原稿が `軽微` / `修正推奨` /
`修正必須` の意味を定めている範囲については、その記述を正本として照合する。現状、`impl-lead` が起動する
reviewer に限れば、この範囲は `responsibility-boundary-reviewer` の「修正コストに見合わない指摘は `軽微`
として扱う」だけである。`Pass` / `Needs attention` / `Blocker` のように3区分と異なる語彙で申告する
reviewer の finding は、申告語彙から3区分への写像規則を定義しないため、evidence と AC・対象 risk への
影響だけから確定する。判定区分に相当する項目を持たない reviewer の finding も同じ扱いとする。

親が確定する値は、重要度に相当する項目を持たない finding を含め、常に `軽微` / `修正推奨` / `修正必須` の
いずれかとする。原稿の他の記述が `軽微` / `修正推奨` / `修正必須` で分岐する場合、その分岐は reviewer の
申告値ではなく親が確定したこの値を指す。「責務境界」節の routing はこれに当たる。

廃止した patch 経路の後継実行経路は現 bundle では定義しない。他の reference が既存 actor への経路を
明示する場合だけその経路に従い、経路がない finding は修正 actor を選択・起動せず未完了として停止する。
停止時は finding ID、evidence、重要度、影響する Acceptance Criteria・risk、必要な変更範囲を Data として返す。
理由付き不採用は従来どおり親が記録できる。

## 責務境界

返却物 QA を通過した diff は、最終検証前に親が次を軽量確認する。

- 1つの function、class、module に複数の変更理由が混ざっていないか。
- input validation、業務判断、永続化、外部 I/O、表示整形が同じ場所に詰め込まれていないか。
- DB、API、HTTP、file、framework の具体実装を上位層が知りすぎていないか。
- 副作用が分散し、再実行、test、失敗時の扱いが難しくなっていないか。
- boolean flag や mode 引数で大きく責務を切り替えていないか。
- 既存の責務配置、命名、directory 構成から不自然に外れていないか。
- 分割や抽象化が過剰になっていないか。

この軽量確認で、親 QA が返却 diff から特定した対象リスクとして
`responsibility-boundary-reviewer` の対象リスクが成立したと判断した場合は、
[専門 reviewer](reviewer-dispatch.md) の起動条件に従って起動する。対象リスクが成立する具体例も
[専門 reviewer](reviewer-dispatch.md) が定める。この節は専門 reviewer の起動条件を
独自に定義しない。以下は起動した場合の判定区分ごとの停止判断である。

- `問題なし`: 通過。
- `軽微` / `修正推奨`: 変更が必要なら元 Implementer へ差し戻す。
- `修正必須`: 解消するまで完了せず、元 Implementer へ差し戻す。

`responsibility-boundary-reviewer` は修正しない。新しい reviewer worker として diff text を渡し、
全体判定と、指摘ごとの問題箇所、種類、理由、影響範囲、最小修正方針を返させる。
diff にない既存問題は「既存課題」として判定から分ける。
起動時は[reviewer 起動テンプレート](reviewer-dispatch.md)の全欄を埋め、diff artifact の絶対 path を渡すことを既定とする。
