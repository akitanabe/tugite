#!/usr/bin/env python3
"""Gunte mutations for this repository's plan-verification default."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
POLICY_TEXT = """計画成果物の既定 verification は、この repository で実行できる native 手段に限り、EVAL を含めない。
Gunte が保証しない点は残存 risk / 未検証とし、受け入れを EVAL 実行に依存させない。
EVAL は Human が明示したとき、または既存 EVAL 成果物の変更自体が要求対象のときだけ使う。
"""
GUIDELINES = Path("shared/repository-guidelines.md")
PREDICATE_FAILED = re.compile(r"predicate (\S+) failed")
REQUIRES_ID = "repository-plan-verification-default-1cd0b7e4ffb5"
FORBIDS_LLM_ID = "no-eval-as-default-llm-quality"
FORBIDS_EVALS_DIR_ID = "no-evals-dir-as-inventory"
TARGETS = ("agents-guidance", "claude-guidance")


def failed_predicate_ids(stderr_and_stdout: str) -> set[str]:
    return set(PREDICATE_FAILED.findall(stderr_and_stdout))


def run_gunte_check(project: Path, target: str) -> tuple[int, str]:
    completed = subprocess.run(
        ["gunte", "check", "--target", target],
        cwd=project,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode, completed.stdout + completed.stderr


class PlanVerificationContractMutationTests(unittest.TestCase):
    def _copy_project(self) -> Path:
        destination = Path(tempfile.mkdtemp())
        shutil.copytree(
            REPO_ROOT,
            destination,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"),
        )
        return destination

    def _guidelines(self, project: Path) -> Path:
        return project / GUIDELINES

    def _replace_once(self, project: Path, old: str, new: str) -> None:
        path = self._guidelines(project)
        text = path.read_text(encoding="utf-8")
        if old not in text:
            self.fail(f"{GUIDELINES} does not contain the mutation witness")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def _assert_only_predicate(self, project: Path, target: str, predicate_id: str) -> None:
        status, output = run_gunte_check(project, target)
        self.assertEqual(status, 1, output)
        self.assertEqual(failed_predicate_ids(output), {predicate_id}, output)

    def test_removing_plan_verification_policy_fails_only_the_requires_contract(self) -> None:
        for target in TARGETS:
            with self.subTest(target=target):
                project = self._copy_project()
                try:
                    self._replace_once(project, POLICY_TEXT, "")
                    self._assert_only_predicate(project, target, REQUIRES_ID)
                finally:
                    shutil.rmtree(project)

    def test_restoring_eval_as_llm_quality_default_fails_only_the_forbids_contract(self) -> None:
        old = "serialization、byte drift は `gunte check` に任せます。"
        restored = (
            "serialization、byte drift は `gunte check` に任せ、"
            "LLM の判断品質や読みやすさは EVAL または editorial review で扱います。"
        )
        for target in TARGETS:
            with self.subTest(target=target):
                project = self._copy_project()
                try:
                    self._replace_once(project, old, restored)
                    self._assert_only_predicate(project, target, FORBIDS_LLM_ID)
                finally:
                    shutil.rmtree(project)

    def test_restoring_evals_directory_inventory_fails_only_the_forbids_contract(self) -> None:
        old = "自動テストは `tests/` にあります。"
        restored = "自動テストは `tests/`、手動評価シナリオは `evals/` にあります。"
        for target in TARGETS:
            with self.subTest(target=target):
                project = self._copy_project()
                try:
                    self._replace_once(project, old, restored)
                    self._assert_only_predicate(project, target, FORBIDS_EVALS_DIR_ID)
                finally:
                    shutil.rmtree(project)


if __name__ == "__main__":
    unittest.main()
