#!/usr/bin/env bash
# Base FG quota micro-sweep: cut forced freegame sim share (publish FS stays ~hr=200).
#
#   nohup ./scripts/sweep_fg_quota.sh > /tmp/clash_fg_quota_sweep.log 2>&1 </dev/null &
#   disown
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GAME_DIR="$REPO_ROOT/games/0_0_clash_kronos"
export TUNING_LOG="${TUNING_LOG:-$GAME_DIR/library/fg_quota_sweep_log.csv}"

export PAYTABLE_SCALE=1.0
unset KRONOS_WILD_PROB KRONOS_BAR_THRESHOLD BR0_VARIANT || true

log() { echo "[$(date +%H:%M:%S)] $*"; }

if [[ -f "$TUNING_LOG" ]]; then
  mv "$TUNING_LOG" "${TUNING_LOG%.csv}_backup_$(date +%Y%m%d_%H%M%S).csv"
fi

log "=== sweep_fg_quota: 4 runs → $TUNING_LOG ==="
cd "$REPO_ROOT"
chmod +x "$SCRIPT_DIR/tune_clash_kronos.sh"

run_count=0
fail_count=0

# tag fg_quota zero_quota
RUNS=(
  "fg04_zero12:0.04:0.12"
  "fg05_zero12:0.05:0.12"
  "fg06_zero12:0.06:0.12"
  "fg05_zero10:0.05:0.10"
)

for spec in "${RUNS[@]}"; do
  IFS=: read -r tag fg zero <<< "$spec"
  run_count=$((run_count + 1))
  log "---------- Run $run_count/4: $tag (FG=$fg ZERO=$zero) ----------"
  git checkout HEAD -- "$GAME_DIR/reels/BR0.csv" 2>/dev/null || true
  export DIST_FG_QUOTA="$fg"
  export DIST_ZERO_QUOTA="$zero"
  export TAG="$tag"
  if ! "$SCRIPT_DIR/tune_clash_kronos.sh"; then
    log "ERROR: run failed: $tag"
    fail_count=$((fail_count + 1))
  fi
done

log "=== Sweep complete: $run_count runs, $fail_count failed ==="
log "Review: $TUNING_LOG"
"$SCRIPT_DIR/summarize_tuning_log.sh" "$TUNING_LOG" || true
