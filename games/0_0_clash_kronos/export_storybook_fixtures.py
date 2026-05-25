"""Export Storybook fixtures to web-sdk apps/clash-kronos."""
import argparse
import json
import os
import random
import sys

_GAME_DIR = os.path.dirname(os.path.abspath(__file__))
_SDK_ROOT = os.path.abspath(os.path.join(_GAME_DIR, "..", ".."))
_WEB_SDK_ROOT = os.path.abspath(os.path.join(_SDK_ROOT, "..", "web-sdk"))
_FIXTURES_RELPATH = "apps/clash-kronos/src/stories/data/math_fixtures"


def load_books(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def has_type(book: dict, event_type: str) -> bool:
    return any(e["type"] == event_type for e in book["events"])


def to_fixture(book: dict) -> dict:
    events = book["events"]
    first_reveal = next((e for e in events if e["type"] == "reveal"), None)
    game_type = first_reveal["gameType"] if first_reveal else "basegame"
    return {"gameType": game_type, "events": events}


def pick_named(books: list) -> dict[str, dict]:
    out = {}
    for book in books:
        events = book["events"]
        if has_type(book, "kronosTransform") and "base_kronos" not in out:
            out["base_kronos"] = to_fixture(book)
        if has_type(book, "collectHiddenMults") and "base_collect" not in out:
            out["base_collect"] = to_fixture(book)
        if has_type(book, "updateGlobalMult") and "base_global_mult" not in out:
            gm = max(
                (e.get("globalMult", 0) for e in events if e["type"] in ("updateGlobalMult", "collectHiddenMults")),
                default=0,
            )
            if gm > 1 and "base_global_mult" not in out:
                out["base_global_mult"] = to_fixture(book)
        if not has_type(book, "winInfo") and "base_no_win" not in out:
            out["base_no_win"] = to_fixture(book)
        if has_type(book, "winInfo") and not has_type(book, "collectHiddenMults") and "base_one_cluster" not in out:
            out["base_one_cluster"] = to_fixture(book)
        if sum(1 for e in events if e["type"] == "tumbleBoard") >= 2 and "base_multi_tumble" not in out:
            out["base_multi_tumble"] = to_fixture(book)
        if has_type(book, "freeSpinTrigger") and "bonus_trigger" not in out:
            out["bonus_trigger"] = to_fixture(book)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=_WEB_SDK_ROOT)
    args = parser.parse_args()
    out_dir = os.path.join(args.out_dir, _FIXTURES_RELPATH)
    os.makedirs(out_dir, exist_ok=True)

    books_dir = os.path.join(_GAME_DIR, "library", "books")
    base_path = os.path.join(books_dir, "books_base.json")
    bonus_path = os.path.join(books_dir, "books_bonus.json")

    if not os.path.isfile(base_path):
        print("Missing books_base.json — run: python run_fixtures.py", file=sys.stderr)
        sys.exit(1)

    base_books = load_books(base_path)
    random.seed(42)
    random.shuffle(base_books)

    named = pick_named(base_books)
    for name, fixture in named.items():
        path = os.path.join(out_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(fixture, f, indent=2)
        print(f"Wrote {path}")

    pool = [to_fixture(b) for b in base_books[: min(25, len(base_books))]]
    pool_path = os.path.join(out_dir, "base_pool.json")
    with open(pool_path, "w", encoding="utf-8") as f:
        json.dump(pool, f, indent=2)
    print(f"Wrote {pool_path} ({len(pool)} books)")

    if os.path.isfile(bonus_path):
        bonus_books = load_books(bonus_path)
        random.shuffle(bonus_books)
        bonus_pool = [to_fixture(b) for b in bonus_books[: min(15, len(bonus_books))]]
        bp = os.path.join(out_dir, "bonus_pool.json")
        with open(bp, "w", encoding="utf-8") as f:
            json.dump(bonus_pool, f, indent=2)
        print(f"Wrote {bp} ({len(bonus_pool)} books)")


if __name__ == "__main__":
    main()
