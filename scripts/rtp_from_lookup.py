#!/usr/bin/env python3
"""Print unweighted and weighted RTP from Clash Kronos lookup CSVs.

Unweighted: mean(payoutMultiplier) / 100  (same as mean final_win for cost 1×).

Weighted: distribution from lookUpTable_*_0.csv (weight column), mean return / bet cost.

Usage:
  python scripts/rtp_from_lookup.py \\
    games/0_0_clash_kronos/library/lookup_tables/lookUpTable_base.csv \\
    games/0_0_clash_kronos/library/publish_files/lookUpTable_base_0.csv 1.0

  python scripts/rtp_from_lookup.py \\
    .../lookUpTable_bonus.csv .../lookUpTable_bonus_0.csv 100.0
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.analysis.distribution_functions import get_distribution_average, make_win_distribution


def unweighted_mean_return(csv_path: str) -> tuple[float, int]:
    total = 0.0
    n = 0
    with open(csv_path, encoding="UTF-8") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 3:
                total += float(parts[2])
                n += 1
    if n == 0:
        return 0.0, 0
    return total / n / 100.0, n


def weighted_rtp_fraction(weighted_csv: str, bet_cost: float) -> float:
    dist = make_win_distribution(weighted_csv, normalize=True)
    mean_return = float(get_distribution_average(dist))
    return mean_return / bet_cost


def main() -> None:
    p = argparse.ArgumentParser(description="RTP from lookup tables")
    p.add_argument(
        "unweighted_csv",
        nargs="?",
        default="games/0_0_clash_kronos/library/lookup_tables/lookUpTable_base.csv",
        help="Raw lookup (weight column usually 1)",
    )
    p.add_argument(
        "weighted_csv",
        nargs="?",
        default="games/0_0_clash_kronos/library/publish_files/lookUpTable_base_0.csv",
        help="Optimized weighted lookup (*_0.csv)",
    )
    p.add_argument(
        "bet_cost",
        nargs="?",
        type=float,
        default=1.0,
        help="Bet mode cost (1.0 base, 100.0 bonus buy)",
    )
    args = p.parse_args()

    uw_path = os.path.abspath(args.unweighted_csv)
    w_path = os.path.abspath(args.weighted_csv)

    if not os.path.isfile(uw_path):
        print(f"Missing unweighted file: {uw_path}", file=sys.stderr)
        sys.exit(1)

    mean_uw, n = unweighted_mean_return(uw_path)
    print(f"Unweighted ({n} rows): mean return × bet = {mean_uw:.6f}  (~{mean_uw * 100:.2f}% if read as %)")

    if os.path.isfile(w_path):
        rtp_w = weighted_rtp_fraction(w_path, args.bet_cost)
        print(
            f"Weighted ({w_path}): RTP fraction = {rtp_w:.6f}  (~{rtp_w * 100:.2f}%)  (bet_cost={args.bet_cost})"
        )
    else:
        print(f"No weighted file yet: {w_path}  (run optimization to generate *_0.csv)")


if __name__ == "__main__":
    main()
