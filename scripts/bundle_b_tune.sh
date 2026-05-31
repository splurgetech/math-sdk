#!/usr/bin/env bash
# Bundle B — aggressive raw pool reduction (quotas + cool BR0 + pay caps + feature cool-down).
#
#   nohup ./scripts/bundle_b_tune.sh > /tmp/clash_bundle_b.log 2>&1 &
#
# Levers:
#   30% zero / 6% FG (was 40/10)
#   PAYTABLE_SCALE=0.8 + cluster-aligned per-symbol caps (game_paytable.py)
#   Strong cool BR0 (rebuild before sync)
#   Hidden mult coverage max 40%, 10×/20× spike weight ×0.25
#   Kronos bar 28, wild transform 18%
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GAME_DIR="$REPO_ROOT/games/0_0_clash_kronos"
LOG="${LOG:-/tmp/clash_bundle_b.log}"
TAG="bundle_b"

export DIST_FG_QUOTA=0.06
export DIST_ZERO_QUOTA=0.30
export PAYTABLE_SCALE=0.8
export TAG
export TUNING_LOG="$GAME_DIR/library/tuning_log.csv"
export SIM_BASE="${SIM_BASE:-150000}"
export SIM_BONUS="${SIM_BONUS:-20000}"
export SIM_THREADS="${SIM_THREADS:-10}"
export BR0_VARIANT=cool_strong
export SYNC_NUC_LOCAL=1

# Feature cool-down (big tail cut)
export HIDDEN_MULT_COVERAGE_MAX=0.40
export HIDDEN_MULT_SPIKE_MULT=0.25
export KRONOS_BAR_THRESHOLD=28
export KRONOS_WILD_PROB=0.18

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

# BR0 strong-cool is committed in git; do not rebuild here (double-cool bug).
# To regenerate once: cd games/0_0_clash_kronos && git checkout HEAD -- reels/BR0.csv && BR0_COOL_STRONG=1 python3 build_br0_cool.py && commit.
if [[ "${BUNDLE_B_REBUILD_BR0:-0}" == "1" ]]; then
  log "========== $TAG: rebuild BR0 (strong cool, from stock in git) =========="
  cd "$GAME_DIR"
  git checkout HEAD -- reels/BR0.csv 2>/dev/null || true
  BR0_COOL_STRONG=1 python3 build_br0_cool.py 2>&1 | tee -a "$LOG"
fi

log "========== $TAG sim+opt (FG=$DIST_FG_QUOTA ZERO=$DIST_ZERO_QUOTA scale=$PAYTABLE_SCALE) =========="
"$SCRIPT_DIR/tune_clash_kronos.sh" 2>&1 | tee -a "$LOG"
log "========== DONE $TAG — see $TUNING_LOG =========="
