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
| Run sims (default 150k base, 0 bonus, scale **0.0007**) | `./scripts/run_sims_on_nuc.sh` |
| Custom counts / scale | `./scripts/run_sims_on_nuc.sh 150000 0 0.0007` |
| Pull results | `./scripts/pull_library_from_nuc.sh` |
| RTP from pulled CSVs | `./scripts/rtp_from_lookup.sh` |
| Optimization only (after sims; Rust required) | `./scripts/run_optimization_on_nuc.sh` |

**Production FS cap:** default runs use 50 max FS (do not set `KRONOS_UNCAPPED_FS` unless researching tails).

---

## Overnight / background sims (avoid Mac `suspended (tty input)`)

Do **not** rely on `nohup ./scripts/run_sims_on_nuc.sh &` alone from zsh — the inner SSH can suspend.

Use **one SSH** to the NUC and redirect on the Mac:

```bash
cd /Users/evanlegator/math-sdk
nohup ssh nuc "cd math-sdk && powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_clash_kronos_sims.ps1 -SimBase 150000 -SimBonus 0 -PaytableScale 0.0007" \
  > ~/nuc-sim.log 2>&1 </dev/null &
disown
tail -f ~/nuc-sim.log
```

---

## RTP: scale then optimize

1. **Pay ladder:** `PAYTABLE_SCALE` in [`game_config.py`](../games/0_0_clash_kronos_cluster/game_config.py) (default **0.0007**) or override per run (3rd arg to `run_sims_on_nuc.sh`). Tune until unweighted mean from `lookUpTable_base.csv` is roughly **0.8–1.5×** (see `rtp_from_lookup.sh`).
2. **Shippable ~96.5% RTP:** run the Rust optimizer (`RUN_OPTIMIZATION=1`). Weighted tables: `library/publish_files/lookUpTable_base_0.csv`. Verify with `./scripts/rtp_from_lookup.sh` (weighted line vs bet cost **1.0** base, **100.0** bonus).

`run.py` env flags (from `games/0_0_clash_kronos_cluster/`):

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

## NUC paths

| Item | Path |
|------|------|
| Repo | `C:\Users\evanl\math-sdk` |
| Sim output | `games\0_0_clash_kronos_cluster\library\` |
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
| numpy build fail | Use Python 3.12 + `setup_windows.ps1`, not raw 3.14 without wheels |
| Optimization fails (`cargo` not found) | Run `scripts\nuc_install_rust.ps1`; add `%USERPROFILE%\.cargo\bin` to PATH |
| Post-quantum SSH warnings on Mac | Harmless on LAN; optional `WarnWeakCrypto no` under `Host nuc` |
