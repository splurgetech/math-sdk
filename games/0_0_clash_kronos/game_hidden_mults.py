"""Hidden cell multiplier assignment and collection."""

import random

from game_constants import (
    HIDDEN_MULT_COVERAGE_MAX,
    HIDDEN_MULT_COVERAGE_MIN,
    HIDDEN_MULT_VALUE_WEIGHTS,
    VISIBLE_CELL_COUNT,
)
from src.calculations.statistics import get_random_outcome


def _weighted_hidden_value() -> int:
    return int(get_random_outcome(HIDDEN_MULT_VALUE_WEIGHTS))


def assign_hidden_mults(num_reels: int, num_rows: list) -> list[list[int]]:
    """Return per-cell hidden mult values (0 = none)."""
    coverage = random.uniform(HIDDEN_MULT_COVERAGE_MIN, HIDDEN_MULT_COVERAGE_MAX)
    target = max(0, min(VISIBLE_CELL_COUNT, int(VISIBLE_CELL_COUNT * coverage)))
    all_cells = [(r, row) for r in range(num_reels) for row in range(num_rows[r])]
    random.shuffle(all_cells)
    grid = [[0 for _ in range(num_rows[r])] for r in range(num_reels)]
    for reel, row in all_cells[:target]:
        grid[reel][row] = _weighted_hidden_value()
    return grid


def collect_from_wins(
    hidden_grid: list[list[int]],
    win_data: dict,
) -> tuple[list[dict], int]:
    """Collect hidden mults from winning positions; clear those cells. Returns (collected, total_added)."""
    collected = []
    total_added = 0
    seen: set[tuple[int, int]] = set()
    for win in win_data.get("wins", []):
        for pos in win["positions"]:
            reel, row = pos["reel"], pos["row"]
            key = (reel, row)
            if key in seen:
                continue
            seen.add(key)
            value = hidden_grid[reel][row]
            if value <= 0:
                continue
            collected.append({"reel": reel, "row": row, "value": value})
            total_added += value
            hidden_grid[reel][row] = 0
    return collected, total_added
