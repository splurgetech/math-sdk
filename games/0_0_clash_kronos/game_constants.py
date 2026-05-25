"""Clash of Kronos — tunable constants."""

PAYING_SYMBOLS = ("A", "B", "C", "D", "E", "F", "G")
SYMBOL_SCATTER = "SC"
SYMBOL_WILD = "WD"

KRONOS_BAR_THRESHOLD = 20
KRONOS_WILD_PROBABILITY = 0.25

# Hidden mult coverage: uniform fraction of grid cells per spin
HIDDEN_MULT_COVERAGE_MIN = 0.20
HIDDEN_MULT_COVERAGE_MAX = 0.80
VISIBLE_CELL_COUNT = 49

# Value weights (sum = 100)
HIDDEN_MULT_VALUE_WEIGHTS = {
    1: 45,
    2: 25,
    3: 12,
    4: 7,
    5: 4,
    6: 3,
    7: 2,
    8: 1,
    9: 0.5,
    10: 0.5,
}

MAX_SCATTERS_ON_BOARD = 5
MAX_FS_RETRIGGERS = 3

FREESPIN_TRIGGERS = {3: 8, 4: 10, 5: 12}

# Bonus-buy entry scatter count weights
BONUS_BUY_SCATTER_WEIGHTS = {3: 70, 4: 20, 5: 10}
