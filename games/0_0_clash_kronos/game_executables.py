"""Clash of Kronos executables — hidden mults, global mult, Kronos bar/transform."""

from game_calculations import GameCalculations
from game_events import (
    collect_hidden_mults_event,
    kronos_bar_event,
    kronos_transform_event,
    update_global_mult_event,
)
from game_hidden_mults import assign_hidden_mults, collect_from_wins
from game_kronos import (
    KronosBarState,
    apply_symbol_transform,
    count_exploded_cells,
    pick_transform_symbols,
)
from src.calculations.cluster import Cluster
from src.events.events import update_freespin_event


class GameExecutables(GameCalculations):
    def reset_hidden_mults(self):
        self.hidden_mult_grid = [
            [0 for _ in range(self.config.num_rows[reel])] for reel in range(self.config.num_reels)
        ]

    def reset_kronos_bar(self):
        self.kronos_bar = KronosBarState(self.config.kronos_bar_threshold)
        self.kronos_organic_wins = True
        kronos_bar_event(self, progress=0, filled=False)

    def assign_spin_hidden_mults(self):
        self.hidden_mult_grid = assign_hidden_mults(self.config.num_reels, self.config.num_rows)

    def get_clusters_update_wins(self):
        clusters = Cluster.get_clusters(self.board, "wild")
        return_data = {"totalWin": 0, "wins": []}
        self.board, self.win_data = self.evaluate_clusters_global(
            config=self.config,
            board=self.board,
            clusters=clusters,
            global_multiplier=int(self.global_multiplier),
            return_data=return_data,
        )
        if self.win_data.get("totalWin", 0) > 0:
            Cluster.record_cluster_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        self.win_manager.tumble_win = self.win_data.get("totalWin", 0)

    def collect_hidden_mults_after_wins(self) -> None:
        if self.win_data.get("totalWin", 0) <= 0:
            return
        collected, added = collect_from_wins(self.hidden_mult_grid, self.win_data)
        if added <= 0:
            return
        prev = int(self.global_multiplier)
        self.global_multiplier = prev + added
        collect_hidden_mults_event(self, collected, int(self.global_multiplier))
        if int(self.global_multiplier) != prev:
            update_global_mult_event(self)

    def emit_tumble_win_events(self) -> None:
        if self.win_data.get("totalWin", 0) > 0:
            super().emit_tumble_win_events()
            self.collect_hidden_mults_after_wins()

    def apply_kronos_bar_organic(self, exploded_count: int) -> None:
        if not self.kronos_organic_wins or exploded_count <= 0:
            return
        filled = self.kronos_bar.add_organic_wins(exploded_count)
        kronos_bar_event(self, progress=self.kronos_bar.progress, filled=filled)

    def tumble_after_organic_win(self) -> None:
        exploded = count_exploded_cells(self.win_data)
        self.tumble_game_board()
        self.apply_kronos_bar_organic(exploded)

    def run_organic_tumble_loop(self) -> None:
        self.get_clusters_update_wins()
        self.emit_tumble_win_events()
        while self.win_data.get("totalWin", 0) > 0 and not self.wincap_triggered:
            self.tumble_after_organic_win()
            self.get_clusters_update_wins()
            self.emit_tumble_win_events()

    def resolve_kronos_transform(self) -> None:
        from_sym, to_sym = pick_transform_symbols(self.board)
        positions = apply_symbol_transform(self.board, self.symbol_storage, from_sym, to_sym)
        self.kronos_bar.reset()
        kronos_bar_event(self, progress=0, filled=False)
        kronos_transform_event(self, from_sym, to_sym, positions)
        self.kronos_organic_wins = False
        self.get_clusters_update_wins()
        self.emit_tumble_win_events()
        self.kronos_organic_wins = True
        while self.win_data.get("totalWin", 0) > 0 and not self.wincap_triggered:
            self.tumble_after_organic_win()
            self.get_clusters_update_wins()
            self.emit_tumble_win_events()

    def run_kronos_phase(self) -> None:
        while self.kronos_bar.progress >= self.kronos_bar.threshold and not self.wincap_triggered:
            if self.win_data.get("totalWin", 0) > 0:
                break
            self.resolve_kronos_transform()

    def run_spin_phases(self) -> None:
        self.run_organic_tumble_loop()
        self.run_kronos_phase()

    def update_freespin(self) -> None:
        self.fs += 1
        update_freespin_event(self)
        self.win_manager.reset_spin_win()
        self.tumblewin_mult = 0
        self.win_data = {}
