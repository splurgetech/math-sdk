# Install Rust toolchain on Windows NUC (required for math-sdk optimization).
$ErrorActionPreference = "Stop"

if (Get-Command cargo -ErrorAction SilentlyContinue) {
    Write-Host "Rust already on PATH:"
    cargo --version
    exit 0
}

Write-Host "Installing Rust via winget (Rustlang.Rustup) ..."
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget not found. Install Rust from https://rustup.rs/"
    exit 1
}

winget install Rustlang.Rustup --accept-package-agreements --accept-source-agreements

$cargoBin = Join-Path $env:USERPROFILE ".cargo\bin"
if (-not (Test-Path (Join-Path $cargoBin "cargo.exe"))) {
    Write-Host "Install finished; open a new PowerShell or add $cargoBin to PATH, then run: cargo --version"
    exit 0
}

& (Join-Path $cargoBin "cargo.exe") --version

# Rust on Windows needs MSVC (link.exe). Install Build Tools if missing.
$vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
$hasLink = $false
if (Test-Path $vswhere) {
    $vsRoot = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath 2>$null
    if ($vsRoot -and (Test-Path (Join-Path $vsRoot "VC\Tools\MSVC"))) { $hasLink = $true }
}
if (-not $hasLink) {
    Write-Host "Installing Visual Studio 2022 Build Tools (C++ workload) via winget ..."
    winget install -e --id Microsoft.VisualStudio.2022.BuildTools `
        --accept-package-agreements --accept-source-agreements `
        --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
    Write-Host "If winget reports a reboot, restart the NUC once, then run: cd optimization_program; cargo build --release"
} else {
    Write-Host "MSVC Build Tools already present."
}

Write-Host "Rust ready. Ensure $cargoBin is on PATH for non-interactive SSH sessions."
Write-Host "Optimization uses scripts/run_opt_on_nuc.ps1 (adds MSVC to PATH for cargo)."
