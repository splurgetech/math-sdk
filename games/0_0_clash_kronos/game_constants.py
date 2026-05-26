"""Clash of Kronos — tunable constants."""

PAYING_SYMBOLS = ("H1", "H2", "H3", "L1", "L2", "L3", "L4")
SYMBOL_SCATTER = "S"
SYMBOL_WILD = "W"

KRONOS_BAR_THRESHOLD = 20
KRONOS_WILD_PROBABILITY = 0.25

# Hidden mult coverage: uniform fraction of grid cells per spin (min 10% per design)
HIDDEN_MULT_COVERAGE_MIN = 0.10
HIDDEN_MULT_COVERAGE_MAX = 0.50
VISIBLE_CELL_COUNT = 36

# Value weights (sum = 100); tiers 1–5× common, 10× / 20× rare spikes only
HIDDEN_MULT_VALUE_WEIGHTS = {
    1: 45,
    2: 25,
    3: 12,
    4: 5,
    5: 2.5,
    10: 0.25,
    20: 0.15,
}

MAX_SCATTERS_ON_BOARD = 5
MAX_FS_RETRIGGERS = 3

FREESPIN_TRIGGERS = {3: 8, 4: 10, 5: 12}

# Forced FS / bonus-buy entry: ~89% ×3, ~10% ×4, ~1% ×5 (5S was 10% — too much RTP)
FS_ENTRY_SCATTER_WEIGHTS = {3: 89, 4: 10, 5: 1}
BONUS_BUY_SCATTER_WEIGHTS = FS_ENTRY_SCATTER_WEIGHTS
