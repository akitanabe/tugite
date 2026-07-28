"""Repository contracts for post-return diff-unit replanning."""

from __future__ import annotations

from pathlib import Path
import unittest

from build_plugin_assets_test_support import RepositoryContractSupport


class ImplLeadReviewLoopContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    @staticmethod
    def _normalize_contract(text: str) -> str:
        return "".join(text.replace("`", "").split())

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
        no_split_case = corpus.split("## EVAL-29:", 1)[1].split(
            "# 結果記録", 1
        )[0]

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

    def _review_conflict_sections(self, workflow: str) -> dict[str, str]:
        heading = "## reviewer 間の競合解消"
        self.assertEqual(1, workflow.count(heading))
        end_heading = "## 返却 diff の変更単位判定"
        self.assertEqual(1, workflow.count(end_heading))
        section = workflow.split(heading, 1)[1].split(end_heading, 1)[0]
        subsection_headings = (
            "### 全 findings の収集 barrier",
            "### 問題と修正案の比較",
            "### 不採用・変更後の再実行",
            "### 安全に解消できない場合の差し戻し",
        )
        for subheading in subsection_headings:
            self.assertEqual(1, section.count(subheading))
        positions = [section.index(subheading) for subheading in subsection_headings]
        self.assertEqual(sorted(positions), positions)
        boundaries = positions + [len(section)]
        subsections = {
            heading: section[start:end]
            for heading, start, end in zip(
                subsection_headings, boundaries, boundaries[1:]
            )
        }
        return subsections

    def test_workflows_gate_conflict_resolution_by_snapshot_and_subsection_order(
        self,
    ) -> None:
        """Observe the collection barrier before comparison and any repair route."""
        workflows = self._repository_workflow_texts()
        for path, workflow in workflows.items():
            with self.subTest(path=path):
                subsections = self._review_conflict_sections(workflow)
                barrier = "".join(subsections["### 全 findings の収集 barrier"].split())
                for contract in (
                    "同一diffsnapshot",
                    "必須完了ゲートとriskにより選択した専門reviewer",
                    "全対象reviewer",
                    "全findingsとevidenceを収集",
                    "修正前",
                    "全findingsとevidenceを収集するまで、修正routingを開始しない",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(contract, barrier)

    def test_workflows_compare_findings_with_parent_axes_and_record_decision(
        self,
    ) -> None:
        """Observe parent-owned comparison and decision recording in its subsection."""
        workflows = self._repository_workflow_texts()
        for path, workflow in workflows.items():
            with self.subTest(path=path):
                subsections = self._review_conflict_sections(workflow)
                comparison = self._normalize_contract(
                    subsections["### 問題と修正案の比較"]
                )
                for contract in (
                    "親は reviewer の人数や多数決を使わず、各 finding の問題と修正案を分け、evidence と問題の妥当性を確認して比較する",
                    "競合する finding の問題が共に成立する場合は、代替解法を含めて次の判断軸を比較する",
                    "Acceptance Criteria（AC）と、適用される外部／repository 指示の優先順位",
                    "具体的失敗リスク、影響、発生可能性、対象 risk の残存",
                    "検証可能性、scope、rollback",
                    "最小修正と保守性",
                    "親は比較結果、採用した解消方針、採用しなかった修正案と各理由、各 finding の最終状態を記録する",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), comparison)

    def test_workflows_separate_no_change_changed_snapshot_and_unsafe_routes(
        self,
    ) -> None:
        """Observe both completion boundaries and the original-implementer handoff."""
        workflows = self._repository_workflow_texts()
        for path, workflow in workflows.items():
            with self.subTest(path=path):
                subsections = self._review_conflict_sections(workflow)
                rerun = "".join(subsections["### 不採用・変更後の再実行"].split())
                unsafe = "".join(
                    subsections["### 安全に解消できない場合の差し戻し"].split()
                )
                for contract in (
                    "diff変更なし",
                    "findingごとに問題を採用しない理由を記録する",
                    "diff変更あり",
                    "新しい同一snapshot",
                    "親QA",
                    "必須完了ゲート",
                    "競合当事者の専門reviewer",
                    "変更後も対象riskが成立する全専門reviewer",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(contract, rerun)
                for contract in (
                    "親だけではreviewer競合を安全に解消できない場合",
                    "review-patch-refactorerではなく元Implementer",
                    "競合しているreviewer名",
                    "指摘を識別できる情報および内容",
                    "守るAC",
                    "優先指示",
                    "許容不能リスク",
                    "必要な検証",
                    "再設計条件",
                    "上記の変更後snapshot再実行契約",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(contract, unsafe)
                self.assertIn(
                    "これらすべてを同時に満たす方針を説明できない場合",
                    unsafe,
                )
                self.assertNotIn(
                    "安全に解消できない場合はreview-patch-refactorer",
                    unsafe,
                )

    def _decision_case_sections(
        self,
        corpus: str,
        heading: str,
        next_heading: str,
    ) -> dict[str, str]:
        case = corpus.split(heading, 1)[1].split(next_heading, 1)[0]
        section_headings = (
            "**入力**",
            "**期待する判断**",
            "**必須動作**",
            "**禁止動作**",
        )
        end_heading = "**許容される差異**"
        platform_heading = "**Claude/Codex 差**"
        for section_heading in section_headings:
            self.assertEqual(1, case.count(section_heading))
        self.assertEqual(1, case.count(end_heading))
        self.assertEqual(1, case.count(platform_heading))
        positions = [case.index(section_heading) for section_heading in section_headings]
        end_position = case.index(end_heading)
        platform_position = case.index(platform_heading)
        all_positions = positions + [end_position, platform_position]
        self.assertEqual(sorted(all_positions), all_positions)
        boundaries = positions + [end_position]
        sections = {
            section_heading: case[start:end]
            for section_heading, start, end in zip(
                section_headings, boundaries, boundaries[1:]
            )
        }
        sections[end_heading] = case.split(end_heading, 1)[1].split(
            platform_heading, 1
        )[0]
        return sections

    def test_decision_corpus_has_independent_reviewer_conflict_cases(self) -> None:
        """Protect each conflict case's route in its expected/action/prohibited sections."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        cases = (
            (
                "## EVAL-30:",
                "## EVAL-31:",
                (
                    "同じ snapshot の diff は、決済 idempotency 判定と外部 payment gateway I/O",
                    "responsibility-boundary-reviewer は、純粋な冪等性判定 Calculation と外部 gateway I/O Action を別 service へ分離し",
                    "over-engineering-reviewer は、その分離案のうち既存 Action を一度呼ぶだけの PaymentGatewayService は純粋な pass-through",
                    "この2つの修正案は同時には成立しないが、両方の問題は妥当である",
                ),
                (
                    "diff 変更ありの場合は、新しい同一 snapshot で親QA、必須完了ゲート、競合当事者の専門 reviewer、変更後も対象 risk が成立する全専門 reviewer を再実行してから受け入れる",
                    "多数決を使わず、各 finding の問題と修正案を分け、evidence、問題の妥当性、代替解法、AC、外部／repository 指示の優先順位、具体的失敗リスク、影響、発生可能性、検証可能性、scope、rollback、最小修正、保守性を比較する",
                ),
                (
                    "diff 変更ありの修正後は新しい同一 snapshot で親QA、必須完了ゲート、競合当事者、残存risk の専門 reviewer を再実行する",
                    "全対象 reviewer を同じ diff snapshot へ起動し、全 findings と evidence を親が収集する",
                    "問題の妥当性と修正案の有効性を分離し、上記の比較軸と選択理由を記録する",
                ),
                (
                    "一部の findings だけを根拠に diff を変更し、同一 snapshot の再実行を省略する",
                    "reviewer の人数や多数決だけで競合を決める",
                ),
                (
                    "競合の具体的な reviewer 名",
                    "同等に安全で検証可能な代替解法",
                    "diff 変更ありと新しい同一 snapshot の再実行は固定し、親の比較責任、多数決禁止、同一 snapshot の収集は共通である",
                ),
            ),
            (
                "## EVAL-31:",
                "## EVAL-32:",
                (
                    "再現順序は「DB update → audit API 成功 → DB commit 失敗」であり、audit 済みだが session/token 未失効の部分成功になる",
                    "同期 audit API を commit 前に完了させる案",
                    "commit 失敗時に外部 side effect を DB rollback できず",
                    "許容不能 risk と AC-1 違反を残す",
                    "transaction 内 outbox から commit 後に audit API を送る案",
                    "外部 audit 失敗時に DB transaction を rollback するという AC-2 を満たさない",
                ),
                (
                    "review-patch-refactorer ではなく元 Implementer へ差し戻す",
                    "再設計後の新しい同一 snapshot で親QA、必須完了ゲート、競合当事者、変更後も対象 risk が成立する全専門 reviewer を再実行してから受け入れる",
                ),
                (
                    "競合している reviewer 名",
                    "指摘を識別できる情報",
                    "守る AC",
                    "元 Implementer",
                    "再設計条件",
                    "差し戻し後は元 Implementer の protocol 再設計（守る AC は変更しない）と実装を待ち、新しい同一 snapshot でこの節の変更後 snapshot 再実行契約を満たす",
                ),
                (
                    "安全に解消できない競合を review-patch-refactorer の局所修正へ送る",
                    "再設計後の同一 snapshot reviewer 再実行なしに受け入れる",
                ),
                (
                    "守る AC を変更しない",
                    "Implementation Plan の AC 確定",
                    "ユーザー確認",
                    "Branch Plan の再生成",
                    "再検証",
                    "再承認",
                ),
            ),
            (
                "## EVAL-32:",
                "# 結果記録",
                (
                    "security-side-effect-reviewer は「token が log に出る可能性がある」と指摘するが",
                    "file / 行、再現手順、参照 Data の path / id のいずれも示さず",
                    "repository の現状からも該当出力を確認できない",
                ),
                (
                    "evidence 不成立の finding は問題を検証できないため、finding ごとの理由付き不採用として完了する",
                ),
                (
                    "修正 routing をしない、snapshot 変更なしで完了し、AC 1〜2 の既存 green 検証を親が確認する",
                ),
                (
                    "review-patch-refactorer または元 Implementer へ修正 routing する",
                    "finding を理由なしに消す、または多数決で不採用にする",
                    "snapshot を変更して reviewer を再実行する",
                ),
                (),
            ),
        )
        for heading, next_heading, input_contracts, expected, required, prohibited, allowed in cases:
            sections = self._decision_case_sections(corpus, heading, next_heading)
            input_section = self._normalize_contract(sections["**入力**"])
            expected_section = sections["**期待する判断**"]
            required_section = sections["**必須動作**"]
            prohibited_section = sections["**禁止動作**"]
            expected_section = self._normalize_contract(expected_section)
            required_section = self._normalize_contract(required_section)
            prohibited_section = self._normalize_contract(prohibited_section)
            allowed_section = self._normalize_contract(sections["**許容される差異**"])
            for contract in input_contracts:
                with self.subTest(case=heading, section="input", contract=contract):
                    self.assertIn(self._normalize_contract(contract), input_section)
            if heading == "## EVAL-30:":
                self.assertEqual(2, input_section.count("payments.py:140-151"))
            for contract in expected:
                with self.subTest(case=heading, section="expected", contract=contract):
                    self.assertIn(self._normalize_contract(contract), expected_section)
            for contract in required:
                with self.subTest(case=heading, section="required", contract=contract):
                    self.assertIn(self._normalize_contract(contract), required_section)
            for contract in prohibited:
                with self.subTest(case=heading, section="prohibited", contract=contract):
                    self.assertIn(self._normalize_contract(contract), prohibited_section)
            for contract in allowed:
                with self.subTest(case=heading, section="allowed", contract=contract):
                    self.assertIn(self._normalize_contract(contract), allowed_section)
