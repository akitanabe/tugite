"""Real-repository contract tests for generated plugin assets."""

from __future__ import annotations

from pathlib import Path
import unittest

from build_plugin_assets_test_support import (
    AGENT_NAMES,
    CLAUDE_MODEL_PROFILES,
    CLAUDE_PROFILE_PATH,
    CODEX_MODEL_PROFILES,
    CODEX_PROFILE_PATH,
    DELEGATE_SKILL,
    GENERATED_MARKDOWN_WARNING,
    GENERATED_SKILL_REFERENCE_PATHS,
    GENERATED_SKILL_PATHS,
    READ_ONLY_TOOL_AGENT_NAMES,
    REPOSITORY_ROOT,
    RepositoryContractSupport,
    SHARED_SKILL_PATH,
    SHARED_SKILL_REFERENCE_PATHS,
    SKILL_REFERENCE_NAMES,
    generated_skill_path,
    generated_skill_reference_path,
    shared_skill_path,
    shared_skill_reference_path,
)


PLAN_SKILL = "plan-implementation-branches"
# 契約が要求する reference 構成をテスト側で明示的に宣言する。生成 mapping への
# 依存を避け、原稿が未整備の状態を「必要ファイルの欠落」として検出させる。
PLAN_REFERENCE_NAMES = (
    "branch-plan-schema.md",
    "branch-splitting.md",
    "plan-review.md",
)
DRAFT_SKILL = "draft-implementation-plan"
DRAFT_REFERENCE_NAMES = (
    "implementation-plan-schema.md",
    "plan-drafting.md",
    "adversarial-review.md",
    "overengineering-plan-review.md",
)
REVIEWER_FINDINGS_REFERENCE = "reviewer-findings.md"
# findings を返す reviewer だけが共通契約の対象。expert-selection-reviewer は起動可否の
# 審査、review-patch-refactorer は修正担当であり、指摘 Data を返す役割ではない。
FINDINGS_REVIEWER_NAMES = (
    "responsibility-boundary-reviewer",
    "test-quality-reviewer",
    "security-side-effect-reviewer",
    "writing-principles-reviewer",
    "over-engineering-reviewer",
    "plan-adversarial-reviewer",
)
# 6 原稿で「示す」（判定項目を持つ3原稿）と「示します」（持たない3原稿）に語尾が割れる
# ため、両方に共通する接頭辞までで値を切り詰めている。動詞を補うと、語尾が異なる側の
# 原稿で test_findings_reviewers_require_a_count_summary_and_evidence が失敗する。
FINDINGS_COUNT_REQUIREMENT = "指摘件数は0件でも必ず"
FINDINGS_EVIDENCE_REQUIREMENT = (
    "evidence（該当ファイルと行の引用 / 再現手順 / 参照した Data の path と id の"
    "いずれか）を示す"
)
# 出力形式の先頭に判定項目を持つ reviewer は、その項目へ件数を足す。判定項目と件数を
# 別行に分けると、親が 1 行で読み取れるというサマリ行の目的が崩れる。
VERDICT_LEADING_REVIEWER_SUMMARY_ITEMS = {
    "responsibility-boundary-reviewer": (
        "1. 全体判定と指摘件数（判定は指摘のうち最も重い判定に合わせる。指摘がなければ "
        "`問題なし`。指摘件数は0件でも必ず示す。別のサマリ行は追加しない）"
    ),
    "test-quality-reviewer": (
        "1. 判定と指摘件数（`Pass` / `Needs attention` / `Blocker`。"
        "指摘件数は0件でも必ず示す。別のサマリ行は追加しない）"
    ),
    "security-side-effect-reviewer": (
        "1. 判定と指摘件数（`Pass` / `Needs attention` / `Blocker`。"
        "指摘件数は0件でも必ず示す。別のサマリ行は追加しない）"
    ),
}
COUNT_ONLY_REVIEWER_SUMMARY_LINE = (
    "応答の冒頭に指摘件数のサマリ行を置いてください。指摘件数は0件でも必ず示します。"
    "判定項目は新設しません。"
)
COUNT_ONLY_REVIEWER_NAMES = (
    "writing-principles-reviewer",
    "over-engineering-reviewer",
    "plan-adversarial-reviewer",
)


class BuildPluginAssetsRepositoryContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _assert_qa_report_reference_files_exist(self) -> None:
        paths = (
            SHARED_SKILL_REFERENCE_PATHS["qa-report.md"],
            GENERATED_SKILL_REFERENCE_PATHS["claude"]["qa-report.md"],
            GENERATED_SKILL_REFERENCE_PATHS["codex"]["qa-report.md"],
        )
        for path in paths:
            self.assertTrue(
                (REPOSITORY_ROOT / path).is_file(),
                f"missing QA report reference: {path}",
            )

    def _read_qa_report_references(self) -> dict[Path, str]:
        self._assert_qa_report_reference_files_exist()
        return {
            SHARED_SKILL_REFERENCE_PATHS["qa-report.md"]: self._repository_text(
                SHARED_SKILL_REFERENCE_PATHS["qa-report.md"]
            ),
            GENERATED_SKILL_REFERENCE_PATHS["claude"][
                "qa-report.md"
            ]: self._repository_text(
                GENERATED_SKILL_REFERENCE_PATHS["claude"]["qa-report.md"]
            ),
            GENERATED_SKILL_REFERENCE_PATHS["codex"][
                "qa-report.md"
            ]: self._repository_text(
                GENERATED_SKILL_REFERENCE_PATHS["codex"]["qa-report.md"]
            ),
        }

    def _extract_qa_report_template(self, report: str) -> str:
        heading = "## 標準テンプレート"
        opening_fence = "```markdown\n"
        closing_fence = "\n```"
        self.assertEqual(1, report.count(heading))
        template_section = report.split(heading, 1)[1]
        self.assertEqual(1, template_section.count(opening_fence))
        fenced_content = template_section.split(opening_fence, 1)[1]
        self.assertIn(closing_fence, fenced_content)
        return fenced_content.split(closing_fence, 1)[0]

    def _assert_qa_report_template_excludes_raw_fields(self, template: str) -> None:
        forbidden_template_fields = (
            "Conversation:",
            "Prompt:",
            "Raw reviewer output:",
            "Raw command log:",
            "Full command log:",
            "Credential:",
            "Absolute path:",
            "Local checkout path:",
            "Integration checkout / commit",
        )
        for field in forbidden_template_fields:
            self.assertNotIn(field, template)

    def test_repository_skill_uses_progressive_disclosure(self) -> None:
        """Keep the core workflow lean and route each detailed phase explicitly."""
        main_texts = {
            SHARED_SKILL_PATH: self._repository_text(SHARED_SKILL_PATH),
            GENERATED_SKILL_PATHS["claude"]: self._repository_text(
                GENERATED_SKILL_PATHS["claude"]
            ),
            GENERATED_SKILL_PATHS["codex"]: self._repository_text(
                GENERATED_SKILL_PATHS["codex"]
            ),
        }
        reference_headings = {
            "implementation-branches.md": "# 実装枝の準備と委譲",
            "expert-selection.md": "# Expert 選択",
            "qa-and-integration.md": "# QA・修正・統合",
            "qa-report.md": "# 永続 QA レポート",
        }

        for path, main in main_texts.items():
            with self.subTest(path=path):
                self.assertLess(len(main.splitlines()), 300)
                for name in SKILL_REFERENCE_NAMES[DELEGATE_SKILL]:
                    self.assertIn(f"(references/{name})", main)
                for heading in reference_headings.values():
                    self.assertNotIn(heading, main)
                self.assertLess(
                    main.index("(references/implementation-branches.md)"),
                    main.index("(references/expert-selection.md)"),
                )
                self.assertLess(
                    main.index("(references/expert-selection.md)"),
                    main.index("先頭の枝だけを委譲する"),
                )
                self.assertLess(
                    main.index("先頭の枝だけを委譲する"),
                    main.index("(references/qa-and-integration.md)"),
                )
                normalized = "".join(main.split())
                conditional_reference = (
                    "永続QAレポートの出力条件を満たす場合だけ"
                    "[永続QAレポート](references/qa-report.md)を読む"
                )
                self.assertIn(conditional_reference, normalized)
                self.assertEqual(1, main.count("(references/qa-report.md)"))

        self._assert_qa_report_reference_files_exist()
        skills = self._repository_skill_texts()
        for name, heading in reference_headings.items():
            self.assertIn(heading, skills.source_references[name])
            self.assertIn(heading, skills.claude_references[name])
            self.assertIn(heading, skills.codex_references[name])
            self.assertFalse(
                skills.source_references[name].startswith(
                    GENERATED_MARKDOWN_WARNING
                )
            )
            self.assertTrue(
                skills.claude_references[name].startswith(
                    f"{GENERATED_MARKDOWN_WARNING}\n\n"
                )
            )
            self.assertTrue(
                skills.codex_references[name].startswith(
                    f"{GENERATED_MARKDOWN_WARNING}\n\n"
                )
            )

    def test_repository_writes_one_parent_qa_report_only_when_requested(
        self,
    ) -> None:
        """Generate one parent-owned report only after an explicit opt-in."""
        required_contracts = (
            "会話上の最終報告は常に行う。",
            "永続 QA レポートは任意",
            "入力語彙 `lite` / `standard(-adaptive)` / `strict(-adaptive)` / `strict-full`",
            "`direct` は対象外",
            "既定では生成しない",
            "ユーザーの明示的な要求",
            "repository instruction",
            "Acceptance Criteria",
            "いずれかが要求した場合だけ",
            "親の最終判断時に1回",
            "トップレベルの workflow run ごとに report は1つだけ生成",
            "複数の実装枝は同じ report へ列挙",
            "`Accepted`",
            "`Rejected`",
            "`Needs revision`",
            "未実行の検証",
            "未統合の状態",
            "最終判断は親だけが行う",
            "sanitize できない場合は生成しない",
            "生成しなかった理由を会話上の最終報告へ含める",
        )

        for path, report in self._read_qa_report_references().items():
            with self.subTest(path=path):
                normalized = "".join(report.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized)

    def test_repository_qa_report_creation_is_confined_and_non_overwriting(
        self,
    ) -> None:
        """Reject traversal and links, and never overwrite an existing report."""
        required_contracts = (
            "repository root 相対の `.agentic-qa/reports/<slug>.md`",
            "task ID または title",
            "空なら git branch",
            "Unicode NFKC",
            "前後の空白を除去",
            "ASCII lowercase",
            "非 `[a-z0-9]` の連続を `-`",
            "連続する `-` と前後の `-` を除去",
            "base は最大64文字",
            "`delegated-implementation`",
            "機密な入力名は使わず fallback",
            "Windows 予約名には `qa-` prefix",
            "`con`, `prn`, `aux`, `nul`, `com1`〜`com9`, `lpt1`〜`lpt9`",
            "path separator を許可しない",
            "`.` または `..` を許可しない",
            "絶対 path を許可しない",
            "reports 直下以外を許可しない",
            "`ＡＢＣ １２３` は `abc-123`",
            "title が `日本語`、git branch が `Feature QA` なら `feature-qa`",
            "title と git branch が `日本語` なら `delegated-implementation`",
            "`CON` は `qa-con`",
            "既存 file を上書きしない",
            "`<slug>-2.md`, `<slug>-3.md`",
            "最初の空き",
            "suffix 込みの stem は最大80文字",
            "base の末尾を切る",
            "出力先または候補が symlink、directory、非通常 file なら停止",
            "`.agentic-qa` と `reports` の各既存 ancestor component",
            "symlink を追わない `lstat` 相当",
            "symlink または directory 以外なら停止",
            "canonical repository root 外へ解決される場合は停止",
            "生成と削除の両方へ適用",
            "sanitized Markdown Data を先に完成",
            "symlink を追わない exclusive create 相当",
            "1回だけ書く",
            "競合時は書き込まず次の suffix を再選択",
            "安全な create Action を保証できない場合は生成しない",
            "workflow 内では既存 report を更新しない",
        )

        for path, report in self._read_qa_report_references().items():
            with self.subTest(path=path):
                normalized = "".join(report.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized)
                self.assertNotIn(
                    "".join(
                        "既存 report の更新はユーザーが対象 path を明示".split()
                    ),
                    normalized,
                )

    def test_repository_does_not_manage_or_delete_qa_reports_implicitly(
        self,
    ) -> None:
        """Leave Git management, retention, and deletion to explicit policy."""
        required_contracts = (
            "`agentic-qa-workflow` repository の template source と generated asset は tracked 配布物",
            "利用先 repository で生成する report instance",
            "既定では untracked / unstaged / uncommitted",
            "`.gitignore` と `.git/info/exclude` を自動変更しない",
            "`git status` に `??` として表示されてよい",
            "既定では `git add`、stage、commit しない",
            "ユーザーの明示的な要求または既存の repository policy",
            "既存の実装 commit へ黙って amend しない",
            "自動期限または自動 purge を行わない",
            "明示的な削除または repository policy まで保持",
            "reports 配下であることを確認してから削除",
            "通常の削除 commit では Git 履歴から機密情報を消去できない",
            "親の統合 checkout へ保存",
            "削除予定の worker worktree へ保存しない",
        )

        for path, report in self._read_qa_report_references().items():
            with self.subTest(path=path):
                normalized = "".join(report.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized)

    def test_repository_qa_report_persists_only_sanitized_evidence(self) -> None:
        """Persist only minimal reviewed evidence without secrets or raw transcripts."""
        prohibited_content = (
            "会話全文",
            "prompt",
            "reviewer の生出力",
            "command の全 log",
            "token",
            "password",
            "cookie",
            "Authorization",
            "private key",
            "`.env`",
            "credential 付き URL",
            "機密 query",
            "個人情報",
        )
        sanitized_evidence_contracts = (
            "file は repository 相対 path",
            "worktree は論理 ID、git branch、cleanup 状態",
            "Implementer は role 名",
            "command は sanitize 済み文字列、status、短い要約",
            "次の機密情報と生の証跡を保存しない",
            "絶対 path と local checkout path を保存しない",
            "git branch と file が敏感なら省略または sanitize",
            "保存直前に親が report 全体を確認",
        )

        for path, report in self._read_qa_report_references().items():
            with self.subTest(path=path):
                normalized = "".join(report.split())
                for contract in prohibited_content + sanitized_evidence_contracts:
                    self.assertIn("".join(contract.split()), normalized)

    def test_repository_qa_report_normalizes_untrusted_markdown_fields(
        self,
    ) -> None:
        """Render untrusted values as escaped single-line Markdown text."""
        required_contracts = (
            "untrusted field",
            "改行 `\\n` と control 文字を空白へ置換して単一行",
            "Markdown context に応じて metacharacter を escape",
            "HTML、link、image を plain text として escape",
            "`line 1\\nline 2` は `line 1 line 2`",
            "`<b>admin</b>` は `&lt;b&gt;admin&lt;/b&gt;`",
            "`[label](https://example.invalid)` は plain text として escape",
            "`![alt](https://example.invalid/image.png)` は plain text として escape",
        )

        for path, report in self._read_qa_report_references().items():
            with self.subTest(path=path):
                normalized = "".join(report.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized)

    def test_repository_qa_report_template_exposes_complete_parent_qa(self) -> None:
        """Expose every decision and verification gap needed for parent acceptance."""
        required_fields = (
            "Sanitized task ID / title",
            "Delegation policy",
            "Base commit",
            "Logical checkout ID / commit",
            "Implementation branches",
            "導出 mode と上書き後の mode の両方が読み取れるように",
            "降格には理由の記録を必須とする",
            "Acceptance Criteria → test",
            "Changed files",
            "Verification",
            "`Pass` / `Fail` / `Not run`",
            "`Not run` は理由必須",
            "Red / Green / Refactor",
            "Responsibility boundaries",
            "Test quality",
            "Writing principles",
            "Over-engineering",
            "Security / side effects",
            "Integrated diff review",
            "Residual risks",
            "Parent decision",
            "`Accepted` / `Rejected` / `Needs revision`",
            "判断理由",
            "Next action",
            "reviewer を起動しなかった場合も理由を記録",
            "対象 risk がないことは有効な理由",
            "最終判断は親だけが記入",
        )

        for path, report in self._read_qa_report_references().items():
            with self.subTest(path=path):
                normalized = "".join(report.split())
                for field in required_fields:
                    self.assertIn("".join(field.split()), normalized)

                template = self._extract_qa_report_template(report)
                required_template_fields = (
                    "Logical checkout ID / commit",
                    "Logical worktree ID",
                    "Branch (sanitized or omitted)",
                    "Implementer role",
                    "Risk level",
                    "Derived mode",
                    "Manual override",
                    "Sanitized command",
                    "Status",
                    "Short summary",
                )
                for field in required_template_fields:
                    self.assertIn(field, template)
                self._assert_qa_report_template_excludes_raw_fields(template)

                # The manual-override recording note is prose guidance for the parent,
                # not a field the parent copies into every report; it must live outside
                # the fenced template body (paired with the required_fields presence
                # check above, this proves the note is present but not inside the fence).
                normalized_template = "".join(template.split())
                manual_override_note = (
                    "導出 mode と上書き後の mode の両方が読み取れるように",
                    "降格には理由の記録を必須とする",
                )
                for fragment in manual_override_note:
                    self.assertNotIn(
                        "".join(fragment.split()), normalized_template
                    )

    def test_repository_writes_qa_report_after_cleanup_and_before_chat_report(
        self,
    ) -> None:
        """Persist cleanup outcomes before sending the required chat report."""
        skills = self._repository_skill_texts()
        main_texts = (
            skills.source_main,
            skills.claude_main,
            skills.codex_main,
        )
        cleanup_instruction = "cleanup の実施可否と結果を確定する"
        report_reference = "(references/qa-report.md)"
        final_report = "会話上の最終報告を行う"

        for main in main_texts:
            normalized = " ".join(main.split())
            self.assertIn(cleanup_instruction, normalized)
            self.assertIn(report_reference, normalized)
            self.assertIn(final_report, normalized)
            self.assertLess(
                normalized.index(cleanup_instruction),
                normalized.index(report_reference),
            )
            self.assertLess(
                normalized.index(report_reference),
                normalized.index(final_report),
            )

        required_reference_contracts = (
            "最終 gate 後に cleanup の実施可否と結果を確定してから",
            "出力条件を満たす場合だけ report を生成",
            "`Needs revision` などで worktree を保持する場合も cleanup 状態と理由を記録",
        )
        for path, report in self._read_qa_report_references().items():
            with self.subTest(path=path):
                normalized = "".join(report.split())
                for contract in required_reference_contracts:
                    self.assertIn("".join(contract.split()), normalized)

    def test_repository_continues_revisions_but_finalizes_unintegrated_termination(
        self,
    ) -> None:
        """Continue revisions; finalize only an explicit unintegrated decision."""
        skills = self._repository_skill_texts()
        main = "".join(skills.source_main.split())
        qa_reference = skills.source_references["qa-and-integration.md"]
        qa_and_integration = "".join(qa_reference.split())
        unintegrated_section = qa_reference[
            qa_reference.index("## 未統合で終了する場合") : qa_reference.index(
                "## 責務境界"
            )
        ]
        normalized_unintegrated_section = "".join(unintegrated_section.split())
        revision_continuation = (
            "QA 修正を続ける場合は手順7の修正経路を継続する。"
        )
        unintegrated_termination = (
            "親が未統合の枝について `Rejected` / `Needs revision` を最終判断とし、"
            "top-level workflow を終了する場合は、手順9へ進む。"
        )
        finalization = (
            "全枝を完了した場合、または手順8で未統合のまま終了する場合は、"
            "適用可能な統合済み diff review と最終検証を行い、親の最終判断を確定する。"
        )
        cleanup_decision = (
            "最終 gate 後に、各 worker worktree の cleanup の実施可否と結果を確定する。"
        )
        final_decision_invariant = (
            "全ての委譲 mode で、親の最終判断を省略しない。"
            "受け入れた枝では統合後の検証を省略しない。"
        )
        main_contracts = (
            revision_continuation,
            unintegrated_termination,
            finalization,
            cleanup_decision,
            final_decision_invariant,
        )
        reference_contracts = (
            "通常の `Needs revision` は上の修正先へ差し戻し、top-level workflow を継続する。",
            "親が未統合の枝について `Rejected` / `Needs revision` を最終判断とし、top-level workflow を終了する場合だけ",
            "実行可能な検証を行い",
            "未実行の検証、未統合の理由、worktree を保持する理由",
            "Data として記録",
            "main の手順9へ戻る",
        )

        for contract in main_contracts:
            self.assertIn("".join(contract.split()), main)
        for contract in reference_contracts:
            self.assertIn("".join(contract.split()), qa_and_integration)
        self.assertNotIn("cleanup", normalized_unintegrated_section)
        self.assertNotIn(
            "".join(
                "全ての委譲 mode で、親による統合後の検証と最終的な受け入れ判断を省略しない。".split()
            ),
            main,
        )

        normalized_termination = "".join(unintegrated_termination.split())
        normalized_finalization = "".join(finalization.split())
        normalized_cleanup_decision = "".join(cleanup_decision.split())
        self.assertLess(
            main.index(normalized_termination),
            main.index(normalized_finalization),
        )
        self.assertLess(
            main.index(normalized_finalization),
            main.index(normalized_cleanup_decision),
        )
        self.assertLess(
            main.index(normalized_cleanup_decision),
            main.index("(references/qa-report.md)"),
        )

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

    def test_repository_tool_restricted_reviewers_platforms_reject_file_modification(
        self,
    ) -> None:
        """Publish platform-enforced read-only settings with each reviewer definition."""
        for name in READ_ONLY_TOOL_AGENT_NAMES:
            with self.subTest(name=name):
                source_metadata = self._agent_source_metadata(name)
                claude_artifact = self._repository_text(
                    CLAUDE_PROFILE_PATH / f"{name}.md"
                )
                codex_artifact = self._codex_agent_artifact_metadata(name)

                self.assertEqual(
                    ["Read", "Grep", "Glob"],
                    source_metadata["claude"]["tools"],
                )
                self.assertEqual(
                    ["Bash", "Edit", "Write", "NotebookEdit"],
                    source_metadata["claude"]["disallowed_tools"],
                )
                self.assertIn("tools: Read, Grep, Glob\n", claude_artifact)
                self.assertIn(
                    "disallowedTools: Bash, Edit, Write, NotebookEdit\n",
                    claude_artifact,
                )
                self.assertEqual(
                    "read-only", source_metadata["codex"]["sandbox_mode"]
                )
                self.assertEqual("read-only", codex_artifact["sandbox_mode"])

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

    def test_repository_workflows_route_specialists_and_require_mandatory_completion_gates(
        self,
    ) -> None:
        """Require both completion gates without making risk-based specialists mandatory."""
        workflows = self._repository_workflow_texts()
        risk_routes = {
            "responsibility-boundary-reviewer": "責務混在、設計境界、分散した副作用",
            "test-quality-reviewer": "弱いテスト、欠けているケース、実装詳細に依存したテスト",
            "security-side-effect-reviewer": (
                "外部 I/O、破壊的操作、機密データ、セキュリティ影響"
            ),
        }
        required_rules = (
            "ユーザーが専門 reviewer を明示的に要求した場合。",
            "親が reviewer の責務と一致する具体的なリスクを特定した場合。",
            "専門 reviewer を汎用コードレビューの代替にしない。",
            "専門 reviewer は mode 名だけを理由に一律起動しない。",
            "対象リスクがない専門 reviewer を無条件で起動しない。",
            "対象リスクと review 範囲を明示する。",
            "- 必須完了ゲート",
            "この表の2本は必須の完了ゲートであり、上記の任意起動条件の対象外とする。",
            (
                "`writing-principles-reviewer` は `lite` / `standard` / `strict` の"
                "すべてで、各実装枝を受け入れる前に必ず起動する。"
            ),
            (
                "`over-engineering-reviewer` は `standard` / `strict` の枝でだけ、"
                "受け入れる前に必ず起動し"
            ),
            "ゲート間の起動順は定めない。",
            "reviewer は最終的な受け入れ判断を行わない。",
            "親が diff、テスト、検証結果を確認し、最終的な受け入れを判断する。",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized_workflow = "".join(workflow.split())

                for name, risk in risk_routes.items():
                    self.assertIn(f"| `{name}` | {risk} |", workflow)
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized_workflow)
                self.assertNotIn("`writing-principles-refactorer`", workflow)

    def test_repository_over_engineering_gate_applies_only_to_standard_and_strict(
        self,
    ) -> None:
        """Apply the over-engineering gate to standard and strict branches only."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        # 適用 mode の正本はゲート表なので、表の行と mode 文言だけを pin する。
        # `lite` を除外する根拠の散文は、文言の微修正だけで red になる割に
        # 「`lite` へ誤って適用される」欠陥をこの2つより先に検出しない。
        gate_rows = (
            (
                "| 記述原則 | `writing-principles-reviewer` "
                "| `lite` / `standard` / `strict` "
                "| How/What/Why/Why Not の配置、命名、説明 |"
            ),
            (
                "| 過剰実装 | `over-engineering-reviewer` "
                "| `standard` / `strict` "
                "| 除去しても AC と制約を満たせるテストと実装 |"
            ),
        )
        mode_rules = (
            "適用 mode の正本はこの表とする。",
            (
                "`over-engineering-reviewer` は `standard` / `strict` の枝でだけ、"
                "受け入れる前に必ず起動し、`lite` では起動しない。"
            ),
        )
        # 根拠の散文は上記方針どおり広くは pin しない。`lite` の親 QA 範囲を広げたときに
        # 除外根拠が旧範囲を指したまま残る矛盾だけを、根拠が依存する2点で検出する。
        exclusion_grounds = (
            (
                "除去許可の判定に必要な網羅性の確認"
                "（観点2: 境界値・異常系・例外経路・分岐・期待値の根拠）が課されない。"
            ),
            (
                "`lite` が課すのは AC と検証の対応の識別までであり、"
                "その検証が AC をどこまで支えているかの判断は課さない。"
            ),
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in gate_rows + mode_rules + exclusion_grounds:
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_over_engineering_gate_bounds_parent_approved_removal(
        self,
    ) -> None:
        """Approve each removal per finding id and return unlocatable coverage."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        approval_conditions = (
            "### 過剰実装ゲートの除去許可",
            "親は指摘IDごとに次をすべて確認する。",
            "除去後も対象 AC を満たす実装と検証が残ること",
            "除去しても外部から観測可能な振る舞いと公開契約が変わらないこと",
            "除去する操作が局所的で、周辺の再設計を必要としないこと",
            "1つでも満たさない場合は元 Implementer へ差し戻す",
        )
        type_c_route = (
            "類型 C（残る検証を特定できないテスト）は `review-patch-refactorer` へ渡さず、"
            "元 Implementer へ差し戻す"
        )
        duplicate_test_identification = (
            "削除する側と残す側をファイルとテスト名で特定",
            "個別許可のない除去を行わせない",
        )
        launch_inputs = (
            "除去を許可する場合の、指摘IDごとの除去対象と残す対象",
            "pass-through 層の除去では、付け替えが必要な呼び出し箇所のファイルを"
            "変更許可リストへ含める",
        )
        # 「テストケースの削除」単体は親の再確認リストにも現れるため、
        # 変更制約側へ入ったことは文全体で pin しないと判定できない。
        scope_constraint = (
            "新規作成・削除・移動、指摘外のテストケース追加、テストケースの削除、"
            "fixture や helper の追加をさせない。"
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in (
                    approval_conditions
                    + duplicate_test_identification
                    + launch_inputs
                    + (type_c_route, scope_constraint)
                ):
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_workflow_passes_selected_reviewer_context(self) -> None:
        """Pass baseline review data plus purpose-selected context, never the whole repo."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        baseline_inputs = (
            "レビュー対象とリスクに応じて、必要な周辺コンテキストを選択して reviewer へ渡す",
            "タスクの目的",
            "Acceptance Criteria",
            "変更対象と commit 範囲",
            "変更ファイル一覧と diff text",
            "reviewer に確認させる具体的な観点",
        )
        optional_inputs = (
            "関連する interface、type、schema",
            "主要な呼び出し元",
            "関連する既存テスト",
            "周辺の directory 構造",
            "generated file とその生成元",
            "変更対象に関係する既存実装",
            "外部指示",
            "`AGENTS.md`",
            "`CLAUDE.md`",
            "`README.md`",
        )
        selection_constraints = (
            "repository 全体を無条件に渡さない",
            "reviewer の役割に関係しない情報を過剰に渡さない",
            "親の結論だけを渡さず、reviewer が独立して判断できる一次情報を渡す",
            "周辺コードを渡す場合は、なぜ必要なのかを明示する",
            "外部指示と repository 内の指示が競合する場合は、優先関係を明示する",
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in (
                    baseline_inputs + optional_inputs + selection_constraints
                ):
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_specialist_reviewers_accept_parent_selected_context(
        self,
    ) -> None:
        """Use parent-selected context as evidence without widening the review scope."""
        reviewer_sources = (
            "responsibility-boundary-reviewer",
            "test-quality-reviewer",
            "security-side-effect-reviewer",
        )
        required_contracts = (
            "親が選択した周辺コンテキスト",
            "指摘範囲を広げる理由にしない",
        )

        for name in reviewer_sources:
            with self.subTest(name=name):
                source = self._repository_text(Path("shared/agents") / f"{name}.md")
                for contract in required_contracts:
                    self.assertIn(contract, source)

    def test_repository_decision_corpus_extends_reviewer_context(self) -> None:
        """Evaluate purpose-selected reviewer context with independent primary evidence."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        eval_06 = corpus.split(
            "## EVAL-06: 責務混在が見える返却 diff",
            1,
        )[1].split("## EVAL-07:", 1)[0]
        required_contracts = (
            "周辺コンテキストを選択し、必要な理由と併せて渡す",
            "repository 全体を無条件に渡す",
            "一次情報を渡さない",
            "選択理由を明示し",
        )

        for contract in required_contracts:
            with self.subTest(contract=contract):
                self.assertIn(contract, eval_06)

    def test_repository_decision_corpus_requires_read_only_writing_review_gate(
        self,
    ) -> None:
        """Evaluate the mandatory writing review as a read-only post-return gate."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        common_responsibilities = corpus.split(
            "### 全委譲ケースで親が保持する責任",
            1,
        )[1].split("## 共通の手動評価手順", 1)[0]
        eval_08 = corpus.split(
            "## EVAL-08: 機能的に green だが記述原則を外す差分",
            1,
        )[1].split("## EVAL-24:", 1)[0]

        section_boundaries = {
            "expected decision": ("**期待する判断**", "**必須動作**"),
            "required actions": ("**必須動作**", "**禁止動作**"),
            "prohibited actions": ("**禁止動作**", "**許容される差異**"),
            "manual checks": ("**手動評価項目**", None),
        }
        eval_sections = {}
        for name, (start, end) in section_boundaries.items():
            self.assertEqual(1, eval_08.count(start))
            section = eval_08.split(start, 1)[1]
            if end is not None:
                self.assertEqual(1, section.count(end))
                section = section.split(end, 1)[0]
            eval_sections[name] = section

        with self.subTest(contract="retired agent name"):
            self.assertNotIn("writing-principles-refactorer", corpus)
        with self.subTest(contract="retired completion gate role"):
            self.assertNotIn("記述 refactorer", corpus)

        for contract in (
            "`writing-principles-reviewer`",
            "`lite`、`standard`、`strict`",
            "必須の完了ゲート",
            "各実装枝を受け入れる前",
        ):
            with self.subTest(
                section="common responsibilities",
                contract=contract,
            ):
                self.assertIn(contract, common_responsibilities)

        section_contracts = {
            "expected decision": (
                "専門 reviewer を追加せず",
                "`writing-principles-reviewer` を最終差分へ起動する",
                "reviewer は自身で変更せず",
                "`no-change` または指摘ID付きの Data",
                "親が各指摘ID",
                "修正先または不採用",
            ),
            "required actions": (
                "親が先に diff と test",
                "`review-patch-refactorer` へ渡す",
                "元 Implementer へ差し戻す",
                "修正後は親QA",
                "reviewer 再確認",
            ),
            "prohibited actions": (
                "`writing-principles-reviewer` 自身にファイル変更",
                "reviewer の指摘を親が確認せず",
                "修正先の選択や不採用判断を reviewer に委ねる",
                "責務・test・security reviewer を一律起動する",
                "reviewer の判定を親の受け入れ判断に置き換える",
            ),
            "manual checks": (
                "read-only の `writing-principles-reviewer` を必須ゲート",
                "`no-change` または指摘ID付き Data",
                "親が各指摘ID",
                "`review-patch-refactorer`、元 Implementer、不採用",
                "修正後に親QAと reviewer 再確認",
                "親が最終受け入れ判断",
            ),
        }
        for section_name, contracts in section_contracts.items():
            for contract in contracts:
                with self.subTest(section=section_name, contract=contract):
                    self.assertIn(contract, eval_sections[section_name])

    def test_repository_mandatory_gates_accept_no_change_result(self) -> None:
        """Pass any mandatory gate whose review reports no findings."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        required_contracts = (
            "no-change",
            "指摘が0件",
            "正常なゲート通過結果",
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_mandatory_gates_receive_parent_collected_bounded_data(
        self,
    ) -> None:
        """Review only changed behavior using evidence collected by the parent."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        required_contracts = (
            "`git diff`",
            "`git status`",
            "commit log",
            "テスト結果",
            "親が取得",
            "Data として各必須完了ゲートの reviewer へ渡す",
            "基準 commit からの diff が導入または悪化させた問題",
            "既存問題を広く探索しない",
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_mandatory_gates_resolve_structured_findings_before_acceptance(
        self,
    ) -> None:
        """Block acceptance until every identified finding has a recorded outcome."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        required_contracts = (
            "指摘ID",
            "構造化 Data",
            "各指摘ID",
            "修正先または不採用",
            "判断を記録",
            "reviewer の指摘が0件",
            "すべての指摘が修正され、再確認を通過",
            "親が不採用とした指摘について、理由が記録",
            "未解決または判断未記録の指摘がある枝を受け入れない",
            "`review-patch-refactorer` による修正後",
            "その枝で適用されるすべての必須完了ゲートを再実行",
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_workflow_defines_review_patch_routing_boundary(self) -> None:
        """Patch only green implementations with concrete, behavior-preserving findings."""
        workflows = self._repository_workflow_texts()
        startup_conditions = (
            "専門 reviewer（必須完了ゲートの reviewer を含む）の具体的な指摘が存在する。",
            "Acceptance Criteria は満たされている。",
            "機能的なテストは green である。",
            "修正範囲が局所的である。",
            "仕様の再解釈を必要としない。",
            "新機能追加ではない。",
            "振る舞いを維持したまま修正できる。",
            "reviewer が修正方針または問題箇所を明示している。",
            "evidence を欠く指摘は、「必須完了ゲート」の evidence を欠く指摘の扱いに従い、"
            "親が evidence を補って通常の判断へ戻している。",
        )
        implementer_routes = (
            "Acceptance Criteria 未達",
            "仕様誤解",
            "機能欠落",
            "テスト失敗",
            "正常系・異常系・境界値不足",
            "振る舞い変更が必要",
            "テストケース追加",
            "ケース追加や期待値の再検討が必要",
            "仕様判断",
            "設計変更",
            "振る舞い判断",
            "`strict` mode の Red / Green / Refactor 継続",
            "過剰要素の除去に仕様判断、AC の再解釈、振る舞い変更が必要",
            "失う AC が特定できないテストの除去",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized_workflow = "".join(workflow.split())

                for condition in startup_conditions:
                    self.assertIn("".join(condition.split()), normalized_workflow)
                for route in implementer_routes:
                    self.assertIn("".join(route.split()), normalized_workflow)

    def test_repository_workflow_bounds_review_patch_inputs_and_parent_scope_qa(
        self,
    ) -> None:
        """Launch the patch refactorer with bounded data and re-verify scope on return."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        launch_contracts = (
            "親が指摘を確認し、修正対象として採用している。",
            "Acceptance Criteria を変更する必要がない。",
            "指摘元 reviewer、対象となる指摘ID、指摘本文",
            "親が採用した修正条件",
            "変更を許可するファイルと変更を禁止するファイル",
            "削除・移動・新規作成の可否と commit の要否",
            "必須検証 command",
            "推測で補わず、ファイルを変更せず親へ返す",
        )
        # 正規化比較は行境界を消すため、行単体の pin は限定句を行全体へ前置した
        # 劣化版も部分一致で通してしまう。前の bullet と `-` マーカーまで含めて
        # 行頭を固定する。
        parent_scope_qa = (
            "自己申告だけを信用せず",
            "基準 commit からの変更ファイル一覧と diff",
            "- 許可範囲外の変更がないこと\n"
            "- 親が個別に許可していないファイルの追加・削除・移動がないこと",
            "reviewer 指摘外の変更がないこと",
            "- 親が個別に許可していないテストケースの削除がないこと\n"
            "- テストケースの追加・変更、期待値、skip 設定の変更がないこと",
            "除去を許可した場合は、除去対象が許可した指摘IDと一致し、"
            "対象 AC を満たす実装と検証が残っていること",
            "focused test と関連する全体検証が green であること",
        )
        relaxations_beyond_removal = (
            "親が個別に許可していないテストケースの追加",
            "親が個別に許可していない期待値",
            "親が個別に許可していないskip",
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in launch_contracts + parent_scope_qa:
                    self.assertIn("".join(contract.split()), normalized_workflow)
                for relaxation in relaxations_beyond_removal:
                    self.assertNotIn(
                        "".join(relaxation.split()), normalized_workflow
                    )

    def test_repository_decision_corpus_bounds_review_patch_scope(self) -> None:
        """Evaluate bounded refactorer inputs and zero out-of-scope changes."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        eval_08 = corpus.split(
            "## EVAL-08: 機能的に green だが記述原則を外す差分",
            1,
        )[1].split("## EVAL-24:", 1)[0]
        required_contracts = (
            "指摘元 reviewer、指摘ID、指摘本文、親が採用した修正条件、変更を許可するファイル",
            "指摘外変更、許可範囲外変更、ファイルの追加・削除・移動が0件",
            "指摘外の修正、テストケース追加、ファイルの新規作成・削除・移動をさせる",
        )

        for contract in required_contracts:
            with self.subTest(contract=contract):
                self.assertIn(contract, eval_08)

    def test_repository_mandatory_gates_recheck_every_fix_before_acceptance(
        self,
    ) -> None:
        """Return every fix route to parent QA and the mandatory completion gates."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        required_contracts = (
            "`review-patch-refactorer` または元 Implementer による修正後",
            "親が変更後の diff とテスト結果を確認",
            "その枝で適用されるすべての必須完了ゲートを再実行",
            "再確認を通過",
            "枝を受け入れない",
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_mandatory_gates_do_not_ground_passage_in_missing_evidence(
        self,
    ) -> None:
        """Withhold gate passage on findings whose evidence the parent cannot verify."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        required_contracts = (
            "[Reviewer findings の共通契約](reviewer-findings.md)",
            "evidence を欠く指摘は、単独でゲート通過の根拠にしない。",
            "該当ファイルと行の引用・再現手順・参照した Data の path と id のいずれかを、"
            "自分が読んだ diff・テスト結果・repository の現状から特定できる場合は、"
            "親が evidence を補って通常の判断へ戻す。",
            "この扱いは必須完了ゲートの reviewer に限らず、"
            "「専門 reviewer」節の reviewer を含む指摘全般に適用する。",
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_distribution_does_not_reference_retired_agent_names(self) -> None:
        """Remove retired names from every distributed source and generated surface."""
        paths = (
            REPOSITORY_ROOT / "shared",
            REPOSITORY_ROOT / "plugins",
            REPOSITORY_ROOT / "scripts",
            REPOSITORY_ROOT / "tests",
        )
        retired_names = (
            "refactor-patch-" + "agent",
        )

        for path in paths:
            for file_path in path.rglob("*"):
                if not file_path.is_file():
                    continue
                content = file_path.read_text(encoding="utf-8")
                for name in retired_names:
                    self.assertNotIn(name, content, file_path)

    def test_repository_generated_agents_match_canonical_inventory(self) -> None:
        """Publish the reviewer under its new name without retaining old agent assets."""
        expected_claude = {f"{name}.md" for name in AGENT_NAMES}
        expected_codex = {f"{name}.toml" for name in AGENT_NAMES}
        actual_claude = {
            path.name
            for path in (REPOSITORY_ROOT / CLAUDE_PROFILE_PATH).glob("*.md")
        }
        actual_codex = {
            path.name
            for path in (REPOSITORY_ROOT / CODEX_PROFILE_PATH).glob("*.toml")
        }

        self.assertEqual(expected_claude, actual_claude)
        self.assertEqual(expected_codex, actual_codex)

    def test_repository_workflows_select_delegation_modes_without_crossing_direct_boundary(
        self,
    ) -> None:
        """Select delegation modes while keeping direct work outside the skill."""
        workflows = self._repository_workflow_texts()
        required_rules = (
            "委譲の決定は次の3層に分ける。層をまたいで並列に選ばない。",
            "経路の選択 — `direct`（この skill の外）か、委譲（この skill）か。",
            "配分方針の選択 — 委譲する場合に、配分方針 `policy` と基準 `baseline` を決める。",
            "枝 mode の導出 — `policy`、`baseline`、枝の `risk.level` から枝ごとの mode を導く。",
            "`direct` は親が実装する、この skill の外にある経路である。",
            "委譲 mode ではないため、配分方針や枝 mode と同じ層に並べて選ばない。",
            "タスク規模だけでこの skill を発火しない。",
            "`direct` が明示された場合も、この skill を発火しない。",
            "`lite` / `standard(-adaptive)` / `strict(-adaptive)` / `strict-full` の明示は"
            "委譲要求を兼ねる。",
            "委譲だけが明示され mode が指定されていない場合は `{adaptive, standard}` を選ぶ。",
            "`lite` を自動選択しない。",
            "`direct` と委譲が同時に指定された場合は、実装前にユーザーへ確認する。",
            "委譲 mode の強度は `lite < standard < strict` とする。",
            "`direct` から委譲へ変更する場合は、ユーザーへ確認する。",
            "仕様が曖昧な場合は mode を選ぶ前に実装を止め、ユーザーへ確認する。",
            "`lite` の選択条件を満たさなくなった場合は `standard` 以上へ引き上げる。",
            "`standard` では扱えないリスクが判明した場合は `strict` へ引き上げる。",
        )
        route_contracts = (
            (
                "| `direct` | — | — |",
                "この skill を発火しない skill 外の経路。委譲要求がなく、仕様が明確で"
                "影響範囲が閉じ、親が直接処理する変更。",
            ),
        )
        obsolete_classifications = (
            "枝の種別",
            "軽い修正・明確な仕様",
            "通常実装（既定）",
            "重要・高リスク実装",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized_workflow = "".join(workflow.split())

                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized_workflow)
                for route, contract in route_contracts:
                    self.assertIn(route, workflow)
                    self.assertIn("".join(contract.split()), normalized_workflow)
                for classification in obsolete_classifications:
                    self.assertNotIn(classification, workflow)

    def test_repository_workflows_split_delegation_mode_into_policy_and_baseline(
        self,
    ) -> None:
        """Treat adaptive as an allocation policy over the existing branch modes."""
        workflows = self._repository_workflow_texts()
        required_rules = (
            "配分方針  policy   : fixed | adaptive",
            "基準      baseline : lite | standard | strict",
            "枝 mode            : lite | standard | strict",
            "policy / baseline と枝の risk.level から導出する",
            "`adaptive` は新しい実装フローではなく、既存の `lite` / `standard` / `strict` を"
            "枝へ割り当てる配分方針である。",
            "枝へ割り当てられた後は、その枝を既存の各 mode のフローで実行する。",
            "`policy: fixed` は、全枝固定であることを明示的に表現する語彙だけに割り当てる。",
            "それ以外の語彙と mode 未指定はすべて `adaptive` へ写す。",
            "今後語彙を追加する場合の既定も `adaptive` とする。",
            "`policy: adaptive` では、`baseline` と枝の `risk.level` の決定表で"
            "枝ごとの mode を導出する。",
            "決定表の正本は [Branch Plan の受け入れ](references/branch-plan-intake.md) とする。",
            "`policy: fixed` では導出を行わず、全枝へ `baseline` をそのまま適用する。",
        )
        vocabulary_rows = (
            (
                "| 指定なし | `adaptive` | `standard` |",
                "通常利用のデフォルト。mode 未指定の明示的な委譲でもこれを選ぶ。",
            ),
            (
                "| `standard` / `standard-adaptive` | `adaptive` | `standard` |",
                "通常の実装委譲。",
            ),
            (
                "| `strict` / `strict-adaptive` | `adaptive` | `strict` |",
                "全体として厳格な確認を要求するが、明らかに低リスクの枝まで一律 `strict` に"
                "しない。`standard-adaptive` より保守的に導出する。",
            ),
            (
                "| `strict-full` | `fixed` | `strict` |",
                "全枝へ `strict` を固定適用する。枝ごとの導出を行わない。",
            ),
            (
                "| `lite` | `fixed` | `lite` |",
                "全枝を軽量フローで処理する。枝ごとの導出を行わない。ユーザーが明示し、"
                "仕様が明確で影響範囲が局所的、容易に戻せる変更にだけ選ぶ。",
            ),
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized_workflow = "".join(workflow.split())

                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized_workflow)
                for row, contract in vocabulary_rows:
                    self.assertIn(row, workflow)
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_workflows_bound_mode_downgrade_ban_to_allocation_policy(
        self,
    ) -> None:
        """Ban downgrades of the allocation policy, not of derived branch modes."""
        workflows = self._repository_workflow_texts()
        required_rules = (
            "引き下げ禁止の対象は配分方針 `{policy, baseline}` とする。",
            "ユーザーが明示した `baseline` を親都合で引き下げない。",
            "`policy` を親都合で `fixed` から `adaptive` へ変えない。",
            "枝への mode 割り当ては決定表による導出結果であり、引き下げに当たらない。",
            "導出表を逸脱した割り当てだけを引き上げ / 引き下げとして扱う。",
            "mode を引き上げた場合は、その具体的なリスクをユーザーへ報告する。",
            "導出結果より高い mode で枝を実行する場合も、枝単位で具体的なリスクを"
            "ユーザーへ報告する。",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized_workflow = "".join(workflow.split())
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized_workflow)

    def test_repository_workflows_present_branch_allocation_before_delegating(
        self,
    ) -> None:
        """Show the resolved allocation before delegating and gate strict-full."""
        skills = self._repository_skill_texts()
        workflows = self._repository_workflow_texts()
        required_rules = (
            "## 実行前サマリー",
            "導出後、委譲開始前に次を提示する。",
            "解決後の配分方針。`strict` を指定したユーザーが、その場で `strict-adaptive` "
            "として解釈されたことを確認できるようにする。",
            "枝 mode ごとの件数。",
            "各枝の `risk.level`、導出した mode、手動上書きの有無。",
            "Mode: standard-adaptive  (policy: adaptive / baseline: standard)",
            "Branch allocation:\n  strict   1\n  standard 3\n  lite     1",
            "1. authorization-check  high    → strict",
            "4. api-response         low     → lite → standard  (override)",
            "5. label-text           low     → lite",
            "枝 mode ごとの件数は、手動上書き後の実効 mode を集計する。",
            "各枝の行では、上書きがある場合に「導出 mode → 上書き後の mode」の両方を示す。",
            "`strict-full`（`{fixed, strict}`）は枝数に比例してコストが増えるため、"
            "枝数を明示したユーザー確認を委譲開始条件とする。",
            "確認が得られるまで委譲を開始しない。",
            "実行前サマリーを提示する。",
            "`strict-full` では枝数を明示したユーザー確認を得るまで委譲を開始しない。",
            "会話上の最終報告を行う。採用した配分方針と枝ごとの mode を含める。",
            "導出した枝 mode は Branch Plan へ書き戻さず、実行 Data として保持して"
            "最終報告で報告する。",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized_workflow = "".join(workflow.split())
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized_workflow)

        for main in (skills.source_main, skills.claude_main, skills.codex_main):
            with self.subTest(main=main[:40]):
                self.assertLess(
                    main.index("実行前サマリーを提示する"),
                    main.index("先頭の枝だけを委譲する"),
                )

    def test_repository_workflows_apply_mode_specific_qa_and_parent_verification(
        self,
    ) -> None:
        """Apply each delegation mode's QA strength and retain parent verification."""
        workflows = self._repository_workflow_texts()
        mode_contracts = (
            (
                "| `lite` |",
                "親は返却の diff とテストを確認し、Acceptance Criteria に対応する振る舞いが"
                "検証されていることを確かめ、focused test またはタスクで指定された成功条件で"
                "green を確認する。",
            ),
            (
                "| `standard` |",
                "AC→テスト対応表、境界値、異常系、Red 時点の失敗出力を要求する。",
            ),
            (
                "| `strict` |",
                "テスト計画→失敗テスト→実装→Refactor の段階ゲートに分ける。",
            ),
        )
        required_rules = (
            "- 委譲 mode: <この枝に導出された枝 mode。lite / standard / strict>",
            "`lite` では、親が明示した場合だけ AC 対応表と Red 時点の失敗出力を付けること。",
            "`standard` では、Red 時点の失敗出力と",
            "「AC-n → それを検証するテスト名 → 期待値の根拠（仕様のどこから導いたか）」"
            "の対応表を必ず付けること。",
            "最終返却には `standard` と同じ AC 対応表と Red 証跡を含める。",
            "`standard` と `strict` では全観点を手を動かして確認する。",
            (
                "`lite` では観点0（diff を読む）、観点5（自分で green を確認）、"
                "Acceptance Criteria に対応する振る舞いが検証されていることの確認へ絞ってよい。"
            ),
            (
                "`lite` のこの確認は親が diff と検証結果から行うものであり、"
                "Implementer への AC 対応表や Red 証跡の要求に置き換えない。"
            ),
            (
                "検証手段はテストに限定せず、プロジェクトまたはタスクで指定された成功条件"
                "（自動テスト、type check、lint、build、静的解析、実行結果の確認、"
                "手動確認手順、snapshot 比較、API レスポンス確認など）を使う。"
            ),
            "検証 command が成功したことだけを完了根拠にしない。",
            (
                "親は「どの Acceptance Criteria を」「どのテストまたは確認手順で」"
                "「どの結果によって」満たしたと判断したかを説明できる状態にする。"
            ),
            "全ての委譲 mode で、親による統合後の検証と最終的な受け入れ判断を省略しない。",
            "`direct` でも、親は必要なテストと検証を実行し、diff review と最終報告を行う。",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized_workflow = "".join(workflow.split())

                for mode, contract in mode_contracts:
                    self.assertIn(mode, workflow)
                    self.assertIn("".join(contract.split()), normalized_workflow)
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized_workflow)

    def test_repository_workflows_limit_green_red_evidence_to_regression_tests(
        self,
    ) -> None:
        skills = self._repository_skill_texts()
        implementation_contracts = (
            "新機能または未実装仕様を検証する test は Red 必須",
            "既存挙動を固定する regression test",
            "追加時点で Green",
            "既存挙動を固定する追補 test であること",
            "対応する AC",
            "期待値の根拠",
            "既存実装がすでに仕様を満たしていたこと",
            "形式的な Red を作るために本番 code を一時変更してはならない",
            "mutation は親が明示した一時検証に限定",
            "mutation を commit してはならない",
            "変更禁止範囲や本番 code を mutation の対象にしてはならない",
            "regression Green 例外の Red 段階では passing test を commit",
            "変更がない Green / Refactor 段階に空 commit を作らない",
        )
        qa_contracts = (
            "AC、test、期待値の根拠、既存挙動の対応",
            "新機能または未実装仕様なら Red",
            "regression test が追加時点で Green",
        )
        intake_contracts = (
            "新機能または未実装仕様",
            "既存挙動を固定する regression test",
            "分類できない場合は Green 例外を適用せず判断点として返す",
        )

        reference_sets = (
            skills.source_references,
            skills.claude_references,
            skills.codex_references,
        )
        for references in reference_sets:
            for reference, contracts in (
                ("implementation-branches.md", implementation_contracts),
                ("qa-and-integration.md", qa_contracts),
                ("branch-plan-intake.md", intake_contracts),
            ):
                with self.subTest(reference=reference):
                    normalized = "".join(references[reference].split())
                    for contract in contracts:
                        self.assertIn("".join(contract.split()), normalized)

    def test_repository_implementers_return_regression_green_evidence(
        self,
    ) -> None:
        required_contracts = (
            "新機能または未実装仕様では Red を必須",
            "既存挙動を固定する regression test に限り追加時点の Green を許可",
            "既存挙動を固定する追補 test であること",
            "対応する AC",
            "期待値の根拠",
            "既存実装がすでに仕様を満たしていたこと",
            "形式的な Red のために本番 code を変更しない",
            "親が明示した一時 mutation 検証だけを行い、commit しない",
            "変更禁止範囲と本番 code を mutation の対象にしない",
        )

        for name in ("implementer", "senior-implementer", "expert-implementer"):
            paths = (
                Path("shared/agents") / f"{name}.md",
                Path("plugins/claude/agents") / f"{name}.md",
                Path("plugins/codex/install/agents") / f"{name}.toml",
            )
            for path in paths:
                with self.subTest(name=name, path=path):
                    normalized = "".join(self._repository_text(path).split())
                    for contract in required_contracts:
                        self.assertIn("".join(contract.split()), normalized)

    def test_repository_decision_corpus_covers_red_and_regression_green_cases(
        self,
    ) -> None:
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        required_contracts = (
            "## EVAL-11: 新機能では Red 証跡が必須",
            "新機能または未実装仕様",
            "Red 時点の失敗出力を必須",
            "## EVAL-12: regression test の追加時点 Green 例外",
            "既存挙動を固定する追補 test",
            "期待値の根拠",
            "既存実装がすでに仕様を満たしていた",
            "形式的 Red のために本番 code を変更しない",
            "mutation を commit しない",
            "親が AC、test、期待値の根拠、既存挙動の対応を確認",
        )
        normalized = "".join(corpus.split())
        for contract in required_contracts:
            self.assertIn("".join(contract.split()), normalized)

    def test_repository_decision_corpus_records_parent_managed_worktree_contract(
        self,
    ) -> None:
        """Record the issue #49 worktree contract verification and drop its superseded contract text."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        normalized = "".join(corpus.split())

        required_contracts = (
            "### worktree 契約の検証記録(issue #49)",
            "親管理 worktree 契約を採用し、`isolation: \"worktree\"` を廃止する",
            "HEAD 不一致を検出し、reset / merge / checkout などの自力修復を試みず",
            "`git worktree remove` と `git branch -D`",
            "既知の制約",
            "## EVAL-19: 開始条件不成立を検出した未着手返却",
            "契約通りの正常動作として扱う",
            "branch 不一致、dirty status のいずれであっても同じ扱いとする。",
            "worktree を基準 commit から作り直し",
            "Implementer へ reset / merge / checkout などの自力修復を指示しない。",
            "未着手返却を失敗として扱い、Implementer を責める、または mode を引き下げる。",
            "HEAD 不一致だけを特別扱いし、path 不一致・branch 不一致・dirty status を異なる扱いにする。",
            "Claude Code と Codex は「platform 共通の期待」に記載した起動、継続 mechanism だけが異なる。",
            "Red 必須と親 QA は共通であり、agent の起動 mechanism だけが異なる。",
            "引き上げ受諾後の段階継続 mechanism は platform に合わせてよい。",
        )
        for contract in required_contracts:
            self.assertIn("".join(contract.split()), normalized)

        stale_contracts = (
            "Claude Code と Codex は「platform 共通の期待」に記載した worktree 準備、"
            "起動、継続 mechanism だけが異なる。",
            "Red 必須と親 QA は共通であり、worktree と agent の起動 mechanism だけが異なる。",
            "引き上げ受諾後の worktree 準備・段階継続 mechanism は platform に合わせてよい。",
        )
        for contract in stale_contracts:
            self.assertNotIn("".join(contract.split()), normalized)

    def test_repository_decision_corpus_covers_findings_sourced_planning(
        self,
    ) -> None:
        """Evaluate findings-sourced planning as listed IDs, confirmed wording, and traceable origins."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        planning_cases = corpus.split("# Planning cases", 1)[1].split(
            "# Plan-intake cases", 1
        )[0]
        required_contracts = (
            "## EVAL-25: Test Inventory 報告の findings を元プランにする枝分割計画",
            "指定のない `G-3` は採用しない。",
            "対象 `G-*` ごとに `summary` / `evidence` / `suggestion` の原文と"
            "導出した AC 案を対で提示する。",
            "確定前は `unresolved_decisions` に `kind: ac-derivation`",
            "確定した AC の `derived_from` に由来する finding ID を記録",
            "導出案をユーザー確定なしに AC の `text` に入れる。",
            "`suggestion` にない対象・範囲・実装方針を導出で補う。",
        )
        normalized = "".join(planning_cases.split())
        for contract in required_contracts:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), normalized)

    def test_repository_readmes_list_all_distributed_agents(self) -> None:
        """Make every bundled agent discoverable from both platform READMEs."""
        claude_readme = (REPOSITORY_ROOT / "plugins" / "claude" / "README.md").read_text(
            encoding="utf-8"
        )
        codex_readme = (REPOSITORY_ROOT / "plugins" / "codex" / "README.md").read_text(
            encoding="utf-8"
        )

        for name in AGENT_NAMES:
            with self.subTest(name=name):
                self.assertIn(f"agents/{name}.md", claude_readme)
                self.assertIn(f"`{name}`", codex_readme)

    def test_repository_does_not_reference_retired_flat_mode_contract_text(
        self,
    ) -> None:
        """Detect leftover flat lite/standard/strict contract text from before adaptive mode."""
        scan_roots = (
            REPOSITORY_ROOT / "shared",
            REPOSITORY_ROOT / "plugins",
            REPOSITORY_ROOT / "scripts",
            REPOSITORY_ROOT / "tests",
            REPOSITORY_ROOT / "evals",
            REPOSITORY_ROOT / "README.md",
        )
        # Each phrase below was the pre-adaptive-mode contract text superseded by the
        # {policy, baseline} vocabulary across the three branches this branch depends
        # on. A survivor means one of those branches missed a reference, not that this
        # branch should silently rewrite it. Phrases are built by concatenation (like
        # the retired agent name above) so this literal does not self-match the scan.
        retired_phrases = (
            "requested_mode: null | lite | standard" + " | strict",
            "propose: " + "strict",
            "- 委譲 mode: <lite / standard" + " / strict>",
            "| route / mode | " + "選択条件 |",
            "Executor が standard" + " を選ぶ",
            "委譲だけが明示され mode が指定されていない場合は `standard`" + " を選ぶ。",
            # Bare flat-enum field assignments (e.g. from evals corpus examples
            # written before the {policy, baseline} structure existed). Confirmed
            # absent repository-wide before adding; the new structured form always
            # writes "requested_mode: {" so it cannot collide with these literals.
            "requested_mode: " + "lite",
            "requested_mode: " + "standard",
            "requested_mode: " + "strict",
        )

        for root in scan_roots:
            file_paths = [root] if root.is_file() else list(root.rglob("*"))
            for file_path in file_paths:
                if not file_path.is_file():
                    continue
                content = file_path.read_text(encoding="utf-8")
                for phrase in retired_phrases:
                    with self.subTest(path=file_path, phrase=phrase):
                        self.assertNotIn(phrase, content)

    def test_repository_delegate_skill_description_names_the_input_vocabulary(
        self,
    ) -> None:
        """Fire on the five input tokens and keep the direct exclusion in the description."""
        vocabulary_tokens = (
            "`lite`",
            "`standard(-adaptive)`",
            "`strict(-adaptive)`",
            "`strict-full`",
            "`direct`",
        )
        exclusion_contract = (
            "`direct` の明示時や、委譲指示なしにタスク規模だけを理由として使わない。"
        )

        for platform in ("claude", "codex"):
            with self.subTest(platform=platform):
                content = self._repository_text(GENERATED_SKILL_PATHS[platform])
                frontmatter = content.split("---", 2)[1]
                self.assertIn("description:", frontmatter)
                normalized_frontmatter = "".join(frontmatter.split())
                for token in vocabulary_tokens:
                    self.assertIn(token, frontmatter)
                self.assertIn(
                    "".join(exclusion_contract.split()), normalized_frontmatter
                )


class PlanImplementationBranchesContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _plan_skill_texts(self) -> dict[str, str]:
        return {
            "source": self._repository_text(shared_skill_path(PLAN_SKILL)),
            "claude": self._repository_text(
                generated_skill_path("claude", PLAN_SKILL)
            ),
            "codex": self._repository_text(
                generated_skill_path("codex", PLAN_SKILL)
            ),
        }

    def _plan_reference_texts(self, name: str) -> dict[str, str]:
        return {
            "source": self._repository_text(
                shared_skill_reference_path(PLAN_SKILL, name)
            ),
            "claude": self._repository_text(
                generated_skill_reference_path("claude", PLAN_SKILL, name)
            ),
            "codex": self._repository_text(
                generated_skill_reference_path("codex", PLAN_SKILL, name)
            ),
        }

    def test_plan_skill_exposes_platform_frontmatter_and_reference_links(
        self,
    ) -> None:
        """Expose planning frontmatter and route each detail to its reference."""
        for platform in ("claude", "codex"):
            main = self._plan_skill_texts()[platform]
            with self.subTest(platform=platform):
                self.assertTrue(main.startswith(f"---\nname: {PLAN_SKILL}\n"))
                self.assertLess(len(main.splitlines()), 300)
                for name in PLAN_REFERENCE_NAMES:
                    self.assertIn(f"(references/{name})", main)
                self.assertNotIn("<!-- claude-only", main)
                self.assertNotIn("<!-- codex-only", main)

    def test_plan_references_carry_generated_warning_and_table_of_contents(
        self,
    ) -> None:
        """Give each planning reference a warning-free source and a table of contents."""
        for name in PLAN_REFERENCE_NAMES:
            texts = self._plan_reference_texts(name)
            with self.subTest(reference=name):
                self.assertFalse(
                    texts["source"].startswith(GENERATED_MARKDOWN_WARNING)
                )
                self.assertTrue(texts["source"].startswith("# "))
                self.assertIn("## 目次", texts["source"])
                for platform in ("claude", "codex"):
                    reference = texts[platform]
                    self.assertTrue(
                        reference.startswith(f"{GENERATED_MARKDOWN_WARNING}\n\n")
                    )
                    self.assertIn("## 目次", reference)

    def test_plan_schema_reference_holds_the_canonical_schema(self) -> None:
        """Carry the confirmed schema, violation codes, transitions, and tests meaning."""
        required = (
            "status: blocked | awaiting_review | approved",
            "confirmation_mode: review | auto",
            "delegation:",
            "authorized: false",
            "| code | 検査内容 |",
            "duplicate-id",
            "unknown-reference",
            "branch-without-primary-ac",
            "delegation-invalid",
            "mode-proposal-invalid",
            "## 状態遷移と権限",
            "## tests / stage_tests の意味",
        )
        excluded = (
            "## implementation_stages の実行規約",
            "## Executor 側の再検証",
            "## レビュー指摘への対応",
            "## 再レビュー指摘への対応",
            "## issue #46 確定事項からの意図的な変更",
        )
        for platform, text in self._plan_reference_texts(
            "branch-plan-schema.md"
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)
                for section in excluded:
                    self.assertNotIn("".join(section.split()), normalized)

    def test_plan_schema_reference_points_terminology_to_the_implementation_branches_glossary(
        self,
    ) -> None:
        """Route branch terminology to the delegate-implementation glossary, not a local copy."""
        required = (
            "用語",
            "delegate-implementation",
            "../../delegate-implementation/references/implementation-branches.md",
        )
        for platform, text in self._plan_reference_texts(
            "branch-plan-schema.md"
        ).items():
            with self.subTest(platform=platform):
                for contract in required:
                    self.assertIn(contract, text)

    def test_plan_skill_matches_confirmed_schema_contract(self) -> None:
        """Separate approval from delegation and never start delegation from the skill."""
        required = (
            "承認と委譲開始権限は独立",
            "`delegation.authorized` は常に `false`",
            "確認モードの既定は `review`",
            "`auto` はユーザーが明示した場合のみ",
            "`delegate-implementation` を直接起動しない",
            "blocking な不足は `unresolved_decisions`",
            "minor な不足は `assumptions`",
        )
        for platform, main in self._plan_skill_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(main.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_references_define_branch_responsibility_exclusions(self) -> None:
        """Generate responsibility exclusions separately from physical path limits."""
        reference_contracts = {
            "branch-plan-schema.md": (
                "`allowed_paths` は変更を許可する物理的なファイル範囲",
                "`forbidden_paths` は変更を禁止する物理的なファイル範囲",
                "`out_of_scope` は許可範囲内でもこの枝では担当しない責務・作業",
            ),
            "branch-splitting.md": (
                "同じ `allowed_paths` 内に複数の責務・作業が含まれ",
                "担当しない責務・作業を `out_of_scope` に列挙する",
                "パスで表現できる禁止範囲を `out_of_scope` で代用しない",
            ),
        }

        for reference, contracts in reference_contracts.items():
            for platform, text in self._plan_reference_texts(reference).items():
                with self.subTest(reference=reference, platform=platform):
                    normalized = "".join(text.split())
                    for contract in contracts:
                        self.assertIn("".join(contract.split()), normalized)

    def test_plan_schema_holds_requested_mode_as_policy_and_baseline(self) -> None:
        """Carry the requested delegation mode as an allocation policy and a baseline."""
        required = (
            "[issue #68](https://github.com/akitanabe/agentic-qa-workflow/issues/68)",
            "policy: fixed | adaptive",
            "baseline: lite | standard | strict",
            "mode 未指定の明示的な委譲要求は null のまま保持し、"
            "Executor が {adaptive, standard} を採用する。",
            "`{adaptive, lite}` と `{fixed, standard}` は入力語彙が存在しないため無効とし、"
            "表に含めない。",
            "`baseline` を `lite` にすると low risk 枝の割り当て先が `lite` しかなく導出が"
            "恒等写像になり、`medium` 以上を引き上げる用途は `{adaptive, standard}` と"
            "同一になるため、独立した配分方針として意味を持たない。",
            "`{fixed, standard}` は全枝固定を明示する入力語彙が存在しないため到達できない。"
            "仮に語彙を足しても `{adaptive, standard}` は low risk 枝だけを `lite` に落とし"
            "他は `standard` のままなので、品質面で下回らずコストだけが下がり、優位性がない。",
        )
        valid_combinations = (
            "| `false` | `null` | `null` |",
            "| `true` | `user` | `null`(mode 未指定の委譲要求。"
            "Executor が `{adaptive, standard}` を選ぶ) |",
            "| `true` | `user` | `{fixed, lite}` |",
            "| `true` | `user` | `{adaptive, standard}` |",
            "| `true` | `user` | `{adaptive, strict}` |",
            "| `true` | `user` | `{fixed, strict}` |",
        )
        for platform, text in self._plan_reference_texts(
            PLAN_SCHEMA_REFERENCE
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required + valid_combinations:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_schema_derives_branch_mode_from_risk_instead_of_a_field(
        self,
    ) -> None:
        """Keep branch risk as the only source for the derived branch mode."""
        required = (
            "枝ごとの委譲 mode は schema に持たせず、`branches[].risk` を正として導出する。",
            "枝側に `recommended_mode` を置くと `risk` と二重管理になり、矛盾したときに"
            "どちらを正とするか決められないため。",
            "AC 割り当てを枝側の一方向参照へ正規化したのと同じ理由である。",
            "導出した枝 mode は Branch Plan へ書き戻さず、実行 Data として保持して"
            "最終報告で報告する。",
            "mode の判定理由は `risk.reasons` に書き、mode ごとの理由欄を別に設けない。",
        )
        for platform, text in self._plan_reference_texts(
            PLAN_SCHEMA_REFERENCE
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_schema_limits_mode_proposal_to_fixed_policy_mismatch(self) -> None:
        """Propose an adaptive policy only where a fixed policy ignores branch risk."""
        required = (
            "propose:",
            "policy: adaptive",
            "baseline: standard | strict",
            "`policy: adaptive` では枝の `risk.level` から mode を導出するため、"
            "high risk 枝は決定表側で `strict` になる。",
            "提案が必要なのは `policy: fixed` が枝の `risk` と整合しない場合だけである。",
            "`{fixed, strict}` に対して降格を提案しない。",
            "引き上げだけを提案する非対称性は、コストの削減より品質の担保を優先する"
            "判断であり、low risk 枝から `lite` を提案しないのと同じ理由である。",
        )
        proposal_rows = (
            "| `{fixed, lite}` | `high` を含む | `{adaptive, strict}` を提案 |",
            "| `{fixed, lite}` | `medium` を含み `high` なし | "
            "`{adaptive, standard}` を提案 |",
            "| `{fixed, lite}` | 全枝 `low` | 出力しない |",
            "| `{fixed, strict}` | 任意 | 出力しない |",
            "| `{adaptive, *}` または `null` | 任意 | 出力しない |",
        )
        violation_recalculation = (
            "`delegation_mode_proposal` の要否・内容が `requested_mode` と枝の "
            "`risk.level` からの再計算(出力条件表)と一致しない",
            "必要時の欠落、不要時の出力、表と異なる `{policy, baseline}` の提案",
        )
        for platform, text in self._plan_reference_texts(
            PLAN_SCHEMA_REFERENCE
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required + proposal_rows + violation_recalculation:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_splitting_reference_defines_risk_level_criteria(self) -> None:
        """Assign risk levels from failure impact rather than from change size."""
        required = (
            "## risk.level の判定観点",
            "これは枝 mode を決める関数ではなく、`risk.level` の付け方を揃える"
            "チェックリストである。",
            "判定は実装量やファイル数ではなく、失敗したときの影響を中心に行う。",
            "1. 失敗時の影響範囲",
            "2. 変更の可逆性 / 切り戻しの容易さ",
            "3. 外部副作用の有無と数",
            "4. セキュリティ・権限への影響",
            "5. データ整合性への影響",
            "6. 後方互換性への影響",
            "7. 仕様の明確さ",
            "8. テストによる担保の可能性",
            "9. 他の枝との依存関係",
            "変更量が1行でも、権限判定やデータ削除条件に関わる場合は `high` とする。",
            "判定に使った観点は `risk.reasons` に記録する。",
            "決定表をここに再掲しない。",
        )
        level_rows = (
            "| `low` | 表示文言のみの変更、設定値の追加、振る舞いに影響しないリネーム、"
            "局所的な機械的修正。外部副作用がなく、容易に切り戻せる。 |",
            "| `medium` | 通常の機能追加、既存ロジックの変更、API 内部処理の変更、"
            "UI とバックエンドの通常連携。テストで十分に担保でき、失敗時の影響が限定的。 |",
            "| `high` | 認証・認可・権限判定、データ削除・上書き・移行、"
            "外部 API の契約変更、後方互換性への影響、決済・請求・金額計算、"
            "機密情報への影響、複数の外部 I/O。失敗時の影響が広い、切り戻しが困難、"
            "または仕様の曖昧さが重大な不具合につながる。 |",
        )
        for platform, text in self._plan_reference_texts("branch-splitting.md").items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required + level_rows:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_skill_takes_inventory_findings_only_for_user_listed_ids(
        self,
    ) -> None:
        """Accept inventory findings as a source plan only for explicitly listed finding IDs."""
        required = (
            "元プラン(path / issue URL / 会話内 / `inventory-test-suite` の "
            "Test Inventory 報告の findings)",
            "findings 由来の AC では、原文はユーザーが確定した文言を指す。",
            "対象 findings の ID(`G-*`)をユーザーが明示的に指定する。"
            "全 findings の自動採用はしない。",
            "対象 ID の指定がないまま findings 全体を渡された場合は、"
            "自動採用せず対象 ID の明示指定を求める。",
            "導出は `suggestion` を受け入れ条件の形に整えることに限る。",
            "findings にない対象・範囲・実装方針を足さない。",
        )
        for platform, main in self._plan_skill_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(main.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_schema_traces_findings_through_derived_from_on_criteria(
        self,
    ) -> None:
        """Trace an inventory finding to its branch through one-way references only."""
        required = (
            "path / issue URL / 「会話内」/ 「Test Inventory 報告」",
            "derived_from: []",
            "findings 由来のときだけ元の finding ID(`G-*`)を列挙する",
            "空なら元プラン由来",
            "実装枝 → `covers_acceptance_criteria` → AC → `derived_from` の一方向参照",
            "実装枝側に finding ID を持たせない",
            "`derived_from` は blocking violation code の検査対象にしない",
            "Branch Plan 内では参照先の存在を解決できない",
            "承認可否の判定が実際には検査していない事実を根拠に持つ",
        )
        for platform, text in self._plan_reference_texts(
            PLAN_SCHEMA_REFERENCE
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_schema_blocks_on_unconfirmed_findings_derived_criteria(
        self,
    ) -> None:
        """Hold an unconfirmed derived wording as its own unresolved decision kind."""
        required = (
            "kind: ac-derivation",
            "findings から導出した AC の文言が未確定であることを表す",
            "`unresolved_decisions.affects` の `branch` / `ac-assignment` / "
            "`ac-derivation`",
        )
        for platform, text in self._plan_reference_texts(
            PLAN_SCHEMA_REFERENCE
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_review_confirms_findings_derived_criteria_before_approval(
        self,
    ) -> None:
        """Pair each finding with its draft criterion and confirm the wording before approval."""
        required = (
            "## findings 由来 AC の確定",
            "対象 `G-*` ごとに、`summary` / `evidence` / `suggestion` の原文と、"
            "そこから導出した AC 案を対で提示する。",
            "AC の `text` にはユーザーが確定した文言だけを入れる。",
            "`kind: ac-derivation` の `affects` を置き、`status: blocked` のまま"
            "承認操作を求めない。",
            "文言が確定したら AC の `text` を確定文言に置き換え、対応する "
            "`unresolved_decisions` を取り除く。",
            "`suggestion` にない対象・範囲・実装方針を足す必要が生じた場合は、"
            "導出せず `unresolved_decisions` の `question` としてユーザーへ確定を求める。",
        )
        for platform, text in self._plan_reference_texts("plan-review.md").items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_review_applies_checkability_guidance_to_ac_wording_only(
        self,
    ) -> None:
        """Scope drafting's checkability guidance to wording, routing scope growth elsewhere."""
        for platform, text in self._plan_reference_texts("plan-review.md").items():
            with self.subTest(platform=platform):
                self.assertIn(
                    "[起草手順](../../draft-implementation-plan/references/plan-drafting.md)",
                    text,
                )
                normalized = "".join(text.split())
                required = (
                    "の「AC の書き方」が定める判定可能性の指針を適用する。",
                    "適用範囲は AC 案の文言整形までに限り、`suggestion` にない対象・範囲を"
                    "新たに足す判断には使わない。",
                    "対象・範囲を足す必要が生じた場合は、下記のとおり `unresolved_decisions` へ"
                    "回す。",
                )
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)


INTAKE_REFERENCE = "branch-plan-intake.md"
PLAN_SCHEMA_REFERENCE = "branch-plan-schema.md"


class DelegateImplementationIntakeContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _assert_intake_reference_files_exist(self) -> None:
        paths = (
            shared_skill_reference_path(DELEGATE_SKILL, INTAKE_REFERENCE),
            generated_skill_reference_path("claude", DELEGATE_SKILL, INTAKE_REFERENCE),
            generated_skill_reference_path("codex", DELEGATE_SKILL, INTAKE_REFERENCE),
        )
        for path in paths:
            self.assertTrue(
                (REPOSITORY_ROOT / path).is_file(),
                f"missing intake reference: {path}",
            )

    def _intake_reference_texts(self) -> dict[str, str]:
        self._assert_intake_reference_files_exist()
        return {
            "source": self._repository_text(
                shared_skill_reference_path(DELEGATE_SKILL, INTAKE_REFERENCE)
            ),
            "claude": self._repository_text(
                generated_skill_reference_path(
                    "claude", DELEGATE_SKILL, INTAKE_REFERENCE
                )
            ),
            "codex": self._repository_text(
                generated_skill_reference_path(
                    "codex", DELEGATE_SKILL, INTAKE_REFERENCE
                )
            ),
        }

    def _delegate_skill_texts(self) -> dict[str, str]:
        return {
            "source": self._repository_text(shared_skill_path(DELEGATE_SKILL)),
            "claude": self._repository_text(
                generated_skill_path("claude", DELEGATE_SKILL)
            ),
            "codex": self._repository_text(
                generated_skill_path("codex", DELEGATE_SKILL)
            ),
        }

    def _delegate_reference_texts(self, name: str) -> dict[str, str]:
        return {
            "source": self._repository_text(
                shared_skill_reference_path(DELEGATE_SKILL, name)
            ),
            "claude": self._repository_text(
                generated_skill_reference_path("claude", DELEGATE_SKILL, name)
            ),
            "codex": self._repository_text(
                generated_skill_reference_path("codex", DELEGATE_SKILL, name)
            ),
        }

    def test_intake_reference_is_generated_with_warning_and_toc(self) -> None:
        """Distribute the intake reference to both platforms with a warning-free source."""
        texts = self._intake_reference_texts()
        self.assertTrue(texts["source"].startswith("# "))
        self.assertFalse(texts["source"].startswith(GENERATED_MARKDOWN_WARNING))
        self.assertIn("## 目次", texts["source"])
        for platform in ("claude", "codex"):
            reference = texts[platform]
            with self.subTest(platform=platform):
                self.assertTrue(
                    reference.startswith(f"{GENERATED_MARKDOWN_WARNING}\n\n")
                )
                self.assertIn("## 目次", reference)

    def test_delegate_skill_links_to_the_intake_reference(self) -> None:
        """Route a confirmed Branch Plan through the intake reference from SKILL.md."""
        for platform, main in self._delegate_skill_texts().items():
            with self.subTest(platform=platform):
                self.assertIn(f"(references/{INTAKE_REFERENCE})", main)
                self.assertLess(len(main.splitlines()), 300)
                normalized = "".join(main.split())
                self.assertIn(
                    "".join("確定済み Branch Plan が渡されている場合は".split()),
                    normalized,
                )

    def test_intake_reference_moves_execution_and_revalidation_sections(self) -> None:
        """Carry the execution and revalidation sections as the canonical source."""
        moved_sections = (
            "## implementation_stages の実行規約",
            "## Executor 側の再検証",
        )
        moved_body = (
            "`strict` の段階ゲート機構で実行する",
            "各 stage を `strict` の1サイクル(テスト計画 → Red → Green → Refactor)"
            "として実行する。",
            "`status: approved` であり、`approval.method` が設定済みである。",
            "blocking violation code 表のすべての検査規則を入力 Data から再計算し、"
            "違反が0件である。",
        )
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                for section in moved_sections:
                    self.assertIn(section, text)
                normalized = "".join(text.split())
                for body in moved_body:
                    self.assertIn("".join(body.split()), normalized)

    def test_intake_reference_declares_the_acceptance_gate_rules(self) -> None:
        """Re-validate before delegation and fall back to inline splitting otherwise."""
        gate_rules = (
            "親は Branch Plan の自己申告を信用せず、再検証してから枝と配分方針の入力にする。",
            "「Executor 側の再検証」の5項目を委譲開始前に",
            "再検証を満たさない場合は実装を開始せず",
            "既存の委譲 prompt の Data へそのまま流し込む",
            "委譲 prompt の必須テストと検証 command で",
            "Branch Plan が渡されていない場合は、現行どおり親が inline に枝を分ける。",
            "`plan-implementation-branches` の使用を",
        )
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for rule in gate_rules:
                    self.assertIn("".join(rule.split()), normalized)

    def test_intake_reference_holds_the_branch_mode_derivation_table(self) -> None:
        """Map each allocation policy and risk level pair onto one branch mode."""
        derivation_rows = (
            "| policy | baseline | `risk.level: low` | `medium` | `high` |",
            "| `fixed` | `lite` | `lite` | `lite` | `lite` |",
            "| `fixed` | `strict` | `strict` | `strict` | `strict` |",
            "| `adaptive` | `standard` | `lite` | `standard` | `strict` |",
            "| `adaptive` | `strict` | `standard` | `strict` | `strict` |",
        )
        required_rules = (
            "## 枝 mode の決定表",
            "本 reference は実行規約、Executor 側の再検証、枝 mode の決定表の正本を担う。",
            "この表を正本とし、planning Skill と Executor は同じ表を使う。",
            "`policy: fixed` では導出を行わず、全枝へ `baseline` をそのまま適用する。",
            "`{adaptive, strict}` の `low` は `lite` ではなく `standard` とする。",
            "「判断に迷う場合は基準側へ倒す」方針を `strict` baseline では `low` にも"
            "適用するのが一貫するためである。",
            "`{adaptive, strict}` は `risk.level` の3値に対して2値しか使わず、"
            "`{adaptive, standard}` との差は `medium` だけでなく `low` にも現れる。",
            "`{adaptive, strict}` で `lite` が必要な枝は、理由を記録した手動上書きで降格する。",
        )
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for row in derivation_rows:
                    self.assertIn(row, text)
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized)

    def test_intake_reference_derives_branch_modes_before_delegating(self) -> None:
        """Recompute branch modes from input Data instead of trusting the plan."""
        required_rules = (
            "全枝の `risk.level` が `low` / `medium` / `high` のいずれかである。",
            "欠落または3値以外の枝がある場合は決定的に導出できないため、"
            "委譲を開始せず Branch Plan の修正を要求する。",
            "5項目を満たした後、委譲開始前に枝ごとの mode を導出する。",
            "`delegation.requested_mode` を入力語彙の写像ではなく Data として受け取り、"
            "`null` の場合は `{adaptive, standard}` を採用する。",
            "「枝 mode の決定表」から枝ごとの mode を再計算する。",
            "planning Skill 側の申告や `delegation_mode_proposal` の内容を根拠にしない。",
            "導出結果は実行 Data として保持し、Branch Plan へ書き戻さない。",
        )
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized)

    def test_intake_reference_keeps_staged_branches_at_strict(self) -> None:
        """Run staged branches at strict and treat the gap as a per-branch upgrade."""
        required_rules = (
            "stages を宣言した枝は、決定表の導出結果に関わらず `strict` の段階ゲート機構で"
            "実行する。",
            "導出結果が `strict` 未満の場合、これは枝単位の mode 引き上げに当たる。",
            "SKILL.md の引き上げ契約に従い、具体的なリスクを報告して `strict` へ引き上げる。",
            "引き上げが受け入れられない場合は stages を実行せず、"
            "枝の再分割または stages の削除を要求する。",
            "stages を宣言する枝は実質的に `risk.level` が `low` ではない。",
            "`{adaptive, standard}` かつ `risk.level: low` かつ stages 宣言という組み合わせが"
            "出た場合は、stages 側ではなく `risk.level` の付け方を疑い、"
            "planning へ差し戻すかどうかを判断する。",
        )
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized)

    def test_intake_reference_excludes_shared_foundation_from_derivation(self) -> None:
        """Keep the parent-built shared foundation out of the branch allocation."""
        required_rules = (
            "`shared_foundation` は親が委譲前に実装する明示的な例外であり委譲枝ではないため、"
            "枝 mode の導出対象外とする。",
            "親は現行どおり `verification` を実行して基準 commit にする。",
            "実行前サマリーの枝一覧にも配分対象として並べない。",
        )
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized)

    def test_intake_reference_bounds_manual_branch_mode_overrides(self) -> None:
        """Allow overrides as execution Data while requiring reasons for downgrades."""
        required_rules = (
            "### 手動上書き",
            "上書きは実行 Data であり、Branch Plan のフィールドではない。",
            "引き上げ(`lite → standard`、`standard → strict`)は理由の記録を必須としない。",
            "降格は理由の記録を必須とする。理由なしの降格は受け付けない。",
            "`risk.level: high` の枝を `lite` へ直接降格させない。",
            "判断材料が不足している場合は `baseline` 側へ倒す。",
            "上書きは最終報告に含める。",
            "`risk.level` そのものが誤っていると判断した場合は、上書きではなく Branch Plan の "
            "`risk` を修正して再検証する。上書きを risk 修正の代用にしない。",
            "上書きを受け付ける入力経路は本 reference で規定しない。",
        )
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized)

    def test_delegate_prompt_declares_the_derived_branch_mode(self) -> None:
        """Hand the Implementer its branch mode without the allocation policy."""
        required_rules = (
            "- 委譲 mode: <この枝に導出された枝 mode。lite / standard / strict>",
            "## 委譲 mode に応じた TDD/QA",
            "表の `委譲 mode` は枝ごとに導出された枝 mode であり、"
            "配分方針 `{policy, baseline}` ではない。",
            "導出は [Branch Plan の受け入れ](branch-plan-intake.md) の"
            "「枝 mode の決定表」に従う。",
            "委譲 prompt の「委譲 mode」欄には、その枝に導出された枝 mode を書き、"
            "配分方針 `{policy, baseline}` を渡さない。",
            "Implementer は枝 mode とその枝で要求される TDD 要件だけで作業でき、"
            "配分方針を知る必要がないためである。",
        )
        for platform, text in self._delegate_reference_texts(
            "implementation-branches.md"
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized)

    def test_delegate_references_preserve_branch_responsibility_exclusions(self) -> None:
        """Carry exclusions unchanged into delegation and verify them before acceptance."""
        reference_contracts = {
            "branch-plan-intake.md": (
                "責務制約は `out_of_scope` の各項目を意味を変えず",
                "委譲 prompt の「この枝でやらないこと」へ渡す",
            ),
            "implementation-branches.md": (
                "- 変更を許可する物理的範囲: <allowed_paths>",
                "- 変更を禁止する物理的範囲: <forbidden_paths>",
                "- この枝でやらないこと: <out_of_scope。空なら「なし」>",
                "必要になった場合は変更せず、必要性と理由を親へ報告する",
            ),
            "qa-and-integration.md": (
                "基準 commit からの diff",
                "枝の `out_of_scope` に列挙された責務・作業を含まないこと",
            ),
        }

        for reference, contracts in reference_contracts.items():
            for platform, text in self._delegate_reference_texts(reference).items():
                with self.subTest(reference=reference, platform=platform):
                    normalized = "".join(text.split())
                    for contract in contracts:
                        self.assertIn("".join(contract.split()), normalized)

    def test_intake_reference_resolves_the_cross_skill_schema_link(self) -> None:
        """Resolve the schema code table link across shared and generated trees."""
        relative_link = (
            "../../plan-implementation-branches/references/branch-plan-schema.md"
        )
        intake_paths = {
            "source": shared_skill_reference_path(DELEGATE_SKILL, INTAKE_REFERENCE),
            "claude": generated_skill_reference_path(
                "claude", DELEGATE_SKILL, INTAKE_REFERENCE
            ),
            "codex": generated_skill_reference_path(
                "codex", DELEGATE_SKILL, INTAKE_REFERENCE
            ),
        }
        texts = self._intake_reference_texts()
        for structure, intake_path in intake_paths.items():
            with self.subTest(structure=structure):
                self.assertIn(relative_link, texts[structure])
                resolved = (REPOSITORY_ROOT / intake_path).parent / relative_link
                self.assertTrue(
                    resolved.resolve().is_file(),
                    f"unresolved cross-skill link from {intake_path}",
                )


INVENTORY_SKILL = "inventory-test-suite"
INVENTORY_REPORT_REFERENCE = "inventory-report.md"


class InventoryTestSuiteReportContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _inventory_report_texts(self) -> dict[str, str]:
        return {
            "source": self._repository_text(
                shared_skill_reference_path(
                    INVENTORY_SKILL, INVENTORY_REPORT_REFERENCE
                )
            ),
            "claude": self._repository_text(
                generated_skill_reference_path(
                    "claude", INVENTORY_SKILL, INVENTORY_REPORT_REFERENCE
                )
            ),
            "codex": self._repository_text(
                generated_skill_reference_path(
                    "codex", INVENTORY_SKILL, INVENTORY_REPORT_REFERENCE
                )
            ),
        }

    def test_inventory_report_offers_end_or_plan_operations_like_plan_review(
        self,
    ) -> None:
        """Offer plan-review's bulleted-operations-then-permission-boundary shape."""
        required = (
            "## 確認操作",
            "報告のみで終了",
            "既定。この操作を選んだ場合、この Skill は何も起こさない。",
            "指摘の解消を計画",
            "対象の gap 指摘 `G-*` をユーザーが指定し、`plan-implementation-branches` へ",
            "渡して実装枝計画へ進める。",
            "`plan-implementation-branches` へ渡すのは親エージェントの責務であり、この Skill は",
            "`plan-implementation-branches` を直接起動しない。",
        )
        for platform, text in self._inventory_report_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_inventory_report_withholds_plan_operation_without_scanned_gaps(
        self,
    ) -> None:
        """Withhold the plan-resolution operation once no gap finding exists to target."""
        required = (
            "gap 指摘が `該当なし` の場合は提示しない",
            "指定できる解消対象がないためである。",
        )
        for platform, text in self._inventory_report_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_inventory_report_presentation_order_governs_confirmation_visibility(
        self,
    ) -> None:
        """Let `## 提示の順序` alone decide confirmation visibility and position per status."""
        required = (
            "→ 確認操作の",
            "最後に確認操作を",
            "確認操作も提示しない",
        )
        for platform, text in self._inventory_report_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_inventory_report_table_of_contents_lists_confirmation_operations(
        self,
    ) -> None:
        """Register the confirmation-operations section in the table of contents."""
        toc_heading = "## 目次"
        for platform, text in self._inventory_report_texts().items():
            with self.subTest(platform=platform):
                self.assertIn(toc_heading, text)
                toc_section = text.split(toc_heading, 1)[1].split("##", 1)[0]
                self.assertIn("確認操作", toc_section)


class DraftImplementationPlanContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _draft_skill_texts(self) -> dict[str, str]:
        return {
            "source": self._repository_text(shared_skill_path(DRAFT_SKILL)),
            "claude": self._repository_text(
                generated_skill_path("claude", DRAFT_SKILL)
            ),
            "codex": self._repository_text(
                generated_skill_path("codex", DRAFT_SKILL)
            ),
        }

    def _draft_reference_texts(self, name: str) -> dict[str, str]:
        return {
            "source": self._repository_text(
                shared_skill_reference_path(DRAFT_SKILL, name)
            ),
            "claude": self._repository_text(
                generated_skill_reference_path("claude", DRAFT_SKILL, name)
            ),
            "codex": self._repository_text(
                generated_skill_reference_path("codex", DRAFT_SKILL, name)
            ),
        }

    def test_draft_skill_exposes_platform_frontmatter_and_reference_links(
        self,
    ) -> None:
        """Expose drafting frontmatter and route each detail to its reference."""
        for platform in ("claude", "codex"):
            main = self._draft_skill_texts()[platform]
            with self.subTest(platform=platform):
                self.assertTrue(main.startswith(f"---\nname: {DRAFT_SKILL}\n"))
                self.assertLess(len(main.splitlines()), 300)
                for name in DRAFT_REFERENCE_NAMES:
                    self.assertIn(f"(references/{name})", main)
                self.assertNotIn("<!-- claude-only", main)
                self.assertNotIn("<!-- codex-only", main)

    def test_draft_references_carry_generated_warning_and_table_of_contents(
        self,
    ) -> None:
        """Give each drafting reference a warning-free source and a table of contents."""
        for name in DRAFT_REFERENCE_NAMES:
            texts = self._draft_reference_texts(name)
            with self.subTest(reference=name):
                self.assertFalse(
                    texts["source"].startswith(GENERATED_MARKDOWN_WARNING)
                )
                self.assertTrue(texts["source"].startswith("# "))
                self.assertIn("## 目次", texts["source"])
                for platform in ("claude", "codex"):
                    reference = texts[platform]
                    self.assertTrue(
                        reference.startswith(f"{GENERATED_MARKDOWN_WARNING}\n\n")
                    )
                    self.assertIn("## 目次", reference)

    def test_draft_schema_reference_holds_the_canonical_schema(self) -> None:
        """Carry the confirmed schema, violation codes, transitions, and handoff map."""
        required = (
            "status: blocked | awaiting_review | approved",
            "confirmation_mode: review | auto",
            "rounds_limit: 10",
            "termination: null | zero-findings | trivial-only | round-limit",
            "全 round・全 reviewer 通算の指摘台帳",
            "| code | 検査内容 |",
            "duplicate-id",
            "unknown-reference",
            "vocabulary-invalid",
            "state-invalid",
            "scope-conflict",
            "review-incomplete",
            "resolution-missing",
            "rounds-invalid",
            "handoff-incomplete",
            "## 状態遷移と権限",
            "## plan-implementation-branches への引き渡し",
        )
        for platform, text in self._draft_reference_texts(
            "implementation-plan-schema.md"
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_draft_schema_reference_points_terminology_to_the_implementation_branches_glossary(
        self,
    ) -> None:
        """Route branch terminology to the delegate-implementation glossary, not a local copy."""
        required = (
            "用語",
            "delegate-implementation",
            "../../delegate-implementation/references/implementation-branches.md",
        )
        for platform, text in self._draft_reference_texts(
            "implementation-plan-schema.md"
        ).items():
            with self.subTest(platform=platform):
                for contract in required:
                    self.assertIn(contract, text)

    def test_draft_skill_matches_confirmed_contract(self) -> None:
        """Separate plan approval from downstream work and keep drafting review-gated."""
        required = (
            "確認モードの既定は `review`",
            "`auto` はユーザーが明示した場合のみ",
            "`plan-implementation-branches` を直接起動しない",
            "blocking な不足は `open_questions`",
            "minor な不足は `assumptions`",
            "`rounds_limit` の既定は 10",
            "reviewer の自己申告をそのまま採用しない",
        )
        for platform, main in self._draft_skill_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(main.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_draft_review_reference_defines_termination_conditions(self) -> None:
        """Terminate the loop only via the three confirmed conditions."""
        required = (
            "1 round = `plan-adversarial-reviewer` 起動1回",
            "`zero-findings`",
            "`trivial-only`",
            "`round-limit`",
            "reviewer の verdict 申告をそのまま採用しない",
            "`修正推奨` 以上へ引き上げた指摘が1件でもあればループを継続",
            "`auto` でも自動承認しない",
            "この round も `rounds_limit` に数える",
        )
        for platform, text in self._draft_reference_texts(
            "adversarial-review.md"
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_draft_review_reference_records_resolution_per_finding(self) -> None:
        """Record adopted or rejected per finding id before any termination."""
        required = (
            "指摘IDごと",
            "adopted",
            "rejected",
            "`unresolved` を残さない",
            "`resolution: unresolved`",
            "YAML より前に未解決一覧",
        )
        for platform, text in self._draft_reference_texts(
            "adversarial-review.md"
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_draft_review_reference_withholds_plan_edits_from_missing_evidence(
        self,
    ) -> None:
        """Reject findings lacking evidence unless the parent supplies it from primary sources."""
        required = (
            "[Reviewer findings の共通契約]"
            "(../../delegate-implementation/references/reviewer-findings.md)",
            "evidence を欠く指摘だけを根拠にプランを修正しない。",
            "親自身が確認した",
            "repository の現状・プラン本文・既存 manuscript から特定できる場合は",
            "親が evidence を補って通常の",
            "`軽微` の定義への照合と `adopted` / `rejected` の判断",
            "指摘が成立したと仮定した場合の影響を影響基準に当てて verdict を確定した",
            "指摘IDごとに不採用（理由: evidence 不足）として",
            "`review.findings` に記録する",
        )
        for platform, text in self._draft_reference_texts(
            "adversarial-review.md"
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_draft_review_reference_resolves_the_reviewer_findings_link(self) -> None:
        """Resolve the cross-skill evidence contract link across shared and generated trees."""
        relative_link = "../../delegate-implementation/references/reviewer-findings.md"
        reference_paths = {
            "source": shared_skill_reference_path(
                DRAFT_SKILL, "adversarial-review.md"
            ),
            "claude": generated_skill_reference_path(
                "claude", DRAFT_SKILL, "adversarial-review.md"
            ),
            "codex": generated_skill_reference_path(
                "codex", DRAFT_SKILL, "adversarial-review.md"
            ),
        }
        texts = self._draft_reference_texts("adversarial-review.md")
        for structure, reference_path in reference_paths.items():
            with self.subTest(structure=structure):
                self.assertIn(relative_link, texts[structure])
                resolved = (REPOSITORY_ROOT / reference_path).parent / relative_link
                self.assertTrue(
                    resolved.resolve().is_file(),
                    f"unresolved cross-skill link from {reference_path}",
                )

    def test_draft_overengineering_reference_confines_plan_review_routing(
        self,
    ) -> None:
        """Route every over-engineering finding back into plan edits only."""
        required = (
            "プラン入力モード",
            "指摘の反映経路はプラン修正だけ",
            "`review-patch-refactorer` を使わない",
            "adversarial の収束後に1回",
        )
        for platform, text in self._draft_reference_texts(
            "overengineering-plan-review.md"
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_adversarial_reviewer_defines_failure_path_scope_and_finding_contract(
        self,
    ) -> None:
        """Return only findings that identify a concrete failure path."""
        source = self._repository_text(
            Path("shared/agents/plan-adversarial-reviewer.md")
        )
        normalized = "".join(source.split())
        review_scope = (
            "このプランのまま実装したとき、AC を満たせない・検証できない・実装できない・"
            "手戻りが生じる具体的な失敗経路が存在するか。",
            "失敗経路を特定できる指摘だけを返す",
            "反証を能動的に探索する",
            "失敗経路を特定できない懸念の列挙",
            "指摘0件は正常な結果として扱います",
            "自身はファイルを変更しない",
            "ループの打ち切りは判定しません",
        )
        finding_types = (
            "見落とし",
            "根拠のない仮定",
            "AC の曖昧さ",
            "実現不能性",
            "依存の見落とし",
            "範囲の矛盾",
        )
        finding_fields = (
            "指摘ID",
            "対象（スキーマ path または AC id）",
            "類型",
            "判定（`軽微` / `修正推奨` / `修正必須`）",
            "具体的な失敗経路",
            "根拠",
            "解消を確認する条件",
        )

        for contract in review_scope + finding_types + finding_fields:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), normalized)
        self.assertNotIn("Needs attention", source)

    def test_plan_adversarial_reviewer_owns_the_trivial_verdict_definition(
        self,
    ) -> None:
        """Define 軽微 by an impact criterion plus a typed catalog with escape conditions."""
        source = self._repository_text(
            Path("shared/agents/plan-adversarial-reviewer.md")
        )
        normalized = "".join(source.split())
        required = (
            "採用してもしなくても、AC 充足・検証可能性・実行可否・後続の実装枝構造・"
            "受け入れ判断のいずれも変わらない指摘",
            "修正コストに見合わない指摘は `軽微` として扱う",
            "軽微としない条件",
            "`assumptions` に記録済みの事項の再指摘",
            "仮定を覆す新しい根拠を伴う場合",
            "カタログは影響基準の適用例",
            "カタログ外の指摘も影響基準を満たせば `軽微`",
        )

        for contract in required:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), normalized)

    def test_plan_adversarial_reviewer_consumes_the_ledger_without_resubmitting(
        self,
    ) -> None:
        """Take the prior-round ledger and never resubmit resolved findings without new grounds."""
        source = self._repository_text(
            Path("shared/agents/plan-adversarial-reviewer.md")
        )
        normalized = "".join(source.split())
        required = (
            "前 round の指摘台帳",
            "解消済み・不採用記録済みの指摘を、新しい根拠なしに再提出しない",
        )

        for contract in required:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), normalized)

    def test_over_engineering_reviewer_defines_additive_plan_input_mode(
        self,
    ) -> None:
        """Add a plan-input mode that rereads the diff contract without touching it."""
        source = self._repository_text(
            Path("shared/agents/over-engineering-reviewer.md")
        )
        normalized = "".join(source.split())
        required = (
            "## プラン入力モード",
            "既定は現行の diff 入力モード",
            "明示して Implementation Plan Data を渡した場合のみ",
            "プランが新規に導入しようとする要素",
            "テスト結果は入力として要求しない",
            "どの AC・制約にも辿れない計画要素",
            "実装詳細が未確定の要素には適用しない",
            "`review-patch-refactorer` は使わない",
            "判定せず親へ差し戻して",
        )

        for contract in required:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), normalized)

    def test_plan_drafting_requires_quantifiable_or_observable_ac_wording(
        self,
    ) -> None:
        """Require every AC to name a quantitative value, an enumeration, or an observable event."""
        required = (
            "AC は定量値・列挙・観測可能な事象のいずれかの形式で書く。",
            "AC の text には、充足を判定する観測点(何を確認すれば、何が起きたら"
            "満たしたと言えるか)を含める。",
            "観測点を text の外に置き、判定者の解釈に委ねない。",
        )
        for platform, text in self._draft_reference_texts("plan-drafting.md").items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_drafting_provides_checkable_ac_reference_examples(self) -> None:
        """Pair each checkability pattern with a concrete example sentence."""
        required = (
            "## 判定可能な AC の参考例",
            "ショートカットの先回り: 判定者が実物を確認せず要約や代替物で済ませられる抜け道を、"
            "AC 側で先に塞ぐ書き方。",
            "生成された出力ファイルそのものを確認対象とし、内容を要約した報告や動作説明では"
            "代替しない。出力ファイルを開き、指定した項目がすべて含まれていることを確認する。",
            "スコープ外の明示: AC が判定する範囲としない範囲を text 内で書き分ける書き方。",
            "入力チェックはメールアドレス形式と必須項目の有無だけを判定する。"
            "パスワード強度の判定はこの AC の対象にしない。",
        )
        for platform, text in self._draft_reference_texts("plan-drafting.md").items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)


class ReviewerFindingsContractTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _reviewer_findings_reference_texts(self) -> dict[str, str]:
        paths = {
            "source": shared_skill_reference_path(
                DELEGATE_SKILL, REVIEWER_FINDINGS_REFERENCE
            ),
            "claude": generated_skill_reference_path(
                "claude", DELEGATE_SKILL, REVIEWER_FINDINGS_REFERENCE
            ),
            "codex": generated_skill_reference_path(
                "codex", DELEGATE_SKILL, REVIEWER_FINDINGS_REFERENCE
            ),
        }
        for path in paths.values():
            self.assertTrue(
                (REPOSITORY_ROOT / path).is_file(),
                f"missing reviewer findings reference: {path}",
            )
        return {key: self._repository_text(path) for key, path in paths.items()}

    def _findings_reviewer_texts(self, name: str) -> dict[str, str]:
        """Read one reviewer manuscript and both distributed agent artifacts."""
        return {
            "shared": self._repository_text(Path("shared/agents") / f"{name}.md"),
            "claude": self._repository_text(CLAUDE_PROFILE_PATH / f"{name}.md"),
            "codex": self._repository_text(CODEX_PROFILE_PATH / f"{name}.toml"),
        }

    def test_reviewer_findings_reference_is_distributed_with_warning_and_toc(
        self,
    ) -> None:
        """Distribute the findings contract to both platforms from a warning-free source."""
        texts = self._reviewer_findings_reference_texts()
        self.assertTrue(texts["source"].startswith("# "))
        self.assertFalse(texts["source"].startswith(GENERATED_MARKDOWN_WARNING))
        self.assertIn("## 目次", texts["source"])
        for platform in ("claude", "codex"):
            with self.subTest(platform=platform):
                self.assertTrue(
                    texts[platform].startswith(f"{GENERATED_MARKDOWN_WARNING}\n\n")
                )
                self.assertIn("## 目次", texts[platform])
        self.assertEqual(texts["claude"], texts["codex"])

    def test_reviewer_findings_reference_defines_summary_line_and_evidence(
        self,
    ) -> None:
        """Hold the canonical two-point findings contract and defer wording to each reviewer."""
        required = (
            "## 指摘件数のサマリ行",
            "応答の冒頭に、指摘件数を1行で読み取れるサマリ行を置く。",
            "出力形式の先頭に判定項目を持つ reviewer は、その判定項目と同じ行に件数を示す。",
            "判定項目を持たない reviewer は、件数だけを示すサマリ行を冒頭に置く。",
            "指摘0件でもサマリ行を省略しない。",
            "0件であることを表す語は、各 reviewer が既に使っている語をそのまま使う。",
            "## 指摘ごとの evidence",
            "該当ファイルと行の引用",
            "再現手順",
            "参照した Data の path と id",
            "いずれか1つを示せばよい。",
            "evidence 専用の項目を新設しない。",
            "判定語彙、0件の表記、判定対象外の範囲の書き方は各 reviewer 原稿を正本とし、"
            "この reference では変更しない。",
        )
        for platform, text in self._reviewer_findings_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_delegate_skill_links_to_the_reviewer_findings_reference(self) -> None:
        """Reach the findings contract from the QA phase of the delegation workflow."""
        main_texts = {
            SHARED_SKILL_PATH: self._repository_text(SHARED_SKILL_PATH),
            GENERATED_SKILL_PATHS["claude"]: self._repository_text(
                GENERATED_SKILL_PATHS["claude"]
            ),
            GENERATED_SKILL_PATHS["codex"]: self._repository_text(
                GENERATED_SKILL_PATHS["codex"]
            ),
        }
        for path, main in main_texts.items():
            with self.subTest(path=path):
                self.assertIn(f"(references/{REVIEWER_FINDINGS_REFERENCE})", main)
                self.assertLess(
                    main.index("(references/qa-and-integration.md)"),
                    main.index(f"(references/{REVIEWER_FINDINGS_REFERENCE})"),
                )

    def test_findings_reviewers_require_a_count_summary_and_evidence(self) -> None:
        """Require the shared two points from every reviewer that returns findings."""
        for name in FINDINGS_REVIEWER_NAMES:
            for platform, text in self._findings_reviewer_texts(name).items():
                with self.subTest(name=name, platform=platform):
                    normalized = "".join(text.split())
                    self.assertIn(
                        "".join(FINDINGS_COUNT_REQUIREMENT.split()), normalized
                    )
                    self.assertIn(
                        "".join(FINDINGS_EVIDENCE_REQUIREMENT.split()), normalized
                    )

    def test_verdict_leading_reviewers_carry_the_count_in_their_verdict_item(
        self,
    ) -> None:
        """Add the count to the leading verdict item instead of a separate summary line."""
        preserved_zero_finding_words = {
            "responsibility-boundary-reviewer": "`問題なし`",
            "test-quality-reviewer": "指摘がない場合は `Pass` としてください",
            "security-side-effect-reviewer": "指摘がない場合は `Pass` とし",
        }
        for name, summary_item in VERDICT_LEADING_REVIEWER_SUMMARY_ITEMS.items():
            for platform, text in self._findings_reviewer_texts(name).items():
                with self.subTest(name=name, platform=platform):
                    normalized = "".join(text.split())
                    self.assertIn("".join(summary_item.split()), normalized)
                    self.assertNotIn(
                        "".join(COUNT_ONLY_REVIEWER_SUMMARY_LINE.split()),
                        normalized,
                    )
                    self.assertIn(
                        "".join(preserved_zero_finding_words[name].split()),
                        normalized,
                    )

    def test_count_only_reviewers_add_a_summary_line_without_a_verdict_item(
        self,
    ) -> None:
        """Add a count-only summary line and keep the existing zero-finding wording."""
        for name in COUNT_ONLY_REVIEWER_NAMES:
            for platform, text in self._findings_reviewer_texts(name).items():
                with self.subTest(name=name, platform=platform):
                    normalized = "".join(text.split())
                    self.assertIn(
                        "".join(COUNT_ONLY_REVIEWER_SUMMARY_LINE.split()), normalized
                    )
                    self.assertIn("指摘0件", normalized)
                    for summary_item in VERDICT_LEADING_REVIEWER_SUMMARY_ITEMS.values():
                        self.assertNotIn(
                            "".join(summary_item.split()), normalized
                        )


# The 19 field labels the reviewer-launch template must expose as independent lines
# (AC-1). Order mirrors the branch spec so the fence-extraction test below can pair
# each label with the line at the same position, catching a field silently merged
# onto a neighboring line (a defect a plain substring search would miss).
REVIEWER_LAUNCH_TEMPLATE_FIELDS = (
    "対象 reviewer",
    "確認させる観点",
    "対象リスク",
    "review 範囲",
    "タスクの目的",
    "Acceptance Criteria",
    "親が明示した制約",
    "基準 commit",
    "対象 commit 範囲",
    "commit log",
    "変更ファイル一覧",
    "diff artifact の絶対 path",
    "diff text（artifact を生成できない場合）",
    "`git status` の結果",
    "テスト結果",
    "親が選択した周辺コンテキスト",
    "そのコンテキストを渡す理由",
    "返却してほしい判定",
    "前回の指摘と親の採否（ゲート再実行時）",
)


class ReviewerLaunchTemplateAndDiffArtifactContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _qa_and_integration_reference_texts(self) -> dict[str, str]:
        skills = self._repository_skill_texts()
        return {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }

    def _extract_reviewer_launch_template(self, reference: str) -> str:
        """Isolate the fenced launch template, mirroring `_extract_qa_report_template`."""
        heading = "## reviewer 起動テンプレート"
        opening_fence = "```text\n"
        closing_fence = "\n```"
        self.assertEqual(1, reference.count(heading))
        section = reference.split(heading, 1)[1].split("\n## ", 1)[0]
        self.assertEqual(1, section.count(opening_fence))
        fenced_content = section.split(opening_fence, 1)[1]
        self.assertIn(closing_fence, fenced_content)
        return fenced_content.split(closing_fence, 1)[0]

    def test_repository_reviewer_launch_template_lists_all_fields_as_independent_lines(
        self,
    ) -> None:
        """Require every reviewer-launch field on its own filled-in line inside one fence."""
        for platform, reference in self._qa_and_integration_reference_texts().items():
            with self.subTest(platform=platform):
                template = self._extract_reviewer_launch_template(reference)
                self.assertNotIn("{{", template)
                lines = [line for line in template.splitlines() if line.strip()]
                self.assertEqual(len(REVIEWER_LAUNCH_TEMPLATE_FIELDS), len(lines))
                for field, line in zip(REVIEWER_LAUNCH_TEMPLATE_FIELDS, lines):
                    self.assertTrue(
                        line.strip().startswith(f"- {field}:"),
                        f"{platform}: expected field '{field}' line, got {line!r}",
                    )

    def test_repository_reviewer_launch_template_is_mandatory_and_reachable(
        self,
    ) -> None:
        """Require full field completion and let two independent sections reach it."""
        obligation_contracts = (
            "必須完了ゲートの reviewer と専門 reviewer のどちらを起動する場合も",
            "次のテンプレートの全欄を1項目ずつ埋めて渡す",
            "該当がない欄は「なし」と記入する",
            "欄を空欄のまま残すことと、欄自体を削除することを禁じる",
        )
        for platform, reference in self._qa_and_integration_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(reference.split())
                for contract in obligation_contracts:
                    self.assertIn("".join(contract.split()), normalized)

                self.assertEqual(1, reference.count("## 必須完了ゲート"))
                mandatory_gate_section = reference.split(
                    "## 必須完了ゲート", 1
                )[1].split("\n## ", 1)[0]
                self.assertIn(
                    "「reviewer 起動テンプレート」", mandatory_gate_section
                )

                self.assertEqual(1, reference.count("## 責務境界"))
                responsibility_section = reference.split("## 責務境界", 1)[
                    1
                ].split("\n## ", 1)[0]
                self.assertIn(
                    "「reviewer 起動テンプレート」", responsibility_section
                )

    def test_repository_diff_artifact_creation_defines_path_and_inherited_rules(
        self,
    ) -> None:
        """Fix the diff-artifact save path and inherit only the non-Markdown QA rules."""
        required_contracts = (
            "## diff artifact の作成",
            "`.agentic-qa/reports/<slug>-diff.patch`",
            "slug の base の",
            "候補順と正規化手順、Windows 予約名の扱い、衝突時の suffix 選択、ancestor 検査、"
            "削除時の再検査、Git 管理と保持は",
            "[永続 QA レポート](qa-report.md)",
            "Markdown file を前提とする path 制約は継承しない",
            "target は `.agentic-qa/reports/` 直下の単一 file に限る",
            "file name component に path separator を許可しない",
            "`.` または `..` を許可しない",
            "絶対 path を許可しない",
            "`-diff` を保持したまま `<slug>-diff-2.patch` の順に最初の空きを選ぶ",
            "worker worktree で取得した `git -C <worktree> diff <base>...HEAD` の出力を、"
            "親が転記・要約せず",
            "1回の書き出しでそのまま保存する",
            "保存先 path は親の統合 checkout の repository root を基準に解決し、"
            "ancestor 検査も同じ root で行う",
            "同一の diff 状態（同じ実装枝、同じ commit 範囲、修正 commit の追加なし）に"
            "対する複数 reviewer の起動では同じ artifact を渡してよい",
            "diff 状態が変わったとき（修正後のゲート再実行、別の実装枝）は新しい"
            "artifact を生成し、変化後に古い artifact を渡さない",
            "候補 path が既存の場合に上書きせず失敗する Action",
            "候補 path の衝突による失敗は次の suffix を選び直す",
            "衝突以外の書き出し失敗は「diff artifact の受け渡しと停止条件」の確認手順に従い",
            "artifact 経路を既定とし、diff text の直接受け渡しは同節の停止条件に"
            "該当する場合の例外とする",
            "保存先 directory が存在しない場合は、ancestor 検査を行ったうえで作成し、"
            "作成後に同じ検査を再実行してから書き出す",
        )
        for platform, reference in self._qa_and_integration_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(reference.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized)
                self.assertNotIn("{{", reference.split("## diff artifact の作成", 1)[1])

    def test_repository_diff_artifact_handoff_confirms_and_stops_on_secrets(
        self,
    ) -> None:
        """Confirm the write before handoff and fall back to diff text on stop conditions."""
        required_contracts = (
            "## diff artifact の受け渡しと停止条件",
            "起動 prompt の diff artifact 欄には絶対 path を書く",
            "永続 QA レポートと会話上の報告へ path を記録する場合は"
            "repository 相対 path だけを使う",
            "verbatim 保存される diff 本文はこの記録規則の適用対象にしない",
            "reviewer がその file を Read し全文を diff text として判定根拠にする旨の指示を添える",
            "その text を判定根拠にする旨を添える",
            "2つの欄は排他とし、採らなかった側の欄には「なし」と記入して、"
            "両方を同時に有効な指示として残さない",
            "token、password、cookie、Authorization、private key、`.env` の値、"
            "credential 付き URL、個人情報のいずれかを含む場合",
            "作成 Action を保証できない場合は artifact を生成せず、diff text 欄へ本文を"
            "直接記入して渡し、生成しなかった理由を記録する",
            "repository 相対 path、コード中の文字列リテラル、prompt テンプレートの原稿は、"
            "diff が構造上含む要素として停止条件に該当しない",
            "親は diff 全文を自分の context へ読み込まずに書き出し結果を確認する",
            "書き出し command の exit status が 0 であることと、"
            "artifact が空でないことの2点で行う",
            "commit を持つ実装枝に対して artifact が空になった場合は、取得元 worktree または"
            "基準 commit の指定誤りとして扱う",
            "満たさない artifact は reviewer へ渡さず",
            "[永続 QA レポート](qa-report.md) の削除時の再検査に従って削除したうえで再生成し、"
            "再生成できない場合は diff text 経路へ落ちる",
            "この削除は qa-report.md の「明示的な削除」に該当し、保持規約の違反にならない",
        )
        for platform, reference in self._qa_and_integration_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(reference.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized)

    def test_repository_existing_reviewer_launch_sites_connect_to_diff_artifact_path(
        self,
    ) -> None:
        """Connect the four existing launch-data sites to the artifact-path route."""
        new_connections = (
            "親の統合 checkout に生成した diff artifact",
            "この確認によって worker の変更の混入と誤認しない",
            "ここでの作業 tree は worker worktree を指し、親の統合 checkout に保存した"
            "diff artifact を reviewer が Read することとは矛盾しない",
            "diff artifact の絶対 path を渡すことを既定とし、artifact を生成できない場合だけ"
            "diff text 欄へ本文を直接記入する",
            "この基本情報は「reviewer 起動テンプレート」の各欄に対応する",
            "起動 prompt は「reviewer 起動テンプレート」の全欄を埋めて渡す",
            "起動時は「reviewer 起動テンプレート」の全欄を埋め、diff artifact の絶対 path を"
            "渡すことを既定とする",
            "「専門 reviewer」節の対象リスクと review 範囲、「返却と統合」手順5 の task・AC・"
            "commit 範囲・変更ファイル・diff text・対象 risk を含め、reviewer 起動時に渡す"
            "Data はすべてこのテンプレートの欄として吸収する",
            "テンプレート外に残る起動時 Data はない",
        )
        for platform, reference in self._qa_and_integration_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(reference.split())
                for contract in new_connections:
                    self.assertIn("".join(contract.split()), normalized)

    def test_repository_git_status_step_distinguishes_own_diff_artifact_from_worker_changes(
        self,
    ) -> None:
        """Reach a rule that separates the parent's own diff artifact from contamination."""
        for platform, reference in self._qa_and_integration_reference_texts().items():
            with self.subTest(platform=platform):
                integration_steps = reference.split("## 返却と統合", 1)[1].split(
                    "\n## ", 1
                )[0]
                step_2 = integration_steps.split("2. 親は", 1)[1].split("3. ", 1)[0]
                normalized_step_2 = "".join(step_2.split())
                self.assertIn(
                    "".join("親の統合 checkout に生成した diff artifact".split()),
                    normalized_step_2,
                )
                self.assertIn(
                    "".join("作成規約は「diff artifact の作成」節に従う".split()),
                    normalized_step_2,
                )


if __name__ == "__main__":
    unittest.main()
