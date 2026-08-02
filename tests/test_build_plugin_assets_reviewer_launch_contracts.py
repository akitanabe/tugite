"""Repository contracts for reviewer launch templates and diff artifacts."""

from __future__ import annotations

import unittest

from build_plugin_assets_test_support import (
    RepositoryContractSupport,
)


REVIEWER_LAUNCH_TEMPLATE_FIELDS = (
    "対象 reviewer",
    "確認させる観点",
    "Branch Plan の failure_impact.reasons",
    "親 QA が返却 diff から特定した対象リスク",
    "review 範囲",
    "タスクの目的",
    "Acceptance Criteria",
    "親が明示した制約",
    "基準 commit",
    "対象 commit 範囲",
    "commit log",
    "変更ファイル一覧",
    "diff artifact の絶対 path",
    "diff text（artifact を生成できない場合）",
    "`git status` の結果",
    "テスト結果",
    "親が選択した周辺コンテキスト",
    "そのコンテキストを渡す理由",
    "返却してほしい判定",
    "前回の指摘と親の採否（再起動時）",
)


REVIEWER_LAUNCH_SNAPSHOT_SECTION = "## reviewer 起動前後の worktree・親 checkout 照合"
# The check is written for every launch rather than for the reviewers that can
# run commands: which reviewers those are is decided in the agent definitions,
# and a rule in this document that depends on that split would go stale without
# anything failing. Naming a tool here would also collide with the ban on
# restating the read-only rule in this file.
REVIEWER_LAUNCH_SNAPSHOT_CONTRACTS = (
    "reviewer を起動する直前に、対象 worktree の `git rev-parse HEAD` と `git status --short`、"
    "および親の統合 checkout の `git rev-parse HEAD` と `git status --short` を親が記録する。",
    # Pins that the parent-checkout record is retaken after the diff artifact
    # is written, not reused from 返却と統合 手順2 (SEC-9): reusing 手順2's
    # value would always mismatch once a run creates `.tugite/` after that
    # step, discarding legitimate findings for a reason unrelated to the
    # reviewer's own behavior.
    "親の統合 checkout の記録は diff artifact の書き出し後に取り直し、"
    "「返却と統合」手順2 で取得した値を使い回さない。",
    "reviewer の返却後に同じ4つを取り直し、起動前の記録と一致することを確認する。",
    "一致しない場合、同一 `snapshot` へ一斉起動した全 `reviewer` の `findings` を採用せず破棄する。",
    "破棄した事実と件数を差異の内容とあわせて最終報告へ記録する。",
    "reviewer が到達するのは対象 worktree だけでなく親の統合 checkout でもあるため、"
    "照合はどちらか一方に絞らず両方に掛ける。",
    "この照合は起動する reviewer を選ばず、すべての reviewer 起動に掛ける。",
)


class ReviewerLaunchTemplateAndDiffArtifactContractsTest(
    RepositoryContractSupport,
    unittest.TestCase,
):
    def _extract_reviewer_launch_template(self, reference: str) -> str:
        heading = "## reviewer 起動テンプレート"
        opening_fence = "```text\n"
        closing_fence = "\n```"
        self.assertEqual(1, reference.count(heading))
        section = reference.split(heading, 1)[1].split("\n## ", 1)[0]
        self.assertEqual(1, section.count(opening_fence))
        fenced_content = section.split(opening_fence, 1)[1]
        self.assertIn(closing_fence, fenced_content)
        return fenced_content.split(closing_fence, 1)[0]

    def test_repository_reviewer_launch_template_lists_all_fields_as_independent_lines(
        self,
    ) -> None:
        """Require every reviewer-launch field on its own filled-in line inside one fence."""
        for platform, reference in self._impl_lead_reference_texts("reviewer-dispatch.md").items():
            with self.subTest(platform=platform):
                template = self._extract_reviewer_launch_template(reference)
                self.assertNotIn("{{", template)
                lines = [line for line in template.splitlines() if line.strip()]
                self.assertEqual(len(REVIEWER_LAUNCH_TEMPLATE_FIELDS), len(lines))
                for field, line in zip(REVIEWER_LAUNCH_TEMPLATE_FIELDS, lines):
                    self.assertTrue(
                        line.strip().startswith(f"- {field}:"),
                        f"{platform}: expected field '{field}' line, got {line!r}",
                    )

    def test_repository_reviewer_launch_template_is_mandatory_and_reachable(
        self,
    ) -> None:
        """Require full field completion and let two independent sections reach it."""
        obligation_contracts = (
            "必須完了ゲートの reviewer と専門 reviewer のどちらを起動する場合も",
            "次のテンプレートの全欄を1項目ずつ埋めて渡す",
            "該当がない欄は「なし」と記入する",
            "欄を空欄のまま残すことと、欄自体を削除することを禁じる",
        )
        branch_reviews = self._impl_lead_reference_texts("branch-review.md")
        finding_routings = self._impl_lead_reference_texts("finding-routing.md")
        for platform, reference in self._impl_lead_reference_texts("reviewer-dispatch.md").items():
            with self.subTest(platform=platform):
                normalized = "".join(reference.split())
                for contract in obligation_contracts:
                    self.assertIn("".join(contract.split()), normalized)

                self.assertEqual(1, branch_reviews[platform].count("## 必須完了ゲート"))
                mandatory_gate_section = branch_reviews[platform].split(
                    "## 必須完了ゲート", 1
                )[1].split("\n## ", 1)[0]
                self.assertIn(
                    "[reviewer 起動テンプレート](reviewer-dispatch.md)",
                    mandatory_gate_section,
                )

                self.assertEqual(1, finding_routings[platform].count("## 責務境界"))
                responsibility_section = finding_routings[platform].split("## 責務境界", 1)[
                    1
                ].split("\n## ", 1)[0]
                self.assertIn(
                    "[reviewer 起動テンプレート](reviewer-dispatch.md)",
                    responsibility_section,
                )

    def test_repository_diff_artifact_creation_defines_path_and_inherited_rules(
        self,
    ) -> None:
        """Fix the diff-artifact save path and inherit only the non-Markdown QA rules."""
        required_contracts = (
            "## diff artifact の作成",
            "`.tugite/diffs/<slug>-diff.patch`",
            "slug の base の",
            "候補順と正規化手順、Windows 予約名の扱い、衝突時の suffix 選択、ancestor 検査、"
            "削除時の再検査、Git 管理は",
            "[永続 QA レポート](qa-report.md)",
            "ancestor 検査の対象 component は `.tugite` と `diffs` に読み替える",
            "Markdown file を前提とする path 制約は継承しない",
            "保持と削除の規約も継承せず、「diff artifact の削除」節で定義する",
            "target は `.tugite/diffs/` 直下の単一 file に限る",
            "file name component に path separator を許可しない",
            "`.` または `..` を許可しない",
            "絶対 path を許可しない",
            "`-diff` を保持したまま `<slug>-diff-2.patch` の順に最初の空きを選ぶ",
            "worker worktree で取得した `git -C <worktree> diff <base>...HEAD` の出力を、"
            "親が転記・要約せず",
            "1回の書き出しでそのまま保存する",
            "保存先 path は親の統合 checkout の repository root を基準に解決し、"
            "ancestor 検査も同じ root で行う",
            "同一の diff 状態（同じ実装枝、同じ commit 範囲、修正 commit の追加なし）に"
            "対する複数 reviewer の起動では同じ artifact を渡してよい",
            "diff 状態が変わったとき（修正後の再起動、別の実装枝）は新しい"
            "artifact を生成し、変化後に古い artifact を渡さない",
            "候補 path が既存の場合に上書きせず失敗する Action",
            "候補 path の衝突による失敗は次の suffix を選び直す",
            "衝突以外の書き出し失敗は「diff artifact の受け渡しと停止条件」の確認手順に従い",
            "artifact 経路を既定とし、diff text の直接受け渡しは同節の停止条件に"
            "該当する場合の例外とする",
            "保存先 directory が存在しない場合は、ancestor 検査を行ったうえで作成し、"
            "作成後に同じ検査を再実行してから書き出す",
            "report と別 directory に分けるのは",
            "diff artifact は reviewer へ diff を渡すためだけの中間物で run 完了時に削除する",
            "保持規約の異なる file を同じ directory へ混在させない",
        )
        for platform, reference in self._impl_lead_reference_texts("reviewer-dispatch.md").items():
            with self.subTest(platform=platform):
                normalized = "".join(reference.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized)
                creation_section = reference.split(
                    "## diff artifact の作成", 1
                )[1].split("\n## ", 1)[0]
                self.assertNotIn("{{", creation_section)

    def test_repository_diff_artifact_handoff_confirms_and_stops_on_secrets(
        self,
    ) -> None:
        """Confirm the write before handoff and fall back to diff text on stop conditions."""
        required_contracts = (
            "## diff artifact の受け渡しと停止条件",
            "起動 prompt の diff artifact 欄には絶対 path を書く",
            "永続 QA レポートと会話上の報告へ path を記録する場合は"
            "repository 相対 path だけを使う",
            "verbatim 保存される diff 本文はこの記録規則の適用対象にしない",
            "reviewer がその file を Read し全文を diff text として判定根拠にする旨の指示を添える",
            "その text を判定根拠にする旨を添える",
            "2つの欄は排他とし、採らなかった側の欄には「なし」と記入して、"
            "両方を同時に有効な指示として残さない",
            "token、password、cookie、Authorization、private key、`.env` の値、"
            "credential 付き URL、個人情報のいずれかを含む場合",
            "作成 Action を保証できない場合は artifact を生成せず、diff text 欄へ本文を"
            "直接記入して渡し、生成しなかった理由を記録する",
            "repository 相対 path、コード中の文字列リテラル、prompt テンプレートの原稿は、"
            "diff が構造上含む要素として停止条件に該当しない",
            "親は diff 全文を自分の context へ読み込まずに書き出し結果を確認する",
            "書き出し command の exit status が 0 であることと、"
            "artifact が空でないことの2点で行う",
            "commit を持つ実装枝に対して artifact が空になった場合は、取得元 worktree または"
            "基準 commit の指定誤りとして扱う",
            "満たさない artifact は reviewer へ渡さず",
            "「diff artifact の削除」の手順で削除したうえで再生成し、"
            "再生成できない場合は diff text 経路へ落ちる",
        )
        for platform, reference in self._impl_lead_reference_texts("reviewer-dispatch.md").items():
            with self.subTest(platform=platform):
                normalized = "".join(reference.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized)

    def test_repository_diff_artifact_is_deleted_when_the_run_completes(
        self,
    ) -> None:
        """Discard diff artifacts at cleanup instead of inheriting report retention."""
        required_contracts = (
            "## diff artifact の削除",
            "diff artifact は run 完了時に削除する",
            "[後始末](run-closeout.md) で、この run に生成した diff artifact をすべて破棄するとき",
            "[永続 QA レポート](qa-report.md) の削除時の再検査を行い、"
            "対象が `.tugite/diffs/` 配下の通常 file であることを確認する",
            "symlink、directory、非通常 file は削除しない",
            "`.tugite/diffs/` が空になった場合は directory も削除する",
            "差し戻しまたは再検証の可能性がある間は後始末の削除を始めない",
            "削除できない artifact は理由と repository 相対 path を最終報告に含める",
        )
        cleanup_contracts = (
            "この run に生成した diff artifact を"
            "[diff artifact の削除](reviewer-dispatch.md) の手順で削除する",
            "永続 QA レポートと `<slug>-tests.md` は削除しない",
        )
        closeouts = self._impl_lead_reference_texts("run-closeout.md")
        for platform, reference in self._impl_lead_reference_texts("reviewer-dispatch.md").items():
            with self.subTest(platform=platform):
                normalized = "".join(reference.split())
                for contract in required_contracts:
                    self.assertIn("".join(contract.split()), normalized)

                cleanup_section = closeouts[platform].split("## 後始末", 1)[1].split(
                    "\n## ", 1
                )[0]
                normalized_cleanup = "".join(cleanup_section.split())
                for contract in cleanup_contracts:
                    self.assertIn("".join(contract.split()), normalized_cleanup)

    def test_repository_existing_reviewer_launch_sites_connect_to_diff_artifact_path(
        self,
    ) -> None:
        """Connect the four existing launch-data sites to the artifact-path route."""
        owned_connections = {
            "qa-and-integration.md": (
                "この確認によって worker の変更の混入と誤認しない",
                "ここでの作業 tree は worker worktree を指し、親の統合 checkout に保存した"
                "diff artifact を reviewer が Read することとは矛盾しない",
                "diff artifact の絶対 path を渡すことを既定とし、artifact を生成できない場合だけ"
                "diff text 欄へ本文を直接記入する",
            ),
            "reviewer-dispatch.md": (
                "この基本情報は「reviewer 起動テンプレート」の各欄に対応する",
                "「専門 reviewer」節の2つのリスク入力と review 範囲、"
                "[返却と統合](qa-and-integration.md) 手順5 の task・AC・commit 範囲・変更ファイル・"
                "diff text を含め、reviewer 起動時に渡す Data はすべて"
                "このテンプレートの欄として吸収する",
                "テンプレート外に残る起動時 Data はない",
            ),
            "branch-review.md": (
                "起動 prompt は [reviewer 起動テンプレート](reviewer-dispatch.md) の全欄を埋めて渡す",
            ),
            "finding-routing.md": (
                "起動時は [reviewer 起動テンプレート](reviewer-dispatch.md) の全欄を埋め、"
                "diff artifact の絶対 path を渡すことを既定とする",
            ),
        }
        reference_groups = {
            "qa-and-integration.md": self._qa_and_integration_reference_texts(),
            "reviewer-dispatch.md": self._impl_lead_reference_texts("reviewer-dispatch.md"),
            "branch-review.md": self._impl_lead_reference_texts("branch-review.md"),
            "finding-routing.md": self._impl_lead_reference_texts("finding-routing.md"),
        }
        for name, references in reference_groups.items():
            for platform, reference in references.items():
                with self.subTest(name=name, platform=platform):
                    normalized = "".join(reference.split())
                    for contract in owned_connections[name]:
                        self.assertIn("".join(contract.split()), normalized)

    def test_return_and_integration_exempts_parent_written_artifacts_from_contamination(
        self,
    ) -> None:
        """Exempt every artifact the parent side writes from the contamination check."""
        # `feature-lead` の一括経路では `plan-craft` が起草直後にプラン文書を書くため、
        # 最初の枝を受ける時点で `.tugite/plans/` がすでに untracked として存在する。
        # 除外しないと、親が worker の変更の混入と誤認して枝が `Needs revision` へ落ちる。
        required = (
            "`plan-craft` が書き出したプラン artifact(`.tugite/plans/` 配下)も"
            "親側が書き出した既知の untracked file として同じ扱いとし、"
            "worker の変更の混入と誤認しない",
            "[プラン artifact](../../plan-craft/references/plan-artifacts.md)",
        )
        for platform, reference in self._qa_and_integration_reference_texts().items():
            with self.subTest(platform=platform):
                section = reference.split("## 返却と統合", 1)[1].split("\n## ", 1)[0]
                normalized = "".join(section.split())
                for contract in required:
                    self.assertIn("".join(contract.split()), normalized)

    def test_repository_reviewer_launch_compares_the_worktree_before_and_after(
        self,
    ) -> None:
        """Reject findings from a launch whose review target moved while the reviewer held it."""
        for platform, reference in self._impl_lead_reference_texts("reviewer-dispatch.md").items():
            with self.subTest(platform=platform):
                self.assertEqual(
                    1, reference.count(REVIEWER_LAUNCH_SNAPSHOT_SECTION)
                )
                self.assertIn(
                    REVIEWER_LAUNCH_SNAPSHOT_SECTION.removeprefix("## "),
                    reference.split("## 目次", 1)[1].split("\n## ", 1)[0],
                )
                section = reference.split(REVIEWER_LAUNCH_SNAPSHOT_SECTION, 1)[
                    1
                ].split("\n## ", 1)[0]
                normalized_section = "".join(section.split())
                for contract in REVIEWER_LAUNCH_SNAPSHOT_CONTRACTS:
                    with self.subTest(contract=contract):
                        self.assertIn(
                            "".join(contract.split()), normalized_section
                        )
                self.assertNotIn(
                    "一致しない場合、そのreviewerのfindingsを採用しない",
                    normalized_section,
                )

    def test_repository_reviewer_launch_treats_artifact_hash_delta_as_mismatch_and_keeps_inline_text_outside_scope(
        self,
    ) -> None:
        """Treat a changed handed-off artifact as a batch mismatch and exclude inline diff text."""
        for platform, reference in self._impl_lead_reference_texts("reviewer-dispatch.md").items():
            with self.subTest(platform=platform):
                section = reference.split(REVIEWER_LAUNCH_SNAPSHOT_SECTION, 1)[1].split(
                    "\n## ", 1
                )[0]
                normalized = self._normalize_contract(section)
                for contract in (
                    "diff artifact の絶対 path を渡して起動した場合、親は起動直前と返却後にその artifact の内容 hash を記録し、一致することを確認する",
                    "diff text 欄へ本文を直接記入して起動した場合は、この確認の対象外とする",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), normalized)
                self.assertNotIn(
                    self._normalize_contract(
                        "diff text 欄へ本文を直接記入して起動した場合は、この確認の対象とする"
                    ),
                    normalized,
                )

                parent_mismatch = normalized.split(
                    self._normalize_contract("親の統合 checkout の差異"), 1
                )[1]
                for contract in (
                    "渡した diff artifact の内容 hash が一致しない場合",
                    "Needs revision として統合しない",
                    "不一致になった diff artifact は以後の reviewer 起動へ再利用せず",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), parent_mismatch)

    def test_repository_reviewer_launch_confines_untracked_cleanup_to_quiescent_exact_target_and_post_delete_recheck(
        self,
    ) -> None:
        """Require safe cleanup to finish before rerunning a mismatched launch."""
        for platform, reference in self._impl_lead_reference_texts("reviewer-dispatch.md").items():
            with self.subTest(platform=platform):
                section = reference.split(REVIEWER_LAUNCH_SNAPSHOT_SECTION, 1)[1].split(
                    "\n## ", 1
                )[0]
                normalized = self._normalize_contract(section)
                target_marker = self._normalize_contract(
                    "対象 worktree の新規非追跡項目だけが差異である場合"
                )
                other_marker = self._normalize_contract("対象 worktree のその他の差異")
                self.assertIn(target_marker, normalized)
                self.assertIn(other_marker, normalized)
                target_only = normalized.split(target_marker, 1)[1].split(
                    other_marker, 1
                )[0]

                for contract in (
                    "全 reviewer の返却または停止を確認してから",
                    "削除対象を再検査",
                    "対象 worktree の root 内に限定",
                    "起動前になかった非追跡の項目",
                    "削除後に対象 worktree の git rev-parse HEAD と git status --short",
                    "削除後に親の統合 checkout の git rev-parse HEAD と git status --short",
                    "削除後に渡した diff artifact の内容 hash",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), target_only)

                self.assertTrue(
                    any(
                        marker in target_only
                        for marker in (
                            "symlinkを辿らず",
                            "symlinkを追従せず",
                            "symlinkのリンク先を削除しない",
                        )
                    ),
                    f"{platform}: cleanup must not follow symlinks",
                )
                self.assertLess(
                    target_only.index("全reviewerの返却または停止を確認してから"),
                    target_only.index("削除対象を再検査"),
                )
                self.assertLess(
                    target_only.index("削除対象を再検査"),
                    target_only.index("同じ相を再実施する"),
                )
                self.assertLess(
                    target_only.index("削除後に対象worktreeのgitrev-parseHEADとgitstatus--short"),
                    target_only.index("同じ相を再実施する"),
                )
                self.assertLess(
                    target_only.index("削除後に親の統合checkoutのgitrev-parseHEADとgitstatus--short"),
                    target_only.index("同じ相を再実施する"),
                )
                self.assertLess(
                    target_only.index("削除後に渡したdiffartifactの内容hash"),
                    target_only.index("同じ相を再実施する"),
                )

                failure_marker = self._normalize_contract("削除に失敗した場合")
                success_marker = self._normalize_contract("全条件が成立した場合だけ")
                self.assertIn(failure_marker, target_only)
                self.assertIn(success_marker, target_only)
                failure = target_only.split(failure_marker, 1)[1].split(
                    success_marker, 1
                )[0]
                success = target_only.split(success_marker, 1)[1]
                for contract in (
                    "削除対象が残存する場合",
                    "追加差異がある場合",
                    "unsafe candidate",
                    "Needs revision",
                    "再実施せず",
                ):
                    with self.subTest(route="failure", contract=contract):
                        self.assertIn(self._normalize_contract(contract), failure)
                self.assertNotIn("同じ相を再実施する", failure)
                for contract in (
                    "同じ相を再実施する",
                    "再実施は新たな round を消費する",
                ):
                    with self.subTest(route="success", contract=contract):
                        self.assertIn(self._normalize_contract(contract), success)
                self.assertNotIn(self._normalize_contract("Needs revision"), success)

    def test_repository_reviewer_launch_limits_observation_section_to_points_and_findings_contract(
        self,
    ) -> None:
        """Keep assurance limits in the read-only contract instead of the observation list."""
        observation_marker = self._normalize_contract("この照合が観測する対象は")
        read_only_reference = self._normalize_contract(
            "観測できない範囲を担保としてどう扱うかは [Reviewer findings の共通契約](reviewer-findings.md) の「read-only の担保」を正本とする"
        )
        observation_points = (
            "対象 worktree の git rev-parse HEAD",
            "親の統合 checkout の git rev-parse HEAD",
            "git status --short が示す追跡ファイルの状態（内容変更を含む）と非追跡の項目の増減",
            "渡した diff artifact の内容",
            "非追跡 directory 配下の個別ファイルの増減と内容変更は観測しない",
            "ignore 対象のファイルへの書き込みも観測しない",
        )
        # The canonical read-only reference is intentionally inside this
        # boundary. Do not ban generic 「担保」 wording or the reference
        # itself; only these finite limit markers describe a prohibited
        # assurance claim that would exceed the observation contract.
        assurance_limit_markers = (
            "担保対象外",
            "担保しない",
            "保証しない",
            "保証できない",
            "防止できない",
            "防止を保証",
            "外部副作用",
            "network送信",
            "credential参照",
        )
        for platform, reference in self._impl_lead_reference_texts("reviewer-dispatch.md").items():
            with self.subTest(platform=platform):
                section = reference.split(REVIEWER_LAUNCH_SNAPSHOT_SECTION, 1)[1].split(
                    "\n## ", 1
                )[0]
                normalized = self._normalize_contract(section)
                self.assertIn(observation_marker, normalized)
                observation = normalized.split(observation_marker, 1)[1].split(
                    self._normalize_contract("一致しない場合"), 1
                )[0]
                for contract in observation_points:
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), observation)
                for marker in assurance_limit_markers:
                    with self.subTest(marker=marker):
                        self.assertNotIn(self._normalize_contract(marker), observation)
                self.assertIn(read_only_reference, observation)

    def test_repository_reviewer_launch_discards_all_snapshot_findings_and_reports_mismatch(
        self,
    ) -> None:
        """Discard the whole launch batch and keep mismatch facts out of acceptance state."""
        for platform, reference in self._impl_lead_reference_texts("reviewer-dispatch.md").items():
            with self.subTest(platform=platform):
                section = reference.split(REVIEWER_LAUNCH_SNAPSHOT_SECTION, 1)[1].split(
                    "\n## ", 1
                )[0]
                normalized = self._normalize_contract(section)
                for contract in (
                    "同一 snapshot へ一斉起動した全 reviewer の findings を採用せず破棄する",
                    "破棄した findings は、settled の定義1番目が言う「その時点までに受け取った全指摘」にも、枝の受け入れ点が言う「未解決または判断未記録の指摘」にも含めない",
                    "破棄した事実と件数を差異の内容とあわせて最終報告へ記録する",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), normalized)
                self.assertNotIn(
                    "一致しない場合、そのreviewerのfindingsを採用しない",
                    normalized,
                )

    def test_repository_reviewer_launch_retries_after_target_only_untracked_addition_in_run_worktree(
        self,
    ) -> None:
        """Restore only a run-local untracked addition and rerun the same phase."""
        for platform, reference in self._impl_lead_reference_texts("reviewer-dispatch.md").items():
            with self.subTest(platform=platform):
                section = reference.split(REVIEWER_LAUNCH_SNAPSHOT_SECTION, 1)[1].split(
                    "\n## ", 1
                )[0]
                normalized = self._normalize_contract(section)
                marker = self._normalize_contract(
                    "対象 worktree の新規非追跡項目だけが差異である場合"
                )
                self.assertIn(marker, normalized)
                target_addition = normalized.split(marker, 1)[1].split(
                    self._normalize_contract("対象 worktree のその他の差異"), 1
                )[0]
                for contract in (
                    "対象 worktree はこの run 専用に作成した一時領域",
                    "起動前になかった非追跡の項目を親が削除して記録済み snapshot へ戻す",
                    "同じ相を再実施する",
                    "再実施は新たな round を消費する",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), target_addition)

    def test_repository_reviewer_launch_needs_revision_without_restore_for_target_head_tracked_or_untracked_removal(
        self,
    ) -> None:
        """Stop without restoration when the target HEAD, tracked state, or untracked set regresses."""
        for platform, reference in self._impl_lead_reference_texts("reviewer-dispatch.md").items():
            with self.subTest(platform=platform):
                section = reference.split(REVIEWER_LAUNCH_SNAPSHOT_SECTION, 1)[1].split(
                    "\n## ", 1
                )[0]
                normalized = self._normalize_contract(section)
                marker = self._normalize_contract("対象 worktree のその他の差異")
                self.assertIn(marker, normalized)
                target_other = normalized.split(marker, 1)[1].split(
                    self._normalize_contract("親の統合 checkout の差異"), 1
                )[0]
                for contract in (
                    "HEAD または追跡ファイルが記録値と異なる場合",
                    "非追跡の項目が減少・消失した場合",
                    "復旧を試みず",
                    "Needs revision として統合しない",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), target_other)
                self.assertNotIn("同じ相を再実施する", target_other)

    def test_repository_reviewer_launch_needs_revision_without_restore_for_parent_or_artifact_mismatch(
        self,
    ) -> None:
        """Keep parent checkout and artifact mismatches unrepaired and out of later launches."""
        for platform, reference in self._impl_lead_reference_texts("reviewer-dispatch.md").items():
            with self.subTest(platform=platform):
                section = reference.split(REVIEWER_LAUNCH_SNAPSHOT_SECTION, 1)[1].split(
                    "\n## ", 1
                )[0]
                normalized = self._normalize_contract(section)
                marker = self._normalize_contract("親の統合 checkout の差異")
                self.assertIn(marker, normalized)
                parent_mismatch = normalized.split(marker, 1)[1]
                for contract in (
                    "HEAD または git status --short が記録値と異なる場合",
                    "渡した diff artifact の内容 hash が一致しない場合",
                    "親の統合 checkout にある項目を自動で復旧・削除せず",
                    "Needs revision として統合しない",
                    "不一致になった diff artifact は以後の reviewer 起動へ再利用せず",
                    "run 完了時の通常の後始末で扱う",
                ):
                    with self.subTest(contract=contract):
                        self.assertIn(self._normalize_contract(contract), parent_mismatch)
                self.assertNotIn("自動で復旧・削除する", parent_mismatch)

    def test_repository_reviewer_launch_prioritizes_parent_disposition_when_both_checkouts_differ(
        self,
    ) -> None:
        """Use the parent-checkout disposition when both observed checkouts differ."""
        for platform, reference in self._impl_lead_reference_texts("reviewer-dispatch.md").items():
            with self.subTest(platform=platform):
                section = reference.split(REVIEWER_LAUNCH_SNAPSHOT_SECTION, 1)[1].split(
                    "\n## ", 1
                )[0]
                normalized = self._normalize_contract(section)
                self.assertIn(
                    self._normalize_contract(
                        "両方に差異がある場合は、親の統合 checkout に差異がある側の処分を採る"
                    ),
                    normalized,
                )

    def test_repository_git_status_step_distinguishes_own_diff_artifact_from_worker_changes(
        self,
    ) -> None:
        """Reach a rule that separates the parent's own diff artifact from contamination."""
        for platform, reference in self._qa_and_integration_reference_texts().items():
            with self.subTest(platform=platform):
                integration_steps = reference.split("## 返却と統合", 1)[1].split(
                    "\n## ", 1
                )[0]
                step_2 = integration_steps.split("2. 親は", 1)[1].split("3. ", 1)[0]
                normalized_step_2 = "".join(step_2.split())
                self.assertIn(
                    "".join("親の統合 checkout に生成した diff artifact".split()),
                    normalized_step_2,
                )
                self.assertIn(
                    "".join(
                        "作成規約は [diff artifact の作成](reviewer-dispatch.md) に従う".split()
                    ),
                    normalized_step_2,
                )


if __name__ == "__main__":
    unittest.main()
