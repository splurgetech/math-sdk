"""Executables for Clash Kronos Cluster."""

from game_calculations import GameCalculations
from game_kronos_bar import KronosBarState, apply_strike, count_exploded_symbols
from game_events import update_grid_mult_event, kronos_bar_event, kronos_strike_event
from src.calculations.cluster import Cluster
from src.events.events import update_freespin_event


class GameExecutables(GameCalculations):
    """Game-specific grouped functions."""

    def reset_grid_mults(self):
        """Zero out all cell multipliers."""
        self.position_multipliers = [
            [0] * self.config.num_rows[reel] for reel in range(self.config.num_reels)
        ]

    def reset_kronos_bar(self):
        """Create a fresh bar state for this spin sequence."""
        self.kronos_bar = KronosBarState(self.config.kronos_bar_threshold)

    def update_grid_mults(self):
        """Write 2× onto each cell in winning clusters; double if already stamped (cap 128×).

        Per GDD: first contribution 2×, each later win on same cell doubles.
        """
        if not self.win_data.get("totalWin"):
            return
        for win in self.win_data["wins"]:
            for pos in win["positions"]:
                r, row = pos["reel"], pos["row"]
                current = self.position_multipliers[r][row]
                if current == 0:
                    self.position_multipliers[r][row] = 2
                else:
                    self.position_multipliers[r][row] = min(current * 2, self.config.maximum_board_mult)
        update_grid_mult_event(self)

    def advance_kronos_bar(self):
        """Add this tumble step's exploded count to bar; trigger strike if bar fills."""
        exploded = count_exploded_symbols(self.win_data)
        if exploded == 0:
            return
        triggered = self.kronos_bar.add_symbols(exploded)
        kronos_bar_event(self, progress=self.kronos_bar.progress, filled=triggered)
        if triggered:
            self._run_kronos_strike()

    def _run_kronos_strike(self):
        """Perform strike: choose random cells, emit strike event, update grid, reset bar."""
        hits = apply_strike(
            self.position_multipliers,
            self.config.num_reels,
            self.config.num_rows,
        )
        kronos_strike_event(self, hits)
        update_grid_mult_event(self)
        self.kronos_bar.reset()
        kronos_bar_event(self, progress=0, filled=False)

    def get_clusters_update_wins(self):
        """Find clusters on board and update win manager."""
        clusters = Cluster.get_clusters(self.board, "wild")
        return_data = {"totalWin": 0, "wins": []}
        self.board, self.win_data = self.evaluate_clusters_with_grid(
            config=self.config,
            board=self.board,
            clusters=clusters,
            pos_mult_grid=self.position_multipliers,
            global_multiplier=self.global_multiplier,
            return_data=return_data,
        )
        Cluster.record_cluster_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        self.win_manager.tumble_win = self.win_data.get("totalWin", 0)

    def update_freespin(self) -> None:
        """Called before each FS reveal."""
        self.fs += 1
        update_freespin_event(self)
        self.win_manager.reset_spin_win()
        self.tumblewin_mult = 0
        self.win_data = {}
