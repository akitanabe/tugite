"""Protect the v5 agent surface and its Gunte ownership boundaries."""

from __future__ import annotations

import hashlib
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
WORKFLOW_SKILLS = {
    "impl-lead",
    "plan-craft",
    "review-loop",
    "work-unit-design",
}
CODEX_ONLY_SKILLS = {"install-custom-agents"}
RETIRED_SKILLS = {
    "feature-lead",
    "impl-delegate",
    "branch-design",
    "test-audit",
    "impl-lead-v5",
    "plan-craft-v5",
}
RETIRED_IMPLEMENTATION_PATHS = (
    "scripts/build_plugin_assets.py",
    "shared/terms.toml",
    "tests/build_plugin_assets_test_support.py",
)
EXPLICIT_CLAUDE_SKILLS = {"impl-lead", "plan-craft"}


class V5RepositoryContractsTest(unittest.TestCase):
    def _names(self, root: Path, suffix: str) -> set[str]:
        return {path.name.removesuffix(suffix) for path in root.glob(f"*{suffix}")}

    def _frontmatter_lines(self, text: str) -> list[str]:
        parts = text.split("---", 2)
        self.assertGreaterEqual(len(parts), 3)
        return parts[1].splitlines()

    def _exact_line_count(self, lines: list[str], key: str, value: str) -> int:
        scalar = f"{key}: {value}"
        return sum(line == scalar for line in lines)

    def _key_count(self, lines: list[str], key: str) -> int:
        return sum(line.lstrip().partition(":")[0] == key for line in lines)

    def _block_count(self, lines: list[str], first: str, second: str) -> int:
        return sum(
            lines[index] == first and lines[index + 1] == second
            for index in range(len(lines) - 1)
        )

    def test_v5_agent_inventory_is_exact_across_source_and_runtimes(self) -> None:
        self.assertEqual(AGENTS, self._names(ROOT / "shared/agents", ".md"))
        self.assertEqual(AGENTS, self._names(ROOT / "plugins/claude/agents", ".md"))
        self.assertEqual(
            AGENTS,
            self._names(ROOT / "plugins/codex/install/agents", ".toml"),
        )

    def test_v5_workflow_skill_inventory_is_exact_across_source_and_runtimes(self) -> None:
        self.assertEqual(
            WORKFLOW_SKILLS,
            {path.name for path in (ROOT / "shared/skill").iterdir() if path.is_dir()},
        )
        self.assertEqual(
            WORKFLOW_SKILLS,
            {path.name for path in (ROOT / "plugins/claude/skills").iterdir() if path.is_dir()},
        )
        self.assertEqual(
            WORKFLOW_SKILLS | CODEX_ONLY_SKILLS,
            {path.name for path in (ROOT / "plugins/codex/skills").iterdir() if path.is_dir()},
        )
        for name in WORKFLOW_SKILLS:
            with self.subTest(source=name):
                self.assertEqual(
                    {"SKILL.md"},
                    {
                        path.relative_to(ROOT / f"shared/skill/{name}").as_posix()
                        for path in (ROOT / f"shared/skill/{name}").rglob("*")
                        if path.is_file()
                    },
                )

        declarations_root = ROOT / "declarations/codex/skills"
        self.assertEqual(
            WORKFLOW_SKILLS,
            {path.name for path in declarations_root.iterdir() if path.is_dir()},
        )
        self.assertEqual(
            {f"{name}/openai.yaml" for name in WORKFLOW_SKILLS},
            {
                path.relative_to(declarations_root).as_posix()
                for path in declarations_root.rglob("*")
                if path.is_file()
            },
        )
        for name in WORKFLOW_SKILLS:
            with self.subTest(claude=name):
                self.assertEqual(
                    {"SKILL.md"},
                    {
                        path.relative_to(ROOT / f"plugins/claude/skills/{name}").as_posix()
                        for path in (ROOT / f"plugins/claude/skills/{name}").rglob("*")
                        if path.is_file()
                    },
                )
            with self.subTest(codex=name):
                self.assertEqual(
                    {"SKILL.md", "agents/openai.yaml"},
                    {
                        path.relative_to(ROOT / f"plugins/codex/skills/{name}").as_posix()
                        for path in (ROOT / f"plugins/codex/skills/{name}").rglob("*")
                        if path.is_file()
                    },
                )

    def test_retired_workflow_skill_paths_are_absent(self) -> None:
        roots = (
            ROOT / "shared/skill",
            ROOT / "declarations/codex/skills",
            ROOT / "plugins/claude/skills",
            ROOT / "plugins/codex/skills",
        )
        for root in roots:
            for name in RETIRED_SKILLS:
                with self.subTest(root=root, name=name):
                    self.assertFalse((root / name).exists())

    def test_retired_implementation_paths_are_absent(self) -> None:
        for relative_path in RETIRED_IMPLEMENTATION_PATHS:
            with self.subTest(path=relative_path):
                self.assertFalse((ROOT / relative_path).exists())
        self.assertEqual([], list((ROOT / "tests").glob("test_build_plugin_assets*.py")))

    def test_gunte_owns_exact_v5_source_inventory(self) -> None:
        config = tomllib.loads((ROOT / "gunte.toml").read_text(encoding="utf-8"))
        expected = {f"shared/agents/{name}.md" for name in AGENTS} | {
            "declarations/claude/plugin.json",
            "declarations/codex/plugin.json",
            "shared/VERSION",
        } | {f"shared/skill/{name}/SKILL.md" for name in WORKFLOW_SKILLS} | {
            f"declarations/codex/skills/{name}/openai.yaml" for name in WORKFLOW_SKILLS
        }
        self.assertEqual(expected, set(config["sources"]["files"]))
        self.assertEqual("5.0.0", config["project"]["version"])

    def test_gunte_owns_workflow_skills_and_codex_metadata(self) -> None:
        config = tomllib.loads((ROOT / "gunte.toml").read_text(encoding="utf-8"))

        claude_skill_rules = [
            rule
            for rule in config["targets"]["claude"]["rules"]
            if rule["match"] == "shared/skill/*/SKILL.md"
        ]
        self.assertEqual(
            [{
                "match": "shared/skill/*/SKILL.md",
                "path": "skills/{1}/SKILL.md",
                "profile": "markdown+yaml-frontmatter-v1",
                "header": "<!-- Generated from shared/. Do not edit directly. -->",
            }],
            claude_skill_rules,
        )
        codex_skill_rules = [
            rule
            for rule in config["targets"]["codex"]["rules"]
            if rule["match"] in {
                "shared/skill/*/SKILL.md",
                "declarations/codex/skills/*/openai.yaml",
            }
        ]
        self.assertCountEqual(
            [
                {
                    "match": "shared/skill/*/SKILL.md",
                    "path": "skills/{1}/SKILL.md",
                    "profile": "markdown+yaml-frontmatter-v1",
                    "header": "<!-- Generated from shared/. Do not edit directly. -->",
                },
                {
                    "match": "declarations/codex/skills/*/openai.yaml",
                    "path": "skills/{1}/agents/openai.yaml",
                    "profile": "markdown-v1",
                },
            ],
            codex_skill_rules,
        )

    def test_codex_skill_metadata_has_one_unambiguous_boolean_policy_scalar(self) -> None:
        implicit_skills = {"review-loop", "work-unit-design"}
        for name in WORKFLOW_SKILLS:
            with self.subTest(name=name):
                source = ROOT / f"declarations/codex/skills/{name}/openai.yaml"
                expected = "true" if name in implicit_skills else "false"
                text = source.read_text(encoding="utf-8")
                lines = text.splitlines()
                self.assertEqual(1, self._key_count(lines, "policy"), source)
                self.assertEqual(1, self._key_count(lines, "allow_implicit_invocation"), source)
                self.assertEqual(
                    1,
                    self._block_count(
                        lines,
                        "policy:",
                        f"  allow_implicit_invocation: {expected}",
                    ),
                    source,
                )

    def test_claude_skill_frontmatter_has_bounded_invocation_policy(self) -> None:
        for name in WORKFLOW_SKILLS:
            with self.subTest(name=name):
                path = ROOT / f"plugins/claude/skills/{name}/SKILL.md"
                lines = self._frontmatter_lines(path.read_text(encoding="utf-8"))
                self.assertEqual(1, self._key_count(lines, "name"), path)
                self.assertEqual(1, self._exact_line_count(lines, "name", name), path)
                if name in EXPLICIT_CLAUDE_SKILLS:
                    self.assertEqual(1, self._key_count(lines, "disable-model-invocation"), path)
                    self.assertEqual(1, self._exact_line_count(lines, "disable-model-invocation", "true"), path)
                else:
                    self.assertEqual(0, self._key_count(lines, "disable-model-invocation"), path)

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

        retired_skill_entries = {
            entry["pattern"]: entry
            for name, entry in registry.items()
            if name.endswith("-skill") and entry["kind"] == "forbids"
        }
        self.assertEqual(RETIRED_SKILLS, set(retired_skill_entries))
        for pattern, entry in retired_skill_entries.items():
            with self.subTest(pattern=pattern):
                self.assertEqual(["claude", "codex"], entry["applies_to"])

    def test_sliced_contract_ids_are_stable_content_hashes(self) -> None:
        registry = tomllib.loads((ROOT / "contracts.toml").read_text(encoding="utf-8"))["contracts"]
        for name, entry in registry.items():
            if "slice" not in entry:
                continue
            canonical = "\0".join(
                (
                    entry["kind"],
                    entry["slice"],
                    entry["pattern"],
                    ",".join(sorted(entry["applies_to"])),
                )
            )
            digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:8]
            with self.subTest(contract=name):
                self.assertTrue(name.endswith(f"-{digest}"), name)

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
