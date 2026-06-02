# Clash of Kronos

6×6 cluster pays (5+). Hidden cell mults (1×–5× / 10× / 20× only, 10–50% of cells, peaked ~25–30%) collect into additive global mult.
Kronos bar (25 organic win cells per spin; resets each spin incl. FS) → symbol transform or W wild (10%).

Symbols: H1–H3 / L1–L5 pays, S scatter, W wild (Kronos only).

FS: 3→8, 4→10, 5→12 spins; retriggers +3 flat (max 3); cap 21 FS spins/bonus; forced entry ~89%×3 / 10%×4 / 1%×5; max 5 SC; 3 retrigger cap then FR0_NS.
Bonus buy: 100×, ≥3 SC (weighted toward 3); FS reels FR0_BUY / FR0_BUY_NS (tamer than organic FR0).

RTP target 96–97%, wincap 10,000×.

Fixtures: python run_fixtures.py && python export_storybook_fixtures.py
Production sims: NUC via `./scripts/run_tone_down_nuc.sh` or `./scripts/run_sims_on_nuc.sh`.
Reel dilution (L5): `python dilute_reels_l5.py` in this directory.
Distribution quotas (env): DIST_FG_QUOTA default 0.08, DIST_ZERO_QUOTA default 0.25, wincap 0.001.
Tone-down batch: `./scripts/run_tone_down_nuc.sh` — scale 0.8, 28% zero / 8% FG, Kronos bar 25 / wild 10%.
Tuning log: library/tuning_log.csv — target publish 96.5%, raw pool ~0.90–1.05×, zero-weight < ~50%.
Payouts rounded to 0.1× (10¢ steps) for Stake RGS upload.
