#!/usr/bin/env bash
# Sync (git) then run Clash Kronos sims on the NUC.
#
# Usage:
#   ./scripts/run_sims_on_nuc.sh
#   ./scripts/run_sims_on_nuc.sh 150000 0          # SimBase SimBonus
#   ./scripts/run_sims_on_nuc.sh 150000 0 0.003    # + PAYTABLE_SCALE
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/nuc_common.sh"

SIM_BASE="${1:-150000}"
SIM_BONUS="${2:-0}"
PAYTABLE_SCALE="${3:-1.0}"

"$SCRIPT_DIR/sync_to_nuc.sh"

echo "=== Running sims on NUC (base=$SIM_BASE bonus=$SIM_BONUS scale=$PAYTABLE_SCALE) ==="
nuc_ssh "cd $(nuc_repo_path) && powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_clash_kronos_sims.ps1 -SimBase $SIM_BASE -SimBonus $SIM_BONUS -PaytableScale $PAYTABLE_SCALE"

echo "=== Sims finished. Pull results: ./scripts/pull_library_from_nuc.sh ==="
