# v7 Construction Surface

`shared-v7/` は、current v6 canonical source である `shared/` と分離して、Tugite v7 を selective rebuild するための temporary construction surface です。

v6 の `shared/` を clone-and-prune せず、v7 architecture から必要な responsibility を導出し、必要な artifact だけをここへ追加します。

## Verification

v7 の `SKILL.md` または Programmatic Flow を含む Skill-local reference を追加・変更した場合は、対象 path を明示して既存の `lint:skills` を実行します。

```bash
npm ci
npm run lint:skills -- <v7-skill-path>/SKILL.md
npm run lint:skills -- <v7-skill-path>/references/<file>.md
```

current v6 canonical と repository の回帰確認には、次を使用します。

```bash
gunte check
git diff --check
```

`shared-v7/` は current canonical plugin generation surface として登録しません。v7 candidate の完成と検証後に canonical `shared/` へ切り替え、この construction surface は完成 architecture に migration concept として残しません。
