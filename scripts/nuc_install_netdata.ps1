# Install Netdata on Windows NUC (silent, LAN dashboard on :19999).
# Run via SSH: powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\evanl\math-sdk\scripts\nuc_install_netdata.ps1
#Requires -RunAsAdministrator

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$msi = Join-Path $env:TEMP 'netdata-x64.msi'
$url = 'https://github.com/netdata/netdata/releases/latest/download/netdata-x64.msi'

Write-Host "=== Netdata install ==="

if (-not (Get-Service -Name 'Netdata' -ErrorAction SilentlyContinue)) {
    Write-Host "Downloading $url ..."
    Invoke-WebRequest -Uri $url -OutFile $msi
    Write-Host 'Running msiexec (silent)...'
    $proc = Start-Process -FilePath 'msiexec.exe' -ArgumentList '/qn', '/i', $msi, '/norestart' -Wait -PassThru
    if ($proc.ExitCode -ne 0) {
        throw "msiexec failed with exit code $($proc.ExitCode)"
    }
    Write-Host 'MSI install complete.'
} else {
    Write-Host 'Netdata service already exists; skipping MSI.'
}

$svc = Get-Service -Name 'Netdata' -ErrorAction SilentlyContinue
if (-not $svc) {
    throw 'Netdata service not found after install.'
}

if ($svc.Status -ne 'Running') {
    Start-Service Netdata
}
Set-Service Netdata -StartupType Automatic
Write-Host "Service: $($svc.Status) (startup Automatic)"

# Allow LAN access on default port
$ruleName = 'Netdata Dashboard (TCP 19999)'
$existing = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
if (-not $existing) {
    New-NetFirewallRule -DisplayName $ruleName `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 19999 `
        -Action Allow `
        -Profile Any | Out-Null
    Write-Host 'Firewall rule added for TCP 19999 (all profiles; Wi-Fi is often Public).'
} else {
    Write-Host 'Firewall rule already present.'
}

# Bind dashboard to all interfaces (not only localhost)
$confCandidates = @(
    "$env:ProgramFiles\Netdata\etc\netdata\netdata.conf",
    "${env:ProgramFiles(x86)}\Netdata\etc\netdata\netdata.conf",
    "$env:ProgramData\Netdata\etc\netdata\netdata.conf"
)
$conf = $confCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($conf) {
    $text = Get-Content -Raw -Path $conf
    if ($text -notmatch '(?m)^\s*bind to\s*=') {
        Add-Content -Path $conf -Value "`n[web]`n    bind to = *`n"
        Write-Host "Added [web] bind to = * in $conf"
        Restart-Service Netdata
    } elseif ($text -match 'bind to\s*=\s*localhost') {
        $text = $text -replace 'bind to\s*=\s*localhost', 'bind to = *'
        Set-Content -Path $conf -Value $text -NoNewline
        Write-Host "Updated bind to = * in $conf"
        Restart-Service Netdata
    } else {
        Write-Host "netdata.conf already allows non-localhost bind: $conf"
    }
} else {
    Write-Host 'WARN: netdata.conf not found; default bind may be localhost only.'
}

Start-Sleep -Seconds 3
try {
    $r = Invoke-WebRequest -Uri 'http://127.0.0.1:19999/api/v1/info' -UseBasicParsing -TimeoutSec 10
    Write-Host "Local API OK: HTTP $($r.StatusCode)"
} catch {
    Write-Host "WARN: local API check failed: $_"
}

$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
        $_.IPAddress -notlike '127.*' -and
        $_.IPAddress -notlike '169.254.*' -and
        $_.PrefixOrigin -eq 'Dhcp'
    } | Select-Object -First 1).IPAddress
if (-not $ip) {
    $ip = '192.168.84.161'
}
Write-Host ''
Write-Host "=== Done ==="
Write-Host "iPhone Safari: http://${ip}:19999"
Write-Host 'Add to Home Screen for a full-screen shortcut.'
