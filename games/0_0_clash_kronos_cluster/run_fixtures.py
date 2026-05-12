"""
Generate small simulation books for Storybook fixture export.
Keeps simulation count well below 500k; safe for a laptop.

Bypasses multiprocessing entirely — runs all sims in a single process.
Skips the "freegame" distribution (force_freegame=True) because retrying until
scatter-trigger + non-zero win lands takes too long on a laptop.
Free-spin sequences are covered by golden_base_book.ts in Storybook.

Usage (from this directory):
    python run_fixtures.py

Outputs:
    library/books/books_base.json   — 300 base-game books (no-win + winning)
"""
import sys
import os
import json
import random
import time

# Ensure math-sdk root and game dir are importable
_GAME_DIR = os.path.dirname(os.path.abspath(__file__))
_SDK_ROOT = os.path.abspath(os.path.join(_GAME_DIR, "..", ".."))
for p in [_SDK_ROOT, _GAME_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from game_config import GameConfig
from gamestate import GameState
from src.wins.win_manager import WinManager

# ── sim counts (keep total << 500k) ──────────────────────────────────────────
# We skip the "freegame" distribution to avoid slow retries.
# "0" = forced zero-win, "basegame" = any-win.
# 120 "0" + 180 "basegame" = 300 books total.
BASE_CRITERIA = [("0", 120), ("basegame", 180)]
# ─────────────────────────────────────────────────────────────────────────────


def run_criteria(gamestate, config, betmode_name: str, criteria: str, num_sims: int) -> list:
    """Run num_sims for one criteria value; return list of book dicts."""
    mode_wincap = next(bm._wincap for bm in config.bet_modes if bm._name == betmode_name)
    gamestate.win_manager = WinManager(config.basegame_type, config.freegame_type, mode_wincap)
    gamestate.library = {}
    gamestate.recorded_events = {}
    gamestate.betmode = betmode_name

    t0 = time.time()
    for sim_idx in range(num_sims):
        gamestate.criteria = criteria
        gamestate.run_spin(sim_idx, sim_idx + 1)

    books = list(gamestate.library.values())
    print(f"  criteria='{criteria}': {len(books)} books in {time.time()-t0:.1f}s")
    return books


def write_books_json(books: list, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2)
    print(f"  Written {len(books)} books → {path}")


if __name__ == "__main__":
    GameConfig._instance = None
    config = GameConfig()
    gamestate = GameState(config)

    books_dir = os.path.join(_GAME_DIR, "library", "books")
    os.makedirs(books_dir, exist_ok=True)

    print("\nRunning base-game sims (no freegame distribution)...")
    all_base_books = []
    for criteria, count in BASE_CRITERIA:
        books = run_criteria(gamestate, config, "base", criteria, count)
        all_base_books.extend(books)

    random.shuffle(all_base_books)
    write_books_json(all_base_books, os.path.join(books_dir, "books_base.json"))
    print("\nDone. Books written to:", books_dir)
