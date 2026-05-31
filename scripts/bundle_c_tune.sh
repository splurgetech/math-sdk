#!/usr/bin/env bash
# Bundle C — middle ground after B if raw still high OR zero_wt still brutal.
# Closer to Stake cluster quotas; mild cool BR0; slightly less aggressive pay cut than B.
#
#   nohup ./scripts/bundle_c_tune.sh > /tmp/clash_bundle_c.log 2>&1 &
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GAME_DIR="$REPO_ROOT/games/0_0_clash_kronos"
LOG="${LOG:-/tmp/clash_bundle_c.log}"
TAG="bundle_c"

export DIST_FG_QUOTA=0.07
export DIST_ZERO_QUOTA=0.35
export PAYTABLE_SCALE=0.85
export TAG
export TUNING_LOG="$GAME_DIR/library/tuning_log.csv"
export SIM_BASE="${SIM_BASE:-150000}"
export SIM_BONUS="${SIM_BONUS:-20000}"
export SIM_THREADS="${SIM_THREADS:-10}"
export BR0_VARIANT=cool_mild

export HIDDEN_MULT_COVERAGE_MAX=0.45
export HIDDEN_MULT_SPIKE_MULT=0.4
export KRONOS_BAR_THRESHOLD=24
export KRONOS_WILD_PROB=0.22

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

if [[ "${BUNDLE_C_REBUILD_BR0:-1}" == "1" ]]; then
  log "========== $TAG: mild cool BR0 from committed stock =========="
  cd "$GAME_DIR"
  git checkout HEAD -- reels/BR0.csv 2>/dev/null || true
  python3 build_br0_cool.py 2>&1 | tee -a "$LOG"
  export SYNC_NUC_LOCAL=1
fi

log "========== $TAG sim+opt =========="
"$SCRIPT_DIR/tune_clash_kronos.sh" 2>&1 | tee -a "$LOG"
log "========== DONE $TAG =========="
