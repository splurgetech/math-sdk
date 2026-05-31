# Audit NUC for cleanup (read-only).
$ErrorActionPreference = 'Continue'

Write-Host '=== OS ==='
(Get-CimInstance Win32_OperatingSystem).Caption
Write-Host ''

Write-Host '=== Power plan ==='
powercfg /getactivescheme
Write-Host ''

Write-Host '=== RAM ==='
$os = Get-CimInstance Win32_OperatingSystem
$usedPct = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize * 100, 1)
Write-Host "$usedPct% used ($([math]::Round($os.FreePhysicalMemory/1MB,1)) GB free)"
Write-Host ''

Write-Host '=== Top processes (working set) ==='
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 20 Name, Id,
    @{ N = 'MB'; E = { [math]::Round($_.WorkingSet64 / 1MB, 0) } } | Format-Table -AutoSize

Write-Host '=== Installed (user-relevant) ==='
@(
    'Netdata*', 'Glances*', 'Python*', 'Rust*', 'Microsoft Visual Studio*',
    'OneDrive', 'Xbox*', 'Spotify*', 'Steam*', 'Discord*', 'Google Chrome*',
    'Microsoft Edge*', 'Teams*', 'Slack*'
) | ForEach-Object {
    Get-Package -Name $_ -ErrorAction SilentlyContinue | Select-Object Name, Version
} | Format-Table -AutoSize

Write-Host '=== Services: Running, not core (sample) ==='
$skip = '^(RpcSs|DcomLaunch|EventLog|Schedule|Winmgmt|LanmanServer|LanmanWorkstation|Dhcp|Dnscache|mpssvc|w32time|SamSs|LSM|Power|ProfSvc|UserManager|CoreMessagingRegistrar|StateRepository|SystemEventsBroker|BrokerInfrastructure|PlugPlay|Power|RpcEptMapper|LSM|nsi|BFE|CryptSvc|KeyIso|Netlogon|SamSs|EventSystem|FontCache|Themes|AudioSrv|Spooler|W32Time|WinRM|ssh-agent|sshd|OpenSSH)'
Get-Service | Where-Object {
    $_.Status -eq 'Running' -and
    $_.Name -notmatch $skip -and
    $_.DisplayName -notmatch 'Windows|Microsoft|Intel|AMD|NVIDIA|Realtek|Hyper-V|WLAN|Bluetooth|Print|Fax|Update|Defender|Security|Telemetry|Diagnostic|Xbox|Game|OneDrive|Store|Search|Spotlight|Widgets|Copilot'
} | Sort-Object DisplayName | Select-Object Name, DisplayName, StartType | Format-Table -AutoSize

Write-Host '=== Startup commands ==='
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command | Format-Table -Wrap

Write-Host '=== Scheduled tasks (enabled, non-Microsoft path) ==='
Get-ScheduledTask | Where-Object {
    $_.State -ne 'Disabled' -and $_.TaskPath -notlike '\Microsoft*'
} | Select-Object TaskName, TaskPath, State | Format-Table -AutoSize

Write-Host '=== Netdata / Glances ==='
Get-Service Netdata -ErrorAction SilentlyContinue | Format-List Name, Status, StartType
Get-ScheduledTask GlancesWebNUC -ErrorAction SilentlyContinue | Format-List TaskName, State
