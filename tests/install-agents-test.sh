#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
installer="$repo_root/plugins/codex/install/install-agents.sh"
expected_version="$(cat "$repo_root/plugins/codex/install/VERSION")"
plugin_version="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$repo_root/plugins/codex/.codex-plugin/plugin.json")"
required_agents=(
  researcher
)

# Fail the test with a concise diagnostic.
fail() {
  echo "FAIL: $*" >&2
  exit 1
}

# Assert that two files have identical content.
assert_same() {
  cmp -s "$1" "$2" || fail "$1 and $2 differ"
}

create_fixture() {
  local repository_root="$1"
  local fixture_parent="$repository_root/.local"
  local repository_identity
  local fixture_parent_identity

  [[ ! -L "$fixture_parent" ]] || return 1
  mkdir -p "$fixture_parent"
  [[ -d "$fixture_parent" && ! -L "$fixture_parent" ]] || return 1
  repository_identity="$(cd -- "$repository_root" && pwd -P)" || return 1
  fixture_parent_identity="$(cd -- "$fixture_parent" && pwd -P)" || return 1
  [[ "$fixture_parent_identity" == "$repository_identity/.local" ]] || return 1
  mktemp -d "$fixture_parent/install-agents-test.XXXXXX"
}

researcher_source="$repo_root/plugins/codex/install/agents/researcher.toml"
[[ -f "$researcher_source" && ! -L "$researcher_source" ]] || \
  fail "required Research Agent definition is missing"

fixture_parent="$repo_root/.local"
tmp_dir="$(create_fixture "$repo_root")"
fixture_parent_identity="$(cd -- "$fixture_parent" && pwd -P)"
tmp_dir_identity="$(cd -- "$tmp_dir" && pwd -P)"

cleanup() {
  [[ -e "$tmp_dir" || -L "$tmp_dir" ]] || return 0
  case "$(basename -- "$tmp_dir")" in
    install-agents-test.*) ;;
    *)
      echo "FAIL: refusing to clean up an unowned fixture name: $tmp_dir" >&2
      return 1
      ;;
  esac

  [[ -d "$tmp_dir" && ! -L "$tmp_dir" ]] || {
    echo "FAIL: refusing to clean up an unowned fixture type: $tmp_dir" >&2
    return 1
  }

  local current_tmp_dir_identity
  local current_fixture_parent_identity
  current_tmp_dir_identity="$(cd -- "$tmp_dir" && pwd -P)" || return 1
  current_fixture_parent_identity="$(cd -- "$(dirname -- "$tmp_dir")" && pwd -P)" || return 1
  [[ "$current_tmp_dir_identity" == "$tmp_dir_identity" &&
    "$current_fixture_parent_identity" == "$fixture_parent_identity" ]] || {
    echo "FAIL: refusing to clean up a fixture with changed identity: $tmp_dir" >&2
    return 1
  }

  rm -rf -- "$tmp_dir"
}

trap cleanup EXIT
target_repo="$tmp_dir/repo"
mkdir -p "$target_repo/.codex/agents"
printf '%s\n' 'name = "unrelated"' > "$target_repo/.codex/agents/unrelated.toml"

test_fixture_parent_rejects_symlink() {
  local case_dir="$tmp_dir/fixture-parent-symlink"
  local repository="$case_dir/repo"
  local outside="$case_dir/outside"
  mkdir -p "$repository" "$outside"
  printf '%s\n' 'outside sentinel' > "$outside/sentinel"
  ln -s "$outside" "$repository/.local"

  set +e
  create_fixture "$repository" >/dev/null 2>&1
  local status=$?
  set -e

  [[ $status -ne 0 ]] || fail "fixture creation accepted a symlinked .local directory"
  [[ "$(cat "$outside/sentinel")" == "outside sentinel" ]] || fail "fixture creation changed the outside sentinel"
  [[ -z "$(find "$outside" -mindepth 1 -maxdepth 1 -name 'install-agents-test.*' -print -quit)" ]] || \
    fail "fixture creation wrote outside the repository"
}

test_fixture_parent_rejects_symlink

[[ "$plugin_version" == "$expected_version" ]] || fail "plugin and custom-agent versions differ"

install_output="$("$installer" --repo "$target_repo")"
agent_dir="$target_repo/.codex/agents"
[[ -f "$agent_dir/unrelated.toml" ]] || fail "unrelated agent was removed"
[[ "$(cat "$agent_dir/.tugite-version")" == "$expected_version" ]] || fail "version was not recorded"
for agent in "${required_agents[@]}"; do
  assert_same "$repo_root/plugins/codex/install/agents/$agent.toml" "$agent_dir/$agent.toml"
  [[ "$install_output" == *"  $agent"* ]] || fail "install output did not list $agent"
done

same_output="$("$installer" --check --repo "$target_repo")"
[[ "$same_output" == *"up to date"* ]] || fail "check did not report up-to-date installation"

test_install_preserves_retired_agent_when_update_is_refused() {
  local retired_agents=(
    expert-selection-reviewer
    review-patch-refactorer
    writing-principles-refactorer
  )
  local retired_agent
  for retired_agent in "${retired_agents[@]}"; do
    printf '%s\n' 'retired local agent' > "$agent_dir/$retired_agent.toml"
  done

  set +e
  local check_output
  check_output="$("$installer" --check --repo "$target_repo" 2>&1)"
  local check_status=$?
  local refusal_output
  refusal_output="$("$installer" --repo "$target_repo" 2>&1)"
  local refusal_status=$?
  set -e

  [[ $check_status -eq 3 ]] || fail "check did not detect the retired agent"
  [[ $refusal_status -eq 3 ]] || fail "retired-agent migration without --force should exit 3"
  [[ "$refusal_output" == *"--force"* ]] || fail "retired-agent refusal did not require explicit overwrite"
  for retired_agent in "${retired_agents[@]}"; do
    [[ "$check_output" == *"$retired_agent"* ]] || fail "check did not identify $retired_agent"
    [[ -f "$agent_dir/$retired_agent.toml" ]] || fail "refused migration removed $retired_agent"
  done
}

test_force_update_removes_all_retired_agents() {
  "$installer" --force --repo "$target_repo"

  [[ ! -e "$agent_dir/expert-selection-reviewer.toml" ]] || fail "forced update retained expert-selection-reviewer"
  [[ ! -e "$agent_dir/review-patch-refactorer.toml" ]] || fail "forced update retained review-patch-refactorer"
  [[ ! -e "$agent_dir/writing-principles-refactorer.toml" ]] || fail "forced update retained writing-principles-refactorer"
  assert_same "$researcher_source" "$agent_dir/researcher.toml"
  [[ -f "$agent_dir/unrelated.toml" ]] || fail "forced migration removed an unrelated agent"
}

test_dangling_retired_agent_requires_approved_migration() {
  local retired_agent="$agent_dir/writing-principles-refactorer.toml"
  ln -s "$tmp_dir/missing-writing-principles-refactorer.toml" "$retired_agent"

  set +e
  local check_output
  check_output="$("$installer" --check --repo "$target_repo" 2>&1)"
  local check_status=$?
  local refusal_output
  refusal_output="$("$installer" --repo "$target_repo" 2>&1)"
  local refusal_status=$?
  set -e

  [[ $check_status -eq 3 ]] || fail "check did not detect the dangling retired-agent symlink"
  [[ "$check_output" == *"writing-principles-refactorer"* ]] || fail "check did not identify the dangling retired-agent symlink"
  [[ $refusal_status -eq 3 ]] || fail "dangling retired-agent migration without --force should exit 3"
  [[ "$refusal_output" == *"--force"* ]] || fail "dangling retired-agent refusal did not require explicit overwrite"
  [[ -L "$retired_agent" ]] || fail "refused migration removed the dangling retired-agent symlink"

  "$installer" --force --repo "$target_repo"

  [[ ! -e "$retired_agent" ]] || fail "forced migration retained the retired-agent target"
  [[ ! -L "$retired_agent" ]] || fail "forced migration retained the dangling retired-agent symlink"
}

test_install_rejects_symlinked_codex_directory() {
  local case_dir="$tmp_dir/symlink-scope"
  local outside="$case_dir/outside"
  mkdir -p "$case_dir/repo" "$outside"
  printf '%s\n' 'outside sentinel' > "$outside/sentinel"
  ln -s "$outside" "$case_dir/repo/.codex"

  set +e
  "$installer" --force --repo "$case_dir/repo" >/dev/null 2>&1
  local status=$?
  set -e

  [[ $status -ne 0 ]] || fail "installer accepted a symlinked .codex directory"
  [[ "$(cat "$outside/sentinel")" == "outside sentinel" ]] || fail "scope escape changed outside sentinel"
  [[ ! -e "$outside/researcher.toml" ]] || fail "scope escape installed outside the repository"
}

test_install_rejects_agent_and_version_destination_symlinks() {
  local case_dir="$tmp_dir/symlink-files"
  local outside="$case_dir/outside"
  local repo="$case_dir/repo"
  mkdir -p "$repo/.codex/agents" "$outside"
  printf '%s\n' 'agent sentinel' > "$outside/agent-sentinel"
  ln -s "$outside/agent-sentinel" "$repo/.codex/agents/researcher.toml"

  set +e
  "$installer" --force --repo "$repo" >/dev/null 2>&1
  local agent_status=$?
  set -e

  [[ $agent_status -ne 0 ]] || fail "installer accepted a required-agent destination symlink"
  [[ "$(cat "$outside/agent-sentinel")" == "agent sentinel" ]] || fail "required-agent symlink target was overwritten"

  rm -f "$repo/.codex/agents/researcher.toml"
  printf '%s\n' 'version sentinel' > "$outside/version-sentinel"
  ln -s "$outside/version-sentinel" "$repo/.codex/agents/.tugite-version"

  set +e
  "$installer" --force --repo "$repo" >/dev/null 2>&1
  local version_status=$?
  set -e

  [[ $version_status -ne 0 ]] || fail "installer accepted a version marker symlink"
  [[ "$(cat "$outside/version-sentinel")" == "version sentinel" ]] || fail "version symlink target was overwritten"
}

test_install_preserves_retired_agent_when_update_is_refused
test_force_update_removes_all_retired_agents
test_dangling_retired_agent_requires_approved_migration
test_install_rejects_symlinked_codex_directory
test_install_rejects_agent_and_version_destination_symlinks

printf '%s\n' 'local customization' > "$agent_dir/researcher.toml"
printf '%s\n' '0.9.0' > "$agent_dir/.tugite-version"
before_hash="$(sha256sum "$agent_dir/researcher.toml")"

set +e
refusal_output="$("$installer" --repo "$target_repo" 2>&1)"
refusal_status=$?
set -e
[[ $refusal_status -eq 3 ]] || fail "update without --force should exit 3"
[[ "$refusal_output" == *"--force"* ]] || fail "refusal did not explain explicit overwrite"
[[ "$(sha256sum "$agent_dir/researcher.toml")" == "$before_hash" ]] || fail "refused update changed an agent"

"$installer" --force --repo "$target_repo"
[[ "$(cat "$agent_dir/.tugite-version")" == "$expected_version" ]] || fail "forced update did not record version"
assert_same "$researcher_source" "$agent_dir/researcher.toml"

echo "PASS: install-agents"
