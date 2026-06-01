#!/usr/bin/env bash
# Ghostblade-aligned NUC sims (detached) -> Mac pull -> optimize -> RTP log.
#
#   ./scripts/run_gb_pay_nuc.sh
#   SIM_THREADS=8 ./scripts/run_gb_pay_nuc.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GAME_DIR="$REPO_ROOT/games/0_0_clash_kronos"
source "$SCRIPT_DIR/nuc_common.sh"

TAG="${TAG:-gb_pay_1.0}"
SIM_BASE="${SIM_BASE:-20000}"
SIM_BONUS="${SIM_BONUS:-5000}"
SIM_THREADS="${SIM_THREADS:-8}"
POLL_SECS="${POLL_SECS:-180}"
MAX_WAIT_SECS="${MAX_WAIT_SECS:-14400}"
TUNING_LOG="${TUNING_LOG:-$GAME_DIR/library/tuning_log.csv}"

NUC_STATUS="$(nuc_repo_path)/games/0_0_clash_kronos/library/.sim_status"

log() { echo "[$(date +%H:%M:%S)] $*"; }

log "========== $TAG NUC sims (${SIM_BASE} base / ${SIM_BONUS} bonus, ${SIM_THREADS} threads) =========="

"$SCRIPT_DIR/sync_to_nuc.sh"

log "Launching detached sim on NUC..."
nuc_ssh "cd $(nuc_repo_path) && powershell -NoProfile -ExecutionPolicy Bypass -File scripts/nuc_run_detached.ps1 \
  -SimBase $SIM_BASE -SimBonus $SIM_BONUS -SimThreads $SIM_THREADS \
  -PaytableScale 1.0 -DistFgQuota 0.10 -DistZeroQuota 0.10 \
  -KronosWildProb 0.13 -KronosBarThreshold 24 \
  -HiddenMultCoverageMax 0.42 -HiddenMultSpikeMult 0.3 \
  -MaxWin 10000 -MaxGlobalMult 0" 2>&1 | tail -2

waited=0
while true; do
  sleep "$POLL_SECS"
  waited=$((waited + POLL_SECS))
  st=$(nuc_ssh 'type math-sdk\games\0_0_clash_kronos\library\.sim_status' 2>/dev/null | tr -d '\r' | tail -1)
  fin=$(scp -q nuc:math-sdk/games/0_0_clash_kronos/library/.sim_run.log /tmp/nuc_gb_pay.log 2>/dev/null && tr -d '\000' < /tmp/nuc_gb_pay.log | grep -c "Thread .* finished" || echo 0)
  log "poll ${waited}s: $st | threads_finished=$fin"
  case "$st" in
    DONE*) break ;;
    FAIL*) log "NUC sim FAILED: $st"; exit 1 ;;
  esac
  if [[ "$waited" -ge "$MAX_WAIT_SECS" ]]; then
    log "timeout after ${MAX_WAIT_SECS}s"; exit 1
  fi
done

log "Pulling library..."
"$SCRIPT_DIR/pull_library_from_nuc.sh"

log "Optimizing on Mac..."
export PYTHONPATH="$REPO_ROOT:$GAME_DIR"
export KRONOS_WILD_PROB=0.13 KRONOS_BAR_THRESHOLD=24
export PAYTABLE_SCALE=1.0 DIST_FG_QUOTA=0.10 DIST_ZERO_QUOTA=0.10
export MAX_WIN=10000
"$SCRIPT_DIR/run_optimization.sh"

TAG="$TAG" "$SCRIPT_DIR/run_rtp_report.sh" --tag "$TAG" --csv-append "$TUNING_LOG"

SNAP="$GAME_DIR/library/tuning_runs/${TAG}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$SNAP"
cp -R "$GAME_DIR/library/lookup_tables" "$SNAP/" 2>/dev/null || true
cp -R "$GAME_DIR/library/publish_files" "$SNAP/" 2>/dev/null || true
log "Done. Snapshot: $SNAP"
