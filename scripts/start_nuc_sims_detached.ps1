# Launch nuc_sim_worker.ps1 in a new process (returns immediately to SSH).
param(
    [int]$SimBase = 150000,
    [int]$SimBonus = 20000,
    [string]$PaytableScale = "1.0",
    [string]$DistFgQuota = "",
    [string]$DistZeroQuota = "",
    [string]$SimThreads = "10"
)

$RepoRoot = Split-Path -Parent $PSScriptRoot
$worker = Join-Path $RepoRoot "scripts\nuc_sim_worker.ps1"
$args = @(
    "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $worker,
    "-SimBase", $SimBase, "-SimBonus", $SimBonus, "-PaytableScale", $PaytableScale,
    "-SimThreads", $SimThreads
)
if ($DistFgQuota) { $args += @("-DistFgQuota", $DistFgQuota) }
if ($DistZeroQuota) { $args += @("-DistZeroQuota", $DistZeroQuota) }

$p = Start-Process -FilePath "powershell.exe" -ArgumentList $args -WorkingDirectory $RepoRoot -WindowStyle Hidden -PassThru
Write-Host "Detached nuc sim worker PID=$($p.Id)"
