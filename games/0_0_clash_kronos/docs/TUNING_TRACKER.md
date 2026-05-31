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

## Reference (Stake `0_0_cluster` sample)

- **8 paying symbols**, cluster pays baked in `game_config` (no `PAYTABLE_SCALE`)
- Opt fences: `basegame` hr=3.5, `freegame` hr=200, zero fence rtp=0
- Distribution quotas in sample: ~10% FG, ~10% zero (not 40%)

## Runs

| Tag | Status | FG | Zero | Notes |
|-----|--------|-----|------|--------|
| `sample_buckets_40z10fg` | done | 10% | 40% | raw 69.16×, zero_wt 71% |
| `bundle_b` | **in progress** | 6% | 30% | scale 0.8, caps, strong cool BR0, Kronos 28/18%, hidden mult cool |

## Next candidates (if needed)

- **bundle_b2**: fix single-cool BR0 only; same quotas as B
- **bundle_c** (balanced): 35% zero, 7% FG, scale 0.85, mild cool BR0, cluster-aligned opt fences
- **opt-only**: align `game_optimization.py` closer to cluster (basegame hr/rtp split)

Log: `library/tuning_log.csv`  
Overnight log: `/tmp/clash_bundle_b.log`
