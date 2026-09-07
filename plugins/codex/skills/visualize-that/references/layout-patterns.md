<!-- Generated from shared/. Do not edit directly. -->

# Layout Patterns

この catalog は、reader-facing composition を HTML へ表すときの出発点です。pattern は入力の意味を決める schema ではありません。composition で中心命題、primary structure、supporting detail、関係、不確実性を確定してから、一番自然に表せる pattern を選びます。

| 名前 | ファイル | 出発点となる構成 |
| --- | --- | --- |
| base | `assets/template.html` | title、lede、自由に埋める main 領域だけの最小骨格 |
| flow | `assets/flow.html` | 主経路、局所 cycle、branch、step に属する detail |
| comparison | `assets/comparison.html` | 共通の比較軸を持つ table または matrix |
| layers | `assets/layers.html` | 層、境界、層をまたぐ関係 |
| timeline | `assets/timeline.html` | 時点、節目、変化と対応する説明 |
| relationship | `assets/relationship.html` | node、label 付きの関係、分岐 |
| overview | `assets/overview.html` | 一つの中心命題と、それを補う複数の観点 |
| freeform | `assets/freeform.html` | 特定の関係配置を前提にしない component の組み合わせ |

Primary pattern を一つ選び、必要な場合だけ別 pattern の component を部分利用します。たとえば overview の中心命題の下へ comparison の table を置けます。組み合わせる component は元の pattern root class の内側へ置き、pattern 固有 CSS の scope を維持します。特定の pattern が自然に適合しない場合は base から組むか、freeform の小さな断片を使います。例の node 数、section order、表示文、意味は入力に合わせて変更できます。

各 HTML は local preview のため、隣接する `visual-language.css` を `<link>` で参照しています。最終成果物では次の順に一つの `<style>` へ取り込みます。

1. `visual-language.css` の全内容
2. 利用する pattern HTML の `<style>` にある scoped layout CSS

最終 HTML から asset への `<link>` を外し、外部通信や配布 directory なしでも基本の説明と関係が読めることを確認します。複数 pattern を混ぜる場合も、取り込むのは利用した root class の rule だけで構いません。共通 token や primitive を pattern CSS へ複製しません。

`qualified` と `unverified` は state 名と説明本文を残し、色だけで意味を伝えません。`viz:<kebab-case-slug>` の表示、要素の `id`、内部 link、deep-dive target、元 overview との対応は同じ識別子を維持します。識別子は通常 `viz-id` で控えめに表示し、deep dive の焦点に必要な箇所だけ `viz-id--focus` を加えます。
