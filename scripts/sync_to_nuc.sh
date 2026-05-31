#!/usr/bin/env bash
# Sync math-sdk to the NUC via GitHub (source of truth).
#
# Usage:
#   ./scripts/sync_to_nuc.sh           # push (if needed) + git pull on NUC
#   ./scripts/sync_to_nuc.sh --local   # tar-copy working tree (uncommitted changes)
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=scripts/nuc_common.sh
source "$SCRIPT_DIR/nuc_common.sh"

LOCAL_ONLY=false
if [[ "${1:-}" == "--local" ]]; then
  LOCAL_ONLY=true
fi

cd "$REPO_ROOT"

echo "=== Testing SSH to $NUC_HOST ==="
nuc_ssh "hostname"

if [[ "$LOCAL_ONLY" == true ]]; then
  echo "=== Tar sync (includes uncommitted files) ==="
  tar czf - \
    --exclude='./env' \
    --exclude='./.git' \
    --exclude='./games/*/library/temp_multi_threaded_files' \
    --exclude='./games/*/library/tuning_runs' \
    --exclude='./games/*/library/optimization_files' \
    --exclude='./games/*/library/publish_files/*.zst' \
    --exclude='./games/*/library/books/*.jsonl' \
    . | nuc_ssh "cd $(nuc_repo_path) && tar xzf -"
  echo "Local tree copied to NUC."
  exit 0
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "ERROR: Uncommitted changes on Mac. Commit or run: $0 --local" >&2
  exit 1
fi

BRANCH="$(git branch --show-current)"
AHEAD="$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null || echo 0)"
if [[ "$AHEAD" != "0" ]]; then
  echo "=== Pushing $AHEAD commit(s) to origin/$BRANCH ==="
  git push origin "$BRANCH"
fi

echo "=== git pull on NUC ==="
nuc_ssh "cd $(nuc_repo_path) && git fetch origin && git checkout $BRANCH && git pull origin $BRANCH"

echo "=== Sync done (GitHub -> NUC) ==="
