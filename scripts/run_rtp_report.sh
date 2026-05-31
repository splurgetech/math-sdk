#!/usr/bin/env bash
# Full RTP report: raw + publish + segmented criteria + publish zero-weight share.
#
# Usage (from math-sdk repo root):
#   ./scripts/run_rtp_report.sh
#   ./scripts/run_rtp_report.sh --csv-append library/tuning_log.csv --tag quota_fg08
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GAME_DIR="$REPO_ROOT/games/0_0_clash_kronos"
TAG="${TAG:-}"
APPEND_CSV=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --csv-append) APPEND_CSV="$2"; shift 2 ;;
    --tag) TAG="$2"; shift 2 ;;
    *) shift ;;
  esac
done

export PYTHONPATH="$REPO_ROOT:${PYTHONPATH:-}"

PY="$REPO_ROOT/env/bin/python"
if [[ ! -x "$PY" ]]; then
  PY=python3
fi

report_mode() {
  local mode="$1"
  local bet_cost="$2"
  local raw="$GAME_DIR/library/lookup_tables/lookUpTable_${mode}.csv"
  local pub="$GAME_DIR/library/publish_files/lookUpTable_${mode}_0.csv"
  local seg="$GAME_DIR/library/lookup_tables/lookUpTableSegmented_${mode}.csv"

  echo "=== mode: $mode (bet_cost=$bet_cost) ${TAG:+[tag=$TAG]} ==="
  if [[ ! -f "$raw" ]]; then
    echo "  MISSING raw: $raw"
    return 1
  fi
  "$PY" "$SCRIPT_DIR/rtp_from_lookup.py" "$raw" "$pub" "$bet_cost" 2>/dev/null || \
    "$PY" "$SCRIPT_DIR/rtp_from_lookup.py" "$raw" "$raw" "$bet_cost"

  if [[ -f "$seg" ]]; then
    "$PY" - "$seg" << 'PY'
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
        print(f"  segmented {c}: n={len(v)} mean={sum(v)/len(v):.4f}x")
if by:
    allv = [x for vs in by.values() for x in vs]
    print(f"  segmented ALL: mean={sum(allv)/len(allv):.4f}x")
PY
  fi

  if [[ -f "$pub" ]]; then
    "$PY" - "$pub" << 'PY'
import sys
from collections import defaultdict
path = sys.argv[1]
zero_w = 0.0
total_w = 0.0
with open(path) as f:
    for line in f:
        p = line.strip().split(",")
        if len(p) >= 3:
            w = float(p[1])
            pay = float(p[2]) / 100.0
            total_w += w
            if pay == 0.0:
                zero_w += w
if total_w > 0:
    print(f"  publish zero-weight share: {100.0 * zero_w / total_w:.2f}%")
PY
  else
    echo "  publish: (no lookUpTable_${mode}_0.csv yet)"
  fi
  echo ""
}

report_mode base 1.0
report_mode bonus 100.0

if [[ -n "$APPEND_CSV" ]]; then
  mkdir -p "$(dirname "$APPEND_CSV")"
  if [[ ! -f "$APPEND_CSV" ]]; then
    echo "timestamp,tag,dist_fg,dist_zero,kronos_wild,kronos_bar,br0_variant,raw_base,publish_base,raw_bonus,publish_bonus,zero_wt_base_pct,basegame_mean,fg_mean" >"$APPEND_CSV"
  fi
  OUT="$("$PY" - "$GAME_DIR" "$TAG" << 'PY'
import os, sys
from datetime import datetime, timezone
from collections import defaultdict

game_dir = sys.argv[1]
tag = sys.argv[2]

def mean_raw(mode):
    p = os.path.join(game_dir, "library/lookup_tables", f"lookUpTable_{mode}.csv")
    if not os.path.isfile(p):
        return ""
    t = n = 0
    with open(p) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 3:
                t += float(parts[2])
                n += 1
    return f"{t/n/100:.6f}" if n else ""

def publish_rtp(mode, cost):
    p = os.path.join(game_dir, "library/publish_files", f"lookUpTable_{mode}_0.csv")
    if not os.path.isfile(p):
        return ""
    dist = defaultdict(float)
    with open(p) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 3:
                dist[float(parts[2]) / 100.0] += float(parts[1])
    tw = sum(dist.values())
    if tw <= 0:
        return ""
    mean = sum(k * v for k, v in dist.items()) / tw
    return f"{mean / cost:.6f}"

def zero_share(mode):
    p = os.path.join(game_dir, "library/publish_files", f"lookUpTable_{mode}_0.csv")
    if not os.path.isfile(p):
        return ""
    zw = tw = 0.0
    with open(p) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 3:
                w = float(parts[1])
                pay = float(parts[2]) / 100.0
                tw += w
                if pay == 0:
                    zw += w
    return f"{100*zw/tw:.2f}" if tw else ""

def seg_mean(crit):
    p = os.path.join(game_dir, "library/lookup_tables", "lookUpTableSegmented_base.csv")
    if not os.path.isfile(p):
        return ""
    vals = []
    with open(p) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 4 and parts[1] == crit:
                vals.append(float(parts[2]) + float(parts[3]))
    return f"{sum(vals)/len(vals):.4f}" if vals else ""

fg = os.environ.get("DIST_FG_QUOTA", "")
z = os.environ.get("DIST_ZERO_QUOTA", "")
kw = os.environ.get("KRONOS_WILD_PROB", "")
kb = os.environ.get("KRONOS_BAR_THRESHOLD", "")
br0 = os.environ.get("BR0_VARIANT", "")
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
print(",".join([
    ts, tag, fg, z, kw, kb, br0,
    mean_raw("base"), publish_rtp("base", 1.0),
    mean_raw("bonus"), publish_rtp("bonus", 100.0),
    zero_share("base"), seg_mean("basegame"), seg_mean("freegame"),
]))
PY
)"
  echo "$OUT" >>"$APPEND_CSV"
  echo "Appended to $APPEND_CSV"
fi
