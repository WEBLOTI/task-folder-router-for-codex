#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/publish.sh https://github.com/<owner>/task-folder-router-for-codex.git

Publishes this local template repository to an existing empty GitHub repository.

This script does not create the GitHub repository and does not store credentials.
Create the public empty repository on GitHub first.
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -ne 1 ]]; then
  usage >&2
  exit 64
fi

remote_url="$1"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

case "$remote_url" in
  https://github.com/*/task-folder-router-for-codex.git|git@github.com:*/task-folder-router-for-codex.git)
    ;;
  *)
    echo "Refusing unexpected remote URL: $remote_url" >&2
    echo "Expected a GitHub URL ending in /task-folder-router-for-codex.git" >&2
    exit 65
    ;;
esac

cd "$repo_root"

python3 -m unittest tests/test_router.py
python3 -m py_compile .codex/hooks/task_folder_router.py scripts/install.py tests/test_router.py
python3 -m json.tool .codex/task-folder-router.json >/dev/null
python3 -m json.tool .codex/hooks.json >/dev/null

if [[ -n "$(git status --short)" ]]; then
  echo "Working tree is not clean. Commit or discard changes before publishing." >&2
  git status --short >&2
  exit 66
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$remote_url"
else
  git remote add origin "$remote_url"
fi

git push -u origin main
