"""Protect the v5 agent surface and its Gunte ownership boundaries."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
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
ADVISORS = {"plan-quality-advisor"}
REVIEWERS = REVIEWERS_WITH_BASH | REVIEWERS_WITHOUT_BASH
READ_ONLY_AGENTS = REVIEWERS | ADVISORS
READ_ONLY_WITHOUT_BASH = REVIEWERS_WITHOUT_BASH
AGENTS = WORKERS | READ_ONLY_AGENTS
RETIRED = {
    "expert-selection-reviewer",
    "review-patch-refactorer",
    "writing-principles-refactorer",
}
WORKFLOW_SKILLS = {
    "impl-lead",
    "plan-craft",
    "proposal",
    "review-loop",
    "structural-health-gate",
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
INTERNAL_CLAUDE_SKILLS = {"proposal", "structural-health-gate", "work-unit-design"}
PUBLIC_SKILLS = {"impl-lead", "plan-craft", "review-loop"}
INTERNAL_SKILLS = {"proposal", "structural-health-gate", "work-unit-design"}
RELEASE_READMES = (
    ROOT / "README.md",
    ROOT / "plugins/claude/README.md",
    ROOT / "plugins/codex/README.md",
)
EXPECTED_PLUGIN_KEYWORDS = [
    "multi-agent",
    "software-development",
    "planning",
    "delegation",
    "code-review",
    "tdd",
]
KERNELS = {
    "necessity-kernel": {
        "identity": "necessity-kernel-v1",
    }
}
KERNEL_INJECTION_CONTRACT_HEADING = "## Kernel injection contract"
KERNEL_INJECTION_CONTRACT_MARKERS = (
    "読み込み",
    "検証",
    "注入",
    "解決しない",
    "判定基準",
    "必要な周辺 context",
    "identity",
    "必要本文",
    "推測",
    "依存解決",
    "注入順序",
    "裁定",
    "round budget",
    "termination",
)


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

    def _section_body(self, text: str, heading: str) -> str:
        """Extract one finite Markdown section without asserting on unrelated prose."""
        self.assertEqual(1, text.count(heading), heading)
        body = text.split(heading, 1)[1]
        next_heading = body.find("\n## ")
        if next_heading >= 0:
            body = body[:next_heading]
        return body

    def _anchored_section_body(self, text: str, heading: str) -> str:
        """Extract a Markdown section by its heading line, excluding inline references."""
        lines = text.splitlines()
        starts = [index for index, line in enumerate(lines) if line == heading]
        self.assertEqual(1, len(starts), heading)
        body = lines[starts[0] + 1 :]
        next_heading = next(
            (index for index, line in enumerate(body) if line.startswith("## ")),
            len(body),
        )
        return "\n".join(body[:next_heading])

    def _labeled_field(self, section: str, label: str) -> str:
        """Extract one uniquely labeled top-level Markdown field from a finite section."""
        prefix = f"- **{label}**:"
        values = [line[len(prefix) :].strip() for line in section.splitlines() if line.startswith(prefix)]
        self.assertEqual(1, len(values), label)
        return values[0]

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
            "shared/necessity-kernel.md",
            "shared/VERSION",
        } | {f"shared/skill/{name}/SKILL.md" for name in WORKFLOW_SKILLS} | {
            f"declarations/codex/skills/{name}/openai.yaml" for name in WORKFLOW_SKILLS
        }
        self.assertEqual(expected, set(config["sources"]["files"]))
        self.assertEqual("5.1.0", config["project"]["version"])

    def test_kernel_injection_contract_is_declared_once_and_names_every_kernel(self) -> None:
        contract = self._section_body(
            (ROOT / "CLAUDE.md").read_text(encoding="utf-8"),
            KERNEL_INJECTION_CONTRACT_HEADING,
        )
        for marker in KERNEL_INJECTION_CONTRACT_MARKERS:
            with self.subTest(marker=marker):
                self.assertIn(marker, contract)
        for name, kernel in KERNELS.items():
            with self.subTest(kernel=name):
                self.assertIn(kernel["identity"], contract)
        pointer = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Kernel injection contract", pointer)
        self.assertIn("CLAUDE.md", pointer)
        self.assertNotIn(KERNEL_INJECTION_CONTRACT_HEADING, pointer)

    def test_necessity_kernel_has_one_shared_reference_target_per_runtime(self) -> None:
        config = tomllib.loads((ROOT / "gunte.toml").read_text(encoding="utf-8"))
        expected_rule = {
            "match": "shared/necessity-kernel.md",
            "path": "references/necessity-kernel.md",
            "profile": "markdown-v1",
            "header": "<!-- Generated from shared/. Do not edit directly. -->",
        }
        for target in ("claude", "codex"):
            with self.subTest(target=target):
                source_owners = [
                    rule
                    for rule in config["targets"][target]["rules"]
                    if rule.get("match") == "shared/necessity-kernel.md"
                ]
                target_owners = [
                    rule
                    for rule in config["targets"][target]["rules"]
                    if rule.get("path") == "references/necessity-kernel.md"
                ]
                self.assertEqual(1, len(source_owners))
                self.assertEqual(1, len(target_owners))
                self.assertEqual(
                    [expected_rule],
                    source_owners,
                )
                generated = ROOT / f"plugins/{target}/references/necessity-kernel.md"
                self.assertTrue(generated.is_file(), generated)
                self.assertIn("# Necessity Kernel v1", generated.read_text(encoding="utf-8"))
                self.assertEqual(
                    {"references/necessity-kernel.md"},
                    {
                        path.relative_to(ROOT / f"plugins/{target}").as_posix()
                        for path in (ROOT / f"plugins/{target}").rglob("*")
                        if path.is_file()
                        and path.relative_to(ROOT / f"plugins/{target}").as_posix().startswith("references/")
                    },
                )

    def test_necessity_kernel_role_mapping_is_local_and_excludes_structural_gate(self) -> None:
        kernel = (ROOT / "shared/necessity-kernel.md").read_text(encoding="utf-8")
        self.assertIn("plan-adversarial-reviewer", kernel)
        self.assertIn("over-engineering-reviewer", kernel)
        self.assertIn("plan-quality-advisor", kernel)
        self.assertIn("proposal", kernel)
        self.assertIn("review-loop", kernel)
        self.assertIn("structural-health-gate", kernel)
        self.assertIn("適用外", kernel)
        self.assertNotIn("## role-specific mapping", kernel)
        for forbidden in ("necessity_verdict", "necessity verdict", "rounds", "termination", "induced-loop"):
            self.assertNotIn(forbidden, kernel)

        required_markers = {
            "plan-adversarial-reviewer": ("成立", "必要性", "Failure", "Minimum Resolution Condition", "判定基準", "identity", "適用範囲", "不足"),
            "over-engineering-reviewer": ("Deletion Test", "remaining witness", "大きさ", "判定基準", "identity", "適用範囲", "不足"),
            "plan-quality-advisor": ("question_or_option", "判断不能", "重複", "判定基準", "identity", "適用範囲", "不足"),
            "proposal": ("adopted", "rejected", "unresolved", "plan-quality-advisor", "../../references/necessity-kernel.md", "判定基準", "必要な周辺 context", "identity", "Task Contract", "不足"),
            "review-loop": ("採用", "却下", "範囲外", "判断保留", "人間確認", "plan-adversarial-reviewer", "over-engineering-reviewer", "../../references/necessity-kernel.md", "判定基準", "必要な周辺 context", "identity", "Task Contract", "不足"),
        }
        allowed_paths = {
            "shared/agents/plan-adversarial-reviewer.md",
            "shared/agents/over-engineering-reviewer.md",
            "shared/agents/plan-quality-advisor.md",
            "shared/skill/proposal/SKILL.md",
            "shared/skill/review-loop/SKILL.md",
            "plugins/claude/agents/plan-adversarial-reviewer.md",
            "plugins/claude/agents/over-engineering-reviewer.md",
            "plugins/claude/agents/plan-quality-advisor.md",
            "plugins/claude/skills/proposal/SKILL.md",
            "plugins/claude/skills/review-loop/SKILL.md",
            "plugins/codex/install/agents/plan-adversarial-reviewer.toml",
            "plugins/codex/install/agents/over-engineering-reviewer.toml",
            "plugins/codex/install/agents/plan-quality-advisor.toml",
            "plugins/codex/skills/proposal/SKILL.md",
            "plugins/codex/skills/review-loop/SKILL.md",
        }
        for root in (
            ROOT / "shared/agents",
            ROOT / "shared/skill",
            ROOT / "plugins/claude/agents",
            ROOT / "plugins/claude/skills",
            ROOT / "plugins/codex/install/agents",
            ROOT / "plugins/codex/skills",
        ):
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                if "necessity-kernel" in path.read_text(encoding="utf-8"):
                    relative = path.relative_to(ROOT).as_posix()
                    self.assertIn(relative, allowed_paths)
        for role, markers in required_markers.items():
            section_heading = "## necessity-kernel v1 の mapping" if role not in {"proposal", "review-loop"} else "## necessity-kernel v1 の parent mapping"
            for relative_path in (
                f"shared/agents/{role}.md" if role.endswith("reviewer") or role.endswith("advisor") else f"shared/skill/{role}/SKILL.md",
                f"plugins/claude/agents/{role}.md" if role.endswith("reviewer") or role.endswith("advisor") else f"plugins/claude/skills/{role}/SKILL.md",
                f"plugins/codex/install/agents/{role}.toml" if role.endswith("reviewer") or role.endswith("advisor") else f"plugins/codex/skills/{role}/SKILL.md",
            ):
                with self.subTest(role=role, path=relative_path):
                    text = self._section_body((ROOT / relative_path).read_text(encoding="utf-8"), section_heading)
                    for marker in markers:
                        self.assertIn(marker, text)
                    if role in {"proposal", "review-loop"}:
                        self.assertLess(text.index("../../references/necessity-kernel.md"), text.index("判定基準"))
                    if role not in {"proposal", "review-loop"}:
                        self.assertNotIn("necessity_kernel_handoff", text)
                        self.assertNotIn("../../references/necessity-kernel.md", text)
        for relative_path in (
            "shared/necessity-kernel.md",
            "shared/skill/proposal/SKILL.md",
            "shared/skill/review-loop/SKILL.md",
            "evals/workflow-decision-corpus.md",
        ):
            self.assertNotIn("necessity_kernel_handoff", (ROOT / relative_path).read_text(encoding="utf-8"))
        for relative_path in allowed_paths:
            self.assertNotIn("necessity_kernel_handoff", (ROOT / relative_path).read_text(encoding="utf-8"))
        for target in ("claude", "codex"):
            self.assertNotIn(
                "necessity_kernel_handoff",
                (ROOT / f"plugins/{target}/references/necessity-kernel.md").read_text(encoding="utf-8"),
            )
        for relative_path in (
            "shared/skill/structural-health-gate/SKILL.md",
            "plugins/claude/skills/structural-health-gate/SKILL.md",
            "plugins/codex/skills/structural-health-gate/SKILL.md",
        ):
            self.assertNotIn("necessity-kernel", (ROOT / relative_path).read_text(encoding="utf-8"))

    def test_necessity_kernel_preserves_existing_role_return_fields_and_parent_verdict_boundary(self) -> None:
        role_return_sections = {
            "plan-adversarial-reviewer": (
                "## 返却形式",
                (
                    "指摘ID",
                    "対象（プラン文書の節または AC id）",
                    "類型",
                    "判定（`軽微` / `修正推奨` / `修正必須`）",
                    "具体的な失敗経路",
                    "根拠。",
                    "解消を確認する条件",
                ),
            ),
            "over-engineering-reviewer": (
                "## 返却形式",
                (
                    "指摘ID",
                    "対象ファイルと該当箇所。",
                    "過剰の類型",
                    "除去しても失われる AC・制約が無いと判断した根拠",
                    "取り除いた後も残る実装または検証とそれが担保する AC",
                    "外部から観測可能な振る舞いへの影響有無",
                    "局所的かつ振る舞いを変えずに取り除けるか",
                    "推奨する修正先",
                ),
            ),
        }
        role_paths = {
            role: (
                f"shared/agents/{role}.md",
                f"plugins/claude/agents/{role}.md",
                f"plugins/codex/install/agents/{role}.toml",
            )
            for role in (
                "plan-adversarial-reviewer",
                "over-engineering-reviewer",
                "plan-quality-advisor",
            )
        }
        for role, (heading, expected_fields) in role_return_sections.items():
            for relative_path in role_paths[role]:
                with self.subTest(role=role, path=relative_path):
                    section = self._anchored_section_body(
                        (ROOT / relative_path).read_text(encoding="utf-8"), heading
                    )
                    fields = tuple(
                        line[2:].strip()
                        for line in section.splitlines()
                        if line.startswith("- ")
                    )
                    self.assertEqual(expected_fields, fields)

        advisor_field_pattern = re.compile(r"各 insight は (.+?) を持ち", re.DOTALL)
        for relative_path in role_paths["plan-quality-advisor"]:
            with self.subTest(role="plan-quality-advisor", path=relative_path):
                section = self._anchored_section_body(
                    (ROOT / relative_path).read_text(encoding="utf-8"), "## 返却 Data"
                )
                declaration = advisor_field_pattern.search(section)
                self.assertIsNotNone(declaration)
                self.assertEqual(
                    ("id", "observation", "evidence", "impact", "question_or_option"),
                    tuple(re.findall(r"`([^`]+)`", declaration.group(1))),
                )

        for role, paths in role_paths.items():
            for relative_path in paths:
                with self.subTest(role=role, path=relative_path):
                    text = (ROOT / relative_path).read_text(encoding="utf-8")
                    for forbidden in ("necessity_verdict", "necessity_status", "necessity_decision", "necessity_field", "necessity_result"):
                        self.assertNotIn(forbidden, text)

        for role in ("proposal", "review-loop"):
            for relative_path in (
                f"shared/skill/{role}/SKILL.md",
                f"plugins/claude/skills/{role}/SKILL.md",
                f"plugins/codex/skills/{role}/SKILL.md",
            ):
                with self.subTest(role=role, path=relative_path):
                    section = self._section_body(
                        (ROOT / relative_path).read_text(encoding="utf-8"),
                        "## necessity-kernel v1 の parent mapping",
                    )
                    self.assertIn("既存語彙へ写像", section)
                    self.assertIn("新verdict fieldではない", section)
                    self.assertIn("round budget", section)
                    self.assertIn("termination", section)
                    self.assertIn("直結させない", section)
                    self.assertNotIn("necessity_kernel_handoff", section)

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

    def test_impl_lead_defines_run_owned_default_isolation_contract(self) -> None:
        source = (ROOT / "shared/skill/impl-lead/SKILL.md").read_text(encoding="utf-8")
        heading = "### Default run-owned checkout"
        self.assertEqual(1, source.count(heading))
        self.assertLess(source.index(heading), source.index("\n## Route and execution order"))

    def test_codex_skill_metadata_has_one_unambiguous_boolean_policy_scalar(self) -> None:
        implicit_skills = {
            "proposal",
            "review-loop",
            "structural-health-gate",
            "work-unit-design",
        }
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

    def test_codex_plugin_default_prompts_expose_public_review_loop(self) -> None:
        manifest = json.loads((ROOT / "declarations/codex/plugin.json").read_text(encoding="utf-8"))
        self.assertIn(
            "Use $review-loop to review an immutable artifact snapshot with bounded rounds and caller-owned acceptance evidence.",
            manifest["interface"]["defaultPrompt"],
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
                if name in INTERNAL_CLAUDE_SKILLS:
                    self.assertEqual(1, self._key_count(lines, "user-invocable"), path)
                    self.assertEqual(1, self._exact_line_count(lines, "user-invocable", "false"), path)
                else:
                    self.assertEqual(0, self._key_count(lines, "user-invocable"), path)

    def test_read_only_agents_have_the_established_claude_tool_split(self) -> None:
        for name in READ_ONLY_AGENTS:
            with self.subTest(name=name):
                source = (ROOT / f"shared/agents/{name}.md").read_text(encoding="utf-8")
                frontmatter = tomllib.loads(source.split("+++", 2)[1])
                self.assertEqual("read-only", frontmatter["codex"]["sandbox_mode"])
                if name not in READ_ONLY_WITHOUT_BASH:
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

    def test_plan_quality_advisor_uses_opus_high_and_keeps_codex_read_only(self) -> None:
        source = (ROOT / "shared/agents/plan-quality-advisor.md").read_text(encoding="utf-8")
        frontmatter = tomllib.loads(source.split("+++", 2)[1])
        self.assertEqual("opus", frontmatter["claude"]["model"])
        self.assertEqual("high", frontmatter["claude"]["effort"])
        self.assertEqual("read-only", frontmatter["codex"]["sandbox_mode"])

    def test_candidate_producer_and_handoff_contract_registry_is_exact(self) -> None:
        registry = tomllib.loads((ROOT / "contracts.toml").read_text(encoding="utf-8"))["contracts"]
        expected = {
            "candidate-producer-boundary-requires-222dd897": (
                "requires",
                "candidate-producer-boundary",
                "candidate snapshot",
            ),
            "candidate-producer-boundary-requires-784e1e12": (
                "requires",
                "candidate-producer-boundary",
                "stop-incomplete",
            ),
            "candidate-producer-boundary-requires-8802cc93": (
                "requires",
                "candidate-producer-boundary",
                "adopted",
            ),
            "candidate-producer-boundary-requires-aab3ab4d": (
                "requires",
                "candidate-producer-boundary",
                "rejected",
            ),
            "candidate-producer-boundary-requires-a5e6a77d": (
                "requires",
                "candidate-producer-boundary",
                "unresolved",
            ),
            "candidate-producer-boundary-requires-8a5814e1": (
                "requires",
                "candidate-producer-boundary",
                "caller-owned parent",
            ),
            "candidate-producer-boundary-requires-8c449450": (
                "requires",
                "candidate-producer-boundary",
                "後段工程を選択・起動せず",
            ),
            "candidate-producer-boundary-requires-d1f15769": (
                "requires",
                "candidate-producer-boundary",
                "advisor insight を自動採用せず",
            ),
            "candidate-producer-boundary-requires-318a8b6a": (
                "requires",
                "candidate-producer-boundary",
                "planner は各 insight を一次情報と要求に照らして次の台帳へ裁定する",
            ),
            "candidate-producer-boundary-requires-e5df9a7c": (
                "requires",
                "candidate-producer-boundary",
                "具体的な品質向上が残る間だけ bounded",
            ),
            "candidate-producer-boundary-requires-a1fa509f": (
                "requires",
                "candidate-producer-boundary",
                "人間の選択が必要な `unresolved` が残る場合は、勝手に進めず判断点・evidence・必要な問いを付けて `stop-incomplete` を返す。",
            ),
            "plan-quality-advisor-boundary-requires-b920a922": (
                "requires",
                "plan-quality-advisor-boundary",
                "read-only advisor",
            ),
            "plan-quality-advisor-boundary-requires-3d8191da": (
                "requires",
                "plan-quality-advisor-boundary",
                "candidate を直接修正せず",
            ),
            "plan-quality-advisor-boundary-requires-2d3924e4": (
                "requires",
                "plan-quality-advisor-boundary",
                "第二の planner にならない",
            ),
            "plan-quality-advisor-boundary-requires-af585f71": (
                "requires",
                "plan-quality-advisor-boundary",
                "後段を起動せず",
            ),
            "plan-quality-advisor-boundary-requires-8bb2deb8": (
                "requires",
                "plan-quality-advisor-boundary",
                "採否を決めず",
            ),
            "plan-quality-advisor-boundary-requires-e875fc13": (
                "requires",
                "plan-quality-advisor-boundary",
                "最終受入を行いません",
            ),
            "plan-craft-proposal-handoff-requires-4fc3816c": (
                "requires",
                "plan-craft-proposal-handoff",
                "candidate snapshot",
            ),
            "plan-craft-proposal-handoff-requires-646de56d": (
                "requires",
                "plan-craft-proposal-handoff",
                "stop-incomplete",
            ),
            "plan-craft-proposal-handoff-requires-361ac902": (
                "requires",
                "plan-craft-proposal-handoff",
                "caller-owned parent",
            ),
            "plan-craft-proposal-before-review-loop": (
                "order",
                None,
                None,
            ),
        }
        contract_names = {
            name
            for name, entry in registry.items()
            if entry.get("slice") in {
                "candidate-producer-boundary",
                "plan-quality-advisor-boundary",
                "plan-craft-proposal-handoff",
            }
            or name == "plan-craft-proposal-before-review-loop"
        }
        self.assertEqual(set(expected), contract_names)
        for name, (kind, slice_name, pattern) in expected.items():
            with self.subTest(contract=name):
                entry = registry[name]
                self.assertEqual(kind, entry["kind"])
                if kind == "requires":
                    self.assertEqual(
                        {"kind", "slice", "pattern", "applies_to"},
                        set(entry),
                    )
                    self.assertEqual(slice_name, entry["slice"])
                    self.assertEqual(pattern, entry["pattern"])
                else:
                    self.assertEqual(
                        {"kind", "before", "after", "applies_to"},
                        set(entry),
                    )
                    self.assertEqual("proposal-start", entry["before"])
                    self.assertEqual("review-loop-handoff", entry["after"])
                self.assertEqual(["claude", "codex"], entry["applies_to"])

    def test_structural_health_gate_contract_registry_is_exact(self) -> None:
        registry = tomllib.loads((ROOT / "contracts.toml").read_text(encoding="utf-8"))["contracts"]
        expected = {
            "structural-health-gate-caller-context-requires-ec2ccc46": (
                "requires", "structural-health-gate-caller-context", "`caller_context` Data"
            ),
            "structural-health-gate-caller-context-requires-d624e872": (
                "requires", "structural-health-gate-caller-context", "`workflow_family`: `proposal-family`"
            ),
            "structural-health-gate-caller-context-requires-4fbc98a7": (
                "requires", "structural-health-gate-caller-context", "`invocation`: `explicit-public-parent`"
            ),
            "structural-health-gate-caller-context-requires-4a432b13": (
                "requires", "structural-health-gate-caller-context", "context 不成立"
            ),
            "structural-health-gate-caller-context-requires-d50aa7cd": (
                "requires", "structural-health-gate-caller-context", "assessment を開始せず"
            ),
            "structural-health-gate-caller-context-requires-78715640": (
                "requires", "structural-health-gate-caller-context", "`stop-incomplete`"
            ),
            "structural-health-gate-caller-context-forbids-3cc1f92b": (
                "forbids", "structural-health-gate-caller-context", "`producer_context`"
            ),
            "structural-health-gate-caller-context-forbids-af4f2954": (
                "forbids", "structural-health-gate-caller-context", "`return target`"
            ),
            "structural-health-gate-caller-context-forbids-c500195c": (
                "forbids", "structural-health-gate-caller-context", "`next skill`"
            ),
            "structural-health-gate-caller-context-forbids-42aaefd9": (
                "forbids", "structural-health-gate-caller-context", "`origin`"
            ),
            "structural-health-gate-boundary-requires-08c3b623": (
                "requires", "structural-health-gate-boundary", "duplicated source of truth"
            ),
            "structural-health-gate-boundary-requires-765af3a3": (
                "requires",
                "structural-health-gate-boundary",
                "明示起動された proposal-family public workflow parent",
            ),
            "structural-health-gate-boundary-requires-f08a5bbf": (
                "requires", "structural-health-gate-boundary", "`location`"
            ),
            "structural-health-gate-boundary-requires-89d00b8c": (
                "requires", "structural-health-gate-boundary", "`non_local_reason`"
            ),
            "structural-health-gate-boundary-requires-57c9e9cb": (
                "requires", "structural-health-gate-boundary", "`predicted_amplification`"
            ),
            "structural-health-gate-boundary-requires-2e003c43": (
                "requires", "structural-health-gate-boundary", "`predicted_churn`"
            ),
            "structural-health-gate-boundary-requires-0891a60b": (
                "requires",
                "structural-health-gate-boundary",
                "public workflow parent が最終的な `pass` / `return` / `stop-incomplete` を決める",
            ),
            "structural-health-gate-boundary-requires-f63294d0": (
                "requires", "structural-health-gate-boundary", "成果物を再設計・直接編集しない"
            ),
            "structural-health-gate-boundary-requires-2a8ee78f": (
                "requires",
                "structural-health-gate-boundary",
                "長さ、複雑さ、finding 数だけを理由に `return` しない",
            ),
            "structural-health-gate-boundary-requires-d19bb5e9": (
                "requires", "structural-health-gate-boundary", "`insufficient-evidence`"
            ),
            "structural-health-gate-boundary-requires-4c89c356": (
                "requires", "structural-health-gate-boundary", "assessment Data"
            ),
            "structural-health-gate-boundary-forbids-21466849": (
                "forbids", "structural-health-gate-boundary", "gate が最終判断する"
            ),
            "structural-health-gate-boundary-forbids-fad0c88b": (
                "forbids", "structural-health-gate-boundary", "gate が成果物を直接編集する"
            ),
            "plan-craft-structural-health-handoff-requires-8b8aab7f": (
                "requires", "plan-craft-structural-health-handoff", "`structural-health-gate`"
            ),
            "plan-craft-structural-health-handoff-requires-945ff3f4": (
                "requires", "plan-craft-structural-health-handoff", "proposal を再実行"
            ),
            "plan-craft-structural-health-handoff-requires-cd8aca82": (
                "requires", "plan-craft-structural-health-handoff", "再 proposal 後"
            ),
            "plan-craft-structural-health-handoff-requires-bdaffd8e": (
                "requires", "plan-craft-structural-health-handoff", "`stop-incomplete`"
            ),
            "plan-craft-structural-health-handoff-requires-a4f20d25": (
                "requires",
                "plan-craft-structural-health-handoff",
                "gate assessment 1回を1 `round` と数える",
            ),
            "plan-craft-structural-health-handoff-requires-f2a5ac96": (
                "requires",
                "plan-craft-structural-health-handoff",
                "`rounds.limit` は下限1の ceiling としてユーザー指定を優先し、未指定時は親が loop 開始時に決定して固定する",
            ),
            "plan-craft-structural-health-handoff-requires-6a8f7d7d": (
                "requires",
                "plan-craft-structural-health-handoff",
                "`pass` は上限未消化でも直ちに `review-loop` へ進む",
            ),
            "plan-craft-structural-health-handoff-requires-80636f85": (
                "requires",
                "plan-craft-structural-health-handoff",
                "`return` は gate evidence だけを入力に proposal を再実行し、別 identity の candidate を再評価する",
            ),
            "plan-craft-structural-health-handoff-requires-cb0fd10c": (
                "requires",
                "plan-craft-structural-health-handoff",
                "`rounds.limit` 到達 round の `return` は `stop-incomplete` とする",
            ),
            "plan-craft-structural-health-handoff-requires-36ddb773": (
                "requires",
                "plan-craft-structural-health-handoff",
                "`insufficient-evidence` は proposal を再実行せず `stop-incomplete` とする",
            ),
            "plan-craft-structural-health-handoff-requires-9f964bf1": (
                "requires",
                "plan-craft-structural-health-handoff",
                "structural gate budget と review-loop budget は別 Data とし、gate round を `adversarial_review_count` 等へ加算しない",
            ),
            "plan-craft-structural-health-handoff-requires-f6271de3": (
                "requires",
                "plan-craft-structural-health-handoff",
                "`rounds.limit=1` の round 1 `return` は proposal を再実行せず `stop-incomplete` とする",
            ),
            "plan-craft-structural-health-handoff-requires-333e4dc6": (
                "requires",
                "plan-craft-structural-health-handoff",
                "`rounds.limit` が1未満なら、親は値を補正・既定値置換せず受理せず、理由を添えて `stop-incomplete` とする",
            ),
            "plan-craft-structural-health-handoff-requires-06b909ed": (
                "requires",
                "plan-craft-structural-health-handoff",
                "`rounds.limit` が1未満の入力では gate assessment、proposal の再実行、`review-loop` を起動しない",
            ),
            "review-loop-structural-boundary-requires-0c775c51": (
                "requires", "review-loop-structural-boundary", "局所的な構造欠陥を事前解消"
            ),
            "review-loop-structural-boundary-requires-212e71a7": (
                "requires",
                "review-loop-structural-boundary",
                "自動で `structural-health-gate` または candidate producer へ逆走しない",
            ),
            "review-loop-structural-boundary-requires-55ef9a2e": (
                "requires", "review-loop-structural-boundary", "`stop-incomplete`"
            ),
        }
        order_expected = {
            "plan-craft-proposal-before-structural-health-gate": (
                "proposal-start", "structural-health-gate-start"
            ),
            "plan-craft-structural-health-gate-before-review-loop": (
                "structural-health-gate-start", "review-loop-handoff"
            ),
        }
        selected = {
            name: entry
            for name, entry in registry.items()
            if entry.get("slice") in {
                "structural-health-gate-boundary",
                "structural-health-gate-caller-context",
                "plan-craft-structural-health-handoff",
                "review-loop-structural-boundary",
            }
            or name in order_expected
        }
        self.assertEqual(set(expected) | set(order_expected), set(selected))
        for name, (kind, slice_name, pattern) in expected.items():
            with self.subTest(contract=name):
                self.assertEqual(
                    {
                        "kind": kind,
                        "slice": slice_name,
                        "pattern": pattern,
                        "applies_to": ["claude", "codex"],
                    },
                    selected[name],
                )
        for name, (before, after) in order_expected.items():
            with self.subTest(contract=name):
                self.assertEqual(
                    {
                        "kind": "order",
                        "before": before,
                        "after": after,
                        "applies_to": ["claude", "codex"],
                    },
                    selected[name],
                )

    def test_gunte_contract_registry_owns_worker_invariants_and_excludes_repository_specific_quality(self) -> None:
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

        self.assertEqual(
            [],
            [entry for entry in registry.values() if entry.get("slice") == "gunte-test-quality"],
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

    def test_test_quality_reviewer_keeps_general_quality_scope_without_gunte_specific_section(self) -> None:
        paths = (
            ROOT / "shared/agents/test-quality-reviewer.md",
            ROOT / "plugins/claude/agents/test-quality-reviewer.md",
            ROOT / "plugins/codex/install/agents/test-quality-reviewer.toml",
        )
        for path in paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("gunte-test-quality", text)
                self.assertNotIn("Gunte", text)
                self.assertNotIn("Gunte repository の追加観点", text)
                for marker in ("受け入れ条件", "観測可能な振る舞い", "境界値", "異常系"):
                    self.assertIn(marker, text)
        source = paths[0].read_text(encoding="utf-8")
        self.assertIn("meaningful failure protection", source)

    def test_release_readmes_describe_current_surface_and_exclude_retired_routes(self) -> None:
        current_agents = WORKERS | REVIEWERS | ADVISORS
        version = (ROOT / "shared/VERSION").read_text(encoding="utf-8").strip()
        for path in RELEASE_READMES:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn(f"v{version}", text)
                for identifier in PUBLIC_SKILLS | INTERNAL_SKILLS | current_agents:
                    self.assertIn(identifier, text)
                for marker in ("shared/", "gunte.toml", "gunte emit", "gunte check"):
                    self.assertIn(marker, text)
                for retired in RETIRED_SKILLS:
                    self.assertNotIn(retired, text)
                for retired in RETIRED:
                    self.assertNotIn(retired, text)
                for retired_mode in (
                    "workflow mode",
                    "Branch Plan",
                    "standard-adaptive",
                    "strict-adaptive",
                    "strict-full",
                    "serial implementation branches",
                    "each in its own worktree",
                ):
                    self.assertNotIn(retired_mode, text)

    def test_plugin_manifests_describe_current_v5_route(self) -> None:
        manifests = (
            ROOT / "declarations/claude/plugin.json",
            ROOT / "declarations/codex/plugin.json",
        )
        for path in manifests:
            with self.subTest(path=path):
                manifest = json.loads(path.read_text(encoding="utf-8"))
                description = manifest["description"]
                for skill in PUBLIC_SKILLS:
                    self.assertIn(skill, description)
                self.assertTrue("parent" in description.lower() or "親" in description)
                self.assertNotIn("serial implementation branches", description)
                self.assertNotIn("each in its own worktree", description)
        codex = json.loads(manifests[1].read_text(encoding="utf-8"))
        self.assertIn("Work Unit", codex["interface"]["longDescription"])
        self.assertIn("parent QA", codex["interface"]["longDescription"])

    def test_public_marketplace_metadata_and_release_selectors_are_exact(self) -> None:
        claude_marketplace = json.loads(
            (ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
        )
        self.assertEqual("tugite", claude_marketplace["name"])
        self.assertEqual(
            ["tugite"],
            [plugin["name"] for plugin in claude_marketplace["plugins"]],
        )
        claude_manifest = json.loads(
            (ROOT / "declarations/claude/plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            claude_manifest["description"],
            claude_marketplace["plugins"][0]["description"],
        )

        codex_marketplace = json.loads(
            (ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8")
        )
        self.assertEqual("tugite", codex_marketplace["name"])
        self.assertEqual("Tugite", codex_marketplace["interface"]["displayName"])
        self.assertEqual(
            ["tugite"],
            [plugin["name"] for plugin in codex_marketplace["plugins"]],
        )

        for relative_path in (
            "declarations/claude/plugin.json",
            "declarations/codex/plugin.json",
            "plugins/claude/.claude-plugin/plugin.json",
            "plugins/codex/.codex-plugin/plugin.json",
        ):
            with self.subTest(manifest=relative_path):
                manifest = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
                self.assertEqual("tugite", manifest["name"])
                display_name = manifest.get("displayName")
                if display_name is None:
                    display_name = manifest["interface"]["displayName"]
                self.assertEqual("Tugite", display_name)
                self.assertEqual(EXPECTED_PLUGIN_KEYWORDS, manifest["keywords"])

        claude_readme = (ROOT / "plugins/claude/README.md").read_text(encoding="utf-8")
        self.assertEqual(
            1,
            claude_readme.splitlines().count("/plugin install tugite@tugite"),
        )
        self.assertNotIn("tugite-marketplace", claude_readme)

        codex_readme = (ROOT / "plugins/codex/README.md").read_text(encoding="utf-8")
        self.assertEqual(
            1,
            codex_readme.splitlines().count("codex plugin add tugite@tugite"),
        )
        self.assertEqual(
            1,
            codex_readme.count("`codex plugin add tugite@tugite`"),
        )
        self.assertNotIn("tugite@personal", codex_readme)

    def test_common_downstream_routing_contract_registry_is_exact(self) -> None:
        registry = tomllib.loads((ROOT / "contracts.toml").read_text(encoding="utf-8"))["contracts"]
        expected = {
            "public-workflow-routing-requires-cb680296": (
                "requires", "public-workflow-routing", "`return target` は public workflow parent が所有する"
            ),
            "public-workflow-routing-requires-dc53d733": (
                "requires", "public-workflow-routing", "明示されていない別 workflow へ自動 switch しない"
            ),
            "review-loop-proposal-family-caller-requires-88448999": (
                "requires", "review-loop-proposal-family-caller", "proposal-family public workflow"
            ),
            "review-loop-proposal-family-caller-requires-2f49b189": (
                "requires", "review-loop-proposal-family-caller", "public workflow parent"
            ),
            "review-loop-proposal-family-caller-requires-56553866": (
                "requires", "review-loop-proposal-family-caller", "ユーザー明示の単独 review"
            ),
            "review-loop-proposal-family-caller-requires-322f4234": (
                "requires", "review-loop-proposal-family-caller", "workflow 間も自動で切り替えない"
            ),
        }
        selected = {
            name: entry
            for name, entry in registry.items()
            if entry.get("slice") in {"public-workflow-routing", "review-loop-proposal-family-caller"}
        }
        self.assertEqual(set(expected), set(selected))
        for name, (kind, slice_name, pattern) in expected.items():
            with self.subTest(contract=name):
                self.assertEqual(
                    {
                        "kind": kind,
                        "slice": slice_name,
                        "pattern": pattern,
                        "applies_to": ["claude", "codex"],
                    },
                    selected[name],
                )

    def test_common_downstream_skill_boundaries_are_explicit(self) -> None:
        proposal = (ROOT / "shared/skill/proposal/SKILL.md").read_text(encoding="utf-8")
        gate = (ROOT / "shared/skill/structural-health-gate/SKILL.md").read_text(encoding="utf-8")
        review = (ROOT / "shared/skill/review-loop/SKILL.md").read_text(encoding="utf-8")
        proposal_metadata = (ROOT / "declarations/codex/skills/proposal/openai.yaml").read_text(encoding="utf-8")
        gate_metadata = (ROOT / "declarations/codex/skills/structural-health-gate/openai.yaml").read_text(encoding="utf-8")

        self.assertIn("caller-owned parent", proposal)
        self.assertIn("candidate snapshot", proposal)
        self.assertIn("stop-incomplete", proposal)
        self.assertIn("後段工程を選択・起動せず", proposal)
        self.assertNotIn("review-loop", proposal)
        self.assertIn("plan-craft", proposal)
        self.assertIn("plan-craft", proposal_metadata)
        self.assertIn("stop-incomplete", proposal_metadata)
        self.assertIn("assessment Data", gate)
        self.assertIn("明示起動された proposal-family public workflow parent", gate)
        self.assertIn("caller_context", gate_metadata)
        self.assertIn("workflow_family: proposal-family", gate_metadata)
        self.assertIn("invocation: explicit-public-parent", gate_metadata)
        self.assertIn("reject missing or invalid caller_context before assessment", gate_metadata)
        for route_name in ("plan-craft", "review-loop"):
            self.assertNotIn(route_name, gate)
        self.assertIn("proposal-family public workflow", review)
        self.assertIn("caller_context", review)
        self.assertIn("ユーザー明示の単独 review", review)
        self.assertIn("workflow 間も自動で切り替えない", review)
        self.assertNotIn("review-loop", proposal_metadata)
        self.assertNotIn("plan-craft", gate_metadata)
        self.assertNotIn("review-loop", gate_metadata)

    def test_final_writing_remediation_registry_has_bounded_route_inventory(self) -> None:
        registry = tomllib.loads((ROOT / "contracts.toml").read_text(encoding="utf-8"))["contracts"]
        entries = [
            entry
            for entry in registry.values()
            if entry.get("slice") == "final-writing-remediation"
        ]
        expected = {
            "final-writing-remediation-requires-642457e2": ("requires", "final writing gate"),
            "final-writing-remediation-requires-89150988": ("requires", "finding Data"),
            "final-writing-remediation-requires-d2943276": ("requires", "final remediation Work Unit"),
            "final-writing-remediation-requires-4a11b1ea": ("requires", "`id`"),
            "final-writing-remediation-requires-f1331240": ("requires", "`purpose`"),
            "final-writing-remediation-requires-2cfdf68e": ("requires", "`acceptance_criteria`"),
            "final-writing-remediation-requires-b5d7e713": ("requires", "`scope`"),
            "final-writing-remediation-requires-84248bf0": ("requires", "`change`"),
            "final-writing-remediation-requires-0ff7524e": ("requires", "`exclude`"),
            "final-writing-remediation-requires-596e7cad": ("requires", "`implementation_freedom`"),
            "final-writing-remediation-requires-b8352482": ("requires", "`constraints`"),
            "final-writing-remediation-requires-c849323a": ("requires", "`depends_on`"),
            "final-writing-remediation-requires-8106515b": ("requires", "`verification`"),
            "final-writing-remediation-requires-5fb37d04": ("requires", "commit message"),
            "final-writing-remediation-requires-740b9168": ("requires", "commit range"),
            "final-writing-remediation-requires-a80e1199": ("requires", "before/after identity"),
            "final-writing-remediation-requires-dbe8c239": ("requires", "same-run accept exception"),
            "final-writing-remediation-requires-550cdb37": ("requires", "fresh Implementer context"),
            "final-writing-remediation-requires-19309f89": ("requires", "single writer"),
            "final-writing-remediation-requires-6bf30d81": ("requires", "mechanically restart"),
            "final-writing-remediation-requires-0b0c31ed": ("requires", "mandatory final writing review"),
            "final-writing-remediation-requires-b05e9dec": ("requires", "closeout"),
            "final-writing-remediation-forbids-1947765d": ("forbids", "review-patch-refactorer"),
            "final-writing-remediation-forbids-bb2ae611": ("forbids", "fixed patch agent"),
            "final-writing-remediation-forbids-19382517": ("forbids", "全 finding の固定 loop"),
        }
        names = [
            name
            for name, entry in registry.items()
            if entry.get("slice") == "final-writing-remediation"
        ]
        self.assertEqual(len(expected), len(entries))
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(set(expected), set(names))
        for name, (kind, pattern) in expected.items():
            with self.subTest(contract=name):
                entry = registry[name]
                self.assertEqual(
                    {"kind", "slice", "pattern", "applies_to"},
                    set(entry),
                )
                self.assertEqual(kind, entry["kind"])
                self.assertEqual("final-writing-remediation", entry["slice"])
                self.assertEqual(pattern, entry["pattern"])
                self.assertEqual(["claude", "codex"], entry["applies_to"])

    def test_review_loop_induced_brake_contract_registry_is_exact(self) -> None:
        registry = tomllib.loads((ROOT / "contracts.toml").read_text(encoding="utf-8"))["contracts"]
        expected = {
            "review-loop-induced-brake-requires-5f2d73b0": (
                "requires",
                "review-loop-induced-brake",
                "直前までに親が採用して verification を完了した修正によって finding が新たに成立した",
            ),
            "review-loop-induced-brake-requires-a0199e5d": (
                "requires",
                "review-loop-induced-brake",
                "対象文の新旧、snapshot 差分、同じ指摘の再出現だけでは",
            ),
            "review-loop-induced-brake-requires-6949511b": (
                "requires",
                "review-loop-induced-brake",
                "各通常 round で、親確定の `修正推奨` 以上",
            ),
            "review-loop-induced-brake-requires-cf51f4de": (
                "requires",
                "review-loop-induced-brake",
                "通常 round 2 回で連続して",
            ),
            "review-loop-induced-brake-requires-3b7c1ff9": (
                "requires",
                "review-loop-induced-brake",
                "両 round とも非誘発の `修正必須` が 0",
            ),
            "review-loop-induced-brake-requires-804e8353": (
                "requires",
                "review-loop-induced-brake",
                "`induced-loop` は自己誘発 churn に対する補助ブレーキ",
            ),
            "review-loop-induced-brake-forbids-dd813c83": (
                "forbids",
                "review-loop-induced-brake",
                "`baseline_round`",
            ),
        }
        selected = {
            name: entry
            for name, entry in registry.items()
            if entry.get("slice") == "review-loop-induced-brake"
        }
        self.assertEqual(set(expected), set(selected))
        for name, (kind, slice_name, pattern) in expected.items():
            with self.subTest(contract=name):
                self.assertEqual(
                    {
                        "kind": kind,
                        "slice": slice_name,
                        "pattern": pattern,
                        "applies_to": ["claude", "codex"],
                    },
                    selected[name],
                )

    def test_necessity_kernel_contract_registry_is_exact(self) -> None:
        registry = tomllib.loads((ROOT / "contracts.toml").read_text(encoding="utf-8"))["contracts"]
        expected = {
            "necessity-kernel-v1-requires-f5c9070d": ("requires", "necessity-kernel-v1", "Task Contract"),
            "necessity-kernel-v1-requires-f4594656": ("requires", "necessity-kernel-v1", "requested outcome"),
            "necessity-kernel-v1-requires-1238f644": ("requires", "necessity-kernel-v1", "明示AC"),
            "necessity-kernel-v1-requires-3812bcb3": ("requires", "necessity-kernel-v1", "scope/exclude/constraints/verification"),
            "necessity-kernel-v1-requires-e6f267b7": ("requires", "necessity-kernel-v1", "公開/外部観測動作"),
            "necessity-kernel-v1-requires-fcdaa507": ("requires", "necessity-kernel-v1", "外部契約/API"),
            "necessity-kernel-v1-requires-c8c89f19": ("requires", "necessity-kernel-v1", "repository invariant"),
            "necessity-kernel-v1-requires-d23b0af1": ("requires", "necessity-kernel-v1", "サポート対象入力/状態/環境"),
            "necessity-kernel-v1-requires-debbd2a6": ("requires", "necessity-kernel-v1", "一般的に有用/将来有用だけ"),
            "necessity-kernel-v1-requires-238cb5f5": ("requires", "necessity-kernel-v1", "Claim"),
            "necessity-kernel-v1-requires-91c41e23": ("requires", "necessity-kernel-v1", "observation/evidence/necessity basis"),
            "necessity-kernel-v1-requires-dbeb2a1a": ("requires", "necessity-kernel-v1", "Deletion Test"),
            "necessity-kernel-v1-requires-110f861c": ("requires", "necessity-kernel-v1", "unnecessary"),
            "necessity-kernel-v1-requires-bf6099cb": ("requires", "necessity-kernel-v1", "necessary"),
            "necessity-kernel-v1-requires-22ed466c": ("requires", "necessity-kernel-v1", "indeterminate"),
            "necessity-kernel-v1-requires-2a899f17": ("requires", "necessity-kernel-v1", "Broken Obligation"),
            "necessity-kernel-v1-requires-6f7405a9": ("requires", "necessity-kernel-v1", "Failure"),
            "necessity-kernel-v1-requires-598c305a": ("requires", "necessity-kernel-v1", "Evidence"),
            "necessity-kernel-v1-requires-2b110254": ("requires", "necessity-kernel-v1", "Minimum Resolution Condition"),
            "necessity-kernel-v1-requires-81ac889b": ("requires", "necessity-kernel-v1", "remaining witness"),
            "necessity-kernel-v1-requires-2eb5615e": ("requires", "necessity-kernel-v1", "mutual deletion"),
            "necessity-kernel-v1-requires-953797cc": ("requires", "necessity-kernel-v1", "updated snapshot"),
            "necessity-kernel-v1-requires-1ad630c7": ("requires", "necessity-kernel-v1", "discovered != admitted"),
            "necessity-kernel-v1-requires-ef993008": ("requires", "necessity-kernel-v1", "Stop Adding Rule"),
            "necessity-kernel-v1-requires-4e0cf845": ("requires", "necessity-kernel-v1", "structural-health-gate 適用外"),
        }
        selected = {
            name: entry
            for name, entry in registry.items()
            if entry.get("slice") == "necessity-kernel-v1"
        }
        self.assertEqual(set(expected), set(selected))
        self.assertEqual(25, len(selected))
        for name, (kind, slice_name, pattern) in expected.items():
            with self.subTest(contract=name):
                self.assertEqual(
                    {
                        "kind": kind,
                        "slice": slice_name,
                        "pattern": pattern,
                        "applies_to": ["claude", "codex"],
                    },
                    selected[name],
                )

    def test_necessity_kernel_eval_inventory_has_minimum_boundary_cases(self) -> None:
        corpus = (ROOT / "evals/workflow-decision-corpus.md").read_text(encoding="utf-8")
        expected = {
            "necessity-kernel-necessary": ("前提 Data", "期待する判断", "禁止動作", "必要証跡", "Broken Obligation"),
            "necessity-kernel-unnecessary": ("前提 Data", "期待する判断", "禁止動作", "必要証跡", "remaining witness"),
            "necessity-kernel-indeterminate": ("前提 Data", "期待する判断", "禁止動作", "必要証跡", "question_or_option", "unresolved", "identity 不一致"),
            "necessity-kernel-mutual-deletion-guard": ("前提 Data", "期待する判断", "禁止動作", "必要証跡", "A/B", "snapshot"),
            "necessity-kernel-high-severity-out-of-scope": ("前提 Data", "期待する判断", "禁止動作", "必要証跡", "high severity", "範囲外"),
        }
        for case_id, markers in expected.items():
            with self.subTest(case_id=case_id):
                section = self._section_body(corpus, f"## {case_id}")
                self.assertTrue(section.strip())
                for marker in markers:
                    self.assertIn(marker, section)
                criteria = self._labeled_field(section, "判定基準")
                for marker in ("necessity-kernel-v1", "Task Contract", "Claim", "Deletion Test"):
                    self.assertIn(marker, criteria)
                if case_id == "necessity-kernel-indeterminate":
                    anomaly = self._labeled_field(section, "異常 variant")
                    for marker in (
                        "necessity-kernel-v0",
                        "必要本文不足",
                        "advisor非起動",
                        "自動採否禁止",
                        "stop-incomplete",
                    ):
                        self.assertIn(marker, anomaly)

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
        self.assertEqual("5.1.0", version)
        for relative_path in (
            "declarations/claude/plugin.json",
            "declarations/codex/plugin.json",
            "plugins/claude/.claude-plugin/plugin.json",
            "plugins/codex/.codex-plugin/plugin.json",
        ):
            with self.subTest(manifest=relative_path):
                self.assertEqual(
                    version,
                    json.loads((ROOT / relative_path).read_text(encoding="utf-8"))["version"],
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
