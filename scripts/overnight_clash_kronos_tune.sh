#!/usr/bin/env bash
# Overnight RTP tuning: run sim variants on NUC, optimize locally, log raw vs publish RTP.
#
# Usage (from math-sdk repo root):
#   nohup ./scripts/overnight_clash_kronos_tune.sh > /tmp/clash_overnight.log 2>&1 &
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GAME_DIR="$REPO_ROOT/games/0_0_clash_kronos"
LOG_DIR="$GAME_DIR/library/overnight_runs"
SIM_BASE="${SIM_BASE:-150000}"
SIM_BONUS="${SIM_BONUS:-20000}"
PAYTABLE_SCALE="${PAYTABLE_SCALE:-1.0}"

source "$SCRIPT_DIR/nuc_common.sh"

mkdir -p "$LOG_DIR"
STAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="$LOG_DIR/run_${STAMP}.log"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$MASTER_LOG"; }

rtp_report() {
  local tag="$1"
  local out="$LOG_DIR/${tag}_rtp.txt"
  {
    echo "=== $tag $(date -Iseconds) ==="
    python3 "$REPO_ROOT/scripts/rtp_from_lookup.py" \
      "$GAME_DIR/library/lookup_tables/lookUpTable_base.csv" \
      "$GAME_DIR/library/publish_files/lookUpTable_base_0.csv" 1.0
    python3 "$REPO_ROOT/scripts/rtp_from_lookup.py" \
      "$GAME_DIR/library/lookup_tables/lookUpTable_bonus.csv" \
      "$GAME_DIR/library/publish_files/lookUpTable_bonus_0.csv" 100.0
    python3 - "$GAME_DIR/library/lookup_tables/lookUpTableSegmented_base.csv" << 'PY'
import sys
from collections import defaultdict
path = sys.argv[1]
by = defaultdict(list)
with open(path) as f:
    for line in f:
        p = line.strip().split(",")
        if len(p) >= 4:
            by[p[1]].append(float(p[2]) + float(p[3]))
for c in ("0", "basegame", "freegame", "wincap"):
    if c in by:
        v = by[c]
        print(f"  {c}: n={len(v)} mean={sum(v)/len(v):.2f}x")
PY
  } >>"$out" 2>&1
  cat "$out" | tee -a "$MASTER_LOG"
}

save_snapshot() {
  local tag="$1"
  local dest="$LOG_DIR/${tag}_${STAMP}"
  mkdir -p "$dest"
  cp -R "$GAME_DIR/library/lookup_tables" "$dest/" 2>/dev/null || true
  cp -R "$GAME_DIR/library/publish_files" "$dest/" 2>/dev/null || true
  cp "$GAME_DIR/reels/BR0.csv" "$dest/BR0.csv" 2>/dev/null || true
  cp "$GAME_DIR/game_config.py" "$dest/game_config.py" 2>/dev/null || true
  log "Snapshot saved: $dest"
}

run_variant() {
  local tag="$1"
  log "========== VARIANT: $tag =========="
  "$SCRIPT_DIR/sync_to_nuc.sh" --local >>"$MASTER_LOG" 2>&1
  log "NUC sim base=$SIM_BASE bonus=$SIM_BONUS scale=$PAYTABLE_SCALE"
  nuc_ssh "cd $(nuc_repo_path) && powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_clash_kronos_sims.ps1 -SimBase $SIM_BASE -SimBonus $SIM_BONUS -PaytableScale $PAYTABLE_SCALE" \
    >>"$MASTER_LOG" 2>&1
  "$SCRIPT_DIR/pull_library_from_nuc.sh" >>"$MASTER_LOG" 2>&1
  log "Local optimization"
  export PYTHONPATH="$REPO_ROOT:$GAME_DIR"
  (cd "$GAME_DIR" && RUN_SIMS=0 RUN_OPTIMIZATION=1 SIM_BASE=0 SIM_BONUS=0 PAYTABLE_SCALE="$PAYTABLE_SCALE" python3 run.py) \
    >>"$MASTER_LOG" 2>&1
  rtp_report "$tag"
  save_snapshot "$tag"
}

# Backup current tuning artifacts
cp "$GAME_DIR/reels/BR0.csv" "$LOG_DIR/BR0_before_${STAMP}.csv"
cp "$GAME_DIR/game_config.py" "$LOG_DIR/game_config_before_${STAMP}.py"

cd "$REPO_ROOT"

# --- Variant A: stock BR0 (no cluster boost) ---
log "Variant A: restore git BR0"
git checkout HEAD -- games/0_0_clash_kronos/reels/BR0.csv
run_variant "A_git_br0"

# --- Variant B: mild cluster BR0 ---
log "Variant B: mild BR0 (extend 0.06, half promote)"
python3 << 'PY'
from pathlib import Path
p = Path("games/0_0_clash_kronos/build_br0_clusters.py")
text = p.read_text()
text = text.replace("RUN_EXTEND_PROB = 0.14", "RUN_EXTEND_PROB = 0.06")
text = text.replace(
    'PROMOTE = (\n    ("L3", "L2", 0.06),\n    ("L2", "L1", 0.05),\n    ("L1", "H3", 0.04),\n    ("H3", "H2", 0.03),\n    ("H2", "H1", 0.02),\n)',
    'PROMOTE = (\n    ("L3", "L2", 0.03),\n    ("L2", "L1", 0.025),\n    ("L1", "H3", 0.02),\n    ("H3", "H2", 0.015),\n    ("H2", "H1", 0.01),\n)',
)
p.write_text(text)
PY
(cd "$GAME_DIR" && python3 build_br0_clusters.py) >>"$MASTER_LOG" 2>&1
run_variant "B_mild_br0"

# --- Variant C: git BR0 + lower forced-FS quota (8% not 15%) ---
log "Variant C: git BR0 + freegame quota 8%"
git checkout HEAD -- games/0_0_clash_kronos/reels/BR0.csv
python3 << 'PY'
from pathlib import Path
p = Path("games/0_0_clash_kronos/game_config.py")
t = p.read_text()
t = t.replace('quota=0.15,\n                        conditions={\n                            "reel_weights": {\n                                self.basegame_type: {"BR0": 1},\n                                self.freegame_type: {"FR0": 1},', 'quota=0.08,\n                        conditions={\n                            "reel_weights": {\n                                self.basegame_type: {"BR0": 1},\n                                self.freegame_type: {"FR0": 1},')
t = t.replace("quota=0.749,", "quota=0.819,")
p.write_text(t)
PY
run_variant "C_git_br0_low_fs_quota"

# Restore repo files to pre-overnight state (snapshots kept)
log "Restoring BR0 and game_config from backup"
cp "$LOG_DIR/BR0_before_${STAMP}.csv" "$GAME_DIR/reels/BR0.csv"
cp "$LOG_DIR/game_config_before_${STAMP}.py" "$GAME_DIR/game_config.py"
git checkout HEAD -- games/0_0_clash_kronos/build_br0_clusters.py 2>/dev/null || true

log "Overnight complete. See $LOG_DIR/run_${STAMP}.log and *_rtp.txt"
