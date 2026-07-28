"""Repository contracts for impl-lead Branch Plan intake."""

from __future__ import annotations

import unittest

from build_plugin_assets_test_support import (
    IMPL_LEAD_SKILL,
    GENERATED_MARKDOWN_WARNING,
    REPOSITORY_ROOT,
    RepositoryContractSupport,
    generated_skill_path,
    generated_skill_reference_path,
    shared_skill_path,
    shared_skill_reference_path,
)


INTAKE_REFERENCE = "branch-plan-intake.md"
PLAN_SCHEMA_REFERENCE = "branch-plan-schema.md"


class DelegateImplementationIntakeContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _assert_intake_reference_files_exist(self) -> None:
        paths = (
            shared_skill_reference_path(IMPL_LEAD_SKILL, INTAKE_REFERENCE),
            generated_skill_reference_path("claude", IMPL_LEAD_SKILL, INTAKE_REFERENCE),
            generated_skill_reference_path("codex", IMPL_LEAD_SKILL, INTAKE_REFERENCE),
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
                shared_skill_reference_path(IMPL_LEAD_SKILL, INTAKE_REFERENCE)
            ),
            "claude": self._repository_text(
                generated_skill_reference_path(
                    "claude", IMPL_LEAD_SKILL, INTAKE_REFERENCE
                )
            ),
            "codex": self._repository_text(
                generated_skill_reference_path(
                    "codex", IMPL_LEAD_SKILL, INTAKE_REFERENCE
                )
            ),
        }

    def _delegate_skill_texts(self) -> dict[str, str]:
        return {
            "source": self._repository_text(shared_skill_path(IMPL_LEAD_SKILL)),
            "claude": self._repository_text(
                generated_skill_path("claude", IMPL_LEAD_SKILL)
            ),
            "codex": self._repository_text(
                generated_skill_path("codex", IMPL_LEAD_SKILL)
            ),
        }

    def _delegate_reference_texts(self, name: str) -> dict[str, str]:
        return {
            "source": self._repository_text(
                shared_skill_reference_path(IMPL_LEAD_SKILL, name)
            ),
            "claude": self._repository_text(
                generated_skill_reference_path("claude", IMPL_LEAD_SKILL, name)
            ),
            "codex": self._repository_text(
                generated_skill_reference_path("codex", IMPL_LEAD_SKILL, name)
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
            "`branch-design` の使用を",
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
            "../../branch-design/references/branch-plan-schema.md"
        )
        intake_paths = {
            "source": shared_skill_reference_path(IMPL_LEAD_SKILL, INTAKE_REFERENCE),
            "claude": generated_skill_reference_path(
                "claude", IMPL_LEAD_SKILL, INTAKE_REFERENCE
            ),
            "codex": generated_skill_reference_path(
                "codex", IMPL_LEAD_SKILL, INTAKE_REFERENCE
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


if __name__ == "__main__":
    unittest.main()
