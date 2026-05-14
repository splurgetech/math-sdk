"""
Export Storybook fixture books from math-sdk simulation output.

Prerequisites: run `python run_fixtures.py` first to generate
library/books/books_base.json and library/books/books_bonus.json.

Usage (from this directory):
    python export_storybook_fixtures.py
    python export_storybook_fixtures.py --bonus-only   # skip base; only read books_bonus.json

Environment (bonus export):
    BONUS_POOL_MAX — max books written to bonus_pool.json (default 25, clamped 1–100).
      Bonus named picks and pool are taken after a fixed-seed shuffle of the loaded
      books so the pool is not always the same leading slice of the sim output.

Writes JSON fixture files to:
    ../../web-sdk (auto-detected) or via --out-dir flag:
    <out_dir>/apps/clash-kronos-cluster/src/stories/data/math_fixtures/

Each fixture is a JSON object: { "gameType": "...", "events": [...] } for Storybook:
    playBet({ ...fixture, state: fixture.events })

Named outputs: base_*.json, base_pool.json, bonus_*.json (when selectable),
bonus_pool.json.

Run workflow:
    python run_fixtures.py
    python export_storybook_fixtures.py
    (commit resulting math_fixtures/*.json)
"""
import sys
import os
import json
import argparse
import random

_GAME_DIR = os.path.dirname(os.path.abspath(__file__))
_SDK_ROOT = os.path.abspath(os.path.join(_GAME_DIR, "..", ".."))
_WEB_SDK_ROOT = os.path.abspath(os.path.join(_SDK_ROOT, "..", "web-sdk"))
_FIXTURES_RELPATH = "apps/clash-kronos-cluster/src/stories/data/math_fixtures"
# Bonus pool: FS books are longer than base; default cap keeps repo size small.
_DEFAULT_BONUS_POOL_MAX = 25
_BONUS_POOL_MAX_CAP = 100
_BONUS_NAMED_JSON = (
    "bonus_short",
    "bonus_retrigger",
    "bonus_with_strike",
    "bonus_long",
    "bonus_many_retrigger",
)


def load_books(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def has_type(book: dict, event_type: str) -> bool:
    return any(e["type"] == event_type for e in book["events"])


def count_type(book: dict, event_type: str) -> int:
    return sum(1 for e in book["events"] if e["type"] == event_type)


def to_fixture(book: dict) -> dict:
    """Strip math-only keys; return { gameType, events } for Storybook."""
    events = book["events"]
    # Derive gameType from first reveal event
    first_reveal = next((e for e in events if e["type"] == "reveal"), None)
    game_type = first_reveal["gameType"] if first_reveal else "basegame"
    return {"gameType": game_type, "events": events}


def _win_positions(win_info: dict) -> set[tuple[int, int]]:
    out: set[tuple[int, int]] = set()
    for w in win_info.get("wins", []):
        for p in w.get("positions", []):
            out.add((int(p["reel"]), int(p["row"])))
    return out


def validate_tumble_win_chain(events: list, label: str) -> list[str]:
    """
    Light invariant check: each tumbleBoard's explodingSymbols should match the
    immediately preceding winInfo cluster(s) (avoids Storybook tumble desync).
    """
    errs: list[str] = []
    last_win: set[tuple[int, int]] | None = None
    for i, e in enumerate(events):
        t = e.get("type")
        if t == "winInfo":
            last_win = _win_positions(e)
        elif t == "tumbleBoard":
            if last_win is None:
                continue
            for p in e.get("explodingSymbols", []):
                key = (int(p["reel"]), int(p["row"]))
                if key not in last_win:
                    errs.append(
                        f"{label} event[{i}] tumbleBoard: explode {key} "
                        f"not in preceding winInfo positions"
                    )
            last_win = None
    return errs


def select_fixtures(books: list) -> tuple[dict[str, dict], list]:
    """Pick one representative base book per category; return (named fixtures, pool)."""
    no_win = next((b for b in books if not has_type(b, "winInfo")), None)
    one_cluster = next(
        (b for b in books if count_type(b, "winInfo") == 1), None
    )
    two_cascades = next(
        (b for b in books if count_type(b, "winInfo") == 2), None
    )
    # Prefer the shortest book with 3+ wins so the story runs quickly
    multi_tumble_books = [b for b in books if count_type(b, "winInfo") >= 3]
    multi_tumble = min(multi_tumble_books, key=lambda b: len(b["events"]), default=None)

    strike_books = [b for b in books if has_type(b, "kronosStrike")]
    kronos_strike = min(strike_books, key=lambda b: len(b["events"]), default=None)

    # Pool book: all books for the "random" story (trimmed to 50 for git size)
    pool = books[:50]

    selections = {
        "base_no_win": no_win,
        "base_one_cluster": one_cluster,
        "base_two_cascades": two_cascades,
        "base_multi_tumble": multi_tumble,
        "base_kronos_strike": kronos_strike,
    }
    return {k: to_fixture(v) for k, v in selections.items() if v is not None}, [
        to_fixture(b) for b in pool
    ]


def select_bonus_fixtures(books: list, pool_max: int) -> tuple[dict[str, dict], list]:
    """Pick bonus (freegame) fixtures and a trimmed pool for Storybook."""
    with_trigger = [b for b in books if has_type(b, "freeSpinTrigger")]
    bonus_short = min(with_trigger, key=lambda b: len(b["events"]), default=None)

    retrigger = next(
        (
            b
            for b in books
            if has_type(b, "freeSpinRetrigger")
            or count_type(b, "freeSpinTrigger") >= 2
        ),
        None,
    )

    strike_books = [b for b in books if has_type(b, "kronosStrike")]
    bonus_with_strike = (
        min(strike_books, key=lambda b: len(b["events"]), default=None)
        if strike_books
        else None
    )

    bonus_long = max(with_trigger, key=lambda b: len(b["events"]), default=None)

    with_retrigger_evt = [b for b in books if has_type(b, "freeSpinRetrigger")]
    bonus_many_retrigger = (
        max(with_retrigger_evt, key=lambda b: count_type(b, "freeSpinRetrigger"))
        if with_retrigger_evt
        else None
    )

    pool_books = books[:pool_max]

    selections = {
        "bonus_short": bonus_short,
        "bonus_retrigger": retrigger,
        "bonus_with_strike": bonus_with_strike,
        "bonus_long": bonus_long,
        "bonus_many_retrigger": bonus_many_retrigger,
    }
    named = {k: to_fixture(v) for k, v in selections.items() if v is not None}
    pool = [to_fixture(b) for b in pool_books]
    return named, pool


def write_fixture(fixture: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(fixture, f, indent=2)
    event_count = len(fixture["events"])
    print(f"  Written: {os.path.basename(path)}  ({event_count} events)")


def write_pool(pool: list, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(pool, f, indent=2)
    print(f"  Written: {os.path.basename(path)}  ({len(pool)} books)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        default=None,
        help="web-sdk root (default: auto-detect from repo layout)",
    )
    parser.add_argument(
        "--bonus-only",
        action="store_true",
        help="Only export bonus fixtures (skip base); use when books_base.json is absent or base fixtures are unchanged.",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip tumbleBoard vs preceding winInfo checks (not recommended).",
    )
    args = parser.parse_args()

    web_sdk = args.out_dir or _WEB_SDK_ROOT
    fixtures_dir = os.path.join(web_sdk, _FIXTURES_RELPATH)

    if not args.bonus_only:
        base_books_path = os.path.join(_GAME_DIR, "library", "books", "books_base.json")
        if not os.path.exists(base_books_path):
            print(f"ERROR: {base_books_path} not found — run `python run_fixtures.py` first.")
            sys.exit(1)

        print(f"\nLoading books from: {base_books_path}")
        books = load_books(base_books_path)
        print(f"  {len(books)} books loaded")

        fixtures, pool = select_fixtures(books)

        print(f"\nWriting fixtures to: {fixtures_dir}")
        for name, fixture in fixtures.items():
            write_fixture(fixture, os.path.join(fixtures_dir, f"{name}.json"))

        write_pool(pool, os.path.join(fixtures_dir, "base_pool.json"))

        if not args.no_validate:
            for name, fix in fixtures.items():
                ve = validate_tumble_win_chain(fix["events"], name)
                if ve:
                    print("VALIDATION FAILED:\n  " + "\n  ".join(ve))
                    sys.exit(1)
            for bi, fix in enumerate(pool):
                ve = validate_tumble_win_chain(fix["events"], f"base_pool[{bi}]")
                if ve:
                    print("VALIDATION FAILED:\n  " + "\n  ".join(ve))
                    sys.exit(1)

        print(f"\nSelected {len(fixtures)} named base fixtures + pool ({len(pool)} books).")
    else:
        print("\n--bonus-only: skipping base fixture export.")

    bonus_books_path = os.path.join(_GAME_DIR, "library", "books", "books_bonus.json")
    if not os.path.exists(bonus_books_path):
        print(f"ERROR: {bonus_books_path} not found — run `python run_fixtures.py` first.")
        sys.exit(1)

    print(f"\nLoading bonus books from: {bonus_books_path}")
    bonus_books = load_books(bonus_books_path)
    print(f"  {len(bonus_books)} books loaded")

    if len(bonus_books) == 0:
        print("\nNo bonus books in pool — writing empty bonus_pool.json; removing named bonus_*.json.")
        for name in _BONUS_NAMED_JSON:
            p = os.path.join(fixtures_dir, f"{name}.json")
            if os.path.isfile(p):
                os.remove(p)
                print(f"  Removed stale: {os.path.basename(p)}")
        write_pool([], os.path.join(fixtures_dir, "bonus_pool.json"))
    else:
        try:
            raw_max = int(os.environ.get("BONUS_POOL_MAX", str(_DEFAULT_BONUS_POOL_MAX)))
        except ValueError:
            raw_max = _DEFAULT_BONUS_POOL_MAX
        bonus_pool_max = max(1, min(raw_max, _BONUS_POOL_MAX_CAP))
        if raw_max != bonus_pool_max:
            print(
                f"  BONUS_POOL_MAX={raw_max!r} → using {bonus_pool_max} "
                f"(clamped 1–{_BONUS_POOL_MAX_CAP})"
            )

        random.seed(0)
        shuffled_bonus = list(bonus_books)
        random.shuffle(shuffled_bonus)

        bonus_fixtures, bonus_pool = select_bonus_fixtures(
            shuffled_bonus, pool_max=bonus_pool_max
        )

        if not args.no_validate:
            for name, fix in bonus_fixtures.items():
                ve = validate_tumble_win_chain(fix["events"], name)
                if ve:
                    print("VALIDATION FAILED:\n  " + "\n  ".join(ve))
                    sys.exit(1)
            for bi, fix in enumerate(bonus_pool):
                ve = validate_tumble_win_chain(fix["events"], f"bonus_pool[{bi}]")
                if ve:
                    print("VALIDATION FAILED:\n  " + "\n  ".join(ve))
                    sys.exit(1)

        for name, fixture in bonus_fixtures.items():
            write_fixture(fixture, os.path.join(fixtures_dir, f"{name}.json"))

        write_pool(bonus_pool, os.path.join(fixtures_dir, "bonus_pool.json"))

        print(
            f"\nSelected {len(bonus_fixtures)} named bonus fixtures + pool ({len(bonus_pool)} books)."
        )
    print("Done.")


if __name__ == "__main__":
    main()
