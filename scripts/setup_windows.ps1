# Math SDK — Windows NUC setup (no Make required)
# Run from repo root in PowerShell:
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
#   .\scripts\setup_windows.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "=== Math SDK Windows setup ===" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot"

function Test-Python312([string]$Exe, [string[]]$Args = @()) {
    try {
        $ver = & $Exe @Args -c "import sys; print(sys.version_info[:2])" 2>$null
        if ($ver -match "3,\s*1[2-9]" -or $ver -match "3,\s*[2-9]\d") { return $true }
    } catch {}
    return $false
}

$pyCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    # Prefer a launcher that can actually create a venv (3.12 entry may exist but be uninstalled).
    foreach ($args in @(@("-3.12"), @("-3"))) {
        if (Test-Python312 "py" $args) {
            $probe = Join-Path $env:TEMP "mathsdk_venv_probe"
            Remove-Item -Recurse -Force $probe -ErrorAction SilentlyContinue
            & py @args -m venv $probe 2>$null
            if (Test-Path (Join-Path $probe "Scripts\python.exe")) {
                Remove-Item -Recurse -Force $probe -ErrorAction SilentlyContinue
                $pyCmd = @("py") + $args
                break
            }
            Remove-Item -Recurse -Force $probe -ErrorAction SilentlyContinue
        }
    }
}
if (-not $pyCmd -and (Get-Command python -ErrorAction SilentlyContinue)) {
    if (Test-Python312 "python") { $pyCmd = @("python") }
}

if (-not $pyCmd) {
    Write-Host "ERROR: Python 3.12+ required. Install from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "  Check 'Add python.exe to PATH' during install."
    exit 1
}

Write-Host "Using: $($pyCmd -join ' ')" -ForegroundColor Green

$venv = Join-Path $RepoRoot "env"
if (-not (Test-Path $venv)) {
    Write-Host "Creating virtualenv at env\ ..."
    & $pyCmd[0] $pyCmd[1..($pyCmd.Length-1)] -m venv env
}

$venvPy = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Host "ERROR: venv python not found at $venvPy" -ForegroundColor Red
    exit 1
}

Write-Host "Upgrading pip ..."
& $venvPy -m pip install --upgrade pip

Write-Host "Installing requirements (needs Git if stakeengine git dep is used) ..."
& $venvPy -m pip install -r requirements.txt

Write-Host "Installing math-sdk in editable mode ..."
& $venvPy -m pip install -e .

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Green
Write-Host "Activate before sims:"
Write-Host "  .\env\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Smoke test:"
Write-Host "  .\scripts\smoke_test_windows.ps1"
