"""State overrides for Clash Kronos Cluster."""

from game_executables import GameExecutables


class GameStateOverride(GameExecutables):
    """Override/extend universal state functions for this game."""

    def reset_book(self):
        super().reset_book()
        self.tumble_win = 0
        # Reset grid + bar at start of each base spin
        self.reset_grid_mults()
        self.reset_kronos_bar()

    def reset_fs_spin(self):
        """FS entry: grid multipliers persist. Kronos bar resets each free spin in ``run_freespin``."""
        super().reset_fs_spin()
        # Do NOT call reset_grid_mults() here — FS overlays persist.

    def assign_special_sym_function(self):
        pass

    def check_repeat(self) -> None:
        """Checks if the spin failed distribution criteria."""
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

            if self.get_current_distribution_conditions()["force_freegame"] and not self.triggered_freegame:
                self.repeat = True

            # Freegame criteria (base or buy-bonus) can legitimately pay 0 for the whole feature;
            # repeating only burns CPU/RAM without improving distribution.
            if (
                self.win_manager.running_bet_win == 0
                and self.criteria != "0"
                and not (self.criteria == "freegame" and self.betmode in ("bonus", "base"))
            ):
                self.repeat = True

        self.repeat_count += 1
        self.check_current_repeat_count()
