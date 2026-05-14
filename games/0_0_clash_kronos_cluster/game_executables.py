"""Executables for Clash Kronos Cluster."""

from game_constants import GRID_MULT_PENDING
from game_calculations import GameCalculations
from game_kronos_bar import KronosBarState, apply_kronos_bolts
from game_events import update_grid_mult_event, kronos_bar_event, kronos_strike_event
from src.calculations.cluster import Cluster
from src.events.events import update_freespin_event


class GameExecutables(GameCalculations):
    """Game-specific grouped functions."""

    def check_fs_condition(self, scatter_key: str = "scatter") -> bool:
        """No retrigger evaluation once total FS is at cap (avoids fake scatter tease + dead triggers)."""
        if not super().check_fs_condition(scatter_key):
            return False
        cap = getattr(self.config, "max_total_freespins", None)
        if (
            self.gametype == self.config.freegame_type
            and isinstance(cap, int)
            and cap > 0
            and self.tot_fs >= cap
        ):
            return False
        return True

    def reset_grid_mults(self):
        """Zero out all cell multipliers."""
        self.position_multipliers = [
            [0] * self.config.num_rows[reel] for reel in range(self.config.num_reels)
        ]

    def reset_kronos_bar(self):
        """Create a fresh bar state for this spin sequence."""
        self.kronos_bar = KronosBarState(self.config.kronos_bar_threshold)
        self.kronos_strike_pending = False

    def update_grid_mults(self):
        """Sugar Rush ladder: empty → pending ticket; pending → 2×; then double (capped).

        Each cell advances at most once per paying step, even if it appears in multiple
        ``wins[]`` clusters (e.g. overlapping wild-linked clusters).
        """
        if not self.win_data.get("totalWin"):
            return
        cap = self.config.maximum_board_mult
        cells = set()
        for win in self.win_data["wins"]:
            for pos in win["positions"]:
                cells.add((pos["reel"], pos["row"]))
        for r, row in cells:
            current = self.position_multipliers[r][row]
            if current == 0:
                self.position_multipliers[r][row] = GRID_MULT_PENDING
            elif current == GRID_MULT_PENDING:
                self.position_multipliers[r][row] = 2
            else:
                self.position_multipliers[r][row] = min(current * 2, cap)
        update_grid_mult_event(self)

    def resolve_pending_kronos_strike_if_any(self) -> None:
        """After tumble settled: if a bolt was collected on the prior bar update, place wilds then eval next."""
        if not self.kronos_strike_pending:
            return
        hits = apply_kronos_bolts(
            self.board,
            self.symbol_storage,
            self.config.num_reels,
            self.config.num_rows,
        )
        kronos_strike_event(self, hits)
        self.get_special_symbols_on_board()
        self.kronos_strike_pending = False
        # Emit bar clear after strike so clients can show gold (full) until bolt VFX / settle completes.
        kronos_bar_event(self, progress=0, filled=False)

    def apply_kronos_bar_after_tumble(self, exploded_count: int) -> None:
        """Increment bar by symbols removed this tumble (call only after ``tumble_game_board``).

        On threshold: emit full gold bar only, set ``kronos_strike_pending``, reset internal progress.
        The book emits ``kronosBar(progress=0)`` after ``kronosStrike`` so the UI is not overwritten in the same tick.
        """
        if exploded_count <= 0:
            return
        triggered = self.kronos_bar.add_symbols(exploded_count)
        kronos_bar_event(self, progress=self.kronos_bar.progress, filled=triggered)
        if triggered:
            self.kronos_strike_pending = True
            self.kronos_bar.reset()

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

    def _clamp_tot_fs(self) -> None:
        cap = getattr(self.config, "max_total_freespins", None)
        if cap is not None and isinstance(cap, int) and cap > 0:
            self.tot_fs = min(self.tot_fs, cap)

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        super().update_freespin_amount(scatter_key)
        self._clamp_tot_fs()

    def update_fs_retrigger_amt(self, scatter_key: str = "scatter") -> None:
        super().update_fs_retrigger_amt(scatter_key)
        self._clamp_tot_fs()

    def update_freespin(self) -> None:
        """Called before each FS reveal."""
        self.fs += 1
        update_freespin_event(self)
        self.win_manager.reset_spin_win()
        self.tumblewin_mult = 0
        self.win_data = {}
