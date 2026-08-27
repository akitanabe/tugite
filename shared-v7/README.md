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
gunte emit --target shared-v7-contracts
gunte lock
gunte check --target shared-v7-contracts
gunte emit
gunte check
bash tests/shared-v7-contracts-test.sh
git diff --check
```

`shared-v7/` が construction document の正本です。`shared-v7-contracts` target は Issue #306 の対象4文書だけを ignored な
`.local/gunte/shared-v7-contracts/documents/` へ投影します。この projection は検証用の再生成可能な artifact であり、編集や commit の対象にしません。fresh checkout または対象4文書の変更後は、target/full check より先に emit します。

Gunte Green が保護するのは、指定した document identity、relation、order、stop condition、および byte drift です。runtime behavior、artifact の代表性、LLM の判断品質、文書全体の読みやすさは保証しません。

`shared-v7/` は current canonical plugin generation surface として登録しません。v7 candidate の完成と検証後に canonical `shared/` へ切り替え、この construction surface は完成 architecture に migration concept として残しません。
