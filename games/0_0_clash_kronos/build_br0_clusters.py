#!/usr/bin/env python3
"""Rebuild BR0.csv for cluster-friendlier base spins (longer symbol runs, mild premium lift).

Base-only reel: bonus buy FS uses FR0_BUY; organic FS uses FR0. Entry spin on buy still
uses BR0 but most buy value is in FR0_BUY. Regenerate with:

    python build_br0_clusters.py
"""

from __future__ import annotations

import csv
import random
import subprocess
from pathlib import Path

REELS_DIR = Path(__file__).resolve().parent / "reels"
BR0_PATH = REELS_DIR / "BR0.csv"
REPO_ROOT = Path(__file__).resolve().parents[2]

# Longer runs = more adjacent same symbols on a reel → larger clusters when strips align.
# Keep modest — large values blow up base RTP (same pays as bonus).
RUN_EXTEND_PROB = 0.14
# Light premium lift on non-scatter cells (same paytable as bonus).
PROMOTE = (
    ("L3", "L2", 0.06),
    ("L2", "L1", 0.05),
    ("L1", "H3", 0.04),
    ("H3", "H2", 0.03),
    ("H2", "H1", 0.02),
)


def load_git_br0() -> list[list[str]]:
    raw = subprocess.check_output(
        ["git", "show", "HEAD:games/0_0_clash_kronos/reels/BR0.csv"],
        cwd=REPO_ROOT,
        text=True,
    )
    return [row for row in csv.reader(raw.splitlines()) if row]


def read_csv(path: Path) -> list[list[str]]:
    with path.open(newline="") as f:
        return [row for row in csv.reader(f) if row]


def write_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", newline="") as f:
        csv.writer(f).writerows(rows)


def extend_column(symbols: list[str], rng: random.Random) -> list[str]:
    if not symbols:
        return symbols
    out = [symbols[0].strip()]
    for sym in symbols[1:]:
        sym = sym.strip()
        if sym == "S":
            out.append(sym)
            continue
        if out[-1] != "S" and rng.random() < RUN_EXTEND_PROB:
            out.append(out[-1])
        else:
            out.append(sym)
    return out


def promote_column(symbols: list[str], rng: random.Random) -> list[str]:
    out = []
    for sym in symbols:
        if sym == "S":
            out.append(sym)
            continue
        replaced = sym
        for src, dst, prob in PROMOTE:
            if sym == src and rng.random() < prob:
                replaced = dst
                break
        out.append(replaced)
    return out


def transform_rows(rows: list[list[str]], seed: int = 43) -> list[list[str]]:
    nrows = len(rows)
    ncols = max(len(r) for r in rows)
    rng = random.Random(seed)

    columns = [[rows[r][c].strip() for r in range(nrows)] for c in range(ncols)]
    columns = [promote_column(extend_column(col, rng), rng) for col in columns]

    return [[columns[c][r] for c in range(ncols)] for r in range(nrows)]


def main() -> None:
    try:
        rows = load_git_br0()
    except subprocess.CalledProcessError:
        rows = read_csv(BR0_PATH)

    out = transform_rows(rows)
    write_csv(BR0_PATH, out)
    print(f"Wrote {BR0_PATH} ({len(out)} rows, cluster-friendly base strips)")


if __name__ == "__main__":
    main()
