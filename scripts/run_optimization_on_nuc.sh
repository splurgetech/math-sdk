#!/usr/bin/env bash
# Run Rust optimization on NUC after sims (pull library first if you only have books on Mac).
# Usage:
#   ./scripts/run_optimization_on_nuc.sh
#   OPT_MODES=base ./scripts/run_optimization_on_nuc.sh
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/nuc_common.sh"

if [[ "${SKIP_SYNC:-}" != "1" ]]; then
  "$SCRIPT_DIR/sync_to_nuc.sh"
fi

OPT_ARG="${OPT_MODES:-}"
if [[ -n "$OPT_ARG" ]]; then
  nuc_ssh "powershell -NoProfile -ExecutionPolicy Bypass -File C:/Users/evanl/math-sdk/scripts/run_opt_on_nuc.ps1 -OptModes '$OPT_ARG'"
else
  nuc_ssh "powershell -NoProfile -ExecutionPolicy Bypass -File C:/Users/evanl/math-sdk/scripts/run_opt_on_nuc.ps1"
fi

echo "=== Optimization finished. Pull: ./scripts/pull_library_from_nuc.sh ==="
echo "=== RTP check: ./scripts/rtp_from_lookup.sh ==="
