# Quick sim smoke test for Clash Kronos Cluster on Windows NUC
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$venvPy = Join-Path $RepoRoot "env\Scripts\python.exe"
$GameDir = Join-Path $RepoRoot "games\0_0_clash_kronos_cluster"

if (-not (Test-Path $venvPy)) {
    Write-Host "Run .\scripts\setup_windows.ps1 first." -ForegroundColor Red
    exit 1
}

Set-Location $GameDir
$env:SIM_BASE = "200"
$env:SIM_BONUS = "0"
# Omit KRONOS_UNCAPPED_FS for production-like 50 FS cap

Write-Host "Running 200 base sims (no bonus) ..." -ForegroundColor Cyan
& $venvPy run.py

$lut = Join-Path $GameDir "library\lookup_tables\lookUpTable_base.csv"
if (Test-Path $lut) {
    $lines = (Get-Content $lut | Measure-Object -Line).Lines
    Write-Host "OK: $lut ($lines lines)" -ForegroundColor Green
} else {
    Write-Host "FAIL: lookup table not created" -ForegroundColor Red
    exit 1
}
