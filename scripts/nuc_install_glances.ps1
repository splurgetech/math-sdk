# Stop Netdata; install Glances web UI for LAN monitoring (iPhone-friendly).
# Run: powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\evanl\math-sdk\scripts\nuc_install_glances.ps1
#Requires -RunAsAdministrator

$ErrorActionPreference = 'Stop'
$GlancesPort = 61208
$TaskName = 'GlancesWebNUC'

Write-Host '=== Stop Netdata ==='
$netdata = Get-Service -Name 'Netdata' -ErrorAction SilentlyContinue
if ($netdata) {
    if ($netdata.Status -eq 'Running') { Stop-Service Netdata -Force }
    Set-Service Netdata -StartupType Disabled
    Write-Host 'Netdata service stopped and disabled.'
} else {
    Write-Host 'Netdata service not found (already removed).'
}

Write-Host '=== Install Glances (web) ==='
$py = 'py'
$pyArgs = @('-3.12', '-m', 'pip', 'install', '--upgrade', 'glances[web]')
& $py @pyArgs
if ($LASTEXITCODE -ne 0) { throw "pip install failed with exit $LASTEXITCODE" }

# Resolve glances executable (Scripts dir for py launcher)
$scriptsDir = & py -3.12 -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$glancesExe = Join-Path $scriptsDir 'glances.exe'
if (-not (Test-Path $glancesExe)) {
    $glancesExe = 'glances'
}

Write-Host "Glances: $glancesExe"

Write-Host '=== Firewall (TCP 61208) ==='
$ruleName = 'Glances Web (TCP 61208)'
Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue | Remove-NetFirewallRule
New-NetFirewallRule -DisplayName $ruleName `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort $GlancesPort `
    -Action Allow `
    -Profile Any | Out-Null

Write-Host '=== Scheduled task (start at boot) ==='
$action = New-ScheduledTaskAction -Execute $glancesExe -Argument "-w --bind 0.0.0.0 --port $GlancesPort"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings | Out-Null
Start-ScheduledTask -TaskName $TaskName
Write-Host "Task '$TaskName' registered and started."

Start-Sleep -Seconds 5

$lanIp = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
        $_.IPAddress -notlike '127.*' -and
        $_.IPAddress -notlike '169.254.*' -and
        $_.PrefixOrigin -eq 'Dhcp'
    } | Select-Object -First 1).IPAddress
if (-not $lanIp) { $lanIp = '192.168.84.161' }

foreach ($url in @("http://127.0.0.1:$GlancesPort", "http://${lanIp}:$GlancesPort")) {
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 15
        Write-Host "OK $url -> HTTP $($r.StatusCode)"
    } catch {
        Write-Host "WARN $url -> $($_.Exception.Message)"
    }
}

Write-Host ''
Write-Host '=== Done ==='
Write-Host "iPhone Safari: http://${lanIp}:$GlancesPort"
Write-Host 'Processes are listed on the main view; sort/filter for python during sims.'
