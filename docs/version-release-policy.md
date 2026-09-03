# Version / release policy

この文書は Tugite v6.0.0 以降の version と release snapshot の恒久正本である。v5 系には遡及適用しない。
v6 migration 固有の baseline、初回 release の判断、checklist は Issue #241 が保持し、この文書へ複製しない。

## 通常の change と release Action

version は個々の change ではなく release snapshot の属性である。通常の change、Pull Request、main への統合では
`shared/VERSION` とその他の version-bearing field を更新しない。Human が release を明示した場合だけ release Action を開始する。

ordinary-change guard は次の `deterministic-contract-only` rule とする。

```toml
policy_id = "version-release-policy-v1"
classification = "deterministic-contract-only"
owner_action = "parent QA checks the guard before a version edit and before ordinary-change acceptance"
inputs = ["Human release authorization", "task diff", "current shared/VERSION", "candidate state"]
calculation = "without explicit Human release authorization, reject changes to version-bearing fields"
interception_points = ["before version edit", "before final ordinary-change acceptance"]
current_assurance = ["this natural-language policy", "bounded Gunte contract for generated guidance"]
non_mechanization_reason = "the repository has no central release workflow or interceptor, and adding one is outside this policy change"
natural_language_source = "docs/version-release-policy.md"
```

Gunte contract が保証するのは policy identity、required Data、generated guidance の pointer と関係の整合までである。
この文書の意味遵守、release の runtime 実行、bump の自律判断を保証したとは扱わない。

## Snapshot と bump の判断

release の入力は、first-parent の main 上で識別した直前の canonical release commit/tree と、Human が固定した clean かつ
immutable な candidate commit/tree の間の累積差分だけとする。worktree や未固定の branch tip は分類対象にしない。

直前の canonical release snapshot は、その version を初めて導入した全 gate 後の同期済み tree と、その tree が main へ
統合された commit から解決する。partial failure 中の commit や同じ release の follow-up commit は release snapshot とみなさない。
候補が複数ある、欠落している、または tree identity を確認できない場合は推測せず停止する。

bump は累積差分を明示入力にした Calculation として判断する。

- public skill / agent の名前、起動方法、外部 API、保存 artifact の形式、CLI の互換性を壊す変更は major candidate とする。
- compatible な skill / agent / contract の追加や内部契約変更は minor candidate とする。
- 契約の意味を変えない model / effort などの調整は patch candidate とする。
- 複数の影響がある場合は最も大きい candidate を採用する。
- patch / minor は Agent が確定できる。major candidate は Agent が検出し、親が major / minor を最終裁定する。
- 親が major を却下した場合は minor を許可する。

この分類は strict SemVer 準拠を新たに主張せず、breaking change の外部向け release note 義務も設けない。

## Release-only 編集境界

version 編集前に、手編集する各 field または bounded span について次の Data を固定する。

- 対象 path
- candidate 上の旧 bytes
- bump 判断から得た期待する新 bytes
- その入力から Gunte が導出する生成 target

path 単位の allowlist は使わない。同じ file に別の contract や本文が同居していても、固定した field / span 外の変更を
release-only 差分として許可しない。生成物と lock は固定した source 入力から再生成された bytes だけを許可する。

version 編集前と最終受け入れ前に、candidate identity と release-only 差分を再照合する。drift、曖昧な previous snapshot、
固定した field / span 外の変更があれば旧分類を再利用せず停止する。Human が新しい candidate を固定した後に再分類する。

## Version surface inventory

release Action は bounded な repository inventory と readback により、少なくとも次の surface を同期する。

- 正本: `shared/VERSION`
- 手編集する contract: `contracts/shared.toml` の README title contract
- Gunte 生成物: root `README.md`、Claude / Codex / Cursor plugin manifest、`plugins/codex/install/VERSION`、
  `shared/plugins-readme.md` から生成する `plugins/cursor/README.md`
- Gunte 管理外: `plugins/claude/README.md` と `plugins/codex/README.md` の version 表示

declaration manifest の template version scalar は project version metadata で上書きされるため、現行の Gunte 設計では
release version の独立正本にしない。管理外 README の表示は release 差分で同期するか、重複表示を恒久的に削除し、
表示を残したまま stale にしない。将来追加された surface も inventory と bounded readback で検出する。

## Release Action と完了条件

release Action は次の順で進める。

1. Human の明示 release 指示を観測する。
2. 親 QA が previous release と immutable candidate の commit/tree identity を固定する。
3. Agent が累積差分から bump candidate を計算し、major candidate の場合だけ親が major / minor を裁定する。
4. release-only field / span、旧 bytes、期待する新 bytes、生成 target を固定し、candidate identity を再照合する。
5. 正本を更新し、`gunte emit`、`gunte lock`、target/full `gunte check`、installer tests、`git diff --check` の順で検証する。
6. final tree、release-only 差分、main integration tree の identity を再照合する。

全 gate 後の最終同期 tree が対象 version を導入する canonical release tree となる。main へ統合された tree がこれと一致した場合だけ
release 完了とする。一致しない場合は release 完了とせず、新しい candidate を Human が固定して再分類する。
