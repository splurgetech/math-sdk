"""Clash of Kronos configuration."""

import os

from game_constants import (
    BONUS_BUY_SCATTER_WEIGHTS,
    FREESPIN_TRIGGERS,
    KRONOS_BAR_THRESHOLD,
    MAX_FS_RETRIGGERS,
)
from game_paytable import build_paytable
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "0_0_clash_kronos"
        self.provider_number = 0
        self.working_name = "Clash of Kronos"
        self.wincap = 10000.0
        self.win_type = "cluster"
        self.rtp = 0.965
        self.construct_paths()

        self.num_reels = 7
        self.num_rows = [7] * self.num_reels
        self.paytable = build_paytable()

        self.include_padding = True
        self.special_symbols = {"wild": ["WD"], "scatter": ["SC"]}

        self.freespin_triggers = {
            self.basegame_type: dict(FREESPIN_TRIGGERS),
            self.freegame_type: dict(FREESPIN_TRIGGERS),
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }

        self.kronos_bar_threshold = KRONOS_BAR_THRESHOLD
        self.max_fs_retriggers = MAX_FS_RETRIGGERS

        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "FR0_NS": "FR0_NS.csv", "WCAP": "WCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        mode_maxwins = {"base": 10000, "bonus": 10000}

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
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=mode_maxwins["base"],
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "scatter_triggers": {3: 1, 4: 1, 5: 1},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 5, 4: 2, 5: 1},
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
                cost=100.0,
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
                            "scatter_triggers": BONUS_BUY_SCATTER_WEIGHTS,
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
        ]
