#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
tmp_dir="$(mktemp -d /tmp/whats-this-contract-test.XXXXXX)"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

trap 'rm -rf -- "$tmp_dir"' EXIT

copy_project() {
  local destination="$1"
  mkdir -p "$destination"
  cp -a \
    "$repo_root/contracts" \
    "$repo_root/declarations" \
    "$repo_root/shared" \
    "$repo_root/plugins" \
    "$repo_root/gunte.toml" \
    "$repo_root/gunte.lock.json" \
    "$destination/"
}

baseline="$tmp_dir/baseline"
copy_project "$baseline"

baseline_output="$(cd -- "$baseline" && gunte emit 2>&1)" || {
  fail "baseline gunte emit failed: $baseline_output"
}

mutate_explicit_invocation() {
  perl -0pi -e 's/明示的に起動されたときだけ/暗黙に起動されたときだけ/' "$1/shared/skill/whats-this/SKILL.md"
}

mutate_ownership() {
  perl -0pi -e 's/exactly one の task-local/one の task-local/' "$1/shared/skill/whats-this/SKILL.md"
}

mutate_interactive_connection() {
  perl -0pi -e 's/construction Method として利用します。/construction Method として記録します。/' "$1/shared/skill/whats-this/SKILL.md"
}

mutate_reintegration() {
  perl -0pi -e 's/同じ task-local Local Model/別の task-local Local Model/' "$1/shared/skill/whats-this/SKILL.md"
}

mutate_completion_output() {
  perl -0pi -e 's/requested output へ直接接続し、/固定 report へ接続し、/' "$1/shared/skill/whats-this/SKILL.md"
}

mutate_document() {
  perl -0pi -e 's/^# whats-this$/# what-is-this/m' "$1/shared/skill/whats-this/SKILL.md"
}

mutate_claude_invocation_policy() {
  perl -0pi -e 's/(<!-- \@only claude -->.*?disable-model-invocation: )true/${1}false/s' "$1/shared/skill/whats-this/SKILL.md"
}

mutate_cursor_invocation_policy() {
  perl -0pi -e 's/(<!-- \@only cursor -->.*?disable-model-invocation: )true/${1}false/s' "$1/shared/skill/whats-this/SKILL.md"
}

mutate_codex_invocation_policy() {
  perl -0pi -e 's/allow_implicit_invocation: false/allow_implicit_invocation: true/' "$1/declarations/codex/skills/whats-this/openai.yaml"
}

run_contract_failure() {
  local case_name="$1"
  local target="$2"
  local contract_id="$3"
  local failure_kind="$4"
  local source_path="$5"
  local artifact_path="$6"
  local mutation="$7"
  local case_dir="$tmp_dir/$case_name"
  local before_hash
  local output
  local status

  cp -a "$baseline/." "$case_dir/"
  [[ -f "$case_dir/$artifact_path" ]] || fail "$case_name missing projection path $artifact_path"
  before_hash="$(sha256sum "$case_dir/$artifact_path")"
  "$mutation" "$case_dir"

  set +e
  output="$(cd -- "$case_dir" && gunte emit --target "$target" 2>&1)"
  status=$?
  set -e

  [[ $status -ne 0 ]] || fail "$case_name accepted a semantic mutation for $target ($artifact_path)"
  [[ "$output" == *"$contract_id"* ]] || fail "$case_name omitted contract identity $contract_id: $output"
  [[ "$output" == *"$target"* ]] || fail "$case_name omitted target $target: $output"
  [[ "$output" == *"$failure_kind"* ]] || fail "$case_name omitted failure kind $failure_kind: $output"
  [[ "$output" == *"$source_path"* ]] || fail "$case_name omitted source path $source_path: $output"
  [[ "$(sha256sum "$case_dir/$artifact_path")" == "$before_hash" ]] || \
    fail "$case_name rewrote projection path $artifact_path after validation failure"
}

for target in claude codex cursor; do
  run_contract_failure \
    "explicit-$target" "$target" whats-this-explicit-invocation-6aff5f790dc7 requires_violation \
    shared/skill/whats-this/SKILL.md "plugins/$target/skills/whats-this/SKILL.md" mutate_explicit_invocation
  run_contract_failure \
    "ownership-$target" "$target" whats-this-ownership-2aa0a2707b35 requires_violation \
    shared/skill/whats-this/SKILL.md "plugins/$target/skills/whats-this/SKILL.md" mutate_ownership
  run_contract_failure \
    "interactive-$target" "$target" whats-this-interactive-connection-159f2da9a4d4 requires_violation \
    shared/skill/whats-this/SKILL.md "plugins/$target/skills/whats-this/SKILL.md" mutate_interactive_connection
  run_contract_failure \
    "reintegration-$target" "$target" whats-this-reintegration-741726b3c149 requires_violation \
    shared/skill/whats-this/SKILL.md "plugins/$target/skills/whats-this/SKILL.md" mutate_reintegration
  run_contract_failure \
    "completion-$target" "$target" whats-this-completion-output-b68b52f208e7 requires_violation \
    shared/skill/whats-this/SKILL.md "plugins/$target/skills/whats-this/SKILL.md" mutate_completion_output
  run_contract_failure \
    "document-$target" "$target" whats-this-document occurrences_violation \
    shared/skill/whats-this/SKILL.md "plugins/$target/skills/whats-this/SKILL.md" mutate_document
done

run_contract_failure \
  claude-policy claude whats-this-claude-invocation-policy occurrences_violation \
  shared/skill/whats-this/SKILL.md plugins/claude/skills/whats-this/SKILL.md mutate_claude_invocation_policy
run_contract_failure \
  cursor-policy cursor whats-this-cursor-invocation-policy occurrences_violation \
  shared/skill/whats-this/SKILL.md plugins/cursor/skills/whats-this/SKILL.md mutate_cursor_invocation_policy
run_contract_failure \
  codex-policy codex whats-this-codex-invocation-policy occurrences_violation \
  declarations/codex/skills/whats-this/openai.yaml plugins/codex/skills/whats-this/agents/openai.yaml mutate_codex_invocation_policy

echo "PASS: whats-this contract mutation test"
