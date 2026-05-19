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
PAYTABLE_SCALE="${3:-0.003}"

"$SCRIPT_DIR/sync_to_nuc.sh"

echo "=== Running sims on NUC (base=$SIM_BASE bonus=$SIM_BONUS scale=$PAYTABLE_SCALE) ==="
nuc_ssh "powershell -NoProfile -ExecutionPolicy Bypass -Command \"
  Set-Location \\\$HOME\\$(nuc_repo_path);
  \\\$env:SIM_BASE='$SIM_BASE';
  \\\$env:SIM_BONUS='$SIM_BONUS';
  \\\$env:PAYTABLE_SCALE='$PAYTABLE_SCALE';
  Remove-Item Env:KRONOS_UNCAPPED_FS -ErrorAction SilentlyContinue;
  .\\scripts\\run_clash_kronos_sims.ps1 -SimBase $SIM_BASE -SimBonus $SIM_BONUS -PaytableScale $PAYTABLE_SCALE;
  if (\\\$LASTEXITCODE -ne 0) { exit \\\$LASTEXITCODE }
\""

echo "=== Sims finished. Pull results: ./scripts/pull_library_from_nuc.sh ==="
