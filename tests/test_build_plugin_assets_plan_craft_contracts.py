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
