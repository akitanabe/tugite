"""Repository contracts for impl-lead delegation modes and TDD evidence."""

from __future__ import annotations

from pathlib import Path
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
            "枝 mode の導出 — `policy`、`baseline`、枝の `risk.level` から枝ごとの mode を導く。",
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
            "`standard` では扱えないリスクが判明した場合は `strict` へ引き上げる。",
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
            "policy / baseline と枝の risk.level から導出する",
            "`adaptive` は新しい実装フローではなく、既存の `lite` / `standard` / `strict` を"
            "枝へ割り当てる配分方針である。",
            "枝へ割り当てられた後は、その枝を既存の各 mode のフローで実行する。",
            "`policy: fixed` は、全枝固定であることを明示的に表現する語彙だけに割り当てる。",
            "それ以外の語彙と mode 未指定はすべて `adaptive` へ写す。",
            "今後語彙を追加する場合の既定も `adaptive` とする。",
            "`policy: adaptive` では、`baseline` と枝の `risk.level` の決定表で"
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
                "全体として厳格な確認を要求するが、明らかに低リスクの枝まで一律 `strict` に"
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
            "mode を引き上げた場合は、その具体的なリスクをユーザーへ報告する。",
            "導出結果より高い mode で枝を実行する場合も、枝単位で具体的なリスクを"
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
            "各枝の `risk.level`、導出した mode、手動上書きの有無。",
            "Mode: standard-adaptive  (policy: adaptive / baseline: standard)",
            "Branch allocation:\n  strict   1\n  standard 3\n  lite     1",
            "1. authorization-check  high    → strict",
            "4. api-response         low     → lite → standard  (override)",
            "5. label-text           low     → lite",
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

        for main in (skills.source_main, skills.claude_main, skills.codex_main):
            with self.subTest(main=main[:40]):
                self.assertLess(
                    main.index("実行前サマリーを提示する"),
                    main.index("先頭の枝だけを委譲する"),
                )

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
            "引き上げ受諾後の段階継続 mechanism は platform に合わせてよい。",
        )
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

        for root in scan_roots:
            file_paths = [root] if root.is_file() else list(root.rglob("*"))
            for file_path in file_paths:
                if not file_path.is_file():
                    continue
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


if __name__ == "__main__":
    unittest.main()
