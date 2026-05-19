#!/usr/bin/env bash
# Copy math-sdk from this Mac to a Windows NUC over SSH (OpenSSH on Windows).
#
# Usage:
#   export NUC_USER=YourWindowsUsername
#   export NUC_IP=192.168.1.50
#   ./scripts/sync_from_mac.sh
#
# Requires: rsync and ssh (built into macOS). On Windows target, OpenSSH Server running.

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NUC_USER="${NUC_USER:?Set NUC_USER (Windows username)}"
NUC_IP="${NUC_IP:?Set NUC_IP (e.g. 192.168.1.50)}"
# Windows OpenSSH often wants forward slashes in path after C:
DEST="${NUC_USER}@${NUC_IP}:/C/Users/${NUC_USER}/math-sdk/"

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
echo "On the NUC (PowerShell):"
echo "  cd \$HOME\\math-sdk"
echo "  .\\scripts\\setup_windows.ps1"
echo "  .\\scripts\\smoke_test_windows.ps1"
