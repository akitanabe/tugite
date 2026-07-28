"""Repository contracts for post-return diff-unit replanning."""

from __future__ import annotations

from pathlib import Path
import unittest

from build_plugin_assets_test_support import RepositoryContractSupport


class ImplLeadReviewLoopContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def test_workflows_classify_mixed_diff_before_reviewer_or_acceptance(self) -> None:
        """Judge a change unit by its contract boundaries, not a line-count threshold."""
        workflows = self._repository_workflow_texts()
        decision_axes = (
            "変更理由",
            "Acceptance Criteria (AC)",
            "責務",
            "依存",
            "受入",
            "rollback",
            "検証単位",
        )
        decision_signals = (
            "独立した変更理由",
            "AC 無関係変更",
            "異なる rollback・review・前提知識・責務・受入単位",
            "計画 scope の大幅超過",
            "reviewer が一変更単位として判断困難",
            "固定行数だけでは分割しない",
            "diff が大きいだけでは分割しない",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                section = workflow.split("## 返却 diff の変更単位判定", 1)[1].split(
                    "## 再分割・再承認ゲート", 1
                )[0]
                normalized = "".join(section.split())
                self.assertIn("専門 reviewer 起動や受入の前", section)
                for axis in decision_axes:
                    with self.subTest(axis=axis):
                        self.assertIn("".join(axis.split()), normalized)
                for signal in decision_signals:
                    with self.subTest(signal=signal):
                        self.assertIn("".join(signal.split()), normalized)
                self.assertIn(
                    "分割で依存が不自然または検証不能になる場合は1変更として扱う",
                    "".join(workflow.split()),
                )

    def test_workflows_keep_approved_contract_or_replan_before_new_delegation(
        self,
    ) -> None:
        """Separate safe formatting from approval-changing replanning and block delegation."""
        workflows = self._repository_workflow_texts()

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                section = workflow.split("## 再分割・再承認ゲート", 1)[1].split(
                    "### evidence を欠く指摘の扱い", 1
                )[0]
                normalized = "".join(section.split())
                self.assertIn(
                    "混在 diff をそのまま reviewer へ渡したり受け入れたりしない",
                    section,
                )
                self.assertIn("scope 逸脱の差戻し", section)
                for contract in ("commit を分離", "最小範囲だけを残す", "別タスク化"):
                    self.assertIn("".join(contract.split()), normalized)

                format_boundary = section.index("承認済み実装枝の purpose")
                branch_replan = section.index("独立した実装枝への分離")
                implementation_replan = section.index("AC 文言自体の分解・再定義")
                self.assertLess(format_boundary, branch_replan)
                self.assertLess(branch_replan, implementation_replan)

                branch_section = section[branch_replan:implementation_replan]
                for contract in (
                    "Branch Plan を再生成",
                    "blocking violation と Executor 再検証5項目を再計算",
                    "必要なユーザー再承認を得るまで新枝を委譲しない",
                ):
                    self.assertIn("".join(contract.split()), "".join(branch_section.split()))

                implementation_section = section[implementation_replan:]
                for contract in (
                    "Implementation Plan の AC 確定とユーザー確認へ戻る",
                    "その後 Branch Plan を再生成・再検証・再承認する",
                    "再承認後に初めて新枝の委譲を開始する",
                ):
                    self.assertIn(
                        "".join(contract.split()),
                        "".join(implementation_section.split()),
                    )

    def test_decision_corpus_has_independent_split_and_no_split_cases(self) -> None:
        """Keep EVAL-28 and EVAL-29 expectations independently assessable."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        split_case = corpus.split("## EVAL-28:", 1)[1].split("## EVAL-29:", 1)[0]
        no_split_case = corpus.split("## EVAL-29:", 1)[1]

        for case, contracts in (
            (
                split_case,
                (
                    "期待する判断",
                    "必須動作",
                    "禁止動作",
                    "再分割",
                    "Branch Plan を再生成",
                    "再承認前の新枝委譲を禁止",
                ),
            ),
            (
                no_split_case,
                (
                    "期待する判断",
                    "必須動作",
                    "禁止動作",
                    "大きいだけ",
                    "1変更として扱う",
                    "reviewer",
                ),
            ),
        ):
            for contract in contracts:
                with self.subTest(case=case[:20], contract=contract):
                    self.assertIn(contract, case)
