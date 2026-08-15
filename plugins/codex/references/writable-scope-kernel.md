<!-- Generated from shared/. Do not edit directly. -->

# Writable Scope Kernel v1

Kernel identity: `writable-scope-kernel-v1`.
Kernel dependencies: `none`.

この共有規範は、親が現在の execution に明示した filesystem 領域集合を、Worker の write boundary として扱うための最小規範である。
これは Work Unit の意味や platform の実装方法を追加せず、親の execution data と Worker handoff の関係だけを定める。

## Scope assignment model

```text
assigned_writable_scopes = explicit filesystem region set
write_eligibility = target belongs to one assigned region
assignment_owner = parent execution data
scope_change_owner = parent via explicit handoff update
unassigned_user_owned_resource = write-ineligible
```

`assigned_writable_scopes` は、親が現在の execution に明示的に割り当てた filesystem 領域の集合である。Worker が write target に
できるのは、親がその target をこの集合のいずれかに含むと判定した場合だけである。集合は単一の repository/worktree に限定せず、
repository root 外の run-owned worktree を含められる。user-owned resource は、現在の execution への明示 assignment がない限り
write target ではない。

この所属関係は親の execution data として確定し、Worker の推測や現在の checkout の見た目から導かない。scope の集合、対象の
所有権、assignment の有効性が不明または矛盾する場合、Worker は write Action を開始せず親へ返す。

## Parent loader and assignment

親は最初の write-capable Worker handoff より前に、この Kernel reference を読み、identity、dependencies、必要 section を検証する。
load または検証に失敗した場合は `stop-incomplete` とする。親は選択済み isolation と明示された追加領域から
`assigned_writable_scopes` を確定し、検証済み Kernel 本文と assignment を既存の execution constraint / 周辺 context に注入する。
Worker に path 解決や assignment の確定を委ねない。

## Worker write boundary

4 つの Worker role は、検証済み Kernel identity / 必要本文と `assigned_writable_scopes` を親から受け取った場合にだけ write-capable
input となる。missing、invalid、unknown な assignment は no-write のまま親へ返す。Worker は target の path を自分で解決せず、
scope を推測せず、暗黙に拡張しない。

assignment 内の target に対する通常の変更だけを実行し、assignment 外の target や明示 assignment のない user-owned resource は
編集しない。必要な追加領域は親へ返し、親が execution data を更新して新しい handoff で明示するまで write-capable として扱わない。

## Scope changes and non-goals

scope change は Worker の判断ではなく、親の execution data と明示的な handoff update で扱う。Work Unit Data に writable scope を
追加しない。この Kernel は enforcement mechanism、path layout、platform 設定を定義しない。また、一般的な監査記録を強制機構として
導入せず、親の assignment と handoff を canonical boundary とする。
