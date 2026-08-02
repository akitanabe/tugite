"""Repository contracts for feature-lead."""

from __future__ import annotations

from pathlib import Path
import unittest

from build_plugin_assets_test_support import (
    PLATFORMS,
    RepositoryContractSupport,
    generated_skill_path,
    shared_skill_path,
)


FEATURE_LEAD_SKILL = "feature-lead"
IMPL_LEAD_SKILL = "impl-lead"
# The three skills that predate feature-lead and now have to decline a batch
# request. Their manuscripts word the non-firing clause identically so a single
# literal can be asserted against every generated file.
PRE_EXISTING_STAGE_SKILLS = ("plan-craft", "branch-design", IMPL_LEAD_SKILL)


class FeatureLeadContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _generated_texts(self) -> dict[str, str]:
        return self._generated_texts_for(FEATURE_LEAD_SKILL)

    def _generated_texts_for(self, skill: str) -> dict[str, str]:
        return {
            platform: self._repository_text(generated_skill_path(platform, skill))
            for platform in PLATFORMS
        }

    def _feature_lead_main_texts(self) -> dict[str, str]:
        # Includes the manuscript itself (not just the two generated files) so a
        # contract can Red against the file a human actually edits. Checking only
        # the generated pair would let a change to the generator's rendering (or a
        # stale manuscript the generator happens to already satisfy) pass silently.
        return {
            "source": self._repository_text(shared_skill_path(FEATURE_LEAD_SKILL)),
            **self._generated_texts(),
        }

    def _generated_frontmatter_and_body(self, text: str) -> tuple[str, str]:
        # The generated Markdown always opens with a YAML frontmatter block, so the
        # third chunk of the "---\n" split is the body. Splitting instead of matching
        # against the whole file keeps a description-only edit from satisfying a body
        # contract, which is what AC-20 asks the platform blocks to be checked for.
        _, frontmatter, body = text.split("---\n", 2)
        return frontmatter, body

    def _assert_contracts(self, contracts: tuple[str, ...]) -> None:
        for platform, text in self._generated_texts().items():
            normalized = "".join(text.split())
            for contract in contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)

    def test_feature_lead_keeps_attended_as_the_autonomy_default(self) -> None:
        """Choose unattended only when the user asks for it."""
        self._assert_contracts(
            (
                "`autonomy` の明示指定。既定は `attended` とし、ユーザーが全面委任を明示した"
                "場合だけ `unattended` を選ぶ。",
                "タスク規模、段の停止回数、進行の停滞を理由にこの Skill 側で `unattended` へ"
                "切り替えない。",
            )
        )

    def test_feature_lead_ledger_names_its_fields_and_resolution_vocabulary(
        self,
    ) -> None:
        """Record every decision point with its origin, basis kind, and resolver."""
        self._assert_contracts(
            (
                "| `stage` | `plan-craft` / `branch-design` / `impl-lead` |",
                "| `point` | 判断点。原文を言い換えずに保持する |",
                "| `origin` | `open_questions` / `unresolved_decisions` / "
                "`validation.blocking` / `round-limit` / `impl-lead-gate` |",
                "| `resolution` | 確定した内容、または未確定として記録した事実 |",
                "| `basis` | 根拠 |",
                "| `basis_kind` | `observed` / `assumed` |",
                "| `resolved_by` | `user`（`attended` での確定） / "
                "`autonomous`（`unattended` での自律解決） / "
                "`deferred`（解決も確定もされないままユーザーへ返した） |",
                "`resolved_by: deferred` は、解決も確定もされないままユーザーへ返した"
                "すべての判断点に用いる。",
                "不可逆操作を要した判断点、non-resolvable な判断点、同一段の停止に巻き込まれて"
                "未着手のまま返した resolvable な判断点がこれに当たる。",
                "`deferred` は解決を試みていた既存の判断点へ付与し、新しい台帳行を起こさない。",
            )
        )

    def test_feature_lead_defers_decisions_that_need_irreversible_operations(
        self,
    ) -> None:
        """Stop short of irreversible operations and hand the decision back unresolved."""
        self._assert_contracts(
            (
                "不可逆な操作（外部への公開・送信、tracked file の削除、履歴の書き換え、"
                "外部状態の変更）は `unattended` でも自律解決の手段に含めない。",
                "当該操作を伴わずに到達できる範囲まで進め、当該操作を要した既存の判断点へ "
                "`resolved_by: deferred` を付与し、操作が必要だった事実をその判断点の "
                "`resolution` と `basis` へ記録して、未実施のままユーザーへ返す。",
            )
        )

    def test_feature_lead_reports_the_whole_ledger_in_both_autonomy_modes(
        self,
    ) -> None:
        """Require the ledger in the final report whether or not autonomy is unattended."""
        self._assert_contracts(
            (
                "判断点は検出時に台帳へ記録し、会話上の最終報告へ全件を記載する。",
                "判断点台帳の全件を会話上の最終報告にも含める。",
                "台帳の記載は `attended` / `unattended` の双方で必須とする。",
                "`basis_kind: assumed` の項目は台帳内で区別して示し、観測事実に基づく解決と"
                "混ぜない。",
                "仮定の総数を最終報告の冒頭要約にも出す。",
            )
        )

        unattended_only_wording = "".join(
            "`unattended` では判断点台帳の全件を会話上の最終報告にも含める。".split()
        )
        for platform, text in self._generated_texts().items():
            with self.subTest(platform=platform):
                self.assertNotIn(unattended_only_wording, "".join(text.split()))

    def test_feature_lead_classifies_decision_origins_and_bounds_stage_reruns(
        self,
    ) -> None:
        """Route each origin to a rerun or a stop and spend at most one rerun per stage."""
        self._assert_contracts(
            (
                "判断点は `origin` によって resolvable と non-resolvable に分類する。",
                "resolvable は `origin: open_questions` / `origin: unresolved_decisions` / "
                "`origin: validation.blocking` と、ユーザーが `rounds_limit` の値を指定して"
                "いない場合の `origin: round-limit` である。",
                "再実行の入力には、`open_questions` と `unresolved_decisions` では確定した"
                "解決内容を、`validation.blocking` では violation の `code` / `path` / "
                "`message` そのものを載せ、`round-limit` では「`round-limit` の扱い」に従って"
                "引き上げた `rounds_limit` を載せる。",
                "non-resolvable は `origin: impl-lead-gate` と、ユーザーが `rounds_limit` の"
                "値を指定した場合の `origin: round-limit` である。",
                "`origin: impl-lead-gate` は一律 non-resolvable とする。",
                "`mode-proposal-invalid` は「`delegation.requested_mode` の設定」の写像規約に"
                "より `delegation` の設定時点で回避されるため、判断点として発生しない。",
                "分類が一意に決まらない判断点は non-resolvable として扱い停止する。",
                "再実行の計数は段側で数え、各段の再実行は一括実行を通じて1回までとする。",
                "この枠は `unattended` の自律解決による再実行にだけ掛け、`attended` で"
                "ユーザーが判断点を確定した後の再実行は計数しない。",
                "同一段が resolvable と non-resolvable を同時に返した場合は、non-resolvable が"
                "1件でもあれば再実行せず停止する。",
                "同一段が `origin: round-limit` と `origin: validation.blocking` を同時に"
                "返した場合、ユーザーが `rounds_limit` の値を指定していなければ `round-limit` を"
                "優先し、「`round-limit` の扱い」の引き上げ再実行を1回として行う。",
                "値を指定している場合は `round-limit` が non-resolvable であるため優先規則を"
                "適用せず停止する。",
                "再実行後も残る判断点と non-resolvable な判断点は、`unattended` でも停止して"
                "ユーザーへ返す。",
            )
        )

    def test_feature_lead_sets_requested_mode_without_writing_a_proposal(self) -> None:
        """Pick the table's proposal at delegation time instead of emitting a proposal."""
        self._assert_contracts(
            (
                "ユーザーが明示した mode の写像は、`impl-lead` SKILL.md の入力語彙の写像表を"
                "正本として参照する。",
                "mode が未指定の場合は `requested_mode` を `null` のまま保持する。",
                "この Skill は `delegation_mode_proposal` を書かない。",
                "`delegation` を設定するその時点で、表が提案する `{policy, baseline}` を "
                "`requested_mode` へ設定する。",
                "この設定は `delegation.authorized` の `false` から `true` への遷移1回の中で"
                "完結し、状態遷移表の親の権限行に収まる。",
                "判断点を発生させないため台帳へ新しい行を起こさない。",
                "引き上げ先は表が決めるため、この原稿へ表を複製せず正本を参照する。",
                "proposal の判定には枝の `failure_impact.level` を使い、"
                "`implementation_complexity` は使わない。",
                "引き上げた事実と引き上げ前後の `{policy, baseline}` は最終報告へ記録する。",
                "この引き上げの根拠は `impl-lead` SKILL.md の引き下げ禁止の例外条項に置く。",
                "この引き上げは `autonomy` に依らず `attended` と `unattended` の双方で"
                "適用する。",
            )
        )

    def test_feature_lead_scopes_qa_report_justifies_assumed_and_ranks_the_reading(
        self,
    ) -> None:
        """Scope out QA report fields, justify assumed basis, and rank the batch reading."""
        self._assert_contracts(
            (
                "永続 QA レポートの記録項目の規定は本 skill の範囲外であり、正本は "
                "`impl-lead` 側に置く。",
                "後者は起動前の入力に掛かる規定（「入力の確認」）であり、前者は段が判断点として"
                "返した後の記録区分（「自律解決の規律」）である。",
                "両者を同じ「仮定の禁止」で扱うと、根拠を取れない判断点が必ず停止になり "
                "`unattended` が成立しない。",
                "一括実行の明示要求そのものが `confirmation_mode: auto` の明示指定と委譲要求を"
                "兼ねる。",
                "ユーザーが `confirmation_mode` または委譲の要否を明示した場合はその明示を"
                "優先し、この読み替えは明示がない場合にだけ適用する。",
            )
        )

    def test_feature_lead_forces_attended_when_strict_full_is_requested(self) -> None:
        """Drop unattended before plan-craft runs when strict-full is requested."""
        self._assert_contracts(
            (
                "`strict-full`（`policy: fixed` かつ `baseline: strict`）が指定された場合は、"
                "`autonomy` の `unattended` を `attended` へ強制的に落とす。",
                "判定と確定は「入力の確認」の時点で行い、`plan-craft` を起動する前に "
                "`autonomy` を確定して以降の全段へ適用する。",
                "`impl-lead` 段へ入ってから落とす実装を許さず、計画段の判断点も自律解決しない。",
                "`strict-full` は枝数を提示したユーザー確認を委譲開始の条件とする語彙であり、"
                "判断点の自律解決と論理的に両立しない。",
                "落とした事実と理由を最終報告へ記録し、ユーザーが明示した `unattended` を"
                "黙って無効化しない。",
            )
        )

    def test_feature_lead_raises_rounds_limit_only_without_a_user_specified_value(
        self,
    ) -> None:
        """Treat a specified limit value as binding and a launch request as weaker."""
        self._assert_contracts(
            (
                "値の指定がない場合に限り、`rounds_limit` を既定値と同じ幅（10）だけ引き上げて"
                "段を再実行する。",
                "値の指定がある場合は引き上げず停止する。",
                "引き上げは「再実行の枠」に含めて段ごとに1回までとし、再実行後も "
                "`round-limit` に達する場合は停止する。",
                "`plan-craft` の `rounds_limit` の引き上げをユーザーの明示に限る契約は変更せず、"
                "値の指定がない場合に限りこの Skill の起動要求が引き上げの明示を兼ねるという"
                "読み替えで授権する。",
                "値の指定と起動要求による授権を同じ「明示」として扱わない。",
                "引き上げた事実と引き上げ後の値を判断点台帳と最終報告へ記録する。",
            )
        )

    def test_feature_lead_starts_from_the_stage_its_input_determines(self) -> None:
        """Start from branch-design only for an approved plan and never skip a later stage."""
        frontmatter_contract = (
            "確定済みのプラン文書とレビュー状態を渡して実装までの一括実行を要求されたときも"
            "発火し、`branch-design` から開始する。"
        )
        # 開始段は2 artifact が揃っていることで決まる。`plan_document` の path 条件を
        # 落とすと、会話内経路で提示したペアを保存して後日貼り付ける入力が判定を通り、
        # 「会話内経路は後日渡す経路を持たない」規定と二重に適合する。
        body_contracts = (
            "ユーザーが確定済みのプラン文書とレビュー状態を渡して実装までの一括実行を要求した"
            "とき。この場合は `branch-design` から開始する。",
            "レビュー状態が `status: approved` であり、その `plan_document` が repository "
            "相対 path であり、その path のプラン文書が読める場合だけ `branch-design` から"
            "開始する。",
            "それ以外の入力（自然文の要求、`status` を持たないレビュー状態、プラン文書だけを"
            "渡された入力、issue 本文や会話内のプラン）はすべて `plan-craft` から開始する。",
            "プラン文書だけを渡された場合はレビュー状態が無いものとして扱い、その path から"
            "兄弟のレビュー状態を解決しない。",
            # 命名規約が `<slug>.md` と `<slug>-review.yaml` を対にしているため、規約を
            # 知る読者ほど「同じ slug を機械的に探せばよい」という単純化に届く。それが
            # 誤りである理由を原稿へ残させる。
            "レビュー状態は承認の記録であり、推測で解決すると、そのプラン文書に対応しない"
            "レビュー状態を承認済みとして扱う経路が開くためである。",
            "`plan_document: 会話内` のレビュー状態は、プラン文書を会話上に貼り直されても"
            "開始段判定を通さず、`plan-craft` から開始する。",
            "`status` が `awaiting_review` または `blocked` のレビュー状態を"
            "渡されたとき。承認または判断点の確定を求めて差し戻す。これを判断点として台帳へ"
            "記録しない。",
            "判断点は段が返したものだけを対象とし、起動前に渡された入力を「判断点の分類」にも"
            "再実行にも掛けない。",
            "確定済みの Branch Plan を渡されたとき。この Skill の対象外であり、`impl-lead` を"
            "直接使う経路を案内する。",
            "`branch-design` から開始する場合はこの段を実行せず、渡された確定済みの"
            "プラン文書とレビュー状態をそのまま次段の入力にする。",
            "不足が blocking なら補完せず、開始段に応じた受け手へ渡す。`plan-craft` から開始"
            "する場合は `plan-craft` の `open_questions` として扱わせ、`branch-design` から"
            "開始する場合は `branch-design` の `unresolved_decisions` として扱わせる。",
            "次は `plan-craft` から開始する場合の確認項目である。`branch-design` から開始する"
            "場合は、確定済みのプラン文書とレビュー状態がこの位置を占め、受け手のない確認項目を"
            "残さない。",
            "根拠源と scope の基準は開始段に応じて一意に定める。`plan-craft` から開始する場合は"
            "要求原文をこれに充て、`branch-design` から開始する場合は確定済みプラン文書の"
            "見出し行と「scope」節と「Acceptance Criteria」節が要求原文の位置を占める。",
            "開始段より前の段は実行せず、開始段以降の段は飛ばさない。",
            "`branch-design` を省いてプラン文書とレビュー状態を直接 `impl-lead` へ渡さない。",
        )

        for platform, text in self._generated_texts().items():
            frontmatter, body = self._generated_frontmatter_and_body(text)
            normalized_frontmatter = "".join(frontmatter.split())
            normalized_body = "".join(body.split())
            with self.subTest(platform=platform, part="frontmatter"):
                self.assertIn(
                    "".join(frontmatter_contract.split()), normalized_frontmatter
                )
            for contract in body_contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized_body)

    def test_existing_skills_defer_batch_requests_to_feature_lead(self) -> None:
        """Decline a direct batch request while still running as a feature-lead stage."""
        # Asserted against the frontmatter and the body separately because the
        # description lives in per-platform marker blocks while the body is shared.
        # A whole-file match would let a body-only edit satisfy both platforms with
        # an untouched description, which is exactly the miss AC-16 asks about.
        contracts = (
            "ユーザーからプランから実装までの一括実行を直接要求された場合、および確定済みの"
            "プラン文書とレビュー状態を渡して実装までの一括実行を直接要求された場合は、"
            "`feature-lead` の責務であり発火しない。",
            "`feature-lead` の段として起動された場合はこの条件の対象外であり、"
            "通常どおり動作する。",
        )

        for skill in PRE_EXISTING_STAGE_SKILLS:
            for platform, text in self._generated_texts_for(skill).items():
                frontmatter, body = self._generated_frontmatter_and_body(text)
                for part, section in (
                    ("frontmatter", frontmatter),
                    ("body", body),
                ):
                    normalized = "".join(section.split())
                    for contract in contracts:
                        with self.subTest(
                            skill=skill,
                            platform=platform,
                            part=part,
                            contract=contract,
                        ):
                            self.assertIn("".join(contract.split()), normalized)

    def test_impl_lead_keeps_the_downgrade_ban_wording_intact(self) -> None:
        """Keep the allocation-policy downgrade ban worded as it already is."""
        contracts = (
            "引き下げ禁止の対象は配分方針 `{policy, baseline}` とする。",
            "ユーザーが明示した `baseline` を親都合で引き下げない。",
            "`policy` を親都合で `fixed` から `adaptive` へ変えない。",
        )

        for platform, text in self._generated_texts_for(IMPL_LEAD_SKILL).items():
            normalized = "".join(text.split())
            for contract in contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)

    def test_impl_lead_exempts_the_feature_lead_upgrade_from_the_downgrade_ban(
        self,
    ) -> None:
        """Let the batch route pick the table's proposal without calling it a downgrade."""
        contracts = (
            "`feature-lead` の経路で、写像した `requested_mode` が `branch-design` の "
            "branch-plan-schema.md の出力条件表が proposal を要求する組み合わせになる場合に、"
            "表が提案する `{policy, baseline}` を設定することは、この親都合の変更に含めない。",
            "ユーザーが mode を明示して一括実行を要求したことが、この引き上げの授権を兼ねる。",
            "引き上げ先は出力条件表に委ね、この原稿で別の値を選ばない。",
            "引き上げ前後の `{policy, baseline}` を記録し、引き上げが生むリスクを"
            "ユーザーへ報告する。",
            "proposal の安全性判断は `failure_impact.level` を入力にする。",
        )
        # The exception applies in both autonomy settings, so the manuscript must not
        # narrow it. A blanket ban on the word `autonomy` would also fail on unrelated
        # future mentions, so only the narrowing sentence itself is excluded.
        autonomy_narrowing = "この例外は `unattended` の場合にだけ適用する。"

        for platform, text in self._generated_texts_for(IMPL_LEAD_SKILL).items():
            normalized = "".join(text.split())
            for contract in contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)
            with self.subTest(platform=platform, contract=autonomy_narrowing):
                self.assertNotIn("".join(autonomy_narrowing.split()), normalized)

    def test_feature_lead_stops_the_whole_stage_when_any_branch_plan_is_blocked(
        self,
    ) -> None:
        """Treat a Set with any blocked Branch Plan as one stage-wide decision point."""
        # AC-8(a). The two contracts are asserted separately (one in "段の遷移と
        # 判断点の処理", one in "授権の根拠") because they are independent claims:
        # detecting the stage-wide stop does not by itself say authorization is
        # withheld unless every Branch Plan is approved.
        contracts = (
            "`branch-design` が返した Branch Plan Set のうち1件でも Branch Plan が "
            "`blocked` である",
            "この場合は特定の Branch Plan ではなく段全体を判断点として扱う。",
            "授権を設定するのは、Set の全 Branch Plan が `status: approved` を返した"
            "場合だけである。",
            "1件でも `blocked` な Branch Plan があれば段全体を判断点として扱い停止し、"
            "一部の Branch Plan だけを授権して進める経路は持たない。",
        )
        for platform, text in self._feature_lead_main_texts().items():
            normalized = "".join(text.split())
            for contract in contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)

    def test_feature_lead_authorizes_only_the_lead_branch_plan_under_attended(
        self,
    ) -> None:
        """Authorize just the order-first Branch Plan when autonomy stays attended."""
        # AC-8(b), first half. Kept as its own contract (distinct from the
        # unattended one below) so a manuscript that authorizes everything under
        # both settings still fails this test.
        contract = "`attended`（既定）では、`order` の先頭の未実行 Branch Plan だけを授権する。"
        for platform, text in self._feature_lead_main_texts().items():
            with self.subTest(platform=platform):
                self.assertIn(
                    "".join(contract.split()), "".join(text.split())
                )

    def test_feature_lead_authorizes_every_branch_plan_under_unattended(self) -> None:
        """Authorize the whole Set when autonomy is unattended."""
        # AC-8(c), first half. Kept separate from the attended contract above so the
        # attended/unattended distinction cannot collapse into one shared sentence.
        contract = "`unattended` では、Set の全 Branch Plan を授権する。"
        for platform, text in self._feature_lead_main_texts().items():
            with self.subTest(platform=platform):
                self.assertIn(
                    "".join(contract.split()), "".join(text.split())
                )

    def test_feature_lead_relays_the_boundary_stop_and_resumes_after_authorization(
        self,
    ) -> None:
        """Relay impl-lead's boundary presentation instead of copying it, then resume."""
        # AC-8(b), second half.
        contracts = (
            "`impl-lead` が境界で止まったら、`impl-lead` が提示した内容を既存の"
            "最終報告の中継規約に従ってユーザーへ返し、次の Branch Plan の授権を求める。",
            "提示内容そのものは `branch-plan-intake.md` を正本とし、この Skill へ"
            "複製しない。",
            "ユーザーが授権を確定したら、その Branch Plan から `impl-lead` を再開する。",
            "この停止は Skill の責務を果たさずに終了することではなく、Branch Plan を"
            "承認単位にした結果として意図された停止である。",
        )
        for platform, text in self._feature_lead_main_texts().items():
            normalized = "".join(text.split())
            for contract in contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)

    def test_feature_lead_records_the_boundary_passage_when_unattended(self) -> None:
        """Log that an unattended run crossed authorized boundaries and which ids."""
        # AC-8(c), second half.
        contract = (
            "境界を通過した事実と通過した Branch Plan id を最終報告へ記録する。"
        )
        for platform, text in self._feature_lead_main_texts().items():
            with self.subTest(platform=platform):
                self.assertIn(
                    "".join(contract.split()), "".join(text.split())
                )

    def test_feature_lead_keeps_the_boundary_stop_out_of_the_decision_ledger(
        self,
    ) -> None:
        """Explain, not just omit, why the boundary stop never becomes a ledger row."""
        # AC-8(d).
        contracts = (
            "`impl-lead` が未授権の Branch Plan の境界で止まることは、上の判断点の"
            "いずれにも当たらない。",
            "`origin: impl-lead-gate` として判断点台帳へ記録しない。",
            "台帳が対象とするのは段が返した判断点であり、境界の停止は授権が未設定で"
            "あることの帰結だからである。",
        )
        for platform, text in self._feature_lead_main_texts().items():
            normalized = "".join(text.split())
            for contract in contracts:
                with self.subTest(platform=platform, contract=contract):
                    self.assertIn("".join(contract.split()), normalized)

    def test_feature_lead_flow_branches_at_the_boundary_before_the_final_report(
        self,
    ) -> None:
        """Give the numbered flow a stop/resume branch instead of a straight line."""
        # Completion criterion: the numbered "全体の流れ" list must not still end at
        # step 8 presenting the first Branch Plan's final report. Extracting the
        # section (capped at the next "## ") and asserting order, not just presence,
        # is required per the branch's own constraints: a whole-file containment
        # check cannot tell "the branch sits inside the numbered flow" from
        # "the same words happen to exist elsewhere in the file", and a prior
        # branch's review already found that miss in practice.
        required_order = (
            "`order` に従って Branch Plan を実行する。",
            "`impl-lead` が未授権の Branch Plan の境界で止まった場合は",
            "手順9を行わずに",
            "その Branch Plan から手順7へ戻る",
            "`order` の全 Branch Plan の実行が終わったら",
        )
        for platform, text in self._feature_lead_main_texts().items():
            flow = text.split("## 全体の流れ", 1)[1].split("\n## ", 1)[0]
            normalized_flow = "".join(flow.split())
            positions: list[int] = []
            for phrase in required_order:
                needle = "".join(phrase.split())
                with self.subTest(platform=platform, phrase=phrase):
                    self.assertIn(needle, normalized_flow)
                positions.append(normalized_flow.find(needle))
            with self.subTest(platform=platform, check="order"):
                self.assertEqual(positions, sorted(positions))

    def test_feature_lead_has_no_remaining_branch_plan_data_wording(self) -> None:
        """Retire the pre-Set field name, including in the platform frontmatter."""
        for platform, text in self._feature_lead_main_texts().items():
            with self.subTest(platform=platform):
                self.assertNotIn("Branch Plan Data", text)

    def test_feature_lead_does_not_duplicate_impl_lead_intake_presentation_wording(
        self,
    ) -> None:
        """Point at branch-plan-intake.md instead of restating its boundary text."""
        intake_text = self._repository_text(
            Path("shared/skill/impl-lead/references/branch-plan-intake.md")
        )
        duplicated_phrase = (
            "完了済み Branch Plan の最終報告と未実行 Branch Plan の一覧を提示して、"
            "その Branch Plan の授権を要求する。"
        )
        normalized_duplicated_phrase = "".join(duplicated_phrase.split())
        # Guard the guard: if the phrase ever moves or is reworded in the intake
        # reference, this fails loudly instead of the negative assertion below
        # silently passing for the wrong reason.
        self.assertIn(
            normalized_duplicated_phrase, "".join(intake_text.split())
        )
        for platform, text in self._feature_lead_main_texts().items():
            with self.subTest(platform=platform):
                self.assertNotIn(
                    normalized_duplicated_phrase, "".join(text.split())
                )


if __name__ == "__main__":
    unittest.main()
