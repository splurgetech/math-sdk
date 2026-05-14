"""GameState for Clash Kronos Cluster."""

import os

from game_kronos_bar import count_exploded_symbols
from game_override import GameStateOverride
from game_events import update_grid_mult_event


class GameState(GameStateOverride):
    """Core spin/freespin loop with Kronos bar and strike."""

    def _kronos_fs_trace(self, where: str) -> None:
        if os.environ.get("KRONOS_FS_TRACE") != "1":
            return
        remaining = self.tot_fs - self.fs
        print(
            f"[KRONOS_FS_TRACE] sim={self.sim} where={where} fs={self.fs} "
            f"tot_fs={self.tot_fs} remaining={remaining}",
            flush=True,
        )

    def _resolve_strike_then_evaluate(self) -> None:
        """Kronos strike (if pending) runs on settled post-tumble board, then cluster evaluation."""
        self.resolve_pending_kronos_strike_if_any()
        self.get_clusters_update_wins()

    def _emit_grid_tumble_and_update_bar(self) -> None:
        """Emit win events, ladder, tumble, then bar increment (bolt deferred to next resolve)."""
        self.emit_tumble_win_events()
        if self.win_data.get("totalWin", 0) <= 0:
            return
        self.update_grid_mults()
        exploded = count_exploded_symbols(self.win_data)
        self.tumble_game_board()
        self.apply_kronos_bar_after_tumble(exploded)

    def run_spin(self, sim, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()

            self._resolve_strike_then_evaluate()

            while self.win_data.get("totalWin", 0) > 0 and not self.wincap_triggered:
                self._emit_grid_tumble_and_update_bar()
                self._resolve_strike_then_evaluate()

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
            self._kronos_fs_trace("after_update_freespin")
            self.draw_board()
            # Emit current grid state at start of each FS spin (overlays persist)
            update_grid_mult_event(self)

            self._resolve_strike_then_evaluate()

            while self.win_data.get("totalWin", 0) > 0 and not self.wincap_triggered:
                self._emit_grid_tumble_and_update_bar()
                self._resolve_strike_then_evaluate()

            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()
                self._kronos_fs_trace("after_retrigger")

        self.end_freespin()
