"""Repository contracts for feature-lead."""

from __future__ import annotations

import re
import unittest

from build_plugin_assets_test_support import (
    PLATFORMS,
    RepositoryContractSupport,
    generated_skill_path,
    shared_skill_path,
    shared_skill_reference_path,
)


FEATURE_LEAD_SKILL = "feature-lead"
IMPL_LEAD_SKILL = "impl-lead"
# The three skills that predate feature-lead and now have to decline a batch
# request. Their manuscripts word the non-firing clause identically so a single
# literal can be asserted against every generated file.
PRE_EXISTING_STAGE_SKILLS = ("plan-craft", "branch-design", IMPL_LEAD_SKILL)
# Matches a single-backtick inline code span so it can be stripped before an
# HTML-comment delimiter count. Without this, prose that quotes the marker
# syntax (e.g. "行頭の `<!--` で始まる範囲は...") would be miscounted as an
# actual, unclosed comment opener even though nothing is really commented out.
_INLINE_CODE_SPAN_RE = re.compile(r"`[^`\n]*`")


class FeatureLeadContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _generated_texts(self) -> dict[str, str]:
        return self._generated_texts_for(FEATURE_LEAD_SKILL)

    def _generated_texts_for(self, skill: str) -> dict[str, str]:
        return {
            platform: self._repository_text(generated_skill_path(platform, skill))
            for platform in PLATFORMS
        }

    def _feature_lead_main_texts(self) -> dict[str, str]:
        # Includes the manuscript itself (not just the two generated files) so a
        # contract can Red against the file a human actually edits. Checking only
        # the generated pair would let a change to the generator's rendering (or a
        # stale manuscript the generator happens to already satisfy) pass silently.
        return {
            "source": self._repository_text(shared_skill_path(FEATURE_LEAD_SKILL)),
            **self._generated_texts(),
        }

    @staticmethod
    def _section(text: str, heading: str, *, next_heading: str = "\n## ") -> str:
        """Slice out `heading`'s body, capped at the next heading marker.

        Mirrors the split-then-cap pattern already used elsewhere in this suite
        (e.g. the flow test below, and `## Executor 側の再検証` in
        test_build_plugin_assets_impl_lead_intake_contracts.py): a whole-file
        `assertIn` cannot tell "this sentence lives under the right heading"
        from "this sentence exists somewhere in the file", which is the gap a
        review round on this branch found in practice.
        """
        return text.split(heading, 1)[1].split(next_heading, 1)[0]

    @staticmethod
    def _bullet(section: str, marker: str) -> str:
        """Slice out one bullet's text, keeping `marker` itself in the result.

        `str.split` consumes its delimiter, which would strip the very autonomy
        label ("`attended`" / "`unattended`") a contract needs to assert against
        (e.g. "`unattended` では境界で止まらない。" starts with the marker).
        Index-based slicing keeps it.

        Raises `AssertionError` — not the bare `ValueError` `str.index` would
        raise — when `marker` is absent, so a manuscript edit that drops or
        merges a bullet fails as a readable test failure instead of an opaque
        "substring not found" error with no indication of which assumption
        broke.

        Stops at the next bullet marker ("\\n- ") if one exists after `marker`
        in `section`, or at the end of `section` otherwise (PQ-3). Markdown
        has no closing marker for "end of bullet list" the way it does for a
        bullet boundary, so callers must obtain `section` from `_section`,
        which caps at the next heading — the slice is still bounded, just not
        to a marker inside the bullet list itself. Stopping at *any*
        following bullet, rather than requiring one specific literal to
        follow, means two bullets swapping places is not itself a failure
        this helper reports: this file's contracts do not require a
        particular order between, say, the `attended` and `unattended`
        bullets, so a swap between them is not a regression to catch here
        (each bullet's own content is still checked by whichever `assertIn`
        scopes to it).
        """
        if marker not in section:
            raise AssertionError(f"bullet marker {marker!r} not found in section")
        start = section.index(marker)
        rest = section[start:]
        boundary = re.search(r"\n- ", rest)
        return rest[: boundary.start()] if boundary else rest

    @staticmethod
    def _locate_numbered_step(flow: str, number: int) -> tuple[list[str], int, int]:
        """Find step `number`'s physical-line range within `flow`.

        Shared by `_numbered_step` (needs the body text) and
        `_numbered_step_offset` (needs the physical position) so both stay
        anchored to the exact same line-start match — see `_numbered_step`'s
        docstring for why the match has to be anchored to the start of a
        physical line at all.
        """
        lines = flow.split("\n")
        start_pattern = re.compile(rf"^\s*{number}\.\s*")
        next_pattern = re.compile(r"^\s*\d+\.\s*")
        start_index = next(
            (i for i, line in enumerate(lines) if start_pattern.match(line)), None
        )
        if start_index is None:
            raise AssertionError(f"no line starts with step {number}. in the flow")
        end_index = next(
            (
                i
                for i in range(start_index + 1, len(lines))
                if next_pattern.match(lines[i])
            ),
            len(lines),
        )
        return lines, start_index, end_index

    @classmethod
    def _numbered_step(cls, flow: str, number: int) -> str:
        """Return numbered step `number`'s full text, wrapped lines rejoined.

        Anchors the ordinal to the start of a physical line — a bare "N. "
        substring search would also match inside a prose sentence that merely
        mentions the number, or would keep matching a renumbered step whose
        new number still contains the digit as a substring (e.g. a step
        renumbered to "16." still contains "6"). TQ-17 found both misses in
        practice with the previous non-anchored implementation.

        The regex's `\\s*` after the period accepts the fullwidth space
        (U+3000, which `str.isspace()` already treats as whitespace) and a
        missing space alike, so those manuscript-formatting variants keep
        matching. Continuation lines of a wrapped step (indented text that
        does not itself start with "digit.") are folded into the same step,
        so re-wrapping a step across more or fewer physical lines does not
        change what this returns.
        """
        lines, start_index, end_index = cls._locate_numbered_step(flow, number)
        return "\n".join(lines[start_index:end_index])

    @classmethod
    def _numbered_step_offset(cls, flow: str, number: int) -> int:
        """Return the character offset of step `number`'s own line in `flow`.

        TQ-21: `flow.index(cls._numbered_step(flow, number))` looks wrong but
        isn't safe — it re-searches `flow` for the step's body text as a bare
        substring, and returns the *first* occurrence. A decoy earlier in the
        flow that quotes the same ordinal-prefixed sentence (e.g. inside a
        prose aside) makes that search return the decoy's offset instead of
        the real, line-anchored step's, defeating a position check even
        though `_numbered_step` itself correctly found the real step. Summing
        the lengths of the physical lines before the one `_locate_numbered_step`
        actually matched points at that specific occurrence instead of
        whichever text happens to match first.
        """
        lines, start_index, _ = cls._locate_numbered_step(flow, number)
        return sum(len(line) + 1 for line in lines[:start_index])

    def _assert_heading_present_and_live(self, text: str, heading: str) -> None:
        """Fail if `heading` is missing, or sits inside an unclosed HTML comment.

        The generator only strips its own `claude-only` / `codex-only` markers
        (scripts/build_plugin_assets.py); an unrelated `<!-- ... -->` wrapper
        passes through to the generated file with its text intact, so a plain
        `assertIn` cannot distinguish a live heading from one commented out of
        the rendered skill. Counting delimiters up to the heading's position
        catches that case: an unclosed opener before it means the heading is
        being suppressed, not just indented oddly. Same-line, self-contained
        markers (this repository's own "<!-- claude-only:start -->" style
        platform markers — still present verbatim in the "source" manuscript,
        which the generator strips only from the generated output) add one to
        each count and net out, so they do not need special-casing.

        Inline code spans are stripped before counting: a sentence that quotes
        the marker syntax (e.g. "行頭の `<!--` で始まる範囲は...") contains the
        literal substring "<!--" without opening a real comment, and would
        otherwise be miscounted as an unclosed opener.
        """
        self.assertIn(heading, text)
        prefix = _INLINE_CODE_SPAN_RE.sub("", text[: text.index(heading)])
        self.assertLessEqual(
            prefix.count("<!--"),
            prefix.count("-->"),
            f"{heading!r} sits inside an unclosed HTML comment",
        )

    def _generated_frontmatter_and_body(self, text: str) -> tuple[str, str]:
        # The generated Markdown always opens with a YAML frontmatter block, so the
        # third chunk of the "---\n" split is the body. Splitting instead of matching
        # against the whole file keeps a description-only edit from satisfying a body
        # contract, which is what AC-20 asks the platform blocks to be checked for.
        _, frontmatter, body = text.split("---\n", 2)
        return frontmatter, body

    def _assert_contracts(self, contracts: tuple[str, ...]) -> None:
        for platform, text in self._generated_texts().items():
            normalized = "".join(text.split())
            for contract in contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)

    def test_feature_lead_keeps_attended_as_the_autonomy_default(self) -> None:
        """Choose unattended only when the user asks for it."""
        self._assert_contracts(
            (
                "`autonomy` の明示指定。既定は `attended` とし、ユーザーが全面委任を明示した"
                "場合だけ `unattended` を選ぶ。",
                "タスク規模、段の停止回数、進行の停滞を理由にこの Skill 側で `unattended` へ"
                "切り替えない。",
            )
        )

    def test_feature_lead_ledger_names_its_fields_and_resolution_vocabulary(
        self,
    ) -> None:
        """Record every decision point with its origin, basis kind, and resolver."""
        self._assert_contracts(
            (
                "| `stage` | `plan-craft` / `branch-design` / `impl-lead` |",
                "| `point` | 判断点。原文を言い換えずに保持する |",
                "| `origin` | `open_questions` / `unresolved_decisions` / "
                "`validation.blocking` / `round-limit` / `impl-lead-gate` |",
                "| `resolution` | 確定した内容、または未確定として記録した事実 |",
                "| `basis` | 根拠 |",
                "| `basis_kind` | `observed` / `assumed` |",
                "| `resolved_by` | `user`（`attended` での確定） / "
                "`autonomous`（`unattended` での自律解決） / "
                "`deferred`（解決も確定もされないままユーザーへ返した） |",
                "`resolved_by: deferred` は、解決も確定もされないままユーザーへ返した"
                "すべての判断点に用いる。",
                "不可逆操作を要した判断点、non-resolvable な判断点、同一段の停止に巻き込まれて"
                "未着手のまま返した resolvable な判断点がこれに当たる。",
                "`deferred` は解決を試みていた既存の判断点へ付与し、新しい台帳行を起こさない。",
            )
        )

    def test_feature_lead_defers_decisions_that_need_irreversible_operations(
        self,
    ) -> None:
        """Stop short of irreversible operations and hand the decision back unresolved."""
        self._assert_contracts(
            (
                "不可逆な操作（外部への公開・送信、tracked file の削除、履歴の書き換え、"
                "外部状態の変更）は `unattended` でも自律解決の手段に含めない。",
                "当該操作を伴わずに到達できる範囲まで進め、当該操作を要した既存の判断点へ "
                "`resolved_by: deferred` を付与し、操作が必要だった事実をその判断点の "
                "`resolution` と `basis` へ記録して、未実施のままユーザーへ返す。",
            )
        )

    def test_feature_lead_reports_the_whole_ledger_in_both_autonomy_modes(
        self,
    ) -> None:
        """Require the ledger in the final report whether or not autonomy is unattended."""
        self._assert_contracts(
            (
                "判断点は検出時に台帳へ記録し、会話上の最終報告へ全件を記載する。",
                "判断点台帳の全件を会話上の最終報告にも含める。",
                "台帳の記載は `attended` / `unattended` の双方で必須とする。",
                "`basis_kind: assumed` の項目は台帳内で区別して示し、観測事実に基づく解決と"
                "混ぜない。",
                "仮定の総数を最終報告の冒頭要約にも出す。",
            )
        )

        unattended_only_wording = "".join(
            "`unattended` では判断点台帳の全件を会話上の最終報告にも含める。".split()
        )
        for platform, text in self._generated_texts().items():
            with self.subTest(platform=platform):
                self.assertNotIn(unattended_only_wording, "".join(text.split()))

    def test_feature_lead_classifies_decision_origins_and_bounds_stage_reruns(
        self,
    ) -> None:
        """Route each origin to a rerun or a stop and spend at most one rerun per stage."""
        self._assert_contracts(
            (
                "判断点は `origin` によって resolvable と non-resolvable に分類する。",
                "resolvable は `origin: open_questions` / `origin: unresolved_decisions` / "
                "`origin: validation.blocking` と、ユーザーが `rounds_limit` の値を指定して"
                "いない場合の `origin: round-limit` である。",
                "再実行の入力には、`open_questions` と `unresolved_decisions` では確定した"
                "解決内容を、`validation.blocking` では violation の `code` / `path` / "
                "`message` そのものを載せ、`round-limit` では「`round-limit` の扱い」に従って"
                "引き上げた `rounds_limit` を載せる。",
                "non-resolvable は `origin: impl-lead-gate` と、ユーザーが `rounds_limit` の"
                "値を指定した場合の `origin: round-limit` である。",
                "`origin: impl-lead-gate` は一律 non-resolvable とする。",
                "`mode-proposal-invalid` は「`delegation.requested_mode` の設定」の写像規約に"
                "より `delegation` の設定時点で回避されるため、判断点として発生しない。",
                "分類が一意に決まらない判断点は non-resolvable として扱い停止する。",
                "再実行の計数は段側で数え、各段の再実行は一括実行を通じて1回までとする。",
                "この枠は `unattended` の自律解決による再実行にだけ掛け、`attended` で"
                "ユーザーが判断点を確定した後の再実行は計数しない。",
                "同一段が resolvable と non-resolvable を同時に返した場合は、non-resolvable が"
                "1件でもあれば再実行せず停止する。",
                "同一段が `origin: round-limit` と `origin: validation.blocking` を同時に"
                "返した場合、ユーザーが `rounds_limit` の値を指定していなければ `round-limit` を"
                "優先し、「`round-limit` の扱い」の引き上げ再実行を1回として行う。",
                "値を指定している場合は `round-limit` が non-resolvable であるため優先規則を"
                "適用せず停止する。",
                "再実行後も残る判断点と non-resolvable な判断点は、`unattended` でも停止して"
                "ユーザーへ返す。",
            )
        )

    def test_feature_lead_sets_requested_mode_without_writing_a_proposal(self) -> None:
        """Pick the table's proposal at delegation time instead of emitting a proposal."""
        self._assert_contracts(
            (
                "ユーザーが明示した mode の写像は、`impl-lead` SKILL.md の入力語彙の写像表を"
                "正本として参照する。",
                "mode が未指定の場合は `requested_mode` を `null` のまま保持する。",
                "この Skill は `delegation_mode_proposal` を書かない。",
                "`delegation` を設定するその時点で、表が提案する `{policy, baseline}` を "
                "`requested_mode` へ設定する。",
                "この設定は `delegation.authorized` の `false` から `true` への遷移1回の中で"
                "完結し、状態遷移表の親の権限行に収まる。",
                "判断点を発生させないため台帳へ新しい行を起こさない。",
                "引き上げ先は表が決めるため、この原稿へ表を複製せず正本を参照する。",
                "proposal の判定には枝の `failure_impact.level` を使い、"
                "`implementation_complexity` は使わない。",
                "引き上げた事実と引き上げ前後の `{policy, baseline}` は最終報告へ記録する。",
                "この引き上げの根拠は `impl-lead` SKILL.md の引き下げ禁止の例外条項に置く。",
                "この引き上げは `autonomy` に依らず `attended` と `unattended` の双方で"
                "適用する。",
            )
        )

    def test_feature_lead_scopes_qa_report_justifies_assumed_and_ranks_the_reading(
        self,
    ) -> None:
        """Scope out QA report fields, justify assumed basis, and rank the batch reading."""
        self._assert_contracts(
            (
                "永続 QA レポートの記録項目の規定は本 skill の範囲外であり、正本は "
                "`impl-lead` 側に置く。",
                "後者は起動前の入力に掛かる規定（「入力の確認」）であり、前者は段が判断点として"
                "返した後の記録区分（「自律解決の規律」）である。",
                "両者を同じ「仮定の禁止」で扱うと、根拠を取れない判断点が必ず停止になり "
                "`unattended` が成立しない。",
                "一括実行の明示要求そのものが `confirmation_mode: auto` の明示指定と委譲要求を"
                "兼ねる。",
                "ユーザーが `confirmation_mode` または委譲の要否を明示した場合はその明示を"
                "優先し、この読み替えは明示がない場合にだけ適用する。",
            )
        )

    def test_feature_lead_forces_attended_when_strict_full_is_requested(self) -> None:
        """Drop unattended before plan-craft runs when strict-full is requested."""
        self._assert_contracts(
            (
                "`strict-full`（`policy: fixed` かつ `baseline: strict`）が指定された場合は、"
                "`autonomy` の `unattended` を `attended` へ強制的に落とす。",
                "判定と確定は「入力の確認」の時点で行い、`plan-craft` を起動する前に "
                "`autonomy` を確定して以降の全段へ適用する。",
                "`impl-lead` 段へ入ってから落とす実装を許さず、計画段の判断点も自律解決しない。",
                "`strict-full` は枝数を提示したユーザー確認を委譲開始の条件とする語彙であり、"
                "判断点の自律解決と論理的に両立しない。",
                "落とした事実と理由を最終報告へ記録し、ユーザーが明示した `unattended` を"
                "黙って無効化しない。",
            )
        )

    def test_feature_lead_raises_rounds_limit_only_without_a_user_specified_value(
        self,
    ) -> None:
        """Treat a specified limit value as binding and a launch request as weaker."""
        self._assert_contracts(
            (
                "値の指定がない場合に限り、`rounds_limit` を既定値と同じ幅（10）だけ引き上げて"
                "段を再実行する。",
                "値の指定がある場合は引き上げず停止する。",
                "引き上げは「再実行の枠」に含めて段ごとに1回までとし、再実行後も "
                "`round-limit` に達する場合は停止する。",
                "`plan-craft` の `rounds_limit` の引き上げをユーザーの明示に限る契約は変更せず、"
                "値の指定がない場合に限りこの Skill の起動要求が引き上げの明示を兼ねるという"
                "読み替えで授権する。",
                "値の指定と起動要求による授権を同じ「明示」として扱わない。",
                "引き上げた事実と引き上げ後の値を判断点台帳と最終報告へ記録する。",
            )
        )

    def test_feature_lead_starts_from_the_stage_its_input_determines(self) -> None:
        """Start from branch-design only for an approved plan and never skip a later stage."""
        frontmatter_contract = (
            "確定済みのプラン文書とレビュー状態を渡して実装までの一括実行を要求されたときも"
            "発火し、`branch-design` から開始する。"
        )
        # 開始段は2 artifact が揃っていることで決まる。`plan_document` の path 条件を
        # 落とすと、会話内経路で提示したペアを保存して後日貼り付ける入力が判定を通り、
        # 「会話内経路は後日渡す経路を持たない」規定と二重に適合する。
        body_contracts = (
            "ユーザーが確定済みのプラン文書とレビュー状態を渡して実装までの一括実行を要求した"
            "とき。この場合は `branch-design` から開始する。",
            "レビュー状態が `status: approved` であり、その `plan_document` が repository "
            "相対 path であり、その path のプラン文書が読める場合だけ `branch-design` から"
            "開始する。",
            "それ以外の入力（自然文の要求、`status` を持たないレビュー状態、プラン文書だけを"
            "渡された入力、issue 本文や会話内のプラン）はすべて `plan-craft` から開始する。",
            "プラン文書だけを渡された場合はレビュー状態が無いものとして扱い、その path から"
            "兄弟のレビュー状態を解決しない。",
            # 命名規約が `<slug>.md` と `<slug>-review.yaml` を対にしているため、規約を
            # 知る読者ほど「同じ slug を機械的に探せばよい」という単純化に届く。それが
            # 誤りである理由を原稿へ残させる。
            "レビュー状態は承認の記録であり、推測で解決すると、そのプラン文書に対応しない"
            "レビュー状態を承認済みとして扱う経路が開くためである。",
            "`plan_document: 会話内` のレビュー状態は、プラン文書を会話上に貼り直されても"
            "開始段判定を通さず、`plan-craft` から開始する。",
            "`status` が `awaiting_review` または `blocked` のレビュー状態を"
            "渡されたとき。承認または判断点の確定を求めて差し戻す。これを判断点として台帳へ"
            "記録しない。",
            "判断点は段が返したものだけを対象とし、起動前に渡された入力を「判断点の分類」にも"
            "再実行にも掛けない。",
            "確定済みの Branch Plan Set を渡されたとき。この Skill の対象外であり、`impl-lead` を"
            "直接使う経路を案内する。",
            "`branch-design` から開始する場合はこの段を実行せず、渡された確定済みの"
            "プラン文書とレビュー状態をそのまま次段の入力にする。",
            "不足が blocking なら補完せず、開始段に応じた受け手へ渡す。`plan-craft` から開始"
            "する場合は `plan-craft` の `open_questions` として扱わせ、`branch-design` から"
            "開始する場合は `branch-design` の `unresolved_decisions` として扱わせる。",
            "次は `plan-craft` から開始する場合の確認項目である。`branch-design` から開始する"
            "場合は、確定済みのプラン文書とレビュー状態がこの位置を占め、受け手のない確認項目を"
            "残さない。",
            "根拠源と scope の基準は開始段に応じて一意に定める。`plan-craft` から開始する場合は"
            "要求原文をこれに充て、`branch-design` から開始する場合は確定済みプラン文書の"
            "見出し行と「scope」節と「Acceptance Criteria」節が要求原文の位置を占める。",
            "開始段より前の段は実行せず、開始段以降の段は飛ばさない。",
            "`branch-design` を省いてプラン文書とレビュー状態を直接 `impl-lead` へ渡さない。",
        )

        for platform, text in self._generated_texts().items():
            frontmatter, body = self._generated_frontmatter_and_body(text)
            normalized_frontmatter = "".join(frontmatter.split())
            normalized_body = "".join(body.split())
            with self.subTest(platform=platform, part="frontmatter"):
                self.assertIn(
                    "".join(frontmatter_contract.split()), normalized_frontmatter
                )
            for contract in body_contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized_body)

    def test_existing_skills_defer_batch_requests_to_feature_lead(self) -> None:
        """Decline a direct batch request while still running as a feature-lead stage."""
        # Asserted against the frontmatter and the body separately because the
        # description lives in per-platform marker blocks while the body is shared.
        # A whole-file match would let a body-only edit satisfy both platforms with
        # an untouched description, which is exactly the miss AC-16 asks about.
        contracts = (
            "ユーザーからプランから実装までの一括実行を直接要求された場合、および確定済みの"
            "プラン文書とレビュー状態を渡して実装までの一括実行を直接要求された場合は、"
            "`feature-lead` の責務であり発火しない。",
            "`feature-lead` の段として起動された場合はこの条件の対象外であり、"
            "通常どおり動作する。",
        )

        for skill in PRE_EXISTING_STAGE_SKILLS:
            for platform, text in self._generated_texts_for(skill).items():
                frontmatter, body = self._generated_frontmatter_and_body(text)
                for part, section in (
                    ("frontmatter", frontmatter),
                    ("body", body),
                ):
                    normalized = "".join(section.split())
                    for contract in contracts:
                        with self.subTest(
                            skill=skill,
                            platform=platform,
                            part=part,
                            contract=contract,
                        ):
                            self.assertIn("".join(contract.split()), normalized)

    def test_impl_lead_keeps_the_downgrade_ban_wording_intact(self) -> None:
        """Keep the allocation-policy downgrade ban worded as it already is."""
        contracts = (
            "引き下げ禁止の対象は配分方針 `{policy, baseline}` とする。",
            "ユーザーが明示した `baseline` を親都合で引き下げない。",
            "`policy` を親都合で `fixed` から `adaptive` へ変えない。",
        )

        for platform, text in self._generated_texts_for(IMPL_LEAD_SKILL).items():
            normalized = "".join(text.split())
            for contract in contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)

    def test_impl_lead_exempts_the_feature_lead_upgrade_from_the_downgrade_ban(
        self,
    ) -> None:
        """Let the batch route pick the table's proposal without calling it a downgrade."""
        contracts = (
            "`feature-lead` の経路で、写像した `requested_mode` が `branch-design` の "
            "branch-plan-schema.md の出力条件表が proposal を要求する組み合わせになる場合に、"
            "表が提案する `{policy, baseline}` を設定することは、この親都合の変更に含めない。",
            "ユーザーが mode を明示して一括実行を要求したことが、この引き上げの授権を兼ねる。",
            "引き上げ先は出力条件表に委ね、この原稿で別の値を選ばない。",
            "引き上げ前後の `{policy, baseline}` を記録し、引き上げが生むリスクを"
            "ユーザーへ報告する。",
            "proposal の安全性判断は `failure_impact.level` を入力にする。",
        )
        # The exception applies in both autonomy settings, so the manuscript must not
        # narrow it. A blanket ban on the word `autonomy` would also fail on unrelated
        # future mentions, so only the narrowing sentence itself is excluded.
        autonomy_narrowing = "この例外は `unattended` の場合にだけ適用する。"

        for platform, text in self._generated_texts_for(IMPL_LEAD_SKILL).items():
            normalized = "".join(text.split())
            for contract in contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)
            with self.subTest(platform=platform, contract=autonomy_narrowing):
                self.assertNotIn("".join(autonomy_narrowing.split()), normalized)

    def test_feature_lead_stops_the_whole_stage_when_any_branch_plan_is_blocked(
        self,
    ) -> None:
        """Treat a Set with any blocked Branch Plan as one stage-wide decision point."""
        # AC-8(a). The decision-point bullet lives in the "## 段の遷移と判断点の
        # 処理" preamble bullet list; the authorization gate it implies lives in
        # "## 授権の根拠". They are checked as two separate claims because
        # detecting the stage-wide stop does not by itself say authorization is
        # withheld unless every Branch Plan is approved.
        #
        # TQ-11: the gate contracts were still whole-file-scoped after a prior
        # round moved their neighboring sentences (attended/unattended
        # granularity) into the "## 授権の根拠" scope — moving this paragraph
        # out of that section passed silently until scoped here too.
        decision_point_contracts = (
            "`branch-design` が返した Branch Plan Set のうち1件でも Branch Plan が "
            "`blocked` である",
            "（`blocked` の定義は `branch-plan-schema.md` に従う）",
            "この場合は特定の Branch Plan ではなく段全体を判断点として扱う。",
        )
        authorization_gate_contracts = (
            "授権を設定するのは、Set の全 Branch Plan が `status: approved` を返した"
            "場合だけである。",
            "1件でも `blocked` な Branch Plan があれば段全体を判断点として扱い停止し、"
            "一部の Branch Plan だけを授権して進める経路は持たない。",
        )
        # RB-4: `blocked` の成立条件は branch-plan-schema.md の定義そのもの
        # であり、`feature-lead` が逐語コピーすると二重管理になる。旧文言が
        # 戻っていないことを確認する。
        #
        # Why Not: この forbidden だけ whole-file スコープのままにする理由。
        # `assertIn` の節スコープ化は「正しい場所に**ある**こと」を追加で
        # 要求するため検出力が上がるが、`assertNotIn` の節スコープ化は探す
        # 範囲が減るだけで検出力が下がる。RB-4 が禁じる逐語定義は
        # `feature-lead` SKILL.md のどこに出現しても二重管理になるため、
        # 正しいスコープは file 全体である（PQ-1）。ただし禁止命題が
        # 文脈依存である場合（ある bullet では真になる場合）はこの規則の
        # 対象外とし、当該スコープへ閉じる（TQ-13/TQ-16 の
        # `test_feature_lead_records_the_boundary_passage_when_unattended`
        # を参照）。
        forbidden = (
            "その Branch Plan の `unresolved_decisions` または `validation.blocking` "
            "が非空、あるいは Set の `validation.blocking` が非空"
        )
        for platform, text in self._feature_lead_main_texts().items():
            decision_section = "".join(
                self._section(
                    text, "## 段の遷移と判断点の処理", next_heading="\n### "
                ).split()
            )
            gate_section = "".join(
                self._section(text, "## 授権の根拠").split()
            )
            normalized = "".join(text.split())
            for contract in decision_point_contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), decision_section)
            for contract in authorization_gate_contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), gate_section)
            with self.subTest(platform=platform, forbidden=forbidden):
                self.assertNotIn("".join(forbidden.split()), normalized)

    def test_feature_lead_authorizes_only_the_lead_branch_plan_under_attended(
        self,
    ) -> None:
        """Authorize just the order-first Branch Plan when autonomy stays attended."""
        # AC-8(b), first half; RB-1; TQ-2. Scoped to "## 授権の根拠": RB-5 makes
        # that section the sole home for authorization granularity, so a copy
        # drifting or vanishing elsewhere in the file can no longer mask a
        # regression here (previously a whole-file `assertIn` let a mutation
        # that deleted these lines from this exact section still pass, because
        # an identical sentence duplicated the claim in another section).
        contracts = (
            "授権する Branch Plan の範囲の正本は `branch-plan-intake.md`"
            "「Branch Plan 境界の授権」である。",
            "`attended`（既定）では、`order` の先頭の未実行 Branch Plan だけを授権する。",
        )
        for platform, text in self._feature_lead_main_texts().items():
            section = self._section(text, "## 授権の根拠")
            normalized = "".join(section.split())
            for contract in contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)

    def test_feature_lead_authorizes_every_branch_plan_under_unattended(self) -> None:
        """Authorize the whole Set under the intake's bulk-authorization exception."""
        # AC-8(c), first half; RB-1; TQ-2. Same section scope as the attended
        # test above, and the same reasoning: the attended/unattended
        # distinction must not collapse into one shared, half-satisfied
        # sentence, and `branch-plan-intake.md`'s grant of "only an explicit
        # blanket authorization gets every Branch Plan" must be the thing this
        # Skill maps `autonomy: unattended` onto, not an unattributed rule.
        contracts = (
            "`unattended` では、Set の全 Branch Plan を授権する。",
            "`autonomy: unattended` の明示を、正本が例外とする「ユーザーが全 "
            "Branch Plan の一括授権を明示した場合」として読み替える。",
        )
        for platform, text in self._feature_lead_main_texts().items():
            section = self._section(text, "## 授権の根拠")
            normalized = "".join(section.split())
            for contract in contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)

    def test_feature_lead_boundary_stop_section_heading_is_live(self) -> None:
        """Keep the boundary-stop heading real: not renamed, not commented out."""
        # TQ-1. Step 8 of "全体の流れ" points at this heading by name; a rename
        # leaves that reference dangling, and a generic HTML-comment wrapper
        # (the generator strips only its own claude-only/codex-only markers,
        # per scripts/build_plugin_assets.py) would otherwise leave every
        # whole-file `assertIn` in this file satisfied by inert text.
        for platform, text in self._feature_lead_main_texts().items():
            with self.subTest(platform=platform):
                self._assert_heading_present_and_live(
                    text, "### Branch Plan 境界の停止"
                )

    def test_feature_lead_boundary_stop_section_relays_without_duplicating(
        self,
    ) -> None:
        """Describe the boundary relay once, in its own section, without re-deriving it."""
        # AC-8(b) second half; AC-8(d) mechanism; RB-3; RB-5; TQ-1. Scoped to
        # "### Branch Plan 境界の停止" (same split-and-cap pattern as the flow
        # test) so this section's own regressions cannot hide behind a copy
        # living in "授権の根拠" or "判断点台帳".
        contracts = (
            "`impl-lead` が未授権の Branch Plan の境界で止まることは、上の判断点の"
            "いずれにも当たらない。",
            "境界の停止を判断点として扱わない理由は「判断点台帳」に従う。",
            "授権する Branch Plan の範囲は「授権の根拠」に従う。",
            # RB-3: 「既存の最終報告の中継規約」という未定義語をやめ、提示が
            # 手順9の最終報告とは別の中間提示であることを直接書く。
            "`impl-lead` が境界で止まったら、`impl-lead` が提示した内容をそのまま"
            "ユーザーへ返し、次の Branch Plan の授権を求める。",
            "この提示は手順9の最終報告とは別の、会話上の中間提示である。",
            "提示内容そのものは `branch-plan-intake.md` を正本とし、この Skill へ"
            "複製しない。",
            "この停止は Skill の責務を果たさずに終了することではなく、Branch Plan を"
            "承認単位にした結果として意図された停止である。",
        )
        # RB-5: 授権粒度の逐語文と、台帳非記録の理由の逐語文は、それぞれ
        # 「授権の根拠」「判断点台帳」を正本にする。この節へ戻っていないことを
        # 確認する（file 自身の Why Not「判断表を複製すると正本が二重化する」を
        # この節自身の記述にも適用する）。
        #
        # Why Not: この2件も PQ-1 の whole-file 既定（`test_feature_lead_stops_
        # the_whole_stage_when_any_branch_plan_is_blocked` を参照）の例外側に
        # 当たる（TQ-16）。いずれも文脈依存の禁止であり、正本節（「授権の根拠」
        # 「判断点台帳」）では上の positive `assertIn`（:628、および
        # `test_feature_lead_authorizes_only_the_lead_branch_plan_under_attended`
        # / `test_feature_lead_keeps_the_boundary_stop_out_of_the_decision_ledger`）
        # がこの2文の存在を要求しており、whole-file 化すると正しい原稿を落とす。
        forbidden = (
            "`attended`（既定）では、`order` の先頭の未実行 Branch Plan だけを"
            "授権する。",
            "台帳が対象とするのは段が返した判断点であり、境界の停止は授権が"
            "未設定であることの帰結だからである。",
        )
        for platform, text in self._feature_lead_main_texts().items():
            section = self._section(
                text, "### Branch Plan 境界の停止", next_heading="\n## "
            )
            normalized = "".join(section.split())
            for contract in contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)
            for phrase in forbidden:
                with self.subTest(platform=platform, forbidden=phrase):
                    self.assertNotIn("".join(phrase.split()), normalized)

    def test_feature_lead_boundary_resume_sets_delegation_before_returning(
        self,
    ) -> None:
        """Route the attended resume back through delegation, not straight to impl-lead."""
        # RB-2; TQ-3. Isolates the `attended` bullet specifically, not just the
        # section: "その Branch Plan" is anaphoric, so a mutation that moves
        # this sentence into the `unattended` bullet (a boundary unattended
        # never reaches) would still satisfy a section-only scope. The prior
        # wording ("...手順7へ戻る") skipped 手順6, which is the only step that
        # sets `delegation` — resuming without it would hand impl-lead the same
        # unauthorized Branch Plan and loop at the same boundary forever.
        #
        # PQ-3: `_bullet`'s docstring already documents why it does not
        # require a specific literal to follow `attended` — this file's
        # contracts do not require `attended` to precede `unattended`, so
        # a swap between them must not fail this scope.
        resume_contract = (
            "ユーザーが授権を確定したら、「全体の流れ」の手順6からその Branch Plan"
            "について行い直し、`impl-lead` を再開する。"
        )
        # TQ-14; TQ-15: the positive assertIn above only requires the correct
        # sentence to exist somewhere in the bullet; it does not rule out a
        # contradicting sentence appended alongside it. Unlike TQ-13's
        # forbidden text below, "手順6を省いて手順7へ直接戻ってもよい。" is not
        # context-dependent — it is false everywhere in this Skill, not just
        # outside the `attended` bullet — so PQ-1's whole-file rule applies
        # without exception: scoping this check to the bullet would miss the
        # same sentence appended to the `unattended` bullet, the section
        # preamble, or 全体の流れ's own 手順8 (all demonstrated by review).
        # This is the same whole-file scope this file already uses at
        # `test_feature_lead_reports_the_whole_ledger_in_both_autonomy_modes`'s
        # `unattended_only_wording` and
        # `test_impl_lead_exempts_the_feature_lead_upgrade_from_the_downgrade_ban`'s
        # `autonomy_narrowing`.
        forbidden_shortcut = "手順6を省いて手順7へ直接戻ってもよい。"
        for platform, text in self._feature_lead_main_texts().items():
            section = self._section(
                text, "### Branch Plan 境界の停止", next_heading="\n## "
            )
            attended_bullet = self._bullet(section, "- `attended`")
            normalized_bullet = "".join(attended_bullet.split())
            with self.subTest(platform=platform):
                self.assertIn("".join(resume_contract.split()), normalized_bullet)
            with self.subTest(platform=platform, forbidden=forbidden_shortcut):
                self.assertNotIn(
                    "".join(forbidden_shortcut.split()), "".join(text.split())
                )

    def test_feature_lead_records_the_boundary_passage_when_unattended(self) -> None:
        """Log that an unattended run never stops at the boundary, only records it."""
        # AC-8(c), second half; TQ-1; TQ-3. Scoped from the `unattended` marker
        # to the end of the already-bounded "### Branch Plan 境界の停止"
        # section — not to "just this bullet's own text". `_bullet` has no
        # closing marker to slice to for the last bullet in a section (see its
        # docstring), so anything placed after this bullet's real sentences
        # and before the section boundary would also satisfy a plain
        # `assertIn` here.
        contracts = (
            "`unattended` では境界で止まらない。",
            "境界を通過した事実と通過した Branch Plan id を最終報告へ記録する。",
        )
        # TQ-13: the scope above cannot rule out a bullet whose own words say
        # the opposite of AC-8(c) — "この bullet must contain the right
        # sentence" is not the same claim as "this bullet must not also
        # contain the wrong one". Forbid the negation directly.
        #
        # Why Not: この forbidden を `unattended` bullet 単体（`_bullet` の
        # スライス）ではなく「節から `attended` bullet を除いた範囲」へ閉じる
        # 理由（TQ-16; TQ-22）。PQ-1 の whole-file 規則をそのまま適用できない
        # のは、「境界で必ず停止し、ユーザーの授権を待つ。」が `attended` では
        # 真の命題だからである（TQ-16）。ただし `unattended` bullet 単体へ
        # 閉じると、`_bullet` が持つ「次の bullet marker か section 末尾で
        # 止まる」という固定境界（PQ-3 で確定）だけでは、`unattended` bullet
        # の**後ろ**へ新設した兄弟 bullet（あるいは間に挟んだ兄弟 bullet）へ
        # この否定文を置く変異を検出できない（TQ-22）。`attended` 側だけを
        # 除いた範囲は `_bullet` が返す `attended_bullet` の実際の広がりに
        # 依存するため、その依存が壊れて `outside_attended` が無言で縮んだ
        # 場合は、下の guard（TQ-23）がそれを loud な失敗にする。
        forbidden = "境界で必ず停止し、ユーザーの授権を待つ。"
        for platform, text in self._feature_lead_main_texts().items():
            section = self._section(
                text, "### Branch Plan 境界の停止", next_heading="\n## "
            )
            unattended_bullet = self._bullet(section, "- `unattended`")
            normalized = "".join(unattended_bullet.split())
            for contract in contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)
            attended_bullet = self._bullet(section, "- `attended`")
            outside_attended = section.replace(attended_bullet, "", 1)
            # Guard the guard (TQ-23): `outside_attended` depends entirely
            # on `_bullet`'s "next bullet marker or section end" boundary
            # via `attended_bullet` — if that boundary ever grows to
            # swallow the `unattended` bullet
            # too, it fails silently, not with an error: `outside_attended`
            # would just shrink until the `assertNotIn` below passes for the
            # wrong reason (nothing left to search, not "the forbidden text
            # is absent"). Asserting the `unattended` bullet's own text is
            # still present in `outside_attended` makes that collapse loud.
            with self.subTest(platform=platform, guard="outside_attended"):
                self.assertIn(unattended_bullet, outside_attended)
            with self.subTest(platform=platform, forbidden=forbidden):
                self.assertNotIn(
                    "".join(forbidden.split()), "".join(outside_attended.split())
                )

    def test_feature_lead_excludes_boundary_stops_from_the_gate_decision_point(
        self,
    ) -> None:
        """Keep the impl-lead-gate decision point from re-absorbing boundary stops."""
        # TQ-5; TQ-8; TQ-19; AC-8(d) mechanism. Scoped to the gate bullet
        # itself via `_bullet`, not just the "## 段の遷移と判断点の処理"
        # preamble list capped at "### " (TQ-8). The section cap alone still
        # let the exclusion clause migrate to a sibling bullet (the
        # `plan-craft` blocked bullet) or to the prose above the list and
        # keep passing: "これに含めない" is anaphoric and needs the gate
        # bullet's own sentence as its antecedent, the same anaphora risk
        # TQ-3 closed for the attended/unattended bullets. This is the last
        # bullet in the capped preamble list, so `_bullet` scopes it to
        # "gate marker through the end of that already-bounded section" —
        # the same trust in the caller's section boundary `_bullet`'s
        # docstring already documents for the `unattended` bullet.
        contract = (
            "ただし Branch Plan 境界（未授権の Branch Plan への到達）での停止は"
            "これに含めない。「Branch Plan 境界の停止」に従う。"
        )
        for platform, text in self._feature_lead_main_texts().items():
            section = self._section(
                text, "## 段の遷移と判断点の処理", next_heading="\n### "
            )
            gate_bullet = self._bullet(
                section, "- `impl-lead` が各 mode のゲートで停止した"
            )
            normalized = "".join(gate_bullet.split())
            with self.subTest(platform=platform):
                self.assertIn("".join(contract.split()), normalized)

    def test_feature_lead_keeps_the_boundary_stop_out_of_the_decision_ledger(
        self,
    ) -> None:
        """Explain, not just omit, why the boundary stop never becomes a ledger row."""
        # AC-8(d); RB-5; TQ-1; TQ-2. Scoped to "## 判断点台帳": RB-5 makes this
        # section the sole home for the non-recording rationale, so a copy
        # drifting away from "### Branch Plan 境界の停止" (checked separately
        # above to have none) cannot mask a regression here either.
        contracts = (
            "`origin: impl-lead-gate` として判断点台帳へ記録しない。",
            "台帳が対象とするのは段が返した判断点であり、境界の停止は授権が未設定で"
            "あることの帰結だからである。",
        )
        for platform, text in self._feature_lead_main_texts().items():
            section = self._section(text, "## 判断点台帳")
            normalized = "".join(section.split())
            for contract in contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)

    def test_feature_lead_flow_branches_at_the_boundary_before_the_final_report(
        self,
    ) -> None:
        """Give the numbered flow a stop/resume branch instead of a straight line."""
        # Completion criterion: the numbered "全体の流れ" list must not still end at
        # step 8 presenting the first Branch Plan's final report. Extracting the
        # section (capped at the next "## ") and asserting order, not just presence,
        # is required per the branch's own constraints: a whole-file containment
        # check cannot tell "the branch sits inside the numbered flow" from
        # "the same words happen to exist elsewhere in the file", and a prior
        # branch's review already found that miss in practice.
        # TQ-18/OER-1: 手順6 の位置は `required_order` の needle ではなく
        # `check="ordinal-order"`（手順6/7/8/9 の物理行 offset が昇順である
        # こと）と `step=6`（`^\s*6.` 行の本文が delegation 設定文であること）
        # の組で担保する。手順6の本文は `step_nine_contract` と異なり後段の
        # needle と同一の識別力を持たないため、`required_order` からは外す。
        required_order = (
            "`order` に従って Branch Plan を実行する。",
            "`impl-lead` が未授権の Branch Plan の境界で止まった場合は",
            "手順9を行わずに",
            "その Branch Plan について手順6から行い直す",
            "`order` の全 Branch Plan の実行が終わったら",
        )
        # TQ-12; TQ-17: the resume test elsewhere requires the literal "...
        # 手順6からその Branch Plan について行い直し..." but that alone ties
        # nothing to the ordinal "6" actually being the delegation-setting
        # step — a manuscript could renumber or reshuffle the steps and the
        # cross-reference text would keep matching by coincidence. Checking
        # each numbered step's own body (via `_numbered_step`, anchored to
        # the start of a physical line — see its docstring for why a bare
        # substring search is not enough) ties the ordinal to its content
        # directly, so renumbering or swapping step bodies breaks the match
        # instead of only renaming the cross-reference text. This is a
        # different failure mode from the position check above (TQ-18): that
        # one catches the right-numbered step landing in the wrong place,
        # this one catches the right content landing under the wrong number.
        step_six_contract = "".join(
            "「授権の根拠」に従い、対象 Branch Plan の `delegation` を設定する。".split()
        )
        step_nine_contract = "".join(
            "`order` の全 Branch Plan の実行が終わったら".split()
        )
        for platform, text in self._feature_lead_main_texts().items():
            flow = self._section(text, "## 全体の流れ")
            normalized_flow = "".join(flow.split())
            positions: list[int] = []
            for phrase in required_order:
                needle = "".join(phrase.split())
                with self.subTest(platform=platform, phrase=phrase):
                    self.assertIn(needle, normalized_flow)
                positions.append(normalized_flow.find(needle))
            with self.subTest(platform=platform, check="order"):
                self.assertEqual(positions, sorted(positions))
            with self.subTest(platform=platform, step=6):
                self.assertIn(
                    step_six_contract,
                    "".join(self._numbered_step(flow, 6).split()),
                )
            with self.subTest(platform=platform, step=9):
                self.assertIn(
                    step_nine_contract,
                    "".join(self._numbered_step(flow, 9).split()),
                )
            # TQ-20; TQ-21: `required_order`'s position check relies on the
            # needle occurring nowhere else in the flow; `str.find` returns
            # the *first* match, so a decoy copy of 手順6's sentence placed
            # earlier in the flow (with the real step later swapped past
            # 手順7 or 手順9) would pin `positions[0]` to the decoy and let
            # the swap through undetected — two edits, but the second one
            # alone reproduces RB-2's infinite loop. `_numbered_step_offset`
            # closes this the same way `_numbered_step` itself is anchored:
            # it sums the lengths of the physical lines before the one that
            # actually matched `^\s*N\.`, rather than re-searching `flow` for
            # the step's body text as a bare substring. A plain
            # `flow.index(self._numbered_step(flow, n))` looks equivalent but
            # is not — it performs exactly that bare substring search, so a
            # decoy that quotes the ordinal-prefixed sentence (not just the
            # unprefixed body `required_order` guards against) still returns
            # the decoy's offset instead of the real step's; TQ-21 found this
            # in practice.
            with self.subTest(platform=platform, check="ordinal-order"):
                step_starts = [
                    self._numbered_step_offset(flow, n) for n in (6, 7, 8, 9)
                ]
                self.assertEqual(step_starts, sorted(step_starts))

    def test_feature_lead_has_no_remaining_branch_plan_data_wording(self) -> None:
        """Retire the pre-Set field name, including a whitespace-split rewrap."""
        # TQ-4. Normalized the same way as every other contract in this file;
        # the previous raw-text check missed a line-wrapped "Branch Plan\nData".
        forbidden = "".join("Branch Plan Data".split())
        for platform, text in self._feature_lead_main_texts().items():
            with self.subTest(platform=platform):
                self.assertNotIn(forbidden, "".join(text.split()))

    def test_feature_lead_does_not_duplicate_impl_lead_intake_presentation_wording(
        self,
    ) -> None:
        """Point at branch-plan-intake.md instead of restating its boundary text."""
        # TQ-7: resolved via the same reference-path builder the support module
        # already exposes for this skill, instead of a hand-written Path.
        intake_text = self._repository_text(
            shared_skill_reference_path(IMPL_LEAD_SKILL, "branch-plan-intake.md")
        )
        duplicated_phrase = (
            "完了済み Branch Plan の最終報告と未実行 Branch Plan の一覧を提示して、"
            "その Branch Plan の授権を要求する。"
        )
        normalized_duplicated_phrase = "".join(duplicated_phrase.split())
        # Guard the guard: if the phrase ever moves or is reworded in the intake
        # reference, this fails loudly instead of the negative assertion below
        # silently passing for the wrong reason.
        self.assertIn(
            normalized_duplicated_phrase, "".join(intake_text.split())
        )
        for platform, text in self._feature_lead_main_texts().items():
            with self.subTest(platform=platform):
                self.assertNotIn(
                    normalized_duplicated_phrase, "".join(text.split())
                )


if __name__ == "__main__":
    unittest.main()
