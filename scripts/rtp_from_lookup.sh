#!/usr/bin/env bash
# Wrapper: RTP from Clash Kronos library CSVs (run from math-sdk repo root).
# Usage:
#   ./scripts/rtp_from_lookup.sh
#   ./scripts/rtp_from_lookup.sh path/to/lookUpTable_base.csv path/to/lookUpTable_base_0.csv 1.0
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
PY="$REPO_ROOT/env/bin/python"
if [[ -x "$PY" ]]; then
  exec "$PY" "$SCRIPT_DIR/rtp_from_lookup.py" "$@"
fi
exec python3 "$SCRIPT_DIR/rtp_from_lookup.py" "$@"
