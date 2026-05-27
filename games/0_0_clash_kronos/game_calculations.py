from game_constants import BASE_PAYTABLE_SCALE
from src.executables.executables import Executables
from src.calculations.cluster import Cluster
from src.calculations.board import Board
from src.config.config import Config


class GameCalculations(Executables):
    """Cluster evaluation using global multiplier only (no per-cell mult on wins)."""

    def _cluster_pay_scale(self) -> float:
        if self.betmode == "bonus":
            return 1.0
        return BASE_PAYTABLE_SCALE

    def evaluate_clusters_global(
        self,
        config: Config,
        board: Board,
        clusters: dict,
        global_multiplier: int = 0,
        return_data: dict | None = None,
    ):
        if return_data is None:
            return_data = {"totalWin": 0, "wins": []}
        exploding_symbols = []
        total_win = 0
        mult_factor = global_multiplier if global_multiplier > 0 else 1

        for sym in clusters:
            for cluster in clusters[sym]:
                syms_in_cluster = len(cluster)
                if (syms_in_cluster, sym) not in config.paytable:
                    continue
                sym_win = config.paytable[(syms_in_cluster, sym)] * self._cluster_pay_scale()
                symwin_mult = sym_win * mult_factor
                total_win += symwin_mult
                json_positions = [{"reel": p[0], "row": p[1]} for p in cluster]
                central_pos = Cluster.get_central_cluster_position(json_positions)
                return_data["wins"].append(
                    {
                        "symbol": sym,
                        "clusterSize": syms_in_cluster,
                        "win": symwin_mult,
                        "positions": json_positions,
                        "meta": {
                            "globalMult": global_multiplier,
                            "clusterMult": 0,
                            "winWithoutMult": sym_win,
                            "overlay": {"reel": central_pos[0], "row": central_pos[1]},
                        },
                    }
                )
                for positions in cluster:
                    board[positions[0]][positions[1]].explode = True
                    entry = {"reel": positions[0], "row": positions[1]}
                    if entry not in exploding_symbols:
                        exploding_symbols.append(entry)

        return_data["totalWin"] += total_win
        return board, return_data
