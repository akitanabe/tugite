"""Repository contracts for impl-lead review gates and bounded fixes."""

from __future__ import annotations

from pathlib import Path
import unittest

from build_plugin_assets_test_support import (
    REPOSITORY_ROOT,
    RepositoryContractSupport,
)


class ImplLeadReviewGateContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def test_repository_workflows_route_specialists_and_require_mandatory_completion_gates(
        self,
    ) -> None:
        """Require both completion gates without making risk-based specialists mandatory."""
        workflows = self._repository_workflow_texts()
        risk_routes = {
            "responsibility-boundary-reviewer": "責務混在、設計境界、分散した副作用",
            "test-quality-reviewer": "弱いテスト、欠けているケース、実装詳細に依存したテスト",
            "security-side-effect-reviewer": (
                "外部 I/O、破壊的操作、機密データ、セキュリティ影響"
            ),
        }
        required_rules = (
            "ユーザーが専門 reviewer を明示的に要求した場合。",
            "親が reviewer の責務と一致する具体的なリスクを特定した場合。",
            "専門 reviewer を汎用コードレビューの代替にしない。",
            "専門 reviewer は mode 名だけを理由に一律起動しない。",
            "対象リスクがない専門 reviewer を無条件で起動しない。",
            "対象リスクと review 範囲を明示する。",
            "- 必須完了ゲート",
            "この表の2本は必須の完了ゲートであり、上記の任意起動条件の対象外とする。",
            (
                "`writing-principles-reviewer` は `lite` / `standard` / `strict` の"
                "すべてで、各実装枝を受け入れる前に必ず起動する。"
            ),
            (
                "`over-engineering-reviewer` は `standard` / `strict` の枝でだけ、"
                "受け入れる前に必ず起動し"
            ),
            "各ゲートを起動する相は「枝レビューの3相」で定める。",
            "この節は適用 mode の正本であり、相への割り当てを持たない。",
            "reviewer は最終的な受け入れ判断を行わない。",
            "親が diff、テスト、検証結果を確認し、最終的な受け入れを判断する。",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized_workflow = "".join(workflow.split())

                for name, risk in risk_routes.items():
                    self.assertIn(f"| `{name}` | {risk} |", workflow)
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized_workflow)
                self.assertNotIn("`writing-principles-refactorer`", workflow)

    def _qa_and_integration_reference_texts(self) -> dict[str, str]:
        skills = self._repository_skill_texts()
        return {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }

    @staticmethod
    def _normalize_contract(text: str) -> str:
        return "".join(text.replace("`", "").split())

    def _qa_section(self, reference: str, heading: str) -> str:
        self.assertEqual(1, reference.count(heading))
        return reference.split(heading, 1)[1].split("\n## ", 1)[0]

    def test_repository_specialist_launch_conditions_live_only_in_specialist_section(
        self,
    ) -> None:
        """Keep the specialist launch conditions in one section and subordinate the rest."""
        # 起動条件が複数節に分散すると、reviewer を1つ増やすたびに全節が同期点になる。
        # 具体的な判断材料（層・外部 I/O・abstraction・責務混在）は risk 表1行目の
        # 具体例として正本側へ残す。文の1本化で判断材料まで失うと起動判断ができない。
        specialist_risk_examples = (
            "複数層、複数の外部 I/O、新しい abstraction・adapter・service、責務混在の疑い",
        )
        subordination_contracts = (
            "「専門 reviewer」節の起動条件に従って起動する",
            "この節は専門 reviewer の起動条件を独自に定義しない",
        )
        # 起動条件の文を移す際に同居していた義務を巻き添えで落とさないための下限。
        responsibility_obligations = (
            "`問題なし`: 通過。",
            "`軽微` / `修正推奨`: 局所的で全起動条件を満たす場合だけ "
            "`review-patch-refactorer`、それ以外は元 Implementer。",
            "`修正必須`: 解消するまで完了しない。",
            "`responsibility-boundary-reviewer` は修正しない。",
            "diff にない既存問題は「既存課題」として判定から分ける。",
        )
        for platform, reference in self._qa_and_integration_reference_texts().items():
            with self.subTest(platform=platform):
                specialist = self._qa_section(reference, "## 専門 reviewer")
                responsibility = self._qa_section(reference, "## 責務境界")

                normalized_specialist = self._normalize_contract(specialist)
                for example in specialist_risk_examples:
                    self.assertIn(
                        self._normalize_contract(example), normalized_specialist
                    )

                normalized_responsibility = self._normalize_contract(responsibility)
                for contract in subordination_contracts:
                    self.assertIn(
                        self._normalize_contract(contract), normalized_responsibility
                    )
                for obligation in responsibility_obligations:
                    self.assertIn(
                        self._normalize_contract(obligation), normalized_responsibility
                    )
                self.assertNotIn(
                    self._normalize_contract(
                        "責務混在の疑いがある場合は "
                        "`responsibility-boundary-reviewer` を起動する"
                    ),
                    normalized_responsibility,
                )

    def test_repository_integration_step_five_only_defines_reviewer_handoff(
        self,
    ) -> None:
        """Read step 5 as a handoff rule that never decides whether to launch."""
        for platform, reference in self._qa_and_integration_reference_texts().items():
            with self.subTest(platform=platform):
                integration = self._qa_section(reference, "## 返却と統合")
                step_5 = integration.split("\n5. ", 1)[1].split("\n6. ", 1)[0]
                normalized_step_5 = self._normalize_contract(step_5)

                self.assertIn(
                    self._normalize_contract(
                        "起動するかどうかは「専門 reviewer」節の起動条件だけで決まり、"
                        "この手順は渡す Data と diff の受け渡しだけを定める"
                    ),
                    normalized_step_5,
                )
                # 渡す Data の列挙は「reviewer 起動テンプレート」節がこの手順を名指しで
                # 参照しているため、受け渡し規約として保持する。
                for handoff_data in (
                    "task、AC、commit 範囲、変更ファイル、diff text、対象 risk",
                    "diff artifact の絶対 path を渡すことを既定とし",
                ):
                    self.assertIn(
                        self._normalize_contract(handoff_data), normalized_step_5
                    )

    def test_repository_over_engineering_gate_applies_only_to_standard_and_strict(
        self,
    ) -> None:
        """Apply the over-engineering gate to standard and strict branches only."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        # 適用 mode の正本はゲート表なので、表の行と mode 文言だけを pin する。
        # `lite` を除外する根拠の散文は、文言の微修正だけで red になる割に
        # 「`lite` へ誤って適用される」欠陥をこの2つより先に検出しない。
        gate_rows = (
            (
                "| 記述原則 | `writing-principles-reviewer` "
                "| `lite` / `standard` / `strict` "
                "| How/What/Why/Why Not の配置、命名、説明 |"
            ),
            (
                "| 過剰実装 | `over-engineering-reviewer` "
                "| `standard` / `strict` "
                "| 除去しても AC と制約を満たせるテストと実装 |"
            ),
        )
        mode_rules = (
            "適用 mode の正本はこの表とする。",
            (
                "`over-engineering-reviewer` は `standard` / `strict` の枝でだけ、"
                "受け入れる前に必ず起動し、`lite` では起動しない。"
            ),
        )
        # 根拠の散文は上記方針どおり広くは pin しない。`lite` の親 QA 範囲を広げたときに
        # 除外根拠が旧範囲を指したまま残る矛盾だけを、根拠が依存する2点で検出する。
        exclusion_grounds = (
            (
                "除去許可の判定に必要な網羅性の確認"
                "（観点2: 境界値・異常系・例外経路・分岐・期待値の根拠）が課されない。"
            ),
            (
                "`lite` が課すのは AC と検証の対応の識別までであり、"
                "その検証が AC をどこまで支えているかの判断は課さない。"
            ),
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in gate_rows + mode_rules + exclusion_grounds:
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_over_engineering_gate_bounds_parent_approved_removal(
        self,
    ) -> None:
        """Approve each removal per finding id and return unlocatable coverage."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        approval_conditions = (
            "### 過剰実装ゲートの除去許可",
            "親は指摘IDごとに次をすべて確認する。",
            "除去後も対象 AC を満たす実装と検証が残ること",
            "除去しても外部から観測可能な振る舞いと公開契約が変わらないこと",
            "除去する操作が局所的で、周辺の再設計を必要としないこと",
            "1つでも満たさない場合は元 Implementer へ差し戻す",
        )
        type_c_route = (
            "類型 C（残る検証を特定できないテスト）は `review-patch-refactorer` へ渡さず、"
            "元 Implementer へ差し戻す"
        )
        duplicate_test_identification = (
            "削除する側と残す側をファイルとテスト名で特定",
            "個別許可のない除去を行わせない",
        )
        launch_inputs = (
            "除去を許可する場合の、指摘IDごとの除去対象と残す対象",
            "pass-through 層の除去では、付け替えが必要な呼び出し箇所のファイルを"
            "変更許可リストへ含める",
        )
        # 「テストケースの削除」単体は親の再確認リストにも現れるため、
        # 変更制約側へ入ったことは文全体で pin しないと判定できない。
        scope_constraint = (
            "新規作成・削除・移動、指摘外のテストケース追加、テストケースの削除、"
            "fixture や helper の追加をさせない。"
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in (
                    approval_conditions
                    + duplicate_test_identification
                    + launch_inputs
                    + (type_c_route, scope_constraint)
                ):
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_workflow_passes_selected_reviewer_context(self) -> None:
        """Pass baseline review data plus purpose-selected context, never the whole repo."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        baseline_inputs = (
            "レビュー対象とリスクに応じて、必要な周辺コンテキストを選択して reviewer へ渡す",
            "タスクの目的",
            "Acceptance Criteria",
            "変更対象と commit 範囲",
            "変更ファイル一覧と diff text",
            "reviewer に確認させる具体的な観点",
        )
        optional_inputs = (
            "関連する interface、type、schema",
            "主要な呼び出し元",
            "関連する既存テスト",
            "周辺の directory 構造",
            "generated file とその生成元",
            "変更対象に関係する既存実装",
            "外部指示",
            "`AGENTS.md`",
            "`CLAUDE.md`",
            "`README.md`",
        )
        selection_constraints = (
            "repository 全体を無条件に渡さない",
            "reviewer の役割に関係しない情報を過剰に渡さない",
            "親の結論だけを渡さず、reviewer が独立して判断できる一次情報を渡す",
            "周辺コードを渡す場合は、なぜ必要なのかを明示する",
            "外部指示と repository 内の指示が競合する場合は、優先関係を明示する",
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in (
                    baseline_inputs + optional_inputs + selection_constraints
                ):
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_specialist_reviewers_accept_parent_selected_context(
        self,
    ) -> None:
        """Use parent-selected context as evidence without widening the review scope."""
        reviewer_sources = (
            "responsibility-boundary-reviewer",
            "test-quality-reviewer",
            "security-side-effect-reviewer",
        )
        required_contracts = (
            "親が選択した周辺コンテキスト",
            "指摘範囲を広げる理由にしない",
        )

        for name in reviewer_sources:
            with self.subTest(name=name):
                source = self._repository_text(Path("shared/agents") / f"{name}.md")
                for contract in required_contracts:
                    self.assertIn(contract, source)

    def test_repository_decision_corpus_extends_reviewer_context(self) -> None:
        """Evaluate purpose-selected reviewer context with independent primary evidence."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        eval_06 = corpus.split(
            "## EVAL-06: 責務混在が見える返却 diff",
            1,
        )[1].split("## EVAL-07:", 1)[0]
        required_contracts = (
            "周辺コンテキストを選択し、必要な理由と併せて渡す",
            "repository 全体を無条件に渡す",
            "一次情報を渡さない",
            "選択理由を明示し",
        )

        for contract in required_contracts:
            with self.subTest(contract=contract):
                self.assertIn(contract, eval_06)

    def test_repository_decision_corpus_requires_read_only_writing_review_gate(
        self,
    ) -> None:
        """Evaluate the mandatory writing review as a read-only post-return gate."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        common_responsibilities = corpus.split(
            "### 全委譲ケースで親が保持する責任",
            1,
        )[1].split("## 共通の手動評価手順", 1)[0]
        eval_08 = corpus.split(
            "## EVAL-08: 機能的に green だが記述原則を外す差分",
            1,
        )[1].split("## EVAL-24:", 1)[0]

        section_boundaries = {
            "expected decision": ("**期待する判断**", "**必須動作**"),
            "required actions": ("**必須動作**", "**禁止動作**"),
            "prohibited actions": ("**禁止動作**", "**許容される差異**"),
            "manual checks": ("**手動評価項目**", None),
        }
        eval_sections = {}
        for name, (start, end) in section_boundaries.items():
            self.assertEqual(1, eval_08.count(start))
            section = eval_08.split(start, 1)[1]
            if end is not None:
                self.assertEqual(1, section.count(end))
                section = section.split(end, 1)[0]
            eval_sections[name] = section

        with self.subTest(contract="retired agent name"):
            self.assertNotIn("writing-principles-refactorer", corpus)
        with self.subTest(contract="retired completion gate role"):
            self.assertNotIn("記述 refactorer", corpus)

        for contract in (
            "`writing-principles-reviewer`",
            "`lite`、`standard`、`strict`",
            "必須の完了ゲート",
            "各実装枝を受け入れる前",
        ):
            with self.subTest(
                section="common responsibilities",
                contract=contract,
            ):
                self.assertIn(contract, common_responsibilities)

        section_contracts = {
            "expected decision": (
                "専門 reviewer を追加せず",
                "`writing-principles-reviewer` を最終差分へ起動する",
                "reviewer は自身で変更せず",
                "`no-change` または指摘ID付きの Data",
                "親が各指摘ID",
                "修正先または不採用",
            ),
            "required actions": (
                "親が先に diff と test",
                "`review-patch-refactorer` へ渡す",
                "元 Implementer へ差し戻す",
                "修正後は親QA",
                "reviewer 再確認",
            ),
            "prohibited actions": (
                "`writing-principles-reviewer` 自身にファイル変更",
                "reviewer の指摘を親が確認せず",
                "修正先の選択や不採用判断を reviewer に委ねる",
                "責務・test・security reviewer を一律起動する",
                "reviewer の判定を親の受け入れ判断に置き換える",
            ),
            "manual checks": (
                "read-only の `writing-principles-reviewer` を必須ゲート",
                "`no-change` または指摘ID付き Data",
                "親が各指摘ID",
                "`review-patch-refactorer`、元 Implementer、不採用",
                "修正後に親QAと reviewer 再確認",
                "親が最終受け入れ判断",
            ),
        }
        for section_name, contracts in section_contracts.items():
            for contract in contracts:
                with self.subTest(section=section_name, contract=contract):
                    self.assertIn(contract, eval_sections[section_name])

    def test_repository_mandatory_gates_accept_no_change_result(self) -> None:
        """Pass any mandatory gate whose review reports no findings."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        required_contracts = (
            "no-change",
            "指摘が0件",
            "正常なゲート通過結果",
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_mandatory_gates_receive_parent_collected_bounded_data(
        self,
    ) -> None:
        """Review only changed behavior using evidence collected by the parent."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        required_contracts = (
            "`git diff`",
            "`git status`",
            "commit log",
            "テスト結果",
            "親が取得",
            "Data として各必須完了ゲートの reviewer へ渡す",
            "基準 commit からの diff が導入または悪化させた問題",
            "既存問題を広く探索しない",
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_mandatory_gates_resolve_structured_findings_before_acceptance(
        self,
    ) -> None:
        """Block acceptance until every identified finding has a recorded outcome."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        required_contracts = (
            "指摘ID",
            "構造化 Data",
            "各指摘ID",
            "修正先または不採用",
            "判断を記録",
            "reviewer の指摘が0件",
            "`review-patch-refactorer` による修正後",
            # 受け入れ条件は「枝レビューの3相」の枝の受け入れ点へ一本化した。
            # この節に残るのは参照だけで、条件本体を重ねて定義しないことまで固定する。
            "枝の受け入れ可否は「枝レビューの3相」の「枝の受け入れ点」で定める。"
            "この節では受け入れ条件を重ねて定義しない。",
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_workflow_defines_review_patch_routing_boundary(self) -> None:
        """Patch only green implementations with concrete, behavior-preserving findings."""
        workflows = self._repository_workflow_texts()
        startup_conditions = (
            "専門 reviewer（必須完了ゲートの reviewer を含む）の具体的な指摘が存在する。",
            "Acceptance Criteria は満たされている。",
            "機能的なテストは green である。",
            "修正範囲が局所的である。",
            "仕様の再解釈を必要としない。",
            "新機能追加ではない。",
            "振る舞いを維持したまま修正できる。",
            "reviewer が修正方針または問題箇所を明示している。",
            "evidence を欠く指摘は、「必須完了ゲート」の evidence を欠く指摘の扱いに従い、"
            "親が evidence を補って通常の判断へ戻している。",
        )
        implementer_routes = (
            "Acceptance Criteria 未達",
            "仕様誤解",
            "機能欠落",
            "テスト失敗",
            "正常系・異常系・境界値不足",
            "振る舞い変更が必要",
            "テストケース追加",
            "ケース追加や期待値の再検討が必要",
            "仕様判断",
            "設計変更",
            "振る舞い判断",
            "`strict` mode の Red / Green / Refactor 継続",
            "過剰要素の除去に仕様判断、AC の再解釈、振る舞い変更が必要",
            "失う AC が特定できないテストの除去",
        )

        for path, workflow in workflows.items():
            with self.subTest(path=path):
                normalized_workflow = "".join(workflow.split())

                for condition in startup_conditions:
                    self.assertIn("".join(condition.split()), normalized_workflow)
                for route in implementer_routes:
                    self.assertIn("".join(route.split()), normalized_workflow)

    def test_repository_workflow_bounds_review_patch_inputs_and_parent_scope_qa(
        self,
    ) -> None:
        """Launch the patch refactorer with bounded data and re-verify scope on return."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        launch_contracts = (
            "親が指摘を確認し、修正対象として採用している。",
            "Acceptance Criteria を変更する必要がない。",
            "指摘元 reviewer、対象となる指摘ID、指摘本文",
            "親が採用した修正条件",
            "変更を許可するファイルと変更を禁止するファイル",
            "削除・移動・新規作成の可否と commit の要否",
            "必須検証 command",
            "推測で補わず、ファイルを変更せず親へ返す",
        )
        # 正規化比較は行境界を消すため、行単体の pin は限定句を行全体へ前置した
        # 劣化版も部分一致で通してしまう。前の bullet と `-` マーカーまで含めて
        # 行頭を固定する。
        parent_scope_qa = (
            "自己申告だけを信用せず",
            "基準 commit からの変更ファイル一覧と diff",
            "- 許可範囲外の変更がないこと\n"
            "- 親が個別に許可していないファイルの追加・削除・移動がないこと",
            "reviewer 指摘外の変更がないこと",
            "- 親が個別に許可していないテストケースの削除がないこと\n"
            "- テストケースの追加・変更、期待値、skip 設定の変更がないこと",
            "除去を許可した場合は、除去対象が許可した指摘IDと一致し、"
            "対象 AC を満たす実装と検証が残っていること",
            "focused test と関連する全体検証が green であること",
        )
        relaxations_beyond_removal = (
            "親が個別に許可していないテストケースの追加",
            "親が個別に許可していない期待値",
            "親が個別に許可していないskip",
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in launch_contracts + parent_scope_qa:
                    self.assertIn("".join(contract.split()), normalized_workflow)
                for relaxation in relaxations_beyond_removal:
                    self.assertNotIn(
                        "".join(relaxation.split()), normalized_workflow
                    )

    def test_repository_workflow_requires_parent_confirmed_severity_before_routing(
        self,
    ) -> None:
        """Derive every finding's severity from parent judgment before fix routing."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        heading = "## 修正先の選択"
        # AC-1 (d)
        scope_and_timing = (
            "すべての reviewer の finding は、修正先または不採用のいずれを判断するより前に、"
            "親が重要度を確定する。",
            "この適用範囲とタイミングは、以下に列挙する起動条件など本節内の他の記述の"
            "適用有無に関わらず成立する。",
        )
        # AC-1 (a)
        not_self_reported = ("親は reviewer が申告した重要度をそのまま採用しない。",)
        # AC-1 (b)
        evidence_based_grounds = (
            "親が確定する根拠は、finding の evidence と、その finding が影響する Acceptance"
            " Criteria・対象 risk への影響である。",
            "reviewer 原稿が `軽微` / `修正推奨` / `修正必須` の意味を定めている範囲については、"
            "その記述を正本として照合する。",
            "現状、`impl-lead` が起動する reviewer に限れば、この範囲は「責務境界」節が起動する"
            " reviewer の「修正コストに見合わない指摘は `軽微` として扱う」だけである。",
            "`Pass` / `Needs attention` / `Blocker` のように3区分と異なる語彙で申告する"
            " reviewer の finding は、申告語彙から3区分への写像規則を定義しないため、"
            "evidence と AC・対象 risk への影響だけから確定する。",
            "判定区分に相当する項目を持たない reviewer の finding も同じ扱いとする。",
        )
        # AC-1 (c)
        always_three_way = (
            "親が確定する値は、重要度に相当する項目を持たない finding を含め、常に"
            " `軽微` / `修正推奨` / `修正必須` のいずれかとする。",
        )
        # AC-1 (e)
        routing_points_at_confirmed_value = (
            "原稿の他の記述が `軽微` / `修正推奨` / `修正必須` で分岐する場合、その分岐は"
            " reviewer の申告値ではなく親が確定したこの値を指す。",
            "「責務境界」節の routing はこれに当たる。",
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                self.assertEqual(1, workflow.count(heading))
                section = workflow.split(heading, 1)[1].split("\n## ", 1)[0]
                normalized_section = "".join(section.split())
                for contract in (
                    scope_and_timing
                    + not_self_reported
                    + evidence_based_grounds
                    + always_three_way
                    + routing_points_at_confirmed_value
                ):
                    self.assertIn("".join(contract.split()), normalized_section)

    def test_repository_decision_corpus_bounds_review_patch_scope(self) -> None:
        """Evaluate bounded refactorer inputs and zero out-of-scope changes."""
        corpus = self._repository_text(Path("evals/workflow-decision-corpus.md"))
        eval_08 = corpus.split(
            "## EVAL-08: 機能的に green だが記述原則を外す差分",
            1,
        )[1].split("## EVAL-24:", 1)[0]
        required_contracts = (
            "指摘元 reviewer、指摘ID、指摘本文、親が採用した修正条件、変更を許可するファイル",
            "指摘外変更、許可範囲外変更、ファイルの追加・削除・移動が0件",
            "指摘外の修正、テストケース追加、ファイルの新規作成・削除・移動をさせる",
        )

        for contract in required_contracts:
            with self.subTest(contract=contract):
                self.assertIn(contract, eval_08)

    def test_repository_mandatory_gates_recheck_every_fix_before_acceptance(
        self,
    ) -> None:
        """Return every fix route to mode-scoped parent QA and the narrowed relaunch set."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        required_contracts = (
            "`review-patch-refactorer` による修正後の親QAと reviewer 再確認は、"
            "元 Implementer による修正にも適用する。",
            "`review-patch-refactorer` または元 Implementer による修正後",
            "親が変更後の diff とテスト結果を確認",
            # 親 QA の再実行が観点0・5 だけへ縮退しないことは `## 親の QA` の mode 別規定へ
            # 委ねる。ここでは委ね先を固定して、再実行義務が diff 確認だけへ痩せないようにする。
            "`## 親の QA` の mode 別の適用範囲に従って親 QA を再実行する。",
            "再確認する reviewer は\n「枝レビューの3相」の「再起動対象」で定める。",
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_mandatory_gates_do_not_ground_passage_in_missing_evidence(
        self,
    ) -> None:
        """Withhold gate passage on findings whose evidence the parent cannot verify."""
        skills = self._repository_skill_texts()
        qa_workflows = {
            "shared": skills.source_references["qa-and-integration.md"],
            "claude": skills.claude_references["qa-and-integration.md"],
            "codex": skills.codex_references["qa-and-integration.md"],
        }
        required_contracts = (
            "[Reviewer findings の共通契約](reviewer-findings.md)",
            "evidence を欠く指摘は、単独でゲート通過の根拠にしない。",
            "該当ファイルと行の引用・再現手順・参照した Data の path と id のいずれかを、"
            "自分が読んだ diff・テスト結果・repository の現状から特定できる場合は、"
            "親が evidence を補って通常の判断へ戻す。",
            "この扱いは必須完了ゲートの reviewer に限らず、"
            "「専門 reviewer」節の reviewer を含む指摘全般に適用する。",
        )

        for platform, workflow in qa_workflows.items():
            with self.subTest(platform=platform):
                normalized_workflow = "".join(workflow.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized_workflow)

    def test_repository_distribution_does_not_reference_retired_agent_names(self) -> None:
        """Remove retired names from every distributed source and generated surface."""
        paths = (
            REPOSITORY_ROOT / "shared",
            REPOSITORY_ROOT / "plugins",
            REPOSITORY_ROOT / "scripts",
            REPOSITORY_ROOT / "tests",
        )
        retired_names = (
            "refactor-patch-" + "agent",
        )

        for path in paths:
            for file_path in path.rglob("*"):
                if not file_path.is_file():
                    continue
                content = file_path.read_text(encoding="utf-8")
                for name in retired_names:
                    self.assertNotIn(name, content, file_path)


if __name__ == "__main__":
    unittest.main()
