#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
installer="$repo_root/plugins/cursor/install/install-plugin.sh"
expected_version="$(cat "$repo_root/shared/VERSION")"
plugin_version="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$repo_root/plugins/cursor/.cursor-plugin/plugin.json")"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

assert_same() {
  cmp -s "$1" "$2" || fail "$1 and $2 differ"
}

[[ "$plugin_version" == "$expected_version" ]] || fail "plugin and shared versions differ: $plugin_version vs $expected_version"
[[ -f "$installer" ]] || fail "missing installer: $installer"
[[ -f "$repo_root/plugins/cursor/install/install-plugin.ps1" ]] || fail "missing PowerShell installer"
[[ -f "$repo_root/plugins/cursor/references/deletion-test-method.md" ]] || fail "missing Deletion Test Method reference"
[[ -f "$repo_root/plugins/cursor/references/planning-core.md" ]] || fail "missing Planning Core reference"
[[ -f "$repo_root/plugins/cursor/skills/review-refine/SKILL.md" ]] || fail "missing review-refine skill"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

# Build a local Git source that mirrors plugins/cursor for offline installer tests.
source_repo="$tmp_dir/source-repo"
mkdir -p "$source_repo"
git -C "$source_repo" init -q -b main
git -C "$source_repo" config user.email "tugite-test@example.com"
git -C "$source_repo" config user.name "tugite-test"
mkdir -p "$source_repo/plugins"
cp -R "$repo_root/plugins/cursor" "$source_repo/plugins/cursor"
git -C "$source_repo" add .
git -C "$source_repo" commit -q -m "test cursor plugin source"
source_commit="$(git -C "$source_repo" rev-parse HEAD)"

fake_home="$tmp_dir/home"
mkdir -p "$fake_home"
dest_dir="$fake_home/.cursor/plugins/local/tugite"

install_with_home() {
  HOME="$fake_home" "$installer" --user --repo-url "file://$source_repo" --ref main "$@"
}

install_output="$(install_with_home)"
[[ -f "$dest_dir/.cursor-plugin/plugin.json" ]] || fail "plugin manifest was not installed"
[[ "$(cat "$dest_dir/.tugite-version")" == "$expected_version" ]] || fail "version marker mismatch"
[[ "$(cat "$dest_dir/.tugite-commit")" == "$source_commit" ]] || fail "commit marker mismatch"
[[ "$(cat "$dest_dir/.tugite-ref")" == "main" ]] || fail "ref marker mismatch"
assert_same "$source_repo/plugins/cursor/.cursor-plugin/plugin.json" "$dest_dir/.cursor-plugin/plugin.json"

for skill in explorer-this how-it plan-agent plan-interactive review-refine; do
  assert_same "$source_repo/plugins/cursor/skills/$skill/SKILL.md" "$dest_dir/skills/$skill/SKILL.md"
done

for reference in model-construction agentic-model-construction interactive-model-construction behavior-model-observation planning-synthesis planning-core reality-model-observation deletion-test-method researcher-delegation; do
  assert_same "$source_repo/plugins/cursor/references/$reference.md" "$dest_dir/references/$reference.md"
done

for agent in over-engineering-reviewer plan-adversarial-reviewer plan-quality-advisor researcher; do
  assert_same "$source_repo/plugins/cursor/agents/$agent.md" "$dest_dir/agents/$agent.md"
done

[[ ! -e "$dest_dir/skills/clarify-it" ]] || fail "public clarify-it skill was installed"
[[ "$install_output" == *"$dest_dir"* ]] || fail "install output did not mention destination"

same_output="$(install_with_home --check)"
[[ "$same_output" == *"up to date"* ]] || fail "check did not report up-to-date installation"

# Second install without --force must refuse overwrite after a marker drift.
printf '%s\n' "0.0.0-test" > "$dest_dir/.tugite-version"
set +e
check_output="$(install_with_home --check 2>&1)"
check_status=$?
refusal_output="$(install_with_home 2>&1)"
refusal_status=$?
set -e
[[ $check_status -eq 3 ]] || fail "check did not detect outdated installation (status=$check_status)"
[[ $refusal_status -eq 3 ]] || fail "outdated install without --force should exit 3 (status=$refusal_status)"
[[ "$refusal_output" == *"--force"* ]] || fail "refusal did not require explicit overwrite"
[[ "$(cat "$dest_dir/.tugite-version")" == "0.0.0-test" ]] || fail "refused install mutated version marker"

force_output="$(install_with_home --force)"
[[ "$(cat "$dest_dir/.tugite-version")" == "$expected_version" ]] || fail "forced install did not restore version"
[[ "$(cat "$dest_dir/.tugite-commit")" == "$source_commit" ]] || fail "forced install did not restore commit"
[[ "$force_output" == *"Installed Tugite Cursor plugin"* ]] || fail "forced install output missing success text"

# Symlinked destination must be refused.
rm -rf "$dest_dir"
mkdir -p "$fake_home/.cursor/plugins/local"
outside="$tmp_dir/outside-plugin"
mkdir -p "$outside"
printf '%s\n' "sentinel" > "$outside/sentinel.txt"
ln -s "$outside" "$dest_dir"
set +e
symlink_output="$(install_with_home --force 2>&1)"
symlink_status=$?
set -e
[[ $symlink_status -ne 0 ]] || fail "installer accepted a symlinked destination"
[[ "$symlink_output" == *"Refusing symlinked"* ]] || fail "symlink refusal message missing"
[[ "$(cat "$outside/sentinel.txt")" == "sentinel" ]] || fail "symlinked destination target was overwritten"
[[ -L "$dest_dir" ]] || fail "symlinked destination was replaced unexpectedly"

echo "PASS: install-cursor-plugin-test"
