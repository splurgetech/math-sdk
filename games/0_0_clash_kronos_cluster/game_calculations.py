"""Cluster win evaluation using sum-multiplier formula."""

from src.executables.executables import Executables
from src.calculations.cluster import Cluster
from src.calculations.board import Board
from src.config.config import Config


def _numeric_cell_mult(value: int) -> int:
    """Only stored multipliers >= 2 contribute to the cluster sum (0 and pending -1 do not)."""
    if isinstance(value, int) and value >= 2:
        return value
    return 0


class GameCalculations(Executables):
    """Override evaluate_clusters to use basePay * max(1, sum(cellMults))."""

    def create_board_reelstrips(self) -> None:
        """Use scatter-free FR0 when total FS is already at cap (``FR0_NS`` on ``GameConfig``)."""
        cap = getattr(self.config, "max_total_freespins", None)
        if (
            self.gametype == self.config.freegame_type
            and isinstance(cap, int)
            and cap > 0
            and self.tot_fs >= cap
            and "FR0_NS" in self.config.reels
        ):
            cond = self.get_current_distribution_conditions()
            rw = cond["reel_weights"]
            fg_key = self.config.freegame_type
            saved_fg = rw[fg_key]
            rw[fg_key] = {"FR0_NS": 1}
            try:
                super().create_board_reelstrips()
            finally:
                rw[fg_key] = saved_fg
            return
        super().create_board_reelstrips()

    def evaluate_clusters_with_grid(
        self,
        config: Config,
        board: Board,
        clusters: dict,
        pos_mult_grid: list,
        global_multiplier: int = 1,
        return_data: dict = None,
    ) -> type:
        if return_data is None:
            return_data = {"totalWin": 0, "wins": []}

        total_win = 0

        for sym in clusters:
            for cluster in clusters[sym]:
                n = len(cluster)
                n_eff = min(n, 15)
                if (n_eff, sym) not in config.paytable:
                    continue

                # Sum numeric cell mults only; pending (-1) and 0 contribute 0 → max(1, 0)=1 on fresh/ticket-only clusters
                cell_mult_sum = sum(_numeric_cell_mult(pos_mult_grid[p[0]][p[1]]) for p in cluster)
                effective_mult = max(1, cell_mult_sum) * global_multiplier
                base_pay = config.paytable[(n_eff, sym)]
                win = base_pay * effective_mult
                total_win += win

                json_positions = [{"reel": p[0], "row": p[1]} for p in cluster]
                central_pos = Cluster.get_central_cluster_position(json_positions)

                return_data["wins"].append(
                    {
                        "symbol": sym,
                        "clusterSize": n,
                        "win": win,
                        "positions": json_positions,
                        "meta": {
                            "globalMult": global_multiplier,
                            "clusterMult": max(1, cell_mult_sum),
                            "winWithoutMult": base_pay,
                            "overlay": {
                                "reel": central_pos[0],
                                "row": central_pos[1],
                            },
                        },
                    }
                )

                for p in cluster:
                    board[p[0]][p[1]].explode = True

        return_data["totalWin"] += total_win
        return board, return_data
