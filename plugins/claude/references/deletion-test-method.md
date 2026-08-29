<!-- Generated from shared/. Do not edit directly. -->

# Deletion Test Method

## Identity and trigger

`Deletion Test Method` は、stable verified snapshot 上の concrete deletion candidate が、consumer から渡された obligations / constraints を維持するかを observable evidence により判定する deletion-triggered shared Method である。

normal refinement と final trim のどちらからも利用できるが、concrete deletion を含まない変更には起動しない。
Method は repository 全体の不要性や一般的な単純さを判定せず、candidate として特定された削除の意味だけを扱う。

## Inputs

consumer は次を渡す。

- **stable verified snapshot**: candidate の観測基準となる不変な content identity と検証済み状態。
- **concrete deletion candidate**: 削除する対象と、削除後に残る状態を識別できる bounded な候補。
- **obligations / constraints**: 削除後も維持すべき current responsibility、behavior、interface、compatibility、safety boundary。
- **observable evidence**: obligation の成立・不成立を区別できる source、test、contract、runtime observation、または caller-authorized evidence surface。

input が不足し、削除後の obligation を十分に判定できない場合は、推測で `preserves` にしない。

## Result

Method は次のいずれかを、根拠となる evidence と limitation を区別できる形で返す。

- **`deleting preserves obligations`**: deletion 後も supplied obligations / constraints が成立することを observable evidence で判定できる。
- **`deletion breaks obligations`**: deletion により supplied obligation / constraint が成立しなくなることを observable evidence で判定できる。
- **`indeterminate`**: evidence、snapshot、candidate boundary、または obligation の関係が不足・競合し、安全にどちらとも判定できない。

結果は deletion candidate に対する observation であり、変更の採否ではない。

## Method

1. stable verified snapshot、candidate identity、supplied obligations / constraints、evidence conditions を固定する。
2. candidate が current snapshot で担う obligation と、削除後に残る independent witness を observable evidence 上で照合する。
3. witness が同じ selected set 内で同時に削除される別 candidate、candidate 自身への循環参照、または現在の snapshot と一致しない stale evidence でないことを確認する。
4. supplied obligations / constraints をすべて維持できる場合だけ `deleting preserves obligations` とし、具体的な破壊が観測できる場合は `deletion breaks obligations`、十分に区別できない場合は `indeterminate` とする。

obligation を満たす replacement design を Method 内で発明せず、削除以外の remediation が必要なら caller に返す。

## Multiple deletion safety

複数 candidate はそれぞれを個別に Test し、`deleting preserves obligations` と判定された候補から coherent selected deletion set を構成した後、その集合全体を一つの deletion candidate として同じ stable snapshot 上で再 Test する。

selected set 全体が `deleting preserves obligations` の場合だけ、caller は apply 候補として扱える。`deletion breaks obligations` または
`indeterminate` の場合は、Method が一部を自動採用せず、caller が selected set、obligations、evidence のいずれを見直すかを判断する。
個別判定だけで同時削除の安全性を推論しない。

## Caller ownership

Deletion Test Method は scope admission、finding の採否、replacement design、削除の apply、workflow routing、review continuation / completion を所有せず、consumer が Method result と current responsibility に基づいてこれらを裁定する。

Method は artifact を変更せず、persistent history や固定 ledger schema を作らない。consumer は apply 後の verification と verified snapshot の更新を所有する。

## Non-goals

- concrete deletion を伴わない変更の quality review
- repository または artifact 全体の minimality 判定
- obligation / constraint の自律追加
- deletion candidate の生成、scope 拡張、replacement proposal
- Method result からの自動 accept / reject
- workflow の continuation、completion、status の決定
