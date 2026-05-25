"""Generate small book sets for Storybook fixture export."""
import json
import os
import random
import sys
import time

_GAME_DIR = os.path.dirname(os.path.abspath(__file__))
_SDK_ROOT = os.path.abspath(os.path.join(_GAME_DIR, "..", ".."))
for p in [_SDK_ROOT, _GAME_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from game_config import GameConfig
from gamestate import GameState
from src.wins.win_manager import WinManager

BASE_CRITERIA = [
    ("0", int(os.environ.get("FIXTURE_BASE_ZERO", "80"))),
    ("basegame", int(os.environ.get("FIXTURE_BASE_WIN", "120"))),
]
BONUS_SIMS = int(os.environ.get("FIXTURE_BONUS_SIMS", "40"))


def run_criteria(gamestate, config, betmode_name: str, criteria: str, num_sims: int) -> list:
    mode_wincap = next(bm._wincap for bm in config.bet_modes if bm._name == betmode_name)
    gamestate.win_manager = WinManager(config.basegame_type, config.freegame_type, mode_wincap)
    gamestate.library = {}
    gamestate.recorded_events = {}
    gamestate.betmode = betmode_name
    for sim_idx in range(num_sims):
        gamestate.criteria = criteria
        gamestate.run_spin(sim_idx, sim_idx + 1)
    return list(gamestate.library.values())


def write_books(books: list, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2)
    print(f"Wrote {len(books)} books -> {path}")


if __name__ == "__main__":
    GameConfig._instance = None
    config = GameConfig()
    gamestate = GameState(config)
    books_dir = os.path.join(_GAME_DIR, "library", "books")
    os.makedirs(books_dir, exist_ok=True)

    all_base = []
    for criteria, count in BASE_CRITERIA:
        print(f"base/{criteria} x{count}")
        all_base.extend(run_criteria(gamestate, config, "base", criteria, count))
    random.shuffle(all_base)
    write_books(all_base, os.path.join(books_dir, "books_base.json"))

    if BONUS_SIMS > 0:
        print(f"bonus/freegame x{BONUS_SIMS}")
        bonus = run_criteria(gamestate, config, "bonus", "freegame", BONUS_SIMS)
        random.shuffle(bonus)
        write_books(bonus, os.path.join(books_dir, "books_bonus.json"))
    else:
        write_books([], os.path.join(books_dir, "books_bonus.json"))
