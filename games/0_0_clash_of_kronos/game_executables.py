import random

from game_calculations import GameCalculations
from src.events.events import (
    tumble_board_event,
    update_tumble_win_event,
    win_info_event,
    set_total_event,
    set_win_event,
)
from kronos_lines import KronosLines
from game_events_kronos import (
    cascade_tracker_update_event,
    chest_unlock_event,
    chest_values_update_event,
    lightning_strike_event,
    hammer_collect_event,
    hammer_smash_event,
    surge_chests_event,
)

BASE_TRACK_MULTS = {i: x for i, x in zip(range(1, 8), [1, 1, 1, 1, 2, 3, 5])}
FREE_TRACK_MULTS = {i: x for i, x in zip(range(1, 8), [1, 1, 1, 2, 3, 5, 10])}


class GameExecutables(GameCalculations):
    """Cascade line wins + Kronos tracker; powers between cascades."""

    def _tracker_table(self):
        return FREE_TRACK_MULTS if self.gametype == self.config.freegame_type else BASE_TRACK_MULTS

    def _stage_mult(self, stage: int) -> int:
        return self._tracker_table()[min(max(stage, 1), 7)]

    def _chest_threshold(self) -> int:
        return 3 if self.gametype == self.config.freegame_type else 4

    def _preview_stage_mult(self) -> tuple[int, int]:
        preview = max(1, self.cascade_tracker_emitted_count + 1)
        return preview, self._stage_mult(preview)

    def _clear_explode_flags(self) -> None:
        for r in range(self.config.num_reels):
            for row in range(self.config.num_rows[r]):
                self.board[r][row].explode = False

    def _mark_wins_explode(self) -> None:
        seen: set[tuple[int, int]] = set()
        for win in self.win_data["wins"]:
            for p in win["positions"]:
                key = (p["reel"], p["row"])
                if key in seen:
                    continue
                seen.add(key)
                self.board[p["reel"]][p["row"]].explode = True

    def _run_tumble(self) -> None:
        self.tumble_board()
        tumble_board_event(self)

    def _emit_tracker(self, *, stage: int) -> None:
        mult = self._stage_mult(stage)
        setattr(self, "cascade_stage", stage)
        setattr(self, "current_tracker_multiplier", mult)
        cascade_tracker_update_event(
            self,
            stage=stage,
            multiplier=mult,
            chests_active=stage >= self._chest_threshold(),
        )

    def _emit_chest_award_events(self) -> None:
        unlock = []
        updates = []
        for r in range(self.config.num_reels):
            for row in range(self.config.num_rows[r]):
                sym = self.board[r][row]
                if sym.defn.name != "CHEST":
                    continue
                val = random.choice([50, 75, 100, 120, 150, 200])
                sym.assign_attribute({"prize": val})
                client_row = row + 1  # client visible row for Stake padding convention
                unlock.append({"reel": r, "row": client_row})
                updates.append({"position": {"reel": r, "row": client_row}, "value": int(val), "active": True})
        if unlock:
            chest_unlock_event(self, unlock)
            chest_values_update_event(self, updates)

    def _collect_winning_power_symbols(self) -> dict[str, tuple[int, int] | None]:
        want = {"WILD_LIGHTNING": None, "WILD_SURGE": None, "WILD_HAMMER": None, "WILD_EAGLE": None}
        for win in self.win_data["wins"]:
            for p in win["positions"]:
                sym = self.board[p["reel"]][p["row"]]
                if sym.name in want and want[sym.name] is None:
                    want[sym.name] = (p["reel"], p["row"])
        return want  # type: ignore[return-value]

    def _maybe_emit_hammer_collect(self, powers: dict[str, tuple[int, int] | None]) -> None:
        pos = powers.get("WILD_HAMMER")
        if pos is None:
            return
        self.hammer_held = True
        hammer_collect_event(self, hammer_position={"reel": pos[0], "row": pos[1] + 1})

    def _apply_lightning_if_triggered(self, powers: dict[str, tuple[int, int] | None]) -> None:
        if powers.get("WILD_LIGHTNING") is None and powers.get("WILD_EAGLE") is None:
            return
        strikes: list[dict] = []
        candidates: list[tuple[int, int]] = []
        for r in range(self.config.num_reels):
            for row in range(self.config.num_rows[r]):
                sym = self.board[r][row]
                if sym.check_attribute("scatter"):
                    continue
                if sym.defn.name == "CHEST":
                    continue
                if sym.check_attribute("wild"):
                    continue
                candidates.append((r, row))
        random.shuffle(candidates)
        k = min(len(candidates), random.randint(2, min(4, max(2, len(candidates)))))
        for r, row in candidates[:k]:
            new_sym = self.create_symbol("WILD")
            self.board[r][row] = new_sym
            strikes.append({"position": {"reel": r, "row": row + 1}, "toSymbol": {"name": "WILD", "wild": True}})
        if strikes:
            lightning_strike_event(self, strikes)

    def _maybe_surge(self, powers: dict[str, tuple[int, int] | None]) -> None:
        if powers.get("WILD_SURGE") is None and powers.get("WILD_EAGLE") is None:
            return
        if self.cascade_tracker_emitted_count < self._chest_threshold():
            return
        updates = []
        for r in range(self.config.num_reels):
            for row in range(self.config.num_rows[r]):
                sym = self.board[r][row]
                if sym.defn.name != "CHEST":
                    continue
                pv = sym.prize
                if not isinstance(pv, (int, float)) or pv <= 0:
                    continue
                old = float(pv)
                new = max(int(old) + 25, int(old * 1.25))
                sym.assign_attribute({"prize": new})
                updates.append(
                    {"position": {"reel": r, "row": row + 1}, "from": int(old), "to": int(new)}
                )
        if updates:
            surge_chests_event(self, updates)

    def _hammer_clears_board(self) -> list[dict]:
        cleared: list[dict] = []
        for r in range(self.config.num_reels):
            for row in range(self.config.num_rows[r]):
                sym = self.board[r][row]
                keep = sym.check_attribute("scatter") or sym.check_attribute("wild")
                if sym.defn.name == "CHEST" and isinstance(sym.prize, (int, float)) and sym.prize > 0:
                    keep = True
                if keep:
                    sym.explode = False
                else:
                    sym.explode = True
                    cleared.append({"reel": r, "row": row + 1})
        return cleared

    def _resolve_hammer_smash(self) -> None:
        self.hammer_held = False
        self.cascade_tracker_emitted_count += 1
        st_emit = self.cascade_tracker_emitted_count

        self._emit_tracker(stage=st_emit)

        if st_emit == self._chest_threshold() and not getattr(self, "_kronos_chest_book_done", False):
            self._emit_chest_award_events()
            self._kronos_chest_book_done = True

        cleared = self._hammer_clears_board()
        self.tumble_board()
        hammer_smash_event(self, cleared_positions=cleared)
        self._clear_explode_flags()

    def evaluate_lines_board(self) -> None:
        """Cascade: lines → tumble until no wins; aggregates spin_win."""
        self.cascade_tracker_emitted_count = 0
        self._kronos_chest_book_done = False
        setattr(self, "cascade_stage", 0)

        while True:
            self._clear_explode_flags()

            preview_stage, mult_preview = self._preview_stage_mult()
            chest_pay = preview_stage >= self._chest_threshold()

            self.win_data = KronosLines.get_lines(
                self.board,
                self.config,
                chests_unlocked=chest_pay,
                wild_key="wild",
                wild_sym="WILD",
                multiplier_method="symbol",
                global_multiplier=int(mult_preview),
                tracker_stage=preview_stage,
                tracker_multiplier=int(mult_preview),
            )

            if self.win_data["totalWin"] <= 0:
                if getattr(self, "hammer_held", False):
                    self._resolve_hammer_smash()
                    continue
                break

            self.cascade_tracker_emitted_count += 1
            st_emit = self.cascade_tracker_emitted_count

            self._emit_tracker(stage=st_emit)

            if st_emit == self._chest_threshold() and not self._kronos_chest_book_done:
                self._emit_chest_award_events()
                self._kronos_chest_book_done = True

            KronosLines.record_lines_wins(self)
            self.win_manager.update_spinwin(self.win_data["totalWin"])

            win_info_event(self)
            update_tumble_win_event(self)
            self.evaluate_wincap()
            if self.wincap_triggered:
                break

            powers = self._collect_winning_power_symbols()
            self._maybe_emit_hammer_collect(powers)

            self._mark_wins_explode()
            self._run_tumble()

            self._apply_lightning_if_triggered(powers)
            self._maybe_surge(powers)

            self._clear_explode_flags()

        if self.win_manager.spin_win > 0:
            set_win_event(self)
        set_total_event(self)
