"""Repository contracts for plan-craft."""

from __future__ import annotations

from pathlib import Path
import unittest

from build_plugin_assets_test_support import (
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
            "design-missing",
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

    def test_draft_schema_reference_places_the_design_body_as_the_canonical_source(
        self,
    ) -> None:
        """Hold the decided conventions once, in plan.design, sized to what was decided."""
        # 期待値は1行に収まる単位で切り詰める。原稿の YAML コメントは複数行へ折り返され、
        # 折り返し先頭の "#" が空白除去後も残るため、行をまたぐ連結文字列は原稿の
        # 折り返し位置に依存して壊れる。
        required = (
            "design: <決めた規約の本体。設計判断の正本>",
            "`plan.design` は決めた規約の本体を1箇所に置く正本とする。",
            "いずれも規約本文自体を保持しない。",
            "`plan.approach` を設計文書に据える案と別 artifact に分離する案は棄却した。",
            # 空にはできないが、決めた量以上を書く必要もないという境界。design を
            # blocking にする以上、この境界がないと小さなプランへ儀式的な作文を要求する
            # 読みが成立する。
            "書くのは決めたことだけで、要求の再掲や背景の説明は含めない",
            "分量はそのプランで実際に決めた事項の数に従い、決めた事項が少なければ短くてよい",
        )
        for platform, text in self._schema_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)
                self.assertTrue(
                    any(
                        line.strip().startswith("design:")
                        for line in self._plan_block(text)
                    ),
                    "plan.design must live inside the plan block of the schema body",
                )

    def test_draft_schema_reference_subordinates_approach_steps_and_ac_to_the_design_body(
        self,
    ) -> None:
        """Let approach, steps, and AC point at the design body instead of restating it."""
        required = (
            "approach: <design の規約を対象 repository の現状へ当てはめる方針>",
            "どこへ・既存構造のどれを使うかを書く。",
            "design が答えた規約そのものは書かない",
            "`approach` は `design` の要約ではなく、`design` が答えない"
            "「どこへ・既存構造のどれを使うか」を担当する。",
            "要約にすると `design` と変更理由を共有し、写しが要約の粒度で残るためである。",
            "`plan.approach` は `design` の規約を対象 repository の現状へ当てはめる方針、",
            "規約本文は持たず、plan.design を正本として参照する",
            "規約本文の正本は plan.design。",
            "その充足を判定する観測可能な振る舞いだけを書く",
        )
        # #108 は、文を書き換えるときに同居する既存義務を巻き添えで落とす失敗を4件
        # 実測している。design の追記で書き換える3つの定義文が担っていた義務を個別に
        # 固定し、置換で消えたことを検出する。
        preserved = (
            "実装枝への分割はしない。AC を所有しない",
            "id: AC-1                    # 安定 ID。Branch Plan へそのまま引き継ぎ可能。振り直さない",
            "text: <観測可能な振る舞い>",
            "分割は `branch-design` の責務であり、`plan.steps` は起草者が実装の道筋を示す"
            "順序付き作業であって、AC を所有しない。",
        )
        for platform, text in self._schema_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required + preserved:
                    self.assertIn("".join(contract.split()), normalized)

    def test_draft_schema_reference_blocks_a_plan_that_has_no_design_body(self) -> None:
        """Block an empty design from reaching awaiting_review or approved."""
        design_missing_row = (
            "| `design-missing` | `plan.design` が未記載または空のまま "
            "`awaiting_review` 以降へ遷移している |"
        )
        # approved は blocking が空であることを前提にしているため、design-missing が
        # 立つ限り approved へ到達しない。この前提文が残ることで、遷移表へ design 専用の
        # 行を足さずに「design が空のまま approved にできない」が成立する。
        approved_precondition = (
            "approved:         承認済み。open_questions と validation.blocking が"
            "すべて空であることが前提"
        )
        for platform, text in self._schema_reference_texts().items():
            with self.subTest(platform=platform):
                self.assertIn(
                    "".join(approved_precondition.split()), "".join(text.split())
                )
                # 行が blocking violation code 節の中にあることまで固定する。design-missing が
                # validation.blocking に載ることが approved 到達不能の第一リンクであり、
                # 本文のどこかに同じ文字列があるだけではその連鎖は成立しない。
                violation_section = "".join(
                    "".join(
                        self._section_lines(text, "## blocking violation code")
                    ).split()
                )
                self.assertIn("".join(design_missing_row.split()), violation_section)

    def test_draft_schema_reference_keeps_restatement_detection_out_of_the_violation_codes(
        self,
    ) -> None:
        """Record why a restatement check cannot join the recomputable violation codes."""
        required = (
            "入力 Data から再計算できる検査だけで成り立つ",
            "意味判断であり、Data から再計算できない",
            "表全体の再計算可能性が壊れる",
            # 担い手は「起草手順とレビューの判定」の粒度に留める。どちらがどう担うかを
            # ここで書き切ると、後続で決める配分の選択肢を先に潰す。
            "再掲の抑止は起草手順とレビューの判定が担う",
        )
        for platform, text in self._schema_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_draft_schema_reference_keeps_the_branch_design_handoff_map_unchanged(
        self,
    ) -> None:
        """Keep the handoff rows as branch-design's input requirements, without design."""
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
            "`handoff-incomplete` と `design-missing` の検査対象が二重になり、"
            "1つの欠落に2つの code が立つ",
            # handoff-incomplete の必須 field 列挙も固定する。ここへ plan.design を足すと、
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
                self.assertNotIn("plan.design", "".join(table))
                # 表が別節へ丸ごと複製された場合は上の節 slice の行数固定だけでは検出できない
                # （複製先の別 slice には現れない）。文書全体で単一の表であることも併せて担保する。
                self.assertEqual(
                    normalized.count("|`plan.objective`|"),
                    1,
                    "the handoff map must stay a single table",
                )

    def test_plan_review_inputs_carry_the_design_body_to_both_reviewers(self) -> None:
        """Hand the design body to both plan reviewers along with the rest of the plan."""
        # 規約本文が design にある以上、入力列挙が design を欠くと、必須ゲートである
        # 過剰実装審査は通るのに審査対象の中心が reviewer へ渡らない。列挙はスキーマ本体の
        # 並び（objective -> design -> approach -> steps）に合わせる。
        # adversarial-review.md は正本参照（`実装プラン本体` とだけ書く）のままとし、
        # ここでは対象にしない。閉じた列挙だったのは他の3ファイル（本 reference と
        # 下記2 agent）だけであり、正本参照だった箇所へ列挙を新設すると写しが増える。
        reference_contract = (
            "実装プラン本体（`plan.objective` / `plan.design` / "
            "`plan.approach` / `plan.steps`）"
        )
        agent_contracts = {
            "over-engineering-reviewer": "（objective / design / approach / steps）",
            "plan-adversarial-reviewer": "実装プラン本体"
            "（objective / design / approach / steps）",
        }
        for name in ("overengineering-plan-review.md",):
            for platform, text in self._draft_reference_texts(name).items():
                with self.subTest(reference=name, platform=platform):
                    self.assertIn(
                        "".join(reference_contract.split()), "".join(text.split())
                    )
        for agent, contract in agent_contracts.items():
            with self.subTest(agent=agent):
                source = self._repository_text(Path("shared/agents") / f"{agent}.md")
                self.assertIn("".join(contract.split()), "".join(source.split()))

    def test_draft_skill_matches_confirmed_contract(self) -> None:
        """Separate plan approval from downstream work and keep drafting review-gated."""
        required = (
            "確認モードの既定は `review`",
            "`auto` はユーザーが明示した場合のみ",
            "`branch-design` を直接起動しない",
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


if __name__ == "__main__":
    unittest.main()
