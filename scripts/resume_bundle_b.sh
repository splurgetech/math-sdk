#!/usr/bin/env bash
# Resume after laptop sleep / SSH drop: NUC sims already finished; pull LUTs + Mac opt only.
#
#   ./scripts/resume_bundle_b.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Kill stale Mac pipeline (sleeping SSH wait)
pkill -f "bundle_b_tune.sh" 2>/dev/null || true
pkill -f "tee -a /tmp/clash_bundle_b.log" 2>/dev/null || true

export TAG=bundle_b
export DIST_FG_QUOTA=0.06
export DIST_ZERO_QUOTA=0.30
export PAYTABLE_SCALE=0.8
export KRONOS_BAR_THRESHOLD=28
export KRONOS_WILD_PROB=0.18
export HIDDEN_MULT_COVERAGE_MAX=0.40
export HIDDEN_MULT_SPIKE_MULT=0.25
export SKIP_NUC=1

echo "Pulling library from NUC (LUTs from bundle_b sims)..."
"$SCRIPT_DIR/pull_library_from_nuc.sh"

echo "Mac optimization + RTP report (cluster opt fences on main)..."
"$SCRIPT_DIR/tune_clash_kronos.sh"

echo "Done. See library/tuning_log.csv for bundle_b row."
