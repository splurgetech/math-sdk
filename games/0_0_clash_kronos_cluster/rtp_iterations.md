# RTP iteration log (NUC sims, PAYTABLE_SCALE=1.0)

Unweighted RTP = mean of `lookUpTable_base.csv` column 3 ÷ 100 (`./scripts/rtp_from_lookup.sh`).
Weighted ~96.5% comes from Rust optimization on `lookUpTable_base_0.csv` after the pool is sane.

**Do not** tune via `PAYTABLE_SCALE` env (no 0.0007-style hacks). Locked: bar 20, 128× cell cap, 50 FS cap, Kronos strike rules.

| Round | freegame quota | scatter_triggers | Other | SimBase | Unweighted RTP | Notes |
|-------|----------------|------------------|-------|---------|----------------|-------|
| 0 | 0.03 | {3:8,4:2,5:1} | baseline | 50k | **198.42×** | scale 1.0; gate: >>10× → continue distribution tuning |
| 1 | 0.02 | {3:8,4:2,5:1} | — | 50k | **121.99×** | −38% vs R0 |
| 2 | 0.015 | {3:8,4:2,5:1} | — | 50k | **103.83×** | still >>10× |
| 3 | 0.015 | {3:10,4:1,5:1} | — | 50k | **96.82×** | small drop vs R2 |
| 4 | 0.015 | {3:10,4:1,5:1} | 0 quota 0.45 / base 0.45 | 50k | **94.68×** | still >>10× |
| 5 | 0.015 | {3:10,4:1,5:1} | BR0 S halved (40→20) | 50k | **103.44×** | worse than R4 — reverted BR0 |
| — | **best: R4** | same as R4 | no BR0 change | — | **94.68×** | **GATE: still >>10× → major redesign needed**; skip ladder micro-cuts |
| confirm | 0.015 | {3:10,4:1,5:1} | R4 config, BR0 reverted | **150k** | **99.16×** | confirm pool before optimize |
