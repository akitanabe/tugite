<!-- Generated from shared/. Do not edit directly. -->

# Reviewer findings の共通契約

## 目次

- 位置づけ
- 指摘件数のサマリ行
- 指摘ごとの evidence

## 位置づけ

findings を返すすべての reviewer が共通で満たす2点を定義する。正本はこの reference が持ち、
各 reviewer 原稿は同じ2点を自分の出力形式の語彙で本文に書き下す。

対象は `responsibility-boundary-reviewer`、`test-quality-reviewer`、`security-side-effect-reviewer`、
`writing-principles-reviewer`、`over-engineering-reviewer`、`plan-adversarial-reviewer` とする。
指摘 Data を返さない `expert-selection-reviewer` と `review-patch-refactorer` は対象外とする。

判定語彙、0件の表記、判定対象外の範囲の書き方は各 reviewer 原稿を正本とし、この reference では変更しない。

## 指摘件数のサマリ行

応答の冒頭に、指摘件数を1行で読み取れるサマリ行を置く。親が返答本文を数え直さずに指摘の有無と
規模を確定できるようにするための契約であり、件数の書式は規定しない。

置き方は出力形式の先頭に判定項目があるかで2通りに分かれる。

- 出力形式の先頭に判定項目を持つ reviewer は、その判定項目と同じ行に件数を示す。別のサマリ行を追加しない。
- 判定項目を持たない reviewer は、件数だけを示すサマリ行を冒頭に置く。判定項目を新設しない。

指摘0件でもサマリ行を省略しない。0件であることを表す語は、各 reviewer が既に使っている語をそのまま使う。

## 指摘ごとの evidence

指摘ごとに、その指摘が実在することを親が確かめられる evidence を示す。次の3つのうち、いずれか1つを示せばよい。

- 該当ファイルと行の引用
- 再現手順
- 参照した Data の path と id

3択にしてあるのは、diff を持たない工程の reviewer でも evidence を示せるようにするためである。
プランや Data だけを入力に取る reviewer は、参照した Data の path と id で足りる。

evidence は各 reviewer が既に持つ場所または根拠の項目の中で示す。evidence 専用の項目を新設しない。
