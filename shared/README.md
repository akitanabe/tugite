# Tugite v7 Canonical Construction Surface

`shared/` は、Tugite v7 をゼロベースで再構成する canonical construction surface です。

既存 v6 の source は `shared-v6/` に一時隔離しています。v7 の artifact は、current architecture の責務と boundary から必要なものだけを `shared/` へ selective rebuild します。

v6 source の clone-and-prune や、将来の artifact を空の placeholder として先に追加することは、この surface の構築方法ではありません。

## Verification boundary

v7 artifact を追加・変更したときは、その artifact に適用できる既存の lint、test、installer、または repository verification を実行します。

Phase 0 で確認する repository-native な経路は次のとおりです。

```bash
npm run test:lint
bash tests/install-agents-test.sh
bash tests/install-cursor-plugin-test.sh
git diff --check
```

既存 v6 の生成物と生成経路は v7 の source of truth ではありません。v7 artifact が既存 infrastructure category を利用する場合は、利用する integration boundary をその時点で確認します。
