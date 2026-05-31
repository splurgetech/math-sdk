#!/usr/bin/env bash
# Overnight base tune: Kronos wild % × BR0 variant × bar threshold (16 runs).
#
#   nohup ./scripts/sweep_base_overnight.sh > /tmp/clash_base_sweep.log 2>&1 </dev/null &
#   disown
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GAME_DIR="$REPO_ROOT/games/0_0_clash_kronos"
TUNING_LOG="${TUNING_LOG:-$GAME_DIR/library/sweep_base_tuning_log.csv}"

export PAYTABLE_SCALE=1.0
export DIST_FG_QUOTA=0.08
export DIST_ZERO_QUOTA=0.12

WILDS=(0.25 0.20 0.15 0.10)
BARS=(20 24)
BR0_VARIANTS=(stock cool_mild)

log() { echo "[$(date +%H:%M:%S)] $*"; }

# Fresh log with extended columns (keep legacy file intact).
if [[ -f "$TUNING_LOG" ]]; then
  mv "$TUNING_LOG" "${TUNING_LOG%.csv}_backup_$(date +%Y%m%d_%H%M%S).csv"
fi

log "=== sweep_base_overnight: 16 runs → $TUNING_LOG ==="
cd "$REPO_ROOT"
chmod +x "$SCRIPT_DIR/tune_clash_kronos.sh"

run_count=0
fail_count=0

for wild in "${WILDS[@]}"; do
  for br0 in "${BR0_VARIANTS[@]}"; do
    for bar in "${BARS[@]}"; do
      run_count=$((run_count + 1))
      wtag="${wild//./}"
      tag="w${wtag}_b${bar}_br0${br0}"

      log "---------- Run $run_count/16: $tag ----------"

      if [[ "$br0" == "stock" ]]; then
        git checkout HEAD -- "$GAME_DIR/reels/BR0.csv" 2>/dev/null || true
      else
        git checkout HEAD -- "$GAME_DIR/reels/BR0.csv" 2>/dev/null || true
        python3 "$GAME_DIR/build_br0_cool.py"
      fi

      export KRONOS_WILD_PROB="$wild"
      export KRONOS_BAR_THRESHOLD="$bar"
      export BR0_VARIANT="$br0"
      export TAG="$tag"
      export TUNING_LOG

      if ! "$SCRIPT_DIR/tune_clash_kronos.sh"; then
        log "ERROR: run failed: $tag"
        fail_count=$((fail_count + 1))
      fi
    done
  done
done

log "=== Sweep complete: $run_count runs, $fail_count failed ==="
log "Review: $TUNING_LOG"
"$SCRIPT_DIR/summarize_tuning_log.sh" "$TUNING_LOG" || true
