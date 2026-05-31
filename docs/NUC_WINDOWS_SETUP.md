# NUC (Windows) — long-term math-sdk setup

**Only `math-sdk` on the NUC.** `web-sdk` stays on your Mac.

Mac is where you **edit**; NUC is where you **run sims**. GitHub (`splurgetech/math-sdk`) is the source of truth.

---

## SSH (Mac)

`~/.ssh/config` includes:

```
Host nuc
  HostName 192.168.84.161
  User evanl
  IdentityFile ~/.ssh/winpc
```

Test: `ssh nuc "hostname"`

### IP address (read this once)

`192.168.84.161` is assigned by your **router (DHCP)**. It can change after reboot unless you **reserve** it:

1. Open router admin (often `192.168.84.1` or similar).
2. Find DHCP / “connected devices” → NUC `DESKTOP-DT8I9DF`.
3. **Reserve** IP `192.168.84.161` for the NUC’s MAC address.

If the IP changes, update `HostName` in `~/.ssh/config` or fix the reservation.

---

## One-time NUC bootstrap (fresh git clone + Python 3.12 + venv)

On **Mac**, from `math-sdk` (commit & push first):

```bash
chmod +x scripts/*.sh
./scripts/nuc_bootstrap.sh
```

This clones `https://github.com/splurgetech/math-sdk.git` to `C:\Users\evanl\math-sdk`, installs Python 3.12 if needed, runs `setup_windows.ps1` + smoke test.

### One-time Rust (optimization)

On the **NUC** (PowerShell):

```powershell
cd $HOME\math-sdk
powershell -ExecutionPolicy Bypass -File .\scripts\nuc_install_rust.ps1
```

Restart PowerShell or ensure `%USERPROFILE%\.cargo\bin` is on **PATH** for SSH sessions (Windows may need a reboot after winget install).

---

## Daily workflow

| Step | Mac command |
|------|-------------|
| Sync code | `./scripts/sync_to_nuc.sh` |
| Uncommitted Mac changes | `./scripts/sync_to_nuc.sh --local` (tar; use sparingly) |
| Run sims (default 150k base, 0 bonus, scale **1.0**) | `./scripts/run_sims_on_nuc.sh` |
| Custom counts / scale / threads | `./scripts/run_sims_on_nuc.sh 150000 20000 1.0` (set `SIM_THREADS=4` on Windows NUC) |
| Pull results | `./scripts/pull_library_from_nuc.sh` |
| RTP from pulled CSVs | `./scripts/rtp_from_lookup.sh` |
| Optimization only (after sims; Rust required) | **Mac (recommended):** `./scripts/run_optimization.sh` — CPU-heavy, light on RAM. **NUC:** `./scripts/run_optimization_on_nuc.sh` (needs MSVC Build Tools) |

**Production FS cap:** default runs use 50 max FS (do not set `KRONOS_UNCAPPED_FS` unless researching tails).

---

## Overnight / background sims (avoid Mac `suspended (tty input)`)

Do **not** rely on `nohup ./scripts/run_sims_on_nuc.sh &` alone from zsh — the inner SSH can suspend.

Use **one SSH** to the NUC and redirect on the Mac:

```bash
cd /Users/evanlegator/math-sdk
nohup ssh -n nuc "cd math-sdk && powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_clash_kronos_sims.ps1 -SimBase 150000 -SimBonus 0 -PaytableScale 1.0" \
  > ~/nuc-sim.log 2>&1 </dev/null &
disown
tail -f ~/nuc-sim.log
```

---

## RTP: sims on NUC, optimize on Mac (recommended)

1. **Raw sims on NUC** (keeps Mac RAM free): `./scripts/run_sims_on_nuc.sh` — default **full ladder** (`PAYTABLE_SCALE=1.0`), **freegame quota 0.03**, **max 50 FS** (never `KRONOS_UNCAPPED_FS` for publish).
2. **Pull library:** `./scripts/pull_library_from_nuc.sh`
3. **Optimize on Mac:** install [Rust](https://rustup.rs), `cd optimization_program && cargo build --release`, then `./scripts/run_optimization.sh` (or `OPT_MODES=base ./scripts/run_optimization.sh`). Uses CPU; typically fine on a laptop while you work.
4. **Verify:** `./scripts/rtp_from_lookup.sh` — weighted `lookUpTable_base_0.csv` should be ~**0.965**.

NUC optimization is optional (`./scripts/run_optimization_on_nuc.sh`) if MSVC Build Tools are installed.

`run.py` env flags (from `games/0_0_clash_kronos/`):

| Env | Effect |
|-----|--------|
| `RUN_SIMS=0` | Skip book generation (use existing library) |
| `RUN_OPTIMIZATION=1` | Run Rust optimizer after `generate_configs` |
| `RUN_ANALYSIS=1` | PAR sheet (`create_stat_sheet`) |
| `RUN_FORMAT_CHECKS=1` | RGS verification tests |
| `OPT_MODES=base` or `base,bonus` | When `RUN_SIMS=0`, which modes to optimize (default: all modes that have `lookUpTable_<mode>.csv`) |
| `RUST_THREADS=20` | Rust optimizer threads |

Example: sims + optimization + analysis:

```bash
# On NUC in game directory, or via ssh:
RUN_OPTIMIZATION=1 RUN_ANALYSIS=1 SIM_BASE=100000 SIM_BONUS=30000 python run.py
```

---

## Live monitoring (Glances, iPhone / browser)

Headless NUC: simple CPU / RAM / **process list** in Safari (e.g. spare iPhone). Netdata is **disabled** (too busy; Windows free tier is limited).

| Item | Value |
|------|--------|
| URL | **http://192.168.84.161:61208** |
| Auto-start | Scheduled task `GlancesWebNUC` (boot) |
| Install / reinstall | `powershell -ExecutionPolicy Bypass -File C:\Users\evanl\math-sdk\scripts\nuc_install_glances.ps1` |

On the iPhone: Safari → URL above → **Share → Add to Home Screen**.

During sims: sort processes by **CPU** and look for **python**.

---

## Clash Kronos tune pipeline (preferred)

One iteration: sync → NUC sims → pull → Mac optimize → append `library/tuning_log.csv`:

```bash
DIST_FG_QUOTA=0.08 DIST_ZERO_QUOTA=0.10 TAG=quota_fg08_zero10 \
  ./scripts/tune_clash_kronos.sh
```

| Script | Purpose |
|--------|---------|
| `tune_clash_kronos.sh` | Main loop (env: `SIM_BASE`, `SIM_BONUS`, `DIST_*`, `TAG`, `SKIP_NUC`, `SKIP_OPT`) |
| `sweep_fg_quota.sh` | Small matrix: FG 4/5/6% × zero 10/12% |
| `sample_buckets_overnight.sh` | Detached NUC sims + poll + pull + opt (e.g. 40% zero / 10% FG) |
| `run_rtp_report.sh` | Raw + publish RTP, segmented means, zero-weight % |
| `summarize_tuning_log.sh` | Print `library/tuning_log.csv` sorted by raw_base |
| `nuc_sim_worker.ps1` / `start_nuc_sims_detached.ps1` | Run sims on NUC without blocking SSH |
| `nuc_cleanup_sim_host.ps1` | Free RAM/CPU before long sim runs |

**After NUC reboot:** run cleanup, clear `games/0_0_clash_kronos/library/temp_multi_threaded_files/`, then tune.

**Windows sim stalls (~7/10 threads, idle CPU):** reboot NUC, kill stray `python.exe` (not Glances), retry detached worker or `SIM_THREADS=1`.

Legacy / experimental (not needed for normal quota tuning): `overnight_clash_kronos_tune.sh` (3× BR0 variants), `sweep_base_overnight.sh` (16-run Kronos×BR0 matrix).

---

## Sim-host cleanup (free RAM / CPU for sims)

One-shot tune from Mac:

```bash
ssh nuc "powershell -ExecutionPolicy Bypass -File C:/Users/evanl/math-sdk/scripts/nuc_cleanup_sim_host.ps1"
```

Script: `scripts/nuc_cleanup_sim_host.ps1` — High/Ultimate performance power plan, uninstall Netdata, disable telemetry/search/Xbox/OneDrive startup, Intel survey tasks, Game DVR, etc. **Keeps** OpenSSH, Defender, Windows Update, Python 3.12, Rust/MSVC, Glances.

Audit only: `scripts/nuc_audit.ps1`

**After cleanup:** reboot the NUC once. Optionally uninstall unused apps (Chrome, Epic, MindManager, **Python 3.14** if you only use 3.12 for sims).

---

## NUC paths

| Item | Path |
|------|------|
| Repo | `C:\Users\evanl\math-sdk` |
| Sim output | `games\0_0_clash_kronos\library\` |
| Lookup tables | `library\lookup_tables\` |
| Publish (books/LUT) | `library\publish_files\` |

---

## Python

Stake docs recommend **Python ≥ 3.12**. The NUC uses **`py -3.12`** via `scripts\nuc_install_python312.ps1` (winget) when missing.

---

## Troubleshooting

| Issue | Fix |
|--------|-----|
| `Permission denied` SSH | Use `ssh nuc`; check `~/.ssh/winpc` on NUC `authorized_keys` |
| `Not a git repo` on NUC | Run `./scripts/nuc_bootstrap.sh` |
| Sim OOM | Lower bonus sims; run base only: `./scripts/run_sims_on_nuc.sh 150000 0` |
| Sims hang / partial threads | Reboot NUC; `nuc_cleanup_sim_host.ps1`; use `start_nuc_sims_detached.ps1` or `SIM_THREADS=1` |
| `sync_to_nuc.sh --local` slow | Excludes `library/tuning_runs` and `optimization_files` from tar |
| numpy build fail | Use Python 3.12 + `setup_windows.ps1`, not raw 3.14 without wheels |
| Optimization fails (`cargo` not found) | Run `scripts\nuc_install_rust.ps1`; add `%USERPROFILE%\.cargo\bin` to PATH |
| Optimization fails (`link.exe` not found) | Run `scripts\nuc_install_rust.ps1` (installs VS 2022 Build Tools + C++ via winget). Reboot NUC if winget asks. Then `cd optimization_program` and `cargo build --release`. `run_opt_on_nuc.ps1` prepends MSVC to PATH for SSH. |
| Post-quantum SSH warnings on Mac | Harmless on LAN; optional `WarnWeakCrypto no` under `Host nuc` |
| Glances not loading from phone | Rerun `nuc_install_glances.ps1` on NUC (opens TCP 61208, starts `GlancesWebNUC` task) |
