# Tune Windows NUC as a headless Clash Kronos sim host.
# Keeps: SSH, Python/math-sdk, Glances, Rust/MSVC (if installed), networking.
# Run: powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\evanl\math-sdk\scripts\nuc_cleanup_sim_host.ps1
#Requires -RunAsAdministrator

$ErrorActionPreference = 'Continue'
$Log = @()

function Log($msg) {
    Write-Host $msg
    $script:Log += $msg
}

Log '=== NUC sim-host cleanup ==='

# --- Power: High performance, no sleep on AC ---
Log 'Setting High performance power plan...'
$hp = (powercfg /list | Select-String 'High performance|Ultimate Performance').ToString()
if ($hp -match '([a-f0-9-]{36})') {
    powercfg /setactive $Matches[1] | Out-Null
}
powercfg /change standby-timeout-ac 0 | Out-Null
powercfg /change monitor-timeout-ac 0 | Out-Null
powercfg /change hibernate-timeout-ac 0 | Out-Null
powercfg /change disk-timeout-ac 0 | Out-Null
Log 'Power plan: High performance; AC sleep/monitor/hibernate/disk timeouts disabled.'

# --- Stop & disable Netdata (leftover); uninstall MSI if present ---
$nd = Get-Service -Name 'Netdata' -ErrorAction SilentlyContinue
if ($nd) {
    if ($nd.Status -eq 'Running') { Stop-Service Netdata -Force -ErrorAction SilentlyContinue }
    Set-Service Netdata -StartupType Disabled -ErrorAction SilentlyContinue
    Log 'Netdata service stopped and disabled.'
}
$product = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -like 'Netdata*' } | Select-Object -First 1
if ($product -and $product.PSChildName) {
    Log "Uninstalling Netdata: $($product.DisplayName)"
    Start-Process 'msiexec.exe' -ArgumentList '/qn', '/x', $product.PSChildName -Wait -ErrorAction SilentlyContinue
}
Get-NetFirewallRule -DisplayName 'Netdata*' -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue
Log 'Netdata firewall rules removed (if any).'

# --- Disable common consumer bloat services (safe for headless sim box) ---
$disableServices = @(
    'DiagTrack',              # Connected User Experiences and Telemetry
    'dmwappushservice',       # WAP Push
    'WSearch',                # Windows Search indexing
    'SysMain',                # Superfetch (less useful on SSD; can contend with disk)
    'XblAuthManager',
    'XblGameSave',
    'XboxGipSvc',
    'XboxNetApiSvc',
    'OneSyncSvc',             # may be OneDrive sync (name varies by build)
    'MapsBroker',
    'RetailDemo',
    'WMPNetworkSvc',
    'PhoneSvc',
    'TabletInputService',
    'Fax',
    'WbioSrvc',               # Windows Biometric
    'RemoteRegistry',
    'lfsvc',                  # Geolocation
    'SharedAccess',           # ICS (unless you hotspot)
    'WpnService',             # Push notifications
    'ESRV_SVC_QUEENCREEK',    # Intel usage reporting
    'GamingServices',
    'GamingServicesNet',
    'wisvc',                  # Windows Insider
    'WpcMonSvc'               # Parental controls
)
foreach ($name in $disableServices) {
    $svc = Get-Service -Name $name -ErrorAction SilentlyContinue
    if (-not $svc) { continue }
    if ($svc.Status -eq 'Running') {
        Stop-Service -Name $name -Force -ErrorAction SilentlyContinue
    }
    if ($svc.StartType -ne 'Disabled') {
        Set-Service -Name $name -StartupType Disabled -ErrorAction SilentlyContinue
        Log "Disabled service: $name"
    }
}

# OneDrive — stop and remove startup for console user (evanl)
Get-Process -Name OneDrive*, 'OneDrive.Sync.Service' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
$consoleUser = 'evanl'
$userSid = (Get-LocalUser -Name $consoleUser -ErrorAction SilentlyContinue).Sid.Value
if ($userSid) {
    $userRun = "Registry::HKEY_USERS\$userSid\Software\Microsoft\Windows\CurrentVersion\Run"
    foreach ($name in @('OneDrive', 'OneDriveSetup', 'EpicGamesLauncher', 'MMReminderService')) {
        if (Get-ItemProperty -Path $userRun -Name $name -ErrorAction SilentlyContinue) {
            Remove-ItemProperty -Path $userRun -Name $name -Force -ErrorAction SilentlyContinue
            Log "Removed startup: $name"
        }
    }
    $runProps = Get-ItemProperty -Path $userRun -ErrorAction SilentlyContinue
    if ($runProps) {
        $runProps.PSObject.Properties | Where-Object {
            $_.Name -notmatch '^PS' -and [string]$_.Value -match 'msedge\.exe.*win-session-start'
        } | ForEach-Object {
            Remove-ItemProperty -Path $userRun -Name $_.Name -Force -ErrorAction SilentlyContinue
            Log "Removed Edge auto-launch startup: $($_.Name)"
        }
    }
}
Get-ScheduledTask -TaskName '*OneDrive*' -ErrorAction SilentlyContinue | Disable-ScheduledTask -ErrorAction SilentlyContinue | Out-Null
Log 'Disabled OneDrive scheduled tasks.'

# --- Disable non-essential scheduled tasks ---
$disableTasks = @(
    '\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser',
    '\Microsoft\Windows\Application Experience\ProgramDataUpdater',
    '\Microsoft\Windows\Autochk\Proxy',
    '\Microsoft\Windows\Customer Experience Improvement Program\Consolidator',
    '\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip',
    '\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector',
    '\Microsoft\Windows\Feedback\Siuf\DmClient',
    '\Microsoft\Windows\Feedback\Siuf\DmClientOnScenarioDownload',
    '\Microsoft\Windows\Windows Error Reporting\QueueReporting',
    '\Microsoft\Windows\Maps\MapsUpdateTask',
    '\Microsoft\Windows\Shell\FamilySafetyMonitor',
    '\Microsoft\Windows\Maintenance\WinSAT'
)
# Intel / Google updater noise
$extraTasks = @(
    'IntelSURQC-Upgrade-86621605-2a0b-4128-8ffc-15514c247132',
    'IntelSURQC-Upgrade-86621605-2a0b-4128-8ffc-15514c247132-Logon',
    'USER_ESRV_SVC_QUEENCREEK',
    'MicrosoftEdgeUpdateTaskMachineCore',
    'MicrosoftEdgeUpdateTaskMachineUA',
    'GoogleUpdaterTaskSystem149.0.7814.0{07B3F120-51F3-4417-AABF-CBB05924C07F}'
)
foreach ($tn in $extraTasks) {
    $gt = Get-ScheduledTask -TaskName $tn -ErrorAction SilentlyContinue
    if ($gt -and $gt.State -ne 'Disabled') {
        Disable-ScheduledTask -TaskName $tn -ErrorAction SilentlyContinue | Out-Null
        Log "Disabled task: $tn"
    }
}
foreach ($tp in $disableTasks) {
    $t = Get-ScheduledTask -TaskPath (Split-Path $tp -Parent) -TaskName (Split-Path $tp -Leaf) -ErrorAction SilentlyContinue
    if ($t -and $t.State -ne 'Disabled') {
        Disable-ScheduledTask -TaskPath (Split-Path $tp -Parent) -TaskName (Split-Path $tp -Leaf) -ErrorAction SilentlyContinue | Out-Null
        Log "Disabled task: $tp"
    }
}

# --- Visual effects: best performance ---
Log 'Setting visual effects to best performance...'
Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects' -Name 'VisualFXSetting' -Value 2 -Type DWord -ErrorAction SilentlyContinue
$perfKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
Set-ItemProperty -Path $perfKey -Name 'ListviewAlphaSelect' -Value 0 -ErrorAction SilentlyContinue
Set-ItemProperty -Path $perfKey -Name 'TaskbarAnimations' -Value 0 -ErrorAction SilentlyContinue

# --- Game DVR / Xbox Game Bar off (saves CPU during sims) ---
$gameDvr = 'HKCU:\System\GameConfigStore'
if (-not (Test-Path $gameDvr)) { New-Item -Path $gameDvr -Force | Out-Null }
Set-ItemProperty -Path $gameDvr -Name 'GameDVR_Enabled' -Value 0 -Type DWord -Force
$gameBar = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\GameDVR'
if (-not (Test-Path $gameBar)) { New-Item -Path $gameBar -Force | Out-Null }
Set-ItemProperty -Path $gameBar -Name 'AppCaptureEnabled' -Value 0 -Type DWord -Force
Log 'Disabled Game DVR / Game Bar capture.'

# --- Windows tips / suggestions off ---
$content = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager'
if (Test-Path $content) {
    'SystemPaneSuggestionsEnabled', 'SoftLandingEnabled', 'SubscribedContent-338388Enabled',
    'SubscribedContent-310093Enabled', 'SubscribedContent-338389Enabled' | ForEach-Object {
        Set-ItemProperty -Path $content -Name $_ -Value 0 -Type DWord -ErrorAction SilentlyContinue
    }
    Log 'Disabled Content Delivery / suggestions.'
}

# --- Ensure Glances monitoring still runs ---
$glancesTask = Get-ScheduledTask -TaskName 'GlancesWebNUC' -ErrorAction SilentlyContinue
if ($glancesTask) {
    if ($glancesTask.State -eq 'Disabled') { Enable-ScheduledTask -TaskName 'GlancesWebNUC' | Out-Null }
    Start-ScheduledTask -TaskName 'GlancesWebNUC' -ErrorAction SilentlyContinue
    Log 'GlancesWebNUC task OK.'
} else {
    Log 'WARN: GlancesWebNUC task missing — run nuc_install_glances.ps1'
}

# --- Do NOT touch: sshd, OpenSSH, Defender (security), Windows Update service ---
Log ''
Log '=== Left enabled (required) ==='
Log '  OpenSSH, Windows Update, Defender, DHCP/DNS, Glances, Python/Rust toolchain'
Log ''
Log '=== Stopped heavy shell apps (this session) ==='
@('SearchApp', 'PhoneExperienceHost', 'M365Copilot', 'msedge', 'msedgewebview2') | ForEach-Object {
    Get-Process -Name $_ -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}
Log '=== Optional manual steps ==='
Log '  - Uninstall if unused: Chrome, Epic Launcher, MindManager, Python 3.14, Netdata (if MSI remains)'
Log '  - Settings > Apps > Startup: turn off anything still listed'
Log '  - Reboot once after cleanup (recommended)'
Log '  - Long sims: use SSH only; avoid leaving RDP/desktop sessions open'
Log ''
Log '=== Done ==='
