from game_override import GameStateOverride


class GameState(GameStateOverride):
    """7×7 cluster — hidden mults, global mult, Kronos transform."""

    def run_spin(self, sim, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()

            self.run_spin_phases()
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

            self.run_spin_phases()
            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition() and self.fs_retrigger_count < self.config.max_fs_retriggers:
                self.update_fs_retrigger_amt()

        self.end_freespin()
