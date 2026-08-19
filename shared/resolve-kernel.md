<!-- @contract resolve-kernel-v1 -->
# Resolve Kernel v1

Kernel identity: `resolve-kernel-v1`.
Kernel dependencies: `none`.

## 適用範囲

この Kernel の適用可能性は caller 名ではなく、現在すでに表面化している material な resolution point を解決できることで決める。caller 固有 mapping は各 caller Skill が所有し、この Kernel は caller role mapping を複製しない。
共通 `resolve` Skill の新設は対象外である。

## 規範の責務

`resolve-kernel` は workflow や orchestration ではなく、現在すでに表面化している material な
resolution point を解決するための resolution discipline である。Kernel は evidence source、固定 round 数、または
workflow の完了判定を所有せず、新しい workflow-level status、ledger schema、public parameter を所有・導入しない。呼び出し側は既存の責務と返却形式へ
この規範を mapping し、Kernel がその mapping を推測してはならない。

## Caller boundary と role

caller は invocation boundary、execution bound、completion、返却語彙を所有する。caller が渡す current verified
snapshot と必要な evidence が、この規範の入力である。不足、矛盾、読み取り失敗、または authority の不在を推測で
埋めず、caller-owned boundary へ返す。

一つの resolution point には次の role を区別する。

- caller: resolution の境界、bound、返却、最終的な workflow 判断を持つ。
- resolver: 現在の point を判断し、許可された resolution を提案・適用する。
- counterpart: resolution の対象に関する対話相手または判断主体である。
- authority: counterpart の判断が binding か、caller が裁定できるかを定める caller-owned の権限である。

resolver は counterpart の binding な判断を覆さず、caller の権限や完了判定を代行しない。Kernel は role の
具体的な名前、ledger、status、public parameter を追加しない。

## Current verified snapshot、working state、frontier

`current verified snapshot` は、最後に verify が成功して意味のある semantic progress を確認した状態である。
`working state` は一つの point に対する apply の途中状態であり、verify 前の working state を次の判断の基準に
してはならない。

`frontier` は current verified snapshot から観測できる、未解決で material な resolution point の集合である。
frontier の点は一時的な作業順ではなく、updated snapshot から再計算する。latent な issue を新たに探索して
frontier へ追加しない。探索や潜在論点の発見は caller が所有する別の責務である。

## Atomic resolution unit

resolution point は原則 atomic one-at-a-time で扱う。dependency-first の順序を考慮するが、判断 queue を最初に固定しない。
resolver は current verified snapshot の current frontier を見て、依存関係と authority に基づき、
その時点の一件だけを選択する。

各 point は次の一つの cycle で処理する。

`resolve → apply → verify → semantic progress observation → frontier re-evaluation`

- `resolve`: current verified snapshot から一件の point と、その resolution の根拠・authority を確定する。
- `apply`: 確定した一件だけを working state へ反映する。複数 point の判断を一括反映しない。
- `verify`: 反映結果が対象の obligation と外部から観測できる条件を満たすことを確認する。
- `semantic progress observation`: 前回の current verified snapshot と比較し、意味のある前進があったかを確認する。
- `frontier re-evaluation`: semantic progress を確認した updated snapshot から、残りの frontier と次の順序を再評価する。

verify failure reopen の場合、working state を verified snapshot として採用せず、current point を reopen する。
失敗した point の上に次の判断を積まず、caller-owned の retry または返却境界へ戻す。

## Exit と停止

一つの point は、resolution が apply と verify を通り意味のある progress として観測されたときだけ `resolved` と
して閉じる。caller が所有する authority、scope、evidence、または execution boundary により安全な継続ができない
場合だけ、point を消去せず caller-owned `separated` exit として分離する。`resolved` と `separated` はこの規範の
概念上の exit であり、新しい workflow-level status や ledger field ではない。

同じ snapshot、frontier、または意味のない変更を繰り返す no-progress cycle は進展とみなさず、no-progress-cycle stop
へ移る。同型の cycle を継続して latent な探索へ拡張してはならない。残る material な point と停止理由は caller の
既存の incomplete / unresolved 返却経路へ渡す。

execution の bound は caller-owned bound とする。Kernel は bound の数値や固定 round 数を持たず、bound 到達時に
残る frontier を暗黙に削除しない。frontier が空であることは frontier empty is not workflow completion であり、
workflow の完了、direction freeze、candidate の受入を意味しない。caller が既存の完了判定を行う。

## Kernel non-dependency

この Kernel は単独で適用でき、別の Kernel の存在、identity、本文、適用順、結果を成立条件にしない。複数の Kernel
を併用する場合も、それぞれの caller が独立して読み込み、mapping、authority、返却を所有する。Kernel 間の依存を
この規範へ追加せず、必要な結線は別の設計として扱う。
<!-- @/contract -->
