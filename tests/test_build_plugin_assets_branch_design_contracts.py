"""Repository contracts for branch-design."""

from __future__ import annotations

import unittest

from build_plugin_assets_test_support import (
    GENERATED_MARKDOWN_WARNING,
    RepositoryContractSupport,
    generated_skill_path,
    generated_skill_reference_path,
    shared_skill_path,
    shared_skill_reference_path,
)


BRANCH_DESIGN_SKILL = "branch-design"
PLAN_SCHEMA_REFERENCE = "branch-plan-schema.md"
PLAN_REFERENCE_NAMES = (
    "branch-plan-schema.md",
    "branch-splitting.md",
    "plan-review.md",
)


class PlanImplementationBranchesContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _plan_skill_texts(self) -> dict[str, str]:
        return {
            "source": self._repository_text(shared_skill_path(BRANCH_DESIGN_SKILL)),
            "claude": self._repository_text(
                generated_skill_path("claude", BRANCH_DESIGN_SKILL)
            ),
            "codex": self._repository_text(
                generated_skill_path("codex", BRANCH_DESIGN_SKILL)
            ),
        }

    def _plan_reference_texts(self, name: str) -> dict[str, str]:
        return {
            "source": self._repository_text(
                shared_skill_reference_path(BRANCH_DESIGN_SKILL, name)
            ),
            "claude": self._repository_text(
                generated_skill_reference_path("claude", BRANCH_DESIGN_SKILL, name)
            ),
            "codex": self._repository_text(
                generated_skill_reference_path("codex", BRANCH_DESIGN_SKILL, name)
            ),
        }

    def test_plan_skill_exposes_platform_frontmatter_and_reference_links(
        self,
    ) -> None:
        """Expose planning frontmatter and route each detail to its reference."""
        for platform in ("claude", "codex"):
            main = self._plan_skill_texts()[platform]
            with self.subTest(platform=platform):
                self.assertTrue(main.startswith(f"---\nname: {BRANCH_DESIGN_SKILL}\n"))
                self.assertLess(len(main.splitlines()), 300)
                for name in PLAN_REFERENCE_NAMES:
                    self.assertIn(f"(references/{name})", main)
                self.assertNotIn("<!-- claude-only", main)
                self.assertNotIn("<!-- codex-only", main)

    def test_plan_references_carry_generated_warning_and_table_of_contents(
        self,
    ) -> None:
        """Give each planning reference a warning-free source and a table of contents."""
        for name in PLAN_REFERENCE_NAMES:
            texts = self._plan_reference_texts(name)
            with self.subTest(reference=name):
                self.assertFalse(
                    texts["source"].startswith(GENERATED_MARKDOWN_WARNING)
                )
                self.assertTrue(texts["source"].startswith("# "))
                self.assertIn("## 目次", texts["source"])
                for platform in ("claude", "codex"):
                    reference = texts[platform]
                    self.assertTrue(
                        reference.startswith(f"{GENERATED_MARKDOWN_WARNING}\n\n")
                    )
                    self.assertIn("## 目次", reference)

    def test_plan_schema_reference_holds_the_canonical_schema(self) -> None:
        """Carry the confirmed schema, violation codes, transitions, and tests meaning."""
        required = (
            "status: blocked | awaiting_review | approved",
            "confirmation_mode: review | auto",
            "delegation:",
            "authorized: false",
            "| code | 検査内容 |",
            "duplicate-id",
            "unknown-reference",
            "branch-without-primary-ac",
            "delegation-invalid",
            "mode-proposal-invalid",
            "## 状態遷移と権限",
            "## tests / stage_tests の意味",
        )
        excluded = (
            "## implementation_stages の実行規約",
            "## Executor 側の再検証",
            "## レビュー指摘への対応",
            "## 再レビュー指摘への対応",
            "## issue #46 確定事項からの意図的な変更",
        )
        for platform, text in self._plan_reference_texts(
            "branch-plan-schema.md"
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)
                for section in excluded:
                    self.assertNotIn("".join(section.split()), normalized)

    def test_plan_schema_reference_points_terminology_to_the_implementation_branches_glossary(
        self,
    ) -> None:
        """Route branch terminology to the impl-lead glossary, not a local copy."""
        required = (
            "用語",
            "impl-lead",
            "../../impl-lead/references/implementation-branches.md",
        )
        for platform, text in self._plan_reference_texts(
            "branch-plan-schema.md"
        ).items():
            with self.subTest(platform=platform):
                for contract in required:
                    self.assertIn(contract, text)

    def test_plan_skill_matches_confirmed_schema_contract(self) -> None:
        """Separate approval from delegation and never start delegation from the skill."""
        required = (
            "承認と委譲開始権限は独立",
            "`delegation.authorized` は常に `false`",
            "確認モードの既定は `review`",
            "`auto` はユーザーが明示した場合のみ",
            "`impl-lead` を直接起動しない",
            "blocking な不足は `unresolved_decisions`",
            "minor な不足は `assumptions`",
        )
        for platform, main in self._plan_skill_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(main.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_references_define_branch_responsibility_exclusions(self) -> None:
        """Generate responsibility exclusions separately from physical path limits."""
        reference_contracts = {
            "branch-plan-schema.md": (
                "`allowed_paths` は変更を許可する物理的なファイル範囲",
                "`forbidden_paths` は変更を禁止する物理的なファイル範囲",
                "`out_of_scope` は許可範囲内でもこの枝では担当しない責務・作業",
            ),
            "branch-splitting.md": (
                "同じ `allowed_paths` 内に複数の責務・作業が含まれ",
                "担当しない責務・作業を `out_of_scope` に列挙する",
                "パスで表現できる禁止範囲を `out_of_scope` で代用しない",
            ),
        }

        for reference, contracts in reference_contracts.items():
            for platform, text in self._plan_reference_texts(reference).items():
                with self.subTest(reference=reference, platform=platform):
                    normalized = "".join(text.split())
                    for contract in contracts:
                        self.assertIn("".join(contract.split()), normalized)

    def test_plan_schema_holds_requested_mode_as_policy_and_baseline(self) -> None:
        """Carry the requested delegation mode as an allocation policy and a baseline."""
        required = (
            "[issue #68](https://github.com/akitanabe/tugite/issues/68)",
            "policy: fixed | adaptive",
            "baseline: lite | standard | strict",
            "mode 未指定の明示的な委譲要求は null のまま保持し、"
            "Executor が {adaptive, standard} を採用する。",
            "`{adaptive, lite}` と `{fixed, standard}` は入力語彙が存在しないため無効とし、"
            "表に含めない。",
            "`baseline` を `lite` にすると low risk 枝の割り当て先が `lite` しかなく導出が"
            "恒等写像になり、`medium` 以上を引き上げる用途は `{adaptive, standard}` と"
            "同一になるため、独立した配分方針として意味を持たない。",
            "`{fixed, standard}` は全枝固定を明示する入力語彙が存在しないため到達できない。"
            "仮に語彙を足しても `{adaptive, standard}` は low risk 枝だけを `lite` に落とし"
            "他は `standard` のままなので、品質面で下回らずコストだけが下がり、優位性がない。",
        )
        valid_combinations = (
            "| `false` | `null` | `null` |",
            "| `true` | `user` | `null`(mode 未指定の委譲要求。"
            "Executor が `{adaptive, standard}` を選ぶ) |",
            "| `true` | `user` | `{fixed, lite}` |",
            "| `true` | `user` | `{adaptive, standard}` |",
            "| `true` | `user` | `{adaptive, strict}` |",
            "| `true` | `user` | `{fixed, strict}` |",
        )
        for platform, text in self._plan_reference_texts(
            PLAN_SCHEMA_REFERENCE
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required + valid_combinations:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_schema_derives_branch_mode_from_risk_instead_of_a_field(
        self,
    ) -> None:
        """Keep branch risk as the only source for the derived branch mode."""
        required = (
            "枝ごとの委譲 mode は schema に持たせず、`branches[].risk` を正として導出する。",
            "枝側に `recommended_mode` を置くと `risk` と二重管理になり、矛盾したときに"
            "どちらを正とするか決められないため。",
            "AC 割り当てを枝側の一方向参照へ正規化したのと同じ理由である。",
            "導出した枝 mode は Branch Plan へ書き戻さず、実行 Data として保持して"
            "最終報告で報告する。",
            "mode の判定理由は `risk.reasons` に書き、mode ごとの理由欄を別に設けない。",
        )
        for platform, text in self._plan_reference_texts(
            PLAN_SCHEMA_REFERENCE
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_schema_limits_mode_proposal_to_fixed_policy_mismatch(self) -> None:
        """Propose an adaptive policy only where a fixed policy ignores branch risk."""
        required = (
            "propose:",
            "policy: adaptive",
            "baseline: standard | strict",
            "`policy: adaptive` では枝の `risk.level` から mode を導出するため、"
            "high risk 枝は決定表側で `strict` になる。",
            "提案が必要なのは `policy: fixed` が枝の `risk` と整合しない場合だけである。",
            "`{fixed, strict}` に対して降格を提案しない。",
            "引き上げだけを提案する非対称性は、コストの削減より品質の担保を優先する"
            "判断であり、low risk 枝から `lite` を提案しないのと同じ理由である。",
        )
        proposal_rows = (
            "| `{fixed, lite}` | `high` を含む | `{adaptive, strict}` を提案 |",
            "| `{fixed, lite}` | `medium` を含み `high` なし | "
            "`{adaptive, standard}` を提案 |",
            "| `{fixed, lite}` | 全枝 `low` | 出力しない |",
            "| `{fixed, strict}` | 任意 | 出力しない |",
            "| `{adaptive, *}` または `null` | 任意 | 出力しない |",
        )
        violation_recalculation = (
            "`delegation_mode_proposal` の要否・内容が `requested_mode` と枝の "
            "`risk.level` からの再計算(出力条件表)と一致しない",
            "必要時の欠落、不要時の出力、表と異なる `{policy, baseline}` の提案",
        )
        for platform, text in self._plan_reference_texts(
            PLAN_SCHEMA_REFERENCE
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required + proposal_rows + violation_recalculation:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_splitting_reference_defines_risk_level_criteria(self) -> None:
        """Assign risk levels from failure impact rather than from change size."""
        required = (
            "## risk.level の判定観点",
            "これは枝 mode を決める関数ではなく、`risk.level` の付け方を揃える"
            "チェックリストである。",
            "判定は実装量やファイル数ではなく、失敗したときの影響を中心に行う。",
            "1. 失敗時の影響範囲",
            "2. 変更の可逆性 / 切り戻しの容易さ",
            "3. 外部副作用の有無と数",
            "4. セキュリティ・権限への影響",
            "5. データ整合性への影響",
            "6. 後方互換性への影響",
            "7. 仕様の明確さ",
            "8. テストによる担保の可能性",
            "9. 他の枝との依存関係",
            "変更量が1行でも、権限判定やデータ削除条件に関わる場合は `high` とする。",
            "判定に使った観点は `risk.reasons` に記録する。",
            "決定表をここに再掲しない。",
        )
        level_rows = (
            "| `low` | 表示文言のみの変更、設定値の追加、振る舞いに影響しないリネーム、"
            "局所的な機械的修正。外部副作用がなく、容易に切り戻せる。 |",
            "| `medium` | 通常の機能追加、既存ロジックの変更、API 内部処理の変更、"
            "UI とバックエンドの通常連携。テストで十分に担保でき、失敗時の影響が限定的。 |",
            "| `high` | 認証・認可・権限判定、データ削除・上書き・移行、"
            "外部 API の契約変更、後方互換性への影響、決済・請求・金額計算、"
            "機密情報への影響、複数の外部 I/O。失敗時の影響が広い、切り戻しが困難、"
            "または仕様の曖昧さが重大な不具合につながる。 |",
        )
        for platform, text in self._plan_reference_texts("branch-splitting.md").items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required + level_rows:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_skill_takes_inventory_findings_only_for_user_listed_ids(
        self,
    ) -> None:
        """Accept inventory findings as a source plan only for explicitly listed finding IDs."""
        required = (
            "元プラン(path / issue URL / 会話内 / `test-audit` の "
            "Test Inventory 報告の findings)",
            "findings 由来の AC では、原文はユーザーが確定した文言を指す。",
            "対象 findings の ID(`G-*`)をユーザーが明示的に指定する。"
            "全 findings の自動採用はしない。",
            "対象 ID の指定がないまま findings 全体を渡された場合は、"
            "自動採用せず対象 ID の明示指定を求める。",
            "導出は `suggestion` を受け入れ条件の形に整えることに限る。",
            "findings にない対象・範囲・実装方針を足さない。",
        )
        for platform, main in self._plan_skill_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(main.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_schema_traces_findings_through_derived_from_on_criteria(
        self,
    ) -> None:
        """Trace an inventory finding to its branch through one-way references only."""
        required = (
            "path / issue URL / 「会話内」/ 「Test Inventory 報告」",
            "derived_from: []",
            "findings 由来のときだけ元の finding ID(`G-*`)を列挙する",
            "空なら元プラン由来",
            "実装枝 → `covers_acceptance_criteria` → AC → `derived_from` の一方向参照",
            "実装枝側に finding ID を持たせない",
            "`derived_from` は blocking violation code の検査対象にしない",
            "Branch Plan 内では参照先の存在を解決できない",
            "承認可否の判定が実際には検査していない事実を根拠に持つ",
        )
        for platform, text in self._plan_reference_texts(
            PLAN_SCHEMA_REFERENCE
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_schema_blocks_on_unconfirmed_findings_derived_criteria(
        self,
    ) -> None:
        """Hold an unconfirmed derived wording as its own unresolved decision kind."""
        required = (
            "kind: ac-derivation",
            "findings から導出した AC の文言が未確定であることを表す",
            "`unresolved_decisions.affects` の `branch` / `ac-assignment` / "
            "`ac-derivation`",
        )
        for platform, text in self._plan_reference_texts(
            PLAN_SCHEMA_REFERENCE
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_review_confirms_findings_derived_criteria_before_approval(
        self,
    ) -> None:
        """Pair each finding with its draft criterion and confirm the wording before approval."""
        required = (
            "## findings 由来 AC の確定",
            "対象 `G-*` ごとに、`summary` / `evidence` / `suggestion` の原文と、"
            "そこから導出した AC 案を対で提示する。",
            "AC の `text` にはユーザーが確定した文言だけを入れる。",
            "`kind: ac-derivation` の `affects` を置き、`status: blocked` のまま"
            "承認操作を求めない。",
            "文言が確定したら AC の `text` を確定文言に置き換え、対応する "
            "`unresolved_decisions` を取り除く。",
            "`suggestion` にない対象・範囲・実装方針を足す必要が生じた場合は、"
            "導出せず `unresolved_decisions` の `question` としてユーザーへ確定を求める。",
        )
        for platform, text in self._plan_reference_texts("plan-review.md").items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_review_applies_checkability_guidance_to_ac_wording_only(
        self,
    ) -> None:
        """Scope drafting's checkability guidance to wording, routing scope growth elsewhere."""
        for platform, text in self._plan_reference_texts("plan-review.md").items():
            with self.subTest(platform=platform):
                self.assertIn(
                    "[起草手順](../../plan-craft/references/plan-drafting.md)",
                    text,
                )
                normalized = "".join(text.split())
                required = (
                    "の「AC の書き方」が定める判定可能性の指針を適用する。",
                    "適用範囲は AC 案の文言整形までに限り、`suggestion` にない対象・範囲を"
                    "新たに足す判断には使わない。",
                    "対象・範囲を足す必要が生じた場合は、下記のとおり `unresolved_decisions` へ"
                    "回す。",
                )
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)


if __name__ == "__main__":
    unittest.main()
