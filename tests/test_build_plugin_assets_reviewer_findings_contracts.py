"""Repository contracts for reviewer findings."""

from __future__ import annotations

from pathlib import Path
import unittest

from build_plugin_assets_test_support import (
    CLAUDE_PROFILE_PATH,
    CODEX_PROFILE_PATH,
    IMPL_LEAD_SKILL,
    GENERATED_MARKDOWN_WARNING,
    GENERATED_SKILL_PATHS,
    REPOSITORY_ROOT,
    RepositoryContractSupport,
    SHARED_SKILL_PATH,
    generated_skill_reference_path,
    shared_skill_reference_path,
)


REVIEWER_FINDINGS_REFERENCE = "reviewer-findings.md"
FINDINGS_REVIEWER_NAMES = (
    "responsibility-boundary-reviewer",
    "test-quality-reviewer",
    "security-side-effect-reviewer",
    "writing-principles-reviewer",
    "over-engineering-reviewer",
    "plan-adversarial-reviewer",
)
FINDINGS_COUNT_REQUIREMENT = "指摘件数は0件でも必ず"
FINDINGS_EVIDENCE_REQUIREMENT = (
    "evidence（該当ファイルと行の引用 / 再現手順 / 参照した Data の path と id の"
    "いずれか）を示す"
)
VERDICT_LEADING_REVIEWER_SUMMARY_ITEMS = {
    "responsibility-boundary-reviewer": (
        "1. 全体判定と指摘件数（判定は指摘のうち最も重い判定に合わせる。指摘がなければ "
        "`問題なし`。指摘件数は0件でも必ず示す。別のサマリ行は追加しない）"
    ),
    "test-quality-reviewer": (
        "1. 判定と指摘件数（`Pass` / `Needs attention` / `Blocker`。"
        "指摘件数は0件でも必ず示す。別のサマリ行は追加しない）"
    ),
    "security-side-effect-reviewer": (
        "1. 判定と指摘件数（`Pass` / `Needs attention` / `Blocker`。"
        "指摘件数は0件でも必ず示す。別のサマリ行は追加しない）"
    ),
}
COUNT_ONLY_REVIEWER_SUMMARY_LINE = (
    "応答の冒頭に指摘件数のサマリ行を置いてください。指摘件数は0件でも必ず示します。"
    "判定項目は新設しません。"
)
COUNT_ONLY_REVIEWER_NAMES = (
    "writing-principles-reviewer",
    "over-engineering-reviewer",
    "plan-adversarial-reviewer",
)


class ReviewerFindingsContractTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _reviewer_findings_reference_texts(self) -> dict[str, str]:
        paths = {
            "source": shared_skill_reference_path(
                IMPL_LEAD_SKILL, REVIEWER_FINDINGS_REFERENCE
            ),
            "claude": generated_skill_reference_path(
                "claude", IMPL_LEAD_SKILL, REVIEWER_FINDINGS_REFERENCE
            ),
            "codex": generated_skill_reference_path(
                "codex", IMPL_LEAD_SKILL, REVIEWER_FINDINGS_REFERENCE
            ),
        }
        for path in paths.values():
            self.assertTrue(
                (REPOSITORY_ROOT / path).is_file(),
                f"missing reviewer findings reference: {path}",
            )
        return {key: self._repository_text(path) for key, path in paths.items()}

    def _findings_reviewer_texts(self, name: str) -> dict[str, str]:
        """Read one reviewer manuscript and both distributed agent artifacts."""
        return {
            "shared": self._repository_text(Path("shared/agents") / f"{name}.md"),
            "claude": self._repository_text(CLAUDE_PROFILE_PATH / f"{name}.md"),
            "codex": self._repository_text(CODEX_PROFILE_PATH / f"{name}.toml"),
        }

    def test_reviewer_findings_reference_is_distributed_with_warning_and_toc(
        self,
    ) -> None:
        """Distribute the findings contract to both platforms from a warning-free source."""
        texts = self._reviewer_findings_reference_texts()
        self.assertTrue(texts["source"].startswith("# "))
        self.assertFalse(texts["source"].startswith(GENERATED_MARKDOWN_WARNING))
        self.assertIn("## 目次", texts["source"])
        for platform in ("claude", "codex"):
            with self.subTest(platform=platform):
                self.assertTrue(
                    texts[platform].startswith(f"{GENERATED_MARKDOWN_WARNING}\n\n")
                )
                self.assertIn("## 目次", texts[platform])
        self.assertEqual(texts["claude"], texts["codex"])

    def test_reviewer_findings_reference_defines_summary_line_and_evidence(
        self,
    ) -> None:
        """Hold the canonical two-point findings contract and defer wording to each reviewer."""
        required = (
            "## 指摘件数のサマリ行",
            "応答の冒頭に、指摘件数を1行で読み取れるサマリ行を置く。",
            "出力形式の先頭に判定項目を持つ reviewer は、その判定項目と同じ行に件数を示す。",
            "判定項目を持たない reviewer は、件数だけを示すサマリ行を冒頭に置く。",
            "指摘0件でもサマリ行を省略しない。",
            "0件であることを表す語は、各 reviewer が既に使っている語をそのまま使う。",
            "## 指摘ごとの evidence",
            "該当ファイルと行の引用",
            "再現手順",
            "参照した Data の path と id",
            "いずれか1つを示せばよい。",
            "evidence 専用の項目を新設しない。",
            "判定語彙、0件の表記、判定対象外の範囲の書き方は各 reviewer 原稿を正本とし、"
            "この reference では変更しない。",
        )
        for platform, text in self._reviewer_findings_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_delegate_skill_links_to_the_reviewer_findings_reference(self) -> None:
        """Reach the findings contract from the QA phase of the delegation workflow."""
        main_texts = {
            SHARED_SKILL_PATH: self._repository_text(SHARED_SKILL_PATH),
            GENERATED_SKILL_PATHS["claude"]: self._repository_text(
                GENERATED_SKILL_PATHS["claude"]
            ),
            GENERATED_SKILL_PATHS["codex"]: self._repository_text(
                GENERATED_SKILL_PATHS["codex"]
            ),
        }
        for path, main in main_texts.items():
            with self.subTest(path=path):
                self.assertIn(f"(references/{REVIEWER_FINDINGS_REFERENCE})", main)
                self.assertLess(
                    main.index("(references/qa-and-integration.md)"),
                    main.index(f"(references/{REVIEWER_FINDINGS_REFERENCE})"),
                )

    def test_findings_reviewers_require_a_count_summary_and_evidence(self) -> None:
        """Require the shared two points from every reviewer that returns findings."""
        for name in FINDINGS_REVIEWER_NAMES:
            for platform, text in self._findings_reviewer_texts(name).items():
                with self.subTest(name=name, platform=platform):
                    normalized = "".join(text.split())
                    self.assertIn(
                        "".join(FINDINGS_COUNT_REQUIREMENT.split()), normalized
                    )
                    self.assertIn(
                        "".join(FINDINGS_EVIDENCE_REQUIREMENT.split()), normalized
                    )

    def test_verdict_leading_reviewers_carry_the_count_in_their_verdict_item(
        self,
    ) -> None:
        """Add the count to the leading verdict item instead of a separate summary line."""
        preserved_zero_finding_words = {
            "responsibility-boundary-reviewer": "`問題なし`",
            "test-quality-reviewer": "指摘がない場合は `Pass` としてください",
            "security-side-effect-reviewer": "指摘がない場合は `Pass` とし",
        }
        for name, summary_item in VERDICT_LEADING_REVIEWER_SUMMARY_ITEMS.items():
            for platform, text in self._findings_reviewer_texts(name).items():
                with self.subTest(name=name, platform=platform):
                    normalized = "".join(text.split())
                    self.assertIn("".join(summary_item.split()), normalized)
                    self.assertNotIn(
                        "".join(COUNT_ONLY_REVIEWER_SUMMARY_LINE.split()),
                        normalized,
                    )
                    self.assertIn(
                        "".join(preserved_zero_finding_words[name].split()),
                        normalized,
                    )

    def test_count_only_reviewers_add_a_summary_line_without_a_verdict_item(
        self,
    ) -> None:
        """Add a count-only summary line and keep the existing zero-finding wording."""
        for name in COUNT_ONLY_REVIEWER_NAMES:
            for platform, text in self._findings_reviewer_texts(name).items():
                with self.subTest(name=name, platform=platform):
                    normalized = "".join(text.split())
                    self.assertIn(
                        "".join(COUNT_ONLY_REVIEWER_SUMMARY_LINE.split()), normalized
                    )
                    self.assertIn("指摘0件", normalized)
                    for summary_item in VERDICT_LEADING_REVIEWER_SUMMARY_ITEMS.values():
                        self.assertNotIn(
                            "".join(summary_item.split()), normalized
                        )


if __name__ == "__main__":
    unittest.main()
