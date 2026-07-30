"""Isolated-repository CLI tests for agent generation and validation."""

from __future__ import annotations

import tomllib
import unittest

from build_plugin_assets_test_support import (
    BASH_GRANTED_REVIEWER_NAMES,
    BASH_WITHHELD_REVIEWER_NAMES,
    GENERATED_MARKDOWN_WARNING,
    IsolatedRepositorySupport,
    REFACTORER_NAMES,
    REVIEWER_NAMES,
)


class BuildPluginAssetsAgentCliTest(IsolatedRepositorySupport, unittest.TestCase):
    """Verify the generator only through its documented command-line interface."""

    def test_build_renders_agent_metadata_and_markdown_body(self) -> None:
        """Render ordered platform metadata while preserving the Markdown body."""
        with self._temporary_repository() as root:
            result = self._run(root)
            self.assertEqual(0, result.returncode, result)

            claude_path = root / "plugins/claude/agents/implementer.md"
            claude = claude_path.read_text(encoding="utf-8")
            claude_lines = claude.splitlines()
            expected_claude_prefix = [
                "---",
                'name: "implementer"',
                'description: "Claude implementer"',
                "model: sonnet",
                "effort: medium",
                "---",
                GENERATED_MARKDOWN_WARNING,
            ]
            self.assertEqual(expected_claude_prefix, claude_lines[:7])
            self.assertIn(
                "# Parent Claude agent\n\nUse **SendMessage** for the next turn.\n\n"
                "- Keep the Markdown body.\n"
                'Path C:\\workspace has "double quotes".\n'
                'Keep """three consecutive quotes""" intact.\n\n'
                "Claude agent only.\n",
                claude,
            )
            self.assertNotIn("Codex agent only.", claude)

            codex_path = root / "plugins/codex/install/agents/implementer.toml"
            codex = codex_path.read_text(encoding="utf-8")
            codex_lines = codex.splitlines()
            expected_key_order = [
                "name",
                "description",
                "model",
                "model_reasoning_effort",
                "nickname_candidates",
                "developer_instructions",
            ]
            actual_key_order = [
                line.split("=", 1)[0].strip()
                for line in codex_lines
                if "=" in line and not line.startswith("#")
            ]
            self.assertEqual(expected_key_order, actual_key_order)
            metadata = tomllib.loads(codex)
            self.assertEqual("implementer", metadata["name"])
            self.assertEqual("Codex implementer", metadata["description"])
            self.assertEqual(["Builder", "TDD Worker"], metadata["nickname_candidates"])
            self.assertEqual(
                "# Parent Codex agent\n\n"
                "Use **followup_task** for the next turn.\n\n"
                "- Keep the Markdown body.\n"
                'Path C:\\workspace has "double quotes".\n'
                'Keep """three consecutive quotes""" intact.\n\n'
                "Codex agent only.\n",
                metadata["developer_instructions"],
            )

    def test_codex_agent_body_round_trips_toml_special_characters(self) -> None:
        """Preserve quotes, backslashes, and triple quotes through Codex TOML."""
        with self._temporary_repository() as root:
            result = self._run(root)
            self.assertEqual(0, result.returncode, result)

            metadata = tomllib.loads(
                (root / "plugins/codex/install/agents/implementer.toml").read_text(
                    encoding="utf-8"
                )
            )
            expected_body = (
                "# Parent Codex agent\n\n"
                "Use **followup_task** for the next turn.\n\n"
                "- Keep the Markdown body.\n"
                'Path C:\\workspace has "double quotes".\n'
                'Keep """three consecutive quotes""" intact.\n\n'
                "Codex agent only.\n"
            )
            self.assertEqual(expected_body, metadata["developer_instructions"])

    def test_build_publishes_read_only_codex_reviewers_and_writable_refactorers(
        self,
    ) -> None:
        """Publish reviewer sandboxes without restricting writable refactorers."""
        with self._temporary_repository() as root:
            result = self._run(root)
            self.assertEqual(0, result.returncode, result)

            implementer = tomllib.loads(
                (root / "plugins/codex/install/agents/implementer.toml").read_text(
                    encoding="utf-8"
                )
            )
            self.assertNotIn("sandbox_mode", implementer)

            for name in REVIEWER_NAMES:
                with self.subTest(name=name):
                    reviewer_text = (
                        root / f"plugins/codex/install/agents/{name}.toml"
                    ).read_text(encoding="utf-8")
                    reviewer = tomllib.loads(reviewer_text)

                    self.assertEqual("read-only", reviewer["sandbox_mode"])
                    # The Claude-side tool policy now differs per reviewer, so a
                    # leaked key would no longer look uniform enough to spot by
                    # eye in the generated Codex artifact.
                    self.assertNotIn("tools", reviewer)
                    self.assertNotIn("disallowed_tools", reviewer)
                    self.assertLess(
                        reviewer_text.index("model_reasoning_effort ="),
                        reviewer_text.index("sandbox_mode ="),
                    )
                    self.assertLess(
                        reviewer_text.index("sandbox_mode ="),
                        reviewer_text.index("nickname_candidates ="),
                    )

            for name in REFACTORER_NAMES:
                with self.subTest(name=name):
                    refactorer = tomllib.loads(
                        (
                            root / f"plugins/codex/install/agents/{name}.toml"
                        ).read_text(encoding="utf-8")
                    )
                    self.assertNotIn("sandbox_mode", refactorer)

    def test_build_emits_claude_tool_policy_split_by_reviewer_exploration_reach(
        self,
    ) -> None:
        """Reject file-changing tools for every reviewer while granting Bash only to the wider-reach group."""
        expected_tool_lines = {
            name: (
                "tools: Read, Grep, Glob, Bash\n",
                "disallowedTools: Edit, Write, NotebookEdit\n",
            )
            for name in BASH_GRANTED_REVIEWER_NAMES
        } | {
            name: (
                "tools: Read, Grep, Glob\n",
                "disallowedTools: Bash, Edit, Write, NotebookEdit\n",
            )
            for name in BASH_WITHHELD_REVIEWER_NAMES
        }
        with self._temporary_repository() as root:
            result = self._run(root)
            self.assertEqual(0, result.returncode, result)

            for name, (tools_line, disallowed_line) in expected_tool_lines.items():
                with self.subTest(name=name):
                    reviewer = (
                        root / f"plugins/claude/agents/{name}.md"
                    ).read_text(encoding="utf-8")
                    self.assertIn(tools_line, reviewer)
                    self.assertIn(disallowed_line, reviewer)

            refactorer = (
                root / "plugins/claude/agents/review-patch-refactorer.md"
            ).read_text(encoding="utf-8")
            self.assertNotIn("tools:", refactorer)
            self.assertNotIn("disallowedTools:", refactorer)

    def test_build_rejects_invalid_agent_frontmatter_without_writing(self) -> None:
        """Reject schema, type, name, delimiter, and placeholder violations atomically."""
        mutations = {
            "unknown top-level key": lambda text: text.replace(
                'name = "implementer"\n',
                'name = "implementer"\nunknown = "value"\n',
                1,
            ),
            "unknown Claude key": lambda text: text.replace(
                'effort = "medium"\n',
                'effort = "medium"\ntemperature = 1\n',
                1,
            ),
            "unknown Codex key": lambda text: text.replace(
                'nickname_candidates = ["Builder", "TDD Worker"]\n',
                'nickname_candidates = ["Builder", "TDD Worker"]\nunknown = true\n',
                1,
            ),
            "missing Claude description": lambda text: text.replace(
                'description = "Claude implementer"\n', "", 1
            ),
            "missing Claude model": lambda text: text.replace(
                'model = "sonnet"\n', "", 1
            ),
            "missing Claude effort": lambda text: text.replace(
                'effort = "medium"\n', "", 1
            ),
            "missing Codex description": lambda text: text.replace(
                'description = "Codex implementer"\n', "", 1
            ),
            "missing Codex model": lambda text: text.replace(
                'model = "gpt-5.5"\n', "", 1
            ),
            "missing Codex reasoning effort": lambda text: text.replace(
                'model_reasoning_effort = "medium"\n', "", 1
            ),
            "missing Codex nickname candidates": lambda text: text.replace(
                'nickname_candidates = ["Builder", "TDD Worker"]\n', "", 1
            ),
            "missing common name": lambda text: text.replace(
                'name = "implementer"\n', "", 1
            ),
            "missing Claude table": lambda text: text.replace("[claude]\n", "", 1),
            "missing Codex table": lambda text: text.replace("[codex]\n", "", 1),
            "duplicate key": lambda text: text.replace(
                'description = "Claude implementer"\n',
                'description = "Claude implementer"\n'
                'description = "duplicate"\n',
                1,
            ),
            "wrong scalar type": lambda text: text.replace(
                'name = "implementer"\n', "name = 1\n", 1
            ),
            "wrong list type": lambda text: text.replace(
                'nickname_candidates = ["Builder", "TDD Worker"]\n',
                'nickname_candidates = "Builder"\n',
                1,
            ),
            "wrong list element type": lambda text: text.replace(
                'nickname_candidates = ["Builder", "TDD Worker"]\n',
                'nickname_candidates = ["Builder", 1]\n',
                1,
            ),
            "wrong sandbox type": lambda text: text.replace(
                'model_reasoning_effort = "medium"\n',
                'model_reasoning_effort = "medium"\nsandbox_mode = true\n',
                1,
            ),
            "wrong Claude tools type": lambda text: text.replace(
                'effort = "medium"\n',
                'effort = "medium"\ntools = "Read"\n',
                1,
            ),
            "wrong Claude tool element type": lambda text: text.replace(
                'effort = "medium"\n',
                'effort = "medium"\ntools = ["Read", 1]\n',
                1,
            ),
            "wrong Claude disallowed tools type": lambda text: text.replace(
                'effort = "medium"\n',
                'effort = "medium"\ndisallowed_tools = "Write"\n',
                1,
            ),
            "name does not match filename": lambda text: text.replace(
                'name = "implementer"\n', 'name = "other-agent"\n', 1
            ),
            "placeholder in frontmatter": lambda text: text.replace(
                'description = "Claude implementer"\n',
                'description = "{{parent_name}}"\n',
                1,
            ),
            "unclosed frontmatter": lambda text: text.replace("+++\n\n#", "\n#", 1),
            "missing opening frontmatter": lambda text: text.removeprefix("+++\n"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label), self._temporary_repository() as root:
                source = root / "shared/agents/implementer.md"
                source.write_text(
                    mutate(source.read_text(encoding="utf-8")),
                    encoding="utf-8",
                    newline="",
                )
                before = self._snapshot(self._generated_paths(root))
                self._assert_validation_error(
                    root,
                    ("shared/agents/implementer.md",),
                    before,
                )

    def test_build_rejects_empty_agent_markdown_bodies_without_writing(self) -> None:
        """Reject absent and whitespace-only common agent bodies atomically."""
        for label, body in (("absent", ""), ("whitespace", " \n\t\n")):
            with self.subTest(label=label), self._temporary_repository() as root:
                source = root / "shared/agents/implementer.md"
                frontmatter = source.read_text(encoding="utf-8").rsplit("+++\n", 1)[0]
                source.write_text(
                    f"{frontmatter}+++\n{body}",
                    encoding="utf-8",
                    newline="",
                )
                before = self._snapshot(self._generated_paths(root))

                self._assert_validation_error(
                    root,
                    ("shared/agents/implementer.md",),
                    before,
                )


if __name__ == "__main__":
    unittest.main()
