"""Repository contracts for impl-lead QA report behavior."""

from __future__ import annotations

from pathlib import Path
import json
import re
import unittest

from build_plugin_assets_test_support import (
    IMPL_LEAD_SKILL,
    GENERATED_MARKDOWN_WARNING,
    GENERATED_SKILL_REFERENCE_PATHS,
    GENERATED_SKILL_PATHS,
    REPOSITORY_ROOT,
    RepositoryContractSupport,
    SHARED_SKILL_PATH,
    SHARED_SKILL_REFERENCE_PATHS,
    SKILL_REFERENCE_NAMES,
)


class ImplLeadQaReportContractsTest(
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
            "qa-and-integration.md": "# 返却の QA と統合",
            "reviewer-dispatch.md": "# Reviewer の起動と diff の受け渡し",
            "branch-review.md": "# 枝レビューの進行",
            "finding-routing.md": "# Finding の修正 routing",
            "run-closeout.md": "# Run の終了処理",
            "qa-report.md": "# 永続 QA レポート",
        }
        direct_references = (
            "implementation-branches.md",
            "expert-selection.md",
            "qa-and-integration.md",
            "branch-review.md",
            "finding-routing.md",
            "run-closeout.md",
            "qa-report.md",
            "branch-plan-intake.md",
            "reviewer-findings.md",
        )

        for path, main in main_texts.items():
            with self.subTest(path=path):
                self.assertLess(len(main.splitlines()), 300)
                for name in direct_references:
                    self.assertIn(f"(references/{name})", main)
                self.assertNotIn("(references/reviewer-dispatch.md)", main)
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
        for platform, references in (
            ("shared", skills.source_references),
            ("claude", skills.claude_references),
            ("codex", skills.codex_references),
        ):
            with self.subTest(platform=platform):
                self.assertIn(
                    "(reviewer-dispatch.md)",
                    references["finding-routing.md"],
                )

    def test_repository_impl_lead_local_markdown_links_resolve(self) -> None:
        """Resolve every local reference file and section reached by impl-lead."""
        document_sets = (
            (
                "shared",
                SHARED_SKILL_PATH,
                tuple(SHARED_SKILL_REFERENCE_PATHS.values()),
            ),
            (
                "claude",
                GENERATED_SKILL_PATHS["claude"],
                tuple(GENERATED_SKILL_REFERENCE_PATHS["claude"].values()),
            ),
            (
                "codex",
                GENERATED_SKILL_PATHS["codex"],
                tuple(GENERATED_SKILL_REFERENCE_PATHS["codex"].values()),
            ),
        )
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)(?:#([^)]+))?\)")

        for platform, main_path, reference_paths in document_sets:
            for source_path in (main_path, *reference_paths):
                document = self._repository_text(source_path)
                for target, anchor in link_pattern.findall(document):
                    resolved = (
                        REPOSITORY_ROOT / source_path.parent / target
                    ).resolve()
                    with self.subTest(
                        platform=platform,
                        source=source_path,
                        target=target,
                        anchor=anchor,
                    ):
                        self.assertTrue(resolved.is_file(), resolved)
                        if anchor:
                            target_text = resolved.read_text(encoding="utf-8")
                            headings = re.findall(r"^#{1,6} (.+)$", target_text, re.M)
                            slugs = {
                                re.sub(r"\s+", "-", heading.strip().lower())
                                for heading in headings
                            }
                            self.assertIn(anchor, slugs)

        skills = self._repository_skill_texts()
        section_links = (
            (
                "qa-and-integration.md",
                "reviewer へ渡すコンテキスト",
                "reviewer-dispatch.md",
                "reviewer へ渡すコンテキスト",
                "",
            ),
            (
                "branch-review.md",
                "専門 reviewer",
                "reviewer-dispatch.md",
                "専門 reviewer",
                " の起動条件の対象外",
            ),
            (
                "run-closeout.md",
                "修正先の選択",
                "finding-routing.md",
                "修正先の選択",
                " へ差し戻し",
            ),
            (
                "reviewer-findings.md",
                "Reviewer の起動と diff の受け渡し",
                "reviewer-dispatch.md",
                "reviewer 起動前後の worktree・親 checkout 照合",
                " の\n「reviewer 起動前後の worktree・親 checkout 照合」",
            ),
        )
        for platform, references in (
            ("shared", skills.source_references),
            ("claude", skills.claude_references),
            ("codex", skills.codex_references),
        ):
            for source, label, target, target_heading, link_context in section_links:
                with self.subTest(
                    platform=platform,
                    source=source,
                    label=label,
                    target=target,
                    target_heading=target_heading,
                ):
                    self.assertIn(
                        "".join(f"[{label}]({target}){link_context}".split()),
                        "".join(references[source].split()),
                    )
                    target_headings = re.findall(
                        r"^#{1,6} (.+)$",
                        references[target],
                        re.M,
                    )
                    self.assertIn(target_heading, target_headings)

    def test_repository_qa_sections_have_one_owner_and_matching_toc(self) -> None:
        """Keep each QA lifecycle section in one responsibility reference."""
        expected_sections = {
            "qa-and-integration.md": (
                "返却と統合",
                "親の QA",
                "返却 diff の変更単位判定",
                "再分割・再承認ゲート",
            ),
            "reviewer-dispatch.md": (
                "専門 reviewer",
                "reviewer 起動テンプレート",
                "reviewer 起動前後の worktree・親 checkout 照合",
                "diff artifact の作成",
                "diff artifact の受け渡しと停止条件",
                "diff artifact の削除",
            ),
            "branch-review.md": (
                "必須完了ゲート",
                "枝レビューの4相",
                "reviewer 間の競合解消",
            ),
            "finding-routing.md": (
                "evidence を欠く指摘の扱い",
                "過剰実装ゲートの除去許可",
                "修正先の選択",
                "責務境界",
            ),
            "run-closeout.md": (
                "Branch Plan 単位の終了処理",
                "未統合で終了する場合",
                "統合済み diff review",
                "後始末",
                "最終報告",
            ),
        }
        skills = self._repository_skill_texts()
        for platform, references in (
            ("shared", skills.source_references),
            ("claude", skills.claude_references),
            ("codex", skills.codex_references),
        ):
            for name, expected in expected_sections.items():
                text = references[name]
                with self.subTest(platform=platform, reference=name):
                    self.assertEqual(
                        expected, self._markdown_table_of_contents(text)
                    )
                    self.assertEqual(
                        expected, self._markdown_section_headings(text)
                    )

    def test_repository_distribution_version_is_4_3_0(self) -> None:
        """Pin the Branch Plan Set schema to the synchronized minor version."""
        shared_version = self._repository_text(Path("shared/VERSION")).strip()
        self.assertEqual("4.3.0", shared_version)
        for manifest_path in (
            Path("plugins/claude/.claude-plugin/plugin.json"),
            Path("plugins/codex/.codex-plugin/plugin.json"),
        ):
            manifest = json.loads(self._repository_text(manifest_path))
            with self.subTest(path=manifest_path):
                self.assertEqual("4.3.0", manifest["version"])
        self.assertEqual(
            "4.3.0",
            self._repository_text(Path("plugins/codex/install/VERSION")).strip(),
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
            "Branch Plan ごとに report は1つだけ生成",
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
            "repository root 相対の `.tugite/reports/<slug>.md`",
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
            "`.tugite` と `reports` の各既存 ancestor component",
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
            "`tugite` repository の template source と generated asset は tracked 配布物",
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
            "Failure impact",
            "Implementation complexity",
            "mode は implementation complexity から導出する",
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
            "ユーザーによる専門 reviewer の明示がない",
            "reviewer の責務に一致する `failure_impact.reasons` がない",
            "親 QA が返却 diff から特定した reviewer 固有の対象リスクがない",
            "3条件をすべて満たす場合だけ、専門 reviewer の有効な非起動理由とする",
            "最終判断は親だけが記入",
        )

        for path, report in self._read_qa_report_references().items():
            with self.subTest(path=path):
                normalized = "".join(report.split())
                for field in required_fields:
                    self.assertIn("".join(field.split()), normalized)
                self.assertNotIn(
                    "".join(
                        "対象となる failure impact がないことは有効な理由".split()
                    ),
                    normalized,
                )

                template = self._extract_qa_report_template(report)
                required_template_fields = (
                    "Logical checkout ID / commit",
                    "Logical worktree ID",
                    "Branch (sanitized or omitted)",
                    "Implementer role",
                    "Failure impact",
                    "Implementation complexity",
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
        closeout_reference = skills.source_references["run-closeout.md"]
        run_closeout = "".join(closeout_reference.split())
        unintegrated_section = closeout_reference[
            closeout_reference.index("## 未統合で終了する場合") : closeout_reference.index(
                "## 統合済み diff review"
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
            "[Run の終了処理](references/run-closeout.md) に従い、"
            "適用可能な統合済み diff review と最終検証を行い、親の最終判断を確定する。"
        )
        cleanup_decision = (
            "[Run の終了処理](references/run-closeout.md) に従い、最終 gate 後に、"
            "各 worker worktree の cleanup の実施可否と結果を確定する。"
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
            "通常の `Needs revision` は [修正先の選択](finding-routing.md) へ差し戻し、"
            "top-level workflow を継続する。",
            "親が未統合の枝について `Rejected` / `Needs revision` を最終判断とし、top-level workflow を終了する場合だけ",
            "実行可能な検証を行い",
            "未実行の検証、未統合の理由、worktree を保持する理由",
            "Data として記録",
            "main の手順9へ戻る",
        )

        for contract in main_contracts:
            self.assertIn("".join(contract.split()), main)
        for contract in reference_contracts:
            self.assertIn("".join(contract.split()), run_closeout)
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

    def test_repository_qa_report_generation_unit_is_one_report_per_branch_plan(
        self,
    ) -> None:
        """Generate one persistent report per Branch Plan, not per top-level run."""
        # 生成単位は「位置づけと出力条件」と「標準テンプレート」の2箇所に書かれている。
        # 片方だけの改訂で通らないよう、節ごとに切り出して別々に固定し、あわせて
        # 旧単位の語が1箇所も残っていないことを不在で検査する。
        for path, report in self._read_qa_report_references().items():
            with self.subTest(path=path):
                self.assertEqual(
                    0,
                    report.count("トップレベルの workflow run"),
                    "旧 run 単位の生成規約が残っている",
                )

                position = report.split("## 位置づけと出力条件", 1)[1].split(
                    "\n## ", 1
                )[0]
                self.assertIn(
                    "".join(
                        "Branch Plan ごとに report は1つだけ生成する。".split()
                    ),
                    "".join(position.split()),
                )
                self.assertIn(
                    "".join("複数の実装枝は同じ report へ列挙し".split()),
                    "".join(position.split()),
                )

                template_section = report.split("## 標準テンプレート", 1)[1].split(
                    "\n## ", 1
                )[0]
                self.assertIn(
                    "".join(
                        "次のテンプレートを Branch Plan ごとに1つ使用する。".split()
                    ),
                    "".join(template_section.split()),
                )

    def test_run_closeout_finalizes_each_branch_plan_independently(self) -> None:
        """Close out each Branch Plan without waiting for the remaining ones."""
        required_contract = (
            "Run の終了処理(統合済み diff review、後始末、最終報告、テスト一覧 file、"
            "永続 QA レポート)は Branch Plan 単位で行う。",
            "未実行の後続 Branch Plan があっても、完了した Branch Plan の後始末と"
            "最終報告は行う。",
            "完了した Branch Plan の id は実行 Data として親が保持し、"
            "Branch Plan Data へ書き戻さない。",
            "`status` に完了を表す値を足さない。",
            "境界で止まった後に再開する場合、完了済みの Branch Plan を再実行しない。",
            "実行 Data を復元できない場合は、Branch Plan ごとの最終報告と統合済み commit を"
            "根拠に親が完了済みを確定してから再開する。",
            "最終報告は Branch Plan ごとに作り、`order` 順に並べる。",
            "Set 全体の新しい要約は作らない。",
            "テスト一覧 file は Branch Plan ごとに生成し、名前の衝突は既存の suffix 選択規約で"
            "解決する。",
            "Branch Plan 単位の新しい命名規約は作らない。",
        )
        for platform, reference in self._impl_lead_reference_texts(
            "run-closeout.md"
        ).items():
            section = reference.split("## Branch Plan 単位の終了処理", 1)[-1].split(
                "\n## ", 1
            )[0]
            normalized = "".join(section.split())
            for contract in required_contract:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)

    def test_run_closeout_blocks_successor_branch_plans_when_a_predecessor_does_not_complete(
        self,
    ) -> None:
        """Stop successors when a predecessor ends without completing, even unattended."""
        # 2文を別々に固定する。`unattended` の優先関係が欠けると、全 Branch Plan が
        # 授権済みの run で授権が先行完了の要求を上書きすると読めてしまう。
        required_contract = (
            "先行 Branch Plan が完了せずに終了した場合(親が未統合の枝について "
            "`Rejected` / `Needs revision` を最終判断とした場合)は、後続 Branch Plan を"
            "実行せず未実行として報告する。",
            "`unattended` で全 Branch Plan が授権済みの場合も、この規定が授権より優先する。",
        )
        for platform, reference in self._impl_lead_reference_texts(
            "run-closeout.md"
        ).items():
            normalized = "".join(reference.split())
            for contract in required_contract:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)


if __name__ == "__main__":
    unittest.main()
