# Run Clash Kronos sims on Windows NUC
# Usage examples:
#   .\scripts\run_clash_kronos_sims.ps1 -SimBase 50000 -SimBonus 0
#   .\scripts\run_clash_kronos_sims.ps1 -SimBase 0 -SimBonus 20000
#   .\scripts\run_clash_kronos_sims.ps1 -SimBase 150000 -SimBonus 50000 -PaytableScale 0.003

param(
    [int]$SimBase = 50000,
    [int]$SimBonus = 0,
    [string]$PaytableScale = "1.0",
    [string]$DistFgQuota = "",
    [string]$DistZeroQuota = "",
    [string]$KronosWildProb = "",
    [string]$KronosBarThreshold = "",
    [int]$SimThreads = 0,
    [switch]$UncappedFs
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$venvPy = Join-Path $RepoRoot "env\Scripts\python.exe"
$GameDir = Join-Path $RepoRoot "games\0_0_clash_kronos"

Get-CimInstance Win32_Process -Filter "name='python.exe'" |
    Where-Object { $_.CommandLine -match 'run\.py' -and $_.CommandLine -notmatch 'glances' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

if (-not (Test-Path $venvPy)) {
    Write-Host "Run .\scripts\setup_windows.ps1 first." -ForegroundColor Red
    exit 1
}

$env:SIM_BASE = "$SimBase"
$env:SIM_BONUS = "$SimBonus"
if ($PaytableScale) { $env:PAYTABLE_SCALE = $PaytableScale }
if ($DistFgQuota) { $env:DIST_FG_QUOTA = $DistFgQuota }
if ($DistZeroQuota) { $env:DIST_ZERO_QUOTA = $DistZeroQuota }
if ($KronosWildProb) { $env:KRONOS_WILD_PROB = $KronosWildProb }
if ($KronosBarThreshold) { $env:KRONOS_BAR_THRESHOLD = $KronosBarThreshold }
if ($UncappedFs) { $env:KRONOS_UNCAPPED_FS = "1" } else { Remove-Item Env:KRONOS_UNCAPPED_FS -ErrorAction SilentlyContinue }

if ($SimThreads -gt 0) {
    $env:SIM_THREADS = "$SimThreads"
} elseif (-not $env:SIM_THREADS) {
  # Windows spawn multiprocessing is flaky at 10 workers; 4 is reliable on the NUC.
    if ($IsWindows -or $env:OS -match "Windows") {
        $env:SIM_THREADS = "4"
    } else {
        $env:SIM_THREADS = "10"
    }
}
$env:PYTHONUNBUFFERED = "1"
$env:RUN_SIMS = "1"
$env:RUN_OPTIMIZATION = "0"
$env:RUN_ANALYSIS = "0"
$env:RUN_FORMAT_CHECKS = "0"

Set-Location $GameDir
Write-Host "SIM_BASE=$SimBase SIM_BONUS=$SimBonus SIM_THREADS=$($env:SIM_THREADS) PAYTABLE_SCALE=$($env:PAYTABLE_SCALE) DIST_FG=$($env:DIST_FG_QUOTA) DIST_ZERO=$($env:DIST_ZERO_QUOTA) KRONOS_WILD=$($env:KRONOS_WILD_PROB) KRONOS_BAR=$($env:KRONOS_BAR_THRESHOLD) (NUC sims only)" -ForegroundColor Cyan
& $venvPy run.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Done. Lookups: $GameDir\library\lookup_tables\" -ForegroundColor Green
