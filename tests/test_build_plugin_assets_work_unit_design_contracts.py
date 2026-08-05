"""Deterministic repository contracts for the internal work-unit-design skill."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

from build_plugin_assets_test_support import (
    GENERATED_MARKDOWN_WARNING,
    REPOSITORY_ROOT,
    SKILL_REFERENCE_NAMES,
    WORK_UNIT_DESIGN_SKILL,
    generated_skill_path,
    shared_skill_path,
)


WORK_UNIT_DESIGN_CODEX_METADATA = Path(
    "plugins/codex/skills/work-unit-design/agents/openai.yaml"
)
WORK_UNIT_DESIGN_EXPECTED_PATHS = {
    Path("shared/skill/work-unit-design/SKILL.md"),
    Path("plugins/claude/skills/work-unit-design/SKILL.md"),
    Path("plugins/codex/skills/work-unit-design/SKILL.md"),
    WORK_UNIT_DESIGN_CODEX_METADATA,
}


class WorkUnitDesignSkillContractsTest(unittest.TestCase):
    def test_work_unit_design_has_exact_source_and_runtime_path_inventory(self) -> None:
        """Keep the internal skill limited to its source, two runtimes, and metadata."""
        existing = {
            path.relative_to(REPOSITORY_ROOT)
            for root in (
                REPOSITORY_ROOT / "shared/skill/work-unit-design",
                REPOSITORY_ROOT / "plugins/claude/skills/work-unit-design",
                REPOSITORY_ROOT / "plugins/codex/skills/work-unit-design",
            )
            for path in root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(WORK_UNIT_DESIGN_EXPECTED_PATHS, existing)

    def test_work_unit_design_declares_internal_invocation_metadata(self) -> None:
        """Keep source, generated artifacts, and Codex internal invocation metadata aligned."""
        source = (REPOSITORY_ROOT / shared_skill_path(WORK_UNIT_DESIGN_SKILL)).read_text(
            encoding="utf-8"
        )
        claude = (
            REPOSITORY_ROOT / generated_skill_path("claude", WORK_UNIT_DESIGN_SKILL)
        ).read_text(encoding="utf-8")
        codex = (
            REPOSITORY_ROOT / generated_skill_path("codex", WORK_UNIT_DESIGN_SKILL)
        ).read_text(encoding="utf-8")
        self.assertNotIn("disable-model-invocation: true", source)
        self.assertNotIn("disable-model-invocation: true", claude)
        self.assertNotIn("disable-model-invocation: true", codex)
        self.assertIn(GENERATED_MARKDOWN_WARNING, claude)
        self.assertIn(GENERATED_MARKDOWN_WARNING, codex)

        metadata = (REPOSITORY_ROOT / WORK_UNIT_DESIGN_CODEX_METADATA).read_text(
            encoding="utf-8"
        )
        self.assertEqual(
            """interface:
  display_name: "Internal Work Unit Design"
  short_description: "Design candidate Work Units only inside plan-craft-v5 or impl-lead-v5"
  default_prompt: "Use $work-unit-design only inside plan-craft-v5 or impl-lead-v5 as an internal step; do not invoke it directly."
policy:
  allow_implicit_invocation: true
""",
            metadata,
        )

    def test_registered_source_renders_exact_generated_skill_bytes(self) -> None:
        """Keep the closed mapping and generated runtime bytes in sync with shared source."""
        self.assertEqual((), SKILL_REFERENCE_NAMES[WORK_UNIT_DESIGN_SKILL])
        builder_path = REPOSITORY_ROOT / "scripts/build_plugin_assets.py"
        spec = importlib.util.spec_from_file_location("build_plugin_assets", builder_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        builder = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = builder
        spec.loader.exec_module(builder)
        outputs, errors = builder.build_outputs(REPOSITORY_ROOT)
        self.assertEqual([], errors)
        for platform in ("claude", "codex"):
            path = REPOSITORY_ROOT / generated_skill_path(platform, WORK_UNIT_DESIGN_SKILL)
            self.assertEqual(outputs[path].encode("utf-8"), path.read_bytes())

    def test_work_unit_design_has_exact_shared_caller_inventory(self) -> None:
        """Keep the internal skill referenced only by the two v5 caller sources."""
        caller_paths = {
            path.relative_to(REPOSITORY_ROOT)
            for path in (REPOSITORY_ROOT / "shared/skill").glob("*/SKILL.md")
            if path.parent.name != WORK_UNIT_DESIGN_SKILL
            and "`work-unit-design`" in path.read_text(encoding="utf-8")
        }
        self.assertEqual(
            {
                Path("shared/skill/impl-lead-v5/SKILL.md"),
                Path("shared/skill/plan-craft-v5/SKILL.md"),
            },
            caller_paths,
        )


if __name__ == "__main__":
    unittest.main()
