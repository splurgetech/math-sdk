# Run Clash Kronos sims on the NUC DETACHED so the job survives SSH disconnect / Mac sleep.
#
# Launcher mode (default): kill stray run.py, clear temp files, write RUNNING sentinel,
#   spawn a hidden detached worker, and return immediately.
# Worker mode (-Worker): run the sims, then write DONE / FAIL to the sentinel.
#
# Sentinel:  games\0_0_clash_kronos\library\.sim_status  (RUNNING|DONE|FAIL <code> <iso8601>)
# Worker log: games\0_0_clash_kronos\library\.sim_run.log
#
# Example (from Mac via ssh):
#   ssh nuc "cd math-sdk && powershell -NoProfile -ExecutionPolicy Bypass -File scripts/nuc_run_detached.ps1 -SimBase 150000 -SimBonus 20000 -MaxWin 5000 -MaxGlobalMult 25"

param(
    [int]$SimBase = 150000,
    [int]$SimBonus = 20000,
    [string]$PaytableScale = "0.8",
    [string]$DistFgQuota = "0.08",
    [string]$DistZeroQuota = "0.35",
    [string]$KronosWildProb = "0.18",
    [string]$KronosBarThreshold = "28",
    [string]$HiddenMultCoverageMax = "0.42",
    [string]$HiddenMultSpikeMult = "0.3",
    [string]$MaxWin = "10000",
    [string]$MaxGlobalMult = "0",
    [int]$SimThreads = 10,
    [switch]$Worker
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$GameDir = Join-Path $RepoRoot "games\0_0_clash_kronos"
$LibDir = Join-Path $GameDir "library"
$StatusFile = Join-Path $LibDir ".sim_status"
$LogFile = Join-Path $LibDir ".sim_run.log"
$SimScript = Join-Path $PSScriptRoot "run_clash_kronos_sims.ps1"

# Ordered list of param name/value pairs, used to (a) build the spawn command line and
# (b) build a hashtable for name-based splatting into the sim script.
$argPairs = [ordered]@{
    SimBase               = $SimBase
    SimBonus              = $SimBonus
    PaytableScale         = $PaytableScale
    DistFgQuota           = $DistFgQuota
    DistZeroQuota         = $DistZeroQuota
    KronosWildProb        = $KronosWildProb
    KronosBarThreshold    = $KronosBarThreshold
    HiddenMultCoverageMax = $HiddenMultCoverageMax
    HiddenMultSpikeMult   = $HiddenMultSpikeMult
    MaxWin                = $MaxWin
    MaxGlobalMult         = $MaxGlobalMult
    SimThreads            = $SimThreads
}

if (-not (Test-Path $LibDir)) { New-Item -ItemType Directory -Path $LibDir -Force | Out-Null }

if (-not $Worker) {
    # --- Launcher: cleanup + spawn detached worker, return immediately. ---
    Get-CimInstance Win32_Process -Filter "name='python.exe'" |
        Where-Object { $_.CommandLine -match 'run\.py' -and $_.CommandLine -notmatch 'glances' } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

    $temp = Join-Path $LibDir "temp_multi_threaded_files"
    if (Test-Path $temp) { Remove-Item "$temp\*" -Recurse -Force -ErrorAction SilentlyContinue }

    Set-Content -Path $StatusFile -Value ("RUNNING " + (Get-Date -Format o)) -Encoding ascii
    "=== launch $(Get-Date -Format o) MaxWin=$MaxWin MaxGlobalMult=$MaxGlobalMult ===" | Out-File -FilePath $LogFile -Encoding ascii

    # Spawn the worker via Win32_Process.Create so it is NOT a child of the sshd
    # session and survives SSH disconnect / Mac sleep (Start-Process gets reaped on logoff).
    $self = $MyInvocation.MyCommand.Path
    $argStr = (($argPairs.GetEnumerator() | ForEach-Object { "-$($_.Key) $($_.Value)" }) -join " ")
    $cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$self`" -Worker $argStr"
    $res = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd; CurrentDirectory = $RepoRoot }
    if ($res.ReturnValue -ne 0 -or -not $res.ProcessId) {
        Set-Content -Path $StatusFile -Value ("FAIL spawn $($res.ReturnValue) " + (Get-Date -Format o)) -Encoding ascii
        Write-Host "FAILED to spawn worker (ReturnValue=$($res.ReturnValue))"
        exit 1
    }
    Write-Host "DETACHED worker PID $($res.ProcessId). Sentinel: $StatusFile"
    exit 0
}

# --- Worker: run sims, record outcome. ---
try {
    Set-Location $RepoRoot
    ("=== worker start $(Get-Date -Format o) pid $PID ===") | Out-File -FilePath $LogFile -Append -Encoding ascii
    $simParams = @{}
    foreach ($kv in $argPairs.GetEnumerator()) { $simParams[$kv.Key] = $kv.Value }
    & $SimScript @simParams *>> $LogFile
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = 0 }
    if ($code -eq 0) {
        Set-Content -Path $StatusFile -Value ("DONE " + (Get-Date -Format o)) -Encoding ascii
    }
    else {
        Set-Content -Path $StatusFile -Value ("FAIL $code " + (Get-Date -Format o)) -Encoding ascii
    }
}
catch {
    ("EXC " + $_.Exception.Message) | Out-File -FilePath $LogFile -Append -Encoding ascii
    Set-Content -Path $StatusFile -Value ("FAIL exception " + (Get-Date -Format o)) -Encoding ascii
}
