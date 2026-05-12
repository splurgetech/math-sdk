"""GameState for Clash Kronos Cluster."""

from game_override import GameStateOverride
from game_events import update_grid_mult_event


class GameState(GameStateOverride):
    """Core spin/freespin loop with Kronos bar and strike."""

    def _tumble_step(self):
        """Shared inner tumble step: evaluate, emit wins, update grid, advance bar."""
        self.get_clusters_update_wins()
        self.emit_tumble_win_events()
        if self.win_data.get("totalWin", 0) > 0:
            self.update_grid_mults()
            self.advance_kronos_bar()

    def run_spin(self, sim, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()

            self._tumble_step()

            while self.win_data.get("totalWin", 0) > 0 and not self.wincap_triggered:
                self.tumble_game_board()
                self._tumble_step()

            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board()
            # Emit current grid state at start of each FS spin (overlays persist)
            update_grid_mult_event(self)

            self._tumble_step()

            while self.win_data.get("totalWin", 0) > 0 and not self.wincap_triggered:
                self.tumble_game_board()
                self._tumble_step()

            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

        self.end_freespin()
