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

    def test_repository_implementers_self_check_final_standard_and_strict_returns(
        self,
    ) -> None:
        """Require final self-reconciliation while preserving lite/strict gates."""
        expected_section = (
            "- **返却前自己照合**: `standard` と `strict` の最終返却前に、"
            "AC 対応表を task requirements および変更 file / tool outputs と照合し、"
            "返却内容との整合を確認する。`lite` では自己照合を要求しない。"
            "`strict` の途中段階には自己照合を要求しない。"
            "- 不整合を検出した場合は不整合を含む最終返却を行わず、"
            "授権済みの段階・scope内なら修正と再検証を行う。"
            "修正が授権済み段階・scopeを越える場合は、状況と判断点を返す。"
        )

        for name in ("implementer", "senior-implementer", "expert-implementer"):
            paths = (
                Path("shared/agents") / f"{name}.md",
                Path("plugins/claude/agents") / f"{name}.md",
                Path("plugins/codex/install/agents") / f"{name}.toml",
            )
            for path in paths:
                with self.subTest(name=name, path=path):
                    content = self._repository_text(path)
                    lines = content.splitlines()
                    start = next(
                        index
                        for index, line in enumerate(lines)
                        if line.startswith("- **返却前自己照合**:")
                    )
                    second = next(
                        index
                        for index in range(start + 1, len(lines))
                        if lines[index].startswith("- ")
                    )
                    end = next(
                        (
                            index
                            for index in range(second + 1, len(lines))
                            if lines[index].startswith("- ")
                        ),
                        len(lines),
                    )
                    section = "".join(lines[start:end])
                    self.assertEqual(
                        "".join(expected_section.split()),
                        "".join(section.split()),
                    )

    def test_repository_workflow_selects_implementers_by_complexity_and_residual_judgment(
        self,
    ) -> None:
        """Select senior workers for implementation difficulty, not failure impact."""
        reference = self._repository_text(
            SHARED_SKILL_REFERENCE_PATHS["implementation-branches.md"]
        )
        normalized = "".join(reference.split())
        required = (
            "難度は `implementation_complexity` と実装時に残る設計・推論判断で判断する。",
            "| `implementer` | senior 候補に該当せず、仕様が明確で既存 pattern を適用でき、"
            "判断密度が低い枝。 |",
            "| `senior-implementer` | 共通4軸の相対比較で判断密度が高く、残存設計判断と"
            "上位 model で減らせる手戻りが他候補より大きい枝。 |",
            "単なる複数 module への波及、高い失敗コスト、誤実装の代償だけでは "
            "`senior-implementer` を選ばない。",
        )
        for contract in required:
            self.assertIn("".join(contract.split()), normalized)

    def test_repository_workflow_assigns_workers_by_relative_judgment_density(
        self,
    ) -> None:
        """Separate senior eligibility from relative worker allocation and rerouting."""
        required_contract = (
            "senior 候補は Branch Plan の field にせず、`impl-lead` 内部の作業 Data として保持する。",
            "候補抽出と実割当を分離する。",
            "事前設計後も残る判断量",
            "推論難度",
            "誤実装時の手戻り量",
            "他枝への影響",
            "変更量やファイル数だけを昇格根拠にしない。",
            "現在授権され、5項目の再検証と mode 導出を通過した実行対象 Branch Plan 1件の全枝を同一の受入 snapshot 内で評価し",
            "候補抽出後に Branch Plan 単位で実割当を一括確定する",
            "同一の受入 snapshot 内で候補と配車を揺らさない",
            "senior 候補同士を相対比較し、判断密度の高い枝から配分する。",
            "senior 候補が全枝の過半になった場合は",
            "枝分割または Acceptance Criteria の粒度を見直すシグナル",
            "固定的な割合や閾値を senior 昇格の根拠にしない。",
        )
        for path, workflow in self._repository_workflow_texts().items():
            with self.subTest(path=path):
                normalized = "".join(workflow.split())
                for contract in required_contract:
                    self.assertIn("".join(contract.split()), normalized)
                self.assertNotIn("約8割", normalized)

    def test_repository_workflow_reports_senior_assignment_reason(self) -> None:
        """Report the three reasons for a senior assignment and expert distinction."""
        required_contract = (
            "senior の割当理由には、次の3点を必ず記録する。",
            "残存設計判断",
            "上位 model で減らせる誤実装・手戻り",
            "他候補より優先する理由",
            "expert と異なり senior には事前 reviewer を挟まず",
            "親の自己申告に留める",
            "Why Not",
        )
        for platform, reference in self._impl_lead_reference_texts(
            "implementation-branches.md"
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(reference.split())
                for contract in required_contract:
                    self.assertIn("".join(contract.split()), normalized)

    def test_repository_workflow_prefers_implementer_when_uncertain_and_recreates_context(
        self,
    ) -> None:
        """Keep uncertain branches on implementer and recreate context on rerouting."""
        required_contract = (
            "通常と senior で迷ったら `implementer` を選ぶ。",
            "迷いだけでは senior 候補にしない。",
            "設計を確定して `implementer` に再委譲",
            "枝を追加分割",
            "senior へ再配車",
            "新しい Implementer context",
            "未完成 production code は統合せず",
            "親が独立に受入可能と QA した成果だけ",
            "基準 commit の検証",
            "旧 context の worktree / git branch の破棄",
            "基準 commit からの新 context の worktree と git branch の作成",
            "新しい routing snapshot",
            "run-closeout の最終 cleanup ではなく",
            "返却された状況と判断点は確定済み設計判断として新しい prompt に載せる。",
            "1実装枝 = 1つの新規 Implementer context",
            "枝をまたぐ再利用を禁止する規約",
            "同一枝の破棄・新 context 再開は禁止しない。",
        )
        for platform, reference in self._impl_lead_reference_texts(
            "implementation-branches.md"
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(reference.split())
                for contract in required_contract:
                    self.assertIn("".join(contract.split()), normalized)
                lifecycle = "".join(reference.split())
                ordered = (
                    "未完成productioncodeは統合せず",
                    "部分成果の受入判断とQA",
                    "基準commitの検証",
                    "旧contextのworktree/gitbranchの破棄",
                    "基準commitからの新contextのworktreeとgitbranchの作成",
                )
                positions = [lifecycle.index(marker) for marker in ordered]
                self.assertEqual(sorted(positions), positions)

    def test_repository_implementer_profiles_separate_normal_and_high_complexity_branches(
        self,
    ) -> None:
        """Keep source and generated implementer profiles aligned to routing role."""
        for name in ("implementer", "senior-implementer"):
            paths = (
                Path("shared/agents") / f"{name}.md",
                Path("plugins/claude/agents") / f"{name}.md",
                Path("plugins/codex/install/agents") / f"{name}.toml",
            )
            for path in paths:
                content = self._repository_text(path)
                normalized = "".join(content.split())
                with self.subTest(name=name, path=path):
                    if name == "implementer":
                        self.assertIn("implementation_complexity", content)
                    else:
                        self.assertIn("高判断密度", content)
                        for excluded in (
                            "複数 module への波及",
                            "複数モジュールに波及",
                            "broad module impact",
                            "高い失敗コスト",
                            "high cost of mistakes",
                            "誤実装の代償",
                        ):
                            self.assertNotIn("".join(excluded.split()), normalized)

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

        self.assertIn(instruction, skills.source_references["run-closeout.md"])
        self.assertIn(instruction, skills.codex_references["run-closeout.md"])
        self.assertNotIn(instruction, skills.claude_references["run-closeout.md"])

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
            "変更を禁止する物理的範囲、この枝でやらないこと",
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

    def test_repository_impl_lead_skill_uses_forbidden_scope_input_only(self) -> None:
        """Keep the top-level workflow input limited to the forbidden scope."""
        skills = self._repository_skill_texts()
        for skill in skills.all_texts():
            self.assertIn(
                "目的、入力、出力、Acceptance Criteria、禁止範囲を確定する。",
                skill,
            )
            self.assertNotIn(
                "目的、入力、出力、Acceptance Criteria、変更範囲、禁止範囲を確定する。",
                skill,
            )
            self.assertNotIn(
                "目的、入力、出力、Acceptance Criteria、変更禁止範囲、この枝で担当しない責務・作業を確定する。",
                skill,
            )

    def test_repository_implementation_branches_reference_defines_branch_terminology(
        self,
    ) -> None:
        """Define 実装枝, git branch, Branch Plan Set, and Branch Plan in one glossary."""
        # 用語の正本は「用語」節であり、他の節に同じ語が出るだけでは正本にならない。
        # そのため節を次の見出しまでで切り出して、その中だけを検査する。
        required_glossary_content = (
            "**実装枝**",
            "**git branch**",
            "**Branch Plan Set** — `branch-design` が出力する Data。`branch_plans[]` に "
            "Branch Plan を持ち、`acceptance_criteria` と `order` を Set 層で持つ。",
            "**Branch Plan** — Branch Plan Set の要素。",
            "単独の `branch` 表記を使わない",
        )

        for platform, reference in self._impl_lead_reference_texts(
            "implementation-branches.md"
        ).items():
            with self.subTest(platform=platform):
                self.assertIn("## 用語", reference)
                glossary = reference.split("## 用語", 1)[1].split("\n## ", 1)[0]
                normalized_glossary = "".join(glossary.split())
                for item in required_glossary_content:
                    self.assertIn("".join(item.split()), normalized_glossary)

    def test_repository_implementation_branches_chain_base_commits_across_branch_plans(
        self,
    ) -> None:
        """Chain the green base commit across Branch Plans without waiting for main."""
        required_contract = (
            "次の枝は最新の統合済み green な基準コミットから開始する。",
            "この規約は Branch Plan 間にも適用する。",
            "先行 Branch Plan の成果が main へ merge されるのを待たない。",
        )
        expected_sections = (
            "用語",
            "Implementer context と枝の lifecycle",
            "worktree と基準 commit",
            "委譲 mode に応じた TDD/QA",
            "Implementer の選択",
            "委譲 prompt",
        )
        # 「この規約は」は直前の「次の枝は最新の統合済み green な基準コミットから開始する。」
        # を受ける照応語なので、file 全体ではなく両文を含む節を切り出して照合する。連結
        # テキストへの包含だけだと、別の節へ移して照応先が変わっても通ってしまう。
        for platform, reference in self._impl_lead_reference_texts(
            "implementation-branches.md"
        ).items():
            with self.subTest(platform=platform):
                lifecycle = reference.split(
                    "## Implementer context と枝の lifecycle", 1
                )[-1].split("\n## ", 1)[0]
                normalized = "".join(lifecycle.split())

                # 節をまたぐ移動は切り出しが防ぐが、同じ節の中で照応語を照応元の前へ
                # 出す入れ替えは通ってしまうため、節内の順序も固定する。判定は正規化
                # テキスト上で行い、折り返し位置の変更で needle が消えないようにする。
                # 3文すべてを並びへ含めるのは、対象外の文が残ると、その文だけを照応元の
                # 前へ動かす入れ替えを見逃すためである。
                positions = []
                for contract in required_contract:
                    marker = "".join(contract.split())
                    self.assertIn(
                        marker,
                        normalized,
                        f"{platform}: lifecycle 節に「{contract}」がない",
                    )
                    positions.append(normalized.index(marker))
                self.assertEqual(
                    sorted(positions),
                    positions,
                    f"{platform}: 照応元 → Branch Plan 間への適用 → merge を待たない根拠 "
                    f"の順に並んでいない: {positions}",
                )

                self.assertEqual(
                    expected_sections,
                    self._markdown_table_of_contents(reference),
                )
                self.assertEqual(
                    expected_sections,
                    self._markdown_section_headings(reference),
                )


if __name__ == "__main__":
    unittest.main()
