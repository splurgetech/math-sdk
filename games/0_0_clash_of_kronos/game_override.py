from src.calculations.statistics import get_random_outcome

from game_executables import GameExecutables
from game_events_kronos import free_spin_retrigger_event


class GameStateOverride(GameExecutables):
    """
    This class is is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset
    """

    def reset_book(self):
        super().reset_book()
        self.hammer_held = False
        self._kronos_chest_book_done = False

    def update_fs_retrigger_amt(self, scatter_key: str = "scatter") -> None:
        """Retrigger must send incremental spins (`totalFs`), not cumulative `tot_fs`."""
        add = self.config.freespin_triggers[self.gametype][self.count_special_symbols(scatter_key)]
        self.tot_fs += add
        free_spin_retrigger_event(self, add)

    def assign_special_sym_function(self):
        mult_syms = self.config.special_symbols.get("multiplier", [])
        self.special_symbol_functions = {n: [self.assign_mult_property] for n in mult_syms}
        self.special_symbol_functions["CHEST"] = [self.assign_dormant_chest]

    def assign_dormant_chest(self, symbol) -> dict:
        """Locked chests participate in reels but carry no prize until unlock."""
        symbol.prize = None
        symbol.has_prize = False
        return {}

    def assign_mult_property(self, symbol) -> dict:
        """Assign multiplier value to Wild symbol in freegame."""
        multiplier_value = 1
        if self.gametype == self.config.freegame_type:
            multiplier_value = get_random_outcome(
                self.get_current_distribution_conditions()["mult_values"][self.gametype]
            )
        symbol.assign_attribute({"multiplier": multiplier_value})
        return {}

    def check_repeat(self):
        super().check_repeat()
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
                return
            if win_criteria is None and self.final_win == 0:
                self.repeat = True
                return
