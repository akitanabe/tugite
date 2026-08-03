"""Repository contracts for impl-lead delegation modes and TDD evidence."""

from __future__ import annotations

from pathlib import Path
import re
import unittest

from build_plugin_assets_test_support import (
    AGENT_NAMES,
    CLAUDE_PROFILE_PATH,
    CODEX_PROFILE_PATH,
    GENERATED_SKILL_PATHS,
    REPOSITORY_ROOT,
    RepositoryContractSupport,
)


class ImplLeadModeContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def test_repository_generated_agents_match_canonical_inventory(self) -> None:
        """Publish the reviewer under its new name without retaining old agent assets."""
        expected_claude = {f"{name}.md" for name in AGENT_NAMES}
        expected_codex = {f"{name}.toml" for name in AGENT_NAMES}
        actual_claude = {
            path.name
            for path in (REPOSITORY_ROOT / CLAUDE_PROFILE_PATH).glob("*.md")
        }
        actual_codex = {
            path.name
            for path in (REPOSITORY_ROOT / CODEX_PROFILE_PATH).glob("*.toml")
        }

        self.assertEqual(expected_claude, actual_claude)
        self.assertEqual(expected_codex, actual_codex)

    def test_repository_workflows_select_delegation_modes_without_crossing_direct_boundary(
        self,
    ) -> None:
        """Select delegation modes while keeping direct work outside the skill."""
        workflows = self._repository_workflow_texts()
        required_rules = (
            "委譲の決定は次の3層に分ける。層をまたいで並列に選ばない。",
            "経路の選択 — `direct`（この skill の外）か、委譲（この skill）か。",
            "配分方針の選択 — 委譲する場合に、配分方針 `policy` と基準 `baseline` を決める。",
            "枝 mode の導出 — `policy`、`baseline`、枝の "
            "`implementation_complexity.level` から枝ごとの mode を導く。",
            "`direct` は親が実装する、この skill の外にある経路である。",
            "委譲 mode ではないため、配分方針や枝 mode と同じ層に並べて選ばない。",
            "タスク規模だけでこの skill を発火しない。",
            "`direct` が明示された場合も、この skill を発火しない。",
            "`lite` / `standard(-adaptive)` / `strict(-adaptive)` / `strict-full` の明示は"
            "委譲要求を兼ねる。",
            "委譲だけが明示され mode が指定されていない場合は `{adaptive, standard}` を選ぶ。",
            "`lite` を自動選択しない。",
            "`direct` と委譲が同時に指定された場合は、実装前にユーザーへ確認する。",
            "委譲 mode の強度は `lite < standard < strict` とする。",
            "`direct` から委譲へ変更する場合は、ユーザーへ確認する。",
            "仕様が曖昧な場合は mode を選ぶ前に実装を止め、ユーザーへ確認する。",
            "`lite` の選択条件を満たさなくなった場合は `standard` 以上へ引き上げる。",
            "`standard` では扱えない実装複雑度が判明した場合は `strict` へ引き上げる。",
        )
        route_contracts = (
            (
                "| `direct` | — | — |",
                "この skill を発火しない skill 外の経路。委譲要求がなく、仕様が明確で"
                "影響範囲が閉じ、親が直接処理する変更。",
            ),
        )
        obsolete_classifications = (
            "枝の種別",
            "軽い修正・明確な仕様",
            "通常実装（既定）",
            "重要・高リスク実装",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized_workflow = "".join(workflow.split())

                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized_workflow)
                for route, contract in route_contracts:
                    self.assertIn(route, workflow)
                    self.assertIn("".join(contract.split()), normalized_workflow)
                for classification in obsolete_classifications:
                    self.assertNotIn(classification, workflow)

    def test_repository_workflows_split_delegation_mode_into_policy_and_baseline(
        self,
    ) -> None:
        """Treat adaptive as an allocation policy over the existing branch modes."""
        workflows = self._repository_workflow_texts()
        required_rules = (
            "配分方針  policy   : fixed | adaptive",
            "基準      baseline : lite | standard | strict",
            "枝 mode            : lite | standard | strict",
            "policy / baseline と枝の implementation_complexity.level から導出する",
            "`adaptive` は新しい実装フローではなく、既存の `lite` / `standard` / `strict` を"
            "枝へ割り当てる配分方針である。",
            "枝へ割り当てられた後は、その枝を既存の各 mode のフローで実行する。",
            "`policy: fixed` は、全枝固定であることを明示的に表現する語彙だけに割り当てる。",
            "それ以外の語彙と mode 未指定はすべて `adaptive` へ写す。",
            "今後語彙を追加する場合の既定も `adaptive` とする。",
            "`policy: adaptive` では、`baseline` と枝の `implementation_complexity.level` の決定表で"
            "枝ごとの mode を導出する。",
            "決定表の正本は [Branch Plan の受け入れ](references/branch-plan-intake.md) とする。",
            "`policy: fixed` では導出を行わず、全枝へ `baseline` をそのまま適用する。",
        )
        vocabulary_rows = (
            (
                "| 指定なし | `adaptive` | `standard` |",
                "通常利用のデフォルト。mode 未指定の明示的な委譲でもこれを選ぶ。",
            ),
            (
                "| `standard` / `standard-adaptive` | `adaptive` | `standard` |",
                "通常の実装委譲。",
            ),
            (
                "| `strict` / `strict-adaptive` | `adaptive` | `strict` |",
                "全体として厳格な確認を要求するが、明らかに低 complexity の枝まで一律 `strict` に"
                "しない。`standard-adaptive` より保守的に導出する。",
            ),
            (
                "| `strict-full` | `fixed` | `strict` |",
                "全枝へ `strict` を固定適用する。枝ごとの導出を行わない。",
            ),
            (
                "| `lite` | `fixed` | `lite` |",
                "全枝を軽量フローで処理する。枝ごとの導出を行わない。ユーザーが明示し、"
                "仕様が明確で影響範囲が局所的、容易に戻せる変更にだけ選ぶ。",
            ),
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized_workflow = "".join(workflow.split())

                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized_workflow)
                for row, contract in vocabulary_rows:
                    self.assertIn(row, workflow)
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_workflows_bound_mode_downgrade_ban_to_allocation_policy(
        self,
    ) -> None:
        """Ban downgrades of the allocation policy, not of derived branch modes."""
        workflows = self._repository_workflow_texts()
        required_rules = (
            "引き下げ禁止の対象は配分方針 `{policy, baseline}` とする。",
            "ユーザーが明示した `baseline` を親都合で引き下げない。",
            "`policy` を親都合で `fixed` から `adaptive` へ変えない。",
            "枝への mode 割り当ては決定表による導出結果であり、引き下げに当たらない。",
            "導出表を逸脱した割り当てだけを引き上げ / 引き下げとして扱う。",
            "mode を引き上げた場合は、その具体的な実装複雑度をユーザーへ報告する。",
            "導出結果より高い mode で枝を実行する場合も、枝単位で具体的な実装複雑度を"
            "ユーザーへ報告する。",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized_workflow = "".join(workflow.split())
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized_workflow)

    def test_repository_workflows_present_branch_allocation_before_delegating(
        self,
    ) -> None:
        """Show the resolved allocation before delegating and gate strict-full."""
        skills = self._repository_skill_texts()
        workflows = self._repository_workflow_texts()
        required_rules = (
            "## 実行前サマリー",
            "導出後、委譲開始前に次を提示する。",
            "解決後の配分方針。`strict` を指定したユーザーが、その場で `strict-adaptive` "
            "として解釈されたことを確認できるようにする。",
            "枝 mode ごとの件数。",
            "各枝の `failure_impact.level`、`implementation_complexity.level`、"
            "導出した mode、手動上書きの有無。",
            "Mode: standard-adaptive  (policy: adaptive / baseline: standard)",
            "Branch allocation:\n  strict   1\n  standard 3\n  lite     1",
            "1. authorization-check  impact:high / complexity:high    → strict",
            "4. api-response         impact:medium / complexity:low     → lite → standard  (override)",
            "5. label-text           impact:low / complexity:low        → lite",
            "枝 mode ごとの件数は、手動上書き後の実効 mode を集計する。",
            "各枝の行では、上書きがある場合に「導出 mode → 上書き後の mode」の両方を示す。",
            "`strict-full`（`{fixed, strict}`）は枝数に比例してコストが増えるため、"
            "枝数を明示したユーザー確認を委譲開始条件とする。",
            "確認が得られるまで委譲を開始しない。",
            "実行前サマリーを提示する。",
            "`strict-full` では枝数を明示したユーザー確認を得るまで委譲を開始しない。",
            "会話上の最終報告を行う。採用した配分方針と枝ごとの mode を含める。",
            "導出した枝 mode は Branch Plan へ書き戻さず、実行 Data として保持して"
            "最終報告で報告する。",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized_workflow = "".join(workflow.split())
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized_workflow)

        # Branch Plan 単位の提示と確認ゲートは SKILL.md 本体が持つ。連結テキストへの
        # assert だけだと、reference へ移設しても通ってしまい、SKILL.md だけを読む
        # Executor が単位を知らないまま委譲を開始できる。
        branch_plan_unit_rules = (
            "実行前サマリーは Branch Plan 単位で提示する。",
            "Branch Plan ごとに配分方針、枝 mode ごとの件数、枝一覧を提示する。",
            "`strict-full` の確認ゲートは Branch Plan 単位で行う。",
        )
        for platform, main in (
            ("source", skills.source_main),
            ("claude", skills.claude_main),
            ("codex", skills.codex_main),
        ):
            summary_section = main.split("## 実行前サマリー", 1)[-1].split(
                "\n## ", 1
            )[0]
            normalized_summary = "".join(summary_section.split())
            for rule in branch_plan_unit_rules:
                with self.subTest(platform=platform, rule=rule):
                    self.assertIn("".join(rule.split()), normalized_summary)
            with self.subTest(platform=platform, check="order"):
                self.assertLess(
                    main.index("実行前サマリーを提示する"),
                    main.index("先頭の枝だけを委譲する"),
                )

    def test_repository_workflows_separate_mode_and_safety_inputs(self) -> None:
        """Use complexity for adaptive modes and impact only for fixed-lite advice."""
        required_rules = (
            "adaptive の枝 mode は `implementation_complexity.level` だけから導出する。",
            "`failure_impact` は adaptive mode の直接導出に使わない。",
            "`failure_impact` は `{fixed, lite}` の安全性に関する "
            "`delegation_mode_proposal` に使う。",
            "mode の理由の正本は `implementation_complexity.reasons` とする。",
        )
        for path, workflow in self._repository_workflow_texts().items():
            with self.subTest(path=path):
                normalized = "".join(workflow.split())
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized)
                self.assertNotIn("recommended_mode:", workflow)
                self.assertNotIn("required_safeguards:", workflow)

    def test_repository_decision_corpus_separates_impact_from_complexity(self) -> None:
        """Observe inverse assessment combinations without cross-axis escalation."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        eval_33 = corpus.split("## EVAL-33:", 1)[1].split("## EVAL-34:", 1)[0]
        eval_34 = corpus.split("## EVAL-34:", 1)[1].split("## EVAL-35:", 1)[0]
        contracts = {
            "EVAL-33": (
                eval_33,
                (
                    "high impact / low complexity",
                    "failure_impact.level: high",
                    "failure_impact.reasons: [",
                    "implementation_complexity.level: low",
                    "implementation_complexity.reasons: [",
                    "complexity から `lite` を導出",
                    "failure impact だけを理由に `strict` または `senior-implementer` を選ばない",
                    "failure impact は専門 reviewer と rollback 確認へ使う",
                    "依存 edge だけではどちらの level も上げない",
                ),
            ),
            "EVAL-34": (
                eval_34,
                (
                    "low impact / high complexity",
                    "failure_impact.level: low",
                    "failure_impact.reasons: [",
                    "implementation_complexity.level: high",
                    "implementation_complexity.reasons: [",
                    "implementation complexity を根拠に `strict` と `senior-implementer` の候補にする",
                    "failure impact が低いことを理由に mode を下げない",
                    "low impact を理由に `lite` または通常 Implementer へ固定する",
                ),
            ),
        }
        for case_name, (case, required) in contracts.items():
            with self.subTest(case=case_name):
                normalized_case = "".join(case.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized_case)

    def test_repository_valid_branch_plan_evals_include_both_assessment_axes(self) -> None:
        """Give every valid branch example complete impact and complexity Data."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        cases = {
            "EVAL-18": corpus.split("## EVAL-18:", 1)[1].split("## EVAL-22:", 1)[0],
            "EVAL-22": corpus.split("## EVAL-22:", 1)[1].split("## EVAL-23:", 1)[0],
            "EVAL-23": corpus.split("## EVAL-23:", 1)[1].split("## EVAL-24:", 1)[0],
        }
        expected_branch_counts = {"EVAL-18": 2, "EVAL-22": 3, "EVAL-23": 2}
        branch_markers = {
            "EVAL-18": ("`b-index`:", "`b-search`:"),
            "EVAL-22": ("`b-auth`:", "`b-domain`:", "`b-label`:"),
            "EVAL-23": ("`b-migration`:", "`b-format`:"),
        }
        for case_name, case in cases.items():
            with self.subTest(case=case_name):
                expected_count = expected_branch_counts[case_name]
                case_input = case.split("**入力**", 1)[1].split(
                    "**期待する判断**", 1
                )[0]
                self.assertEqual(
                    expected_count, case_input.count("failure_impact.level:")
                )
                self.assertEqual(
                    expected_count, case_input.count("failure_impact.reasons:")
                )
                self.assertEqual(
                    expected_count,
                    case_input.count("implementation_complexity.level:"),
                )
                self.assertEqual(
                    expected_count,
                    case_input.count("implementation_complexity.reasons:"),
                )
                markers = branch_markers[case_name]
                for index, marker in enumerate(markers):
                    with self.subTest(case=case_name, branch=marker):
                        start = case_input.index(marker)
                        end_markers = markers[index + 1 :] + (
                            "`unresolved_decisions",
                        )
                        end = min(
                            position
                            for end_marker in end_markers
                            if (
                                position := case_input.find(
                                    end_marker, start + len(marker)
                                )
                            )
                            != -1
                        )
                        branch = case_input[start:end]
                        for axis in (
                            "failure_impact",
                            "implementation_complexity",
                        ):
                            self.assertEqual(1, branch.count(f"{axis}.level:"))
                            self.assertEqual(1, branch.count(f"{axis}.reasons:"))
                            self.assertEqual(
                                1,
                                len(
                                    re.findall(
                                        rf"{axis}\.level:\s*(?:low|medium|high)",
                                        branch,
                                    )
                                ),
                            )
                            self.assertEqual(
                                1,
                                len(
                                    re.findall(
                                        rf'{axis}\.reasons:\s*\[(?:\s*"[^"]+"\s*,?)+\]',
                                        branch,
                                    )
                                ),
                            )
    def test_repository_decision_corpus_drops_all_stage_vocabulary(self) -> None:
        """Leave no trace of the retired implementation_stages mechanism in the corpus."""
        # 廃止 field 名(implementation_stages / stage_tests / stages_reason)だけでなく、
        # field 名を含まない stage 概念の散文(「stage は AC を所有しない」等)も検出できるよう、
        # 生の "stage" 部分文字列(大小無視)の不在を検査する。原稿側の同型テストと検査形を
        # 揃えている。
        # 検出は Latin 表記に閉じる。corpus は stage 概念を Latin 表記でしか書いておらず、
        # カタカナ「ステージ」への書き戻しは既存語彙からは起こらない。一方で日本語の「段階」は
        # strict の四段階 gate や評価タイミングの説明という別概念で正当に多数使われるため、
        # 検出語へ加えると偽陽性しか増えない。stage 機構を指す日本語の散文は、この検査ではなく
        # EVAL-15 / EVAL-18 の本文を固定する契約テストで排除する。
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        carrying = [line for line in corpus.splitlines() if "stage" in line.lower()]
        self.assertEqual(
            [],
            carrying,
            "corpus に廃止した implementation_stages 機構の語彙(stage)が残っている: "
            f"{carrying}",
        )

    def test_repository_decision_corpus_splits_branch_plans_on_qualitative_criteria(
        self,
    ) -> None:
        """Evaluate Branch Plan Set splitting by purpose and learning boundaries."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        case = corpus.split("## EVAL-15: Branch Plan Set の分割判断", 1)[1].split(
            "## EVAL-16:", 1
        )[0]
        required_contracts = (
            "`planning`",
            "独立した変更目的が複数あり、一方を実行して他方を実行しない選択が成立する",
            "先行部分の完了後に、後続の設計を見直す余地がある",
            "`order`",
            "`depends_on` が同一 Branch Plan 内に閉じることは必要条件であり、十分条件ではない",
            "`decision.split: false`",
        )
        forbidden_contracts = (
            "枝数の固定閾値",
            "新しい blocking violation code",
            "`depends_on` が閉じていることだけを根拠に分割する",
        )
        normalized_case = "".join(case.split())
        for contract in required_contracts:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), normalized_case)
        prohibited = case.split("**禁止動作**", 1)[1].split("**許容される差異**", 1)[0]
        normalized_prohibited = "".join(prohibited.split())
        for contract in forbidden_contracts:
            with self.subTest(prohibited=contract):
                self.assertIn("".join(contract.split()), normalized_prohibited)

    def test_repository_decision_corpus_stops_at_an_unauthorized_branch_plan(
        self,
    ) -> None:
        """Stop at the Branch Plan boundary without treating it as a plan defect."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        case = corpus.split("## EVAL-18: 未授権 Branch Plan の境界での停止", 1)[
            1
        ].split("## EVAL-22:", 1)[0]
        required_contracts = (
            "`plan-intake`",
            "`delegation: { authorized: false, authorized_by: null, requested_mode: null }`",
            "Set 帰属の blocking violation code を先行検査する",
            "再検証5項目を Branch Plan ごとに繰り返し、先行 Branch Plan の結果を流用しない",
            "完了済み Branch Plan の最終報告と未実行 Branch Plan の一覧を提示して授権を要求する",
            "既定では `order` の先頭の未実行 Branch Plan だけを授権する",
        )
        forbidden_contracts = (
            "未授権を Branch Plan の誤りとして修正を要求する",
            "境界のために `delegation.authorized` とは別の状態や field を新設する",
            "1回の委譲要求で全 Branch Plan を授権する",
        )
        normalized_case = "".join(case.split())
        for contract in required_contracts:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), normalized_case)
        prohibited = case.split("**禁止動作**", 1)[1].split("**許容される差異**", 1)[0]
        normalized_prohibited = "".join(prohibited.split())
        for contract in forbidden_contracts:
            with self.subTest(prohibited=contract):
                self.assertIn("".join(contract.split()), normalized_prohibited)

    def test_repository_docs_describe_branch_design_output_as_a_branch_plan_set(
        self,
    ) -> None:
        """Publish the same Branch Plan Set output description in every hand-written doc."""
        # 生成対象ではない手書き文書だけを見る。`shared/` 側の記述は branch-design の
        # 契約テストが持つため、ここでは読者向け文書の語彙追随だけを固定する。
        paths = (
            Path("README.md"),
            Path("plugins/claude/README.md"),
            Path("plugins/codex/README.md"),
            Path("CLAUDE.md"),
        )
        for path in paths:
            text = self._repository_text(path)
            with self.subTest(path=path):
                self.assertIn(
                    "".join("実装プランを委譲可能な Branch Plan Set へ正規化".split()),
                    "".join(text.split()),
                )
                self.assertNotIn("Branch Plan Data", text)

    def test_repository_decision_corpus_rejects_legacy_risk(self) -> None:
        """Observe planning and Executor rejection of legacy risk input."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        required_contracts = (
            "## EVAL-35: legacy risk の拒否",
            "旧 `risk` 単独",
            "旧 `risk` と新 field の混在",
            "planning Skill と Executor の双方",
            "`legacy-risk-present`",
            "互換推測しない",
        )
        normalized = "".join(corpus.split())
        for contract in required_contracts:
            self.assertIn("".join(contract.split()), normalized)

    def test_repository_readmes_describe_independent_branch_assessment_axes(self) -> None:
        """Publish the same two-axis mode contract in every user-facing README."""
        paths = (
            Path("README.md"),
            Path("plugins/claude/README.md"),
            Path("plugins/codex/README.md"),
        )
        required_contracts = (
            "failure_impact",
            "implementation_complexity",
            "adaptive",
            "fixed",
            "lite",
            "strict",
        )
        for path in paths:
            text = self._repository_text(path)
            normalized = "".join(text.split())
            with self.subTest(path=path):
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized)
                self.assertNotIn("branches[].risk", text)
                self.assertNotIn("risk.level", text)
                self.assertNotIn("低リスク", text)
                self.assertNotIn("risk 差", text)

    def test_repository_workflows_apply_mode_specific_qa_and_parent_verification(
        self,
    ) -> None:
        """Apply each delegation mode's QA strength and retain parent verification."""
        workflows = self._repository_workflow_texts()
        mode_contracts = (
            (
                "| `lite` |",
                "親は返却の diff とテストを確認し、Acceptance Criteria に対応する振る舞いが"
                "検証されていることを確かめ、focused test またはタスクで指定された成功条件で"
                "green を確認する。",
            ),
            (
                "| `standard` |",
                "AC→テスト対応表、境界値、異常系、Red 時点の失敗出力を要求する。",
            ),
            (
                "| `strict` |",
                "テスト計画→失敗テスト→実装→Refactor の段階ゲートに分ける。",
            ),
        )
        required_rules = (
            "- 委譲 mode: <この枝に導出された枝 mode。lite / standard / strict>",
            "`lite` では、親が明示した場合だけ AC 対応表と Red 時点の失敗出力を付けること。",
            "`standard` では、Red 時点の失敗出力と",
            "「AC-n → それを検証するテスト名 → 期待値の根拠（仕様のどこから導いたか）」"
            "の対応表を必ず付けること。",
            "最終返却には `standard` と同じ AC 対応表と Red 証跡を含める。",
            "`standard` と `strict` では全観点を手を動かして確認する。",
            (
                "`lite` では観点0（diff を読む）、観点5（自分で green を確認）、"
                "Acceptance Criteria に対応する振る舞いが検証されていることの確認へ絞ってよい。"
            ),
            (
                "`lite` のこの確認は親が diff と検証結果から行うものであり、"
                "Implementer への AC 対応表や Red 証跡の要求に置き換えない。"
            ),
            (
                "検証手段はテストに限定せず、プロジェクトまたはタスクで指定された成功条件"
                "（自動テスト、type check、lint、build、静的解析、実行結果の確認、"
                "手動確認手順、snapshot 比較、API レスポンス確認など）を使う。"
            ),
            "検証 command が成功したことだけを完了根拠にしない。",
            (
                "親は「どの Acceptance Criteria を」「どのテストまたは確認手順で」"
                "「どの結果によって」満たしたと判断したかを説明できる状態にする。"
            ),
            "全ての委譲 mode で、親による統合後の検証と最終的な受け入れ判断を省略しない。",
            "`direct` でも、親は必要なテストと検証を実行し、diff review と最終報告を行う。",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized_workflow = "".join(workflow.split())

                for mode, contract in mode_contracts:
                    self.assertIn(mode, workflow)
                    self.assertIn("".join(contract.split()), normalized_workflow)
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized_workflow)

    def test_repository_workflows_limit_green_red_evidence_to_regression_tests(
        self,
    ) -> None:
        skills = self._repository_skill_texts()
        implementation_contracts = (
            "新機能または未実装仕様を検証する test は Red 必須",
            "既存挙動を固定する regression test",
            "追加時点で Green",
            "既存挙動を固定する追補 test であること",
            "対応する AC",
            "期待値の根拠",
            "既存実装がすでに仕様を満たしていたこと",
            "形式的な Red を作るために本番 code を一時変更してはならない",
            "mutation は親が明示した一時検証に限定",
            "mutation を commit してはならない",
            "変更禁止範囲や本番 code を mutation の対象にしてはならない",
            "regression Green 例外の Red 段階では passing test を commit",
            "変更がない Green / Refactor 段階に空 commit を作らない",
        )
        qa_contracts = (
            "AC、test、期待値の根拠、既存挙動の対応",
            "新機能または未実装仕様なら Red",
            "regression test が追加時点で Green",
        )
        intake_contracts = (
            "新機能または未実装仕様",
            "既存挙動を固定する regression test",
            "分類できない場合は Green 例外を適用せず判断点として返す",
        )

        reference_sets = (
            skills.source_references,
            skills.claude_references,
            skills.codex_references,
        )
        for references in reference_sets:
            for reference, contracts in (
                ("implementation-branches.md", implementation_contracts),
                ("qa-and-integration.md", qa_contracts),
                ("branch-plan-intake.md", intake_contracts),
            ):
                with self.subTest(reference=reference):
                    normalized = "".join(references[reference].split())
                    for contract in contracts:
                        self.assertIn("".join(contract.split()), normalized)

    def test_repository_implementers_return_regression_green_evidence(
        self,
    ) -> None:
        required_contracts = (
            "新機能または未実装仕様では Red を必須",
            "既存挙動を固定する regression test に限り追加時点の Green を許可",
            "既存挙動を固定する追補 test であること",
            "対応する AC",
            "期待値の根拠",
            "既存実装がすでに仕様を満たしていたこと",
            "形式的な Red のために本番 code を変更しない",
            "親が明示した一時 mutation 検証だけを行い、commit しない",
            "変更禁止範囲と本番 code を mutation の対象にしない",
        )

        for name in ("implementer", "senior-implementer", "expert-implementer"):
            paths = (
                Path("shared/agents") / f"{name}.md",
                Path("plugins/claude/agents") / f"{name}.md",
                Path("plugins/codex/install/agents") / f"{name}.toml",
            )
            for path in paths:
                with self.subTest(name=name, path=path):
                    normalized = "".join(self._repository_text(path).split())
                    for contract in required_contracts:
                        self.assertIn("".join(contract.split()), normalized)

    def test_repository_decision_corpus_covers_red_and_regression_green_cases(
        self,
    ) -> None:
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        required_contracts = (
            "## EVAL-11: 新機能では Red 証跡が必須",
            "新機能または未実装仕様",
            "Red 時点の失敗出力を必須",
            "## EVAL-12: regression test の追加時点 Green 例外",
            "既存挙動を固定する追補 test",
            "期待値の根拠",
            "既存実装がすでに仕様を満たしていた",
            "形式的 Red のために本番 code を変更しない",
            "mutation を commit しない",
            "親が AC、test、期待値の根拠、既存挙動の対応を確認",
        )
        normalized = "".join(corpus.split())
        for contract in required_contracts:
            self.assertIn("".join(contract.split()), normalized)

    def test_repository_decision_corpus_records_parent_managed_worktree_contract(
        self,
    ) -> None:
        """Record the issue #49 worktree contract verification and drop its superseded contract text."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        normalized = "".join(corpus.split())

        required_contracts = (
            "### worktree 契約の検証記録(issue #49)",
            "親管理 worktree 契約を採用し、`isolation: \"worktree\"` を廃止する",
            "HEAD 不一致を検出し、reset / merge / checkout などの自力修復を試みず",
            "`git worktree remove` と `git branch -D`",
            "既知の制約",
            "## EVAL-19: 開始条件不成立を検出した未着手返却",
            "契約通りの正常動作として扱う",
            "branch 不一致、dirty status のいずれであっても同じ扱いとする。",
            "worktree を基準 commit から作り直し",
            "Implementer へ reset / merge / checkout などの自力修復を指示しない。",
            "未着手返却を失敗として扱い、Implementer を責める、または mode を引き下げる。",
            "HEAD 不一致だけを特別扱いし、path 不一致・branch 不一致・dirty status を異なる扱いにする。",
            "Claude Code と Codex は「platform 共通の期待」に記載した起動、継続 mechanism だけが異なる。",
            "Red 必須と親 QA は共通であり、agent の起動 mechanism だけが異なる。",
        )
        # 「引き上げ受諾後の段階継続 mechanism は platform に合わせてよい。」は、廃止した
        # implementation_stages 機構を前提にした EVAL-18 の許容差異だった。case ごと書き換えた
        # ため文そのものが corpus に存在せず、存在を要求できない。worktree 準備を含む旧版が
        # 復活しないことは下の stale_contracts が引き続き見る。
        for contract in required_contracts:
            self.assertIn("".join(contract.split()), normalized)

        stale_contracts = (
            "Claude Code と Codex は「platform 共通の期待」に記載した worktree 準備、"
            "起動、継続 mechanism だけが異なる。",
            "Red 必須と親 QA は共通であり、worktree と agent の起動 mechanism だけが異なる。",
            "引き上げ受諾後の worktree 準備・段階継続 mechanism は platform に合わせてよい。",
        )
        for contract in stale_contracts:
            self.assertNotIn("".join(contract.split()), normalized)

    def test_repository_decision_corpus_covers_findings_sourced_planning(
        self,
    ) -> None:
        """Evaluate findings-sourced planning as listed IDs, confirmed wording, and traceable origins."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        planning_cases = corpus.split("# Planning cases", 1)[1].split(
            "# Plan-intake cases", 1
        )[0]
        required_contracts = (
            "## EVAL-25: Test Inventory 報告の findings を元プランにする枝分割計画",
            "指定のない `G-3` は採用しない。",
            "対象 `G-*` ごとに `summary` / `evidence` / `suggestion` の原文と"
            "導出した AC 案を対で提示する。",
            "確定前は `unresolved_decisions` に `kind: ac-derivation`",
            "確定した AC の `derived_from` に由来する finding ID を記録",
            "導出案をユーザー確定なしに AC の `text` に入れる。",
            "`suggestion` にない対象・範囲・実装方針を導出で補う。",
        )
        normalized = "".join(planning_cases.split())
        for contract in required_contracts:
            with self.subTest(contract=contract):
                self.assertIn("".join(contract.split()), normalized)

    def test_repository_readmes_list_all_distributed_agents(self) -> None:
        """Make every bundled agent discoverable from both platform READMEs."""
        claude_readme = (REPOSITORY_ROOT / "plugins" / "claude" / "README.md").read_text(
            encoding="utf-8"
        )
        codex_readme = (REPOSITORY_ROOT / "plugins" / "codex" / "README.md").read_text(
            encoding="utf-8"
        )

        for name in AGENT_NAMES:
            with self.subTest(name=name):
                self.assertIn(f"agents/{name}.md", claude_readme)
                self.assertIn(f"`{name}`", codex_readme)

    def test_repository_does_not_reference_retired_flat_mode_contract_text(
        self,
    ) -> None:
        """Detect leftover flat lite/standard/strict contract text from before adaptive mode."""
        scan_roots = (
            REPOSITORY_ROOT / "shared",
            REPOSITORY_ROOT / "plugins",
            REPOSITORY_ROOT / "scripts",
            REPOSITORY_ROOT / "tests",
            REPOSITORY_ROOT / "evals",
            REPOSITORY_ROOT / "README.md",
        )
        # Each phrase below was the pre-adaptive-mode contract text superseded by the
        # {policy, baseline} vocabulary across the three branches this branch depends
        # on. A survivor means one of those branches missed a reference, not that this
        # branch should silently rewrite it. Phrases are built by concatenation (like
        # the retired agent name above) so this literal does not self-match the scan.
        retired_phrases = (
            "requested_mode: null | lite | standard" + " | strict",
            "propose: " + "strict",
            "- 委譲 mode: <lite / standard" + " / strict>",
            "| route / mode | " + "選択条件 |",
            "Executor が standard" + " を選ぶ",
            "委譲だけが明示され mode が指定されていない場合は `standard`" + " を選ぶ。",
            # Bare flat-enum field assignments (e.g. from evals corpus examples
            # written before the {policy, baseline} structure existed). Confirmed
            # absent repository-wide before adding; the new structured form always
            # writes "requested_mode: {" so it cannot collide with these literals.
            "requested_mode: " + "lite",
            "requested_mode: " + "standard",
            "requested_mode: " + "strict",
        )

        scanned_files = list(self._iter_repository_text_asset_files(*scan_roots))
        # A silently empty scan would pass vacuously without checking anything.
        self.assertTrue(scanned_files, scan_roots)

        for file_path in scanned_files:
            content = file_path.read_text(encoding="utf-8")
            for phrase in retired_phrases:
                with self.subTest(path=file_path, phrase=phrase):
                    self.assertNotIn(phrase, content)

    def test_repository_delegate_skill_description_names_the_input_vocabulary(
        self,
    ) -> None:
        """Fire on the five input tokens and keep the direct exclusion in the description."""
        vocabulary_tokens = (
            "`lite`",
            "`standard(-adaptive)`",
            "`strict(-adaptive)`",
            "`strict-full`",
            "`direct`",
        )
        exclusion_contract = (
            "`direct` の明示時や、委譲指示なしにタスク規模だけを理由として使わない。"
        )

        for platform in ("claude", "codex"):
            with self.subTest(platform=platform):
                content = self._repository_text(GENERATED_SKILL_PATHS[platform])
                frontmatter = content.split("---", 2)[1]
                self.assertIn("description:", frontmatter)
                normalized_frontmatter = "".join(frontmatter.split())
                for token in vocabulary_tokens:
                    self.assertIn(token, frontmatter)
                self.assertIn(
                    "".join(exclusion_contract.split()), normalized_frontmatter
                )

    def test_impl_lead_skill_flow_runs_branch_plans_in_order_and_stops_at_the_boundary(
        self,
    ) -> None:
        """Walk the Branch Plan Set in order and halt at an unauthorized boundary."""
        # 手順の番号は run-closeout.md の「main の手順9へ戻る」と既存契約が参照するため、
        # Branch Plan 単位の分岐は既存手順の中へ織り込み、番号を増やさない。
        skills = self._repository_skill_texts()
        required_flow = (
            "確定済み Branch Plan Set が渡されている場合は",
            "`order` に従って Branch Plan を順に実行する。",
            "いま実行している Branch Plan の全枝を完了した場合は、`order` に未実行の "
            "Branch Plan が残っていても手順9へ進む。",
            "未授権の Branch Plan に到達した場合は実行を止め",
            "授権を要求する",
            "授権された未実行の Branch Plan があれば手順2へ戻り",
            "手順7の修正経路",
        )
        # 決定表と再検証規則は正本参照のままにする。SKILL.md へ再掲すると同じ規則が
        # 2箇所で更新対象になる。決定表はヘッダ行全体で識別する。`| policy | baseline |`
        # だけだと、保持義務のある入力語彙の写像表(`| ユーザー入力 | policy | baseline |
        # 意味と選択条件 |`)にも一致してしまう。
        forbidden_restatements = (
            "| policy | baseline | `implementation_complexity.level: low` | "
            "`medium` | `high` |",
            "`status: approved` であり、`approval.method` が設定済みである。",
        )
        for platform, main in (
            ("source", skills.source_main),
            ("claude", skills.claude_main),
            ("codex", skills.codex_main),
        ):
            flow = main.split("## 全体の流れ", 1)[-1]
            normalized_flow = "".join(flow.split())
            for contract in required_flow:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized_flow)
            for restatement in forbidden_restatements:
                with self.subTest(platform=platform, restatement=restatement):
                    self.assertNotIn("".join(restatement.split()), "".join(main.split()))


if __name__ == "__main__":
    unittest.main()
