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
Write-Host "Rust ready. Ensure $cargoBin is on PATH for non-interactive SSH sessions."
