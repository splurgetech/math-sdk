# Run Rust optimization on NUC (no new sims). Requires books + lookUpTable_*.csv from a prior sim run.
# Optional: -OptModes "base" or "base,bonus" (default: optimize every mode that has a base lookup file).
param(
    [string]$OptModes = ""
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$gameDir = Join-Path $repo "games\0_0_clash_kronos"
$py = Join-Path $repo "env\Scripts\python.exe"

# MSVC link.exe required for `cargo run --release` (non-interactive SSH has no Developer shell PATH).
$vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
if (Test-Path $vswhere) {
    $vsRoot = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath 2>$null
    if ($vsRoot) {
        $linkDir = Get-ChildItem (Join-Path $vsRoot "VC\Tools\MSVC\*\bin\Hostx64\x64\link.exe") -ErrorAction SilentlyContinue |
            Select-Object -First 1 -ExpandProperty DirectoryName
        if ($linkDir) {
            $env:Path = "$linkDir;$env:USERPROFILE\.cargo\bin;$env:Path"
        }
    }
}

Set-Location $gameDir
$env:RUN_SIMS = "0"
$env:RUN_OPTIMIZATION = "1"
$env:SIM_BASE = "0"
$env:SIM_BONUS = "0"
if ($OptModes) {
    $env:OPT_MODES = $OptModes
} else {
    Remove-Item Env:OPT_MODES -ErrorAction SilentlyContinue
}

Write-Host "RUN_SIMS=0 RUN_OPTIMIZATION=1 OPT_MODES=$($env:OPT_MODES)" -ForegroundColor Cyan
& $py run.py
