"""Repository contracts for the bounded v5 implementation loop."""

from __future__ import annotations

from pathlib import Path
import unittest

from build_plugin_assets_test_support import (
    GENERATED_MARKDOWN_WARNING,
    IMPL_LEAD_SKILL,
    IMPL_LEAD_V5_SKILL,
    IsolatedRepositorySupport,
    RepositoryContractSupport,
    SKILL_REFERENCE_NAMES,
    generated_skill_path,
    shared_skill_path,
)


RETIRED_MAIN_TOKENS = (
    "standard-adaptive",
    "strict-adaptive",
    "strict-full",
    "Branch Plan Set",
    "feature-lead",
    "impl-delegate",
    "impl-lead/references",
    "shared/skill/impl-lead/",
    "plugins/claude/skills/impl-lead/",
    "plugins/codex/skills/impl-lead/",
)


class ImplLeadV5ContractsTest(
    IsolatedRepositorySupport,
    RepositoryContractSupport,
    unittest.TestCase,
):
    """Keep the v5 loop independent from the existing v4 workflow."""

    def _skill_texts(self) -> dict[str, str]:
        paths = {
            "shared": shared_skill_path(IMPL_LEAD_V5_SKILL),
            "claude": generated_skill_path("claude", IMPL_LEAD_V5_SKILL),
            "codex": generated_skill_path("codex", IMPL_LEAD_V5_SKILL),
        }
        for path in paths.values():
            self.assertTrue(path.is_file(), path)
        texts = {name: self._repository_text(path) for name, path in paths.items()}
        for name, text in texts.items():
            with self.subTest(name=name):
                self.assertIn(f"name: {IMPL_LEAD_V5_SKILL}", text)
                if name != "shared":
                    self.assertIn(GENERATED_MARKDOWN_WARNING, text)
        return texts

    def test_v4_and_v5_skill_outputs_coexist_without_v5_references(self) -> None:
        """v4 and v5 skill outputs coexist while v5 has no references."""
        texts = self._skill_texts()
        for platform in ("claude", "codex"):
            self.assertFalse(
                (Path("plugins") / platform / "skills" / IMPL_LEAD_V5_SKILL / "references").exists()
            )
            self.assertTrue(
                (Path("plugins") / platform / "skills" / IMPL_LEAD_SKILL / "SKILL.md").is_file()
            )
        self.assertEqual((), SKILL_REFERENCE_NAMES[IMPL_LEAD_V5_SKILL])
        self.assertIn(f"name: {IMPL_LEAD_V5_SKILL}", texts["shared"])

    def test_skill_is_explicit_only_on_both_runtimes(self) -> None:
        """Disable implicit model invocation while retaining the explicit skill name."""
        texts = self._skill_texts()
        claude_frontmatter = texts["claude"].split("---", 2)[1]
        self.assertIn("disable-model-invocation: true", claude_frontmatter)

        codex_metadata = Path(
            "plugins/codex/skills/impl-lead-v5/agents/openai.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "policy:\n  allow_implicit_invocation: false\n",
            codex_metadata,
        )
        prompt_lines = [
            line
            for line in codex_metadata.splitlines()
            if line.startswith("  default_prompt:")
        ]
        self.assertEqual(1, len(prompt_lines))
        self.assertIn(f"${IMPL_LEAD_V5_SKILL}", prompt_lines[0])

    def test_shared_main_has_no_v4_reference_paths_or_retired_identifiers(self) -> None:
        """The v5 source does not expose retired v4 paths or identifiers."""
        text = self._repository_text(shared_skill_path(IMPL_LEAD_V5_SKILL))
        for token in RETIRED_MAIN_TOKENS:
            self.assertNotIn(token, text, token)

    def test_build_replaces_stale_v5_outputs_with_platform_specific_content(self) -> None:
        """The build outputs current platform-specific v5 content."""
        with self._temporary_repository() as root:
            stale = {
                platform: (root / generated_skill_path(platform, IMPL_LEAD_V5_SKILL)).read_text(
                    encoding="utf-8"
                )
                for platform in ("claude", "codex")
            }
            result = self._run(root)
            self.assertEqual(0, result.returncode, result)
            for platform in ("claude", "codex"):
                output = (root / generated_skill_path(platform, IMPL_LEAD_V5_SKILL)).read_text(
                    encoding="utf-8"
                )
                self.assertNotEqual(stale[platform], output)
                self.assertIn(f"name: {IMPL_LEAD_V5_SKILL}\n", output)
                self.assertIn(GENERATED_MARKDOWN_WARNING, output)
                self.assertNotIn(f"stale {platform} skill", output)
                if platform == "claude":
                    self.assertIn("description: Claude fixture skill\n", output)
                    self.assertIn("Parent Claude agent uses SendMessage.", output)
                    self.assertNotIn("Codex-only instruction.", output)
                else:
                    self.assertIn("description: Codex fixture skill\n", output)
                    self.assertIn("Parent Codex agent uses followup_task.", output)
                    self.assertNotIn("Claude-only instruction.", output)
                self.assertFalse(
                    (root / f"plugins/{platform}/skills/{IMPL_LEAD_V5_SKILL}/references").exists()
                )


if __name__ == "__main__":
    unittest.main()
