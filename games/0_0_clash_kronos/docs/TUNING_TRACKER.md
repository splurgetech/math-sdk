# Clash of Kronos — tuning tracker (autonomous)

## Goals (middle ground)

| Metric | Target | Notes |
|--------|--------|--------|
| Publish base RTP | **96.5%** | Stake submit |
| Publish FS weight | **~0.5%** (`hr=200`) | Do not change unless opt fails |
| `raw_base` (sim pool) | **~0.9–1.05×** per readme | Was ~69× at 40z/10fg |
| `zero_wt_base_pct` | **&lt; ~50%** | Was ~71%; player feel |
| Features | Rare but meaningful | FS quota + opt fences, not overpowered tail |
| Small wins | Fair, not stripped | Avoid only cutting low tiers |

## Mechanics (tone-down v1 defaults)

| Knob | Value |
|------|--------|
| Kronos wild | 10% |
| Kronos bar threshold | 25 |
| Hidden mult coverage | 10–50%, triangular mode 27.5% |
| FS entry | 3→8, 4→10, 5→12 |
| Retrigger | +3 flat, max 3, max 21 FS/bonus |
| Paying symbols | H1–H3, L1–**L5** |

## Reference (Stake `0_0_cluster` sample)

- **8 paying symbols**, cluster pays baked in `game_config` (no `PAYTABLE_SCALE`)
- Opt fences: `basegame` hr=3.5, `freegame` hr=200, zero fence rtp=0
- Distribution quotas in sample: ~10% FG, ~10% zero (not 40%)

## Runs

| Tag | Status | FG | Zero | Notes |
|-----|--------|-----|------|--------|
| `sample_buckets_40z10fg` | done | 10% | 40% | raw 69.16×, zero_wt 71% |
| `bundle_b` | done | 6% | 30% | scale 0.8, caps, cool BR0 |
| `cool_k24_w013_20k` | done | — | — | raw 31.58×, zero_wt 71% |
| `gb_pay_1.0` | **failed** | 10% | 10% | thread timeout 7200s; 6/8 base threads |
| `tone_down_v1` | done | 8% | 28% | raw 36.87×, zero_wt 71%; NUC sim ~43s after wincap fix |

## Sim hang fix (2026-06-01)

**Symptom:** NUC sim threads timed out at 7200s (often thread 0); only 6–7/8 base threads finished.

**Cause:** `wincap` criteria books require `final_win == win_criteria` (10,000×). Toned paytable + WCAP strips almost never hit that naturally, so `while self.repeat` never exited (not a tumble/Kronos infinite loop).

**Fix:** [`game_override.py`](../game_override.py) `_force_wincap_book()` — after free spins trigger on a wincap book, stamp exact max-win payout for the optimizer fence. See `diagnose_sim_hang.py` to repro per-criteria.

## Next candidates (if needed)

- **opt-only** on `tone_down_v1` library if `zero_wt` still ~71%
- **opt fence** tweak in `game_optimization.py` if feel target missed

Log: `library/tuning_log.csv`  
NUC runner: `./scripts/run_tone_down_nuc.sh`
