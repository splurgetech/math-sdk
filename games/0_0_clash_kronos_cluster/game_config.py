"""Clash Kronos Cluster game configuration."""

import os
from copy import deepcopy

from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode

from paytable_sugar_rush1000 import build_sugar_rush_style_paytable


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
        self.wincap = 25000.0
        self.win_type = "cluster"
        # Stake-style headline RTP (~96.5%); realized RTP still requires sim tuning + pay ladder.
        self.rtp = 0.965
        self.construct_paths()

        # 7x7 grid, no wilds
        self.num_reels = 7
        self.num_rows = [7] * self.num_reels

        # Stepped cluster pays (sizes 5–14 + 15+ bucket); see paytable_sugar_rush1000.py.
        # Full SR1000-style ladder (× bet). Tune RTP via distributions + Rust optimization, not sub-cent scale.
        self.paytable_scale = float(os.environ.get("PAYTABLE_SCALE", "1.0"))
        self.paytable = build_sugar_rush_style_paytable(self.paytable_scale)

        self.include_padding = True
        # Scatter on reels; ``W`` exists only from Kronos bolts (not on strips)
        self.special_symbols = {"scatter": ["S"], "wild": ["W"]}

        # 3-7 scatters → 10/12/15/20/30 free spins; 8+ same as 7. Same ladder for base entry
        # and for retriggers during freegame (``gametype`` selects the table in executables).
        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 12, 5: 15, 6: 20, 7: 30},
        }
        for n in range(8, self.num_reels * max(self.num_rows) + 1):
            self.freespin_triggers[self.basegame_type][n] = 30
        self.freespin_triggers[self.freegame_type] = deepcopy(self.freespin_triggers[self.basegame_type])
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }

        # Per-cell cap: 2 → 4 → 8 → … → 128
        self.maximum_board_mult = 128
        # Kronos bar fills at this count
        self.kronos_bar_threshold = 20

        # Hard ceiling on total FS (initial + retriggers). Production always 50 (wincap + cert).
        # KRONOS_UNCAPPED_FS=1 disables cap for research only — do not use for publish sims.
        self.max_total_freespins = 50
        if os.environ.get("KRONOS_UNCAPPED_FS") == "1":
            self.max_total_freespins = 0

        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        # At most one scatter per reel on any 7-high window (circular strip); avoids stacked S.
        self._sanitize_scatter_spacing_on_reel_strips()

        # Scatter-free FR0: same layout as FR0 but ``S`` → ``L1`` so at-cap free spins never show scatters.
        self.reels["FR0_NS"] = [
            ["L1" if cell == "S" else cell for cell in col] for col in self.reels["FR0"]
        ]

        mode_maxwins = {"base": 25000, "bonus": 25000}

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
                        quota=0.03,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 8, 4: 2, 5: 1},
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
                            "scatter_triggers": {3: 8, 4: 2, 5: 1},
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
        ]

    def _scatter_id_names(self) -> set[str]:
        return set(self.special_symbols.get("scatter", []))

    def _sanitize_one_reel_strip_column(self, column: list[str], window: int) -> list[str]:
        """Circular strip: at most one scatter symbol in any ``window`` consecutive positions (one per reel column view)."""
        scatter_names = self._scatter_id_names()
        if not column or not scatter_names:
            return column
        repl = "L1"
        out = list(column)
        n = len(out)
        changed = True
        while changed:
            changed = False
            for i in range(n):
                if out[i] not in scatter_names:
                    continue
                for k in range(1, window):
                    j = (i - k) % n
                    if out[j] in scatter_names:
                        out[i] = repl
                        changed = True
                        break
        return out

    def _sanitize_scatter_spacing_on_reel_strips(self) -> None:
        window = max(self.num_rows) if self.num_rows else 7
        for strip_id, cols in list(self.reels.items()):
            self.reels[strip_id] = [
                self._sanitize_one_reel_strip_column(col, window) for col in cols
            ]
