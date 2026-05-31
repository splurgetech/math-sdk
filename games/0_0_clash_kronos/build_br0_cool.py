#!/usr/bin/env python3
"""Rebuild BR0.csv for milder base spins (shorter runs, light premium demote).

Inverse of half-strength build_br0_clusters.py. Start from git stock BR0.

    python build_br0_cool.py
"""

from __future__ import annotations

import csv
import os
import random
import subprocess
from pathlib import Path

REELS_DIR = Path(__file__).resolve().parent / "reels"
BR0_PATH = REELS_DIR / "BR0.csv"
REPO_ROOT = Path(__file__).resolve().parents[2]

_STRONG = os.environ.get("BR0_COOL_STRONG", "").strip() in ("1", "true", "yes")
RUN_EXTEND_PROB = 0.04 if _STRONG else 0.07
# Demote premiums (reverse of cluster builder promote, ~half rates).
_DEMOTE_BASE = (
    ("H1", "H2", 0.01),
    ("H2", "H3", 0.015),
    ("H3", "L1", 0.02),
    ("L1", "L2", 0.025),
    ("L2", "L3", 0.03),
    ("L3", "L4", 0.03),
)
DEMOTE = (
    tuple((a, b, p * 2.0 if _STRONG else p) for a, b, p in _DEMOTE_BASE)
    if _STRONG
    else _DEMOTE_BASE
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


def demote_column(symbols: list[str], rng: random.Random) -> list[str]:
    out = []
    for sym in symbols:
        if sym == "S":
            out.append(sym)
            continue
        replaced = sym
        for src, dst, prob in DEMOTE:
            if sym == src and rng.random() < prob:
                replaced = dst
                break
        out.append(replaced)
    return out


def transform_rows(rows: list[list[str]], seed: int = 44) -> list[list[str]]:
    nrows = len(rows)
    ncols = max(len(r) for r in rows)
    rng = random.Random(seed)

    columns = [[rows[r][c].strip() for r in range(nrows)] for c in range(ncols)]
    columns = [demote_column(extend_column(col, rng), rng) for col in columns]

    return [[columns[c][r] for c in range(ncols)] for r in range(nrows)]


def main() -> None:
    try:
        rows = load_git_br0()
    except subprocess.CalledProcessError:
        rows = read_csv(BR0_PATH)

    out = transform_rows(rows)
    write_csv(BR0_PATH, out)
    mode = "strong cool" if _STRONG else "mild cool"
    print(f"Wrote {BR0_PATH} ({len(out)} rows, {mode} base strips)")


if __name__ == "__main__":
    main()
