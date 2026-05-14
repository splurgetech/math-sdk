"""Book event emitters for Clash Kronos Cluster."""

from copy import deepcopy

from src.events.events import json_ready_sym

UPDATE_GRID = "updateGrid"
KRONOS_BAR = "kronosBar"
KRONOS_STRIKE = "kronosStrike"


def _padded_client_board(gamestate):
    """Same shape as reveal ``board`` (padding rows when enabled)."""
    special_attributes = list(gamestate.config.special_symbols.keys())
    board_client = []
    for reel, _ in enumerate(gamestate.board):
        board_client.append([])
        for row in range(len(gamestate.board[reel])):
            board_client[reel].append(json_ready_sym(gamestate.board[reel][row], special_attributes))
    if gamestate.config.include_padding:
        for reel, _ in enumerate(board_client):
            board_client[reel] = [json_ready_sym(gamestate.top_symbols[reel], special_attributes)] + board_client[
                reel
            ]
            board_client[reel].append(json_ready_sym(gamestate.bottom_symbols[reel], special_attributes))
    return board_client


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
    """Emit kronosStrike with ordered hits and padded client board after wilds."""
    event = {
        "index": len(gamestate.book.events),
        "type": KRONOS_STRIKE,
        "hits": hits,
        "board": _padded_client_board(gamestate),
    }
    gamestate.book.add_event(event)
