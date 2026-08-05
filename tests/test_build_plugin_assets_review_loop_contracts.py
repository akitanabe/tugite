"""Deterministic repository contracts for the v5 review-loop skill."""

from __future__ import annotations

from pathlib import Path
import unittest

from build_plugin_assets_test_support import (
    GENERATED_MARKDOWN_WARNING,
    REPOSITORY_ROOT,
    generated_skill_path,
    shared_skill_path,
)


REVIEW_LOOP_SKILL = "review-loop"
REVIEW_LOOP_CODEX_METADATA = Path(
    "plugins/codex/skills/review-loop/agents/openai.yaml"
)
REVIEW_LOOP_EXPECTED_PATHS = (
    Path("shared/skill/review-loop/SKILL.md"),
    Path("plugins/claude/skills/review-loop/SKILL.md"),
    Path("plugins/codex/skills/review-loop/SKILL.md"),
    REVIEW_LOOP_CODEX_METADATA,
)


class ReviewLoopSkillContractsTest(unittest.TestCase):
    def test_review_loop_has_exact_source_and_runtime_path_inventory(self) -> None:
        """Keep the new skill's authored and generated surface bounded to four files."""
        existing = {
            path.relative_to(REPOSITORY_ROOT)
            for path in (
                REPOSITORY_ROOT / "shared/skill/review-loop"
            ).rglob("*")
            if path.is_file()
        } | {
            path.relative_to(REPOSITORY_ROOT)
            for platform in ("claude", "codex")
            for path in (
                REPOSITORY_ROOT / f"plugins/{platform}/skills/review-loop"
            ).rglob("*")
            if path.is_file()
        }
        self.assertEqual(set(REVIEW_LOOP_EXPECTED_PATHS), existing)

    def test_review_loop_frontmatter_controls_invocation_per_platform(self) -> None:
        """Use explicit Claude metadata and source-derived descriptions on both runtimes."""
        source = (REPOSITORY_ROOT / shared_skill_path(REVIEW_LOOP_SKILL)).read_text(
            encoding="utf-8"
        )
        claude = (REPOSITORY_ROOT / generated_skill_path("claude", REVIEW_LOOP_SKILL)).read_text(
            encoding="utf-8"
        )
        codex = (REPOSITORY_ROOT / generated_skill_path("codex", REVIEW_LOOP_SKILL)).read_text(
            encoding="utf-8"
        )
        self.assertNotIn("disable-model-invocation", source)
        self.assertTrue(claude.startswith("---\nname: review-loop\n"))
        self.assertNotIn("disable-model-invocation", claude)
        self.assertTrue(codex.startswith("---\nname: review-loop\n"))
        self.assertIn(GENERATED_MARKDOWN_WARNING, codex)
        self.assertNotIn("disable-model-invocation", codex)
        metadata = (REPOSITORY_ROOT / REVIEW_LOOP_CODEX_METADATA).read_text(
            encoding="utf-8"
        )
        self.assertRegex(metadata, r"(?m)^  allow_implicit_invocation: true$")

    def test_review_loop_generated_bodies_are_platform_streams_of_source(self) -> None:
        """Ensure generated bodies retain source sections while removing marker syntax."""
        source = (REPOSITORY_ROOT / shared_skill_path(REVIEW_LOOP_SKILL)).read_text(
            encoding="utf-8"
        )
        claude = (REPOSITORY_ROOT / generated_skill_path("claude", REVIEW_LOOP_SKILL)).read_text(
            encoding="utf-8"
        )
        codex = (REPOSITORY_ROOT / generated_skill_path("codex", REVIEW_LOOP_SKILL)).read_text(
            encoding="utf-8"
        )
        for section in ("## 入力", "## 親の裁定", "## 打ち切りと収束", "## final trim"):
            with self.subTest(section=section):
                self.assertIn(section, source)
                self.assertIn(section, claude)
                self.assertIn(section, codex)
        self.assertNotIn("<!-- claude-only", claude)
        self.assertNotIn("<!-- codex-only", codex)
        self.assertNotIn("<!-- claude-only", codex)

    def test_review_loop_codex_metadata_is_scalar_and_source_aligned(self) -> None:
        """Keep Codex interface metadata scalar and aligned with the skill name."""
        metadata = (REPOSITORY_ROOT / REVIEW_LOOP_CODEX_METADATA).read_text(
            encoding="utf-8"
        )
        self.assertRegex(metadata, r'(?m)^  display_name: "[^"]+"$')
        self.assertRegex(metadata, r'(?m)^  short_description: "[^"]+"$')
        self.assertRegex(metadata, r'(?m)^  default_prompt: ".*review-loop.*"$')


if __name__ == "__main__":
    unittest.main()
