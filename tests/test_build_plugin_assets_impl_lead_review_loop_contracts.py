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
        required_contracts = (
            "## 返却 diff の変更単位判定",
            "reviewer 起動や受入の前",
            "変更理由・AC・責務・依存・受入・rollback・検証単位",
            "独立した変更理由",
            "AC 無関係変更",
            "異なる rollback・review・前提知識・責務・受入単位",
            "計画 scope の大幅超過",
            "reviewer が一変更単位として判断困難",
            "固定行数だけでは分割しない",
            "diff が大きいだけでは分割しない",
            "分割で依存が不自然または検証不能になる場合は1変更として扱う",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized = "".join(workflow.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized)

    def test_workflows_keep_approved_contract_or_replan_before_new_delegation(
        self,
    ) -> None:
        """Separate safe formatting from approval-changing replanning and block delegation."""
        workflows = self._repository_workflow_texts()
        required_contracts = (
            "## 再分割・再承認ゲート",
            "混在 diff をそのまま reviewer へ渡したり受け入れたりしない",
            "scope 逸脱の差戻し",
            "承認済み実装枝の purpose・AC 文言・AC ownership・scope・依存・risk を保つ commit 分離",
            "最小範囲だけを残す",
            "別タスク化",
            "Branch Plan を再生成",
            "blocking violation と Executor 再検証5項目を再計算",
            "必要なユーザー再承認を得るまで新枝を委譲しない",
            "Implementation Plan の AC 確定とユーザー確認へ戻る",
            "その後 Branch Plan を再生成・再検証・再承認する",
            "依存が不自然または検証不能になる場合は1変更として扱う",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized = "".join(workflow.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized)

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
