#!/usr/bin/env bash
# Tone-down validation: cooled pays + quotas, stratified threads, long join timeout.
#
#   ./scripts/run_tone_down_nuc.sh
#   SIM_BASE=5000 SIM_BONUS=1000 ./scripts/run_tone_down_nuc.sh   # smoke
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GAME_DIR="$REPO_ROOT/games/0_0_clash_kronos"
source "$SCRIPT_DIR/nuc_common.sh"

export TAG="${TAG:-tone_down_v1}"
export SIM_BASE="${SIM_BASE:-20000}"
export SIM_BONUS="${SIM_BONUS:-5000}"
export SIM_THREADS="${SIM_THREADS:-8}"
export SIM_JOIN_TIMEOUT_SEC="${SIM_JOIN_TIMEOUT_SEC:-28800}"
export PAYTABLE_SCALE="${PAYTABLE_SCALE:-0.8}"
export DIST_FG_QUOTA="${DIST_FG_QUOTA:-0.08}"
export DIST_ZERO_QUOTA="${DIST_ZERO_QUOTA:-0.28}"
export KRONOS_WILD_PROB="${KRONOS_WILD_PROB:-0.10}"
export KRONOS_BAR_THRESHOLD="${KRONOS_BAR_THRESHOLD:-25}"
export HIDDEN_MULT_COVERAGE_MAX="${HIDDEN_MULT_COVERAGE_MAX:-0.50}"
export MAX_WIN="${MAX_WIN:-10000}"
export MAX_GLOBAL_MULT="${MAX_GLOBAL_MULT:-0}"

POLL_SECS="${POLL_SECS:-180}"
MAX_WAIT_SECS="${MAX_WAIT_SECS:-43200}"
TUNING_LOG="${TUNING_LOG:-$GAME_DIR/library/tuning_log.csv}"

log() { echo "[$(date +%H:%M:%S)] $*"; }

log "========== $TAG NUC (${SIM_BASE} base / ${SIM_BONUS} bonus, ${SIM_THREADS} threads, scale=$PAYTABLE_SCALE) =========="

if [[ "${SYNC_LOCAL:-0}" == "1" ]]; then
  "$SCRIPT_DIR/sync_to_nuc.sh" --local
else
  "$SCRIPT_DIR/sync_to_nuc.sh"
fi

log "Launching detached sim on NUC (join timeout ${SIM_JOIN_TIMEOUT_SEC}s)..."
nuc_ssh "cd $(nuc_repo_path) && set SIM_JOIN_TIMEOUT_SEC=$SIM_JOIN_TIMEOUT_SEC&& powershell -NoProfile -ExecutionPolicy Bypass -File scripts/nuc_run_detached.ps1 \
  -SimBase $SIM_BASE -SimBonus $SIM_BONUS -SimThreads $SIM_THREADS \
  -PaytableScale $PAYTABLE_SCALE -DistFgQuota $DIST_FG_QUOTA -DistZeroQuota $DIST_ZERO_QUOTA \
  -KronosWildProb $KRONOS_WILD_PROB -KronosBarThreshold $KRONOS_BAR_THRESHOLD \
  -HiddenMultCoverageMax $HIDDEN_MULT_COVERAGE_MAX -MaxWin $MAX_WIN -MaxGlobalMult $MAX_GLOBAL_MULT" 2>&1 | tail -2

waited=0
while true; do
  sleep "$POLL_SECS"
  waited=$((waited + POLL_SECS))
  st=$(nuc_ssh 'type math-sdk\games\0_0_clash_kronos\library\.sim_status' 2>/dev/null | tr -d '\r' | tail -1)
  fin=$(scp -q nuc:math-sdk/games/0_0_clash_kronos/library/.sim_run.log /tmp/nuc_tone_down.log 2>/dev/null && tr -d '\000' < /tmp/nuc_tone_down.log | grep -c "Thread .* finished" || echo 0)
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
"$SCRIPT_DIR/run_optimization.sh"

TAG="$TAG" "$SCRIPT_DIR/run_rtp_report.sh" --tag "$TAG" --csv-append "$TUNING_LOG"

SNAP="$GAME_DIR/library/tuning_runs/${TAG}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$SNAP"
cp -R "$GAME_DIR/library/lookup_tables" "$SNAP/" 2>/dev/null || true
cp -R "$GAME_DIR/library/publish_files" "$SNAP/" 2>/dev/null || true
log "Done. Snapshot: $SNAP"
