#!/usr/bin/env bash
# Ghostblade-aligned local tune: full pay ladder, cluster quotas/opt, Kronos 24/13%.
# Mac only — set ALLOW_MAC_SIMS=1. Example:
#   ./scripts/run_gb_pay_local.sh
#   SIM_BASE=10000 ./scripts/run_gb_pay_local.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GAME_DIR="$REPO_ROOT/games/0_0_clash_kronos"
TAG="${TAG:-gb_pay_1.0}"

export PYTHONPATH="$REPO_ROOT:$GAME_DIR"
export ALLOW_MAC_SIMS=1

# Ghostblade published pay ladder (bet = 1.00)
export PAYTABLE_SCALE="${PAYTABLE_SCALE:-1.0}"
export PAYTABLE_CAP_H1="${PAYTABLE_CAP_H1:-100}"

# Cluster sample sim quotas
export DIST_FG_QUOTA="${DIST_FG_QUOTA:-0.10}"
export DIST_ZERO_QUOTA="${DIST_ZERO_QUOTA:-0.10}"

# Kronos (current cool direction)
export KRONOS_BAR_THRESHOLD="${KRONOS_BAR_THRESHOLD:-24}"
export KRONOS_WILD_PROB="${KRONOS_WILD_PROB:-0.13}"

# Hidden mult: tame growth, uncapped global mult (core mechanic)
export HIDDEN_MULT_COVERAGE_MAX="${HIDDEN_MULT_COVERAGE_MAX:-0.42}"
export HIDDEN_MULT_SPIKE_MULT="${HIDDEN_MULT_SPIKE_MULT:-0.3}"
export MAX_GLOBAL_MULT="${MAX_GLOBAL_MULT:-0}"

export MAX_WIN="${MAX_WIN:-10000}"

SIM_BASE="${SIM_BASE:-20000}"
SIM_BONUS="${SIM_BONUS:-5000}"
SIM_THREADS="${SIM_THREADS:-4}"
RUST_THREADS="${RUST_THREADS:-8}"

TUNING_LOG="${TUNING_LOG:-$GAME_DIR/library/tuning_log.csv}"

echo "========== $TAG (local Mac) scale=$PAYTABLE_SCALE cap_H1=$PAYTABLE_CAP_H1 ${DIST_ZERO_QUOTA}z/${DIST_FG_QUOTA}fg bar=$KRONOS_BAR_THRESHOLD wild=$KRONOS_WILD_PROB =========="
echo "SIM_BASE=$SIM_BASE SIM_BONUS=$SIM_BONUS SIM_THREADS=$SIM_THREADS"

rm -rf "$GAME_DIR/library/temp_multi_threaded_files/"*

cd "$GAME_DIR"
export RUN_SIMS=1
export RUN_OPTIMIZATION=0
export RUN_ANALYSIS=0
export RUN_FORMAT_CHECKS=0
export SIM_BASE SIM_BONUS SIM_THREADS

PY="$REPO_ROOT/env/bin/python"
if [[ ! -x "$PY" ]]; then
  PY=python3
fi

echo "=== Sims ==="
"$PY" run.py

echo "=== Optimize ==="
cd "$REPO_ROOT"
export RUN_SIMS=0
export RUN_OPTIMIZATION=1
SIM_BASE=0 SIM_BONUS=0 "$SCRIPT_DIR/run_optimization.sh"

echo "=== RTP report ==="
TAG="$TAG" "$SCRIPT_DIR/run_rtp_report.sh" --tag "$TAG" --csv-append "$TUNING_LOG"

SNAP="$GAME_DIR/library/tuning_runs/${TAG}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$SNAP"
cp -R "$GAME_DIR/library/lookup_tables" "$SNAP/" 2>/dev/null || true
cp -R "$GAME_DIR/library/publish_files" "$SNAP/" 2>/dev/null || true
echo "Snapshot: $SNAP"
echo "Done. See $TUNING_LOG"
