"""Pure functions for the Kronos bar state machine and strike."""

import random


def count_exploded_symbols(win_data: dict) -> int:
    """Count total cells exploded across all wins in this tumble step."""
    total = 0
    for win in win_data.get("wins", []):
        total += len(win["positions"])
    return total


def apply_strike(grid: list, num_reels: int, num_rows: list) -> list:
    """Choose 3-6 random cells (with replacement) and apply strike effects.

    Returns list of hit dicts: [{reel, row}, ...] in order.
    Effect per hit:
      - cell has no overlay (0) -> set to 2
      - cell has overlay -> double it (cap at 128)
    """
    hit_count = random.randint(3, 6)
    hits = []
    for _ in range(hit_count):
        reel = random.randint(0, num_reels - 1)
        row = random.randint(0, num_rows[reel] - 1)
        hits.append({"reel": reel, "row": row})
        current = grid[reel][row]
        if current == 0:
            grid[reel][row] = 2
        else:
            grid[reel][row] = min(current * 2, 128)
    return hits


class KronosBarState:
    """Mutable bar state for one spin sequence (base or FS spin)."""

    def __init__(self, threshold: int = 20):
        self.threshold = threshold
        self.progress = 0

    def add_symbols(self, count: int) -> bool:
        """Add exploded symbol count. Returns True if bar just reached threshold."""
        if self.progress >= self.threshold:
            # Already triggered this step; don't accumulate further until reset
            return False
        self.progress = min(self.progress + count, self.threshold)
        return self.progress >= self.threshold

    def reset(self):
        self.progress = 0
