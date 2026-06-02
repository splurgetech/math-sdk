"""Paytable from design spec (bet multipliers)."""

import os

from game_constants import PAYING_SYMBOLS

# Tune via env; default 0.1× design spec for sim/Storybook-friendly wins (target RTP via reels/weights).
PAYTABLE_SCALE = float(os.environ.get("PAYTABLE_SCALE", "0.1"))

# Final pay caps (bet multipliers) — cluster-sample-aligned; applied after PAYTABLE_SCALE.
PAYTABLE_SYMBOL_CAPS = {
    "H1": float(os.environ.get("PAYTABLE_CAP_H1", "100")),
    "H2": float(os.environ.get("PAYTABLE_CAP_H2", "40")),
    "H3": float(os.environ.get("PAYTABLE_CAP_H3", "30")),
    "L1": float(os.environ.get("PAYTABLE_CAP_L1", "10")),
    "L2": float(os.environ.get("PAYTABLE_CAP_L2", "8")),
    "L3": float(os.environ.get("PAYTABLE_CAP_L3", "5")),
    "L4": float(os.environ.get("PAYTABLE_CAP_L4", "4")),
    "L5": float(os.environ.get("PAYTABLE_CAP_L5", "4")),
}


def _tier_pay_groups(values: tuple) -> list[tuple[tuple[int, int], float]]:
    sizes = [5, 6, 7, 8, 9, 10]
    groups = [((size, size), pay) for size, pay in zip(sizes, values[:-1])]
    groups.append(((11, 36), values[-1]))
    return groups


GEM = (0.10, 0.15, 0.30, 0.50, 0.80, 1.00, 1.50)
SCROLL = (0.50, 1.00, 2.00, 4.00, 6.00, 10.00, 15.00)
FAN = (1.00, 2.00, 4.00, 8.00, 15.00, 30.00, 50.00)
HELMET = (2.00, 4.00, 8.00, 15.00, 30.00, 60.00, 100.00)

SYMBOL_TIERS = {
    "L5": GEM,
    "L4": GEM,
    "L3": GEM,
    "L2": GEM,
    "L1": SCROLL,
    "H3": FAN,
    "H2": FAN,
    "H1": HELMET,
}


def build_paytable() -> dict:
    paytable = {}
    for sym in PAYING_SYMBOLS:
        for (rng, pay) in _tier_pay_groups(SYMBOL_TIERS[sym]):
            lo, hi = rng
            for size in range(lo, hi + 1):
                scaled = pay * PAYTABLE_SCALE
                cap = PAYTABLE_SYMBOL_CAPS.get(sym)
                if cap is not None:
                    scaled = min(scaled, cap)
                paytable[(size, sym)] = round(scaled, 6)
    return paytable
