"""Isolated-repository CLI tests for check and write behavior."""

from __future__ import annotations

import json
import os
import unittest

from build_plugin_assets_test_support import (
    GENERATED_SKILL_REFERENCE_PATHS,
    IsolatedRepositorySupport,
    SHARED_SKILL_PATH,
)


class BuildPluginAssetsCheckCliTest(IsolatedRepositorySupport, unittest.TestCase):
    """Verify the generator only through its documented command-line interface."""

    def test_check_succeeds_without_modifying_matching_outputs(self) -> None:
        """Return zero from --check and leave matching generated files untouched."""
        with self._temporary_repository() as root:
            build = self._run(root)
            self.assertEqual(0, build.returncode, build)
            paths = self._generated_paths(root)
            known_mtime = 1_700_000_000_000_000_000
            for path in paths:
                os.utime(path, ns=(known_mtime, known_mtime))
            before = self._snapshot(paths)

            result = self._run(root, "--check")

            self.assertEqual(0, result.returncode, result)
            self.assertEqual("", result.stderr)
            self.assertTrue(result.stdout.strip())
            self.assertEqual(before, self._snapshot(paths))
            self.assertTrue(all(path.stat().st_mtime_ns == known_mtime for path in paths))

    def test_check_reports_all_stale_and_missing_outputs_without_writing(self) -> None:
        """List every mismatch on stderr with exit one and never repair it in --check."""
        with self._temporary_repository() as root:
            build = self._run(root)
            self.assertEqual(0, build.returncode, build)

            stale_skill = root / "plugins/claude/skills/impl-lead/SKILL.md"
            stale_reference = (
                root
                / GENERATED_SKILL_REFERENCE_PATHS["claude"][
                    "implementation-branches.md"
                ]
            )
            missing_reference = (
                root
                / GENERATED_SKILL_REFERENCE_PATHS["codex"]["expert-selection.md"]
            )
            missing_agent = root / "plugins/codex/install/agents/implementer.toml"
            stale_manifest = root / "plugins/codex/.codex-plugin/plugin.json"
            stale_skill.write_text("stale\n", encoding="utf-8", newline="")
            stale_reference.write_text("stale\n", encoding="utf-8", newline="")
            missing_reference.unlink()
            missing_agent.unlink()
            manifest = json.loads(stale_manifest.read_text(encoding="utf-8"))
            manifest["version"] = "9.9.9"
            stale_manifest.write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline=""
            )
            paths = self._generated_paths(root)
            before = self._snapshot(paths)

            result = self._run(root, "--check")

            self.assertEqual(1, result.returncode, result)
            self.assertEqual("", result.stdout)
            for relative_path in (
                "plugins/claude/skills/impl-lead/SKILL.md",
                (
                    "plugins/claude/skills/impl-lead/references/"
                    "implementation-branches.md"
                ),
                (
                    "plugins/codex/skills/impl-lead/references/"
                    "expert-selection.md"
                ),
                "plugins/codex/install/agents/implementer.toml",
                "plugins/codex/.codex-plugin/plugin.json",
            ):
                self.assertIn(relative_path, result.stderr)
            self.assertEqual(before, self._snapshot(paths))

    def test_check_reports_input_errors_without_writing(self) -> None:
        """Return validation exit one on --check and preserve every stale output."""
        with self._temporary_repository() as root:
            (root / "shared/VERSION").write_text(
                "01.0.0\n", encoding="utf-8", newline=""
            )
            paths = self._generated_paths(root)
            before = self._snapshot(paths)

            result = self._run(root, "--check")

            self.assertEqual(1, result.returncode, result)
            self.assertEqual("", result.stdout)
            self.assertIn("shared/VERSION", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(before, self._snapshot(paths))

    def test_cli_rejects_unknown_and_positional_arguments(self) -> None:
        """Return argparse-style usage errors without changing generated files."""
        for arguments in (("--unknown",), ("positional",), ("--check", "extra")):
            with self.subTest(arguments=arguments), self._temporary_repository() as root:
                paths = self._generated_paths(root)
                before = self._snapshot(paths)

                result = self._run(root, *arguments)

                self.assertEqual(2, result.returncode, result)
                self.assertEqual("", result.stdout)
                self.assertIn("usage:", result.stderr.lower())
                self.assertEqual(before, self._snapshot(paths))

    def test_independent_input_errors_are_aggregated_without_partial_updates(self) -> None:
        """Report independent source errors together before changing any output."""
        with self._temporary_repository() as root:
            skill = root / SHARED_SKILL_PATH
            skill.write_text(
                "<!-- claude-only:start -->\nunclosed\n",
                encoding="utf-8",
                newline="",
            )
            agent = root / "shared/agents/implementer.md"
            agent.write_text(
                agent.read_text(encoding="utf-8").replace(
                    'description = "Claude implementer"\n', "", 1
                ),
                encoding="utf-8",
                newline="",
            )
            before = self._snapshot(self._generated_paths(root))

            self._assert_validation_error(
                root,
                (
                    SHARED_SKILL_PATH.as_posix(),
                    "shared/agents/implementer.md",
                ),
                before,
            )

    def test_build_updates_only_files_with_changed_content(self) -> None:
        """Avoid rewriting equal files and repair only one deliberately stale output."""
        with self._temporary_repository() as root:
            first = self._run(root)
            self.assertEqual(0, first.returncode, first)
            paths = self._generated_paths(root)
            expected = self._snapshot(paths)
            known_mtime = 1_700_000_000_000_000_000
            stale_mtime = 1_600_000_000_000_000_000
            for path in paths:
                os.utime(path, ns=(known_mtime, known_mtime))

            unchanged = self._run(root)
            self.assertEqual(0, unchanged.returncode, unchanged)
            self.assertTrue(all(path.stat().st_mtime_ns == known_mtime for path in paths))

            stale_path = root / "plugins/codex/install/agents/implementer.toml"
            stale_path.write_text("stale\n", encoding="utf-8", newline="")
            os.utime(stale_path, ns=(stale_mtime, stale_mtime))
            repaired = self._run(root)

            self.assertEqual(0, repaired.returncode, repaired)
            self.assertEqual(expected, self._snapshot(paths))
            self.assertNotEqual(stale_mtime, stale_path.stat().st_mtime_ns)
            for path in paths:
                if path != stale_path:
                    self.assertEqual(known_mtime, path.stat().st_mtime_ns, path)

    def test_build_is_deterministic_utf8_lf_with_trailing_newlines(self) -> None:
        """Produce identical UTF-8 bytes with LF endings from identical inputs."""
        with self._temporary_repository() as first_root, self._temporary_repository() as second_root:
            roots = (first_root, second_root)
            snapshots = []
            for root in roots:
                result = self._run(root)
                self.assertEqual(0, result.returncode, result)
                paths = self._generated_paths(root)
                relative_bytes = {}
                for path in paths:
                    content = path.read_bytes()
                    content.decode("utf-8")
                    self.assertNotIn(b"\r\n", content, path)
                    self.assertTrue(content.endswith(b"\n"), path)
                    relative_bytes[path.relative_to(root)] = content
                snapshots.append(relative_bytes)

            self.assertEqual(snapshots[0], snapshots[1])

    def test_build_and_check_preserve_out_of_scope_files(self) -> None:
        """Leave interface metadata, docs, installer, and unrelated agents unchanged."""
        with self._temporary_repository() as root:
            outside_paths = [
                root / "README.md",
                root / "docs/plan.md",
                root / "plugins/codex/install/install-agents.sh",
                root / "plugins/codex/skills/impl-lead/agents/openai.yaml",
                (
                    root
                    / "plugins/codex/skills/impl-lead/references/local.md"
                ),
                root / "plugins/claude/agents/local-agent.md",
                root / "plugins/codex/install/agents/local-agent.toml",
            ]
            before = self._snapshot(outside_paths)

            build = self._run(root)
            check = self._run(root, "--check")

            self.assertEqual(0, build.returncode, build)
            self.assertEqual(0, check.returncode, check)
            self.assertEqual(before, self._snapshot(outside_paths))


if __name__ == "__main__":
    unittest.main()
