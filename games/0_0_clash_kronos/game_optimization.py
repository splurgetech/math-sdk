"""Optimization parameters — enable when tuning RTP."""

from optimization_program.optimization_config import (
    ConstructConditions,
    ConstructFenceBias,
    ConstructParameters,
    ConstructScaling,
    verify_optimization_input,
)


class OptimizationSetup:
    def __init__(self, game_config):
        wincaps = {bm.get_name(): bm.get_wincap() for bm in game_config.bet_modes}
        game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.01, av_win=wincaps["base"], search_conditions=wincaps["base"]
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.37, hr=200, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=3.5, rtp=0.59).return_dict(),
                },
            },
            "bonus": {
                "conditions": {
                    "freegame": ConstructConditions(
                        rtp=0.96, hr=1, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                },
            },
        }
        verify_optimization_input(game_config)
