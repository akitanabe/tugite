"""Repository contracts for reviewer findings."""

from __future__ import annotations

from pathlib import Path
import unittest

from build_plugin_assets_test_support import (
    CLAUDE_PROFILE_PATH,
    CODEX_PROFILE_PATH,
    IMPL_LEAD_SKILL,
    GENERATED_MARKDOWN_WARNING,
    GENERATED_SKILL_PATHS,
    REPOSITORY_ROOT,
    REVIEWER_NAMES,
    RepositoryContractSupport,
    SHARED_SKILL_PATH,
    generated_skill_reference_path,
    shared_skill_reference_path,
)


REVIEWER_FINDINGS_REFERENCE = "reviewer-findings.md"
FINDINGS_REVIEWER_NAMES = (
    "responsibility-boundary-reviewer",
    "test-quality-reviewer",
    "security-side-effect-reviewer",
    "writing-principles-reviewer",
    "over-engineering-reviewer",
    "plan-adversarial-reviewer",
)
FINDINGS_COUNT_REQUIREMENT = "指摘件数は0件でも必ず"
FINDINGS_EVIDENCE_REQUIREMENT = (
    "evidence（該当ファイルと行の引用 / 再現手順 / 参照した Data の path と id の"
    "いずれか）を示す"
)
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
QA_AND_INTEGRATION_REFERENCE = "qa-and-integration.md"
QA_AND_INTEGRATION_MUST_GATES_SECTION = "## 必須完了ゲート"
# Both counts are derived from REVIEWER_NAMES / FINDINGS_REVIEWER_NAMES so that
# adding an 8th reviewer to those sets fails this test instead of leaving the
# manuscript's literal count silently stale.
READ_ONLY_ENFORCEMENT_SECTION = "## read-only の担保"
READ_ONLY_ENFORCEMENT_CONTRACTS = (
    READ_ONLY_ENFORCEMENT_SECTION,
    "指摘 Data を返すだけの reviewer には、ファイルを書き換える tool を渡さない。",
    "Claude 向けは agent frontmatter の `disallowed_tools` に "
    "`Edit` / `Write` / `NotebookEdit` を置き、"
    "Codex 向けは `sandbox_mode` の `read-only` が同じ役割を果たす。",
    # Pins the criterion that splits exploration reach. Without it the section
    # would carry only the write-tool ban, and the reason one reviewer is given
    # `Bash` while another is not would be recorded nowhere.
    "判定に検証の実行や基準 commit 時点のファイル参照が必要な reviewer には `Bash` を渡し、"
    "渡された Data のテキストだけで判定できる reviewer には渡さない。",
    "どの reviewer がどちらに属するかはこの節に列挙せず、各 agent 定義を正本とする。",
    # Pins the platform asymmetry the split introduces: a reviewer holding
    # `Bash` can write through it, so on Claude the ban is manuscript text
    # only. Recording it keeps a later reader from assuming both platforms
    # enforce the ban mechanically and removing the instruction as redundant.
    "`Bash` を渡した reviewer について、Claude 側で書き込みを禁じているのは原稿の指示文だけである。",
    "担保の強さは platform 間で非対称であり、"
    "これは `Bash` を渡す判断に伴う既知の制約として引き受ける。",
    # Pins the working limits that apply once `Bash` is granted. The reach
    # split alone leaves "may run commands" unbounded, and nothing on the
    # Claude side stops a reviewer from rewriting what it is reviewing.
    "`Bash` を渡した reviewer は、対象 worktree では読み取りと検証の実行だけを行い、"
    "追跡ファイルを変更しない。",
    "ミューテーション注入や検証用の複製のように書き込みを伴う検証は、"
    "対象 worktree の外へ複製してそこで行う。",
    "`commit` / `checkout` / `switch` / `reset` / `stash` / `rebase` / `merge` / "
    "`cherry-pick` / `worktree add` / `worktree remove` / `branch -d` / `push` を行わない。",
    # Pins why the git operations are listed apart from file edits: they are
    # the ones the parent's own check cannot see.
    "追跡ファイルの編集は親の `git status --short` 検査で気づけるが、これらは status を"
    "汚さずにレビュー対象の snapshot 自体を差し替えるため、その検査をすり抜けるためである。",
    # Pins that the limits are a contract rather than an enforced setting, so a
    # later reader does not assume the tool metadata already blocks them and
    # drop the instruction as redundant.
    "この作業範囲は tool metadata では強制できない。",
    "`disallowed_tools` は tool 単位の指定であり、`Bash` で実行する command の中身までは"
    "選べないためである。",
    f"この節の対象は、上記2点の{len(FINDINGS_REVIEWER_NAMES)}本に "
    f"`expert-selection-reviewer` を加えた reviewer {len(REVIEWER_NAMES)}本とする。",
    "指摘された範囲を修正する `review-patch-refactorer` は書き込みを要するため、"
    "この節でも対象外とする。",
    # Pins the scope disclaimer added in 「位置づけ」: without it, a reader
    # could mistake this section's reviewer count for the 「位置づけ」
    # section's 2-point scope.
    "ここで定めた対象は上記2点だけに適用する。"
    "「read-only の担保」は対象範囲が異なり、同節が自身の対象を定める。",
)
# The delegation pointer, not a second copy of the rule: qa-and-integration.md
# keeps only why the parent hands diff and test results over as Data.
READ_ONLY_ENFORCEMENT_DELEGATION = (
    "reviewer が read-only であることの担保は "
    "[Reviewer findings の共通契約](reviewer-findings.md) の「read-only の担保」に従う。"
)
# A restated read-only rule almost always names the concrete tools or the
# platform config key it grants/withholds. A paraphrase that names neither
# falls outside what a negative assert can catch; that gap is accepted.
# The absence of these markers is pinned across the whole document (not
# just the section the delegation pointer lives in): AC-5's target is this
# file in full, so a restated rule must fail this test regardless of which
# section it lands in.
# "Edit" is listed instead of "NotebookEdit" because it is already a
# substring match for it, and listing both would just be the same check
# twice. "disallowed_tools" / "sandbox_mode" are the platform config keys a
# restated rule tends to leak.
# "編集" (Japanese for "edit") is deliberately left out, but not because it
# is already in use: as of this change every marker below, "編集" included,
# occurs zero times in this document, which now names no tool at all. The
# exclusion is about future risk, not present occurrences: "編集" is a
# generic Japanese word this ~50KB document is far more likely to need
# legitimately (cleanup, parent QA, the review phases) than an English tool
# name is, so a whole-document ban on it would cost authoring freedom the
# English names don't, for a guard that only needs to catch a restated rule
# reappearing.
READ_ONLY_RULE_RESTATEMENT_MARKERS = (
    "Bash",
    "Edit",
    "Write",
    "disallowed_tools",
    "sandbox_mode",
)


class ReviewerFindingsContractTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _skill_reference_texts(self, reference: str) -> dict[str, str]:
        paths = {
            "source": shared_skill_reference_path(IMPL_LEAD_SKILL, reference),
            "claude": generated_skill_reference_path(
                "claude", IMPL_LEAD_SKILL, reference
            ),
            "codex": generated_skill_reference_path(
                "codex", IMPL_LEAD_SKILL, reference
            ),
        }
        for path in paths.values():
            self.assertTrue(
                (REPOSITORY_ROOT / path).is_file(),
                f"missing skill reference: {path}",
            )
        return {key: self._repository_text(path) for key, path in paths.items()}

    def _reviewer_findings_reference_texts(self) -> dict[str, str]:
        return self._skill_reference_texts(REVIEWER_FINDINGS_REFERENCE)

    @staticmethod
    def _section_lines(text: str, heading: str) -> list[str]:
        lines = text.splitlines()
        rest = lines[lines.index(heading) + 1 :]
        end = next(
            (index for index, line in enumerate(rest) if line.startswith("## ")),
            len(rest),
        )
        return rest[:end]

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
        """Distribute the findings contract to both platforms from a warning-free source, with 「read-only の担保」 listed in each 目次."""
        texts = self._reviewer_findings_reference_texts()
        toc_heading = "## 目次"

        def _toc_section(text: str) -> str:
            return text.split(toc_heading, 1)[1].split("##", 1)[0]

        self.assertTrue(texts["source"].startswith("# "))
        self.assertFalse(texts["source"].startswith(GENERATED_MARKDOWN_WARNING))
        self.assertIn(toc_heading, texts["source"])
        self.assertIn("read-only の担保", _toc_section(texts["source"]))
        for platform in ("claude", "codex"):
            with self.subTest(platform=platform):
                self.assertTrue(
                    texts[platform].startswith(f"{GENERATED_MARKDOWN_WARNING}\n\n")
                )
                self.assertIn(toc_heading, texts[platform])
                self.assertIn(
                    "read-only の担保", _toc_section(texts[platform])
                )
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

    def test_reviewer_findings_reference_requires_read_only_on_both_platforms(
        self,
    ) -> None:
        """Hold one canonical reason for enforcing read-only on every reviewer."""
        for platform, text in self._reviewer_findings_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in READ_ONLY_ENFORCEMENT_CONTRACTS:
                    self.assertIn("".join(contract.split()), normalized)

    def test_read_only_section_states_the_split_criterion_without_listing_members(
        self,
    ) -> None:
        """Leave each reviewer's exploration reach to its agent definition instead of copying the roster into the manuscript."""
        # `expert-selection-reviewer` and `review-patch-refactorer` are named
        # deliberately: the section has to say who it covers and who it does
        # not, which is scope, not a per-reviewer tool assignment. Every other
        # reviewer name appearing here would mean the roster is maintained in
        # two places again.
        listed_by_scope = {"expert-selection-reviewer", "review-patch-refactorer"}
        for platform, text in self._reviewer_findings_reference_texts().items():
            section = "\n".join(
                self._section_lines(text, READ_ONLY_ENFORCEMENT_SECTION)
            )
            for name in REVIEWER_NAMES:
                if name in listed_by_scope:
                    continue
                with self.subTest(platform=platform, name=name):
                    self.assertNotIn(
                        name,
                        section,
                        f"「{READ_ONLY_ENFORCEMENT_SECTION}」 must not name "
                        f"'{name}': the section holds the criterion that splits "
                        "exploration reach, and each agent definition holds "
                        "which side a reviewer falls on.",
                    )

    def test_qa_reference_delegates_read_only_enforcement_instead_of_restating_it(
        self,
    ) -> None:
        """Forbid a restated read-only rule anywhere in the document; require the delegation pointer inside its one section."""
        # The delegation pointer is checked only inside "## 必須完了ゲート",
        # pinning the stronger claim that it lives in that specific section
        # rather than merely somewhere in the document. Why the no-restatement
        # check above is document-wide instead is explained where the markers
        # are defined.
        for platform, text in self._skill_reference_texts(
            QA_AND_INTEGRATION_REFERENCE
        ).items():
            with self.subTest(platform=platform):
                for marker in READ_ONLY_RULE_RESTATEMENT_MARKERS:
                    with self.subTest(platform=platform, marker=marker):
                        self.assertFalse(
                            marker in text,
                            f"{platform}'s {QA_AND_INTEGRATION_REFERENCE} must not "
                            f"contain '{marker}': this document names no read-only "
                            "tool or platform config key anywhere in it; the "
                            "canonical rule lives only in reviewer-findings.md's "
                            "「read-only の担保」 (see this marker's definition "
                            "comment for why).",
                        )

                section = "\n".join(
                    self._section_lines(text, QA_AND_INTEGRATION_MUST_GATES_SECTION)
                )
                normalized_section = "".join(section.split())
                self.assertIn(
                    "".join(READ_ONLY_ENFORCEMENT_DELEGATION.split()),
                    normalized_section,
                )

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


if __name__ == "__main__":
    unittest.main()
