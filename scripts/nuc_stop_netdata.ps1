# Disable Netdata only (optional; nuc_install_glances.ps1 does this too).
$nd = Get-Service -Name 'Netdata' -ErrorAction SilentlyContinue
if ($nd) {
    if ($nd.Status -eq 'Running') { Stop-Service Netdata -Force }
    Set-Service Netdata -StartupType Disabled
    Write-Host 'Netdata stopped and disabled.'
} else {
    Write-Host 'Netdata not installed.'
}
