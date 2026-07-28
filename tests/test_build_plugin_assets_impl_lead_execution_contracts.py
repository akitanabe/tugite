"""Repository contracts for impl-lead execution and branch lifecycle behavior."""

from __future__ import annotations

from pathlib import Path
import unittest

from build_plugin_assets_test_support import (
    GENERATED_SKILL_REFERENCE_PATHS,
    RepositoryContractSupport,
    SHARED_SKILL_REFERENCE_PATHS,
)


class ImplLeadExecutionContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def test_repository_workflow_normalizes_implementation_branch_boundaries(
        self,
    ) -> None:
        """Use one isolated branch lifecycle without silent direct fallback."""
        workflows = self._repository_workflow_texts()
        required_contract = (
            "各実装枝は専用 worktree で隔離する。",
            "worktree を用意できない場合は委譲を開始しない。",
            "ユーザーの確認なく親の直接実装へ切り替えない。",
            "共有土台の作成は、実装枝の委譲前に親が行える明示的な例外",
            "返却後の機能修正を親が引き取る根拠にはしない。",
            "4. **Refactor と再検証**",
            "テスト計画では commit を作らない。",
            "Red、Green、Refactor の各段階では、段階の変更を commit する。",
            "最終返却では先頭から末尾までの commit SHA range を返す。",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized = "".join(workflow.split())
                for contract in required_contract:
                    self.assertIn("".join(contract.split()), normalized)

    def test_repository_expert_availability_rules_are_platform_specific(self) -> None:
        """Keep unavailable expert profile names out of the other platform."""
        source = self._repository_text(
            SHARED_SKILL_REFERENCE_PATHS["expert-selection.md"]
        )
        claude = self._repository_text(
            GENERATED_SKILL_REFERENCE_PATHS["claude"]["expert-selection.md"]
        )
        codex = self._repository_text(
            GENERATED_SKILL_REFERENCE_PATHS["codex"]["expert-selection.md"]
        )

        self.assertIn("Fable", source)
        self.assertIn("`gpt-5.6-sol`", source)
        self.assertIn("Fable", claude)
        self.assertNotIn("`gpt-5.6-sol`", claude)
        self.assertIn("`gpt-5.6-sol`", codex)
        self.assertNotIn("Fable", codex)

    def test_repository_implementers_follow_mode_and_writing_contracts(self) -> None:
        """Align every implementer with delegated stages and Why Not comments."""
        for name in ("implementer", "senior-implementer", "expert-implementer"):
            paths = (
                Path("shared/agents") / f"{name}.md",
                Path("plugins/claude/agents") / f"{name}.md",
                Path("plugins/codex/install/agents") / f"{name}.toml",
            )
            for path in paths:
                with self.subTest(name=name, path=path):
                    content = self._repository_text(path)
                    self.assertIn("委譲 mode", content)
                    self.assertIn("指定された段階を越えない", content)
                    self.assertIn("Why Not", content)
                    self.assertIn("返却 commit SHA range", content)
                    self.assertNotIn(
                        "ロジック・制約・前提・テストの意図を残す",
                        content,
                    )

        for name in ("implementer", "senior-implementer"):
            source = self._repository_text(Path("shared/agents") / f"{name}.md")
            self.assertIn(
                "`lite` では親が求めた場合だけ Red 証跡と AC 対応表を返す",
                source,
            )
            self.assertIn(
                "`standard` では Red 証跡と AC 対応表を必ず返す",
                source,
            )

    def test_repository_implementer_worktree_inputs_use_parent_managed_contract(
        self,
    ) -> None:
        """Give both platforms a parent-managed worktree and start-condition gate."""
        start_condition_contracts = (
            "絶対 worktree path と git branch",
            "`pwd -P`",
            "`git status --short` が空",
            "基準 commit",
            "着手せず",
        )
        for name in ("implementer", "senior-implementer", "expert-implementer"):
            claude = self._repository_text(
                Path("plugins/claude/agents") / f"{name}.md"
            )
            codex = self._repository_text(
                Path("plugins/codex/install/agents") / f"{name}.toml"
            )

            for platform, content in (("claude", claude), ("codex", codex)):
                with self.subTest(name=name, platform=platform):
                    normalized = "".join(content.split())
                    for contract in start_condition_contracts:
                        self.assertIn("".join(contract.split()), normalized)

            with self.subTest(name=name, platform="claude", check="no-isolation"):
                self.assertNotIn('isolation: "worktree"', claude)
                self.assertNotIn(
                    "起動後に実際の worktree path と git branch を確認",
                    claude,
                )

    def test_repository_reviewers_separate_boundary_and_safety_risks(self) -> None:
        """Route placement concerns separately from security and failure safety."""
        responsibility = self._repository_text(
            Path("shared/agents/responsibility-boundary-reviewer.md")
        )
        security = self._repository_text(
            Path("shared/agents/security-side-effect-reviewer.md")
        )

        self.assertIn("副作用をどの責務境界へ配置したか", responsibility)
        self.assertIn(
            "認可・機密性・破壊安全性の評価は対象外",
            responsibility,
        )
        self.assertIn("認可、機密性、破壊安全性", security)
        self.assertIn(
            "命名や責務配置そのものの再設計は対象外",
            security,
        )
        test_quality = self._repository_text(
            Path("shared/agents/test-quality-reviewer.md")
        )
        self.assertIn(
            "AC と diff から必要な追加 case を導出することは対象内",
            test_quality,
        )

    def test_repository_codex_skill_waits_for_each_worker_response(self) -> None:
        """Keep Codex workers alive and waiting until each delegated task responds."""
        skills = self._repository_skill_texts()
        required_instructions = (
            "対象 worker ごとに `wait_agent` を繰り返し使い、完了通知または返答が返るまで待機する。",
            "数分間の無応答を理由に worker を `shutdown` または `interrupt_agent` しない。",
            "ユーザーが明示的に取り消した場合、または tool が回復不能な異常を報告した場合は例外",
        )

        for instruction in required_instructions:
            self.assertIn(instruction, skills.source)
            self.assertIn(instruction, skills.codex)
            self.assertNotIn(instruction, skills.claude)

    def test_repository_codex_runs_the_integrated_review_gate(self) -> None:
        """Prefer Codex /review before cleanup when the environment provides it."""
        skills = self._repository_skill_texts()
        instruction = (
            "環境が提供する場合は `/review` を実行し、利用できない場合は"
            "同等の統合済み diff review を親が行う。"
        )

        self.assertIn(instruction, skills.source_references["qa-and-integration.md"])
        self.assertIn(instruction, skills.codex_references["qa-and-integration.md"])
        self.assertNotIn(instruction, skills.claude_references["qa-and-integration.md"])

    def test_repository_skills_clean_up_only_after_the_final_gate(self) -> None:
        """Clean up platform resources only after every final gate has passed."""
        skills = self._repository_skill_texts()

        self.assertIn("## 後始末", skills.source)
        self.assertIn("最終ゲートをすべて通過した後", skills.claude)
        self.assertIn("親がこのタスク用に作成した", skills.claude)
        self.assertIn("`git worktree remove <worktree path>`", skills.claude)
        self.assertIn("最終ゲートをすべて通過した後", skills.codex)
        self.assertIn("親がこのタスク用に作成した", skills.codex)
        self.assertIn("`git worktree remove <worktree path>`", skills.codex)
        self.assertIn("親がこのワークフローで起動した agent を停止する。", skills.codex)
        self.assertNotIn("親がこのワークフローで起動した agent を停止する。", skills.claude)
        self.assertNotIn('isolation: "worktree"', skills.claude)

    def test_repository_skills_start_a_fresh_implementer_context_per_branch(
        self,
    ) -> None:
        """Align each implementation branch with one fresh Implementer context."""
        skills = self._repository_skill_texts()
        shared_contract = (
            "1実装枝 = 1つの新規 Implementer context",
            "別の実装枝に同じ Implementer を再利用しない。",
            "同一実装枝を完成させるための段階ゲートと差し戻し",
        )

        for instruction in shared_contract:
            for skill in skills.all_texts():
                self.assertIn(instruction, skill)

        codex_context_boundary = (
            '新規 Implementer の生成時は必ず `fork_turns: "none"` を指定する。'
        )
        self.assertIn(codex_context_boundary, skills.source)
        self.assertIn(codex_context_boundary, skills.codex)
        self.assertNotIn(codex_context_boundary, skills.claude)

    def test_repository_skills_require_self_contained_implementation_branch_data(
        self,
    ) -> None:
        """Give a fresh Implementer all data needed to finish one branch."""
        skills = self._repository_skill_texts()
        required_data = (
            "実装枝の目的",
            "Acceptance Criteria",
            "変更を許可する物理的範囲、変更を禁止する物理的範囲、この枝でやらないこと",
            "最新の基準コミット",
            "コードから読み取れない確定済みの設計判断や制約",
            "委譲 mode と TDD 要件",
            "検証 command",
            "完了条件",
            "commit と返却報告の形式",
        )

        for item in required_data:
            for skill in skills.all_texts():
                self.assertIn(item, skill)

        self.assertIn("絶対 worktree path と git branch 名", skills.source)
        self.assertIn("絶対 worktree path と git branch 名", skills.claude)
        self.assertIn("絶対 worktree path と git branch 名", skills.codex)
        self.assertNotIn("worktree の隔離条件", skills.claude)

    def test_repository_implementation_branches_reference_defines_branch_terminology(
        self,
    ) -> None:
        """Define 実装枝, git branch, and Branch Plan as distinct terms in one glossary."""
        skills = self._repository_skill_texts()
        required_glossary_content = (
            "## 用語",
            "**実装枝**",
            "**git branch**",
            "**Branch Plan**",
            "単独の `branch` 表記を使わない",
        )

        for item in required_glossary_content:
            for skill in skills.all_texts():
                self.assertIn(item, skill)


if __name__ == "__main__":
    unittest.main()
