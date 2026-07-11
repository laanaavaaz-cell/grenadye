#!/usr/bin/env bash
# Usage: ./scripts/git_push.sh "commit message" [branch]
# If branch is omitted, pushes to current branch.
set -e

MSG="${1:-"chore: auto-push changes"}"
BRANCH="${2:-$(git rev-parse --abbrev-ref HEAD)}"

cd "$(dirname "$0")/.."

git add -A

# Nothing staged? exit cleanly.
if git diff --cached --quiet; then
  echo "Nothing to commit on $BRANCH."
  exit 0
fi

git commit -m "$MSG"
git push origin "$BRANCH"
echo "✅ Pushed to $BRANCH: $MSG"
