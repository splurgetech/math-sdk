# Cluster-based win game

Clusters of 5 or more like-symbols are removed from the board, and symbols above on the reelstrip
fall to fill their place.

**Math targets (config):** headline RTP **~96.5%** (`GameConfig.rtp`), win cap **25,000×** bet, cluster pays from a **Sugar Rush 1000–style stepped ladder** (sizes 5–14 + 15+ bucket; see `paytable_sugar_rush1000.py`) multiplied by **`PAYTABLE_SCALE`** (env; default **0.003** in `game_config`). Raise/lower scale and re-run `run.py` to move empirical RTP. Realized RTP still comes from strips + FS rules — tune after major rule changes.

#### Basegame:
Standard tumbling game with Scatter and Wild symbols.
Minimum of **3** scatter symbols on the visible board are required to enter free spins (see ``freespin_triggers`` for counts).

#### Freegame:
Same basegame rule, except grid positions have multiplier overlays (Sugar Rush style). Cells start empty (`0`). The **first** win on a cell leaves a **pending** ticket (stored as `-1`); it contributes **nothing** to the win sum until that cell wins **again**, when it becomes **2×**, then **doubles** on each further win on that cell (cap **128×**). **Retriggers** use the **same** scatter ladder as base entry (**3+** scatters → same spin adds as ``freespin_triggers``). Strip ``FR0`` scatter density affects how often retriggers occur; ``max_total_freespins`` (**50** by default) clamps total FS. Once at that cap, math uses strip ``FR0_NS`` (``FR0`` with scatters replaced by ``L1``) so new board outcomes never show scatter symbols, and retriggers are not evaluated.

#### Notes:
Because of the separation between basegame and freegame types - there is an additional freespin entry check to check of the criteria requires a forced 
freespin condition. Otherwise, occurences of Scatter symbols tumbling onto the board during basegame criteria may appear.

#### Windows NUC setup
See ``docs/NUC_WINDOWS_SETUP.md``. Mac: ``ssh nuc``, ``./scripts/sync_to_nuc.sh``, ``./scripts/run_sims_on_nuc.sh``, ``./scripts/pull_library_from_nuc.sh``. One-time: ``./scripts/nuc_bootstrap.sh``.

#### Full math sims (`run.py`)
From this directory:

    KRONOS_UNCAPPED_FS=1 python run.py

- **`KRONOS_UNCAPPED_FS=1`** — sets ``max_total_freespins`` to **0** (no artificial cap on total free spins; **wincap** still applies).
- **`SIM_BASE`** / **`SIM_BONUS`** — optional env integers; default **200000** simulations per bet mode if unset.

Example with explicit counts:

    KRONOS_UNCAPPED_FS=1 SIM_BASE=150000 SIM_BONUS=150000 python run.py

Outputs under this game’s library / temp paths per the shared ``create_books`` pipeline; then ``generate_configs`` runs.

#### Storybook fixtures (web-sdk)
From this directory:
  python run_fixtures.py
writes `library/books/books_base.json` and `library/books/books_bonus.json` (gitignored).
By default `FIXTURE_BONUS_SIMS=0` so `books_bonus.json` is **empty** and `run_fixtures.py`
finishes quickly. Set `FIXTURE_BONUS_SIMS` to a positive integer when you can afford the
wall time (freegame-criteria sims are very slow — often run overnight or on CI).

Then:
  python export_storybook_fixtures.py
writes JSON under `web-sdk/apps/clash-kronos-cluster/src/stories/data/math_fixtures/`.

Use `python export_storybook_fixtures.py --bonus-only` to refresh only bonus fixtures when
base JSON is unchanged.

Fixture-only tuning: `FIXTURE_SHORT_FS=1` (default) caps scatter trigger spin counts in
exported books (not for RTP). `FIXTURE_SHORT_FS=0` uses full production triggers.

Longer / uncapped bonus fixture batch (then export to web-sdk):

    FIXTURE_SHORT_FS=0 KRONOS_UNCAPPED_FS=1 FIXTURE_BONUS_SIMS=50 python run_fixtures.py
    python export_storybook_fixtures.py

Production math: total free spins (initial + retriggers) are capped by `GameConfig.max_total_freespins`
(default **50**), unless **`KRONOS_UNCAPPED_FS=1`** (sets cap to **0** = disabled) for research / tail runs.
At cap, retriggers do not apply and freegame draws use ``FR0_NS`` (no scatter symbols). Base and freegame share the same ``freespin_triggers`` ladder below the cap; tail length is otherwise from strips + retriggers + **wincap**.

Debug: `KRONOS_FS_TRACE=1` logs `fs`, `tot_fs`, and remaining spins during the freegame
loop (see `gamestate.run_freespin`).

**Do not** build `books_bonus.json` from hand-authored TS/JSON — Storybook replays events
literally; mismatched `tumbleBoard` vs `winInfo` freezes the tumble layer.

If `run_fixtures.py` prints ``Killed: 9`` during the freegame phase, the process was usually
**SIGKILL**'d for **memory** (macOS OOM). Free other RAM, lower `FIXTURE_BASE_ZERO` /
`FIXTURE_BASE_WIN` for the same run, or generate bonus books on a machine with more headroom.
