"""Isolated-repository CLI tests for inputs, versions, and manifests."""

from __future__ import annotations

import unittest

from build_plugin_assets_test_support import (
    GENERATED_MARKDOWN_WARNING,
    IsolatedRepositorySupport,
    SHARED_SKILL_PATH,
    SHARED_SKILL_REFERENCE_PATHS,
)


class BuildPluginAssetsInputCliTest(IsolatedRepositorySupport, unittest.TestCase):
    """Verify the generator only through its documented command-line interface."""

    def test_build_validates_terms_and_placeholders(self) -> None:
        """Reject invalid term definitions, names, usage, and unresolved placeholders."""
        def undefined_placeholder(root: Path) -> None:
            """Replace one known skill placeholder with an undefined name."""
            source = root / SHARED_SKILL_PATH
            source.write_text(
                source.read_text(encoding="utf-8").replace(
                    "{{parent_name}} uses", "{{missing_term}} uses", 1
                ),
                encoding="utf-8",
                newline="",
            )

        def mutate_terms(root: Path, old: str, new: str) -> None:
            """Apply one deliberate mutation to the isolated term table."""
            terms = root / "shared/terms.toml"
            terms.write_text(
                terms.read_text(encoding="utf-8").replace(old, new, 1),
                encoding="utf-8",
                newline="",
            )

        mutations = {
            "undefined placeholder": undefined_placeholder,
            "missing platform value": lambda root: mutate_terms(
                root, 'codex = "Parent Codex agent"\n', ""
            ),
            "empty value": lambda root: mutate_terms(
                root, 'claude = "Parent Claude agent"', 'claude = ""'
            ),
            "multiline value": lambda root: mutate_terms(
                root,
                'claude = "Parent Claude agent"',
                'claude = """Parent\nClaude agent"""',
            ),
            "unused term": lambda root: mutate_terms(
                root,
                "[terms.parent_name]",
                "[terms.unused_name]\n"
                'claude = "unused"\n'
                'codex = "unused"\n\n'
                "[terms.parent_name]",
            ),
            "invalid term name": lambda root: mutate_terms(
                root, "[terms.parent_name]", "[terms.Parent_Name]"
            ),
            "leading digit term name": lambda root: mutate_terms(
                root, "[terms.parent_name]", "[terms.1parent_name]"
            ),
            "double underscore term name": lambda root: mutate_terms(
                root, "[terms.parent_name]", "[terms.parent__name]"
            ),
            "trailing underscore term name": lambda root: mutate_terms(
                root, "[terms.parent_name]", "[terms.parent_name_]"
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label), self._temporary_repository() as root:
                mutate(root)
                before = self._snapshot(self._generated_paths(root))
                self._assert_validation_error(root, ("shared/",), before)

    def test_build_does_not_recursively_expand_term_values(self) -> None:
        """Leave placeholder-shaped text introduced by a term value untouched."""
        with self._temporary_repository() as root:
            terms = root / "shared/terms.toml"
            terms.write_text(
                terms.read_text(encoding="utf-8")
                .replace(
                    'claude = "Parent Claude agent"',
                    'claude = "Parent {{literal_name}} agent"',
                    1,
                )
                .replace(
                    'codex = "Parent Codex agent"',
                    'codex = "Parent {{literal_name}} agent"',
                    1,
                ),
                encoding="utf-8",
                newline="",
            )

            result = self._run(root)

            self.assertEqual(0, result.returncode, result)
            self.assertIn(
                "Parent {{literal_name}} agent uses SendMessage.",
                (root / "plugins/claude/skills/impl-lead/SKILL.md").read_text(
                    encoding="utf-8"
                ),
            )
            self.assertIn(
                "Parent {{literal_name}} agent uses followup_task.",
                (root / "plugins/codex/skills/impl-lead/SKILL.md").read_text(
                    encoding="utf-8"
                ),
            )

    def test_build_requires_fixed_sources_and_rejects_unknown_shared_markdown(self) -> None:
        """Require every canonical input and reject unknown managed Markdown."""
        required_sources = (
            "shared/terms.toml",
            SHARED_SKILL_PATH.as_posix(),
            *(path.as_posix() for path in SHARED_SKILL_REFERENCE_PATHS.values()),
        )
        for missing in required_sources:
            with self.subTest(missing=missing), self._temporary_repository() as root:
                (root / missing).unlink()
                before = self._snapshot(self._generated_paths(root))
                self._assert_validation_error(root, (missing,), before)

        unknown_skill_paths = (
            SHARED_SKILL_PATH.parent / "notes.md",
            SHARED_SKILL_PATH.parent / "references" / "unknown-reference.md",
        )
        for unknown in unknown_skill_paths:
            with self.subTest(unknown=unknown), self._temporary_repository() as root:
                self._write(root, unknown.as_posix(), "# Unknown reference\n")
                before = self._snapshot(self._generated_paths(root))
                self._assert_validation_error(
                    root,
                    (unknown.as_posix(),),
                    before,
                )

    def test_build_rejects_invalid_skill_references_atomically(self) -> None:
        """Reject invalid or platform-empty references without partial updates."""
        mutations = {
            "invalid marker": (
                lambda text: text + "<!-- claude-only:start -->\nunclosed\n",
                "marker",
            ),
            "undefined placeholder": (
                lambda text: text.replace(
                    "{{parent_name}} reference",
                    "{{missing_term}} reference",
                    1,
                ),
                "undefined placeholder",
            ),
            "platform-empty body": (
                lambda text: (
                    "<!-- codex-only:start -->\n"
                    "# Codex only\n"
                    "<!-- codex-only:end -->\n"
                ),
                "claude",
            ),
        }
        reference_path = SHARED_SKILL_REFERENCE_PATHS[
            "implementation-branches.md"
        ]

        for label, (mutate, expected_message) in mutations.items():
            with self.subTest(label=label), self._temporary_repository() as root:
                source = root / reference_path
                source.write_text(
                    mutate(source.read_text(encoding="utf-8")),
                    encoding="utf-8",
                    newline="",
                )
                before = self._snapshot(self._generated_paths(root))

                stderr = self._assert_validation_error(
                    root,
                    (reference_path.as_posix(),),
                    before,
                )

                self.assertIn(expected_message, stderr.lower())

    def test_build_places_generated_warnings_on_skill_markdown(self) -> None:
        """Place exact warnings at generated skill frontmatter boundaries."""
        with self._temporary_repository() as root:
            result = self._run(root)
            self.assertEqual(0, result.returncode, result)

            markdown_paths = [
                root / "plugins/claude/skills/impl-lead/SKILL.md",
                root / "plugins/codex/skills/impl-lead/SKILL.md",
            ]
            for path in markdown_paths:
                content = path.read_text(encoding="utf-8")
                lines = content.splitlines()
                self.assertEqual(
                    GENERATED_MARKDOWN_WARNING,
                    lines[self._frontmatter_warning_index(content)],
                    path,
                )
                self.assertEqual(1, content.count(GENERATED_MARKDOWN_WARNING), path)


if __name__ == "__main__":
    unittest.main()
