"""Repository contracts for impl-lead Branch Plan Set intake."""

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
BRANCH_DESIGN_SKILL = "branch-design"

# 廃止 field 名を含まない stage 概念の散文と目次項目まで検出するため、Latin 表記の
# "stage" 部分文字列の不在で検査する file。qa-report.md だけは Git の staging を指す
# 別概念の語を保持するため、この一覧から外して個別に検査する。
STAGE_FREE_IMPL_LEAD_DOCS = (
    "branch-plan-intake.md",
    "implementation-branches.md",
    "run-closeout.md",
)
# qa-report.md で `stage` を含んでよい行。Git の staging を指す保存規約の記述であり、
# 実装段階機構とは別概念である。行そのものを固定するのは、除外を「この語を含む行」で
# 表すと、同じ行の末尾へ stage 概念の一文を足す変更を素通ししてしまうため。
QA_REPORT_GIT_STAGING_LINES = (
    "利用先 repository で生成する report instance は既定では untracked / unstaged / "
    "uncommitted とする。",
    "表示されてよい。既定では `git add`、stage、commit しない。",
)


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
        """Route a confirmed Branch Plan Set through the intake reference from SKILL.md."""
        for platform, main in self._delegate_skill_texts().items():
            with self.subTest(platform=platform):
                self.assertIn(f"(references/{INTAKE_REFERENCE})", main)
                self.assertLess(len(main.splitlines()), 300)
                normalized = "".join(main.split())
                self.assertIn(
                    "".join("確定済み Branch Plan Set が渡されている場合は".split()),
                    normalized,
                )

    def test_intake_reference_carries_the_revalidation_section(self) -> None:
        """Carry the revalidation section as the canonical source."""
        moved_body = (
            "`status: approved` であり、`approval.method` が設定済みである。",
            "blocking violation code 表のうち、その Branch Plan 帰属の検査規則を入力 Data から"
            "再計算し、違反が0件である。",
        )
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                self.assertIn("## Executor 側の再検証", text)
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
            "Branch Plan Set が渡されていない場合は、現行どおり親が inline に枝を分ける。",
            "`branch-design` の使用を",
        )
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for rule in gate_rules:
                    self.assertIn("".join(rule.split()), normalized)

    def test_intake_reference_holds_the_complexity_mode_derivation_table(self) -> None:
        """Map policy and implementation complexity onto one branch mode."""
        derivation_rows = (
            "| policy | baseline | `implementation_complexity.level: low` | `medium` | `high` |",
            "| `fixed` | `lite` | `lite` | `lite` | `lite` |",
            "| `fixed` | `strict` | `strict` | `strict` | `strict` |",
            "| `adaptive` | `standard` | `lite` | `standard` | `strict` |",
            "| `adaptive` | `strict` | `standard` | `strict` | `strict` |",
        )
        required_rules = (
            "## 枝 mode の決定表",
            "本 reference は受け入れ口の規定、Executor 側の再検証、枝 mode の決定表、"
            "Branch Plan 境界の授権の正本を担う。",
            "この表を正本とし、planning Skill と Executor は同じ表を使う。",
            "`policy: fixed` では導出を行わず、全枝へ `baseline` をそのまま適用する。",
            "`{adaptive, strict}` の `low` は `lite` ではなく `standard` とする。",
            "「判断に迷う場合は基準側へ倒す」方針を `strict` baseline では `low` にも"
            "適用するのが一貫するためである。",
            "`{adaptive, strict}` は `implementation_complexity.level` の3値に対して2値しか使わず、"
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

    def test_intake_reference_derives_branch_modes_from_complexity_before_delegating(
        self,
    ) -> None:
        """Recompute modes from complexity without using failure impact."""
        required_rules = (
            "5項目を満たした後、委譲開始前に枝ごとの mode を導出する。",
            "`delegation.requested_mode` を入力語彙の写像ではなく Data として受け取り、"
            "`null` の場合は `{adaptive, standard}` を採用する。",
            "「枝 mode の決定表」から枝ごとの mode を再計算する。",
            "`failure_impact` は枝 mode の直接導出に使わない。",
            "planning Skill 側の申告や `delegation_mode_proposal` の内容を根拠にしない。",
            "導出結果は実行 Data として保持し、Branch Plan へ書き戻さない。",
        )
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized)
                self.assertNotIn(
                    "".join(
                        (
                            "欠落または3値以外の枝がある場合は決定的に導出できないため、"
                            "委譲を開始せず Branch Plan の修正を要求する。"
                        ).split()
                    ),
                    normalized,
                )

    def test_intake_reference_accepts_the_branch_plan_set_as_the_unit_of_intake(
        self,
    ) -> None:
        """Take the whole Set and run its Branch Plans in the declared order."""
        required_rules = (
            "受け入れ対象は Branch Plan Set であり、`order` に従って Branch Plan を"
            "順に実行する。",
            "親や `feature-lead` が Set をほどいて Branch Plan を1つずつ渡す形にはしない。",
        )
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized)

    def test_intake_reference_revalidates_the_set_then_each_branch_plan(self) -> None:
        """Check the Set first, then repeat the five checks per Branch Plan."""
        # 「Set 全体の検査を先に行う」と「再検証を Branch Plan ごとに繰り返す」を別々に
        # 固定する。前者だけだと、Set の検査を通した後に Branch Plan ごとの再検証が
        # 落ちる原稿でもこのテストが通ってしまう。
        # 対象 code は帰属表を正本として参照させる。個別列挙を固定すると、`impl-lead` 側に
        # 帰属表の部分複製が生まれ、schema 側で帰属が動いたときに2箇所が食い違う。
        set_wide_rules = (
            "blocking violation code 表で帰属が `Set` の code と、帰属が `両方` の code の "
            "Set 側 field とし、Set 全体の Data から再計算する。",
            "どの code がどちらの帰属かは同表を正本とし、本 reference へ複製しない。",
            "Set の `validation.blocking` が非空なら、Branch Plan 側の状態に関わらず"
            "実行を開始しない。",
        )
        per_branch_plan_rules = (
            "次の5項目は、実行対象の Branch Plan ごとに繰り返す。",
            "blocking violation code 表のうち、その Branch Plan 帰属の検査規則を入力 Data から"
            "再計算し、違反が0件である。",
            "帰属が `Set` の code は先行検査で扱い、ここでは再計算しない。",
        )
        # 「先に行う」「次の5項目」はどちらも位置で意味が決まる語なので、file 全体では
        # なく再検証節を切り出して照合し、Set の先行検査が5項目より前にあることまで見る。
        for platform, text in self._intake_reference_texts().items():
            section = text.split("## Executor 側の再検証", 1)[-1].split("\n## ", 1)[0]
            normalized = "".join(section.split())
            for rule in set_wide_rules:
                with self.subTest(platform=platform, scope="set"):
                    self.assertIn("".join(rule.split()), normalized)
            for rule in per_branch_plan_rules:
                with self.subTest(platform=platform, scope="branch-plan"):
                    self.assertIn("".join(rule.split()), normalized)
            # 順序も正規化テキスト上で判定する。生テキストを引くと、意味を変えない
            # 折り返し位置の変更だけで needle が消え、契約違反がないのに落ちる。
            # 末尾に項目5 を置いて `両方` の担当宣言を項目4 の中へ挟む。境界が無いと、
            # 同じ文が再検証節の後ろ(mode 導出の段落など)へ出ても昇順のまま通る。
            ordered_markers = (
                "Set 全体の検査を先に行う。",
                "1. `status: approved`",
                "帰属が `両方` の code は、Branch Plan 側 field をここで再計算する。",
                "5. 全枝に",
            )
            positions = []
            for marker in ordered_markers:
                normalized_marker = "".join(marker.split())
                self.assertIn(
                    normalized_marker,
                    normalized,
                    f"{platform}: 再検証節に「{marker}」がない",
                )
                positions.append(normalized.index(normalized_marker))
            with self.subTest(platform=platform, scope="order"):
                self.assertEqual(
                    sorted(positions),
                    positions,
                    f"{platform}: Set の先行検査 → 5項目の先頭 → `両方` の担当宣言 → "
                    f"5項目の末尾(境界) の順に並んでいない: {positions}",
                )

    def test_intake_reference_stops_at_an_unauthorized_branch_plan_and_asks_for_authorization(
        self,
    ) -> None:
        """Halt at an unauthorized Branch Plan and request its authorization."""
        required_rules = (
            "Branch Plan 境界の停止は、新しいゲート機構ではなく "
            "`delegation.authorized` の再検証で表す。",
            "`delegation.authorized: false` の Branch Plan に到達した時点で実行を止める。",
            "完了済み Branch Plan の最終報告と未実行 Branch Plan の一覧を提示して、"
            "その Branch Plan の授権を要求する。",
            "再検証の項目2「`delegation.authorized: true` かつ `authorized_by: user`」が"
            "そのまま境界の判定になる。",
            "ただし項目2 だけが不成立の場合は修正を要求せず、本 reference"
            "「Branch Plan 境界の授権」に従う。",
        )
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized)

    def test_intake_reference_authorizes_only_the_next_branch_plan_by_default(
        self,
    ) -> None:
        """Authorize one Branch Plan at a time unless the user asks for all of them."""
        # 3文を別々に固定する。とくに既定の授権範囲が欠けると、1回の委譲要求で全件が
        # 授権され、承認単位を Branch Plan にした意味が消える。
        required_rules = (
            "親は1回の委譲要求で全 Branch Plan を授権しない。",
            "既定では `order` の先頭の未実行 Branch Plan だけを授権する。",
            "ユーザーが全 Branch Plan の一括授権を明示した場合だけ全件を授権する。",
        )
        for platform, text in self._intake_reference_texts().items():
            normalized = "".join(text.split())
            for rule in required_rules:
                with self.subTest(platform=platform, rule=rule):
                    self.assertIn("".join(rule.split()), normalized)

    def test_intake_reference_points_tests_meaning_at_the_existing_schema_section(
        self,
    ) -> None:
        """Cite a section name that the schema reference actually carries."""
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                self.assertIn(
                    "".join("テスト種別の意味は正規スキーマの「tests の意味」に従う。".split()),
                    normalized,
                )

        schema_texts = {
            "source": self._repository_text(
                shared_skill_reference_path(BRANCH_DESIGN_SKILL, PLAN_SCHEMA_REFERENCE)
            ),
            "claude": self._repository_text(
                generated_skill_reference_path(
                    "claude", BRANCH_DESIGN_SKILL, PLAN_SCHEMA_REFERENCE
                )
            ),
            "codex": self._repository_text(
                generated_skill_reference_path(
                    "codex", BRANCH_DESIGN_SKILL, PLAN_SCHEMA_REFERENCE
                )
            ),
        }
        for platform, schema in schema_texts.items():
            with self.subTest(platform=platform, target="schema"):
                self.assertIn("## tests の意味", schema)

    def test_intake_reference_table_of_contents_matches_its_sections(self) -> None:
        """Keep the intake table of contents equal to its own section headings."""
        expected_sections = (
            "受け入れ口の規定",
            "Executor 側の再検証",
            "枝 mode の決定表",
            "Branch Plan 境界の授権",
        )
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                self.assertEqual(
                    expected_sections, self._markdown_table_of_contents(text)
                )
                self.assertEqual(
                    expected_sections, self._markdown_section_headings(text)
                )

    def test_impl_lead_surface_docs_drop_all_stage_vocabulary(self) -> None:
        """Leave no trace of the retired implementation_stages mechanism in impl-lead."""
        # 廃止 field 名を含まない stage 概念の散文と目次項目まで検出できるよう、生の
        # "stage" 部分文字列(大小無視)の不在を検査する。branch-design 側の同型テストと
        # 検査形が違うのは qa-report.md のためである。同 file は Git の staging を指す語
        # (`unstaged` / `git add`、stage) を保存規約として正当に持ち、これは実装段階機構とは
        # 別概念で本 workflow の変更対象でもないため、他4 file と同じ「stage を1件も含まない」
        # 検査を当てられない。そこで qa-report.md だけは、stage を含む行が既知の2行ちょうど
        # であることを全文で照合する。廃止 field 名はいずれも部分文字列 stage を含むため、
        # この照合が残存を検出する。保存規約の文言を改訂したときは、
        # `QA_REPORT_GIT_STAGING_LINES` も同じ変更意図で更新する。
        texts = {
            name: self._delegate_reference_texts(name)
            for name in (*STAGE_FREE_IMPL_LEAD_DOCS, "qa-report.md")
        }
        texts["SKILL.md"] = self._delegate_skill_texts()

        for name in (*STAGE_FREE_IMPL_LEAD_DOCS, "SKILL.md"):
            for platform, text in texts[name].items():
                carrying = [
                    line for line in text.splitlines() if "stage" in line.lower()
                ]
                with self.subTest(document=name, platform=platform):
                    self.assertEqual(
                        [],
                        carrying,
                        f"{name}({platform}) に廃止した implementation_stages 機構の"
                        f"語彙(stage)が残っている: {carrying}",
                    )

        for platform, report in texts["qa-report.md"].items():
            carrying = [line for line in report.splitlines() if "stage" in line.lower()]
            with self.subTest(document="qa-report.md", platform=platform):
                self.assertEqual(
                    list(QA_REPORT_GIT_STAGING_LINES),
                    carrying,
                    f"qa-report.md({platform}) の stage を含む行が、Git staging を述べる"
                    f"既知の2行と一致しない: {carrying}",
                )

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
            "`implementation_complexity.level: high` の枝を `lite` へ直接降格させない。",
            "判断材料が不足している場合は `baseline` 側へ倒す。",
            "上書きは最終報告に含める。",
            "`implementation_complexity.level` そのものが誤っていると判断した場合は、"
            "上書きではなく Branch Plan の `implementation_complexity` を修正して再検証する。",
            "上書きを implementation complexity 修正の代用にしない。",
            "上書きを受け付ける入力経路は本 reference で規定しない。",
        )
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized)

    def test_intake_reference_revalidates_both_branch_assessment_axes(self) -> None:
        """Reject invalid assessments even when planning declared the plan valid."""
        required_rules = (
            "全枝に `failure_impact` と `implementation_complexity` が存在する。",
            "両 field の `level` が `low` / `medium` / `high` のいずれかである。",
            "両 field の `reasons` が欠落しておらず、非空の文字列配列である。",
            "欠落、配列以外、空配列、空文字、非文字列要素",
            "`branch-assessment-missing`",
            "`branch-assessment-invalid`",
            "`legacy-risk-present`",
            "blocking violation code 表のうち、その Branch Plan 帰属の検査規則を入力 Data から"
            "再計算",
        )
        for platform, text in self._intake_reference_texts().items():
            with self.subTest(platform=platform):
                normalized = "".join(text.split())
                for rule in required_rules:
                    self.assertIn("".join(rule.split()), normalized)

    def test_intake_reference_rejects_legacy_risk_without_conversion(self) -> None:
        """Reject legacy risk alone or mixed with either new assessment."""
        required_rules = (
            "旧 `risk` が単独で存在する場合",
            "旧 `risk` が新しい field と混在する場合",
            "`legacy-risk-present`",
            "旧 `risk` から `failure_impact` または `implementation_complexity` を推測しない。",
            "Branch Plan の修正を要求し、委譲を開始しない。",
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
                    self.assertNotIn("allowed_paths", text)

    def test_parent_qa_observes_forbidden_path_contact_in_viewpoint_zero(self) -> None:
        """Define QA viewpoint zero as contact with forbidden paths, not generic scope drift."""
        for platform, text in self._delegate_reference_texts(
            "qa-and-integration.md"
        ).items():
            with self.subTest(platform=platform):
                qa_section = text.split("## 親の QA", 1)[1].split("\n## ", 1)[0]
                normalized = "".join(qa_section.split())
                self.assertIn(
                    "".join(
                        "`forbidden_paths` に列挙された変更禁止範囲へ接触していないこと".split()
                    ),
                    normalized,
                )
                self.assertNotIn("物理的な scope 逸脱", normalized)

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
