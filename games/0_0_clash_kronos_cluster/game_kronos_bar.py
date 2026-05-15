"""Pure functions for the Kronos bar state machine and bolt wild strike."""

import random


def count_exploded_symbols(win_data: dict) -> int:
    """Count total cells exploded across all wins in this tumble step."""
    total = 0
    for win in win_data.get("wins", []):
        total += len(win["positions"])
    return total


def apply_kronos_bolts(board, symbol_storage, num_reels: int, num_rows: list) -> list:
    """Replace every visible cell of one random paying symbol with ``W``.

    The victim symbol is chosen uniformly from **names that appear on the board**
    at least once (excluding scatter and existing wilds). Scatter is never replaced.

    If no eligible symbol exists (e.g. only scatters), returns ``hits=[]``; the strike
    event is still emitted so the client can run bolt VFX.

    ``hits`` lists ``{reel, row}`` in reel-major, top-to-bottom order (same order as replacements).
    """
    names_present = set()
    for reel in range(num_reels):
        for row in range(num_rows[reel]):
            cell = board[reel][row]
            if cell.check_attribute("scatter"):
                continue
            if cell.name == "W":
                continue
            names_present.add(cell.name)

    if not names_present:
        return []

    victim = random.choice(list(names_present))
    hits = []
    for reel in range(num_reels):
        for row in range(num_rows[reel]):
            if board[reel][row].name == victim:
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
