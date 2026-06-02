#!/usr/bin/env python3
"""Inject L5 into reel strips by replacing ~15% of L3/L4 cells (board dilution)."""

from __future__ import annotations

import csv
import random
from pathlib import Path

REELS_DIR = Path(__file__).resolve().parent / "reels"
REEL_FILES = (
    "BR0.csv",
    "FR0.csv",
    "FR0_NS.csv",
    "FR0_BUY.csv",
    "FR0_BUY_NS.csv",
    "WCAP.csv",
)
REPLACE_SOURCES = ("L4", "L3")
REPLACE_PROB = 0.15
SEED = 42


def read_csv(path: Path) -> list[list[str]]:
    with path.open(newline="") as f:
        return [row for row in csv.reader(f) if row]


def write_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", newline="") as f:
        csv.writer(f).writerows(rows)


def dilute(rows: list[list[str]], rng: random.Random) -> list[list[str]]:
    out: list[list[str]] = []
    for row in rows:
        new_row = []
        for cell in row:
            sym = cell.strip()
            if sym in REPLACE_SOURCES and rng.random() < REPLACE_PROB:
                new_row.append("L5")
            else:
                new_row.append(sym)
        out.append(new_row)
    return out


def main() -> None:
    rng = random.Random(SEED)
    for name in REEL_FILES:
        path = REELS_DIR / name
        if not path.is_file():
            print(f"skip missing {name}")
            continue
        rows = read_csv(path)
        write_csv(path, dilute(rows, rng))
        print(f"updated {name}")


if __name__ == "__main__":
    main()
