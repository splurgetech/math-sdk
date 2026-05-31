# Fix Netdata LAN access (firewall + bind). Run as Administrator on NUC.
$ErrorActionPreference = 'Stop'

$ruleName = 'Netdata Dashboard (TCP 19999)'
Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue | Remove-NetFirewallRule
New-NetFirewallRule -DisplayName $ruleName `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 19999 `
    -Action Allow `
    -Profile Any | Out-Null
Write-Host 'Firewall: TCP 19999 allowed on all profiles.'

$conf = 'C:\Program Files\Netdata\etc\netdata\netdata.conf'
if (Test-Path $conf) {
    $lines = Get-Content $conf
    $webIdx = [array]::IndexOf($lines, '[web]')
    if ($webIdx -ge 0) {
        $found = $false
        for ($i = $webIdx + 1; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -match '^\s*\[') { break }
            if ($lines[$i] -match '^\s*bind to\s*=') {
                $lines[$i] = '    bind to = *'
                $found = $true
                break
            }
        }
        if (-not $found) {
            $lines = $lines[0..$webIdx] + '    bind to = *' + $lines[($webIdx + 1)..($lines.Count - 1)]
        }
    } else {
        $lines += ''
        $lines += '[web]'
        $lines += '    bind to = *'
    }
    Set-Content -Path $conf -Value $lines
    Write-Host "Updated $conf"
}

Restart-Service Netdata -Force
Start-Sleep -Seconds 4

foreach ($url in @('http://127.0.0.1:19999/api/v1/info', 'http://192.168.84.161:19999/api/v1/info')) {
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
        Write-Host "OK $url -> $($r.StatusCode)"
    } catch {
        Write-Host "FAIL $url -> $($_.Exception.Message)"
    }
}

Get-NetConnectionProfile | Format-Table InterfaceAlias, NetworkCategory -AutoSize
