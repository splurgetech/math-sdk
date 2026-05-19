#!/usr/bin/env bash
# Copy math-sdk from this Mac to a Windows NUC over SSH (OpenSSH on Windows).
#
# Legacy tar sync — prefer ./scripts/sync_to_nuc.sh (git) or --local.
# Requires Host nuc in ~/.ssh/config (see docs/NUC_WINDOWS_SETUP.md).

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/nuc_common.sh"
DEST="${NUC_HOST}:$(nuc_repo_path)/"

echo "Syncing $REPO_ROOT -> $DEST"
rsync -avz --progress \
  --exclude 'env/' \
  --exclude '__pycache__/' \
  --exclude '.pytest_cache/' \
  --exclude 'games/*/library/temp_multi_threaded_files/' \
  --exclude 'games/*/library/publish_files/*.zst' \
  --exclude 'games/*/library/books/*.jsonl' \
  "$REPO_ROOT/" "$DEST"

echo ""
echo "Prefer: ./scripts/sync_to_nuc.sh --local"
