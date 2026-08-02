"""Repository contracts for branch-design."""

from __future__ import annotations

import itertools
import re
import unittest

from build_plugin_assets_test_support import (
    GENERATED_MARKDOWN_WARNING,
    RepositoryContractSupport,
    generated_skill_path,
    generated_skill_reference_path,
    shared_skill_path,
    shared_skill_reference_path,
)


BRANCH_DESIGN_SKILL = "branch-design"
PLAN_SCHEMA_REFERENCE = "branch-plan-schema.md"
PLAN_REFERENCE_NAMES = (
    "branch-plan-schema.md",
    "branch-splitting.md",
    "plan-review.md",
)

# Set は状態を持たない。status / approval / delegation / 完了判定を Set 直下へ足すと、
# Branch Plan 単位の受け入れ判断と二重管理になるため、この並びを増やすときは
# 状態を持ち込んでいないかを確認する。
# 集合ではなく順序まで固定するのは、YAML の並びを読み手が層の対応表として読むためで、
# どの field がどの層に属するかは並びの見た目から復元される。並び自体を契約に含める。
# violation code 表を assertCountEqual にしているのは、表の行順が読み手向けの並びでしかなく、
# code と帰属の対応だけが契約だからで、扱いの違いはこの「並び自体が契約かどうか」に対応する。
SET_LEVEL_FIELDS = (
    "implementation_plan",
    "acceptance_criteria",
    "order",
    "decision",
    "validation",
    "branch_plans",
)
BRANCH_PLAN_FIELDS = (
    "id",
    "status",
    "confirmation_mode",
    "approval",
    "delegation",
    "unresolved_decisions",
    "assumptions",
    "shared_foundation",
    "branches",
    "execution",
    "delegation_mode_proposal",
    "decision",
    "override",
    "validation",
)

# 帰属は「どの層の Data を見れば再計算できるか」を表す。`Set` の5件は複数 Branch Plan に
# またがる Data がないと判定できず、Branch Plan 単体で検査すると正当な分割で誤検知する。
VIOLATION_CODE_ATTRIBUTIONS = (
    ("duplicate-id", "Set"),
    ("unknown-reference", "Set"),
    ("cross-plan-dependency", "Set"),
    ("ac-unassigned", "Set"),
    ("ac-duplicate-primary", "Set"),
    ("execution-order-invalid", "両方"),
    ("branch-without-primary-ac", "Branch Plan"),
    ("dependency-cycle", "Branch Plan"),
    ("scope-conflict", "Branch Plan"),
    ("tests-missing", "Branch Plan"),
    ("branch-assessment-missing", "Branch Plan"),
    ("branch-assessment-invalid", "Branch Plan"),
    ("legacy-risk-present", "Branch Plan"),
    ("legacy-stages-present", "Branch Plan"),
    ("branch-contract-violation", "Branch Plan"),
    ("state-invalid", "Branch Plan"),
    ("approval-invalid", "Branch Plan"),
    ("delegation-invalid", "Branch Plan"),
    ("mode-proposal-invalid", "Branch Plan"),
)

STAGE_FIELD_NAMES = ("implementation_stages", "stage_tests", "stages_reason")


class PlanImplementationBranchesContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _plan_skill_texts(self) -> dict[str, str]:
        return {
            "source": self._repository_text(shared_skill_path(BRANCH_DESIGN_SKILL)),
            "claude": self._repository_text(
                generated_skill_path("claude", BRANCH_DESIGN_SKILL)
            ),
            "codex": self._repository_text(
                generated_skill_path("codex", BRANCH_DESIGN_SKILL)
            ),
        }

    def _plan_reference_texts(self, name: str) -> dict[str, str]:
        return {
            "source": self._repository_text(
                shared_skill_reference_path(BRANCH_DESIGN_SKILL, name)
            ),
            "claude": self._repository_text(
                generated_skill_reference_path("claude", BRANCH_DESIGN_SKILL, name)
            ),
            "codex": self._repository_text(
                generated_skill_reference_path("codex", BRANCH_DESIGN_SKILL, name)
            ),
        }

    def test_plan_skill_exposes_platform_frontmatter_and_reference_links(
        self,
    ) -> None:
        """Expose planning frontmatter and route each detail to its reference."""
        for platform in ("claude", "codex"):
            main = self._plan_skill_texts()[platform]
            with self.subTest(platform=platform):
                self.assertTrue(main.startswith(f"---\nname: {BRANCH_DESIGN_SKILL}\n"))
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
            "| code | 帰属 | 検査内容 |",
            "duplicate-id",
            "unknown-reference",
            "branch-without-primary-ac",
            "delegation-invalid",
            "mode-proposal-invalid",
            "## 状態遷移と権限",
            "- tests の意味",
            "## tests の意味",
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

    def _schema_block(self, text: str) -> str:
        return text.split("```yaml", 1)[1].split("\n```", 1)[0]

    def _violation_code_table(self, text: str) -> tuple[list[str], ...]:
        section = text.split("## blocking violation code", 1)[1].split("\n## ", 1)[0]
        lines = section.splitlines()
        # この節は状態組み合わせ表・delegation 表・出力条件表も持つため、最初の表だけを取る。
        first_row = next(index for index, line in enumerate(lines) if line.startswith("|"))
        block = itertools.takewhile(
            lambda line: line.startswith("|"), lines[first_row:]
        )
        return tuple(
            [cell.strip() for cell in line.strip().strip("|").split("|")]
            for line in block
        )

    def _assert_carries(self, contract: str, text: str) -> None:
        self.assertTrue(
            "".join(contract.split()) in "".join(text.split()),
            f"契約文が原稿に存在しない: {contract}",
        )

    def test_plan_schema_nests_branch_plans_under_a_stateless_set(self) -> None:
        """Hold the plan-wide inputs on a stateless set and every state on each plan."""
        for platform, text in self._plan_reference_texts(PLAN_SCHEMA_REFERENCE).items():
            with self.subTest(platform=platform):
                block = self._schema_block(text)
                self.assertEqual(
                    SET_LEVEL_FIELDS,
                    tuple(re.findall(r"^([a-z_]+):", block, re.M)),
                )
                plans = block.split("\nbranch_plans:", 1)[1]
                fields = tuple(
                    match.group(1)
                    for match in (
                        re.match(r"^(?:  - |    )([a-z_]+):", line)
                        for line in plans.splitlines()
                    )
                    if match is not None
                )
                self.assertEqual(BRANCH_PLAN_FIELDS, fields)

    def test_plan_schema_attributes_every_violation_code_to_its_layer(self) -> None:
        """Name the layer that recalculates each violation code."""
        for platform, text in self._plan_reference_texts(PLAN_SCHEMA_REFERENCE).items():
            with self.subTest(platform=platform):
                table = self._violation_code_table(text)
                self.assertEqual(["code", "帰属", "検査内容"], table[0])
                rows = table[2:]
                self.assertCountEqual(
                    VIOLATION_CODE_ATTRIBUTIONS,
                    tuple((row[0].strip("`"), row[1]) for row in rows),
                )
                attributions = {row[0].strip("`"): row[1] for row in rows}
                self.assertEqual(
                    5,
                    sum(1 for layer in attributions.values() if layer == "Set"),
                )
                self.assertEqual(
                    ("execution-order-invalid",),
                    tuple(
                        code
                        for code, layer in attributions.items()
                        if layer == "両方"
                    ),
                )
                duplicate_id = next(
                    row[2] for row in rows if row[0].strip("`") == "duplicate-id"
                )
                self.assertIn("Branch Plan id", duplicate_id)
                self.assertIn("branch id", duplicate_id)
                self.assertIn("AC id", duplicate_id)
                self.assertNotIn("stage", duplicate_id)

    def test_plan_schema_scopes_reference_resolution_across_the_set(self) -> None:
        """Resolve AC references set-wide and branch references inside one plan."""
        required = (
            "AC id 参照(`covers_acceptance_criteria` / `verifies_acceptance_criteria` / "
            "`unresolved_decisions.affects` の `ac-assignment` / `ac-derivation`)は "
            "Set の `acceptance_criteria` 全域で解決する。",
            "branch id 参照(`depends_on` / `execution.order` / "
            "`unresolved_decisions.affects` の `branch`)は、その参照を持つ Branch Plan 内の "
            "`branches[].id` だけで解決する。",
            "Set の `order` の要素は `branch_plans[].id` で解決する。",
            "同一 Branch Plan 内で解決できず、かつ Set 全域の branch id には存在する",
            "Set 全域にも存在しない場合は `unknown-reference` とする。",
        )
        for platform, text in self._plan_reference_texts(PLAN_SCHEMA_REFERENCE).items():
            with self.subTest(platform=platform):
                for contract in required:
                    self._assert_carries(contract, text)

    def test_plan_schema_blocks_every_branch_plan_on_a_set_level_violation(self) -> None:
        """Carry a set-level violation into every plan without contradicting its state."""
        required = (
            "Set の `validation.blocking` が非空である間、planning Skill は"
            "全 Branch Plan を `blocked` にする。",
            "その Branch Plan の `unresolved_decisions` または `validation.blocking` が非空、"
            "あるいは Set の `validation.blocking` が非空",
            "有効な組み合わせ表と `state-invalid` の再計算は拡張後の定義を使い、"
            "自身の2 field が空のまま `blocked` である Branch Plan を矛盾として扱わない。",
            "Executor は Set 全体の検査を先に行い、非空なら Branch Plan 側の状態に関わらず"
            "実行を開始しない。",
            # 同じ規則を散文・状態遷移表・スキーマ本体のコメントへ重複して書いているため、
            # 一部だけを固定すると、残りを旧文言へ戻した原稿が自己矛盾したまま通る。原稿にある
            # 14記載(散文5項目・遷移表5行・スキーマ本体のコメント4行)をすべて固定する。
            # 原稿へ記載を足すときは、ここへも足す。
            "# blocked:          「blocking violation code」の節が定める blocked の定義に従う",
            "# awaiting_review:  confirmation_mode: review で Set と自身に blocking なし。"
            "ユーザー承認待ち",
            "# approved:         承認済み。Set と自身の blocking がすべて空であることが前提",
            "| (生成) → `blocked` | planning Skill | 自身の `unresolved_decisions` または "
            "`validation.blocking`、あるいは Set の `validation.blocking` が非空 |",
            "| (生成) → `awaiting_review` | planning Skill | `confirmation_mode: review` かつ "
            "Set と自身に blocking なし |",
            "| (生成) → `approved` (`method: auto`) | planning Skill | "
            "`confirmation_mode: auto` かつ Set と自身に blocking なし |",
            "| `blocked` → `awaiting_review` | planning Skill(再実行) | 原因解消後に全 "
            "validation を再実行して Set と自身に blocking なし、`confirmation_mode: review` |",
            "Set または自身に blocking violation が残る場合は承認操作があっても遷移しない",
            "Set の `validation.blocking` は `state-invalid` の入力にしない。Set 由来の "
            "`blocked` は Set 層の検査と Executor の先行検査で表し、Branch Plan 側では"
            "再判定しない。",
            "# violation の配列。1件でもあれば全 Branch Plan が status: blocked",
        )
        for platform, text in self._plan_reference_texts(PLAN_SCHEMA_REFERENCE).items():
            with self.subTest(platform=platform):
                for contract in required:
                    self._assert_carries(contract, text)

    def test_plan_schema_drops_stage_fields_except_the_legacy_detection_rule(
        self,
    ) -> None:
        """Keep stage vocabulary only in the rule that detects it as a legacy field."""
        # 検査規則の行だけは廃止 field 名を残す。名前を消すと legacy-stages-present が
        # 何を検出するのかを原稿から復元できなくなるため。
        for platform, text in self._plan_reference_texts(PLAN_SCHEMA_REFERENCE).items():
            with self.subTest(platform=platform):
                self.assertFalse(
                    "stages-invalid" in text,
                    "廃止した `stages-invalid` が残っている",
                )
                carrying = [
                    line
                    for line in text.splitlines()
                    if any(name in line for name in STAGE_FIELD_NAMES)
                ]
                self.assertNotEqual(
                    [],
                    carrying,
                    "legacy-stages-present の検査規則行が見つからない",
                )
                for line in carrying:
                    self.assertTrue(
                        line.startswith("| `legacy-stages-present` |"),
                        f"廃止 field 名が検査規則行の外に残っている: {line}",
                    )
                for name in STAGE_FIELD_NAMES:
                    self.assertIn(name, carrying[0])

    def test_plan_schema_reference_points_terminology_to_the_implementation_branches_glossary(
        self,
    ) -> None:
        """Route branch terminology to the impl-lead glossary, not a local copy."""
        required = (
            "用語",
            "impl-lead",
            "../../impl-lead/references/implementation-branches.md",
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
            "`impl-lead` を直接起動しない",
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
            "[issue #68](https://github.com/akitanabe/tugite/issues/68)",
            "policy: fixed | adaptive",
            "baseline: lite | standard | strict",
            "mode 未指定の明示的な委譲要求は null のまま保持し、"
            "Executor が {adaptive, standard} を採用する。",
            "`{adaptive, lite}` と `{fixed, standard}` は入力語彙が存在しないため無効とし、"
            "表に含めない。",
            "`baseline` を `lite` にすると low complexity 枝の割り当て先が `lite` しかなく導出が"
            "恒等写像になり、`medium` 以上を引き上げる用途は `{adaptive, standard}` と"
            "同一になるため、独立した配分方針として意味を持たない。",
            "`{fixed, standard}` は全枝固定を明示する入力語彙が存在しないため到達できない。"
            "仮に語彙を足しても `{adaptive, standard}` は low complexity 枝だけを `lite` に落とし"
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

    def test_plan_schema_derives_branch_mode_only_from_implementation_complexity(
        self,
    ) -> None:
        """Keep implementation complexity as the only source for derived mode."""
        required = (
            "枝ごとの委譲 mode は schema に持たせず、"
            "`branches[].implementation_complexity` を正として導出する。",
            "枝側に `recommended_mode` を置くと `implementation_complexity` と二重管理になり、"
            "矛盾したときに"
            "どちらを正とするか決められないため。",
            "AC 割り当てを枝側の一方向参照へ正規化したのと同じ理由である。",
            "導出した枝 mode は Branch Plan へ書き戻さず、実行 Data として保持して"
            "最終報告で報告する。",
            "mode の判定理由は `implementation_complexity.reasons` に書き、"
            "mode ごとの理由欄を別に設けない。",
        )
        for platform, text in self._plan_reference_texts(
            PLAN_SCHEMA_REFERENCE
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_schema_limits_fixed_lite_proposal_to_failure_impact(self) -> None:
        """Use failure impact only for a fixed-lite safety proposal."""
        required = (
            "propose:",
            "policy: adaptive",
            "baseline: standard | strict",
            "`policy: adaptive` では枝の `implementation_complexity.level` から mode を導出する。",
            "`failure_impact` は adaptive mode の直接導出には使わない。",
            "提案が必要なのは `{fixed, lite}` が枝の `failure_impact` と整合しない場合だけである。",
            "`{fixed, strict}` に対して降格を提案しない。",
            "引き上げだけを提案する非対称性は、コストの削減より品質の担保を優先する"
            "判断であり、low failure impact 枝から `lite` を提案しないのと同じ理由である。",
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
            "`failure_impact.level` からの再計算(出力条件表)と一致しない",
            "必要時の欠落、不要時の出力、表と異なる `{policy, baseline}` の提案",
        )
        for platform, text in self._plan_reference_texts(
            PLAN_SCHEMA_REFERENCE
        ).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required + proposal_rows + violation_recalculation:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_splitting_reference_defines_independent_impact_and_complexity_criteria(
        self,
    ) -> None:
        """Assess failure impact and implementation complexity independently."""
        impact_contracts = (
            "1. 失敗時の影響範囲",
            "2. 変更の可逆性 / 切り戻しの容易さ",
            "3. 外部副作用の有無と数",
            "4. セキュリティ・権限への影響",
            "5. データ整合性への影響",
            "6. 後方互換性への影響",
            "| `low` | 表示文言のみの変更、設定値の追加、振る舞いに影響しないリネーム、局所的な機械的修正。外部副作用がなく、容易に切り戻せる。 |",
            "| `medium` | 通常の機能追加、既存ロジックの変更、API 内部処理の変更、UI とバックエンドの通常連携。テストで十分に担保でき、失敗時の影響が限定的。 |",
            "| `high` | 認証・認可・権限判定、データ削除・上書き・移行、外部 API の契約変更、後方互換性への影響、決済・請求・金額計算、機密情報への影響、複数の外部 I/O。失敗時の影響が広い、または切り戻しが困難。 |",
            "変更量が1行でも、権限判定やデータ削除条件に関わる場合は `high` とする。",
            "判定に使った観点は `failure_impact.reasons` に記録する。",
        )
        complexity_contracts = (
            "1. 仕様の明確さ",
            "2. 適用できる既存 pattern の有無",
            "3. component 間の責務・契約に残る判断",
            "4. 依存関係の複雑性",
            "5. 調査・仮説検証の必要性",
            "| `low` | 仕様と依存契約が明確で、既存 pattern の定型適用として実装でき、調査や設計判断がほぼ残らない。 |",
            "| `medium` | 通常の機能追加や既存ロジック変更で、限定された責務・契約判断または仮説検証が残る。 |",
            "| `high` | 仕様や責務境界に重要な判断が残る、非自明な algorithm・concurrency を含む、または複数の仮説を調査・検証する必要がある。 |",
            "判定に使った観点は `implementation_complexity.reasons` に記録する。",
            "決定表をここに再掲しない。",
        )
        for platform, text in self._plan_reference_texts("branch-splitting.md").items():
            with self.subTest(platform=platform):
                impact = text.split("## failure_impact.level の判定観点", 1)[1].split(
                    "## implementation_complexity.level の判定観点", 1
                )[0]
                complexity = text.split(
                    "## implementation_complexity.level の判定観点", 1
                )[1].split("\n## ", 1)[0]
                normalized_impact = "".join(impact.split())
                normalized_complexity = "".join(complexity.split())
                for contract in impact_contracts:
                    self.assertIn("".join(contract.split()), normalized_impact)
                    self.assertNotIn("".join(contract.split()), normalized_complexity)
                for contract in complexity_contracts:
                    self.assertIn("".join(contract.split()), normalized_complexity)
                    self.assertNotIn("".join(contract.split()), normalized_impact)

    def test_plan_schema_requires_and_validates_both_branch_assessment_axes(
        self,
    ) -> None:
        """Block missing, malformed, empty, and legacy branch assessments."""
        required = (
            "failure_impact:",
            "implementation_complexity:",
            "level: low | medium | high",
            "reasons: [<1件以上の具体的な理由>]",
            "branch-assessment-missing",
            "branch-assessment-invalid",
            "legacy-risk-present",
            "`reasons` の欠落、配列以外、空配列、空文字、非文字列要素",
            "旧 `risk` が単独で存在する場合",
            "旧 `risk` が新しい field と混在する場合",
            "旧 `risk` から新しい2軸を推測しない",
        )
        for platform, text in self._plan_reference_texts(PLAN_SCHEMA_REFERENCE).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_splitting_reference_separates_dependency_and_scope_signals(
        self,
    ) -> None:
        """Separate propagation impact from residual implementation judgment."""
        required = (
            "依存 edge があることだけでは level を上げない。",
            "失敗伝播、部分成功、rollback への影響は `failure_impact` で評価する。",
            "依存先との契約に残る判断は `implementation_complexity` で評価する。",
            "確定済み依存の定型適用では `implementation_complexity` を上げない。",
            "ファイル数、変更量、単なる module 波及だけでは "
            "`implementation_complexity` を上げない。",
        )
        for platform, text in self._plan_reference_texts("branch-splitting.md").items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_schema_keeps_complexity_out_of_branch_contract_violations(
        self,
    ) -> None:
        """Judge branch validity by acceptance boundaries, not complexity level."""
        required = (
            "`implementation_complexity.level: high` だけでは "
            "`branch-contract-violation` にしない。",
            "単独の Acceptance Criteria・検証・受け入れ判断・revert が閉じない場合だけ",
        )
        for platform, text in self._plan_reference_texts(PLAN_SCHEMA_REFERENCE).items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_skill_takes_inventory_findings_only_for_user_listed_ids(
        self,
    ) -> None:
        """Accept inventory findings as a source plan only for explicitly listed finding IDs."""
        required = (
            "元プラン(`plan-craft` のプラン文書 `.tugite/plans/<slug>.md` / path / "
            "issue URL / 会話内 / `test-audit` の Test Inventory 報告の findings)",
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

    def test_plan_skill_reads_the_plan_document_sections_without_renumbering_ids(
        self,
    ) -> None:
        """Take AC wording from the plan document and keep the ids it already carries."""
        # AC id を振り直すと、プラン文書の AC を参照する指摘台帳や issue の記載が
        # Branch Plan 側の id と食い違い、どの AC を指すのかを追えなくなる。
        required = (
            "`plan-craft` のプラン文書を元プランにする場合は、"
            "「Acceptance Criteria」節から AC 原文を取る。",
            "文書が持つ AC id はそのまま引き継ぎ、振り直さない。",
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
                    "[起草手順](../../plan-craft/references/plan-drafting.md)",
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


if __name__ == "__main__":
    unittest.main()
