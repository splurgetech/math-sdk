"""Main entry point for Clash Kronos Cluster math simulation.

Full RTP-style batch (no artificial FS cap on ``tot_fs``):

    KRONOS_UNCAPPED_FS=1 SIM_BASE=200000 SIM_BONUS=200000 python run.py

Omit ``KRONOS_UNCAPPED_FS`` to keep ``GameConfig.max_total_freespins`` (default 50).
Override counts with ``SIM_BASE`` / ``SIM_BONUS`` (integers per bet mode).

Optimization (Rust; install on NUC via ``scripts/nuc_install_rust.ps1``):

    RUN_OPTIMIZATION=1 SIM_BASE=0 SIM_BONUS=0 python run.py   # opt only (books must exist)

    RUN_OPTIMIZATION=1 RUN_ANALYSIS=1 python run.py             # sims + opt + PAR sheet

Env: ``RUN_SIMS`` (default 1), ``RUN_OPTIMIZATION``, ``RUN_ANALYSIS``, ``RUN_FORMAT_CHECKS`` (0/1).
Optional: ``OPT_MODES=base`` or ``base,bonus`` when ``RUN_SIMS=0`` (optimize existing lookups only).
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


def _env_bool(name: str, default: str = "0") -> bool:
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes")


def _optimization_target_modes(gamestate, num_sim_args: dict) -> list:
    """Modes to pass to the Rust optimizer."""
    raw = os.environ.get("OPT_MODES", "").strip()
    if raw:
        return [x.strip() for x in raw.split(",") if x.strip() in ("base", "bonus")]
    modes = [m for m in ("base", "bonus") if num_sim_args.get(m, 0) > 0]
    if modes:
        return modes
    for m in ("base", "bonus"):
        p = gamestate.output_files.lookups[m]["paths"]["base_lookup"]
        if os.path.isfile(p):
            modes.append(m)
    return modes


if __name__ == "__main__":

    num_threads = 10
    rust_threads = int(os.environ.get("RUST_THREADS", "20"))
    batching_size = 50000
    compression = True
    profiling = False

    num_sim_args = {
        "base": int(os.environ.get("SIM_BASE", "200000")),
        "bonus": int(os.environ.get("SIM_BONUS", "200000")),
    }

    run_sims = _env_bool("RUN_SIMS", "1")
    run_conditions = {
        "run_sims": run_sims,
        "run_optimization": _env_bool("RUN_OPTIMIZATION"),
        "run_analysis": _env_bool("RUN_ANALYSIS"),
        "run_format_checks": _env_bool("RUN_FORMAT_CHECKS"),
    }
    config = GameConfig()
    gamestate = GameState(config)
    target_modes = _optimization_target_modes(gamestate, num_sim_args)
    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        OptimizationSetup(config)

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

    if run_conditions["run_optimization"] and target_modes:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        custom_keys = [{"symbol": "scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"]:
        execute_all_tests(config)
