"""Clash of Kronos — tunable constants."""

import os

PAYING_SYMBOLS = ("H1", "H2", "H3", "L1", "L2", "L3", "L4")
SYMBOL_SCATTER = "S"
SYMBOL_WILD = "W"

# Empty env (e.g. sweep unsets KRONOS_*) must fall back to defaults — os.environ.get("X", "20") does not.
KRONOS_BAR_THRESHOLD = int(os.environ.get("KRONOS_BAR_THRESHOLD") or "20")
KRONOS_WILD_PROBABILITY = float(os.environ.get("KRONOS_WILD_PROB") or "0.25")

# Hidden mult coverage: uniform fraction of grid cells per spin (min 10% per design)
HIDDEN_MULT_COVERAGE_MIN = float(os.environ.get("HIDDEN_MULT_COVERAGE_MIN") or "0.10")
HIDDEN_MULT_COVERAGE_MAX = float(os.environ.get("HIDDEN_MULT_COVERAGE_MAX") or "0.55")
VISIBLE_CELL_COUNT = 36

# Value weights (sum = 100); tiers 1–5× common, 10× / 20× rare spikes only
_DEFAULT_HIDDEN_MULT_VALUE_WEIGHTS = {
    1: 45,
    2: 25,
    3: 12,
    4: 5,
    5: 2.5,
    10: 0.25,
    20: 0.15,
}


def hidden_mult_value_weights() -> dict:
    weights = dict(_DEFAULT_HIDDEN_MULT_VALUE_WEIGHTS)
    spike_mult = os.environ.get("HIDDEN_MULT_SPIKE_MULT")
    if spike_mult:
        m = float(spike_mult)
        weights[10] = weights[10] * m
        weights[20] = weights[20] * m
    return weights


HIDDEN_MULT_VALUE_WEIGHTS = hidden_mult_value_weights()

MAX_SCATTERS_ON_BOARD = 5
MAX_FS_RETRIGGERS = 3

FREESPIN_TRIGGERS = {3: 8, 4: 10, 5: 12}

# Retrigger awards = 50% of initial (added spins per retrigger; max 3 retriggers per bonus)
FREESPIN_RETRIGGER_AWARDS = {3: 4, 4: 5, 5: 6}

# Forced FS / bonus-buy entry: ~89% ×3, ~10% ×4, ~1% ×5 (5S was 10% — too much RTP)
FS_ENTRY_SCATTER_WEIGHTS = {3: 89, 4: 10, 5: 1}
BONUS_BUY_SCATTER_WEIGHTS = FS_ENTRY_SCATTER_WEIGHTS
