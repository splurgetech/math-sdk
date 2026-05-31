#!/usr/bin/env bash
# 40% zero / 10% FG: Stake workflow (git sync → NUC sims → pull → Mac opt).
#
#   nohup ./scripts/sample_buckets_overnight.sh > /tmp/clash_sample_buckets.log 2>&1 &
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GAME_DIR="$REPO_ROOT/games/0_0_clash_kronos"
LOG="${LOG:-/tmp/clash_sample_buckets.log}"
TAG="sample_buckets_40z10fg"

export DIST_FG_QUOTA=0.10
export DIST_ZERO_QUOTA=0.40
export TAG
export TUNING_LOG="$GAME_DIR/library/tuning_log.csv"
export PAYTABLE_SCALE="${PAYTABLE_SCALE:-1.0}"
export SIM_BASE="${SIM_BASE:-150000}"
export SIM_BONUS="${SIM_BONUS:-20000}"
export SIM_THREADS="${SIM_THREADS:-4}"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

log "========== $TAG (FG=$DIST_FG_QUOTA ZERO=$DIST_ZERO_QUOTA threads=$SIM_THREADS) =========="
"$SCRIPT_DIR/run_sims_on_nuc.sh" "$SIM_BASE" "$SIM_BONUS" "$PAYTABLE_SCALE" 2>&1 | tee -a "$LOG"
"$SCRIPT_DIR/pull_library_from_nuc.sh" 2>&1 | tee -a "$LOG"
export PYTHONPATH="$REPO_ROOT:$GAME_DIR"
export SKIP_NUC=1
"$SCRIPT_DIR/tune_clash_kronos.sh" 2>&1 | tee -a "$LOG"
log "========== DONE $TAG =========="
