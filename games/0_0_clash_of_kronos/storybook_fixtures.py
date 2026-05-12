"""Generate deterministic Storybook books for Clash of Kronos.

These are development fixtures, not RTP math outputs. They keep the web-sdk
Storybook aligned with the current GDD while the full game math is still being
implemented.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WEB_SDK = ROOT.parent / "web-sdk"
GAME_DIR = Path(__file__).resolve().parent
OUT_DIR = GAME_DIR / "storybook"
WEB_DATA_DIR = WEB_SDK / "apps/clash-of-kronos/src/stories/data"

BASEGAME = "basegame"
FREEGAME = "freegame"
REVEAL_PAD = [0, 0, 0, 0, 0]
NO_ANTICIPATION = [0, 0, 0, 0, 0]

REGULAR_SYMBOLS = [
    "KRONOS_SMALL",
    "PEGASUS",
    "EAGLE",
    "HELMET",
    "SHIELD",
    "RUNE",
]
WILD_SYMBOLS = ["WILD", "WILD_LIGHTNING", "WILD_SURGE", "WILD_HAMMER", "WILD_EAGLE"]

BASE_TRACKER_MULTS = {1: 1, 2: 1, 3: 1, 4: 1, 5: 2, 6: 3, 7: 5}
FREE_TRACKER_MULTS = {1: 1, 2: 1, 3: 1, 4: 2, 5: 3, 6: 5, 7: 10}


def sym(name: str, **attrs: Any) -> dict[str, Any]:
    raw: dict[str, Any] = {"name": name}
    if name == "SCATTER":
        raw["scatter"] = True
    if name in WILD_SYMBOLS:
        raw["wild"] = True
    raw.update(attrs)
    return raw


def chest(active: bool = False, value: int | None = None, underlying: str = "RUNE") -> dict[str, Any]:
    raw = sym("CHEST", chestActive=active, underlyingSymbol=underlying)
    if value is not None:
        raw["chestValue"] = value
    return raw


def board(rows: list[list[dict[str, Any]]]) -> list[list[dict[str, Any]]]:
    if len(rows) != 5 or any(len(row) != 5 for row in rows):
        raise ValueError("expected rows as 5 reels x 5 symbols including padding")
    return deepcopy(rows)


BASE_SAFE_BOARD = board(
    [
        [sym("HELMET"), sym("RUNE"), sym("SHIELD"), chest(False), sym("EAGLE")],
        [sym("SHIELD"), sym("KRONOS_SMALL"), sym("HELMET"), sym("HELMET"), sym("PEGASUS")],
        [sym("PEGASUS"), sym("HELMET"), chest(False), sym("EAGLE"), sym("HELMET")],
        [sym("EAGLE"), sym("HELMET"), sym("PEGASUS"), sym("RUNE"), sym("SHIELD")],
        [sym("KRONOS_SMALL"), sym("SHIELD"), chest(False), sym("HELMET"), sym("HELMET")],
    ]
)

GOLDEN_FIVE_RUNE_BOARD = board(
    [
        [sym("SHIELD"), sym("RUNE"), sym("PEGASUS"), chest(False), sym("EAGLE")],
        [sym("SHIELD"), sym("RUNE"), sym("PEGASUS"), chest(False), sym("EAGLE")],
        [sym("SHIELD"), sym("RUNE"), sym("PEGASUS"), chest(False), sym("EAGLE")],
        [sym("SHIELD"), sym("RUNE"), sym("PEGASUS"), chest(False), sym("EAGLE")],
        [sym("SHIELD"), sym("RUNE"), sym("PEGASUS"), chest(False), sym("EAGLE")],
    ]
)

BASE_LINE_BOARD = board(
    [
        [sym("HELMET"), sym("RUNE"), sym("SHIELD"), chest(False), sym("EAGLE")],
        [sym("SHIELD"), sym("RUNE"), sym("HELMET"), sym("HELMET"), sym("PEGASUS")],
        [sym("PEGASUS"), sym("RUNE"), chest(False), sym("EAGLE"), sym("HELMET")],
        [sym("EAGLE"), sym("HELMET"), sym("PEGASUS"), sym("RUNE"), sym("SHIELD")],
        [sym("KRONOS_SMALL"), sym("SHIELD"), chest(False), sym("HELMET"), sym("HELMET")],
    ]
)

BASE_MULTI_LINE_BOARD = board(
    [
        [sym("HELMET"), sym("RUNE"), sym("SHIELD"), chest(False), sym("EAGLE")],
        [sym("HELMET"), sym("RUNE"), sym("SHIELD"), sym("KRONOS_SMALL"), sym("PEGASUS")],
        [sym("HELMET"), sym("RUNE"), chest(False), sym("EAGLE"), sym("SHIELD")],
        [sym("EAGLE"), sym("PEGASUS"), sym("PEGASUS"), sym("RUNE"), sym("SHIELD")],
        [sym("KRONOS_SMALL"), sym("SHIELD"), chest(False), sym("HELMET"), sym("HELMET")],
    ]
)

BASE_STAGE_BOARD = board(
    [
        [sym("HELMET"), sym("RUNE"), sym("SHIELD"), chest(False), sym("EAGLE")],
        [sym("SHIELD"), sym("RUNE"), sym("HELMET"), sym("HELMET"), sym("PEGASUS")],
        [sym("PEGASUS"), sym("RUNE"), chest(False), sym("EAGLE"), sym("HELMET")],
        [sym("EAGLE"), sym("RUNE"), sym("PEGASUS"), sym("HELMET"), sym("SHIELD")],
        [sym("KRONOS_SMALL"), sym("RUNE"), chest(False), sym("SHIELD"), sym("HELMET")],
    ]
)

BASE_CHEST_BOARD = board(
    [
        [sym("HELMET"), sym("RUNE"), sym("SHIELD"), chest(True, 75), sym("EAGLE")],
        [sym("SHIELD"), sym("RUNE"), sym("HELMET"), sym("HELMET"), sym("PEGASUS")],
        [sym("PEGASUS"), sym("RUNE"), chest(True, 120), sym("EAGLE"), sym("HELMET")],
        [sym("EAGLE"), sym("RUNE"), sym("PEGASUS"), sym("HELMET"), sym("SHIELD")],
        [sym("KRONOS_SMALL"), sym("RUNE"), chest(True, 200), sym("SHIELD"), sym("HELMET")],
    ]
)

BASE_FREE_SPIN_TRIGGER_BOARD = board(
    [
        [sym("HELMET"), sym("SCATTER"), sym("SHIELD"), chest(False), sym("EAGLE")],
        [sym("SHIELD"), sym("RUNE"), sym("HELMET"), sym("HELMET"), sym("PEGASUS")],
        [sym("PEGASUS"), sym("SCATTER"), chest(False), sym("EAGLE"), sym("HELMET")],
        [sym("EAGLE"), sym("HELMET"), sym("PEGASUS"), sym("RUNE"), sym("SHIELD")],
        [sym("KRONOS_SMALL"), sym("SCATTER"), chest(False), sym("HELMET"), sym("HELMET")],
    ]
)

FREE_SAFE_BOARD = board(
    [
        [sym("HELMET"), sym("RUNE"), sym("SHIELD"), chest(False), sym("EAGLE")],
        [sym("SHIELD"), sym("KRONOS_SMALL"), sym("HELMET"), sym("HELMET"), sym("PEGASUS")],
        [sym("PEGASUS"), sym("HELMET"), chest(False), sym("EAGLE"), sym("HELMET")],
        [sym("EAGLE"), sym("HELMET"), sym("PEGASUS"), sym("RUNE"), sym("SHIELD")],
        [sym("KRONOS_SMALL"), sym("SHIELD"), chest(False), sym("HELMET"), sym("HELMET")],
    ]
)


class Book:
    def __init__(self, book_id: str, mode: str, description: str):
        self.book_id = book_id
        self.mode = mode
        self.description = description
        self.events: list[dict[str, Any]] = []

    def add(self, event_type: str, **payload: Any) -> dict[str, Any]:
        event = {"index": len(self.events), "type": event_type, **payload}
        self.events.append(event)
        return event

    def reveal(self, grid: list[list[dict[str, Any]]], game_type: str) -> None:
        self.add(
            "reveal",
            board=deepcopy(grid),
            paddingPositions=REVEAL_PAD,
            anticipation=NO_ANTICIPATION,
            gameType=game_type,
        )

    def finish(self, amount: int, win_level: int = 1, free_spin_end: bool = False) -> None:
        self.add("setTotalWin", amount=amount)
        if amount > 0:
            self.add("setWin", amount=amount, winLevel=win_level)
        if free_spin_end:
            self.add("freeSpinEnd", amount=amount, winLevel=win_level)
        self.add("finalWin", amount=amount)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.book_id,
            "description": self.description,
            "bet": 100,
            "payoutMultiplier": round(sum_final_win(self.events) / 100, 2),
            "events": self.events,
            "mode": self.mode,
        }


def tracker(game_type: str, stage: int) -> dict[str, Any]:
    mults = FREE_TRACKER_MULTS if game_type == FREEGAME else BASE_TRACKER_MULTS
    chest_unlock_stage = 3 if game_type == FREEGAME else 4
    return {
        "stage": stage,
        "multiplier": mults[stage],
        "gameType": game_type,
        "chestsActive": stage >= chest_unlock_stage,
    }


def line_win(
    symbol: str,
    kind: int,
    win: int,
    positions: list[tuple[int, int]],
    line_index: int,
    stage: int,
    game_type: str,
    *,
    chest_wins: list[tuple[tuple[int, int], int]] | None = None,
    power_ups: list[str] | None = None,
) -> dict[str, Any]:
    multiplier = tracker(game_type, stage)["multiplier"]
    win_without_mult = win // multiplier
    raw: dict[str, Any] = {
        "symbol": symbol,
        "kind": kind,
        "win": win,
        "positions": [pos(reel, row) for reel, row in positions],
        "meta": {
            "lineIndex": line_index,
            "multiplier": multiplier,
            "winWithoutMult": win_without_mult,
            "globalMult": multiplier,
            "lineMultiplier": 1,
            "trackerStage": stage,
            "trackerMultiplier": multiplier,
        },
    }
    if chest_wins:
        raw["chestWins"] = [{"position": pos(*position), "amount": amount} for position, amount in chest_wins]
    if power_ups:
        raw["powerUps"] = power_ups
    return raw


def pos(reel: int, row: int) -> dict[str, int]:
    return {"reel": reel, "row": row}


def tumble_symbols(*columns: list[str]) -> list[list[dict[str, Any]]]:
    return [[sym(name) for name in column] for column in columns]


def standard_tumble_positions() -> list[dict[str, int]]:
    return [pos(0, 1), pos(1, 1), pos(2, 1)]


def add_stage_win(
    book: Book,
    stage: int,
    amount: int,
    game_type: str,
    *,
    symbol_name: str = "RUNE",
    positions: list[tuple[int, int]] | None = None,
    power_ups: list[str] | None = None,
    chest_wins: list[tuple[tuple[int, int], int]] | None = None,
    tumble: bool = True,
) -> int:
    positions = positions or [(0, 1), (1, 1), (2, 1)]
    book.add("cascadeTrackerUpdate", **tracker(game_type, stage))
    if stage == (3 if game_type == FREEGAME else 4):
        chest_positions = [pos(0, 3), pos(2, 2), pos(4, 2)]
        book.add("chestUnlock", positions=chest_positions)
        book.add(
            "chestValuesUpdate",
            updates=[
                {"position": pos(0, 3), "value": 75, "active": True},
                {"position": pos(2, 2), "value": 120, "active": True},
                {"position": pos(4, 2), "value": 200, "active": True},
            ],
        )
    win = line_win(
        symbol_name,
        len(positions),
        amount,
        positions,
        2,
        stage,
        game_type,
        chest_wins=chest_wins,
        power_ups=power_ups,
    )
    book.add("winInfo", totalWin=amount, wins=[win])
    book.add("updateTumbleWin", amount=amount)
    if tumble:
        book.add(
            "tumbleBoard",
            explodingSymbols=[pos(reel, row) for reel, row in positions],
            newSymbols=tumble_symbols(["PEGASUS"], ["EAGLE"], ["HELMET"], [], []),
        )
    return amount


def sum_final_win(events: list[dict[str, Any]]) -> int:
    for event in reversed(events):
        if event["type"] == "finalWin":
            return int(event["amount"])
    return 0


def base_books() -> list[Book]:
    books: list[Book] = []

    book = Book("base-no-win", "base", "Base spin with no line wins, scatters, or power-up wilds.")
    book.reveal(BASE_SAFE_BOARD, BASEGAME)
    book.finish(0, 0)
    books.append(book)

    book = Book(
        "golden-five-rune-middle",
        "base",
        "Regression: 5 RUNE on payline middle row (positions must match kind=5).",
    )
    book.reveal(GOLDEN_FIVE_RUNE_BOARD, BASEGAME)
    book.add("cascadeTrackerUpdate", **tracker(BASEGAME, 1))
    book.add(
        "winInfo",
        totalWin=500,
        wins=[
            line_win(
                "RUNE",
                5,
                500,
                [(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)],
                2,
                1,
                BASEGAME,
            )
        ],
    )
    book.add("updateTumbleWin", amount=500)
    book.finish(500)

    books.append(book)

    book = Book("base-one-line-stage-1", "base", "One winning cascade stays at tracker stage 1.")
    book.reveal(BASE_LINE_BOARD, BASEGAME)
    add_stage_win(book, 1, 50, BASEGAME, tumble=False)
    book.finish(50)
    books.append(book)

    book = Book("base-multi-line-stage-1", "base", "Multiple line wins in one cascade still count as stage 1.")
    book.reveal(BASE_MULTI_LINE_BOARD, BASEGAME)
    book.add("cascadeTrackerUpdate", **tracker(BASEGAME, 1))
    wins = [
        line_win("HELMET", 3, 100, [(0, 0), (1, 0), (2, 0)], 1, 1, BASEGAME),
        line_win("RUNE", 3, 50, [(0, 1), (1, 1), (2, 1)], 2, 1, BASEGAME),
    ]
    book.add("winInfo", totalWin=150, wins=wins)
    book.add("updateTumbleWin", amount=150)
    book.add(
        "tumbleBoard",
        explodingSymbols=[pos(0, 0), pos(1, 0), pos(2, 0), pos(0, 1), pos(1, 1), pos(2, 1)],
        newSymbols=tumble_symbols(["PEGASUS", "EAGLE"], ["HELMET", "SHIELD"], ["HELMET", "RUNE"], [], []),
    )
    book.finish(150)
    books.append(book)

    book = Book("base-two-cascades-stage-2", "base", "Two separate winning cascades advance to stage 2.")
    book.reveal(BASE_STAGE_BOARD, BASEGAME)
    add_stage_win(book, 1, 50, BASEGAME)
    add_stage_win(book, 2, 100, BASEGAME, symbol_name="HELMET", positions=[(0, 0), (1, 0), (2, 0)], tumble=False)
    book.finish(150)
    books.append(book)

    book = Book("base-stage-4-chests-unlock", "base", "Fourth winning cascade unlocks chest dollar values.")
    book.reveal(BASE_CHEST_BOARD, BASEGAME)
    total = 0
    for stage, amount in [(1, 50), (2, 50), (3, 100), (4, 270)]:
        total += add_stage_win(
            book,
            stage,
            amount,
            BASEGAME,
            chest_wins=[((2, 2), 120)] if stage == 4 else None,
            tumble=stage < 4,
        )
    book.finish(total, 2)
    books.append(book)

    book = Book("base-stage-5-2x", "base", "Base tracker reaches stage 5 and applies 2x.")
    book.reveal(BASE_CHEST_BOARD, BASEGAME)
    total = 0
    for stage, amount in [(1, 50), (2, 50), (3, 50), (4, 100), (5, 200)]:
        total += add_stage_win(book, stage, amount, BASEGAME, tumble=stage < 5)
    book.finish(total, 2)
    books.append(book)

    book = Book("base-stage-6-3x", "base", "Base tracker reaches stage 6 and applies 3x.")
    book.reveal(BASE_CHEST_BOARD, BASEGAME)
    total = 0
    for stage, amount in [(1, 50), (2, 50), (3, 50), (4, 100), (5, 200), (6, 300)]:
        total += add_stage_win(book, stage, amount, BASEGAME, tumble=stage < 6)
    book.finish(total, 3)
    books.append(book)

    book = Book("base-stage-7-5x", "base", "Base tracker reaches stage 7 and applies 5x.")
    book.reveal(BASE_CHEST_BOARD, BASEGAME)
    total = 0
    for stage, amount in [(1, 50), (2, 50), (3, 50), (4, 100), (5, 200), (6, 300), (7, 500)]:
        total += add_stage_win(book, stage, amount, BASEGAME, tumble=stage < 7)
    book.finish(total, 4)
    books.append(book)

    lightning_board = deepcopy(BASE_LINE_BOARD)
    lightning_board[0][1] = sym("WILD_LIGHTNING")
    book = Book("base-lightning-wild", "base", "Lightning wild creates extra wilds before the next cascade.")
    book.reveal(lightning_board, BASEGAME)
    add_stage_win(book, 1, 100, BASEGAME, positions=[(0, 1), (1, 1), (2, 1)], power_ups=["WILD_LIGHTNING"])
    book.add(
        "lightningStrike",
        strikes=[
            {"position": pos(1, 2), "toSymbol": sym("WILD")},
            {"position": pos(3, 3), "toSymbol": sym("WILD")},
            {"position": pos(4, 1), "toSymbol": sym("WILD")},
        ],
    )
    add_stage_win(book, 2, 100, BASEGAME, tumble=False)
    book.finish(200)
    books.append(book)

    surge_board = deepcopy(BASE_CHEST_BOARD)
    surge_board[1][1] = sym("WILD_SURGE")
    book = Book("base-surge-wild-active-chests", "base", "Surge wild increases active chest values after stage 4.")
    book.reveal(surge_board, BASEGAME)
    total = 0
    for stage, amount in [(1, 50), (2, 50), (3, 50), (4, 120)]:
        total += add_stage_win(
            book,
            stage,
            amount,
            BASEGAME,
            power_ups=["WILD_SURGE"] if stage == 4 else None,
            tumble=True,
        )
    book.add(
        "surgeChests",
        updates=[
            {"position": pos(0, 3), "from": 75, "to": 125},
            {"position": pos(2, 2), "from": 120, "to": 180},
            {"position": pos(4, 2), "from": 200, "to": 300},
        ],
    )
    total += add_stage_win(book, 5, 360, BASEGAME, chest_wins=[((2, 2), 180)], tumble=False)
    book.finish(total, 3)
    books.append(book)

    hammer_board = deepcopy(BASE_LINE_BOARD)
    hammer_board[4][1] = sym("WILD_HAMMER")
    book = Book("base-hammer-wild-smash", "base", "Hammer is collected from a win and consumed after a zero-win cascade.")
    book.reveal(hammer_board, BASEGAME)
    add_stage_win(book, 1, 100, BASEGAME, positions=[(0, 1), (1, 1), (2, 1), (4, 1)], power_ups=["WILD_HAMMER"])
    book.add("hammerCollect", position=pos(4, 1))
    book.add(
        "hammerSmash",
        clearedPositions=[pos(0, 0), pos(1, 2), pos(2, 3), pos(3, 1)],
        newSymbols=tumble_symbols(["PEGASUS", "HELMET"], ["EAGLE"], ["RUNE"], ["SHIELD"], []),
        resultBoard=BASE_STAGE_BOARD,
        trackerStage=2,
        trackerMultiplier=1,
    )
    add_stage_win(book, 2, 100, BASEGAME, tumble=False)
    book.finish(200)
    books.append(book)

    eagle_board = deepcopy(BASE_CHEST_BOARD)
    eagle_board[0][1] = sym("WILD_EAGLE")
    book = Book("base-golden-eagle-wild", "base", "Golden eagle resolves lightning, surge, and hammer collect in sequence.")
    book.reveal(eagle_board, BASEGAME)
    total = 0
    for stage, amount in [(1, 50), (2, 50), (3, 50)]:
        total += add_stage_win(book, stage, amount, BASEGAME)
    total += add_stage_win(book, 4, 180, BASEGAME, power_ups=["WILD_EAGLE"])
    book.add(
        "lightningStrike",
        strikes=[
            {"position": pos(1, 2), "toSymbol": sym("WILD")},
            {"position": pos(3, 3), "toSymbol": sym("WILD")},
        ],
    )
    book.add(
        "surgeChests",
        updates=[
            {"position": pos(0, 3), "from": 75, "to": 125},
            {"position": pos(2, 2), "from": 120, "to": 180},
        ],
    )
    book.add("hammerCollect", position=pos(0, 1))
    book.finish(total, 2)
    books.append(book)

    book = Book("base-free-spin-trigger-3-scatters", "base", "Three scatters trigger eight free spins from base.")
    book.reveal(BASE_FREE_SPIN_TRIGGER_BOARD, BASEGAME)
    book.add("freeSpinTrigger", totalFs=8, positions=[pos(0, 1), pos(2, 1), pos(4, 1)])
    book.add("setTotalWin", amount=0)
    book.add("finalWin", amount=0)
    books.append(book)

    return books


def bonus_books() -> list[Book]:
    books: list[Book] = []

    book = Book("bonus-no-win", "bonus", "Free spin with no win.")
    book.add("updateFreeSpin", amount=0, total=8)
    book.reveal(FREE_SAFE_BOARD, FREEGAME)
    book.finish(0, 0)
    books.append(book)

    book = Book("bonus-stage-3-chests-unlock", "bonus", "Free spin tracker unlocks chests on stage 3.")
    book.add("updateFreeSpin", amount=1, total=8)
    book.reveal(BASE_CHEST_BOARD, FREEGAME)
    total = 0
    for stage, amount in [(1, 50), (2, 50), (3, 170)]:
        total += add_stage_win(
            book,
            stage,
            amount,
            FREEGAME,
            chest_wins=[((2, 2), 120)] if stage == 3 else None,
            tumble=stage < 3,
        )
    book.finish(total, 2)
    books.append(book)

    book = Book("bonus-stage-4-2x", "bonus", "Free spin tracker applies 2x at stage 4.")
    book.add("updateFreeSpin", amount=2, total=8)
    book.reveal(BASE_CHEST_BOARD, FREEGAME)
    total = 0
    for stage, amount in [(1, 50), (2, 50), (3, 100), (4, 200)]:
        total += add_stage_win(book, stage, amount, FREEGAME, tumble=stage < 4)
    book.finish(total, 2)
    books.append(book)

    book = Book("bonus-stage-7-10x", "bonus", "Free spin tracker applies 10x at stage 7.")
    book.add("updateFreeSpin", amount=3, total=8)
    book.reveal(BASE_CHEST_BOARD, FREEGAME)
    total = 0
    for stage, amount in [(1, 50), (2, 50), (3, 100), (4, 200), (5, 300), (6, 500), (7, 1000)]:
        total += add_stage_win(book, stage, amount, FREEGAME, tumble=stage < 7)
    book.finish(total, 4)
    books.append(book)

    retrigger_board = deepcopy(FREE_SAFE_BOARD)
    retrigger_board[0][1] = sym("SCATTER")
    retrigger_board[2][1] = sym("SCATTER")
    retrigger_board[4][1] = sym("SCATTER")
    book = Book("bonus-retrigger-3-scatters", "bonus", "Three free-spin scatters retrigger five spins.")
    book.add("updateFreeSpin", amount=4, total=8)
    book.reveal(retrigger_board, FREEGAME)
    book.add("freeSpinRetrigger", totalFs=5, positions=[pos(0, 1), pos(2, 1), pos(4, 1)])
    book.finish(0, 0)
    books.append(book)

    retrigger_board4 = deepcopy(retrigger_board)
    retrigger_board4[1][1] = sym("SCATTER")
    book = Book("bonus-retrigger-4-scatters", "bonus", "Four free-spin scatters retrigger eight spins.")
    book.add("updateFreeSpin", amount=5, total=8)
    book.reveal(retrigger_board4, FREEGAME)
    book.add("freeSpinRetrigger", totalFs=8, positions=[pos(0, 1), pos(1, 1), pos(2, 1), pos(4, 1)])
    book.finish(0, 0)
    books.append(book)

    lightning_board = deepcopy(BASE_LINE_BOARD)
    lightning_board[0][1] = sym("WILD_LIGHTNING")
    book = Book("bonus-lightning-wild", "bonus", "Lightning wild works during free spins.")
    book.add("updateFreeSpin", amount=6, total=8)
    book.reveal(lightning_board, FREEGAME)
    add_stage_win(book, 1, 100, FREEGAME, positions=[(0, 1), (1, 1), (2, 1)], power_ups=["WILD_LIGHTNING"])
    book.add(
        "lightningStrike",
        strikes=[
            {"position": pos(1, 2), "toSymbol": sym("WILD")},
            {"position": pos(3, 3), "toSymbol": sym("WILD")},
        ],
    )
    book.finish(100)
    books.append(book)

    book = Book("bonus-free-spin-end", "bonus", "Last free spin ends with the outro panel.")
    book.add("updateFreeSpin", amount=7, total=8)
    book.reveal(BASE_LINE_BOARD, FREEGAME)
    add_stage_win(book, 1, 100, FREEGAME, tumble=False)
    book.finish(100, 1, free_spin_end=True)
    books.append(book)

    return books


BASE_EVENT_PREFERRED: dict[str, str] = {
        "reveal": "base-one-line-stage-1",
        "cascadeTrackerUpdate": "base-stage-5-2x",
        "chestUnlock": "base-stage-4-chests-unlock",
        "chestValuesUpdate": "base-stage-4-chests-unlock",
        "winInfo": "golden-five-rune-middle",
        "updateTumbleWin": "base-one-line-stage-1",
        "tumbleBoard": "base-two-cascades-stage-2",
        "lightningStrike": "base-lightning-wild",
        "surgeChests": "base-surge-wild-active-chests",
        "hammerCollect": "base-hammer-wild-smash",
        "hammerSmash": "base-hammer-wild-smash",
        "freeSpinTrigger": "base-free-spin-trigger-3-scatters",
        "freeSpinRetrigger": "bonus-retrigger-3-scatters",
        "updateFreeSpin": "bonus-stage-4-2x",
        "setTotalWin": "base-one-line-stage-1",
        "setWin": "base-one-line-stage-1",
        "freeSpinEnd": "bonus-free-spin-end",
        "finalWin": "base-one-line-stage-1",
    }

BONUS_EVENT_PREFERRED: dict[str, str] = {
    "reveal": "bonus-stage-4-2x",
    "cascadeTrackerUpdate": "bonus-stage-7-10x",
    "chestUnlock": "bonus-stage-3-chests-unlock",
    "chestValuesUpdate": "bonus-stage-3-chests-unlock",
    "winInfo": "bonus-stage-7-10x",
    "updateTumbleWin": "bonus-stage-4-2x",
    "tumbleBoard": "bonus-stage-4-2x",
    "lightningStrike": "bonus-lightning-wild",
    "surgeChests": "base-surge-wild-active-chests",
    "hammerCollect": "base-hammer-wild-smash",
    "hammerSmash": "base-hammer-wild-smash",
    "freeSpinTrigger": "base-free-spin-trigger-3-scatters",
    "freeSpinRetrigger": "bonus-retrigger-3-scatters",
    "updateFreeSpin": "bonus-stage-4-2x",
    "setTotalWin": "bonus-stage-4-2x",
    "setWin": "bonus-stage-4-2x",
    "freeSpinEnd": "bonus-free-spin-end",
    "finalWin": "bonus-stage-4-2x",
}


def representative_events(books: list[Book], preferred: dict[str, str]) -> dict[str, dict[str, Any]]:
    events: dict[str, dict[str, Any]] = {}
    all_books = {book.book_id: book for book in books}
    for event_type, book_id in preferred.items():
        for event in reversed(all_books[book_id].events):
            if event["type"] == event_type:
                events[event_type] = deepcopy(event)
                break
    return events


def validate_books(books: list[Book]) -> None:
    allowed_symbols = set(REGULAR_SYMBOLS + WILD_SYMBOLS + ["SCATTER", "CHEST"])
    for book in books:
        previous_stage = 0
        for event in book.events:
            if event["index"] != book.events.index(event):
                raise ValueError(f"{book.book_id}: non-sequential event index")
            if event["type"] == "reveal":
                for reel in event["board"]:
                    for raw in reel:
                        if raw["name"] not in allowed_symbols:
                            raise ValueError(f"{book.book_id}: unknown symbol {raw['name']}")
            if event["type"] == "cascadeTrackerUpdate":
                if event["stage"] < previous_stage:
                    raise ValueError(f"{book.book_id}: tracker stage regressed")
                if event["stage"] > previous_stage + 1:
                    raise ValueError(f"{book.book_id}: tracker jumped from {previous_stage} to {event['stage']}")
                previous_stage = event["stage"]
                chest_unlock_stage = 3 if event["gameType"] == FREEGAME else 4
                if event["chestsActive"] != (event["stage"] >= chest_unlock_stage):
                    raise ValueError(f"{book.book_id}: invalid chest active state at stage {event['stage']}")
            if event["type"] == "winInfo":
                for w in event["wins"]:
                    if len(w["positions"]) != w["kind"]:
                        raise ValueError(
                            f"{book.book_id}: winInfo symbol={w.get('symbol')!r} kind={w['kind']} "
                            f"positions={len(w['positions'])}"
                        )


def ts_module(name: str, data: Any, imported_type: str) -> str:
    payload = json.dumps(data, indent="\t")
    if imported_type == "Bet":
        return (
            "import type { Bet } from '../../game/typesBookEvent';\n\n"
            "// Generated by math-sdk/games/0_0_clash_of_kronos/storybook_fixtures.py.\n"
            "// Edit the generator instead of this file.\n"
            "type StorybookBet = Bet & { id: string; description: string; mode: 'base' | 'bonus' };\n\n"
            f"const {name} = {payload} satisfies StorybookBet[];\n\n"
            f"export default {name};\n"
        )
    return (
        "import type { BookEvent } from '../../game/typesBookEvent';\n\n"
        "// Generated by math-sdk/games/0_0_clash_of_kronos/storybook_fixtures.py.\n"
        "// Edit the generator instead of this file.\n"
        f"const {name} = {payload} satisfies Record<string, BookEvent>;\n\n"
        f"export default {name};\n"
    )


def write() -> None:
    bases = base_books()
    bonuses = bonus_books()
    all_books = bases + bonuses
    validate_books(all_books)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)

    payloads = {
        "base_books": [book.to_dict() for book in bases],
        "bonus_books": [book.to_dict() for book in bonuses],
        "base_events": representative_events(all_books, BASE_EVENT_PREFERRED),
        "bonus_events": representative_events(all_books, BONUS_EVENT_PREFERRED),
    }

    for file_name, payload in payloads.items():
        (OUT_DIR / f"{file_name}.json").write_text(json.dumps(payload, indent=2) + "\n")

    (WEB_DATA_DIR / "base_books.ts").write_text(ts_module("books", payloads["base_books"], "Bet"))
    (WEB_DATA_DIR / "bonus_books.ts").write_text(ts_module("books", payloads["bonus_books"], "Bet"))
    (WEB_DATA_DIR / "base_events.ts").write_text(ts_module("events", payloads["base_events"], "Record<string, BookEvent>"))
    (WEB_DATA_DIR / "bonus_events.ts").write_text(ts_module("events", payloads["bonus_events"], "Record<string, BookEvent>"))


if __name__ == "__main__":
    write()
