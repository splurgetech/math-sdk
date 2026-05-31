# Clash of Kronos

6×6 cluster pays (5+). Hidden cell mults (1×–5× / 10× / 20× only, 10–55% of cells) collect into additive global mult.
Kronos bar (20 organic win cells per spin; resets each spin incl. FS) → symbol transform or W wild.

Symbols: H1–H3 / L1–L4 pays, S scatter, W wild (Kronos only).

FS: 3→8, 4→10, 5→12 spins; retriggers +4/+5/+6 (50% of initial); forced entry ~89%×3 / 10%×4 / 1%×5; max 5 SC; 3 retrigger cap then FR0_NS.
Bonus buy: 100×, ≥3 SC (weighted toward 3); FS reels FR0_BUY / FR0_BUY_NS (tamer than organic FR0).

RTP target 96–97%, wincap 10,000×.

Fixtures: python run_fixtures.py && python export_storybook_fixtures.py
Production sims: PAYTABLE_SCALE=1.0 on NUC (`./scripts/run_sims_on_nuc.sh` or `tune_clash_kronos.sh`).
Same cluster pays in base and bonus buy (shared paytable; buy uses FR0_BUY strips only).
Distribution quotas (env): DIST_FG_QUOTA default 0.08, DIST_ZERO_QUOTA default 0.10, wincap 0.001.
Tuning log: library/tuning_log.csv — target publish 96.5%, raw pool ~0.90–1.05×, zero-weight < ~50%.
Payouts rounded to 0.1× (10¢ steps) for Stake RGS upload.
