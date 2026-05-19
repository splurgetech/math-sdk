# Ensure Python 3.12 is available via py launcher (Stake Engine recommends >= 3.12).
$ErrorActionPreference = "Stop"

function Test-VenvPy([string[]]$PyArgs) {
    $probe = Join-Path $env:TEMP "mathsdk_py312_probe"
    Remove-Item -Recurse -Force $probe -ErrorAction SilentlyContinue
    try {
        & py @PyArgs -m venv $probe 2>$null | Out-Null
    } catch {
        return $false
    }
    $ok = Test-Path (Join-Path $probe "Scripts\python.exe")
    Remove-Item -Recurse -Force $probe -ErrorAction SilentlyContinue
    return $ok
}

if (Test-VenvPy @("-3.12")) {
    Write-Host "Python 3.12 already available (py -3.12)."
    & py -3.12 --version
    exit 0
}

Write-Host "Installing Python 3.12 ..."
if (Get-Command py -ErrorAction SilentlyContinue) {
    py install 3.12 2>$null
}
if (Get-Command winget -ErrorAction SilentlyContinue) {
    winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
} else {
    Write-Host "winget not found. Install Python 3.12 from https://www.python.org/downloads/"
    exit 1
}

if (-not (Test-VenvPy @("-3.12"))) {
    Write-Host "Python 3.12 install finished but py -3.12 venv probe failed. Re-open PowerShell and retry."
    exit 1
}

& py -3.12 --version
Write-Host "Python 3.12 ready."
