"""Cluster win evaluation using sum-multiplier formula."""

from src.executables.executables import Executables
from src.calculations.cluster import Cluster
from src.calculations.board import Board
from src.config.config import Config


class GameCalculations(Executables):
    """Override evaluate_clusters to use basePay * max(1, sum(cellMults))."""

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
                if (n, sym) not in config.paytable:
                    continue

                # Sum cell multipliers; first win has all zeros so max(1, 0) = 1
                cell_mult_sum = sum(pos_mult_grid[p[0]][p[1]] for p in cluster)
                effective_mult = max(1, cell_mult_sum) * global_multiplier
                base_pay = config.paytable[(n, sym)]
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
