#!/usr/bin/env bash
# Run Rust optimization on this machine (Mac/Linux). CPU-heavy, modest RAM.
#
# Prerequisite: library from a prior sim (usually NUC):
#   ./scripts/pull_library_from_nuc.sh
#
# Prerequisite: Rust (https://rustup.rs):
#   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
#   source "$HOME/.cargo/env"
#   cd optimization_program && cargo build --release
#
# Usage:
#   ./scripts/run_optimization.sh
#   OPT_MODES=base ./scripts/run_optimization.sh
#   RUST_THREADS=10 OPT_MODES=base ./scripts/run_optimization.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GAME_DIR="$REPO_ROOT/games/0_0_clash_kronos_cluster"
GAME_ID="0_0_clash_kronos_cluster"

if [[ -f "$HOME/.cargo/env" ]]; then
  # shellcheck source=/dev/null
  source "$HOME/.cargo/env"
fi

if ! command -v cargo >/dev/null 2>&1; then
  echo "ERROR: cargo not on PATH. Install Rust: https://rustup.rs" >&2
  exit 1
fi

BASE_LUT="$GAME_DIR/library/lookup_tables/lookUpTable_base.csv"
if [[ ! -f "$BASE_LUT" ]]; then
  echo "ERROR: Missing $BASE_LUT — run ./scripts/pull_library_from_nuc.sh first." >&2
  exit 1
fi

export RUN_SIMS=0
export RUN_OPTIMIZATION=1
export RUN_ANALYSIS="${RUN_ANALYSIS:-0}"
export SIM_BASE=0
export SIM_BONUS=0
export OPT_MODES="${OPT_MODES:-}"

PY="$REPO_ROOT/env/bin/python"
if [[ ! -x "$PY" ]]; then
  PY=python3
fi

echo "=== Local optimization (OPT_MODES=${OPT_MODES:-all with lookup}) RUST_THREADS=${RUST_THREADS:-20} ==="
cd "$GAME_DIR"
export PYTHONPATH="$REPO_ROOT:$GAME_DIR"
"$PY" run.py

echo "=== Done. RTP: $REPO_ROOT/scripts/rtp_from_lookup.sh ==="
