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
            # 数えるのは規則そのものを再掲する文だけとし、規則の成立根拠を述べる文と、他 Skill へ
            # 正本を委譲する文は数えない。
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

    def test_plan_splitting_reference_leads_with_the_two_layer_order_and_the_split_section(
        self,
    ) -> None:
        """State the two-layer split order up front and read Set-layer criteria first."""
        # R-1/WP-3: 読み手が Set 層の質的基準を実装枝分割の追加基準として誤読しないよう、
        # 冒頭リード文で2層構成と判断順序(Set 層 → 実装枝層)を宣言し、節の登場順も
        # SKILL.md の全体の流れ(Branch Plan 分割 → 実装枝分割)に合わせる。
        for platform, text in self._plan_reference_texts("branch-splitting.md").items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                self.assertIn(
                    "".join(
                        "この file は Branch Plan Set への分割と実装枝への分割という"
                        "2層の基準を扱い、判断の順序は Set 層 → 実装枝層である。".split()
                    ),
                    normalized,
                )
                toc_section = text.split("## 目次", 1)[1].split("## ", 1)[0]
                self.assertLess(
                    toc_section.index("Branch Plan へ分割する判断基準"),
                    toc_section.index("第一基準と優先順位"),
                )
                self.assertLess(
                    text.index("## Branch Plan へ分割する判断基準"),
                    text.index("## 第一基準と優先順位"),
                )

    def test_plan_splitting_reference_states_qualitative_branch_plan_split_criteria(
        self,
    ) -> None:
        """Judge Branch Plan splits by change-purpose independence, not a fixed branch count."""
        # F-3: AC-7 は「質的基準」がどの節にあるかを問うため、文書全体ではなく
        # 「Branch Plan へ分割する判断基準」節に絞って検査する。
        required = (
            "質的基準とし、枝数の固定閾値も新しい blocking code も設けない。",
            "**分割する** — 独立した変更目的が複数あり、一方を実行して他方を実行しない選択が"
            "成立する。",
            "**分割する** — 先行部分の完了後に、後続の設計を見直す余地がある(学習が起きる境界)。",
            "**分割しない** — 全枝が1つの変更目的に属し、一部だけ受け入れる選択が成立しない。",
            "分割しない場合は Set の `decision.split: false` と理由の",
            "記録を必須とする。実装枝の `decision` と同型の機構であり、新しい形式を導入しない。",
        )
        for platform, text in self._plan_reference_texts("branch-splitting.md").items():
            with self.subTest(platform=platform):
                section = text.split("## Branch Plan へ分割する判断基準", 1)[1].split(
                    "\n## ", 1
                )[0]
                normalized = "".join(section.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_splitting_reference_scopes_the_cross_plan_scope_sentence_to_its_section(
        self,
    ) -> None:
        """Keep the same-Branch-Plan-scope sentence inside the shared_foundation section."""
        # F-3: AC-7 は「shared_foundation の判定節に」と節を指定しているため、
        # 文書全体ではなく `## shared_foundation の判定` 節に絞って検査する。
        required = (
            "宣言条件にある「複数の枝」は、同一 Branch Plan 内の複数の枝を指す。",
            "土台を必要とする枝が Branch Plan をまたぐ場合は、先行 Branch Plan が土台を"
            "作った結果が",
            "基準 commit に入るため、後続 Branch Plan では `shared_foundation.required: false` "
            "とする。",
            "同じ土台を複数の Branch Plan で重複宣言しない。",
        )
        for platform, text in self._plan_reference_texts("branch-splitting.md").items():
            with self.subTest(platform=platform):
                # T-1: 他の節スコープ検査(states_qualitative / names_the_branch_plan_layer)と
                # 同じく `.split("\n## ", 1)[0]` で上限を付ける。`shared_foundation の判定` は
                # 現状最後の節だが、上限がないと文末新設節への移動や見出しレベルの降格を
                # substring 一致のまま見逃す。
                section = text.split("## shared_foundation の判定", 1)[1].split(
                    "\n## ", 1
                )[0]
                normalized = "".join(section.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_splitting_reference_names_the_branch_plan_layer_for_decision_and_override(
        self,
    ) -> None:
        """Name the Branch Plan layer for decision/override now that Set carries a decision too."""
        # R-5: 同 file に Set 層の `decision` が入ったため、「1枝にまとめる判断」節の裸の
        # `decision` / `override` を層明示に揃える。`override` の記録先の正本は
        # plan-review.md の「確認操作」節への参照で示す。
        required = (
            "分割しない場合は Branch Plan の `decision.split: false` を出力し",
            "ユーザーが実装枝の統合を",
            "指示した場合は、記録先の正本である",
            "の「確認操作」節に従い",
            "`override` にその理由を記録する。",
        )
        for platform, text in self._plan_reference_texts("branch-splitting.md").items():
            with self.subTest(platform=platform):
                section = text.split("## 1枝にまとめる判断", 1)[1].split("\n## ", 1)[0]
                normalized = "".join(section.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)
                self.assertIn("plan-review.md", section)

    def test_plan_review_presents_the_set_order_and_layers_the_confirmation_operations(
        self,
    ) -> None:
        """Present the set order and per-plan summary, naming each operation's owning layer."""
        required = (
            "提示の分岐は Set 全体で決める。",
            "Branch Plan が1件でも `blocked` であれば、`blocked` の提示を行う。この状態では"
            "承認操作を求めない。",
            "全 Branch Plan が同じ `status` のときは、その `status` の提示を行う。",
            "Set の `order` を要約表の前に示し、Branch Plan の実行順序を明示する。",
            # F-1: 要約表と提示の順序が Branch Plan 単位になったという記載を固定する。
            # これがないと「Branch Plan ごとに」「その Branch Plan の」を削り Set 全体で
            # 1枚の要約表という旧文へ戻す変異が Green になる。
            "続けて、YAML 全文の前に、Branch Plan ごとに次の列を持つ要約表を表示する。",
            "実行順は、その Branch Plan の `execution.order` の順序に一致させる。",
            "Set の `order` と Branch Plan ごとの要約表 → 確認操作 →",
            "自動承認した記録として Set の `order` と要約表、",
            # T-3: RB-2 の混在時付記(「shared_foundation.required: true の注記と同じ
            # 置き方で」)が参照する正本文そのものを固定する。これがないと、正本文を
            # 旧文(「該当する Branch Plan の」を欠いた「共有土台として表の前に明示する」)へ
            # 差し戻す変異で、RB-2 の付記が指す対象が消えて2文が矛盾したまま Green になる。
            "`shared_foundation.required: true` の場合は、親が委譲前に実装する共有土台として、"
            "該当する Branch Plan の表の前に明示する。",
            # R-2/RB-1: 「この分割で実行」の記録先を明示する。無条件に「各 Branch Plan」へ
            # 記録すると、混在 confirmation_mode の Set で既に approved(auto) の Branch Plan を
            # 上書きし approval-invalid を誘発するため、awaiting_review の Branch Plan だけを
            # 対象にする限定を固定する。
            "この分割で実行 — Set 全体の承認を意味する。`status: awaiting_review` の Branch Plan"
            "について",
            "`approval.method: user` と `status: approved` を記録し、すでに "
            "`approved`(`method: auto`) の Branch Plan は変更しない。Set 層に承認状態は"
            "持たない。",
            # RB-4: 遷移条件と実行主体の正本(branch-plan-schema.md の「状態遷移と権限」)を
            # 参照する1句を固定する。R-5 の override 修正と同じ「正本参照」の形に揃える。
            "遷移条件と実行主体は [Branch Plan Set 正規スキーマ](branch-plan-schema.md) の"
            "「状態遷移と権限」に従う。",
            # RB-3: 「分割を修正」から抜け落ちていた AC 割り当ての反映先を戻す。
            "分割を修正 — Branch Plan への分割(Set の `branch_plans` の分け方や `order`)か、"
            "実装枝への分割(Branch Plan 内の `branches` の分け方)か、どちらの層の修正かを"
            "ユーザーが示す。AC 割り当ての修正は枝の `covers_acceptance_criteria` へ反映する。",
            # R-3/WP-1: 「分割せず1枝で実行」が層をまたいだ場合の帰結を明示する。
            "分割せず1枝で実行 — 実装枝の統合を意味する。対象が単一の Branch Plan 内の枝なら、"
            "記録先は現行どおりその Branch Plan の `override.merge_branches` とする。",
            "対象が `branch_plans` が2件以上ある Set 全体(Branch Plan を1件へまとめる指示)"
            "なら、Set を1件へ畳む指示として扱い、Set の `decision.split: false` と、"
            "統合後の Branch Plan の `override.merge_branches` の両方を記録し、"
            "Branch Plan Set を再生成する。",
            "`override` を Set 層へ増やさない。",
        )
        for platform, text in self._plan_reference_texts("plan-review.md").items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_review_defines_the_mixed_status_presentation(self) -> None:
        """Define the presentation when non-blocked Branch Plans disagree on status."""
        # R-4/WP-2: 「全 Branch Plan が同じ status のときは、その status の提示を行う」が
        # blocked 0件かつ status が揃わない場合(awaiting_review と approved(auto) の混在)を
        # 未定義のまま残していた。confirmation_mode は Branch Plan ごとの field で schema 上
        # 混在しうるため、(a) 混在時の提示を定義する側を選んだ(不変条件を捏造しない)。
        required = (
            "`blocked` が0件で `status` が揃わない場合(`awaiting_review` と "
            "`approved`(`method: auto`) の混在)は、承認操作を求める側の `awaiting_review` "
            "の提示に寄せる。",
            # RB-2: 要約表の行は実装枝単位で Branch Plan 単位の列を持たないため、付記の
            # 置き場所を shared_foundation の注記と同じ「該当する Branch Plan の表の前に」へ
            # 揃える。
            "`approved`(`method: auto`) の Branch Plan は、`shared_foundation.required: true` "
            "の注記と同じ置き方で、該当する Branch Plan の表の前に `confirmation_mode: auto` "
            "により自動承認済みである旨を付記する。",
        )
        for platform, text in self._plan_reference_texts("plan-review.md").items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_review_presents_set_level_blocking_before_branch_plan_detail(
        self,
    ) -> None:
        """Surface a set-wide violation before any per-branch-plan blocking detail."""
        required = (
            "Branch Plan Set 内に `status: blocked` の Branch Plan が1件でもあれば、"
            "承認操作を求めず、原因の解消を依頼する。",
            # RB-5: 「Set の違反が全 Branch Plan を blocked にする」の導出規則は
            # branch-plan-schema.md の「状態遷移と権限」が正本。この節は「先に提示する」という
            # 提示層固有の情報だけを残し、導出規則は正本参照へ寄せる。
            "Set の `validation.blocking` が非空の場合は、これを先に提示する。Set の違反が全"
            "Branch Plan を `blocked` にすることは "
            "[Branch Plan Set 正規スキーマ](branch-plan-schema.md) の「状態遷移と権限」による。",
            "各 blocked な Branch Plan について、`unresolved_decisions` は `question` と "
            "`affects` を対応付けて提示し",
        )
        for platform, text in self._plan_reference_texts("plan-review.md").items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_plan_skill_describes_its_output_as_a_branch_plan_set(self) -> None:
        """Describe the skill's output as a Branch Plan Set and drop the data-only claim."""
        # F-2: source(shared/skill/branch-design/SKILL.md)は人が実際に編集する正本であり、
        # claude/codex の生成物だけを検査すると shared 側の書き戻しを検出できない。
        # test_plan_skill_matches_confirmed_schema_contract と同じく3 platform を検査する。
        for platform, main in self._plan_skill_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(main.split())
                self.assertIn(
                    "".join("Branch Plan Set へ変換する planning skill。".split()),
                    normalized,
                )
                self.assertIn(
                    "".join(
                        "Branch Plan Set を返すだけで、委譲開始権限は含まない。".split()
                    ),
                    normalized,
                )
                self.assertIn("".join("出力は Branch Plan Set だけである".split()), normalized)
                self.assertNotIn("".join("Branch Plan Data".split()), normalized)

    def test_plan_skill_uses_the_set_term_for_the_approval_sentence(self) -> None:
        """Match plan-review.md's set-level approval phrasing instead of the bare Branch Plan noun."""
        # R-5: plan-review.md はすでに「承認は Branch Plan Set の確定だけを意味する。」に
        # 揃っている。SKILL.md 側の同義文が「Branch Plan」の裸のままだと、2 file 間で
        # 承認対象の呼称が食い違う。
        # T-2: この file の他の契約検査はすべて "".join(text.split()) で空白を正規化してから
        # 比較しており、80桁前後で折り返す原稿の運用上、意味を変えない改行位置の変更で
        # 無関係に落ちないようにしている。ここも揃える。
        for platform, main in self._plan_skill_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(main.split())
                self.assertIn(
                    "".join("承認は Branch Plan Set の確定だけを意味する。".split()),
                    normalized,
                )

    def test_plan_skill_flow_adds_a_branch_plan_split_step_before_branch_splitting(
        self,
    ) -> None:
        """Add Branch Plan splitting as a numbered flow step ahead of branch splitting."""
        # F-2: ここも source を含む3 platform を検査する。
        # F-3: AC-18 は「全体の流れ」に手順として現れることを求めるため、`## 全体の流れ`
        # 節に絞って検査し、番号付き手順であることも regex で確認する。
        required_in_flow = (
            "「Branch Plan へ分割する判断基準」に従い、",
            "独立した変更目的が複数あるか、先行部分の完了後に後続の設計を見直す余地があるかを"
            "判断し、Branch Plan Set を分ける。分割しない場合は Set の `decision.split: false` と"
            "理由を記録する。",
            "Set の `validation.blocking`、各 Branch Plan の `unresolved_decisions` と "
            "`validation.blocking` から `status` を決める。",
        )
        for platform, main in self._plan_skill_texts().items():
            with self.subTest(platform=platform):
                flow = main.split("## 全体の流れ", 1)[1].split("\n## ", 1)[0]
                normalized_flow = "".join(flow.split())
                for contract in required_in_flow:
                    self.assertIn("".join(contract.split()), normalized_flow)
                self.assertRegex(
                    flow,
                    r"\n\d+\.\s*\[枝分割判断\]\(references/branch-splitting\.md\) の"
                    r"「Branch Plan へ分割する判断基準」",
                )
                split_step_marker = "".join(
                    "Branch Plan へ分割する判断基準」に従い、".split()
                )
                branch_step_marker = "".join(
                    "外部から観測可能な振る舞いの縦割りで実装枝へ分ける。".split()
                )
                self.assertLess(
                    normalized_flow.index(split_step_marker),
                    normalized_flow.index(branch_step_marker),
                )

    def test_branch_design_surface_docs_drop_all_stage_vocabulary(self) -> None:
        """Leave no trace of the retired implementation_stages mechanism in these docs."""
        # implementation_stages / stage_tests / stages_reason に加え、廃止 field 名を含まない
        # stage 概念の散文(「stage は AC を所有しない」等)や目次項目も検出できるよう、
        # 生の "stage" 部分文字列(大小無視)の不在を検査する。これが崩れると、廃止語だけを
        # 消して概念の散文が残る不完全な削除を見逃す。
        # F-4: 検出は Latin 表記の "stage" 部分文字列に閉じる。この3 file の原稿は stage
        # 概念を Latin 表記(implementation_stages 等)でしか表現していなかったため、
        # カタカナ「ステージ」への書き戻しは既存語彙からは起こらない。カタカナを検出語へ
        # 加えると「ステージング環境」のような無関係な語で偽陽性が増えるため、検査範囲を
        # Latin 表記に意図的に限定する(見落としではなく選択)。
        text_groups: dict[str, dict[str, str]] = {
            "branch-splitting.md": self._plan_reference_texts("branch-splitting.md"),
            "plan-review.md": self._plan_reference_texts("plan-review.md"),
            "branch-design/SKILL.md": self._plan_skill_texts(),
        }
        for doc_name, texts in text_groups.items():
            for platform, text in texts.items():
                with self.subTest(doc=doc_name, platform=platform):
                    self.assertNotIn(
                        "stage",
                        text.lower(),
                        f"{doc_name}({platform}) に廃止した implementation_stages 機構の"
                        "語彙(stage)が残っている",
                    )


if __name__ == "__main__":
    unittest.main()
