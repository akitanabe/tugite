"""Repository contracts for distributed agents and reviewer roles."""

from __future__ import annotations

from pathlib import Path
import unittest

from build_plugin_assets_test_support import (
    AGENT_NAMES,
    BASH_GRANTED_REVIEWER_NAMES,
    BASH_WITHHELD_REVIEWER_NAMES,
    CLAUDE_MODEL_PROFILES,
    CLAUDE_PROFILE_PATH,
    CODEX_MODEL_PROFILES,
    CODEX_PROFILE_PATH,
    GENERATED_SKILL_PATHS,
    REFACTORER_NAMES,
    REPOSITORY_ROOT,
    REVIEWER_NAMES,
    RepositoryContractSupport,
    SHARED_SKILL_PATH,
    WRITE_TOOL_NAMES,
    claude_reviewer_tool_policy,
)


# The manuscript-side restatement of the working limits, kept minimal: the
# reasoning behind each limit lives in reviewer-findings.md's 「read-only の担保」
# and is not duplicated here.
BASH_WORKING_LIMIT_CONTRACTS = (
    "到達したいかなる repository に対して command を実行する場合であっても、"
    "読み取りと検証の実行だけを行い、追跡ファイルを変更しないでください。",
    "書き込みは、対象とした repository の外の一時領域へ"
    "作成した複製に限り、それ以外のいかなる path へも書き込まないでください。",
    "書き込みを伴う検証は、"
    "`mktemp -d` などで新規作成した一時 directory 配下へ複製して行い、削除はその directory に限って"
    "ください。",
    "削除できない場合は path を返却物へ記録し、非追跡ファイルを複製対象に含めないでください。",
    "HEAD・refs・object DB・git 設定・hooks を変更する操作、"
    "および到達可能性や reflog を失わせる操作を行わないでください",
    "`commit` / `checkout` / `switch` / `reset` / `stash` / `rebase` / `merge` / "
    "`cherry-pick` / `worktree add` / `worktree remove` / `branch -d` / `branch -D` / "
    "`branch -f` / `branch -m` / `update-ref` / `symbolic-ref` / `reflog expire` / "
    "`gc --prune=now` / `config` の変更 / `.git/hooks/*` への書き込み / `clean -fdx` / "
    "`restore` / `push` など",
)


class AgentAndReviewerContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def test_repository_codex_agents_use_role_appropriate_model_profiles(
        self,
    ) -> None:
        """Assign each Codex agent the model and effort suited to its role."""
        for name, expected in CODEX_MODEL_PROFILES.items():
            with self.subTest(name=name):
                source_metadata = self._agent_source_metadata(name)
                artifact_metadata = self._codex_agent_artifact_metadata(name)

                self.assertEqual(expected.model, source_metadata["codex"]["model"])
                self.assertEqual(expected.model, artifact_metadata["model"])
                self.assertEqual(
                    expected.reasoning_effort,
                    source_metadata["codex"]["model_reasoning_effort"],
                )
                self.assertEqual(
                    expected.reasoning_effort,
                    artifact_metadata["model_reasoning_effort"],
                )

    def test_repository_claude_agents_use_role_appropriate_model_profiles(
        self,
    ) -> None:
        """Assign each Claude agent the model and effort suited to its role."""
        for name, expected in CLAUDE_MODEL_PROFILES.items():
            with self.subTest(name=name):
                source_metadata = self._agent_source_metadata(name)
                artifact = self._repository_text(CLAUDE_PROFILE_PATH / f"{name}.md")

                self.assertEqual(expected.model, source_metadata["claude"]["model"])
                self.assertEqual(
                    expected.reasoning_effort, source_metadata["claude"]["effort"]
                )
                self.assertIn(f"model: {expected.model}\n", artifact)
                self.assertIn(f"effort: {expected.reasoning_effort}\n", artifact)

    def test_repository_workflows_gate_expert_implementation_with_selection_review(
        self,
    ) -> None:
        """Use expert only after an independent review approves its concrete rationale."""
        workflows = self._repository_workflow_texts()
        required_contract = (
            "`expert-selection-reviewer`",
            "`APPROVE_EXPERT`",
            "`REJECT_USE_SENIOR`",
            "`REJECT_USE_IMPLEMENTER`",
            "`REJECT_REPLAN`",
            "親相当の能力が必要な判断",
            "senior では不足すると判断した具体的根拠",
            "独立 context へ隔離する理由",
            "自動 fallback しない",
            "プランを練り直す",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized_workflow = "".join(workflow.split())
                for instruction in required_contract:
                    self.assertIn("".join(instruction.split()), normalized_workflow)

        codex_only_rule = (
            "登録または agent 名の指定ができない場合は role profile へ代替せず"
        )
        self.assertIn(codex_only_rule, workflows[SHARED_SKILL_PATH])
        self.assertIn(codex_only_rule, workflows[GENERATED_SKILL_PATHS["codex"]])
        self.assertNotIn(codex_only_rule, workflows[GENERATED_SKILL_PATHS["claude"]])

    def test_repository_expert_agents_define_selection_and_side_effect_contracts(
        self,
    ) -> None:
        """Keep expert selection costly, explicit, and bounded by observable contracts."""
        expert = self._repository_text(Path("shared/agents/expert-implementer.md"))
        reviewer = self._repository_text(
            Path("shared/agents/expert-selection-reviewer.md")
        )
        reviewer_metadata = self._agent_source_metadata("expert-selection-reviewer")

        for instruction in (
            "Action → Data → Calculation → Data → Action",
            "避けられない副作用",
            "副作用を配置した境界",
            "実行順序とトランザクション境界",
            "重複実行、再試行、部分失敗時の振る舞い",
            "これ以上副作用を狭められない理由",
        ):
            self.assertIn(instruction, expert)

        for verdict in (
            "APPROVE_EXPERT",
            "REJECT_USE_SENIOR",
            "REJECT_USE_IMPLEMENTER",
            "REJECT_REPLAN",
        ):
            self.assertIn(verdict, reviewer)
        self.assertEqual("read-only", reviewer_metadata["codex"]["sandbox_mode"])
        self.assertIn("ファイル編集", reviewer)
        self.assertIn("最終判断", reviewer)

    def test_repository_specialized_reviewers_define_their_review_contracts(self) -> None:
        """Expose each review focus, common verdicts, and a read-only Codex role."""
        expected_focus = {
            # 「過不足なく」は「不足なく」を部分文字列として含むため、過剰側を
            # 切り出した改訂は前後の語まで含めないと固定できない。
            "test-quality-reviewer": (
                "観測可能な振る舞い",
                "境界値",
                "異常系",
                "必要なテスト範囲が不足なく",
                "テストの過剰と重複の除去は `over-engineering-reviewer` の責務です",
            ),
            "security-side-effect-reviewer": ("認証", "冪等", "path traversal"),
        }

        for name, focus_terms in expected_focus.items():
            with self.subTest(name=name):
                source = self._repository_text(Path("shared/agents") / f"{name}.md")
                metadata = self._agent_source_metadata(name)

                self.assertEqual("read-only", metadata["codex"]["sandbox_mode"])
                for verdict in ("Pass", "Needs attention", "Blocker"):
                    self.assertIn(verdict, source)
                for term in focus_terms:
                    self.assertIn(term, source)

    def test_repository_writing_principles_reviewer_defines_review_scope_and_finding_contract(
        self,
    ) -> None:
        """Review writing artifacts and return actionable findings as structured data."""
        source = self._repository_text(
            Path("shared/agents/writing-principles-reviewer.md")
        )
        review_scope = (
            "コード",
            "変数名",
            "関数名",
            "テスト名",
            "コメント",
            "DocBlock",
        )
        finding_fields = (
            "指摘ID",
            "対象ファイルと該当箇所",
            "違反している記述原則",
            "問題である理由",
            "外部から観測可能な振る舞いへの影響有無",
            "局所的かつ振る舞いを変えず修正可能か",
            "推奨する修正先",
        )

        for contract in review_scope + finding_fields:
            self.assertIn(contract, source)
        self.assertIn("自身はファイルを変更しない", source)

    def test_repository_over_engineering_reviewer_defines_marginal_necessity_scope_and_finding_contract(
        self,
    ) -> None:
        """Judge removability by marginal necessity and return typed findings only."""
        source = self._repository_text(
            Path("shared/agents/over-engineering-reviewer.md")
        )
        normalized = "".join(source.split())
        review_scope = (
            "その要素を取り除いたとき、検証または実装を失う Acceptance Criteria・"
            "明示された制約・repository の既存規約が存在するか。",
            "traceability",
            "重複した 2 本のテストはどちらも AC へ辿れる",
            "指摘は **基準 commit からの diff が導入した要素に限ります**",
            "自身はファイルを変更しない",
            "抽象化の粒度や配置の良し悪しは `responsibility-boundary-reviewer` の責務です",
            "`## 返却形式` の各項目を具体的に埋められない指摘は返さないでください",
            "取り除いた後も残る実装または検証」を具体的に特定できない場合",
        )
        finding_fields = (
            "指摘ID",
            "対象ファイルと該当箇所",
            "過剰の類型",
            "除去しても失われる AC・制約が無いと判断した根拠",
            "取り除いた後も残る実装または検証とそれが担保する AC",
            "外部から観測可能な振る舞いへの影響有無",
            "局所的かつ振る舞いを変えずに取り除けるか",
            "推奨する修正先",
        )
        finding_types = (
            "A: 重複した検証",
            "B: 除去可能な実装要素",
            "C: 残る検証を特定できないテスト",
        )

        for contract in review_scope + finding_fields + finding_types:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), normalized)
        self.assertNotIn("Needs attention", source)

    def test_repository_over_engineering_reviewer_excludes_structural_extraction_from_removal(
        self,
    ) -> None:
        """Keep extracted functions, partial overlap, and adapting layers out of removal."""
        source = self._repository_text(
            Path("shared/agents/over-engineering-reviewer.md")
        )
        normalized = "".join(source.split())
        exclusions = (
            "関数分割による構造化は、呼び出し元が 1 つであることだけを理由に指摘しない",
            "部分重複（どちらも相手の検出範囲を完全には包含しない 2 つのテスト）は指摘しない",
            "引数の詰め替えや型変換を行う層は pass-through ではありません",
        )
        removable_implementation_tiers = (
            "除去してもいかなる呼び出し側の変更も要しない要素",
            "除去に伴う呼び出し側の変更が委譲先への機械的な付け替えに限られ、"
            "引数、意味、振る舞いの変更を伴わない、純粋な pass-through 層",
        )

        for contract in exclusions + removable_implementation_tiers:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), normalized)

    def test_repository_bash_granted_reviewers_carry_their_working_limits(
        self,
    ) -> None:
        """Write the working limits into the manuscripts the reviewers themselves read, and only into those that can run commands."""
        # The limits are restated per manuscript rather than left in the
        # reference alone because a subagent reads its own manuscript at run
        # time and never opens the skill reference. Reviewers without `Bash`
        # are deliberately left untouched: the same paragraph would be a rule
        # they have no way to break. Scanning all of AGENT_NAMES (not just
        # REVIEWER_NAMES) also catches the paragraph leaking into a
        # non-reviewer agent (implementer, refactorer) where it would be a
        # rule that agent has no `Bash`-granted role to break either.
        for name in AGENT_NAMES:
            texts = {
                "shared": self._repository_text(Path("shared/agents") / f"{name}.md"),
                "claude": self._repository_text(CLAUDE_PROFILE_PATH / f"{name}.md"),
                "codex": self._repository_text(CODEX_PROFILE_PATH / f"{name}.toml"),
            }
            expected = name in BASH_GRANTED_REVIEWER_NAMES
            for platform, text in texts.items():
                normalized = "".join(text.split())
                for contract in BASH_WORKING_LIMIT_CONTRACTS:
                    with self.subTest(name=name, platform=platform, contract=contract):
                        if expected:
                            self.assertIn("".join(contract.split()), normalized)
                        else:
                            self.assertNotIn("".join(contract.split()), normalized)

    def test_repository_reviewer_platforms_grant_the_exploration_reach_of_their_group(
        self,
    ) -> None:
        """Publish the wider Bash-carrying reach only for the group whose verdict needs it."""
        for name in REVIEWER_NAMES:
            with self.subTest(name=name):
                tools, disallowed_tools = claude_reviewer_tool_policy(name)
                source_metadata = self._agent_source_metadata(name)
                claude_artifact = self._repository_text(
                    CLAUDE_PROFILE_PATH / f"{name}.md"
                )
                codex_artifact = self._codex_agent_artifact_metadata(name)

                self.assertEqual(tools, source_metadata["claude"]["tools"])
                self.assertEqual(
                    disallowed_tools,
                    source_metadata["claude"]["disallowed_tools"],
                )
                self.assertIn(f"tools: {', '.join(tools)}\n", claude_artifact)
                self.assertIn(
                    f"disallowedTools: {', '.join(disallowed_tools)}\n",
                    claude_artifact,
                )
                self.assertEqual(
                    "read-only", source_metadata["codex"]["sandbox_mode"]
                )
                self.assertEqual("read-only", codex_artifact["sandbox_mode"])

    def test_repository_every_findings_reviewer_is_barred_from_write_tools(
        self,
    ) -> None:
        """Withhold file modification from every reviewer on both platforms, whatever its exploration reach."""
        for name in REVIEWER_NAMES:
            with self.subTest(name=name):
                source_metadata = self._agent_source_metadata(name)
                for tool in WRITE_TOOL_NAMES:
                    with self.subTest(tool=tool):
                        self.assertIn(
                            tool, source_metadata["claude"]["disallowed_tools"]
                        )
                        self.assertNotIn(tool, source_metadata["claude"]["tools"])
                self.assertEqual(
                    "read-only", source_metadata["codex"]["sandbox_mode"]
                )

    def test_repository_reviewer_exploration_groups_partition_every_reviewer(
        self,
    ) -> None:
        """Place each reviewer in exactly one exploration group and keep writable agents out of both."""
        granted = set(BASH_GRANTED_REVIEWER_NAMES)
        withheld = set(BASH_WITHHELD_REVIEWER_NAMES)

        self.assertEqual(set(REVIEWER_NAMES), granted | withheld)
        self.assertEqual(set(), granted & withheld)
        for name in REFACTORER_NAMES:
            with self.subTest(name=name):
                self.assertNotIn(name, granted | withheld)
                self.assertIsNone(claude_reviewer_tool_policy(name))

        claude_restricted = {
            name
            for name in AGENT_NAMES
            if "tools" in self._agent_source_metadata(name)["claude"]
        }
        self.assertEqual(set(REVIEWER_NAMES), claude_restricted)

        codex_sandboxed = {
            name
            for name in AGENT_NAMES
            if self._agent_source_metadata(name)["codex"].get("sandbox_mode")
            == "read-only"
        }
        self.assertEqual(set(REVIEWER_NAMES), codex_sandboxed)

    def test_repository_review_patch_refactorer_defines_writable_narrow_contract(
        self,
    ) -> None:
        """Allow the patch refactorer to apply only its explicitly bounded patch."""
        name = "review-patch-refactorer"
        agent_texts = {
            "shared": self._repository_text(Path("shared/agents") / f"{name}.md"),
            "claude": self._repository_text(CLAUDE_PROFILE_PATH / f"{name}.md"),
            "codex": self._repository_text(CODEX_PROFILE_PATH / f"{name}.toml"),
        }
        required_contracts = (
            "親が確認した reviewer の具体的な指摘",
            "Acceptance Criteria は満たされている。",
            "局所的で振る舞いを変えない修正",
            "指摘されていない箇所のついで修正",
            "追加した修正コミット SHA",
        )
        implementer_route = (
            "テストケース追加、期待値の再検討、仕様判断、設計変更、振る舞い判断が"
            "必要な場合はファイルを変更せず、元 Implementer への差し戻し"
        )
        metadata = self._agent_source_metadata(name)
        artifact = self._codex_agent_artifact_metadata(name)

        self.assertNotIn("sandbox_mode", metadata["codex"])
        self.assertNotIn("sandbox_mode", artifact)
        for platform, agent in agent_texts.items():
            with self.subTest(platform=platform):
                normalized_agent = "".join(agent.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized_agent)
                self.assertIn("".join(implementer_route.split()), normalized_agent)

    def _review_patch_refactorer_texts(self) -> dict[str, str]:
        name = "review-patch-refactorer"
        return {
            "shared": self._repository_text(Path("shared/agents") / f"{name}.md"),
            "claude": self._repository_text(CLAUDE_PROFILE_PATH / f"{name}.md"),
            "codex": self._repository_text(CODEX_PROFILE_PATH / f"{name}.toml"),
        }

    def test_repository_review_patch_refactorer_requires_structured_launch_inputs(
        self,
    ) -> None:
        """Patch only parent-adopted findings supplied as complete structured data."""
        required_inputs = (
            "指摘元 reviewer",
            "対象となる指摘ID",
            "指摘本文",
            "親が採用した修正条件",
            "対象 worktree、git branch、基準 commit、対象 commit 範囲",
            "Acceptance Criteria",
            "変更を許可するファイル",
            "変更を禁止するファイル",
            "削除・移動・新規作成の可否",
            "commit の要否",
            "必須検証 command",
        )
        adoption_conditions = (
            "親が指摘を確認し、修正対象として採用している。",
            "Acceptance Criteria を変更する必要がない。",
        )
        missing_input_route = "入力が不足する場合は推測で補わず、ファイルを変更せず"

        for platform, agent in self._review_patch_refactorer_texts().items():
            with self.subTest(platform=platform):
                normalized_agent = "".join(agent.split())
                for contract in required_inputs + adoption_conditions:
                    self.assertIn("".join(contract.split()), normalized_agent)
                self.assertIn(
                    "".join(missing_input_route.split()), normalized_agent
                )

    def test_repository_review_patch_refactorer_forbids_out_of_scope_changes(
        self,
    ) -> None:
        """Keep every edit inside adopted findings and parent-approved files."""
        prohibited_without_permission = (
            "親が個別に許可しない限り",
            "reviewer が明示していない問題の修正",
            "reviewer が明示していないテストケースの追加",
            "対象指摘の修正に不要な fixture や helper の追加",
            "ファイルの新規作成、削除、移動",
            "許可されていないファイルの変更",
            "テスト期待値の変更、削除、skip、弱体化",
            "新規依存の追加",
        )

        for platform, agent in self._review_patch_refactorer_texts().items():
            with self.subTest(platform=platform):
                normalized_agent = "".join(agent.split())
                for contract in prohibited_without_permission:
                    self.assertIn("".join(contract.split()), normalized_agent)

    def test_repository_review_patch_refactorer_returns_scoped_change_report(
        self,
    ) -> None:
        """Report changed/added/deleted/moved files and zero out-of-scope changes."""
        return_contracts = (
            "指摘IDごとの変更内容",
            "変更したファイル",
            "追加したファイル",
            "削除したファイル",
            "移動したファイル",
            "指摘外の変更が0件",
            "許可範囲外の変更が0件",
            "Acceptance Criteria と外部から観測可能な振る舞いを維持した根拠",
            "修正できなかった指摘と理由",
        )

        for platform, agent in self._review_patch_refactorer_texts().items():
            with self.subTest(platform=platform):
                normalized_agent = "".join(agent.split())
                for contract in return_contracts:
                    self.assertIn("".join(contract.split()), normalized_agent)

    def test_repository_review_patch_refactorer_removes_only_parent_approved_targets(
        self,
    ) -> None:
        """Remove only the excess elements the parent approved per finding id."""
        # 例外を書き足しても無条件規則の本文が残ることを別 pin で押さえる。
        # 例外句だけを pin すると、無条件規則ごと差し替えた版も green になる。
        unconditional_rule = "既存テストを削除、skip、弱体化しない。"
        # 無条件性を担うのは「だけ」なので、自己限定句を含む形で pin する。
        removal_exception = (
            "必須完了ゲートの指摘に基づき親が指摘IDごとに個別許可した"
            "重複テストの削除だけを例外とする"
        )
        removal_targets = (
            "親が指摘IDと対象を特定して個別許可した過剰要素（重複テスト、未使用要素、"
            "除去しても外部から観測可能な振る舞いが変わらない分岐・pass-through 層）の除去。"
        )
        approved_removal_constraints = (
            "### 除去を許可された場合",
            "許可された指摘IDと明示された除去対象だけを取り除く",
            "重複テストでは、残す側として指定されたテストを変更しない",
            "除去後に対象 AC を満たす実装と検証が残ることを実行結果で示す",
            "検証が失われる、または必須検証 command を green に保てない場合は、"
            "除去せず理由を親へ返す",
        )
        removal_report = (
            "除去した要素と、除去後も対象 AC を満たす実装と検証が残っている根拠"
        )

        for platform, agent in self._review_patch_refactorer_texts().items():
            with self.subTest(platform=platform):
                normalized_agent = "".join(agent.split())
                self.assertIn("".join(unconditional_rule.split()), normalized_agent)
                for contract in (
                    (removal_exception, removal_targets, removal_report)
                    + approved_removal_constraints
                ):
                    self.assertIn("".join(contract.split()), normalized_agent)

    def test_security_reviewer_is_defensive_and_detection_only(self) -> None:
        """Keep security review defensive, actionable, and inside its assigned scope."""
        paths = (
            REPOSITORY_ROOT / "shared/agents/security-side-effect-reviewer.md",
            REPOSITORY_ROOT / "plugins/claude/agents/security-side-effect-reviewer.md",
            REPOSITORY_ROOT
            / "plugins/codex/install/agents/security-side-effect-reviewer.toml",
        )
        required_contracts = (
            "攻撃コードや悪用手順の作成は一切行いません",
            "あなたは検出役です",
            "コードの修正は専門 agent が担当します",
            "指摘は修正担当がそのまま着手できる粒度・形式で出力してください",
            "レビュー範囲外の改善提案（命名、責務分離など）は行いません",
        )

        for path in paths:
            content = path.read_text(encoding="utf-8")
            for contract in required_contracts:
                self.assertIn(contract, content, path)


if __name__ == "__main__":
    unittest.main()
