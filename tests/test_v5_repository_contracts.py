"""Protect the v5 agent surface and its Gunte ownership boundaries."""

from __future__ import annotations

import json
from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKERS = {
    "focused-implementer",
    "implementer",
    "senior-implementer",
    "expert-implementer",
}
REVIEWERS_WITH_BASH = {
    "responsibility-boundary-reviewer",
    "test-quality-reviewer",
    "over-engineering-reviewer",
    "security-side-effect-reviewer",
}
REVIEWERS_WITHOUT_BASH = {
    "plan-adversarial-reviewer",
    "writing-principles-reviewer",
}
REVIEWERS = REVIEWERS_WITH_BASH | REVIEWERS_WITHOUT_BASH
AGENTS = WORKERS | REVIEWERS
RETIRED = {
    "expert-selection-reviewer",
    "review-patch-refactorer",
    "writing-principles-refactorer",
}


class V5RepositoryContractsTest(unittest.TestCase):
    def _names(self, root: Path, suffix: str) -> set[str]:
        return {path.name.removesuffix(suffix) for path in root.glob(f"*{suffix}")}

    def test_v5_agent_inventory_is_exact_across_source_and_runtimes(self) -> None:
        self.assertEqual(AGENTS, self._names(ROOT / "shared/agents", ".md"))
        self.assertEqual(AGENTS, self._names(ROOT / "plugins/claude/agents", ".md"))
        self.assertEqual(
            AGENTS,
            self._names(ROOT / "plugins/codex/install/agents", ".toml"),
        )

    def test_gunte_owns_exact_v5_agent_manifest_and_version_sources(self) -> None:
        config = tomllib.loads((ROOT / "gunte.toml").read_text(encoding="utf-8"))
        expected = {f"shared/agents/{name}.md" for name in AGENTS} | {
            "declarations/claude/plugin.json",
            "declarations/codex/plugin.json",
            "shared/VERSION",
        }
        self.assertEqual(expected, set(config["sources"]["files"]))
        self.assertEqual("5.0.0", config["project"]["version"])

    def test_all_reviewers_are_read_only_with_the_established_claude_tool_split(self) -> None:
        for name in REVIEWERS:
            with self.subTest(name=name):
                source = (ROOT / f"shared/agents/{name}.md").read_text(encoding="utf-8")
                frontmatter = tomllib.loads(source.split("+++", 2)[1])
                self.assertEqual("read-only", frontmatter["codex"]["sandbox_mode"])
                if name in REVIEWERS_WITH_BASH:
                    self.assertCountEqual(
                        ["Read", "Grep", "Glob", "Bash"],
                        frontmatter["claude"]["tools"],
                    )
                    self.assertCountEqual(
                        ["Edit", "Write", "NotebookEdit"],
                        frontmatter["claude"]["disallowed_tools"],
                    )
                else:
                    self.assertCountEqual(
                        ["Read", "Grep", "Glob"],
                        frontmatter["claude"]["tools"],
                    )
                    self.assertCountEqual(
                        ["Edit", "Write", "NotebookEdit", "Bash"],
                        frontmatter["claude"]["disallowed_tools"],
                    )

        for name in WORKERS:
            with self.subTest(worker=name):
                source = (ROOT / f"shared/agents/{name}.md").read_text(encoding="utf-8")
                frontmatter = tomllib.loads(source.split("+++", 2)[1])
                self.assertNotIn("sandbox_mode", frontmatter["codex"])
                self.assertNotIn("tools", frontmatter["claude"])
                self.assertNotIn("disallowed_tools", frontmatter["claude"])

    def test_gunte_contract_registry_owns_worker_and_test_quality_invariants(self) -> None:
        registry = tomllib.loads((ROOT / "contracts.toml").read_text(encoding="utf-8"))["contracts"]
        worker_required = {
            "Acceptance Criteria",
            "scope",
            "責任境界",
            "依存",
            "再定義",
            "不足",
            "矛盾",
            "推測せず親",
            "最終受入",
        }
        worker_forbidden = {"委譲 mode", "固定 worktree", "段階 gate", "段階 commit"}
        for slice_name in (
            "focused-worker-boundary",
            "implementer-boundary",
            "senior-worker-boundary",
            "expert-worker-boundary",
        ):
            entries = [entry for entry in registry.values() if entry.get("slice") == slice_name]
            self.assertEqual(worker_required, {entry["pattern"] for entry in entries if entry["kind"] == "requires"})
            self.assertEqual(worker_forbidden, {entry["pattern"] for entry in entries if entry["kind"] == "forbids"})

        test_quality_entries = [
            entry for entry in registry.values() if entry.get("slice") == "gunte-test-quality"
        ]
        self.assertEqual(
            {
                "散文見出し",
                "独自Markdown parser",
                "空scope",
                "過広scope",
                "囮substring",
                "Gunte の生成、projection、serialization、predicate、byte drift",
                "structural test",
                "requires / forbids / order",
                "EVAL",
                "editorial review",
            },
            {entry["pattern"] for entry in test_quality_entries if entry["kind"] == "requires"},
        )

    def test_version_is_synchronized_and_retired_names_are_absent_from_runtimes(self) -> None:
        version = (ROOT / "shared/VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual("5.0.0", version)
        self.assertEqual(
            version,
            json.loads((ROOT / "declarations/claude/plugin.json").read_text(encoding="utf-8"))["version"],
        )
        self.assertEqual(
            version,
            json.loads((ROOT / "declarations/codex/plugin.json").read_text(encoding="utf-8"))["version"],
        )
        self.assertEqual(version, (ROOT / "plugins/codex/install/VERSION").read_text(encoding="utf-8").strip())

        runtime_roots = (
            ROOT / "plugins/claude/agents",
            ROOT / "plugins/codex/install/agents",
            ROOT / "plugins/claude/skills",
            ROOT / "plugins/codex/skills",
        )
        for runtime_root in runtime_roots:
            for path in runtime_root.rglob("*"):
                if path.is_file():
                    text = path.read_text(encoding="utf-8")
                    for retired in RETIRED:
                        self.assertNotIn(retired, text, path)


if __name__ == "__main__":
    unittest.main()
