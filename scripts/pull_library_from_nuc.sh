#!/usr/bin/env bash
# Pull sim outputs from NUC -> Mac (lookup_tables, publish_files, configs).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/nuc_common.sh"

DEST="$REPO_ROOT/$NUC_GAME_LIB"
mkdir -p "$DEST"

echo "=== Pulling library artifacts from $NUC_HOST ==="
nuc_ssh "cd $(nuc_repo_path)/$NUC_GAME_LIB && tar czf - lookup_tables publish_files configs forces" \
  | tar xzf - -C "$DEST"

echo "=== Done. Local path: $DEST ==="
