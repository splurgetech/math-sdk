#!/usr/bin/env bash
# Detached NUC sims (40% zero / 10% FG) → poll → pull → Mac opt → RTP log.
#
#   nohup ./scripts/sample_buckets_overnight.sh > /tmp/clash_sample_buckets_overnight.log 2>&1 &
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GAME_DIR="$REPO_ROOT/games/0_0_clash_kronos"
LOG="/tmp/clash_sample_buckets_overnight.log"
TAG="sample_buckets_40z10fg"
POLL_SEC="${POLL_SEC:-120}"
MAX_WAIT_SEC="${MAX_WAIT_SEC:-28800}"

export DIST_FG_QUOTA=0.10
export DIST_ZERO_QUOTA=0.40
export TAG
export TUNING_LOG="$GAME_DIR/library/tuning_log.csv"
export PAYTABLE_SCALE="${PAYTABLE_SCALE:-1.0}"
export SIM_BASE="${SIM_BASE:-150000}"
export SIM_BONUS="${SIM_BONUS:-20000}"
export SIM_THREADS="${SIM_THREADS:-10}"

source "$SCRIPT_DIR/nuc_common.sh"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

log "========== $TAG overnight (FG=$DIST_FG_QUOTA ZERO=$DIST_ZERO_QUOTA threads=$SIM_THREADS) =========="
"$SCRIPT_DIR/sync_to_nuc.sh" --local 2>&1 | tee -a "$LOG"

log "Starting detached NUC sims..."
nuc_ssh "cd $(nuc_repo_path) && powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start_nuc_sims_detached.ps1 -SimBase $SIM_BASE -SimBonus $SIM_BONUS -PaytableScale $PAYTABLE_SCALE -DistFgQuota $DIST_FG_QUOTA -DistZeroQuota $DIST_ZERO_QUOTA -SimThreads $SIM_THREADS" \
  2>&1 | tee -a "$LOG"

elapsed=0
nuc_done() {
  nuc_ssh "powershell -NoProfile -Command \"Test-Path '$(nuc_repo_path)/games/0_0_clash_kronos/library/$1'\""
}

while [[ $elapsed -lt $MAX_WAIT_SEC ]]; do
  if nuc_done "nuc_sim.done" | grep -q True; then
    log "NUC sims finished (nuc_sim.done)"
    break
  fi
  if nuc_done "nuc_sim.failed" | grep -q True; then
    log "NUC sims FAILED — tail nuc_sim.log:"
    nuc_ssh "powershell -NoProfile -Command \"Get-Content $(nuc_repo_path)/games/0_0_clash_kronos/library/nuc_sim.log -Tail 40\"" 2>&1 | tee -a "$LOG" || true
    exit 1
  fi
  log "Waiting (${elapsed}s / ${MAX_WAIT_SEC}s)..."
  nuc_ssh "powershell -NoProfile -Command \"if (Test-Path $(nuc_repo_path)/games/0_0_clash_kronos/library/nuc_sim.log) { Get-Content $(nuc_repo_path)/games/0_0_clash_kronos/library/nuc_sim.log -Tail 3 }\"" 2>&1 | tee -a "$LOG" || true
  sleep "$POLL_SEC"
  elapsed=$((elapsed + POLL_SEC))
done

if [[ $elapsed -ge $MAX_WAIT_SEC ]]; then
  log "ERROR: timed out waiting for NUC sims"
  exit 1
fi

"$SCRIPT_DIR/pull_library_from_nuc.sh" 2>&1 | tee -a "$LOG"
export PYTHONPATH="$REPO_ROOT:$GAME_DIR"
export SKIP_NUC=1
"$SCRIPT_DIR/tune_clash_kronos.sh" 2>&1 | tee -a "$LOG"

log "========== DONE $TAG =========="
