"""Book event emitters for Clash Kronos Cluster."""

from copy import deepcopy

UPDATE_GRID = "updateGrid"
KRONOS_BAR = "kronosBar"
KRONOS_STRIKE = "kronosStrike"


def update_grid_mult_event(gamestate):
    """Emit current position-multiplier grid snapshot."""
    event = {
        "index": len(gamestate.book.events),
        "type": UPDATE_GRID,
        "gridMultipliers": deepcopy(gamestate.position_multipliers),
    }
    gamestate.book.add_event(event)


def kronos_bar_event(gamestate, progress: int, filled: bool):
    """Emit kronosBar progress update."""
    event = {
        "index": len(gamestate.book.events),
        "type": KRONOS_BAR,
        "progress": progress,
        "filled": filled,
    }
    gamestate.book.add_event(event)


def kronos_strike_event(gamestate, hits: list):
    """Emit kronosStrike with ordered list of {reel, row} hits."""
    event = {
        "index": len(gamestate.book.events),
        "type": KRONOS_STRIKE,
        "hits": hits,
    }
    gamestate.book.add_event(event)
