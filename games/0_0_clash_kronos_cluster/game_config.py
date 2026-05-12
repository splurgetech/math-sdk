"""Clash Kronos Cluster game configuration."""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):
    """Singleton config for Clash Kronos Cluster."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "0_0_clash_kronos_cluster"
        self.provider_number = 0
        self.working_name = "Clash of Kronos (Cluster)"
        self.wincap = 5000.0
        self.win_type = "cluster"
        self.rtp = 0.9700
        self.construct_paths()

        # 7x7 grid, no wilds
        self.num_reels = 7
        self.num_rows = [7] * self.num_reels

        self.paytable = self._build_paytable()

        self.include_padding = True
        # No wilds — scatter only
        self.special_symbols = {"scatter": ["S"]}

        # 3-7 scatters → 10/12/15/20/30 free spins; 8+ treated same as 7
        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 12, 5: 15, 6: 20, 7: 30},
            self.freegame_type: {3: 10, 4: 12, 5: 15, 6: 20, 7: 30},
        }
        for gt in [self.basegame_type, self.freegame_type]:
            for n in range(8, self.num_reels * max(self.num_rows) + 1):
                self.freespin_triggers[gt][n] = 30
        # Anticipation from 2 scatters (min trigger - 1)
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }

        # Per-cell cap: 2 → 4 → 8 → … → 128
        self.maximum_board_mult = 128
        # Kronos bar fills at this count
        self.kronos_bar_threshold = 20

        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        mode_maxwins = {"base": 5000, "bonus": 5000}

        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=mode_maxwins["base"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="freegame",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 5, 4: 3, 5: 1},
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.4,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.5,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="bonus",
                cost=100,
                rtp=self.rtp,
                max_win=mode_maxwins["bonus"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="freegame",
                        quota=1.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            # Bonus buy always enters FS with >=3 scatters
                            "scatter_triggers": {3: 5, 4: 3, 5: 1},
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
        ]

    def _build_paytable(self) -> dict:
        """Per-exact-size paytable for cluster sizes 5..49. Placeholder values."""
        paytable = {}
        base_pays = {
            "H1": 5.0, "H2": 2.0,
            "M1": 1.0, "M2": 0.7,
            "L1": 0.5, "L2": 0.3, "L3": 0.2,
        }
        growth = 1.35
        for sym, pay5 in base_pays.items():
            for n in range(5, 50):
                paytable[(n, sym)] = round(pay5 * (growth ** (n - 5)), 4)
        return paytable
