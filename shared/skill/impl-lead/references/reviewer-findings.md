# Reviewer findings の共通契約

## 目次

- 位置づけ
- read-only の担保
- 指摘件数のサマリ行
- 指摘ごとの evidence

## 位置づけ

findings を返すすべての reviewer が共通で満たす2点を定義する。正本はこの reference が持ち、
各 reviewer 原稿は同じ2点を自分の出力形式の語彙で本文に書き下す。

対象は `responsibility-boundary-reviewer`、`test-quality-reviewer`、`security-side-effect-reviewer`、
`writing-principles-reviewer`、`over-engineering-reviewer`、`plan-adversarial-reviewer` とする。
指摘 Data を返さない `expert-selection-reviewer` と `review-patch-refactorer` は対象外とする。

判定語彙、0件の表記、判定対象外の範囲の書き方は各 reviewer 原稿を正本とし、この reference では変更しない。

ここで定めた対象は上記2点だけに適用する。「read-only の担保」は対象範囲が異なり、同節が自身の対象を定める。

## read-only の担保

reviewer が read-only であることを原稿の指示文だけに委ねず、platform が強制できる設定として持つ。
Claude 向けは agent frontmatter の `tools` と `disallowed_tools`、Codex 向けは `sandbox_mode` で担保し、
片方の platform にだけ制限が入っている状態を作らない。同じ契約の担保の強さが platform で変わると、
どちらの platform で起動したかによって reviewer が実際に取れる操作が変わってしまうためである。

この節の対象は、上記2点の6本に `expert-selection-reviewer` を加えた reviewer 7本とする。
`expert-selection-reviewer` は指摘 Data を返さないため上記2点の対象外だが、ファイルを変更しない点は
共通であり、この節では対象に含める。指摘された範囲を修正する `review-patch-refactorer` は書き込みを要するため、
この節でも対象外とする。

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
