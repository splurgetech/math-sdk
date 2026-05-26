"""Clash of Kronos — tunable constants."""

PAYING_SYMBOLS = ("H1", "H2", "H3", "L1", "L2", "L3", "L4")
SYMBOL_SCATTER = "S"
SYMBOL_WILD = "W"

KRONOS_BAR_THRESHOLD = 20
KRONOS_WILD_PROBABILITY = 0.25

# Hidden mult coverage: uniform fraction of grid cells per spin (max half the grid)
HIDDEN_MULT_COVERAGE_MIN = 0.10
HIDDEN_MULT_COVERAGE_MAX = 0.50
VISIBLE_CELL_COUNT = 36

# Value weights (sum = 100); biased to 1×–3×
HIDDEN_MULT_VALUE_WEIGHTS = {
    1: 50,
    2: 28,
    3: 15,
    4: 4,
    5: 1.5,
    6: 0.8,
    7: 0.4,
    8: 0.2,
    9: 0.05,
    10: 0.05,
}

MAX_SCATTERS_ON_BOARD = 5
MAX_FS_RETRIGGERS = 3

FREESPIN_TRIGGERS = {3: 8, 4: 10, 5: 12}

# Forced FS / bonus-buy entry: ~89% ×3, ~10% ×4, ~1% ×5 (5S was 10% — too much RTP)
FS_ENTRY_SCATTER_WEIGHTS = {3: 89, 4: 10, 5: 1}
BONUS_BUY_SCATTER_WEIGHTS = FS_ENTRY_SCATTER_WEIGHTS
