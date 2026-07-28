"""Repository contracts for test-audit reporting."""

from __future__ import annotations

import unittest

from build_plugin_assets_test_support import (
    RepositoryContractSupport,
    generated_skill_reference_path,
    shared_skill_reference_path,
)


TEST_AUDIT_SKILL = "test-audit"
INVENTORY_REPORT_REFERENCE = "inventory-report.md"


class InventoryTestSuiteReportContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _inventory_report_texts(self) -> dict[str, str]:
        return {
            "source": self._repository_text(
                shared_skill_reference_path(
                    TEST_AUDIT_SKILL, INVENTORY_REPORT_REFERENCE
                )
            ),
            "claude": self._repository_text(
                generated_skill_reference_path(
                    "claude", TEST_AUDIT_SKILL, INVENTORY_REPORT_REFERENCE
                )
            ),
            "codex": self._repository_text(
                generated_skill_reference_path(
                    "codex", TEST_AUDIT_SKILL, INVENTORY_REPORT_REFERENCE
                )
            ),
        }

    def test_inventory_report_offers_end_or_plan_operations_like_plan_review(
        self,
    ) -> None:
        """Offer plan-review's bulleted-operations-then-permission-boundary shape."""
        required = (
            "## 確認操作",
            "報告のみで終了",
            "既定。この操作を選んだ場合、この Skill は何も起こさない。",
            "指摘の解消を計画",
            "対象の gap 指摘 `G-*` をユーザーが指定し、`branch-design` へ",
            "渡して実装枝計画へ進める。",
            "`branch-design` へ渡すのは親エージェントの責務であり、この Skill は",
            "`branch-design` を直接起動しない。",
        )
        for platform, text in self._inventory_report_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_inventory_report_withholds_plan_operation_without_scanned_gaps(
        self,
    ) -> None:
        """Withhold the plan-resolution operation once no gap finding exists to target."""
        required = (
            "gap 指摘が `該当なし` の場合は提示しない",
            "指定できる解消対象がないためである。",
        )
        for platform, text in self._inventory_report_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_inventory_report_presentation_order_governs_confirmation_visibility(
        self,
    ) -> None:
        """Let `## 提示の順序` alone decide confirmation visibility and position per status."""
        required = (
            "→ 確認操作の",
            "最後に確認操作を",
            "確認操作も提示しない",
        )
        for platform, text in self._inventory_report_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_inventory_report_table_of_contents_lists_confirmation_operations(
        self,
    ) -> None:
        """Register the confirmation-operations section in the table of contents."""
        toc_heading = "## 目次"
        for platform, text in self._inventory_report_texts().items():
            with self.subTest(platform=platform):
                self.assertIn(toc_heading, text)
                toc_section = text.split(toc_heading, 1)[1].split("##", 1)[0]
                self.assertIn("確認操作", toc_section)


if __name__ == "__main__":
    unittest.main()
