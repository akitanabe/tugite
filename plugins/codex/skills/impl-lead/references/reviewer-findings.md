<!-- Generated from shared/. Do not edit directly. -->

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

指摘 Data を返すだけの reviewer には、ファイルを書き換える tool を渡さない。
Claude 向けは agent frontmatter の `disallowed_tools` に `Edit` / `Write` / `NotebookEdit` を置き、
Codex 向けは `sandbox_mode` の `read-only` が同じ役割を果たす。原稿の指示文だけに委ねると、
reviewer が指摘を返す代わりに対象を直してしまう余地が残るためである。

探索手段は責務で分ける。判定に検証の実行や基準 commit 時点のファイル参照が必要な reviewer には
`Bash` を渡し、渡された Data のテキストだけで判定できる reviewer には渡さない。実行できない reviewer が
「実行すれば分かること」を推測で書く状態と、テキストで足りる reviewer に実行手段が余る状態の、
どちらも避けるための分け方である。

どの reviewer がどちらに属するかはこの節に列挙せず、各 agent 定義を正本とする。ここに一覧を置くと、
reviewer を増やすたび原稿と定義の2箇所を揃えることになり、片方だけが古い状態を作るためである。

`Bash` を渡した reviewer について、Claude 側で書き込みを禁じているのは原稿の指示文だけである。
`Bash` からファイルを書けるため `disallowed_tools` は迂回でき、Codex 側の `sandbox_mode` のように
機構としては禁じられない。担保の強さは platform 間で非対称であり、これは `Bash` を渡す判断に伴う
既知の制約として引き受ける。

`Bash` を渡した reviewer は、対象 worktree では読み取りと検証の実行だけを行い、追跡ファイルを変更しない。
ミューテーション注入や検証用の複製のように書き込みを伴う検証は、対象 worktree の外へ複製してそこで行う。
あわせて `commit` / `checkout` / `switch` / `reset` / `stash` / `rebase` / `merge` / `cherry-pick` /
`worktree add` / `worktree remove` / `branch -d` / `push` を行わない。追跡ファイルの編集は親の
`git status --short` 検査で気づけるが、これらは status を汚さずにレビュー対象の snapshot 自体を
差し替えるため、その検査をすり抜けるためである。

この作業範囲は tool metadata では強制できない。`disallowed_tools` は tool 単位の指定であり、
`Bash` で実行する command の中身までは選べないためである。したがってここで定めるのは契約であり、
担保は各 reviewer 原稿の指示文と、親が起動前後で HEAD と `git status --short` を突き合わせる検査になる。
検査の手順は [QA・修正・統合](qa-and-integration.md) の「reviewer 起動前後の worktree 照合」に従う。

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
