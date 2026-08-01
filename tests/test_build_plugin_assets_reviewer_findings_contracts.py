"""Repository contracts for reviewer findings."""

from __future__ import annotations

from pathlib import Path
import re
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
REVIEWER_DISPATCH_REFERENCE = "reviewer-dispatch.md"
QA_AND_INTEGRATION_MUST_GATES_SECTION = "## 必須完了ゲート"
PARENT_DATA_LOWER_BOUND_DECLARATION = (
    "親が取得して渡す Data は reviewer の判断に必要な情報の下限であり、"
    "この節は reviewer 自身の探索手段を定義しない。"
)
LEGACY_PARENT_DATA_EXPLORATION_BAN = (
    "これらの情報は親が取得して渡すものであり、reviewer 自身に取得させない。"
)
# Keep this finite and semantic: generic words such as 「探索」 or 「取得」 also
# occur in legitimate lower-bound and diff-scope statements.  These combinations
# cover the known regression where the reviewer is made the subject of a direct
# information-acquisition ban, without attempting to enumerate natural-language
# paraphrases indefinitely.
REVIEWER_SIDE_EXPLORATION_BAN_PATTERNS = (
    ("reviewer 自身", "追加情報を取得", "してはならない"),
    ("reviewer 自身", "探索", "を禁止する"),
)
DIFF_SCOPE_DECLARATION = (
    "対象は基準 commit からの diff が導入または悪化させた問題に限定し、"
    "既存問題を広く探索しない。"
)
READ_ONLY_DELEGATION_DECLARATION = (
    "reviewer が read-only であることの担保は "
    "[Reviewer findings の共通契約](reviewer-findings.md) の「read-only の担保」に従う。"
)
# Both counts are derived from REVIEWER_NAMES / FINDINGS_REVIEWER_NAMES so that
# adding an 8th reviewer to those sets fails this test instead of leaving the
# manuscript's literal count silently stale.
POSITIONING_SECTION = "## 位置づけ"
READ_ONLY_ENFORCEMENT_SECTION = "## read-only の担保"
READ_ONLY_ENFORCEMENT_CONTRACTS = (
    # The heading itself is not pinned here: `_section_lines` already raises
    # if the heading is missing, so a separate membership check on it would
    # be redundant once every other contract below is scoped to the section.
    "指摘 Data を返すだけの reviewer には、ファイルを書き換える tool を渡さない。",
    # Pins that `tools`（allowlist）is the actual guarantor and
    # `disallowed_tools` is a restated overlay, not an independent guarantee.
    # An earlier draft named `disallowed_tools` as co-equal with `tools`,
    # which does not hold once a reviewer lacks `tools` altogether.
    "担保の実体は Claude 向け agent frontmatter の `tools`（許可 tool の allowlist）であり、"
    "`Edit` / `Write` / `NotebookEdit` を含めないことでこれらの tool が渡らない。",
    "`disallowed_tools` にも同じ3つを重ねて書くが、これは意図を明示する重ね書きであり、"
    "`tools` を伴わずに単独で担保になるものではない。",
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
    # Pins the tool-unit restriction as a general phrase (not just
    # `disallowed_tools`), since `tools` allowlist exclusion is equally
    # bypassable once `Bash` is granted.
    "`Bash` からファイルを書けるため、tool 単位の制限"
    "（`tools` の allowlist からの除外や `disallowed_tools`）はいずれも迂回でき、"
    "Codex 側の `sandbox_mode` のように機構としては禁じられない。",
    "担保の強さは platform 間で非対称であり、"
    "これは `Bash` を渡す判断に伴う既知の制約として引き受ける。",
    # Pins the working limits that apply once `Bash` is granted. The reach
    # split alone leaves "may run commands" unbounded, and nothing on the
    # Claude side stops a reviewer from rewriting what it is reviewing. The
    # scope is unconditional reach (target worktree, parent's integrated
    # checkout, or anywhere else the reviewer lands) rather than a condition
    # keyed on "target worktree", which a reviewer cannot resolve on its own.
    "`Bash` を渡した reviewer は、対象 worktree に限らず、自身が到達できるいかなる repository"
    "（対象 worktree、親の統合 checkout など）に対しても、読み取りと検証の実行だけを行い、"
    "追跡ファイルを変更しない。",
    # Pins the effect-based write-destination rule (SEC-11): write is limited
    # to a duplicate created outside the target repository, no matter what
    # class of location it is — not just other repositories. Without this,
    # destinations that belong to no repository (`~/.bashrc`, `~/.ssh/config`,
    # a plugin's install path) fall outside the ban and outside what the
    # HEAD/status check can observe.
    "書き込みは、対象とした repository の外の一時領域へ作成した複製に限り、それ以外の"
    "いかなる path へも書き込まない。",
    "書き込みを repository 単位でしか条件付けないと、`~/.bashrc` や"
    "`~/.ssh/config`、plugin の install 先のようにどの repository にも属さない書き込み先が射程外になり、"
    "親が突き合わせる git 状態にも現れないため、run 限りのはずの権限が run を越えて永続化しうる。",
    # Pins the duplicate-destination rule (SEC-12): a freshly created,
    # unique directory, with deletion scoped to that directory only — not a
    # reused fixed-name location.
    "ミューテーション注入や検証用の複製のように書き込みを伴う検証は、`mktemp -d` などで新規作成した"
    "一時 directory 配下へ複製して行う。",
    "固定名の directory を再利用すると、既存内容ごと再利用・削除する"
    "余地が残るためである。",
    "複製は run 中に削除し、削除の対象は自分が作成したその複製 directory に限る。",
    "削除できない場合は path を返却物へ記録する。",
    "worktree を丸ごと複製すると非追跡の `.env` や credential も複製されかねないため、"
    "複製対象に非追跡ファイルを含めない。",
    # Pins the effect-based principle as the primary rule, with the git
    # subcommand list kept only as an example. A closed enumeration alone
    # missed `branch -D`/`-f`/`-m`, `update-ref`, `symbolic-ref`, `reflog
    # expire`, `gc --prune=now`, `config`, hooks, `clean -fdx`, and `restore`.
    "あわせて、HEAD・refs・object DB・git 設定・hooks を変更する操作、"
    "および到達可能性や reflog を失わせる操作を行わない。",
    "例えば `commit` / `checkout` / `switch` / `reset` / `stash` / `rebase` / `merge` / "
    "`cherry-pick` / `worktree add` / `worktree remove` / `branch -d` / `branch -D` / "
    "`branch -f` / `branch -m` / `update-ref` / `symbolic-ref` / `reflog expire` / "
    "`gc --prune=now` / `config` の変更 / `.git/hooks/*` への書き込み / `clean -fdx` / "
    "`restore` / `push` が該当する。",
    # Pins why the git operations are listed apart from file edits: they are
    # the ones that can evade the parent's pre/post check by restoring state,
    # unlike a tracked-file edit which the check observes directly. Named via
    # the check itself (not a specific command) since `rev-parse HEAD` was
    # added to that check after this sentence was first written, and a
    # command-specific claim would go stale again the next time the check's
    # observation points change.
    "追跡ファイルの編集は親の照合で気づけるが、これらは状態を戻せば照合をすり抜けうるためである。",
    # Pins that the limits are a contract rather than an enforced setting, so a
    # later reader does not assume the tool metadata already blocks them and
    # drop the instruction as redundant. The reasoning itself (`disallowed_tools`
    # being tool-scoped, `Bash` command contents being unselectable) lives once,
    # in the write-ban paragraph above; this second mention only points back to
    # it instead of restating the same fact a second time in the same section.
    "この作業範囲も上記と同じ理由で tool metadata では強制できない。",
    # Pins that the guarantor is a delegated check rather than a restated
    # list of observation points (RB-6): reviewer-dispatch.md's own section
    # is the one place that enumerates what gets compared, so this file only
    # points at it instead of keeping a second, driftable copy.
    "担保は各 reviewer 原稿の指示文と、親が起動前後に行う照合になる。",
    "検査の対象と手順は [Reviewer の起動と diff の受け渡し](reviewer-dispatch.md) の"
    "「reviewer 起動前後の worktree・親 checkout 照合」に従う。",
    # Pins the limit of this guarantee (SEC-10): the pre/post check assumes a
    # target worktree exists, so a launch path without one (plan-craft's plan
    # review) is left with manuscript instructions only.
    "この照合は `impl-lead` の委譲経路が対象 worktree を持つことを前提にした手順であり、"
    "`plan-craft` のプラン審査のように対象 worktree を持たない起動経路では、"
    "担保は各 reviewer 原稿の指示文だけになる。",
    # Pins that network egress and credential access sit outside this
    # contract's guarantees: neither the `push` ban nor the HEAD/status check
    # observes them, so a reader must not assume they are mechanically covered.
    "network 送信（`curl` / `gh api` / `ssh` などによる外部送信）と credential の参照"
    "（`~/.git-credentials` や `.env` の読み取りなど）は、この契約の担保対象外である。",
    f"この節の対象は、上記2点の{len(FINDINGS_REVIEWER_NAMES)}本に "
    f"`expert-selection-reviewer` を加えた reviewer {len(REVIEWER_NAMES)}本とする。",
    "指摘された範囲を修正する `review-patch-refactorer` は書き込みを要するため、"
    "この節でも対象外とする。",
)
# Lives in 「位置づけ」, not in 「read-only の担保」: the disclaimer keeps a
# reader from mistaking the read-only section's 7-reviewer scope for
# 「位置づけ」's own 2-point scope. Checked against 「位置づけ」's own section
# text (not the whole document) so that moving the disclaimer into
# 「read-only の担保」 — which would restore the exact misreading this
# disclaimer exists to prevent — fails this test.
READ_ONLY_SCOPE_DISCLAIMER_IN_POSITIONING_SECTION = (
    "ここで定めた対象は上記2点だけに適用する。"
    "「read-only の担保」は対象範囲が異なり、同節が自身の対象を定める。"
)
# The delegation pointer, not a second copy of the rule: branch-review.md
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
                section = "\n".join(
                    self._section_lines(text, READ_ONLY_ENFORCEMENT_SECTION)
                )
                normalized = "".join(section.split())
                for contract in READ_ONLY_ENFORCEMENT_CONTRACTS:
                    self.assertIn("".join(contract.split()), normalized)
                positioning_section = "\n".join(
                    self._section_lines(text, POSITIONING_SECTION)
                )
                self.assertIn(
                    "".join(
                        READ_ONLY_SCOPE_DISCLAIMER_IN_POSITIONING_SECTION.split()
                    ),
                    "".join(positioning_section.split()),
                )

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
            "branch-review.md"
        ).items():
            with self.subTest(platform=platform):
                for marker in READ_ONLY_RULE_RESTATEMENT_MARKERS:
                    with self.subTest(platform=platform, marker=marker):
                        self.assertFalse(
                            marker in text,
                            f"{platform}'s branch-review.md must not "
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

    def test_branch_review_requires_parent_data_as_decision_lower_bound(self) -> None:
        """Require the mandatory gate to leave reviewer-side exploration undefined."""
        for platform, text in self._skill_reference_texts(
            "branch-review.md"
        ).items():
            with self.subTest(platform=platform):
                section = "\n".join(
                    self._section_lines(text, QA_AND_INTEGRATION_MUST_GATES_SECTION)
                )
                normalized = "".join(section.split())
                self.assertIn(
                    "".join(PARENT_DATA_LOWER_BOUND_DECLARATION.split()),
                    normalized,
                )

    def test_branch_review_rejects_reviewer_side_exploration_bans(self) -> None:
        """Keep parent-only and reviewer-side exploration bans out of every distributed gate."""
        for platform, text in self._skill_reference_texts(
            "branch-review.md"
        ).items():
            with self.subTest(platform=platform):
                section_lines = self._section_lines(
                    text, QA_AND_INTEGRATION_MUST_GATES_SECTION
                )
                section = "\n".join(section_lines)
                self.assertNotIn(
                    "".join(LEGACY_PARENT_DATA_EXPLORATION_BAN.split()),
                    "".join(section.split()),
                )
                paragraphs: list[str] = []
                paragraph_lines: list[str] = []
                for line in (*section_lines, ""):
                    if line.strip():
                        paragraph_lines.append(line)
                    elif paragraph_lines:
                        paragraphs.append("".join(paragraph_lines))
                        paragraph_lines = []
                sentences = (
                    sentence
                    for paragraph in paragraphs
                    for sentence in re.split(r"(?<=[。！？!?])", paragraph)
                )
                for sentence in sentences:
                    normalized_sentence = "".join(sentence.split())
                    for subject, target, polarity in (
                        REVIEWER_SIDE_EXPLORATION_BAN_PATTERNS
                    ):
                        self.assertFalse(
                            all(
                                marker in normalized_sentence
                                for marker in (
                                    "".join(subject.split()),
                                    "".join(target.split()),
                                    "".join(polarity.split()),
                                )
                            ),
                            f"{platform}'s mandatory gate must not prohibit "
                            f"reviewer-side exploration with the semantic pattern "
                            f"{subject!r}, {target!r}, {polarity!r}",
                        )

    def test_branch_review_preserves_diff_scope_and_read_only_delegation(self) -> None:
        """Preserve the bounded diff scope and findings-contract delegation in the gate."""
        for platform, text in self._skill_reference_texts(
            "branch-review.md"
        ).items():
            with self.subTest(platform=platform):
                section = "\n".join(
                    self._section_lines(text, QA_AND_INTEGRATION_MUST_GATES_SECTION)
                )
                normalized = "".join(section.split())
                self.assertIn("".join(DIFF_SCOPE_DECLARATION.split()), normalized)
                self.assertIn(
                    "".join(READ_ONLY_DELEGATION_DECLARATION.split()),
                    normalized,
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
                    main.index("(references/branch-review.md)"),
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
