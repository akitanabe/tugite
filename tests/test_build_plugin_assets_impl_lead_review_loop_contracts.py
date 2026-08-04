"""Repository contracts for post-return diff-unit replanning."""

from __future__ import annotations

from pathlib import Path
import unittest

from build_plugin_assets_test_support import RepositoryContractSupport


class ImplLeadReviewLoopContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _four_phase_sections(self, reference: str) -> dict[str, str]:
        heading = "## 枝レビューの4相"
        self.assertEqual(1, reference.count(heading))
        section = reference.split(heading, 1)[1].split("\n## ", 1)[0]
        subsection_headings = (
            "### 1 round の数え方",
            "### 打ち切り条件",
            "### 枝の受け入れ点",
            "### initial レビュー群",
            "### レビューループ",
            "### 最終レビュー群",
            "### 完了レビュー群",
        )
        for subheading in subsection_headings:
            self.assertEqual(1, reference.count(subheading))
        positions = [section.index(subheading) for subheading in subsection_headings]
        self.assertEqual(sorted(positions), positions)
        boundaries = positions + [len(section)]
        return {
            subheading: section[start:end]
            for subheading, start, end in zip(
                subsection_headings, boundaries, boundaries[1:]
            )
        } | {"__all__": section}



    def test_workflows_bound_branch_review_rounds_and_define_two_post_exhaustion_exceptions(
        self,
    ) -> None:
        """Count completion review runs and bound the total at the limit plus two."""
        for platform, reference in self._impl_lead_reference_texts("branch-review.md").items():
            with self.subTest(platform=platform):
                sections = self._four_phase_sections(reference)
                counting = self._normalize_contract(sections["### 1 round の数え方"])
                termination = self._normalize_contract(sections["### 打ち切り条件"])

                # 計数単位を snapshot ではなく相の実施に置く。同一 snapshot へ複数の相が
                # 走るため、snapshot 基準では最終レビュー群が round を消費しなくなる。
                self.assertIn("1roundは相の1回の実施とする", counting)
                self.assertIn(
                    "起動対象のreviewerが0名でも実施があれば1roundと数え、起動件数には依存しない",
                    counting,
                )
                self.assertIn(
                    "modeにより相の起動対象が存在しない相は実施せずroundを消費しない（liteの最終レビュー群を含む）",
                    counting,
                )
                self.assertIn(
                    "相4の実施も同一通番の1roundとして数える",
                    counting,
                )
                self.assertIn("通番は枝あたりとし", counting)
                self.assertIn("枝の途中でリセットしない", counting)

                for contract in (
                    "settled",
                    "rounds-exhausted",
                    "branch_review_roundsは枝あたりのround上限で、既定は12とする",
                    "親が[修正先の選択](finding-routing.md)で修正必須として確定した指摘が"
                    "解消されている。理由付き不採用だけではsettledにしない",
                    "上限規則が発火するのは、枝の受け入れ点が未達のまま新たなroundが必要になった場合だけである",
                    "settled済みsnapshotへの最終レビュー群の実施が未了である場合のその1回だけを",
                    "完了レビュー群の前提条件を満たしたsnapshotへの完了レビュー群の実施が未了である場合のその1回だけを",
                    "この上界はroundの種類を問わず一様に掛かり、再構成起動もこれに従う",
                    "枝あたりの総round数は上限＋2で有界になる",
                    "rounds-exhaustedで打ち切った枝は受け入れない",
                    "standard/strictの枝を過剰実装ゲート未実施のまま受け入れることはない",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), termination)

                # 上限値は Branch Plan schema へ持ち出さない。持ち出すと branch-design 側の
                # 契約変更を伴い、feature-lead の rounds_limit とも名前空間が交差する。
                self.assertIn(
                    "値はこの節に閉じて持ち、BranchPlanその他の外部Dataへfieldを追加しない",
                    termination,
                )
                self.assertNotIn("上限＋1", termination)
                self.assertIn(
                    "相の「実施が完了した」とは、その実施で得たfindingsを親が受領し、指摘があればその採否を記録した状態",
                    termination,
                )
                self.assertIn("指摘0件のno-change", termination)
                self.assertIn("全指摘を理由付き不採用にした場合", termination)
                self.assertIn(
                    "D9により破棄された実施はroundを消費するが実施完了に当たらず",
                    termination,
                )
                self.assertIn(
                    "例外で実施した相がD9により破棄された場合は、その相を再実施せず",
                    termination,
                )

    def test_workflows_route_completion_findings_without_loop_reentry(self) -> None:
        """Keep completion findings in their bounded route and out of loop rounds."""
        for platform, reference in self._impl_lead_reference_texts("branch-review.md").items():
            with self.subTest(platform=platform):
                sections = self._four_phase_sections(reference)
                completion = self._normalize_contract(sections["### 完了レビュー群"])
                for contract in (
                    "writing-principles-reviewerを全modeで1回実施する",
                    "D9の照合不一致による再実施だけをその1回の例外とし",
                    "この相の指摘をレビューループへ戻さない",
                    "起動は通常のreviewer起動テンプレートで行い、量的な絞り込みを加えない",
                    "前回の指摘と親の採否",
                    "通常どおり適用され",
                    "不採用済み指摘の再申告を新規として扱わない",
                    "レビューの再起動は行わず、相2への復帰も元Implementerへの差し戻しもしない",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), completion)

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
                    # 再実行対象の列挙は4相節の「再起動対象」へ一本化した。ここに独自の
                    # 列挙が戻ると、絞り込み規約と別内容の2規約が同じ状況へ指示を出す。
                    "「枝レビューの4相」の「再起動対象」が定めるreviewerを起動して",
                    "受け入れ可否は同節の「枝の受け入れ点」に従う",
                    "前のsnapshotのfindingを自動的に解消済みとみなさない",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(contract, rerun)
                for contract in (
                    "親だけではreviewer競合を安全に解消できない場合",
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

    def test_decision_corpus_has_independent_reviewer_conflict_cases(self) -> None:
        """Protect each conflict case's route in its expected/action/prohibited sections."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        cases = (
            (
                "## EVAL-30:",
                "## EVAL-31:",
                (
                    "initial レビュー群で responsibility-boundary-reviewer が、純粋な冪等性判定 Calculation と外部 gateway I/O Action を別 service へ分離し",
                    "親はこの指摘を採用し、gateway 呼び出しを委譲する PaymentGatewayService を切り出す修正を routing した",
                    "その確定 snapshot に対する最終レビュー群で over-engineering-reviewer が、切り出された PaymentGatewayService は既存 Action を一度呼ぶだけの純粋な pass-through なので除去し",
                    "この修正案は親が採用済みの分離判断と同時には成立しないが、両方の問題は妥当である",
                ),
                (
                    "比較の相手は前の snapshot の finding ではなく、親が記録した分離採用の判断とその根拠である",
                    "最終レビュー群の指摘を採用して diff が変わった場合はレビューループへ戻し、再起動対象が定める reviewer を起動する",
                    "復帰した round で over-engineering-reviewer は起動しない",
                    "多数決を使わず、各 finding の問題と修正案を分け、evidence、問題の妥当性、代替解法、AC、外部／repository 指示の優先順位、具体的失敗リスク、影響、発生可能性、検証可能性、scope、rollback、最小修正、保守性を比較する",
                ),
                (
                    "diff 変更ありの修正後はレビューループへ戻し、新しい同一 snapshot で親QAと再起動対象の reviewer を実施する",
                    "再収束後に最終レビュー群を再度実施する",
                    "最終レビュー群の全 findings と evidence を親が収集してから routing を決める",
                    "問題の妥当性と修正案の有効性を分離し、上記の比較軸と選択理由を記録する",
                ),
                (
                    "一部の findings だけを根拠に diff を変更し、レビューループへの復帰と再収束後の最終レビュー群を省略する",
                    "復帰した round で over-engineering-reviewer を再起動する",
                    "reviewer の人数や多数決だけで競合を決める",
                ),
                (
                    "競合の具体的な reviewer 名",
                    "同等に安全で検証可能な代替解法",
                    "diff 変更ありでのレビューループ復帰と再収束後の最終レビュー群の再実施は固定し、親の比較責任、多数決禁止、相ごとの findings 収集は共通である",
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
                    "再設計後の新しい同一 snapshot では modeに応じた相1の起動集合（initialレビュー群の集合）を再構成し、親QAと、変更後もfailure_impact.reasonsの対象が成立する専門 reviewer を実施する",
                    "親の最終受入判断は相4の完了後に行う",
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
                    "再設計後の snapshot で initial レビュー群の起動集合を再構成せずに受け入れる",
                ),
                (
                    "守る AC を変更しない",
                    "プラン文書の AC 確定",
                    "ユーザー確認",
                    "Branch Plan の再生成",
                    "再検証",
                    "再承認",
                ),
            ),
            (
                "## EVAL-32:",
                "## EVAL-33:",
                (
                    "security-side-effect-reviewer は「token が log に出る可能性がある」と指摘するが",
                    "file / 行、再現手順、参照 Data の path / id のいずれも示さず",
                    "repository の現状からも該当出力を確認できない",
                    "完了レビュー群で writing-principles-reviewer が no-change を返し",
                ),
                (
                    "evidence 不成立の finding は問題を検証できないため、finding ごとの理由付き不採用として完了する",
                    "完了レビュー群の no-change を受領した後",
                ),
                (
                    "完了レビュー群の実施を完了してから、修正 routing をしない、snapshot 変更なしで完了し、AC 1〜2 の既存 green 検証を親が確認する",
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
                self.assertEqual(1, input_section.count("payments.py:140-151"))
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

    def test_workflows_split_branch_review_into_four_phases(self) -> None:
        """Assign each gate to its phase without weakening the mode table."""
        for platform, reference in self._impl_lead_reference_texts("branch-review.md").items():
            with self.subTest(platform=platform):
                sections = self._four_phase_sections(reference)
                all_phases = self._normalize_contract(sections["__all__"])
                initial = self._normalize_contract(sections["### initial レビュー群"])
                final = self._normalize_contract(sections["### 最終レビュー群"])
                completion = self._normalize_contract(sections["### 完了レビュー群"])

                self.assertIn(
                    "initialレビュー群・レビューループ・最終レビュー群・完了レビュー群の4相で進める",
                    all_phases,
                )
                self.assertIn(
                    "この節は各ゲートをどの相で起動するかだけを定め、必須完了ゲート表が定める適用modeを覆さない",
                    all_phases,
                )
                self.assertIn("standard/strict", initial)
                self.assertIn("writing-principles-reviewer", initial)
                self.assertIn("選んだ専門reviewerを起動する", initial)
                self.assertIn("lite", initial)
                self.assertIn("起動せず", initial)
                self.assertNotIn("writing-principles-reviewerの枝あたり最低1回", initial)

                # 相への割り当ての正本はこの節だけとする。initial 群が
                # over-engineering-reviewer を起動しないことが issue #103 の中核なので、
                # 「含まれない」側も列挙の有無で判定できる形に固定する。
                self.assertIn(
                    "standard/strictの相1ではwriting-principles-reviewerと、[専門reviewer](reviewer-dispatch.md)の起動条件により",
                    initial,
                )
                self.assertNotIn("over-engineering-reviewerを実施", initial)
                self.assertIn(
                    "settledに到達した確定snapshotに対してover-engineering-reviewerを実施する",
                    final,
                )
                self.assertIn("実施の計数単位は収束ごとに1回とする", final)
                # 収束後に置く根拠は判定軸の成立条件であってコストではない。
                # コスト由来の根拠へ書き換わると、中間 snapshot へ戻す改訂を止められない。
                self.assertIn("起動回数の削減のためではない", final)
                self.assertIn(
                    "diffの最終形に対してのみ安定して成立し、中間snapshotでの判定は後続の修正で無効化されうる",
                    final,
                )
                self.assertIn(
                    "settledに到達している",
                    completion,
                )
                self.assertIn("最終レビュー群が起動対象を持つmodeでは", completion)
                self.assertIn("その実施が完了し", completion)
                self.assertIn("起動対象を持たないmode（lite）では", completion)
                self.assertIn("settled到達をもってこの前提を満たす", completion)
                self.assertIn(
                    "writing-principles-reviewerを全modeで1回実施する",
                    completion,
                )

    def test_workflows_select_specialists_from_the_specialist_section_alone(
        self,
    ) -> None:
        """Point the initial phase at one specialist section instead of enumerating sites."""
        for platform, reference in self._impl_lead_reference_texts("branch-review.md").items():
            with self.subTest(platform=platform):
                sections = self._four_phase_sections(reference)
                initial = self._normalize_contract(sections["### initial レビュー群"])

                self.assertIn(
                    "[専門reviewer](reviewer-dispatch.md)の起動条件は、この相のユーザー明示、failure_impact.reasonsとの責務一致、または返却diff由来の対象リスクによる選択と、レビューループroundの「再起動対象」の第2類型の双方へ効く",
                    initial,
                )
                # 起動条件の所在を数え上げると、起動指示が増えるたびにこの列挙が
                # 同期漏れを起こす。所在は「専門 reviewer」節ひとつに閉じる。
                self.assertIn(
                    "起動条件は[専門reviewer](reviewer-dispatch.md)節だけが定める",
                    initial,
                )
                for enumerated_site in ("「返却と統合」手順5", "「責務境界」節"):
                    with self.subTest(enumerated_site=enumerated_site):
                        self.assertNotIn(
                            self._normalize_contract(enumerated_site), initial
                        )

    def test_workflows_use_failure_impact_reasons_for_review_and_rollback(self) -> None:
        """Route safety review and rollback checks from recorded failure impact."""
        contracts = {
            "reviewer-dispatch.md": (
                "`security-side-effect-reviewer` と rollback の確認は主に `failure_impact.reasons` を入力にし",
                "`implementation_complexity` や枝 mode だけを理由に専門 reviewer を選ばない。",
            ),
            "qa-and-integration.md": (
                "`failure_impact.reasons` に記録された失敗伝播、部分成功、rollback 影響を確認する。",
                "rollback の確認を `implementation_complexity` から導出しない。",
            ),
        }
        for reference_name, required in contracts.items():
            for platform, reference in self._impl_lead_reference_texts(
                reference_name
            ).items():
                normalized = self._normalize_contract(reference)
                with self.subTest(reference=reference_name, platform=platform):
                    for contract in required:
                        self.assertIn(self._normalize_contract(contract), normalized)

    def test_workflows_handle_zero_target_initial_phase_and_mode_specific_phase_skips(
        self,
    ) -> None:
        """Advance a lite branch with no phase-one target without spending a round."""
        for platform, reference in self._impl_lead_reference_texts("branch-review.md").items():
            with self.subTest(platform=platform):
                sections = self._four_phase_sections(reference)
                initial = self._normalize_contract(sections["### initial レビュー群"])
                counting = self._normalize_contract(sections["### 1 round の数え方"])
                for contract in (
                    "相1の起動対象が0名になった枝（liteかつ専門reviewerの起動条件が1本も成立しない枝）",
                    "相1の起動対象が0名になった枝（liteかつ専門reviewerの起動条件が1本も成立しない枝）は、指摘0件のままsettledに到達したものとして扱い、相3へ進む",
                    "この枝のround通番は、最初に実施した相の実施をround1とする",
                    "相3の起動対象がない場合は相3を実施せず、roundを消費せずに相4へ進む",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), initial)
                for contract in (
                    "modeにより相の起動対象が存在しない相は実施せずroundを消費しない（liteの最終レビュー群を含む）",
                    "起動対象が空でも実施される復帰roundと再構成起動は、現行どおり実施としてroundを消費する",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), counting)


    def test_workflows_count_integrity_reexecution_as_new_round_and_limit_it_to_phase_three_or_four(
        self,
    ) -> None:
        """Make the post-exhaustion snapshot-reexecution boundary observable for phases three and four."""
        for platform, reference in self._impl_lead_reference_texts("branch-review.md").items():
            with self.subTest(platform=platform):
                sections = self._four_phase_sections(reference)
                counting = self._normalize_contract(sections["### 1 round の数え方"])
                termination = self._normalize_contract(sections["### 打ち切り条件"])

                self.assertIn(
                    self._normalize_contract(
                        "照合不一致による対象 worktree の新規非追跡項目だけの削除後に同じ相を再実施する場合、再実施は新たな round を消費する"
                    ),
                    counting,
                )
                for contract in (
                    "branch_review_roundsが12のstandard枝でround12に相4を実施し、その返却後照合が非追跡ファイルの増加だけで不一致になった場合は、例外1回でround13へ相4を再実施する",
                    "同じ枝のround12が相2で同じ不一致になった場合は、例外を持たないため再実施せず、rounds-exhaustedで打ち切った枝として受け入れない",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), termination)

    def test_workflows_reject_repeatedly_discarded_exception_reexecution(self) -> None:
        """Do not loop after an exception-phase rerun is discarded a second time."""
        for platform, reference in self._impl_lead_reference_texts("branch-review.md").items():
            with self.subTest(platform=platform):
                termination = self._normalize_contract(
                    self._four_phase_sections(reference)["### 打ち切り条件"]
                )
                for contract in (
                    "rounds-exhausted到達後の例外で実施した相を再実施した場合、その再実施が再びD9により破棄されたときは、再々実施せず",
                    "その枝をNeeds revisionとして統合しない",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), termination)

    def test_workflows_exclude_both_completion_gates_from_relaunch_targets_and_accept_only_after_completion(
        self,
    ) -> None:
        """Relaunch only eligible reviewers and require completion review before acceptance."""
        for platform, reference in self._impl_lead_reference_texts("branch-review.md").items():
            with self.subTest(platform=platform):
                sections = self._four_phase_sections(reference)
                loop = self._normalize_contract(sections["### レビューループ"])
                acceptance = self._normalize_contract(sections["### 枝の受け入れ点"])

                for contract in (
                    "各roundにも全findingsの収集barrierが掛かる",
                    "この規約はレビューループroundの起動対象を定める唯一の規約であり",
                    "直前のdiff変更のきっかけとなった指摘を出したreviewer、"
                    "および同じ競合解消で修正案が採用されなかった競合当事者",
                    "指摘が出た相は問わず",
                    "変更後にfailure_impact.reasonsとの責務一致または返却diff由来の対象リスクが新たに成立するreviewer",
                    "第2類型の判定対象は専門reviewerである",
                    "必須完了ゲート2本は第1類型と第2類型の対象外とし、レビューループroundの起動対象から除外する",
                    "この2類型は起動し、これ以外は起動しない",
                    "over-engineering-reviewer",
                    "writing-principles-reviewer",
                    "前者の再確認は最終レビュー群、後者の再確認は完了レビュー群が担う",
                    "最終レビュー群から復帰したroundではover-engineering-reviewerを起動せず",
                    "その snapshot では mode に応じた相1の起動集合（initial レビュー群の集合）を再構成し",
                    "再構成起動は同一通番の1roundとして数え",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), loop)
                self.assertNotIn(
                    "修正が記述原則の対象（命名、コメント、テスト名、説明）へ触れた場合はwriting-principles-reviewerがこれに当たる",
                    loop,
                )

                # 受け入れ点はここだけに置く。必須完了ゲート節や責務境界節へ2つ目の
                # 定義が戻ると、同じ状況に対して2つの受け入れ規約が同時に成立する。
                for contract in (
                    "受け入れ可否を決める条件はここだけに置き、他の節で別内容を定義しない",
                    "レビューループがsettledに到達している",
                    "完了レビュー群の実施が完了し、その指摘の全採否が記録され、採用分の修正・親QA・green確認が完了している",
                    "完了レビュー群の実施前提（最終レビュー群の完了と、それを持たないmodeの書き分けを含む）は「完了レビュー群」節が定める",
                    "完了レビュー群のものを含む全指摘に採否が記録され、不採用には理由が記録されている",
                    "未解決または判断未記録の指摘を残していない",
                    "親が[修正先の選択](finding-routing.md)で修正必須として確定した指摘が解消されている。"
                    "理由付き不採用だけでは受け入れ点を満たさない",
                    "[責務境界](finding-routing.md)の判定区分ごとの列挙は修正先のroutingだけを定める",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), acceptance)
                self.assertNotIn(
                    "liteの枝は最終レビュー群に起動対象がないため実施せず、settledがそのまま受け入れ点になる",
                    acceptance,
                )






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
                    "プラン文書の AC 確定とユーザー確認へ戻る",
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
                    # barrier の起動対象は4相節が相ごとに定める。ここで reviewer 名や
                    # ゲート集合を再掲すると起動対象の正本が二重化するため、参照だけを固定する。
                    "その相で起動対象となるreviewer",
                    "initialレビュー群では「枝レビューの4相」のinitialレビュー群が定める集合",
                    "レビューループroundでは同節の「再起動対象」が定める集合",
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
