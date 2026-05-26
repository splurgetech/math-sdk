"""Clash of Kronos book events."""

from copy import deepcopy

from src.events.event_constants import EventConstants
from src.events.events import json_ready_sym, padded_client_board

COLLECT_HIDDEN_MULTS = "collectHiddenMults"
KRONOS_BAR = "kronosBar"
KRONOS_TRANSFORM = "kronosTransform"


def reveal_with_hidden_mults_event(gamestate):
    board_client = padded_client_board(gamestate)
    hidden = []
    for reel in range(gamestate.config.num_reels):
        for row in range(gamestate.config.num_rows[reel]):
            value = gamestate.hidden_mult_grid[reel][row]
            if value > 0:
                hidden.append({"reel": reel, "row": row + 1, "value": value})
    event = {
        "index": len(gamestate.book.events),
        "type": EventConstants.REVEAL.value,
        "board": board_client,
        "paddingPositions": gamestate.reel_positions,
        "gameType": gamestate.gametype,
        "anticipation": gamestate.anticipation,
        "hiddenMults": hidden,
    }
    gamestate.book.add_event(event)


def collect_hidden_mults_event(gamestate, collected: list, global_mult: int) -> None:
    if not collected:
        return
    gamestate.book.add_event(
        {
            "index": len(gamestate.book.events),
            "type": COLLECT_HIDDEN_MULTS,
            "collected": collected,
            "globalMult": global_mult,
        }
    )


def update_global_mult_event(gamestate) -> None:
    gamestate.book.add_event(
        {
            "index": len(gamestate.book.events),
            "type": "updateGlobalMult",
            "globalMult": int(gamestate.global_multiplier),
        }
    )


def kronos_bar_event(gamestate, progress: int, filled: bool = False) -> None:
    gamestate.book.add_event(
        {
            "index": len(gamestate.book.events),
            "type": KRONOS_BAR,
            "progress": progress,
            "threshold": gamestate.kronos_bar.threshold,
            "filled": filled,
        }
    )


def kronos_transform_event(gamestate, from_symbol: str, to_symbol: str, positions: list) -> None:
    board_client = padded_client_board(gamestate)
    client_positions = [{"reel": p["reel"], "row": p["row"] + 1} for p in positions]
    gamestate.book.add_event(
        {
            "index": len(gamestate.book.events),
            "type": KRONOS_TRANSFORM,
            "fromSymbol": from_symbol,
            "toSymbol": to_symbol,
            "positions": client_positions,
            "board": board_client,
        }
    )
