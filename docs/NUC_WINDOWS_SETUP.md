# NUC (Windows) — Math SDK only

You only need **math-sdk** on the NUC for RTP sims. **web-sdk** stays on your Mac.

I (Cursor) cannot SSH into your NUC from the cloud. Use this guide + the scripts in `scripts/` to get an identical, correct setup.

---

## What you need on the NUC

| Install | Why |
|--------|-----|
| **Python 3.12+** | [python.org](https://www.python.org/downloads/) — check **“Add python.exe to PATH”** |
| **Git for Windows** | Clone repo + `requirements.txt` git dependency |
| **OpenSSH Server** (optional) | So your Mac can `ssh` / `scp` without a USB stick |

You do **not** need Node, pnpm, or web-sdk on the NUC.

---

## Option A — Clone from GitHub (easiest if `main` is up to date)

On the NUC, in **PowerShell**:

```powershell
cd $HOME
git clone https://github.com/splurgetech/math-sdk.git
cd math-sdk
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\scripts\setup_windows.ps1
.\scripts\smoke_test_windows.ps1
```

If you use another branch:

```powershell
cd $HOME\math-sdk
git fetch origin
git checkout your-branch-name
.\scripts\setup_windows.ps1
```

---

## Option B — Copy from your Mac (unpushed local changes)

On your **Mac** (replace `NUC_USER` and `NUC_IP`):

```bash
# One-time: exclude venv and generated library bulk
cd /Users/evanlegator/math-sdk
rsync -avz --progress \
  --exclude 'env/' \
  --exclude '.git/' \
  --exclude 'games/*/library/temp_multi_threaded_files/' \
  --exclude 'games/*/library/publish_files/*.zst' \
  ./ NUC_USER@NUC_IP:C:/Users/NUC_USER/math-sdk/
```

Then on the **NUC**:

```powershell
cd $HOME\math-sdk
.\scripts\setup_windows.ps1
```

Or push to GitHub from the Mac and use Option A on the NUC.

---

## Enable SSH on the NUC (optional, recommended)

On the **NUC** (PowerShell **as Administrator**):

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
New-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -DisplayName "OpenSSH Server (sshd)" -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

Find the NUC username: `whoami`  
Find the IP: `ipconfig` (e.g. `192.168.1.50`)

From your **Mac**:

```bash
ssh NUC_USER@NUC_IP
```

First copy of the repo via SCP:

```bash
scp -r /Users/evanlegator/math-sdk NUC_USER@NUC_IP:C:/Users/NUC_USER/
# Then on NUC rename if needed and run setup_windows.ps1
```

---

## Daily use on the NUC

```powershell
cd $HOME\math-sdk
.\env\Scripts\Activate.ps1

# Base-only batch (good first overnight run)
.\scripts\run_clash_kronos_sims.ps1 -SimBase 150000 -SimBonus 0 -PaytableScale 0.003

# Bonus-only on same NUC (run after base, or separate session)
.\scripts\run_clash_kronos_sims.ps1 -SimBase 0 -SimBonus 50000 -PaytableScale 0.003
```

Check mean return (unweighted) after base sims:

```powershell
# In PowerShell from game folder — rough RTP check
$rows = Import-Csv "games\0_0_clash_kronos_cluster\library\lookup_tables\lookUpTable_base.csv" -Header id,weight,payout
$mean = ($rows.payout | Measure-Object -Average).Average
Write-Host "Mean payoutMultiplier (cents): $mean ; RTP fraction ~ $($mean/100)"
```

Copy `library\` back to the Mac when done (Finder share, `scp`, or git commit + push from NUC if you use a branch).

---

## Rust (only for optimization later)

Sims (`run.py`) do **not** need Rust. When you enable `run_optimization: True`:

1. Install Rust: https://rustup.rs/ (Windows MSVC toolchain)
2. Restart PowerShell, then run optimization from repo per `run.py`

---

## Troubleshooting

| Problem | Fix |
|--------|-----|
| `python` not found | Reinstall Python with **Add to PATH**; try `py -3.12` |
| `ExecutionPolicy` blocks scripts | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `pip install` fails on git URL | Install **Git for Windows**; reopen PowerShell |
| Process **Killed** / out of memory | Lower `-SimBonus`; run base and bonus in separate runs |
| `num_sims/(batch*threads)` error | Use sim counts divisible by `10 * 50000` or lower `batching_size` in `run.py` |
| Very slow | Normal on 2017 NUC; run overnight |

---

## Repo reminder

| Repo | NUC? | Purpose |
|------|------|---------|
| **math-sdk** | Yes | `run.py`, RTP, books, lookups |
| **web-sdk** | No | Storybook / frontend on Mac only |

Fixture export (`export_storybook_fixtures.py`) can run on the Mac after you copy `library/` back.
