#!/usr/bin/env bash
# One tuning iteration: sync → NUC sim → pull → Mac optimize → RTP report.
#
# Sims ALWAYS run on the NUC (run_clash_kronos_sims.ps1). This script never
# invokes run.py with RUN_SIMS=1 on the Mac. Use ALLOW_MAC_SIMS=1 only for
# explicit local smoke tests outside this script.
#
# Usage:
#   DIST_FG_QUOTA=0.08 DIST_ZERO_QUOTA=0.10 TAG=quota_fg08 \
#     ./scripts/tune_clash_kronos.sh
#
#   SWEEP=1 ./scripts/tune_clash_kronos.sh    # runs quota matrix (runs 1–3)
#   PRODUCTION=1 ./scripts/tune_clash_kronos.sh  # 250k/50k final
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GAME_DIR="$REPO_ROOT/games/0_0_clash_kronos"
TUNING_LOG="${TUNING_LOG:-$GAME_DIR/library/tuning_log.csv}"

source "$SCRIPT_DIR/nuc_common.sh"

export PYTHONPATH="$REPO_ROOT:$GAME_DIR"
export PAYTABLE_SCALE="${PAYTABLE_SCALE:-1.0}"
export DIST_FG_QUOTA="${DIST_FG_QUOTA:-0.08}"
export DIST_ZERO_QUOTA="${DIST_ZERO_QUOTA:-0.10}"
# Do not export empty KRONOS_* — breaks game_constants int()/float() on Mac opt.
[[ -n "${KRONOS_WILD_PROB:-}" ]] && export KRONOS_WILD_PROB
[[ -n "${KRONOS_BAR_THRESHOLD:-}" ]] && export KRONOS_BAR_THRESHOLD
[[ -n "${HIDDEN_MULT_COVERAGE_MAX:-}" ]] && export HIDDEN_MULT_COVERAGE_MAX
[[ -n "${HIDDEN_MULT_SPIKE_MULT:-}" ]] && export HIDDEN_MULT_SPIKE_MULT
[[ -n "${BR0_VARIANT:-}" ]] && export BR0_VARIANT

SIM_BASE="${SIM_BASE:-150000}"
SIM_BONUS="${SIM_BONUS:-20000}"
SIM_THREADS="${SIM_THREADS:-10}"
SKIP_NUC="${SKIP_NUC:-0}"
SKIP_OPT="${SKIP_OPT:-0}"

if [[ "${PRODUCTION:-0}" == "1" ]]; then
  SIM_BASE=250000
  SIM_BONUS=50000
  TAG="${TAG:-production}"
fi

run_one() {
  local tag="$1"
  export TAG="$tag"
  echo "========== tune_clash_kronos: $tag (FG=$DIST_FG_QUOTA ZERO=$DIST_ZERO_QUOTA WILD=${KRONOS_WILD_PROB:-default} BAR=${KRONOS_BAR_THRESHOLD:-default} BR0=${BR0_VARIANT:-stock}) =========="

  if [[ "$SKIP_NUC" != "1" ]]; then
    if [[ "${SYNC_NUC_LOCAL:-0}" == "1" ]]; then
      "$SCRIPT_DIR/sync_to_nuc.sh" --local
    else
      "$SCRIPT_DIR/sync_to_nuc.sh"
    fi
    local ps_args="-SimBase $SIM_BASE -SimBonus $SIM_BONUS -PaytableScale $PAYTABLE_SCALE -DistFgQuota $DIST_FG_QUOTA -DistZeroQuota $DIST_ZERO_QUOTA -SimThreads $SIM_THREADS"
    [[ -n "${KRONOS_WILD_PROB:-}" ]] && ps_args="$ps_args -KronosWildProb $KRONOS_WILD_PROB"
    [[ -n "${KRONOS_BAR_THRESHOLD:-}" ]] && ps_args="$ps_args -KronosBarThreshold $KRONOS_BAR_THRESHOLD"
    [[ -n "${HIDDEN_MULT_COVERAGE_MAX:-}" ]] && ps_args="$ps_args -HiddenMultCoverageMax $HIDDEN_MULT_COVERAGE_MAX"
    [[ -n "${HIDDEN_MULT_SPIKE_MULT:-}" ]] && ps_args="$ps_args -HiddenMultSpikeMult $HIDDEN_MULT_SPIKE_MULT"
    nuc_ssh "cd $(nuc_repo_path) && powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_clash_kronos_sims.ps1 $ps_args"
    "$SCRIPT_DIR/pull_library_from_nuc.sh"
  fi

  if [[ "$SKIP_OPT" != "1" ]]; then
    "$SCRIPT_DIR/run_optimization.sh"
  fi

  chmod +x "$SCRIPT_DIR/run_rtp_report.sh"
  "$SCRIPT_DIR/run_rtp_report.sh" --tag "$tag" --csv-append "$TUNING_LOG"

  local snap="$GAME_DIR/library/tuning_runs/${tag}_$(date +%Y%m%d_%H%M%S)"
  mkdir -p "$snap"
  cp -R "$GAME_DIR/library/lookup_tables" "$snap/" 2>/dev/null || true
  cp -R "$GAME_DIR/library/publish_files" "$snap/" 2>/dev/null || true
  cp "$GAME_DIR/game_config.py" "$snap/" 2>/dev/null || true
  echo "Snapshot: $snap"
}

if [[ "${SWEEP:-0}" == "1" ]]; then
  git checkout HEAD -- "$GAME_DIR/reels/BR0.csv" 2>/dev/null || true
  export DIST_FG_QUOTA=0.08 DIST_ZERO_QUOTA=0.10
  run_one "quota_fg08_zero10"
  export DIST_FG_QUOTA=0.10 DIST_ZERO_QUOTA=0.10
  run_one "quota_fg10_zero10"
  export DIST_FG_QUOTA=0.08 DIST_ZERO_QUOTA=0.12
  run_one "quota_fg08_zero12"
  echo "Sweep done. Review $TUNING_LOG"
  exit 0
fi

run_one "${TAG:-manual}"
