#!/usr/bin/env bash
set -euo pipefail

# Install Tugite Cursor plugin for the current user from a Git remote (main by default).
# Works on Linux, macOS, WSL, and Git Bash for Windows. Symlink installs are not supported.

DEFAULT_REPO_URL="https://github.com/akitanabe/tugite.git"
DEFAULT_REF="main"
PLUGIN_SUBDIR="plugins/cursor"
INSTALLED_VERSION_FILE=".tugite-version"
INSTALLED_COMMIT_FILE=".tugite-commit"
INSTALLED_SOURCE_FILE=".tugite-source"
INSTALLED_REF_FILE=".tugite-ref"

usage() {
  cat <<'USAGE'
Usage:
  install-plugin.sh [--check | --force] --user [--repo-url <url>] [--ref <ref>]

Clone the Tugite repository and copy plugins/cursor into the Cursor user local plugin directory.

Options:
  --check              Report installation status without changing files
  --force              Explicitly overwrite an existing or outdated installation
  --user               Install to $HOME/.cursor/plugins/local/tugite
  --repo-url <url>     Git remote or local repository path (default: https://github.com/akitanabe/tugite.git)
  --ref <ref>          Branch or tag to install (default: main)
  -h, --help           Show this help

Notes:
  - Symlink destinations are refused.
  - On native Windows PowerShell, use install-plugin.ps1 instead.
USAGE
}

resolve_home() {
  if [[ -n "${HOME:-}" ]]; then
    printf '%s\n' "$HOME"
    return 0
  fi
  if [[ -n "${USERPROFILE:-}" ]]; then
    if command -v cygpath >/dev/null 2>&1; then
      cygpath -u "$USERPROFILE"
      return 0
    fi
    printf '%s\n' "$USERPROFILE"
    return 0
  fi
  echo "HOME or USERPROFILE is required" >&2
  exit 1
}

reject_symlink() {
  local path="$1"
  local label="$2"
  if [[ -L "$path" ]]; then
    echo "Refusing symlinked $label: $path" >&2
    exit 1
  fi
}

require_cmd() {
  local name="$1"
  if ! command -v "$name" >/dev/null 2>&1; then
    echo "Required command not found: $name" >&2
    exit 1
  fi
}

read_manifest_version() {
  local manifest="$1"
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$manifest"
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    python -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$manifest"
    return 0
  fi
  # Fallback for environments without Python: read the first "version" string.
  sed -n 's/^[[:space:]]*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$manifest" | head -n 1
}

copy_tree() {
  local src="$1"
  local dest="$2"
  mkdir -p "$dest"
  if command -v tar >/dev/null 2>&1; then
    (cd -- "$src" && tar cf - .) | (cd -- "$dest" && tar xf -)
    return 0
  fi
  cp -R "$src"/. "$dest"/
}

mode="install"
scope=""
repo_url="$DEFAULT_REPO_URL"
ref="$DEFAULT_REF"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check)
      [[ "$mode" == "install" ]] || { usage >&2; exit 2; }
      mode="check"
      shift
      ;;
    --force)
      [[ "$mode" == "install" ]] || { usage >&2; exit 2; }
      mode="force"
      shift
      ;;
    --user)
      [[ -z "$scope" ]] || { usage >&2; exit 2; }
      scope="user"
      shift
      ;;
    --repo-url)
      [[ $# -ge 2 ]] || { usage >&2; exit 2; }
      repo_url="$2"
      shift 2
      ;;
    --ref)
      [[ $# -ge 2 ]] || { usage >&2; exit 2; }
      ref="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
done

[[ "$scope" == "user" ]] || { usage >&2; exit 2; }

require_cmd git
require_cmd mktemp

home_dir="$(resolve_home)"
cursor_root="$home_dir/.cursor"
plugins_root="$cursor_root/plugins"
local_root="$plugins_root/local"
dest_dir="$local_root/tugite"

reject_symlink "$home_dir" "home directory"
reject_symlink "$cursor_root" ".cursor directory"
reject_symlink "$plugins_root" "plugins directory"
reject_symlink "$local_root" "local plugins directory"
reject_symlink "$dest_dir" "plugin destination"
reject_symlink "$dest_dir/$INSTALLED_VERSION_FILE" "version marker"
reject_symlink "$dest_dir/$INSTALLED_COMMIT_FILE" "commit marker"

work_dir="$(mktemp -d "${TMPDIR:-/tmp}/tugite-cursor-install.XXXXXX")"
cleanup() {
  rm -rf -- "$work_dir"
}
trap cleanup EXIT

clone_dir="$work_dir/src"
git clone --depth 1 --branch "$ref" --single-branch -- "$repo_url" "$clone_dir" >/dev/null

plugin_src="$clone_dir/$PLUGIN_SUBDIR"
manifest="$plugin_src/.cursor-plugin/plugin.json"
if [[ ! -f "$manifest" ]]; then
  echo "Missing Cursor plugin manifest in cloned source: $manifest" >&2
  exit 1
fi

bundled_version="$(read_manifest_version "$manifest")"
if [[ -z "$bundled_version" ]]; then
  echo "Unable to read version from $manifest" >&2
  exit 1
fi
bundled_commit="$(git -C "$clone_dir" rev-parse HEAD)"

installed_version="not installed"
installed_commit="not installed"
if [[ -f "$dest_dir/$INSTALLED_VERSION_FILE" ]]; then
  installed_version="$(<"$dest_dir/$INSTALLED_VERSION_FILE")"
fi
if [[ -f "$dest_dir/$INSTALLED_COMMIT_FILE" ]]; then
  installed_commit="$(<"$dest_dir/$INSTALLED_COMMIT_FILE")"
elif [[ -e "$dest_dir" ]]; then
  installed_commit="unknown"
  if [[ "$installed_version" == "not installed" ]]; then
    installed_version="unknown"
  fi
fi

is_up_to_date=true
if [[ "$installed_commit" != "$bundled_commit" || "$installed_version" != "$bundled_version" ]]; then
  is_up_to_date=false
fi
if [[ ! -f "$dest_dir/.cursor-plugin/plugin.json" ]]; then
  is_up_to_date=false
fi

if [[ "$is_up_to_date" == true ]]; then
  echo "Cursor plugin is up to date (version $bundled_version, commit $bundled_commit): $dest_dir"
  exit 0
fi

cat <<EOF
Cursor plugin update status:
  installed version: $installed_version
  installed commit:  $installed_commit
  bundled version:   $bundled_version
  bundled commit:    $bundled_commit
  source:            $repo_url ($ref)
  target:            $dest_dir
EOF

if [[ "$mode" == "check" ]]; then
  exit 3
fi

if [[ "$installed_version" != "not installed" && "$mode" != "force" ]]; then
  echo "Existing Cursor plugin was not changed. Confirm the overwrite explicitly, then rerun with --force." >&2
  exit 3
fi

staging_dir="$work_dir/staging"
copy_tree "$plugin_src" "$staging_dir"
printf '%s\n' "$bundled_version" > "$staging_dir/$INSTALLED_VERSION_FILE"
printf '%s\n' "$bundled_commit" > "$staging_dir/$INSTALLED_COMMIT_FILE"
printf '%s\n' "$repo_url" > "$staging_dir/$INSTALLED_SOURCE_FILE"
printf '%s\n' "$ref" > "$staging_dir/$INSTALLED_REF_FILE"

mkdir -p "$local_root"
if [[ -e "$dest_dir" ]]; then
  rm -rf -- "$dest_dir"
fi
mv -- "$staging_dir" "$dest_dir"

cat <<EOF
Installed Tugite Cursor plugin version $bundled_version
  commit: $bundled_commit
  path:   $dest_dir

IMPORTANT:
  Restart Cursor, or run Developer: Reload Window, before using the plugin.
  Symlink installs are not supported; rerun this installer to update from Git.
EOF
