#!/usr/bin/env bash
# Sort tuning log for picking a base-game winner.
#
#   ./scripts/summarize_tuning_log.sh
#   ./scripts/summarize_tuning_log.sh games/0_0_clash_kronos/library/sweep_base_tuning_log.csv
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG="${1:-$REPO_ROOT/games/0_0_clash_kronos/library/sweep_base_tuning_log.csv}"

if [[ ! -f "$LOG" ]]; then
  LOG="$REPO_ROOT/games/0_0_clash_kronos/library/tuning_log.csv"
fi

if [[ ! -f "$LOG" ]]; then
  echo "No tuning log found." >&2
  exit 1
fi

PY="$REPO_ROOT/env/bin/python"
if [[ ! -x "$PY" ]]; then
  PY=python3
fi

"$PY" - "$LOG" << 'PY'
import csv
import sys

path = sys.argv[1]
with open(path, newline="") as f:
    rows = list(csv.DictReader(f))

if not rows:
    print("Empty log.")
    sys.exit(0)

def fnum(row, key, default=999.0):
    try:
        return float(row.get(key) or default)
    except ValueError:
        return default

# Publish ~0.965; prefer low raw_base and low zero_wt.
ok = [r for r in rows if abs(fnum(r, "publish_base", 0) - 0.965) < 0.002]
pool = ok if ok else rows
pool.sort(key=lambda r: (fnum(r, "raw_base"), fnum(r, "zero_wt_base_pct")))

cols = [
    "tag", "kronos_wild", "kronos_bar", "br0_variant",
    "raw_base", "publish_base", "zero_wt_base_pct", "basegame_mean", "raw_bonus",
]
print(f"=== {path} ({len(rows)} rows, showing top {min(16, len(pool))} by raw_base) ===\n")
header = " | ".join(c for c in cols if any(c in r for r in pool))
print(header)
print("-" * len(header))
for r in pool[:16]:
    parts = []
    for c in cols:
        if c in r:
            v = r.get(c, "")
            if c in ("raw_base", "publish_base", "zero_wt_base_pct", "basegame_mean", "raw_bonus"):
                try:
                    v = f"{float(v):.4f}" if v else ""
                except ValueError:
                    pass
            parts.append(f"{c}={v}")
    print(" | ".join(parts))
PY
