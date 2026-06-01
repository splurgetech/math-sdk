#!/usr/bin/env bash
# Cool Clash raw_base: reliable NUC sims (detached + sentinel + short-poll) then Mac optimize.
# Survives Mac sleep / SSH drop because the NUC job is detached and we only short-poll a sentinel.
#
#   nohup ./scripts/cool_raw_tune.sh > /tmp/clash_cool_raw.log 2>&1 &
#
# Runs two variants by default (wincap 5000 vs 10000) with identical magnitude cuts.
# Override the set with VARIANTS="tag:maxwin tag:maxwin".
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GAME_DIR="$REPO_ROOT/games/0_0_clash_kronos"
source "$SCRIPT_DIR/nuc_common.sh"

# --- Magnitude-cut config (hybrid 35z/8fg + caps + capped global mult) ---
SIM_BASE="${SIM_BASE:-150000}"
SIM_BONUS="${SIM_BONUS:-20000}"
SIM_THREADS="${SIM_THREADS:-10}"
PAYTABLE_SCALE="${PAYTABLE_SCALE:-0.8}"
DIST_FG_QUOTA="${DIST_FG_QUOTA:-0.08}"
DIST_ZERO_QUOTA="${DIST_ZERO_QUOTA:-0.35}"
KRONOS_WILD_PROB="${KRONOS_WILD_PROB:-0.13}"
KRONOS_BAR_THRESHOLD="${KRONOS_BAR_THRESHOLD:-24}"
HIDDEN_MULT_COVERAGE_MAX="${HIDDEN_MULT_COVERAGE_MAX:-0.42}"
HIDDEN_MULT_SPIKE_MULT="${HIDDEN_MULT_SPIKE_MULT:-0.3}"
# Global multiplier is the core game mechanic — it MUST stay uncapped (0 = off).
# This knob exists only as an optional safety rail; never use it as a balance lever.
MAX_GLOBAL_MULT="${MAX_GLOBAL_MULT:-0}"

POLL_SECS="${POLL_SECS:-180}"
MAX_WAIT_SECS="${MAX_WAIT_SECS:-10800}"   # 3h hard ceiling per variant
TUNING_LOG="${TUNING_LOG:-$GAME_DIR/library/tuning_log.csv}"
VARIANTS="${VARIANTS:-cool_wc5000:5000 cool_wc10000:10000}"

NUC_STATUS="$(nuc_repo_path)/games/0_0_clash_kronos/library/.sim_status"

log() { echo "[$(date +%H:%M:%S)] $*"; }

# Keep the Mac awake while attended (no-op safety if it sleeps anyway: NUC job is detached).
if command -v caffeinate >/dev/null 2>&1; then
  caffeinate -dimsu -w $$ >/dev/null 2>&1 &
fi

nuc_status() {
  nuc_ssh "powershell -NoProfile -Command \"if (Test-Path '$NUC_STATUS') { Get-Content '$NUC_STATUS' } else { 'MISSING' }\"" 2>/dev/null | tr -d '\r' | tail -1
}

nuc_python_count() {
  nuc_ssh "powershell -NoProfile -Command \"(Get-CimInstance Win32_Process -Filter \\\"name='python.exe'\\\" | Where-Object { \$_.CommandLine -match 'run.py' }).Count\"" 2>/dev/null | tr -d '\r' | tr -d ' ' | tail -1
}

run_variant() {
  local tag="$1" maxwin="$2"
  log "========== $tag (MAX_WIN=$maxwin MAX_GMULT=$MAX_GLOBAL_MULT FG=$DIST_FG_QUOTA ZERO=$DIST_ZERO_QUOTA SCALE=$PAYTABLE_SCALE BAR=$KRONOS_BAR_THRESHOLD) =========="

  # 1) Preflight: code to NUC via git (commit+push must be done before running this script).
  "$SCRIPT_DIR/sync_to_nuc.sh"

  # 2) Launch detached sim on NUC (returns immediately).
  log "Launching detached NUC sim..."
  nuc_ssh "cd $(nuc_repo_path) && powershell -NoProfile -ExecutionPolicy Bypass -File scripts/nuc_run_detached.ps1 \
    -SimBase $SIM_BASE -SimBonus $SIM_BONUS -PaytableScale $PAYTABLE_SCALE \
    -DistFgQuota $DIST_FG_QUOTA -DistZeroQuota $DIST_ZERO_QUOTA \
    -KronosWildProb $KRONOS_WILD_PROB -KronosBarThreshold $KRONOS_BAR_THRESHOLD \
    -HiddenMultCoverageMax $HIDDEN_MULT_COVERAGE_MAX -HiddenMultSpikeMult $HIDDEN_MULT_SPIKE_MULT \
    -MaxWin $maxwin -MaxGlobalMult $MAX_GLOBAL_MULT -SimThreads $SIM_THREADS"

  # 3) Short-poll the sentinel. Each poll is a fast SSH; Mac sleep only delays polling.
  local waited=0
  while true; do
    sleep "$POLL_SECS"
    waited=$((waited + POLL_SECS))
    local st; st="$(nuc_status || echo UNREACHABLE)"
    local py; py="$(nuc_python_count || echo '?')"
    log "  poll ${waited}s: status='$st' python=$py"

    case "$st" in
      DONE*) log "  NUC sims DONE."; break ;;
      FAIL*) log "  NUC sims FAILED ($st). Aborting $tag."; return 1 ;;
      RUNNING*)
        if [[ "$py" == "0" ]]; then
          log "  python died with status still RUNNING -> FAIL $tag."; return 1
        fi
        ;;
      UNREACHABLE) log "  NUC unreachable this poll (sleep/network); will retry." ;;
      MISSING) log "  no sentinel yet; will retry." ;;
    esac

    if [[ "$waited" -ge "$MAX_WAIT_SECS" ]]; then
      log "  exceeded MAX_WAIT_SECS ($MAX_WAIT_SECS) -> timeout FAIL $tag."; return 1
    fi
  done

  # 4) Pull + Mac optimize + RTP report + log + snapshot.
  log "Pulling library..."
  "$SCRIPT_DIR/pull_library_from_nuc.sh"

  log "Optimizing on Mac + RTP report (tag=$tag)..."
  SKIP_NUC=1 TAG="$tag" TUNING_LOG="$TUNING_LOG" \
    DIST_FG_QUOTA="$DIST_FG_QUOTA" DIST_ZERO_QUOTA="$DIST_ZERO_QUOTA" PAYTABLE_SCALE="$PAYTABLE_SCALE" \
    KRONOS_WILD_PROB="$KRONOS_WILD_PROB" KRONOS_BAR_THRESHOLD="$KRONOS_BAR_THRESHOLD" \
    HIDDEN_MULT_COVERAGE_MAX="$HIDDEN_MULT_COVERAGE_MAX" HIDDEN_MULT_SPIKE_MULT="$HIDDEN_MULT_SPIKE_MULT" \
    MAX_WIN="$maxwin" MAX_GLOBAL_MULT="$MAX_GLOBAL_MULT" \
    "$SCRIPT_DIR/tune_clash_kronos.sh"

  log "========== $tag complete =========="
  return 0
}

overall=0
for spec in $VARIANTS; do
  tag="${spec%%:*}"
  maxwin="${spec##*:}"
  if ! run_variant "$tag" "$maxwin"; then
    log "Variant $tag did not complete; continuing to next."
    overall=1
  fi
done

log "All variants attempted. Results: $TUNING_LOG"
exit $overall
