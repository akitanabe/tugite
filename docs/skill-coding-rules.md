# Skill Coding Rules

Skill の新規作業では、過去の失敗や旧構造を防御する規範を蓄積するのではなく、
現在の仕様、責務、構造から必要な意味を直接記述する。

## Scope

この規範は、新規作業として作成・変更する Skill、shared component、
contract、test、lint rule に適用する。

changelog、ADR、migration note、work log など、
履歴の保存自体を目的とする文書は対象外とする。
ただし、現在の artifact は、それらの履歴を読まなくても理解できなければならない。

## 1. Current State Only

完了した artifact は、現在の仕様、責務、構造だけで理解できる状態にする。

- 旧名称、旧構造、削除履歴、過去の誤りを、現在の仕様を理解するための前提として残さない。
- 「以前はこうだった」「旧版ではこうだった」を、現在の構造や責務の説明理由にしない。
- 過去への防御ではなく、現在必要な意味と責務を直接記述する。

旧名称、旧形式、legacy behavior であっても、現在サポートされているものは current state として記述する。
deprecated であることと、deleted であることを混同しない。

## 2. Positive Specification

contract、test、lint rule は、原則として「何が存在してはいけないか」ではなく、
「現在何が成立しなければならないか」を記述する。

避ける:

```text
旧構造 X を禁止する
```

優先する:

```text
現在の責務は Y が所有する
```

Negative test や禁止形式そのものを禁止しない。

現在の安全性、構文、責務、accepted / rejected boundary を直接表す
negative constraint は、Positive Specification に含まれる。

避けるのは、過去の失敗、削除履歴、旧名称だけを根拠とする historical defense である。

過去の失敗から得られた知見が必要な場合は、個別の禁止事項として残すのではなく、
現在の invariant、responsibility、boundary に一般化して表現する。

```text
複数の失敗
    ↓
共通する現在の意味を抽出
    ↓
現在の invariant / responsibility / boundary として記述
```

レビュー時は、次を確認する。

> その rule の必要性を、削除履歴を知らない読者に対して、
> 現在の invariant、responsibility、boundary だけで説明できるか。

説明できない場合、その rule は historical defense である可能性が高い。

## 3. No Deletion-Only Guards

削除された要素が存在しないことだけを保証する恒久的な test、contract、lint rule は追加しない。

対象には次を含む。

- 旧 field 名が存在しないことだけを確認する test
- 廃止済み文言を禁止する contract
- 過去の構造へ戻らないことだけを目的とする lint rule
- 削除済みファイル、名称、section の不存在チェック

削除確認が必要な場合は、変更作業中の temporary verification として実施し、
作業完了時には deletion-only guard を残さない。

```text
変更中
  → 削除対象が残っていないことを確認
  → 現在仕様が成立していることを確認
  → deletion-only verification は除去
```

temporary verification は、一時的な test、検索、確認コマンドとして実施できる。
作業記録として確認結果を残すことは妨げないが、
それを恒久的な test、contract、lint rule として維持しない。

## Summary

Skill 作成時は次の3原則を優先する。

1. **Current State Only** — 現在の仕様・責務・構造だけで理解可能にする。
2. **Positive Specification** — 過去の禁止事項ではなく、現在成立すべき invariant、responsibility、boundary を直接規定する。
3. **No Deletion-Only Guards** — 削除済み要素の不存在だけを保証する恒久的な guard を残さない。
