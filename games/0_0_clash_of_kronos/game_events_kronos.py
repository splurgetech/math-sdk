"""Custom Storybook-aligned events for Clash of Kronos."""

from src.events.events import json_ready_sym, padded_client_board


def _emit(gamestate, event: dict) -> None:
    event["index"] = len(gamestate.book.events)
    gamestate.book.add_event(event)


def cascade_tracker_update_event(gamestate, *, stage: int, multiplier: int, chests_active: bool) -> None:
    _emit(
        gamestate,
        {
            "type": "cascadeTrackerUpdate",
            "stage": stage,
            "multiplier": multiplier,
            "gameType": gamestate.gametype,
            "chestsActive": chests_active,
        },
    )


def chest_unlock_event(gamestate, positions: list[dict]) -> None:
    _emit(gamestate, {"type": "chestUnlock", "positions": positions})


def chest_values_update_event(gamestate, updates: list[dict]) -> None:
    _emit(gamestate, {"type": "chestValuesUpdate", "updates": updates})


def lightning_strike_event(gamestate, strikes: list[dict]) -> None:
    _emit(gamestate, {"type": "lightningStrike", "strikes": strikes})


def surge_chests_event(gamestate, updates: list[dict]) -> None:
    _emit(gamestate, {"type": "surgeChests", "updates": updates})


def hammer_collect_event(gamestate, hammer_position: dict | None = None) -> None:
    payload: dict = {"type": "hammerCollect"}
    if hammer_position is not None:
        payload["position"] = hammer_position
    _emit(gamestate, payload)


def hammer_smash_event(gamestate, *, cleared_positions: list[dict]) -> None:
    specials = list(gamestate.config.special_symbols.keys())
    new_symbols = [[] for _ in range(gamestate.config.num_reels)]
    for r, _ in enumerate(gamestate.new_symbols_from_tumble):
        if len(gamestate.new_symbols_from_tumble[r]) > 0:
            new_symbols[r] = [json_ready_sym(s, specials) for s in gamestate.new_symbols_from_tumble[r]]
    board_client = padded_client_board(gamestate)
    _emit(
        gamestate,
        {
            "type": "hammerSmash",
            "clearedPositions": cleared_positions,
            "newSymbols": new_symbols,
            "resultBoard": board_client,
            "trackerStage": getattr(gamestate, "cascade_stage", 1),
            "trackerMultiplier": getattr(gamestate, "current_tracker_multiplier", 1),
        },
    )


def free_spin_retrigger_event(gamestate, added_fs: int) -> None:
    """Emit `freeSpinRetrigger` with spins **added this retrigger**, not cumulative `tot_fs`."""
    positions = []
    for r in range(gamestate.config.num_reels):
        for row in range(gamestate.config.num_rows[r]):
            if gamestate.board[r][row].check_attribute("scatter"):
                positions.append({"reel": r, "row": row + 1})
    _emit(
        gamestate,
        {
            "type": "freeSpinRetrigger",
            "totalFs": added_fs,
            "positions": positions,
        },
    )
