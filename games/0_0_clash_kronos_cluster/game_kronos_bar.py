"""Pure functions for the Kronos bar state machine and bolt wild strike."""

import random


def count_exploded_symbols(win_data: dict) -> int:
    """Count total cells exploded across all wins in this tumble step."""
    total = 0
    for win in win_data.get("wins", []):
        total += len(win["positions"])
    return total


def apply_kronos_bolts(board, symbol_storage, num_reels: int, num_rows: list) -> list:
    """Place 4–10 wilds on unique random visible cells. Mutates board in place.

    Scatter cells are never replaced so a buy-bonus / forced-FS board cannot lose
    its trigger scatters before ``check_freespin_entry`` runs.

    Each hit replaces the symbol at (reel, row) with a new ``W`` instance.

    Returns list of hit dicts ``[{reel, row}, ...]`` in strike order.
    """
    bolt_count = random.randint(4, 10)
    max_cells = sum(num_rows[r] for r in range(num_reels))
    n = min(bolt_count, max_cells)
    pairs = set()
    hits = []
    max_attempts = max(5000, n * 500)
    attempts = 0
    while len(pairs) < n and attempts < max_attempts:
        attempts += 1
        reel = random.randint(0, num_reels - 1)
        row = random.randint(0, num_rows[reel] - 1)
        key = (reel, row)
        if key in pairs:
            continue
        if board[reel][row].check_attribute("scatter"):
            continue
        pairs.add(key)
        hits.append({"reel": reel, "row": row})
        board[reel][row] = symbol_storage.create_symbol("W")
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
