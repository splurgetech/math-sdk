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

---

## Daily workflow

| Step | Mac command |
|------|-------------|
| Sync code | `./scripts/sync_to_nuc.sh` |
| Uncommitted Mac changes | `./scripts/sync_to_nuc.sh --local` (tar; use sparingly) |
| Run sims (default 150k base, 0 bonus) | `./scripts/run_sims_on_nuc.sh` |
| Custom counts | `./scripts/run_sims_on_nuc.sh 150000 0 0.003` |
| Pull results | `./scripts/pull_library_from_nuc.sh` |

**RTP tuning:** adjust `PAYTABLE_SCALE` (3rd arg to `run_sims_on_nuc.sh`). **Optimization** (weighted lookup to 96.5%) is a later step on Mac or NUC after Rust is installed.

**Production FS cap:** default runs use 50 max FS (do not set `KRONOS_UNCAPPED_FS` unless researching tails).

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
