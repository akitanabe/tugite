"""Isolated-repository CLI tests for skill generation and markers."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from build_plugin_assets_test_support import (
    IMPL_LEAD_SKILL,
    GENERATED_SKILL_REFERENCE_PATHS,
    GENERATED_MARKDOWN_WARNING,
    IsolatedRepositorySupport,
    PLATFORMS,
    SHARED_SKILL_PATH,
    SKILL_REFERENCE_NAMES,
    generated_skill_path,
    generated_skill_reference_path,
    shared_skill_path,
    shared_skill_reference_path,
)


class BuildPluginAssetsSkillCliTest(IsolatedRepositorySupport, unittest.TestCase):
    """Verify the generator only through its documented command-line interface."""

    def test_build_generates_all_assets_and_syncs_versions(self) -> None:
        """Generate skill packages, eighteen agent assets, and synchronized versions."""
        with self._temporary_repository() as root:
            result = self._run(root)

            self.assertEqual(0, result.returncode, result)
            self.assertEqual("", result.stderr)
            self.assertTrue(result.stdout.strip())
            for path in self._generated_paths(root):
                self.assertTrue(path.is_file(), path)

            for manifest_path in (
                "plugins/claude/.claude-plugin/plugin.json",
                "plugins/codex/.codex-plugin/plugin.json",
            ):
                manifest = json.loads((root / manifest_path).read_text(encoding="utf-8"))
                self.assertEqual("1.2.3", manifest["version"])
                self.assertEqual(f"fixture for {manifest_path}", manifest["description"])
            self.assertEqual(
                "1.2.3\n",
                (root / "plugins/codex/install/VERSION").read_text(encoding="utf-8"),
            )

    def test_build_filters_markers_before_replacing_terms(self) -> None:
        """Select one platform branch, then replace terms without leaking markers."""
        with self._temporary_repository() as root:
            result = self._run(root)
            self.assertEqual(0, result.returncode, result)

            claude = (
                root / "plugins/claude/skills/impl-lead/SKILL.md"
            ).read_text(encoding="utf-8")
            codex = (
                root / "plugins/codex/skills/impl-lead/SKILL.md"
            ).read_text(encoding="utf-8")
            self.assertTrue(claude.startswith("---\nname: impl-lead\n"))
            self.assertTrue(codex.startswith("---\nname: impl-lead\n"))
            self.assertIn("Parent Claude agent uses SendMessage.", claude)
            self.assertIn("Claude-only instruction.", claude)
            self.assertNotIn("Codex-only instruction.", claude)
            self.assertIn("Parent Codex agent uses followup_task.", codex)
            self.assertIn("Codex-only instruction.", codex)
            self.assertNotIn("Claude-only instruction.", codex)
            self.assertNotIn("<!-- claude-only", claude + codex)
            self.assertNotIn("<!-- codex-only", claude + codex)

    def test_build_generates_platform_specific_skill_references(self) -> None:
        """Render every canonical reference with the same marker and term rules."""
        with self._temporary_repository() as root:
            result = self._run(root)

            self.assertEqual(0, result.returncode, result)
            self.assertEqual("", result.stderr)
            for name in SKILL_REFERENCE_NAMES[IMPL_LEAD_SKILL]:
                claude = (
                    root / GENERATED_SKILL_REFERENCE_PATHS["claude"][name]
                ).read_text(encoding="utf-8")
                codex = (
                    root / GENERATED_SKILL_REFERENCE_PATHS["codex"][name]
                ).read_text(encoding="utf-8")

                self.assertTrue(
                    claude.startswith(f"{GENERATED_MARKDOWN_WARNING}\n\n")
                )
                self.assertTrue(
                    codex.startswith(f"{GENERATED_MARKDOWN_WARNING}\n\n")
                )
                self.assertIn(
                    "Parent Claude agent reference uses SendMessage.",
                    claude,
                )
                self.assertIn(f"Claude reference only: {name}.", claude)
                self.assertNotIn("Codex reference only:", claude)
                self.assertIn(
                    "Parent Codex agent reference uses followup_task.",
                    codex,
                )
                self.assertIn(f"Codex reference only: {name}.", codex)
                self.assertNotIn("Claude reference only:", codex)
                self.assertNotIn("<!-- claude-only", claude + codex)
                self.assertNotIn("<!-- codex-only", claude + codex)
                self.assertTrue(claude.endswith("\n"))
                self.assertTrue(codex.endswith("\n"))

    def test_build_generates_every_registered_skill(self) -> None:
        """Generate SKILL.md and references for each mapping entry on both platforms."""
        extra = {"secondary-workflow": ("alpha.md", "beta.md")}
        with self._temporary_repository(extra_skills=extra) as root:
            result = self._run(root)

            self.assertEqual(0, result.returncode, result)
            self.assertEqual("", result.stderr)
            for platform in PLATFORMS:
                skill = root / generated_skill_path(platform, "secondary-workflow")
                self.assertTrue(skill.is_file(), skill)
                for name in extra["secondary-workflow"]:
                    reference = root / generated_skill_reference_path(
                        platform, "secondary-workflow", name
                    )
                    self.assertTrue(reference.is_file(), reference)
                    self.assertTrue(
                        reference.read_text(encoding="utf-8").startswith(
                            f"{GENERATED_MARKDOWN_WARNING}\n\n"
                        )
                    )
                self.assertTrue(
                    (root / generated_skill_path(platform, IMPL_LEAD_SKILL)).is_file()
                )

    def test_build_generates_skill_without_references(self) -> None:
        """Emit only SKILL.md for a registered skill that maps to no references."""
        extra = {"reference-free": ()}
        with self._temporary_repository(extra_skills=extra) as root:
            result = self._run(root)

            self.assertEqual(0, result.returncode, result)
            self.assertEqual("", result.stderr)
            for platform in PLATFORMS:
                self.assertTrue(
                    (root / generated_skill_path(platform, "reference-free")).is_file()
                )
                self.assertFalse(
                    (
                        root / f"plugins/{platform}/skills/reference-free/references"
                    ).exists()
                )

    def test_build_rejects_unknown_skill_directory(self) -> None:
        """Reject a skill directory that no mapping entry registers."""
        with self._temporary_repository() as root:
            self._write(
                root,
                "shared/skill/unregistered/SKILL.md",
                "---\nname: unregistered\ndescription: x\n---\n\n# body\n",
            )
            before = self._snapshot(self._generated_paths(root))

            self._assert_validation_error(
                root,
                ("shared/skill/unregistered",),
                before,
            )

    def test_build_requires_and_bounds_every_registered_skill_source(self) -> None:
        """Require each mapped source and reject unknown Markdown for every skill."""
        extra = {"secondary-workflow": ("alpha.md",)}

        def remove_skill(root: Path) -> str:
            path = shared_skill_path("secondary-workflow")
            (root / path).unlink()
            return path.as_posix()

        def remove_reference(root: Path) -> str:
            path = shared_skill_reference_path("secondary-workflow", "alpha.md")
            (root / path).unlink()
            return path.as_posix()

        def add_unknown_markdown(root: Path) -> str:
            path = "shared/skill/secondary-workflow/notes.md"
            self._write(root, path, "# stray\n")
            return path

        def add_unknown_reference(root: Path) -> str:
            path = "shared/skill/secondary-workflow/references/stray.md"
            self._write(root, path, "# stray\n")
            return path

        for label, mutate in {
            "missing SKILL.md": remove_skill,
            "missing reference": remove_reference,
            "unknown skill Markdown": add_unknown_markdown,
            "unknown reference Markdown": add_unknown_reference,
        }.items():
            with (
                self.subTest(label=label),
                self._temporary_repository(extra_skills=extra) as root,
            ):
                expected_path = mutate(root)
                before = self._snapshot(self._generated_paths(root, extra_skills=extra))

                self._assert_validation_error(root, (expected_path,), before)

    def test_check_detects_stale_output_for_each_registered_skill(self) -> None:
        """Report one registered skill's stale artifact while leaving others intact."""
        extra = {"secondary-workflow": ("alpha.md",)}
        with self._temporary_repository(extra_skills=extra) as root:
            build = self._run(root)
            self.assertEqual(0, build.returncode, build)

            stale = root / generated_skill_reference_path(
                "claude", "secondary-workflow", "alpha.md"
            )
            stale.write_text("stale\n", encoding="utf-8", newline="")
            paths = self._generated_paths(root, extra_skills=extra)
            before = self._snapshot(paths)

            result = self._run(root, "--check")

            self.assertEqual(1, result.returncode, result)
            self.assertEqual("", result.stdout)
            self.assertIn(
                generated_skill_reference_path(
                    "claude", "secondary-workflow", "alpha.md"
                ).as_posix(),
                result.stderr,
            )
            self.assertEqual(before, self._snapshot(paths))

    def test_build_accepts_whitespace_around_marker_lines(self) -> None:
        """Treat a marker as valid after stripping leading and trailing whitespace."""
        with self._temporary_repository() as root:
            source = root / SHARED_SKILL_PATH
            content = source.read_text(encoding="utf-8")
            content = content.replace("<!-- claude-only", "  <!-- claude-only")
            content = content.replace("<!-- codex-only", "\t<!-- codex-only")
            content = content.replace(" -->\n", " -->  \n")
            source.write_text(content, encoding="utf-8", newline="")

            result = self._run(root)

            self.assertEqual(0, result.returncode, result)
            self.assertEqual("", result.stderr)

    def test_build_rejects_invalid_markers_without_writing_outputs(self) -> None:
        """Reject malformed marker structure with line diagnostics and no writes."""
        invalid_sources = {
            "not independent": "prefix <!-- claude-only:start -->\n",
            "nested": (
                "<!-- claude-only:start -->\n"
                "<!-- codex-only:start -->\n"
                "text\n"
                "<!-- codex-only:end -->\n"
                "<!-- claude-only:end -->\n"
            ),
            "unknown platform": (
                "<!-- other-only:start -->\ntext\n<!-- other-only:end -->\n"
            ),
            "stray end": "<!-- claude-only:end -->\n",
            "mismatched end": (
                "<!-- claude-only:start -->\ntext\n<!-- codex-only:end -->\n"
            ),
            "unclosed": "<!-- claude-only:start -->\ntext\n",
            "unknown action": "<!-- claude-only:begin -->\n",
            "missing action": "<!-- claude-only -->\n",
        }
        for label, invalid in invalid_sources.items():
            with self.subTest(label=label), self._temporary_repository() as root:
                source = root / SHARED_SKILL_PATH
                source.write_text(
                    source.read_text(encoding="utf-8").replace(
                        "# Delegation\n",
                        f"# Delegation\n{invalid}",
                        1,
                    ),
                    encoding="utf-8",
                    newline="",
                )
                before = self._snapshot(self._generated_paths(root))

                stderr = self._assert_validation_error(
                    root,
                    (SHARED_SKILL_PATH.as_posix(),),
                    before,
                )

                self.assertRegex(
                    stderr,
                    rf"{SHARED_SKILL_PATH.as_posix()}:\d+",
                )
                self.assertIn("marker", stderr.lower())

    def test_build_preserves_unrelated_html_comments(self) -> None:
        """Keep ordinary HTML comments that are not platform marker syntax."""
        with self._temporary_repository() as root:
            source = root / SHARED_SKILL_PATH
            comment = "<!-- ordinary documentation note -->"
            source.write_text(
                source.read_text(encoding="utf-8").replace(
                    "# Delegation\n",
                    f"# Delegation\n{comment}\n",
                    1,
                ),
                encoding="utf-8",
                newline="",
            )

            result = self._run(root)

            self.assertEqual(0, result.returncode, result)
            for platform in ("claude", "codex"):
                generated = (
                    root / f"plugins/{platform}/skills/impl-lead/SKILL.md"
                ).read_text(encoding="utf-8")
                self.assertIn(comment, generated)

    def test_build_validates_each_rendered_skill_frontmatter_and_body(self) -> None:
        """Reject missing YAML frontmatter and empty bodies for both rendered skills."""
        def rendered_validation_source(platform: str, problem: str) -> str:
            """Build one source whose selected platform render has one boundary error."""
            claude_frontmatter = (
                "not Claude frontmatter\n"
                if platform == "claude" and problem == "frontmatter"
                else "---\nname: impl-lead\ndescription: Claude skill\n---\n"
            )
            codex_frontmatter = (
                "not Codex frontmatter\n"
                if platform == "codex" and problem == "frontmatter"
                else "---\nname: impl-lead\ndescription: Codex skill\n---\n"
            )
            if problem == "frontmatter":
                body = "\n{{parent_name}} uses {{followup_tool}}.\n"
            else:
                claude_body = (
                    ""
                    if platform == "claude"
                    else "{{parent_name}} uses {{followup_tool}}.\n"
                )
                codex_body = (
                    ""
                    if platform == "codex"
                    else "{{parent_name}} uses {{followup_tool}}.\n"
                )
                body = (
                    "\n<!-- claude-only:start -->\n"
                    f"{claude_body}"
                    "<!-- claude-only:end -->\n"
                    "<!-- codex-only:start -->\n"
                    f"{codex_body}"
                    "<!-- codex-only:end -->\n"
                )
            return (
                "<!-- claude-only:start -->\n"
                f"{claude_frontmatter}"
                "<!-- claude-only:end -->\n"
                "<!-- codex-only:start -->\n"
                f"{codex_frontmatter}"
                "<!-- codex-only:end -->\n"
                f"{body}"
            )

        for platform in ("claude", "codex"):
            for problem in ("frontmatter", "body"):
                with (
                    self.subTest(platform=platform, problem=problem),
                    self._temporary_repository() as root,
                ):
                    source = root / SHARED_SKILL_PATH
                    source.write_text(
                        rendered_validation_source(platform, problem),
                        encoding="utf-8",
                        newline="",
                    )
                    before = self._snapshot(self._generated_paths(root))

                    stderr = self._assert_validation_error(
                        root,
                        (SHARED_SKILL_PATH.as_posix(),),
                        before,
                    )

                    self.assertIn(platform, stderr.lower())


if __name__ == "__main__":
    unittest.main()
