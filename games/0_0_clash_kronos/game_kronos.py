"""Kronos bar and symbol transform."""

import random

from game_constants import (
    KRONOS_BAR_THRESHOLD,
    KRONOS_WILD_PROBABILITY,
    PAYING_SYMBOLS,
    SYMBOL_WILD,
)
from game_events import kronos_bar_event, kronos_transform_event


class KronosBarState:
    def __init__(self, threshold: int = KRONOS_BAR_THRESHOLD):
        self.threshold = threshold
        self.progress = 0

    def add_organic_wins(self, cell_count: int) -> bool:
        if cell_count <= 0:
            return False
        self.progress = min(self.progress + cell_count, self.threshold)
        return self.progress >= self.threshold

    def reset(self) -> None:
        self.progress = 0


def count_exploded_cells(win_data: dict) -> int:
    total = 0
    for win in win_data.get("wins", []):
        total += len(win["positions"])
    return total


def pick_transform_symbols(board, paying_symbols: tuple = PAYING_SYMBOLS) -> tuple[str, str]:
    """Pick source paying symbol on board and target (other pay symbol or WD)."""
    on_board = set()
    for reel in board:
        for sym in reel:
            if sym.name in paying_symbols:
                on_board.add(sym.name)
    if not on_board:
        on_board = set(paying_symbols)
    from_sym = random.choice(list(on_board))
    if random.random() < KRONOS_WILD_PROBABILITY:
        return from_sym, SYMBOL_WILD
    others = [s for s in paying_symbols if s != from_sym]
    return from_sym, random.choice(others)


def apply_symbol_transform(board, symbol_storage, from_sym: str, to_sym: str) -> list[dict]:
    """Replace all visible instances of from_sym; return changed positions."""
    positions = []
    new_sym = symbol_storage.create_symbol(to_sym)
    for reel, column in enumerate(board):
        for row, sym in enumerate(column):
            if sym.name == from_sym:
                board[reel][row] = new_sym
                positions.append({"reel": reel, "row": row})
    return positions
