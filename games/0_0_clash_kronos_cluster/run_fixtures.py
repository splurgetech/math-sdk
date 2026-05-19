"""
Generate small simulation books for Storybook fixture export.
Keeps simulation count well below 100k outer spins total; safe for a laptop.

Bypasses multiprocessing entirely — runs all sims in a single process.

Usage (from this directory):
    python run_fixtures.py

Outputs:
    library/books/books_base.json   — base-game books (no-win + winning; default 300)
    library/books/books_bonus.json  — FS books from **base** betmode + `freegame` criteria
        (forced scatter entry; same event shape as production FS). Slow: use env below.

Optional env overrides (slow laptop tuning): FIXTURE_BASE_ZERO, FIXTURE_BASE_WIN,
FIXTURE_BONUS_SIMS (see source for defaults). For free-spin diagnostics during bonus sims,
set ``KRONOS_FS_TRACE=1`` (prints ``fs`` / ``tot_fs`` / remaining each FS spin and after retriggers).

Research / tail fidelity (same as ``run.py``): ``KRONOS_UNCAPPED_FS=1`` sets ``max_total_freespins``
to **0** so features are not cut off by the default cap. Use with ``FIXTURE_SHORT_FS=0`` when you
need full scatter→spin counts in exported books.

**Bonus pool:** default `FIXTURE_BONUS_SIMS=0` skips the freegame-criteria phase (writes an
empty `books_bonus.json`) so this script always finishes quickly. Set
`FIXTURE_BONUS_SIMS` to a positive number when you can afford the wall time (often
hours for large N — each sim is a full base tumble + freegame). Use
`FIXTURE_SHORT_FS=1` (default) to cap scatter trigger spin counts for fixture export only
(not RTP). `FIXTURE_SHORT_FS=0` uses the full production trigger table.

Progress: set FIXTURE_LOG_EVERY=N to print every N completed sims during a criteria
block (default 5); use PYTHONUNBUFFERED=1 for live logs.

If the shell shows ``Killed: 9`` during the bonus phase, macOS often **SIGKILL**'d Python for
**memory pressure** (OOM). Close other apps, lower ``FIXTURE_BASE_*`` / run on a machine
with more free RAM, or keep ``FIXTURE_BONUS_SIMS=0`` until you can run bonus sims elsewhere.
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

# winInfo/setTotalWin store int cents (round(win * 100)). Production PAYTABLE_SCALE
# (default 0.0007) makes most cluster pays < $0.01 → Storybook shows $0.00.
# Fixture runs default to scale 1.0 unless PAYTABLE_SCALE is set explicitly.
if not os.environ.get("PAYTABLE_SCALE"):
    os.environ["PAYTABLE_SCALE"] = "1.0"

from game_config import GameConfig
from gamestate import GameState
from src.wins.win_manager import WinManager


def _apply_fixture_short_fs_cap(config: GameConfig) -> None:
    """Cap FS counts from scatter triggers so fixture runs finish (not for RTP books)."""
    if os.environ.get("FIXTURE_SHORT_FS", "1") == "0":
        return
    cap = _fixture_int("FIXTURE_FS_CAP", 2)
    for gt in [config.basegame_type, config.freegame_type]:
        trig = config.freespin_triggers[gt]
        for k in list(trig.keys()):
            trig[k] = min(int(trig[k]), cap)


def _fixture_int(env_name: str, default: int) -> int:
    raw = os.environ.get(env_name)
    if raw is None or raw == "":
        return default
    return int(raw)


# ── sim counts (keep total << 100k outer attempts) ────────────────────────────
# Base: "0" = forced zero-win, "basegame" = any-win.
BASE_CRITERIA = [
    ("0", _fixture_int("FIXTURE_BASE_ZERO", 120)),
    ("basegame", _fixture_int("FIXTURE_BASE_WIN", 180)),
]
# Bonus: base betmode + freegame criteria (forced scatter). Default 0 = skip (fast).
BONUS_FREEGAME_SIMS = _fixture_int("FIXTURE_BONUS_SIMS", 0)
FIXTURE_LOG_EVERY = _fixture_int("FIXTURE_LOG_EVERY", 5)
# ─────────────────────────────────────────────────────────────────────────────


def _log(msg: str) -> None:
    print(msg, flush=True)


def run_criteria(gamestate, config, betmode_name: str, criteria: str, num_sims: int) -> list:
    """Run num_sims for one criteria value; return list of book dicts."""
    mode_wincap = next(bm._wincap for bm in config.bet_modes if bm._name == betmode_name)
    gamestate.win_manager = WinManager(config.basegame_type, config.freegame_type, mode_wincap)
    gamestate.library = {}
    gamestate.recorded_events = {}
    gamestate.betmode = betmode_name

    t0 = time.time()
    log_every = max(1, FIXTURE_LOG_EVERY)
    for sim_idx in range(num_sims):
        gamestate.criteria = criteria
        gamestate.run_spin(sim_idx, sim_idx + 1)
        if (sim_idx + 1) % log_every == 0 or sim_idx + 1 == num_sims:
            _log(
                f"    ... {sim_idx + 1}/{num_sims} sims ({betmode_name}/{criteria}) "
                f"elapsed {time.time() - t0:.1f}s"
            )

    books = list(gamestate.library.values())
    elapsed = time.time() - t0
    _log(f"  criteria='{criteria}' betmode='{betmode_name}': {len(books)} books in {elapsed:.1f}s")
    if len(books) < num_sims:
        _log(
            f"  (note: expected {num_sims} imprinted books but got {len(books)} — "
            "library keys may dedupe; or repeats exhausted before imprint)"
        )
    return books


def write_books_json(books: list, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2)
    _log(f"  Written {len(books)} books → {path}")


if __name__ == "__main__":
    GameConfig._instance = None
    config = GameConfig()
    _apply_fixture_short_fs_cap(config)
    gamestate = GameState(config)

    books_dir = os.path.join(_GAME_DIR, "library", "books")
    os.makedirs(books_dir, exist_ok=True)

    _log("\nRunning base-game sims...")
    all_base_books = []
    for criteria, count in BASE_CRITERIA:
        books = run_criteria(gamestate, config, "base", criteria, count)
        all_base_books.extend(books)

    random.shuffle(all_base_books)
    write_books_json(all_base_books, os.path.join(books_dir, "books_base.json"))

    bonus_path = os.path.join(books_dir, "books_bonus.json")
    if BONUS_FREEGAME_SIMS <= 0:
        _log(
            "\nSkipping bonus (freegame) fixture sims — FIXTURE_BONUS_SIMS is 0. "
            "Writing empty books_bonus.json. Set FIXTURE_BONUS_SIMS>0 to generate math FS books."
        )
        write_books_json([], bonus_path)
    else:
        _log(
            "\nRunning freegame-criteria sims on **base** betmode for Storybook FS pool "
            f"({BONUS_FREEGAME_SIMS} books; may take a long time)…"
        )
        t_bonus = time.time()
        bonus_books = run_criteria(gamestate, config, "base", "freegame", BONUS_FREEGAME_SIMS)
        random.shuffle(bonus_books)
        write_books_json(bonus_books, bonus_path)
        _log(f"  Bonus phase wall time: {time.time() - t_bonus:.1f}s ({len(bonus_books)} books)")

    total_outer = sum(c for _, c in BASE_CRITERIA) + max(0, BONUS_FREEGAME_SIMS)
    _log(f"\nOuter spin attempts (budget check): {total_outer} (target < 100k)")

    _log("\nDone. Books written to: " + books_dir)
