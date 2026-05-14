"""Main entry point for Clash Kronos Cluster math simulation.

Full RTP-style batch (no artificial FS cap on ``tot_fs``):

    KRONOS_UNCAPPED_FS=1 SIM_BASE=200000 SIM_BONUS=200000 python run.py

Omit ``KRONOS_UNCAPPED_FS`` to keep ``GameConfig.max_total_freespins`` (default 50).
Override counts with ``SIM_BASE`` / ``SIM_BONUS`` (integers per bet mode).
"""

import os

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":

    num_threads = 10
    rust_threads = 20
    batching_size = 50000
    compression = True
    profiling = False

    # Default: substantial batch for RTP/tail work. Override: SIM_BASE / SIM_BONUS env (ints).
    num_sim_args = {
        "base": int(os.environ.get("SIM_BASE", "200000")),
        "bonus": int(os.environ.get("SIM_BONUS", "200000")),
    }

    run_conditions = {
        "run_sims": True,
        "run_optimization": False,
        "run_analysis": False,
        "run_format_checks": False,
    }
    target_modes = ["base", "bonus"]

    config = GameConfig()
    gamestate = GameState(config)
    if run_conditions["run_optimization"]:
        optimization_setup_class = OptimizationSetup(config)

    if run_conditions["run_sims"]:
        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )

    generate_configs(gamestate)

    if run_conditions["run_optimization"]:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        custom_keys = [{"symbol": "scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"]:
        execute_all_tests(config)
