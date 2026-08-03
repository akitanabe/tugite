"""Repository contracts for the explicit, lightweight impl-delegate skill."""

from __future__ import annotations

from pathlib import Path
import re
import unittest

from build_plugin_assets_test_support import (
    GENERATED_MARKDOWN_WARNING,
    IMPL_DELEGATE_SKILL,
    RepositoryContractSupport,
    generated_skill_path,
    shared_skill_path,
)


class ImplDelegateContractsTest(RepositoryContractSupport, unittest.TestCase):
    """Keep the impl-delegate workflow explicit and bounded."""

    def _skill_texts(self) -> dict[str, str]:
        paths = {
            "shared": shared_skill_path(IMPL_DELEGATE_SKILL),
            "claude": generated_skill_path("claude", IMPL_DELEGATE_SKILL),
            "codex": generated_skill_path("codex", IMPL_DELEGATE_SKILL),
        }
        for path in paths.values():
            self.assertTrue(path.is_file(), path)
        texts = {
            name: self._repository_text(path)
            for name, path in paths.items()
        }
        for name, text in texts.items():
            with self.subTest(name=name):
                self.assertIn(f"name: {IMPL_DELEGATE_SKILL}", text)
                if name != "shared":
                    self.assertIn(GENERATED_MARKDOWN_WARNING, text)
        return texts

    @staticmethod
    def _frontmatter_regions(text: str) -> tuple[str, ...]:
        """Extract YAML frontmatter blocks, including platform-specific shared blocks."""
        return tuple(
            match.group(1)
            for match in re.finditer(r"(?ms)^---\n(.*?)^---\n", text)
        )

    def test_frontmatter_routes_impl_lead_and_impl_delegate_without_overlap(self) -> None:
        """Keep general impl-lead routing and explicit-only impl-delegate routing distinct."""
        impl_lead_paths = (
            Path("shared/skill/impl-lead/SKILL.md"),
            Path("plugins/claude/skills/impl-lead/SKILL.md"),
            Path("plugins/codex/skills/impl-lead/SKILL.md"),
        )
        for path in impl_lead_paths:
            text = self._repository_text(path)
            regions = self._frontmatter_regions(text)
            with self.subTest(path=path):
                self.assertTrue(regions)
                self.assertTrue(
                    all(
                        self._normalize_contract(
                            "`impl-delegate` が明示された場合は `impl-lead` を発火しない。"
                        )
                        in self._normalize_contract(region)
                        for region in regions
                    )
                )
                self.assertTrue(
                    all(
                        self._normalize_contract(
                            "一般的な実装委譲要求が明示された場合に発火する。"
                        )
                        in self._normalize_contract(region)
                        for region in regions
                    )
                )

        impl_delegate_paths = (
            Path("shared/skill/impl-delegate/SKILL.md"),
            Path("plugins/claude/skills/impl-delegate/SKILL.md"),
            Path("plugins/codex/skills/impl-delegate/SKILL.md"),
        )
        for path in impl_delegate_paths:
            text = self._repository_text(path)
            regions = self._frontmatter_regions(text)
            with self.subTest(path=path):
                self.assertTrue(regions)
                for region in regions:
                    normalized = self._normalize_contract(region)
                    self.assertIn(
                        self._normalize_contract(
                            "ユーザーが `impl-delegate` を明示した場合だけ発火する。"
                        ),
                        normalized,
                    )
                    self.assertIn(
                        self._normalize_contract(
                            "自然言語の作業内容やタスク規模から推測して発火しない。"
                        ),
                        normalized,
                    )

    def test_skill_is_explicit_only_and_excludes_impl_lead(self) -> None:
        """Fire only on an explicit skill request and keep impl-lead out of that route."""
        texts = self._skill_texts()
        for name, text in texts.items():
            with self.subTest(name=name):
                normalized = self._normalize_contract(text)
                for contract in (
                    "ユーザーが `impl-delegate` を明示的に指定した場合だけ発火する。",
                    "自然言語の作業内容やタスク規模から推測して発火しない。",
                    "`impl-delegate` が明示された場合は `impl-lead` を発火しない。",
                    "事前適用 gate は設けない。",
                ):
                    self.assertIn(self._normalize_contract(contract), normalized)

    def test_skill_uses_one_worker_with_parent_selected_implementer(self) -> None:
        """Use one normal implementer by default and senior only by parent judgment."""
        texts = self._skill_texts()
        required = (
            "1名の worker へ委譲する。",
            "通常は `implementer` を選ぶ。",
            "事前整理後も残る設計または推論判断がある場合、誤実装時の手戻りまたは rollback 負担が大きい場合、周辺機能または外部副作用への影響が大きい場合",
            "上位 model で誤実装リスクを具体的に減らせると親が判断した場合だけ `senior-implementer` を選んでよい。",
            "変更量、ファイル数、高い失敗コストというラベルだけでは `senior-implementer` に昇格しない。",
            "通常と senior で迷えば `implementer` を選ぶ。",
            "親は `senior-implementer` を選んだ具体的理由を記録して最終報告する。",
        )
        for name, text in texts.items():
            with self.subTest(name=name):
                normalized = self._normalize_contract(text)
                for contract in required:
                    self.assertIn(self._normalize_contract(contract), normalized)

    def test_skill_requires_tdd_and_parent_qa(self) -> None:
        """Require TDD and parent QA while keeping artifact checks separate."""
        texts = self._skill_texts()
        required = (
            "worker は指定された範囲で TDD の Red → Green → Refactor を必須として実施する。",
            "Red 証跡の提出は親の要求に従う。提出がないことだけを理由に成果を拒否せず",
            "親 QA は必須である。worker の返却後、親は次を自分で確認する。",
            "Red 証跡は親が要求した場合に確認する。",
            "TDD の Green と test、Acceptance Criteria、diff を再確認し、Green の検証 command を再実行すること。",
        )
        forbidden_as_requirements = (
            "Branch Plan を必須とする",
            "QA report を必須とする",
            "diff artifact を必須とする",
        )
        for name, text in texts.items():
            with self.subTest(name=name):
                normalized = self._normalize_contract(text)
                for contract in required:
                    self.assertIn(self._normalize_contract(contract), normalized)
                for contract in forbidden_as_requirements:
                    self.assertNotIn(self._normalize_contract(contract), normalized)

    def test_skill_defines_intake_parent_qa_and_closeout_contract(self) -> None:
        """Protect the lightweight workflow's intake, parent QA, and closeout boundaries."""
        texts = self._skill_texts()
        required = (
            "## Intake",
            "Issue または doc を先に読む",
            "`pwd -P`、`git branch`、基準 commit、`git status --short` を確認する",
            "既存の dirty/untracked を変更しない",
            "正本と関連 test を読む",
            "Intake 後、親が基準 commit から専用 worktree を作成する",
            "worker はその worktree のみを編集する",
            "親は同じ対象を並行編集しない",
            "専門 reviewer と writing-principles-reviewer は同じ隔離 worktree の確定 snapshot を読む",
            "review-patch-refactorer も同じ worktree を修正する",
            "基準 snapshot からの diff を確認する",
            "親が focused test を実行する",
            "生成された配布物を直接編集しない",
            "既存 test を弱体化しない",
            "scope 外の変更がない",
            "## Closeout",
            "repository-native の最終 gate",
            "最終 diff と `git status --short` を確認する",
            "安全を確認して worktree を cleanup する",
            "変更ファイル、検証 command と結果、AC 対応、残存 risk、未検証事項を報告する",
        )
        for name, text in texts.items():
            with self.subTest(name=name):
                normalized = self._normalize_contract(text)
                for contract in required:
                    self.assertIn(self._normalize_contract(contract), normalized)

    def test_skill_requires_worktree_but_not_impl_lead_artifacts(self) -> None:
        """Require isolation while keeping heavier impl-lead artifacts optional."""
        texts = self._skill_texts()
        worktree_contracts = (
            "専用 worktree を作成する",
            "専用 worktree を必須とする",
        )
        artifact_nonrequirements = (
            "Branch Plan を作成・提出しない",
            "永続 QA report を作成・提出しない",
            "独立した diff artifact を作成・提出しない",
        )
        for name, text in texts.items():
            with self.subTest(name=name):
                normalized = self._normalize_contract(text)
                self.assertTrue(
                    any(
                        self._normalize_contract(contract) in normalized
                        for contract in worktree_contracts
                    )
                )
                for contract in artifact_nonrequirements:
                    self.assertIn(self._normalize_contract(contract), normalized)

    def test_skill_routes_non_local_writing_findings_to_parent_decision(self) -> None:
        """Keep behavior-changing writing findings outside the local patch route."""
        texts = self._skill_texts()
        required = (
            "writing-principles-reviewer の finding が振る舞い変更、仕様判断、または再設計を要する場合",
            "`review-patch-refactorer` へ渡さない",
            "親が理由付き不採用または未完了と判断する",
            "修正範囲を拡張しない",
            "writing-principles-reviewer を再起動しない",
        )
        for name, text in texts.items():
            with self.subTest(name=name):
                normalized = self._normalize_contract(text)
                for contract in required:
                    self.assertIn(self._normalize_contract(contract), normalized)

    def test_skill_selects_specialist_reviewers_by_concrete_risk(self) -> None:
        """Mirror impl-lead risk-based reviewer selection and same-snapshot collection."""
        texts = self._skill_texts()
        required = (
            "専門 reviewer は impl-lead と同じ具体的リスク選択方針に従う。",
            "ユーザーが reviewer を明示した場合",
            "要求・Acceptance Criteria・既知の失敗影響、または返却 diff から reviewer の責務と一致する具体的リスクがある場合",
            "`test-quality-reviewer`",
            "`responsibility-boundary-reviewer`",
            "`security-side-effect-reviewer`",
            "該当する reviewer がなければ 0名でよい。",
            "複数 reviewer は同一 snapshot に対して起動する。同一の diff snapshot と同じ親の一次情報を渡し、全 finding を収集してから親が採否、修正先、または不採用を判断する。",
            "同じ diff snapshot、Acceptance Criteria、変更ファイル、focused test の結果、具体的な review angle を Data として渡す。",
            "親は全 finding を受け取るまで採否、修正、または不採用の処理を開始しない。",
            "mode 名や変更量だけを理由に一律起動しない。",
            "`over-engineering-reviewer` は Acceptance Criteria に不要な追加を行ったという具体的な疑いがある場合だけ",
        )
        for name, text in texts.items():
            with self.subTest(name=name):
                normalized = self._normalize_contract(text)
                for contract in required:
                    self.assertIn(self._normalize_contract(contract), normalized)

    def test_skill_bounds_additional_review_and_final_writing_gate(self) -> None:
        """Permit targeted follow-up only, then run the writing gate exactly once."""
        texts = self._skill_texts()
        required = (
            "修正後も具体的なリスクが残る場合は、影響を受ける reviewer だけを追加確認してよい。",
            "固定 round を要求しない。",
            "全 reviewer を再起動しない。",
            "収束 loop を設けない。",
            "最終 diff に対して `writing-principles-reviewer` を必ず1回起動する。",
            "採用した指摘だけを `review-patch-refactorer` に渡す。review-patch-refactorer は最小の behavior-preserving patch だけを行う。",
            "patch 後に同 reviewer を再起動しない。",
            "patch 後は親 QA と Green 確認で終了する。",
        )
        for name, text in texts.items():
            with self.subTest(name=name):
                normalized = self._normalize_contract(text)
                for contract in required:
                    self.assertIn(self._normalize_contract(contract), normalized)

    def test_skill_leaves_commit_and_publication_to_explicit_request(self) -> None:
        """Keep commit, push, and PR side effects opt-in."""
        texts = self._skill_texts()
        required = (
            "commit・push・PR はユーザーが明示した場合だけ行う。",
            "明示がなければ、親へ変更ファイル、検証 command と結果、",
        )
        for name, text in texts.items():
            with self.subTest(name=name):
                normalized = self._normalize_contract(text)
                for contract in required:
                    self.assertIn(self._normalize_contract(contract), normalized)

    def test_skill_orders_publication_before_cleanup_and_preserves_uncommitted_worktree(
        self,
    ) -> None:
        """Publish or retain changes before safely cleaning the isolated worktree."""
        texts = self._skill_texts()
        required = (
            "明示された commit/push/PR と最終確認を先に実行する。",
            "安全に回収済みの場合だけ cleanup する。",
            "commit 未依頼で変更が worktree に残る場合は cleanup せず、path/status を報告する。",
            "force 削除しない。",
        )
        for name, text in texts.items():
            with self.subTest(name=name):
                closeout = self._normalize_contract(text).split(
                    self._normalize_contract("## Closeout"), 1
                )[1]
                for contract in required:
                    self.assertIn(self._normalize_contract(contract), closeout)
                publish_pos = closeout.index(
                    self._normalize_contract(
                        "明示された commit/push/PR と最終確認を先に実行する。"
                    )
                )
                cleanup_pos = closeout.index(
                    self._normalize_contract("安全に回収済みの場合だけ cleanup する。")
                )
                self.assertLess(publish_pos, cleanup_pos)


if __name__ == "__main__":
    unittest.main()
