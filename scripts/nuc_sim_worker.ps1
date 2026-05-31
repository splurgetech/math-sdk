# Runs Clash Kronos sims on NUC with logging. Writes library/nuc_sim.done on success.
param(
    [int]$SimBase = 150000,
    [int]$SimBonus = 20000,
    [string]$PaytableScale = "1.0",
    [string]$DistFgQuota = "",
    [string]$DistZeroQuota = "",
    [string]$SimThreads = "10"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$GameDir = Join-Path $RepoRoot "games\0_0_clash_kronos"
$LibDir = Join-Path $GameDir "library"
$venvPy = Join-Path $RepoRoot "env\Scripts\python.exe"
$log = Join-Path $LibDir "nuc_sim.log"
$done = Join-Path $LibDir "nuc_sim.done"
$fail = Join-Path $LibDir "nuc_sim.failed"

Remove-Item $done, $fail -ErrorAction SilentlyContinue
"=== nuc_sim_worker start $(Get-Date -Format o) ===" | Out-File $log -Encoding utf8

Get-CimInstance Win32_Process -Filter "name='python.exe'" |
    Where-Object { $_.CommandLine -match 'run\.py' -and $_.CommandLine -notmatch 'glances' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

$tempDir = Join-Path $LibDir "temp_multi_threaded_files"
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force (Join-Path $tempDir "*") -ErrorAction SilentlyContinue
}

$env:SIM_BASE = "$SimBase"
$env:SIM_BONUS = "$SimBonus"
$env:SIM_THREADS = "$SimThreads"
$env:PAYTABLE_SCALE = $PaytableScale
if ($DistFgQuota) { $env:DIST_FG_QUOTA = $DistFgQuota }
if ($DistZeroQuota) { $env:DIST_ZERO_QUOTA = $DistZeroQuota }
$env:RUN_SIMS = "1"
$env:RUN_OPTIMIZATION = "0"
$env:RUN_ANALYSIS = "0"
$env:RUN_FORMAT_CHECKS = "0"
$env:PYTHONUNBUFFERED = "1"

Set-Location $GameDir
try {
    & $venvPy run.py 2>&1 | Tee-Object -FilePath $log -Append
    if ($LASTEXITCODE -ne 0) { throw "run.py exit $LASTEXITCODE" }
    "=== nuc_sim_worker ok $(Get-Date -Format o) ===" | Tee-Object -FilePath $log -Append
    "ok" | Out-File $done -Encoding ascii
} catch {
    "=== FAILED: $_ $(Get-Date -Format o) ===" | Tee-Object -FilePath $log -Append
    "$_" | Out-File $fail -Encoding ascii
    exit 1
}
