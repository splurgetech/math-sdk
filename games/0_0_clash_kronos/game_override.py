from copy import deepcopy

from game_constants import (
    BONUS_BUY_SCATTER_WEIGHTS,
    FREESPIN_TRIGGERS,
    MAX_FS_RETRIGGERS,
    MAX_SCATTERS_ON_BOARD,
)
from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
from src.events.events import fs_trigger_event


def _stake_cents(payout_multiplier: float) -> int:
    """RGS lookup/books use payoutMultiplier in cents; must be a multiple of 10."""
    cents = int(round(payout_multiplier * 100))
    return (cents // 10) * 10


class GameStateOverride(GameExecutables):
    def update_final_win(self) -> None:
        super().update_final_win()
        cents = _stake_cents(self.book.payout_multiplier)
        self.final_win = cents / 100.0
        self.book.payout_multiplier = self.final_win
        if round(self.book.basegame_wins + self.book.freegame_wins, 2) != self.final_win:
            self.book.freegame_wins = round(self.final_win - self.book.basegame_wins, 2)

    def reset_book(self):
        super().reset_book()
        self.global_multiplier = 0
        self.tumble_win = 0
        self.fs_retrigger_count = 0
        self.reset_hidden_mults()
        self.reset_kronos_bar()

    def reset_fs_spin(self):
        super().reset_fs_spin()
        self.global_multiplier = 0
        self.fs_retrigger_count = 0
        self.reset_hidden_mults()

    def update_freespin(self) -> None:
        """Each FS spin starts with an empty Kronos bar (same as base spins)."""
        self.reset_kronos_bar()
        super().update_freespin()

    def assign_special_sym_function(self):
        pass

    def _scatter_count_for_trigger(self) -> int:
        n = self.count_special_symbols("scatter")
        if n not in self.config.freespin_triggers[self.gametype]:
            n = min(n, max(self.config.freespin_triggers[self.gametype].keys()))
        return n

    def _scatter_count_for_retrigger(self) -> int:
        n = self.count_special_symbols("scatter")
        if n not in self.config.freespin_retriggers[self.gametype]:
            n = min(n, max(self.config.freespin_retriggers[self.gametype].keys()))
        return n

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        self.record(
            {
                "kind": self.count_special_symbols(scatter_key),
                "symbol": scatter_key,
                "gametype": self.gametype,
            }
        )
        n = self._scatter_count_for_trigger()
        self.tot_fs = self.config.freespin_triggers[self.gametype][n]
        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        fs_trigger_event(self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger)

    def update_fs_retrigger_amt(self, scatter_key: str = "scatter") -> None:
        if self.fs_retrigger_count >= MAX_FS_RETRIGGERS:
            return
        self.fs_retrigger_count += 1
        n = self._scatter_count_for_retrigger()
        self.tot_fs += self.config.freespin_retriggers[self.gametype][n]
        fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)

    def _no_scatter_fs_reel_id(self) -> str:
        """After max retriggers, use buy-specific strips in bonus buy mode."""
        if self.betmode == "bonus" and "FR0_BUY_NS" in self.config.reels:
            return "FR0_BUY_NS"
        return "FR0_NS"

    def create_board_reelstrips(self) -> None:
        conditions = self.get_current_distribution_conditions()
        reel_weights = conditions["reel_weights"]
        ns_reel = self._no_scatter_fs_reel_id()
        if (
            self.gametype == self.config.freegame_type
            and self.fs_retrigger_count >= MAX_FS_RETRIGGERS
            and ns_reel in self.config.reels
        ):
            saved = deepcopy(reel_weights[self.gametype])
            reel_weights[self.gametype] = {ns_reel: 1}
            super().create_board_reelstrips()
            reel_weights[self.gametype] = saved
        else:
            super().create_board_reelstrips()

    def draw_board(self, emit_event: bool = True, trigger_symbol: str = "scatter") -> None:
        if (
            self.get_current_distribution_conditions().get("force_freegame")
            and self.gametype == self.config.basegame_type
        ):
            triggers = self.get_current_distribution_conditions().get(
                "scatter_triggers", BONUS_BUY_SCATTER_WEIGHTS
            )
            num_scatters = int(get_random_outcome(triggers))
            num_scatters = min(num_scatters, MAX_SCATTERS_ON_BOARD)
            self.force_special_board(trigger_symbol, num_scatters)
        elif (
            not self.get_current_distribution_conditions().get("force_freegame")
            and self.gametype == self.config.basegame_type
        ):
            self.create_board_reelstrips()
            min_trigger = min(self.config.freespin_triggers[self.gametype].keys())
            while self.count_special_symbols(trigger_symbol) >= min_trigger:
                self.create_board_reelstrips()
            while self.count_special_symbols(trigger_symbol) > MAX_SCATTERS_ON_BOARD:
                self.create_board_reelstrips()
        else:
            self.create_board_reelstrips()
            while self.count_special_symbols(trigger_symbol) > MAX_SCATTERS_ON_BOARD:
                self.create_board_reelstrips()

        self.assign_spin_hidden_mults()
        if emit_event:
            from game_events import reveal_with_hidden_mults_event

            reveal_with_hidden_mults_event(self)

    def check_repeat(self) -> None:
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

            if self.get_current_distribution_conditions().get("force_freegame") and not (
                self.triggered_freegame
            ):
                self.repeat = True

            if self.win_manager.running_bet_win == 0 and self.criteria != "0":
                self.repeat = True
