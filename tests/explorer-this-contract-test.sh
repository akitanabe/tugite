#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
tmp_dir="$(mktemp -d /tmp/explorer-this-contract-test.XXXXXX)"

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

file_hash() {
  sha256sum "$1" | awk '{print $1}'
}

baseline="$tmp_dir/baseline"
copy_project "$baseline"

baseline_output="$(cd -- "$baseline" && gunte emit 2>&1)" || {
  fail "baseline gunte emit failed: $baseline_output"
}

baseline_lock_output="$(cd -- "$baseline" && gunte lock 2>&1)" || {
  fail "baseline gunte lock failed: $baseline_lock_output"
}

mutate_agentic_first() {
  perl -0pi -e 's/Agentic Model Construction を first route として利用し/Agentic Model Construction を later route として利用し/' \
    "$1/shared/skill/explorer-this/SKILL.md"
}

mutate_fallback_boundary() {
  perl -0pi -e 's/場合だけ、Interactive Model Construction/場合は常に、Interactive Model Construction/' \
    "$1/shared/skill/explorer-this/SKILL.md"
}

mutate_nonhuman_stop() {
  perl -0pi -e 's/Interactive fallback にせず、qualified stop/Interactive fallback とし、qualified stop/' \
    "$1/shared/skill/explorer-this/SKILL.md"
}

mutate_continuity() {
  perl -0pi -e 's/同じ task-local Local Model、取得済み evidence/別の task-local Local Model、取得済み evidence/' \
    "$1/shared/skill/explorer-this/SKILL.md"
}

mutate_authority() {
  perl -0pi -e 's/calling workflow が所有し、`whats-this`/Interactive Method が所有し、`whats-this`/' \
    "$1/shared/skill/explorer-this/SKILL.md"
}

mutate_output() {
  perl -0pi -e 's/元の requested output へ接続し/固定 report へ接続し/' \
    "$1/shared/skill/explorer-this/SKILL.md"
}

mutate_document() {
  perl -0pi -e 's/^# explorer-this$/# explore-this/m' "$1/shared/skill/explorer-this/SKILL.md"
}

mutate_claude_invocation_policy() {
  perl -0pi -e 's/(<!-- \@only claude -->.*?disable-model-invocation: )true/${1}false/s' \
    "$1/shared/skill/explorer-this/SKILL.md"
}

mutate_cursor_invocation_policy() {
  perl -0pi -e 's/(<!-- \@only cursor -->.*?disable-model-invocation: )true/${1}false/s' \
    "$1/shared/skill/explorer-this/SKILL.md"
}

mutate_codex_invocation_policy() {
  perl -0pi -e 's/allow_implicit_invocation: false/allow_implicit_invocation: true/' \
    "$1/declarations/codex/skills/explorer-this/openai.yaml"
}

swap_contract_blocks() {
  local case_dir="$1"
  local first="$2"
  local second="$3"
  local source_file="$case_dir/shared/skill/explorer-this/SKILL.md"

  EXPLORER_SWAP_FIRST="$first" EXPLORER_SWAP_SECOND="$second" perl -0pi -e '
    my $first = $ENV{EXPLORER_SWAP_FIRST};
    my $second = $ENV{EXPLORER_SWAP_SECOND};
    my ($first_block) = /(<!-- \@contract \Q$first\E -->.*?<!-- \@\/contract -->)/s;
    my ($second_block) = /(<!-- \@contract \Q$second\E -->.*?<!-- \@\/contract -->)/s;
    die "missing contract block for swap\n" unless defined $first_block && defined $second_block;
    my $placeholder = "__EXPLORER_THIS_CONTRACT_SWAP__";
    s/\Q$first_block\E/$placeholder/ or die "first contract block was not replaced\n";
    s/\Q$second_block\E/$first_block/ or die "second contract block was not replaced\n";
    s/\Q$placeholder\E/$second_block/ or die "first contract placeholder was not replaced\n";
  ' "$source_file"
}

swap_anchor_and_contract() {
  local case_dir="$1"
  local anchor="$2"
  local contract="$3"
  local source_file="$case_dir/shared/skill/explorer-this/SKILL.md"

  EXPLORER_SWAP_ANCHOR="$anchor" EXPLORER_SWAP_CONTRACT="$contract" perl -0pi -e '
    my $anchor = $ENV{EXPLORER_SWAP_ANCHOR};
    my $contract = $ENV{EXPLORER_SWAP_CONTRACT};
    my ($anchor_marker) = /(<!-- \@anchor \Q$anchor\E -->)/s;
    my ($contract_block) = /(<!-- \@contract \Q$contract\E -->.*?<!-- \@\/contract -->)/s;
    die "missing anchor or contract block for swap\n" unless defined $anchor_marker && defined $contract_block;
    my $placeholder = "__EXPLORER_THIS_ANCHOR_SWAP__";
    s/\Q$anchor_marker\E/$placeholder/ or die "anchor marker was not replaced\n";
    s/\Q$contract_block\E/$anchor_marker/ or die "contract block was not replaced\n";
    s/\Q$placeholder\E/$contract_block/ or die "anchor placeholder was not replaced\n";
  ' "$source_file"
}

mutate_document_before_agentic() {
  swap_anchor_and_contract "$1" explorer-this-document-relation explorer-this-agentic-first
}

mutate_agentic_before_fallback() {
  swap_contract_blocks "$1" explorer-this-fallback-boundary explorer-this-agentic-first
}

mutate_fallback_before_nonhuman() {
  swap_contract_blocks "$1" explorer-this-nonhuman-stop explorer-this-fallback-boundary
}

mutate_nonhuman_before_continuity() {
  swap_contract_blocks "$1" explorer-this-continuity explorer-this-nonhuman-stop
}

mutate_continuity_before_authority() {
  swap_contract_blocks "$1" explorer-this-authority explorer-this-continuity
}

mutate_authority_before_output() {
  swap_contract_blocks "$1" explorer-this-output explorer-this-authority
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
  local restored_output
  local restored_check

  cp -a "$baseline/." "$case_dir/"
  [[ -f "$case_dir/$artifact_path" ]] || fail "$case_name missing projection path $artifact_path"
  before_hash="$(file_hash "$case_dir/$artifact_path")"
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
  [[ "$(file_hash "$case_dir/$artifact_path")" == "$before_hash" ]] || \
    fail "$case_name rewrote projection path $artifact_path after validation failure"

  cp -a "$baseline/." "$case_dir/"
  restored_output="$(cd -- "$case_dir" && gunte emit --target "$target" 2>&1)" || {
    fail "$case_name restore emit failed: $restored_output"
  }
  restored_check="$(cd -- "$case_dir" && gunte check --target "$target" 2>&1)" || {
    fail "$case_name restore check failed: $restored_check"
  }
  [[ "$(file_hash "$case_dir/$source_path")" == "$(file_hash "$baseline/$source_path")" ]] || \
    fail "$case_name did not restore source $source_path"
  [[ "$(file_hash "$case_dir/$artifact_path")" == "$before_hash" ]] || \
    fail "$case_name restore changed projection path $artifact_path"
}

for target in claude codex cursor; do
  run_contract_failure \
    "rejects-agentic-not-first-$target" "$target" explorer-this-agentic-first-f7726fdb98b3 requires_violation \
    shared/skill/explorer-this/SKILL.md "plugins/$target/skills/explorer-this/SKILL.md" mutate_agentic_first
  run_contract_failure \
    "rejects-unqualified-fallback-$target" "$target" explorer-this-fallback-boundary-2f0e78869ab4 requires_violation \
    shared/skill/explorer-this/SKILL.md "plugins/$target/skills/explorer-this/SKILL.md" mutate_fallback_boundary
  run_contract_failure \
    "rejects-nonhuman-fallback-$target" "$target" explorer-this-nonhuman-stop-b7450dd0304d requires_violation \
    shared/skill/explorer-this/SKILL.md "plugins/$target/skills/explorer-this/SKILL.md" mutate_nonhuman_stop
  run_contract_failure \
    "rejects-broken-model-continuity-$target" "$target" explorer-this-continuity-f34cebd89ba8 requires_violation \
    shared/skill/explorer-this/SKILL.md "plugins/$target/skills/explorer-this/SKILL.md" mutate_continuity
  run_contract_failure \
    "rejects-authority-leak-$target" "$target" explorer-this-authority-383e26f59917 requires_violation \
    shared/skill/explorer-this/SKILL.md "plugins/$target/skills/explorer-this/SKILL.md" mutate_authority
  run_contract_failure \
    "rejects-output-boundary-change-$target" "$target" explorer-this-output-337180f80846 requires_violation \
    shared/skill/explorer-this/SKILL.md "plugins/$target/skills/explorer-this/SKILL.md" mutate_output
  run_contract_failure \
    "rejects-missing-explorer-this-title-$target" "$target" explorer-this-document occurrences_violation \
    shared/skill/explorer-this/SKILL.md "plugins/$target/skills/explorer-this/SKILL.md" mutate_document
  run_contract_failure \
    "rejects-document-after-agentic-$target" "$target" explorer-this-document-before-agentic order_violation \
    shared/skill/explorer-this/SKILL.md "plugins/$target/skills/explorer-this/SKILL.md" mutate_document_before_agentic
  run_contract_failure \
    "rejects-agentic-after-fallback-$target" "$target" explorer-this-agentic-before-fallback order_violation \
    shared/skill/explorer-this/SKILL.md "plugins/$target/skills/explorer-this/SKILL.md" mutate_agentic_before_fallback
  run_contract_failure \
    "rejects-fallback-after-nonhuman-$target" "$target" explorer-this-fallback-before-nonhuman order_violation \
    shared/skill/explorer-this/SKILL.md "plugins/$target/skills/explorer-this/SKILL.md" mutate_fallback_before_nonhuman
  run_contract_failure \
    "rejects-nonhuman-after-continuity-$target" "$target" explorer-this-nonhuman-before-continuity order_violation \
    shared/skill/explorer-this/SKILL.md "plugins/$target/skills/explorer-this/SKILL.md" mutate_nonhuman_before_continuity
  run_contract_failure \
    "rejects-continuity-after-authority-$target" "$target" explorer-this-continuity-before-authority order_violation \
    shared/skill/explorer-this/SKILL.md "plugins/$target/skills/explorer-this/SKILL.md" mutate_continuity_before_authority
  run_contract_failure \
    "rejects-authority-after-output-$target" "$target" explorer-this-authority-before-output order_violation \
    shared/skill/explorer-this/SKILL.md "plugins/$target/skills/explorer-this/SKILL.md" mutate_authority_before_output
done

run_contract_failure \
  rejects-implicit-explorer-claude-skill-invocation claude explorer-this-claude-invocation-policy occurrences_violation \
  shared/skill/explorer-this/SKILL.md plugins/claude/skills/explorer-this/SKILL.md mutate_claude_invocation_policy
run_contract_failure \
  rejects-implicit-explorer-cursor-skill-invocation cursor explorer-this-cursor-invocation-policy occurrences_violation \
  shared/skill/explorer-this/SKILL.md plugins/cursor/skills/explorer-this/SKILL.md mutate_cursor_invocation_policy
run_contract_failure \
  rejects-implicit-explorer-codex-declaration codex explorer-this-codex-invocation-policy occurrences_violation \
  declarations/codex/skills/explorer-this/openai.yaml plugins/codex/skills/explorer-this/agents/openai.yaml mutate_codex_invocation_policy

echo "PASS: explorer-this contract mutation test"
