# Run Clash Kronos sims on Windows NUC
# Usage examples:
#   .\scripts\run_clash_kronos_sims.ps1 -SimBase 50000 -SimBonus 0
#   .\scripts\run_clash_kronos_sims.ps1 -SimBase 0 -SimBonus 20000
#   .\scripts\run_clash_kronos_sims.ps1 -SimBase 150000 -SimBonus 50000 -PaytableScale 0.003

param(
    [int]$SimBase = 50000,
    [int]$SimBonus = 0,
    [string]$PaytableScale = "1.0",
    [switch]$UncappedFs
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$venvPy = Join-Path $RepoRoot "env\Scripts\python.exe"
$GameDir = Join-Path $RepoRoot "games\0_0_clash_kronos"

if (-not (Test-Path $venvPy)) {
    Write-Host "Run .\scripts\setup_windows.ps1 first." -ForegroundColor Red
    exit 1
}

$env:SIM_BASE = "$SimBase"
$env:SIM_BONUS = "$SimBonus"
if ($PaytableScale) { $env:PAYTABLE_SCALE = $PaytableScale }
if ($UncappedFs) { $env:KRONOS_UNCAPPED_FS = "1" } else { Remove-Item Env:KRONOS_UNCAPPED_FS -ErrorAction SilentlyContinue }

Set-Location $GameDir
Write-Host "SIM_BASE=$SimBase SIM_BONUS=$SimBonus PAYTABLE_SCALE=$($env:PAYTABLE_SCALE) KRONOS_UNCAPPED_FS=$($env:KRONOS_UNCAPPED_FS)" -ForegroundColor Cyan
& $venvPy run.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Done. Lookups: $GameDir\library\lookup_tables\" -ForegroundColor Green
