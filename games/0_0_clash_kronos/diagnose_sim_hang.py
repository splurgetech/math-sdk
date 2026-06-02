#!/usr/bin/env python3
"""Detect pathological sims: repeat counts and wall time per criteria."""

import os
import sys
import time

_GAME_DIR = os.path.dirname(os.path.abspath(__file__))
_SDK_ROOT = os.path.abspath(os.path.join(_GAME_DIR, "..", ".."))
for p in [_SDK_ROOT, _GAME_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("ALLOW_MAC_SIMS", "1")
os.environ.setdefault("PAYTABLE_SCALE", "0.8")
os.environ.setdefault("KRONOS_WILD_PROB", "0.10")
os.environ.setdefault("KRONOS_BAR_THRESHOLD", "25")

from game_config import GameConfig
from gamestate import GameState
from src.wins.win_manager import WinManager

MAX_REPEAT = 100_000
CRITERIA = ("0", "basegame", "freegame", "wincap")


def run_one(criteria: str, sim: int = 0) -> dict:
    config = GameConfig()
    gs = GameState(config)
    mode_wincap = next(bm._wincap for bm in config.bet_modes if bm._name == "base")
    gs.win_manager = WinManager(config.basegame_type, config.freegame_type, mode_wincap)
    gs.betmode = "base"
    gs.criteria = criteria

    t0 = time.perf_counter()
    gs.reset_seed(sim)
    gs.repeat = True
    repeats = 0
    while gs.repeat:
        repeats += 1
        if repeats > MAX_REPEAT:
            raise RuntimeError(f"{criteria} sim={sim}: repeat cap {MAX_REPEAT}")
        gs.reset_book()
        gs.draw_board()
        gs.run_spin_phases()
        gs.set_end_tumble_event()
        gs.win_manager.update_gametype_wins(gs.gametype)
        if gs.check_fs_condition() and gs.check_freespin_entry():
            gs.run_freespin_from_base()
        gs.evaluate_finalwin()
        gs.check_repeat()

    elapsed = time.perf_counter() - t0
    return {
        "criteria": criteria,
        "repeats": repeats,
        "seconds": round(elapsed, 3),
        "final_win": gs.final_win,
        "triggered_fg": gs.triggered_freegame,
    }


def main() -> None:
    print("Diagnosing base criteria (single accepted book each)...")
    for c in CRITERIA:
        try:
            r = run_one(c)
            print(f"  OK {r}")
        except Exception as e:
            print(f"  FAIL {c}: {e}")
    print("Done.")


if __name__ == "__main__":
    main()
