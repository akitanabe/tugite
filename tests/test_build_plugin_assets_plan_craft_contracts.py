"""Repository contracts for plan-craft."""

from __future__ import annotations

from pathlib import Path
import re
import unittest

from build_plugin_assets_test_support import (
    CLAUDE_PROFILE_PATH,
    CODEX_PROFILE_PATH,
    GENERATED_MARKDOWN_WARNING,
    REPOSITORY_ROOT,
    RepositoryContractSupport,
    generated_skill_path,
    generated_skill_reference_path,
    shared_skill_path,
    shared_skill_reference_path,
)


PLAN_CRAFT_SKILL = "plan-craft"
SCHEMA_REFERENCE_NAME = "implementation-plan-schema.md"
DRAFT_REFERENCE_NAMES = (
    "implementation-plan-schema.md",
    "plan-drafting.md",
    "adversarial-review.md",
    "overengineering-plan-review.md",
)
PLAN_BODY_SECTIONS_HEADING = "## プラン本文の節構成"
# 廃止した `plan.design` / `plan.approach` / `plan.steps` を現行の field として指す表記。
# 素の英単語（design / steps）は英語の frontmatter や散文にも一致するため採らない。
# backtick 付き・ドット付き・YAML key 形に加え、接頭辞なしの列挙も直接列挙する。
# 廃止した設計を Why Not として説明する記述もこの走査に掛かるため、そうした説明は
# field 名を使わずに書く。その代替文は schema の設計方針に置き、専用テストで固定する。
RETIRED_PLAN_FIELD_TOKENS = (
    "plan.design",
    "plan.approach",
    "plan.steps",
    "`design`",
    "`approach`",
    "`steps`",
    "design:",
    "approach:",
    "steps:",
    "objective / design / approach / steps",
    "`approach` / `steps` / `acceptance_criteria`",
    "steps・AC",
)
# 起草時に Implementation Plan の field へ書き込ませる指示。field 名の単独出現は
# スキーマ側・レビュー規約側で正当に残るため、書き込みを指示する形の結合文字列で見る。
DRAFTING_FIELD_WRITE_INSTRUCTIONS = (
    "`plan.source` に",
    "`plan.objective`",
    "`open_questions` にする",
    "`assumptions` に明示する",
)
RETIRED_FIELD_SCAN_ROOTS = (
    Path("shared/skill/plan-craft"),
    Path("plugins/claude/skills/plan-craft"),
    Path("plugins/codex/skills/plan-craft"),
)
PLAN_REVIEWER_AGENT_NAMES = (
    "plan-adversarial-reviewer",
    "over-engineering-reviewer",
)


class DraftImplementationPlanContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _draft_skill_texts(self) -> dict[str, str]:
        return {
            "source": self._repository_text(shared_skill_path(PLAN_CRAFT_SKILL)),
            "claude": self._repository_text(
                generated_skill_path("claude", PLAN_CRAFT_SKILL)
            ),
            "codex": self._repository_text(
                generated_skill_path("codex", PLAN_CRAFT_SKILL)
            ),
        }

    def _draft_reference_texts(self, name: str) -> dict[str, str]:
        return {
            "source": self._repository_text(
                shared_skill_reference_path(PLAN_CRAFT_SKILL, name)
            ),
            "claude": self._repository_text(
                generated_skill_reference_path("claude", PLAN_CRAFT_SKILL, name)
            ),
            "codex": self._repository_text(
                generated_skill_reference_path("codex", PLAN_CRAFT_SKILL, name)
            ),
        }

    def test_draft_skill_exposes_platform_frontmatter_and_reference_links(
        self,
    ) -> None:
        """Expose drafting frontmatter and route each detail to its reference."""
        for platform in ("claude", "codex"):
            main = self._draft_skill_texts()[platform]
            with self.subTest(platform=platform):
                self.assertTrue(main.startswith(f"---\nname: {PLAN_CRAFT_SKILL}\n"))
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
            # violation code をここで全列挙する。ただし素の部分文字列は本文の他所（Why Not
            # 段落など）にも一致しうるため、この列挙は表の網羅性の目安であって行の存在証明
            # ではない。行本文と表内での位置は code ごとの専用テストが固定する。
            "body-missing",
            "handoff-incomplete",
            "## 状態遷移と権限",
            "## branch-design への引き渡し",
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
        """Route branch terminology to the impl-lead glossary, not a local copy."""
        required = (
            "用語",
            "impl-lead",
            "../../impl-lead/references/implementation-branches.md",
        )
        for platform, text in self._draft_reference_texts(
            "implementation-plan-schema.md"
        ).items():
            with self.subTest(platform=platform):
                for contract in required:
                    self.assertIn(contract, text)

    def _schema_reference_texts(self) -> dict[str, str]:
        return self._draft_reference_texts(SCHEMA_REFERENCE_NAME)

    @staticmethod
    def _plan_block(text: str) -> list[str]:
        lines = text.splitlines()
        return lines[lines.index("plan:") : lines.index("acceptance_criteria:")]

    @staticmethod
    def _section_lines(text: str, heading: str) -> list[str]:
        lines = text.splitlines()
        rest = lines[lines.index(heading) + 1 :]
        end = next(
            (index for index, line in enumerate(rest) if line.startswith("## ")),
            len(rest),
        )
        return rest[:end]

    def test_draft_schema_reference_holds_the_plan_body_as_three_fields(self) -> None:
        """Keep plan to objective, source, and a block-scalar body of the reviewed prose."""
        # 2 空白インデントの key だけを拾う。`body` の block scalar の中身は 4 空白以上へ
        # 字下げされるため、この抽出にも `_section_lines` の行頭 `## ` 判定にも掛からない。
        # プレースホルダを他の field と同じ平文1行で書くと、本文の Markdown を入れた時点で
        # Data が不正な YAML になるため、block scalar であること自体を固定する。
        for platform, text in self._schema_reference_texts().items():
            with self.subTest(platform=platform):
                block = self._plan_block(text)
                keys = tuple(
                    match.group(1)
                    for match in (re.match(r"^  ([a-z_]+):", line) for line in block)
                    if match is not None
                )
                self.assertEqual(("objective", "source", "body"), keys)
                self.assertTrue(
                    any(line.strip() == "body: |" for line in block),
                    "plan.body must be written as a block scalar",
                )
                joined = "".join("".join(block).split())
                for retired in ("design:", "approach:", "steps:"):
                    self.assertNotIn(retired, joined)

    def test_draft_schema_reference_keeps_the_structural_field_annotations(
        self,
    ) -> None:
        """Keep the AC annotations pointing at the plan body's design section."""
        # #108 は、文を書き換えるときに同居する既存義務を巻き添えで落とす失敗を4件
        # 実測している。plan block の作り直しで触れる acceptance_criteria の注記が
        # 担っていた義務を個別に固定し、置換で消えたことを検出する。
        required = (
            "id: AC-1                    # 安定 ID。Branch Plan へそのまま引き継ぎ可能。振り直さない",
            "text: <観測可能な振る舞い>",
            "規約本文の正本はプラン本文の「設計」節。",
            "その充足を判定する観測可能な振る舞いだけを書く",
        )
        for platform, text in self._schema_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_draft_schema_reference_keeps_the_plan_scope_design_principles(
        self,
    ) -> None:
        """Keep the schema's own principles while the section conventions move away."""
        required = (
            "Implementation Plan は実装枝への分割を持たない。分割は `branch-design` の責務であり、"
            "プラン本文の「手順」節は起草者が実装の道筋を示す順序付き作業であって、AC を所有しない。",
            "AC は安定 ID を持ち、Branch Plan の `acceptance_criteria` へそのまま引き継げる形",
            "レビューの経過は `review.findings` に全 round・全 reviewer 通算の指摘台帳として持つ。",
            "`validation.blocking` は安定した code を持つ violation の配列とし、承認可否は "
            "blocking violation の有無だけで決まる。自己評価 boolean は持たない。",
            "承認（`approval`）は Implementation Plan の確定だけを意味し、"
            "枝分割・委譲の開始権限を含まない。",
        )
        # 設計文書を Data の field に据える案と別 artifact へ分離する案を棄却した理由は、
        # 本変更がその「棄却した案」に見える形へ進むため、削除ではなく回答へ置き換える。
        # 置き換えないと、次の改訂者が同じ案の再提出と読む。廃止 field 名を使わずに書く
        # 制約は、この文自体が RETIRED_PLAN_FIELD_TOKENS の走査対象に入るためである。
        superseded_rejection = (
            "1つの設計判断を複数の場所へ別々の言い回しで写すと、"
            "レビューは写しの不一致の同期に費やされる。",
            "以前この案を棄却したのは、分離した artifact と Data が並存して写しが残るため"
            "であった。本設計では並存しない。",
            "乖離が入りうるのは確定時の転記の1点に限られ、round ごとに増殖しない。",
        )
        for platform, text in self._schema_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required + superseded_rejection:
                    self.assertIn("".join(contract.split()), normalized)

    def test_draft_schema_reference_transcribes_structural_fields_from_the_plan_body(
        self,
    ) -> None:
        """Generate the structural fields once, by transcription, at confirmation time."""
        required = (
            "構造 field（`acceptance_criteria` / `scope` / `dependencies` / `constraints` / "
            "`open_questions` / `assumptions`）は、確定時に `plan.body` の該当節から"
            "言い換えずに転記する。",
            "レビュー中は本文だけが存在し、構造 field は確定時に1回だけ生成する。",
            "`plan.objective` は `plan.body` の見出し行から、`plan.source` は「要求の所在」行から、"
            "いずれも言い換えずに転記する。",
        )
        # 転記一致を code にしない理由は violation code 節が持つ。設計方針側へも写すと、
        # 本変更が塞ごうとしている「1つの判断が複数箇所へ別の言い回しで残る」を再現する。
        not_a_violation_code = (
            "構造 field が `plan.body` の該当節と食い違っていないか",
            "転記一致と節見出しの有無は code にしない",
        )
        for platform, text in self._schema_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)
                violation_section = "".join(
                    "".join(
                        self._section_lines(text, "## blocking violation code")
                    ).split()
                )
                for contract in not_a_violation_code:
                    self.assertIn("".join(contract.split()), violation_section)

    def test_draft_schema_reference_delegates_the_section_conventions_to_plan_drafting(
        self,
    ) -> None:
        """Hold only a pointer to the body-section conventions, never a second copy."""
        delegation = (
            "プラン本文の節構成と各節の責務は [起草手順](plan-drafting.md) の"
            "「プラン本文の節構成」を正本とする。"
        )
        # 委譲だけを持つことは、リンクの存在では固定できない。正本側の本文が写された
        # ことを検出するために、移設した2文が現れないことを文書全体で見る。
        moved_away = (
            "分量はそのプランで実際に決めた事項の数に従い、決めた事項が少なければ短くてよい",
            "要約にすると",
        )
        for platform, text in self._schema_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                self.assertIn("".join(delegation.split()), normalized)
                for contract in moved_away:
                    self.assertNotIn("".join(contract.split()), normalized)

    def test_draft_schema_reference_blocks_a_plan_that_has_no_body(self) -> None:
        """Block an empty plan body from reaching awaiting_review or approved."""
        body_missing_row = (
            "| `body-missing` | `plan.body` が未記載または空のまま "
            "`awaiting_review` 以降へ遷移している |"
        )
        # approved は blocking が空であることを前提にしているため、body-missing が
        # 立つ限り approved へ到達しない。この前提文が残ることで、遷移表へ本文専用の
        # 行を足さずに「本文が空のまま approved にできない」が成立する。
        approved_precondition = (
            "approved:         承認済み。open_questions と validation.blocking が"
            "すべて空であることが前提"
        )
        for platform, text in self._schema_reference_texts().items():
            with self.subTest(platform=platform):
                self.assertIn(
                    "".join(approved_precondition.split()), "".join(text.split())
                )
                # 行が blocking violation code 節の中にあることまで固定する。body-missing が
                # validation.blocking に載ることが approved 到達不能の第一リンクであり、
                # 本文のどこかに同じ文字列があるだけではその連鎖は成立しない。
                violation_section = "".join(
                    "".join(
                        self._section_lines(text, "## blocking violation code")
                    ).split()
                )
                self.assertIn("".join(body_missing_row.split()), violation_section)
                self.assertNotIn("design-missing", violation_section)

    def test_draft_schema_reference_keeps_semantic_checks_out_of_the_violation_codes(
        self,
    ) -> None:
        """Record why transcription and section checks cannot join the recomputable codes."""
        required = (
            "入力 Data から再計算できる検査だけで成り立つ",
            "意味判断であり、Data から再計算できない",
            "表全体の再計算可能性が壊れる",
            # 担い手は「起草手順とレビューの判定」の粒度に留める。どちらがどう担うかを
            # ここで書き切ると、後続で決める配分の選択肢を先に潰す。
            "節の充足は起草手順とレビューの判定が担う",
            # 節見出しの有無を検査条件に足すと、どの見出しをどう書けば節と認めるかを
            # Data 検査のために固定することになり、本文を散文にした目的と衝突する。
            "本文が規定の節見出しを備えているか",
        )
        for platform, text in self._schema_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_draft_schema_reference_keeps_the_branch_design_handoff_map_unchanged(
        self,
    ) -> None:
        """Keep the handoff rows as branch-design's input requirements, without the body."""
        # 左列は branch-design の入力要件そのもの。5行の全列挙は「行が消えないこと」しか
        # 検出しないので、表の領域を切り出して行数も固定し、6行目の追加を落とす。
        rows = (
            "| 実装目的 | `plan.objective` |",
            "| 元プラン | `plan.source`（この Data 自体を渡す場合は本 Data の所在） |",
            "| Acceptance Criteria（原文） | `acceptance_criteria[].text`（ID ごと原文のまま） |",
            "| 変更可能範囲と変更禁止範囲 | `scope.allowed_paths` / `scope.forbidden_paths` |",
            "| 既知の依存 | `dependencies` |",
        )
        why_not = (
            "左列は `branch-design` の入力要件そのものであり、"
            "行を足すことは入力要件の変更になる",
            "`handoff-incomplete` と `body-missing` の検査対象が二重になり、"
            "1つの欠落に2つの code が立つ",
            # handoff-incomplete の必須 field 列挙も固定する。ここへ plan.body を足すと、
            # 上の Why Not が避けた「1つの欠落に2つの code」が表の外側で成立してしまう。
            "| `handoff-incomplete` | 引き渡し必須 field（`plan.objective` / `plan.source` / "
            "`acceptance_criteria` / `scope`）の欠落 |",
        )
        for platform, text in self._schema_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in rows + why_not:
                    self.assertIn("".join(contract.split()), normalized)
                table = [
                    line
                    for line in self._section_lines(
                        text, "## branch-design への引き渡し"
                    )
                    if line.startswith("|")
                ]
                self.assertEqual(
                    len(table),
                    len(rows) + 2,
                    "the handoff map must keep exactly the branch-design input rows",
                )
                self.assertNotIn("plan.body", "".join(table))
                # 表が別節へ丸ごと複製された場合は上の節 slice の行数固定だけでは検出できない
                # （複製先の別 slice には現れない）。文書全体で単一の表であることも併せて担保する。
                self.assertEqual(
                    normalized.count("|`plan.objective`|"),
                    1,
                    "the handoff map must stay a single table",
                )

    def test_plan_review_inputs_hand_the_whole_plan_body_to_both_reviewers(
        self,
    ) -> None:
        """Hand the whole plan body — and nothing enumerated beside it — to both reviewers."""
        # 必須ゲートである過剰実装審査の審査対象が reviewer へ渡ることを担保する。
        # 本文とは別に AC・scope・constraints・assumptions を列挙して渡すと、本文と
        # 重複した写しが入力の側に残る。渡す対象の宣言と、別列挙が無いことを対にして見る。
        checks = {
            "overengineering-plan-review.md": (
                "## 渡す入力",
                (
                    "プラン本文の全文",
                    "2 round 目以降は前 round までの指摘台帳",
                ),
                ("plan.objective", "AC の全文", "`allowed_paths`"),
            ),
            "adversarial-review.md": (
                "## round の構成",
                (
                    "reviewer へプラン本文の全文と、2 round 目以降は前 round までの"
                    "指摘台帳を渡して起動する。",
                ),
                ("AC、scope、constraints、assumptions",),
            ),
        }
        for name, (heading, required, forbidden) in checks.items():
            for platform, text in self._draft_reference_texts(name).items():
                with self.subTest(reference=name, platform=platform):
                    section = "".join(
                        "".join(self._section_lines(text, heading)).split()
                    )
                    for contract in required:
                        self.assertIn("".join(contract.split()), section)
                    for contract in forbidden:
                        self.assertNotIn("".join(contract.split()), section)

        agent_checks = {
            "plan-adversarial-reviewer": (
                "## 立場",
                (
                    "判定にはプラン本文の全文と、対象 repository への読み取りアクセスが"
                    "必要です。",
                    "2 round 目以降は前 round までの指摘台帳を受け取ります。",
                ),
            ),
            # 「立場」節が持つ diff 入力モード向けの入力一覧はこの判定の対象外なので、
            # over-engineering-reviewer はプラン入力モード節だけを切り出して見る。
            "over-engineering-reviewer": (
                "## プラン入力モード",
                ("判定にはプラン本文の全文を使います。",),
            ),
        }
        for agent, (heading, required) in agent_checks.items():
            with self.subTest(agent=agent):
                source = self._repository_text(Path("shared/agents") / f"{agent}.md")
                section = "".join(
                    "".join(self._section_lines(source, heading)).split()
                )
                for contract in required:
                    self.assertIn("".join(contract.split()), section)
                self.assertNotIn(
                    "".join("objective / design / approach / steps".split()), section
                )

    def _retired_field_scan_paths(self) -> list[Path]:
        paths: list[Path] = []
        for root in RETIRED_FIELD_SCAN_ROOTS:
            paths.extend(
                sorted(
                    candidate.relative_to(REPOSITORY_ROOT)
                    for candidate in (REPOSITORY_ROOT / root).rglob("*")
                    if candidate.is_file()
                )
            )
        for agent in PLAN_REVIEWER_AGENT_NAMES:
            paths.append(Path("shared/agents") / f"{agent}.md")
            paths.append(CLAUDE_PROFILE_PATH / f"{agent}.md")
            paths.append(CODEX_PROFILE_PATH / f"{agent}.toml")
        return paths

    def test_plan_craft_manuscripts_drop_the_retired_plan_fields(self) -> None:
        """Leave no manuscript naming the retired plan fields as current fields."""
        for path in self._retired_field_scan_paths():
            normalized = "".join(self._repository_text(path).split())
            for token in RETIRED_PLAN_FIELD_TOKENS:
                with self.subTest(path=str(path), token=token):
                    self.assertEqual(
                        0,
                        normalized.count("".join(token.split())),
                        f"{path} still names a retired plan field",
                    )

    def test_draft_skill_matches_confirmed_contract(self) -> None:
        """Separate plan approval from downstream work and keep drafting review-gated."""
        required = (
            "確認モードの既定は `review`",
            "`auto` はユーザーが明示した場合のみ",
            "`branch-design` を直接起動しない",
            "blocking な不足はプラン本文の「依存 / 制約 / 前提 / 未確定」節",
            "minor な不足は同じ節に仮定として明示",
            "`rounds_limit` の既定は 10",
            "reviewer の自己申告をそのまま採用しない",
        )
        for platform, main in self._draft_skill_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(main.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_draft_skill_generates_the_plan_data_after_both_reviews(self) -> None:
        """Build the Data once, after both reviews and before blocking is recomputed."""
        # 手順の番号ではなく本文の出現位置で順序を測る。手順は複数行へ折り返され、
        # 番号行だけを拾うと折り返した本文が落ちる。
        ordered = (
            "[敵対的レビューループ]",
            "[過剰実装のプラン審査]",
            "Implementation Plan Data を生成する",
            "`validation.blocking` を確定する",
        )
        for platform, main in self._draft_skill_texts().items():
            with self.subTest(platform=platform):
                flow = "".join(
                    "".join(self._section_lines(main, "## 全体の流れ")).split()
                )
                positions = []
                for marker in ordered:
                    position = flow.find("".join(marker.split()))
                    self.assertGreater(position, -1, f"the flow must cover {marker}")
                    positions.append(position)
                self.assertEqual(
                    positions,
                    sorted(positions),
                    "the plan Data must be generated after both reviews",
                )
                self.assertIn(
                    "".join(
                        "この時点では Implementation Plan Data を生成しない。".split()
                    ),
                    flow,
                )

    def test_draft_review_reference_targets_the_plan_body_not_the_ac_set(
        self,
    ) -> None:
        """Point the loop at the plan body's design section, not the acceptance criteria set."""
        # 判定対象の宣言は round の構成節に置く。文書全体を検索すると、後続で別節へ
        # 移動しても落ちないため、round 手順の先頭にあることまでを固定する。
        # 同じ宣言を運用者向けと reviewer 向けの両方へ置くため、どちらが正本かを添えないと
        # 語気の差が次の改訂で別の規定に見える。所有者の1語まで含めて固定する。
        declaration = (
            "レビューが判定する対象はプラン本文の「設計」節であって AC の集合ではない"
            "（判定の軸の正本は `plan-adversarial-reviewer`）。"
        )
        # 責務分担の本文はここへ写さず正本を指す。写した時点でこの PR が塞ぐ経路
        # （1つの設計判断が複数箇所へ別の言い回しで残る）を原稿自身が再現する。
        # 責務分担の正本はスキーマから起草手順の「プラン本文の節構成」へ移った。
        canonical_link = "[起草手順](plan-drafting.md)"
        texts = self._draft_reference_texts("adversarial-review.md")
        for structure, text in texts.items():
            with self.subTest(structure=structure):
                section = "".join(
                    "".join(self._section_lines(text, "## round の構成")).split()
                )
                self.assertIn("".join(declaration.split()), section)
                self.assertIn("".join(canonical_link.split()), section)

    def test_draft_review_reference_places_the_ledger_outside_the_plan_body(
        self,
    ) -> None:
        """Keep the findings ledger out of the prose and inside the review block."""
        required = (
            "指摘台帳と round 状態はプラン本文の外に持つ。",
            "本文へ書くと、指摘の解消が本文の変更として現れず、"
            "round ごとに本文と台帳の両方を同期することになる。",
            "台帳は Implementation Plan の `review` block そのものとし、"
            "新しい field 名を導入しない。",
            "確定時は写し替えや構造変換を行わず、そのまま `review` の下へ置く。",
        )
        for platform, text in self._draft_reference_texts(
            "adversarial-review.md"
        ).items():
            with self.subTest(platform=platform):
                section = "".join(
                    "".join(self._section_lines(text, "## 指摘台帳")).split()
                )
                for contract in required:
                    self.assertIn("".join(contract.split()), section)

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
            "(../../impl-lead/references/reviewer-findings.md)",
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
        relative_link = "../../impl-lead/references/reviewer-findings.md"
        reference_paths = {
            "source": shared_skill_reference_path(
                PLAN_CRAFT_SKILL, "adversarial-review.md"
            ),
            "claude": generated_skill_reference_path(
                "claude", PLAN_CRAFT_SKILL, "adversarial-review.md"
            ),
            "codex": generated_skill_reference_path(
                "codex", PLAN_CRAFT_SKILL, "adversarial-review.md"
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

    def test_overengineering_plan_review_triggers_on_the_plan_body(self) -> None:
        """Trigger on a received plan body and bounce back only a plan without any AC."""
        launch = (
            "起動時にプラン入力モードであることを明示し、レビュー済みのプラン本文の全文を渡す。",
            "明示しない起動は既定の diff 入力モードになるため、プラン審査には使えない。",
        )
        bounce_back = (
            "「Acceptance Criteria」節に AC が1件も無いプラン本文は、"
            "reviewer が判定せず親へ差し戻す。",
            # 制約の記載を差し戻し条件に残すと、制約が無い正当なプランが差し戻される。
            # 差し戻しは審査完了として記録されないため review-incomplete が立ち続け、
            # そのプランは awaiting_review へ到達できなくなる。
            "制約の記載の有無は差し戻し条件にしない。",
            "差し戻しは指摘0件と区別して扱い、"
            "`termination` や台帳に審査完了として記録しない。",
        )
        for platform, text in self._draft_reference_texts(
            "overengineering-plan-review.md"
        ).items():
            with self.subTest(platform=platform):
                launch_section = "".join(
                    "".join(self._section_lines(text, "## 起動契約")).split()
                )
                for contract in launch:
                    self.assertIn("".join(contract.split()), launch_section)
                bounce_section = "".join(
                    "".join(self._section_lines(text, "## 差し戻し条件")).split()
                )
                for contract in bounce_back:
                    self.assertIn("".join(contract.split()), bounce_section)
                self.assertNotIn(
                    "".join("AC または明示された制約が無い".split()), bounce_section
                )

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
            "対象（プラン本文の節または AC id）",
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

    def test_plan_adversarial_reviewer_reviews_the_design_section_first(
        self,
    ) -> None:
        """Judge the plan body's design section first while keeping the four failure modes."""
        source = self._repository_text(
            Path("shared/agents/plan-adversarial-reviewer.md")
        )
        section = "".join("".join(self._section_lines(source, "## 判定の軸")).split())
        required = (
            "主たる判定対象はプラン本文の「設計」節です。",
            # 判定対象を「設計」節へ寄せたときに、既存の失敗経路4種と「失敗経路を特定
            # できる指摘だけ」の縛りが道連れで落ちるのを防ぐ。判定対象の変更であって
            # 判定の緩和ではない。
            "AC を満たせない・検証できない・実装できない・手戻りが生じる"
            "具体的な失敗経路が存在するか。",
            "失敗経路を特定できる指摘だけを返す",
        )
        for contract in required:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), section)

    def test_plan_adversarial_reviewer_withholds_wording_differences_as_findings(
        self,
    ) -> None:
        """Drop wording differences alone while keeping contradictions with the design section."""
        source = self._repository_text(
            Path("shared/agents/plan-adversarial-reviewer.md")
        )
        section = "".join("".join(self._section_lines(source, "## 判定の軸")).split())
        required = (
            # 抑止は「失敗経路を特定できないまま」で限定する。無条件に抑止すると、
            # 「設計」節を薄く言い換えて判定不能になった AC が、「設計」節と矛盾もせず
            # 「設計」節に無い決定も含まないまま上位層で消える。散文1本になった分、
            # 隣接する節どうしの言い回し差で round が発散する余地は増えている。
            "プラン本文の節どうしの言い回しの差そのものを、"
            "失敗経路を特定できないまま単独の指摘として返さない",
            # 残す経路は例示。閉じた列挙にすると、新しい救済条件が現れるたびに列を
            # 伸ばすことになり、この原稿が塞ぐ「規約を分散して持つ」構造を再現する。
            # 枠組み文を固定しないと「これらも指摘対象から外します」への反転が通る。
            "たとえば次は指摘対象として残ります。",
            "「設計」節と矛盾する",
            "「設計」節に無い決定を含む",
        )
        for contract in required:
            with self.subTest(contract=contract):
                # 抑止と例示が同じ節に併記されることまでを検証する。文書全体を対象に
                # すると、例示だけ別節へ散らす改訂が通る。
                self.assertIn("".join(contract.split()), section)

    def test_plan_adversarial_reviewer_separates_return_scope_from_the_verdict(
        self,
    ) -> None:
        """Keep the wording rule about what to return, not about how to grade it."""
        source = self._repository_text(
            Path("shared/agents/plan-adversarial-reviewer.md")
        )
        section = "".join("".join(self._section_lines(source, "## 判定の軸")).split())
        # 返す範囲の規定と verdict の規定が同じ層に見えると、軽微類型カタログの
        # 「軽微としない条件」が返却前の抑止に飲まれる。層の別を明記させる。
        # スコープは節に限る。文書全体を対象にすると、この一文が「判定区分と
        # `軽微` の定義」節へ移された場合を検出できない。この一文は「返す範囲は
        # ここ（判定の軸）にあり、判定区分は別節が持つ」という層の所在そのものの
        # 宣言なので、意味が置かれた節に依存させる必要があり、移されると自己参照に
        # なって層の別を表さなくなる。
        self.assertIn(
            "".join(
                (
                    "これは指摘として返す範囲の規定であり、返した指摘の判定区分は"
                    "「判定区分と `軽微` の定義」に従います。"
                ).split()
            ),
            section,
        )

    def test_plan_adversarial_reviewer_keeps_the_six_finding_types(self) -> None:
        """Keep all six finding types when the review target moves to the plan body."""
        source = self._repository_text(
            Path("shared/agents/plan-adversarial-reviewer.md")
        )
        section_lines = self._section_lines(source, "## 指摘の類型")
        types = (
            "見落とし",
            "根拠のない仮定",
            "AC の曖昧さ",
            "実現不能性",
            "依存の見落とし",
            "範囲の矛盾",
        )
        # 個々の名前の存在だけでは、類型を1つ落として別の1つを足した改訂を通す。
        # 節内の項目数も併せて固定する。
        self.assertEqual(
            len([line for line in section_lines if line.startswith("- ")]),
            len(types),
            "the finding-type catalog must keep exactly its six types",
        )
        for name in types:
            with self.subTest(name=name):
                self.assertIn(f"- {name}: ", "\n".join(section_lines))

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
            "カタログは影響基準の適用例",
            "カタログ外の指摘も影響基準を満たせば `軽微`",
        )

        for contract in required:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), normalized)

        catalog = (
            "文言・表現の好み",
            "プラン本文の整形・体裁（項目順、記法、表記ゆれ）",
            "「依存 / 制約 / 前提 / 未確定」節に記録済みの事項の再指摘",
            "同義の言い換え提案",
        )
        escapes = (
            "AC の判定可能性を損なう曖昧さを含む場合",
            # 旧文言「スキーマ違反により」に対応する概念は、節構成を定めた以上は
            # 節構成の欠落である。新しい規約の追加ではなく同じ escape の言い換え。
            "節構成を欠いて後続工程が読み取れなくなる場合",
            "仮定を覆す新しい根拠を伴う場合",
            "現行の文言そのものが失敗経路の根拠になっている場合",
        )
        # 件数を数えるスコープは `### 軽微類型カタログ` 以降に限る。`## 判定区分と
        # `軽微` の定義` 全体で数えると、`### 影響基準` へ箇条書きを足しただけで
        # カタログの契約違反として報告され、失敗メッセージから原因の節へ辿れない。
        # `_section_lines` は次の `## ` までを返すため終端を自前で切り、カタログの
        # 後ろに新しい `### ` 節が足された場合の混入も防ぐ（共有シグネチャは他の
        # 呼び出しへ波及するため変えない）。
        catalog_lines = self._section_lines(source, "### 軽微類型カタログ")
        catalog_end = next(
            (
                i
                for i, line in enumerate(catalog_lines)
                if line.startswith("### ")
            ),
            len(catalog_lines),
        )
        catalog_lines = catalog_lines[:catalog_end]
        catalog_section = "".join("".join(catalog_lines).split())
        for contract in catalog + escapes:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), catalog_section)
        self.assertEqual(
            len([line for line in catalog_lines if line.startswith("- ")]),
            len(catalog),
            "the trivial catalog must keep exactly its four types",
        )

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
            "明示してプラン本文を渡した場合のみ",
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

    def test_over_engineering_reviewer_plan_mode_states_its_own_fallback(
        self,
    ) -> None:
        """Let the plan mode carry its own bounce-back rule and override the stance demand."""
        source = self._repository_text(
            Path("shared/agents/over-engineering-reviewer.md")
        )
        section = "".join(
            "".join(self._section_lines(source, "## プラン入力モード")).split()
        )
        required = (
            "「Acceptance Criteria」節に AC が1件も無いプラン本文は、推測で補わず、"
            "判定せず親へ差し戻してください。",
            "制約の記載の有無は差し戻し条件にしません。",
            # 「立場」節の入力要求は mode を限定せず agent 全体に掛かるため、参照を
            # やめるだけでは矛盾が残る。明示的な否定文で上書きする。同節が既に
            # 「テスト結果は入力として要求しない」で立場節を上書きしている構造に揃える。
            "AC・明示された制約が別立てで渡されていないことを理由に親へ要求しないで"
            "ください。",
        )
        for contract in required:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), section)
        # 差し戻し条件が「立場」節を参照したままだと、同節だけで条件が読み切れない。
        self.assertNotIn("".join("diff 入力モードと同様に".split()), section)

    def test_over_engineering_reviewer_keeps_the_diff_mode_input_demand(self) -> None:
        """Keep the stance section's diff-mode input demand untouched by the plan mode."""
        # impl-lead の必須完了ゲートが diff を渡して起動するとき、AC と制約の受け渡しを
        # 担保するのはこの一文だけである。shared/skill/impl-lead/ は変更禁止のため、
        # 失われた保証を代替する場所がない。プラン入力モードの改訂で巻き添えにしない。
        source = self._repository_text(
            Path("shared/agents/over-engineering-reviewer.md")
        )
        section = "".join("".join(self._section_lines(source, "## 立場")).split())
        required = (
            "判定にはタスク要約、AC、親が明示した制約、対象コミット範囲、diff テキスト、"
            "テスト結果が必要です。",
            "AC または制約が渡されていない場合は推測で補わず、判定前に親へ要求します。",
        )
        for contract in required:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), section)

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

    def _plan_body_sections(self, text: str) -> str:
        return "".join(
            "".join(self._section_lines(text, PLAN_BODY_SECTIONS_HEADING)).split()
        )

    def test_plan_drafting_enumerates_the_plan_body_sections(self) -> None:
        """Name the heading line, the source line, and every section of the plan body."""
        # 節見出しの skeleton を fenced code block で書かない。行頭 `## 設計` を fence 内へ
        # 置くと `_section_lines` がそこで節を終端し、以降の固定文言を取りこぼしたまま
        # このテストが緑になる。節構成は箇条書きで表す。
        required = (
            "見出し行: 実装目的の1行要約。",
            "「要求の所在」行: 見出し行の直下に置く1行。",
            "「設計」: 決めた規約の本体。設計判断の正本。",
            "「方針」: 「設計」の規約を対象 repository の現状へ当てはめる方針。",
            "「手順」: 「設計」を実現する順序付きの作業。",
            "「Acceptance Criteria」: 安定 ID 付きの観測可能な振る舞い。",
            "「scope」: 変更可能 / 変更禁止 / 対象外。",
            "「依存 / 制約 / 前提 / 未確定」: 依存、ユーザーが明示した制約の原文、"
            "置いた仮定、確定が必要な問い。",
            # 「設計」節を空にできると読めると、body-missing は plan.body 全体の空だけを
            # 見るため、判定対象の設計文書が存在しないまま approved へ到達する経路が開く。
            "節は省略しない。該当する事項がない節には「該当なし」と書く。"
            "ただし「設計」節に「該当なし」は書けない。",
            # 章立ての免責と節構成の固定は両立する。免責の適用範囲を書かないと、
            # 節構成そのものを固定しない読みが立つ。
            "章立てと必須項目は固定しない。この免責は「設計」節の内側に限って適用し、"
            "本文の節構成そのものには適用しない。",
        )
        for platform, text in self._draft_reference_texts("plan-drafting.md").items():
            with self.subTest(platform=platform):
                section = self._plan_body_sections(text)
                for contract in required:
                    self.assertIn("".join(contract.split()), section)

    def test_plan_drafting_assigns_each_body_section_its_responsibility(self) -> None:
        """Hold the section responsibilities once, here, sized to what was decided."""
        # スキーマから移設した責務分担の正本。#108 は、文を書き換えるときに同居する
        # 既存義務を巻き添えで落とす失敗を4件実測している。移設元のテストが個別に
        # 固定していた義務を、移設先でも個別に固定する。
        required = (
            "「設計」に書くのは決めたことだけで、要求の再掲や背景の説明は含めない。",
            # 空にはできないが、決めた量以上を書く必要もないという境界。「設計」節を
            # 実質必須にする以上、この境界がないと小さなプランへ儀式的な作文を要求する
            # 読みが成立する。
            "分量はそのプランで実際に決めた事項の数に従い、決めた事項が少なければ短くてよい",
            "「方針」は「設計」の要約ではなく、「設計」が答えない"
            "「どこへ・既存構造のどれを使うか」を担当する。",
            "要約にすると「設計」と変更理由を共有し、写しが要約の粒度で残るためである。",
            "「手順」は実装の道筋であり、実装枝への分割はしない。"
            "AC の割り当て、受け入れ判断の単位、revert 単位は持たせない。"
            "それらは `branch-design` の責務である。",
            "「方針」「手順」「Acceptance Criteria」は、いずれも規約本文自体を保持しない。",
            "規約の正本は「設計」であり、他の節は「設計」を正本として参照する。",
        )
        for platform, text in self._draft_reference_texts("plan-drafting.md").items():
            with self.subTest(platform=platform):
                section = self._plan_body_sections(text)
                for contract in required:
                    self.assertIn("".join(contract.split()), section)

    def _drafting_procedure(self, text: str) -> str:
        return "".join(
            "".join(self._section_lines(text, "## 起草の進め方")).split()
        )

    def test_plan_drafting_writes_the_design_section_before_approach_ac_and_steps(
        self,
    ) -> None:
        """Draft the design section first, then apply, observe, and sequence it."""
        # 手順の番号ではなく本文の出現位置で順序を測る。手順は複数行へ折り返され、
        # 番号行だけを拾うと折り返した本文が落ちる。
        ordered = (
            "「設計」節に、",
            "「方針」節を書く",
            "AC を導出し",
            "「手順」節に",
        )
        for platform, text in self._draft_reference_texts("plan-drafting.md").items():
            with self.subTest(platform=platform):
                procedure = self._drafting_procedure(text)
                positions = []
                for marker in ordered:
                    position = procedure.find("".join(marker.split()))
                    self.assertGreater(
                        position, -1, f"drafting procedure must cover {marker}"
                    )
                    positions.append(position)
                self.assertEqual(
                    positions,
                    sorted(positions),
                    "the design section must be drafted before approach, AC, and steps",
                )

    def test_plan_drafting_delegates_the_approach_responsibility_to_the_body_sections(
        self,
    ) -> None:
        """Delegate what the 方針 section covers to the body sections, keeping the ban."""
        required = (
            "担当する内容は手順3 と同じく「プラン本文の節構成」を正本とし、"
            "ここでは再掲しない。",
            # 担当範囲の定義は節構成の担当だが、要約で書いてしまう失敗は起草時に起きる。
            # 失敗モードの禁止だけを手順側に残す。
            "「設計」節の要約にしない。",
        )
        for platform, text in self._draft_reference_texts("plan-drafting.md").items():
            with self.subTest(platform=platform):
                procedure = self._drafting_procedure(text)
                for contract in required:
                    self.assertIn("".join(contract.split()), procedure)
                # 担当範囲を節構成の言い回しで書き直すと、双方が別々のテストへ逐語固定され、
                # 片方だけの改訂で同期漏れが起きる。この PR が消そうとしている構造そのもの。
                self.assertNotIn(
                    "".join("どこへ・既存構造のどれを使う".split()), procedure
                )

    def _drafting_step(self, text: str, number: int) -> str:
        lines = self._section_lines(text, "## 起草の進め方")
        start = next(
            (
                index
                for index, line in enumerate(lines)
                if line.startswith(f"{number}. ")
            ),
            None,
        )
        if start is None:
            self.fail(f"drafting procedure step {number} was not found")
        rest = lines[start + 1 :]
        # 継続行のインデント幅では手順3 の範囲を区切らない。「3 空白以上」を境界にすると、
        # 2 空白インデントの子箇条（例: M4c 相当の必須項目の追加）が手順3 の外側として
        # すり抜け、次の手順の内容と誤認されないまま検出漏れになる。次の番号付き手順行の
        # 直前までを手順3 の範囲とし、インデント幅に関わらず子箇条を取り込む。
        end = next(
            (index for index, line in enumerate(rest) if re.match(r"\d+\. ", line)),
            len(rest),
        )
        return "".join("".join(lines[start : start + 1 + end]).split())

    def test_plan_drafting_defers_the_design_section_shape_to_the_body_sections(
        self,
    ) -> None:
        """Point the design section's responsibility split and size at the section conventions."""
        # 章立てを課すと、決めた事項が少ないプランへ空章の作文を要求する読みが立ち、
        # 節構成側の分量の境界と衝突する。免責文の存在だけを assertIn で見ると、免責文を
        # 残したまま必須項目を「追加」した自己矛盾を通してしまう。手順3 のブロック全体を
        # 固定し、免責文の削除と必須項目の追加の両方を検出する。免責文そのものは
        # 「プラン本文の節構成」へ移したため、手順3 は委譲だけを持つ。
        #
        # ただしブロック等価固定が守るのは手順3 の**内側**の改変だけである。分量の境界の
        # 写し（例:「「設計」節の分量は決めた事項が少なければ短くてよい」）は手順3 以外の
        # 位置（手順6 など）へ書かれてもこの PR が塞ぎたい失敗であり、ブロック等価固定では
        # 検出できない。節全体を対象にした assertNotIn を別途置き、写しの流入場所を手順3 に
        # 限定しない形で塞ぐ。両者は守備範囲が異なるため重複ではない。
        #
        # これら2つの assertion が機械的に塞ぐのは、手順3 の直後（インデント幅を問わない
        # 子箇条）へ必須項目を書く経路（M4c 相当）までである。手順3 以外の遠い手順へ独立した
        # 必須項目を書く経路（M4d 相当、例: 手順7 に「章立てを固定する」文を新設する）はこの
        # 境界拡張では塞がらない。M4d を機械で塞ぐには節全体の語彙禁止（「必須」「固定する」等の
        # 語を全手順で禁止する）が必要になり、正当な語彙まで巻き込む過剰検出になる。M4d は
        # レビュー（reviewer による diff 精査）側の判断に残す。
        expected = (
            "3. 「設計」節に、そのプランで決めた規約の本体を書く。"
            "節構成と各節の責務、および「設計」節の分量は"
            "「プラン本文の節構成」を正本とし、ここでは再掲しない。"
        )
        for platform, text in self._draft_reference_texts("plan-drafting.md").items():
            with self.subTest(platform=platform):
                self.assertEqual(
                    self._drafting_step(text, 3), "".join(expected.split())
                )
                procedure = self._drafting_procedure(text)
                self.assertNotIn(
                    "".join("決めた事項が少なければ短くてよい".split()), procedure
                )

    def test_plan_drafting_writes_sections_instead_of_plan_data_fields(self) -> None:
        """Keep every drafting instruction on the prose, never on the Data fields."""
        # 起草時に field へ書かせる指示が残ると、「レビュー前に Data を作り始める」経路が
        # 起草手順の正本の側から開く。field 名の単独出現はスキーマ側とレビュー規約側で
        # 正当に残るため、書き込みを指示する形の結合文字列だけを禁じる。
        texts = {
            f"plan-drafting.md:{platform}": text
            for platform, text in self._draft_reference_texts(
                "plan-drafting.md"
            ).items()
        }
        texts.update(
            {
                f"SKILL.md:{platform}": text
                for platform, text in self._draft_skill_texts().items()
            }
        )
        for label, text in texts.items():
            normalized = "".join(text.split())
            for instruction in DRAFTING_FIELD_WRITE_INSTRUCTIONS:
                with self.subTest(target=label, instruction=instruction):
                    self.assertNotIn("".join(instruction.split()), normalized)

    def test_plan_drafting_keeps_convention_text_out_of_acceptance_criteria(
        self,
    ) -> None:
        """Bar the convention body from AC text while keeping the observation point in it."""
        required = (
            "規約・設計の本文を AC の `text` へ再掲しない。",
            "規約の正本はプラン本文の「設計」節であり、AC は「設計」節の充足を"
            "外部から観測できる条件として書く。",
            # 「観測点を text に含める」既存規約と衝突して読まれないよう、含めるもの
            # （観測点）と含めないもの（規約本文）を同じ項目内で書き分ける。
            "text に含めるのは充足を判定する観測点であって、規約本文そのものではない。",
        )
        for platform, text in self._draft_reference_texts("plan-drafting.md").items():
            with self.subTest(platform=platform):
                section = "".join(
                    "".join(self._section_lines(text, "## AC の書き方")).split()
                )
                for contract in required:
                    self.assertIn("".join(contract.split()), section)

    def test_plan_drafting_keeps_the_obligations_the_rewritten_steps_carried(
        self,
    ) -> None:
        """Keep every obligation the drafting steps and AC rules carried before the rewrite."""
        # #108 は、文を書き換えるときに同居する既存義務を巻き添えで落とす失敗を4件
        # 実測している。節構成への書き換えで触れる手順と AC 規約の義務を個別に固定する。
        procedure = (
            "要求原文を言い換えずに保持し、プラン本文の「要求の所在」行に所在を書く。",
            "対象 repository の現状を読み、",
            # 前置詞句で切ると、禁止を許可へ反転させた原稿を通す。禁止条項は述部まで固定する。
            "現状を確認せずに以降の手順へ進まない。",
            "安定 ID を付与して「Acceptance Criteria」節に書く。",
            "「scope」節と「依存 / 制約 / 前提 / 未確定」節を確定し、"
            "確定できない事項を不足として振り分ける。",
            "「手順」節に「設計」節を実現する実装の道筋を順序付きで書く。",
        )
        ac_rules = (
            "AC は外部から観測可能な振る舞いとして書く。内部実装の手順や構造を AC にしない。",
            "受け入れ判断が割れない判定可能な文言にする。",
            "AC は定量値・列挙・観測可能な事象のいずれかの形式で書く。",
            "AC の text には、充足を判定する観測点",
            "ユーザーが文言を示した場合は原文のまま保持し、言い換えない。",
            "ID は `AC-1` 形式の安定 ID とし、プラン修正で振り直さない。",
        )
        for platform, text in self._draft_reference_texts("plan-drafting.md").items():
            with self.subTest(platform=platform):
                for contract in procedure:
                    self.assertIn(
                        "".join(contract.split()), self._drafting_procedure(text)
                    )
                section = "".join(
                    "".join(self._section_lines(text, "## AC の書き方")).split()
                )
                for contract in ac_rules:
                    self.assertIn("".join(contract.split()), section)

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

    def test_eval_corpus_describes_the_plan_body_procedure_section(self) -> None:
        """Describe EVAL-27's synthetic run through the plan body, not a Data field."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        section = "".join(
            "".join(
                self._section_lines(
                    corpus, "## EVAL-27: プラン入力モードの過剰実装指摘"
                )
            ).split()
        )
        required = (
            "プラン本文の「手順」節に、要求にない",
            "プラン本文の「手順」節から当該作業を取り除いた後",
        )
        # 書き換えで同居する既存の評価観点を落とさない。EVAL-27 の主眼は反映経路と
        # round 計上であって、入力の呼称ではない。
        preserved = (
            "指摘を同じ `PF-*` 台帳へ `reviewer: over-engineering-reviewer` として記録し",
            "採用指摘の反映はプラン修正だけで行う。",
            "プラン修正後に adversarial レビューを再実行してから提示する。",
            "過剰実装審査の round を `rounds_limit` の外に置いて無限ループの余地を残す。",
            "reviewer にテスト結果や diff を要求させる。",
        )
        for contract in required + preserved:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), section)
        for retired in ("プランの steps に", "当該 step を取り除いた"):
            with self.subTest(retired=retired):
                self.assertNotIn("".join(retired.split()), section)


if __name__ == "__main__":
    unittest.main()
