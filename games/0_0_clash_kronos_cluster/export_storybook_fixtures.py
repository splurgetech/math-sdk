"""
Export Storybook fixture books from math-sdk simulation output.

Prerequisites: run `python run_fixtures.py` first to generate
library/books/books_base.json.

Usage (from this directory):
    python export_storybook_fixtures.py

Writes JSON fixture files to:
    ../../web-sdk (auto-detected) or via --out-dir flag:
    <out_dir>/apps/clash-kronos-cluster/src/stories/data/math_fixtures/

Each fixture is a JSON object: { "gameType": "basegame", "events": [...] }
matching the shape of golden_base_book.ts so Storybook can use it with:
    playBet({ ...fixture, state: fixture.events })

Run workflow:
    python run_fixtures.py
    python export_storybook_fixtures.py
    (commit resulting math_fixtures/*.json)
"""
import sys
import os
import json
import argparse

_GAME_DIR = os.path.dirname(os.path.abspath(__file__))
_SDK_ROOT = os.path.abspath(os.path.join(_GAME_DIR, "..", ".."))
_WEB_SDK_ROOT = os.path.abspath(os.path.join(_SDK_ROOT, "..", "web-sdk"))
_FIXTURES_RELPATH = "apps/clash-kronos-cluster/src/stories/data/math_fixtures"


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


def select_fixtures(books: list) -> dict[str, dict]:
    """Pick one representative book per category; return {name: fixture}."""
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
    args = parser.parse_args()

    web_sdk = args.out_dir or _WEB_SDK_ROOT
    fixtures_dir = os.path.join(web_sdk, _FIXTURES_RELPATH)

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

    print(f"\nSelected {len(fixtures)} named fixtures + pool ({len(pool)} books).")
    print("Done.")


if __name__ == "__main__":
    main()
