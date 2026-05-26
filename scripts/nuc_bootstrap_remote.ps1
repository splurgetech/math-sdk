# Run on NUC via: powershell -File C:\Users\evanl\math-sdk\scripts\nuc_bootstrap_remote.ps1
# (Used after git clone exists; Mac script calls this for reset/bootstrap.)
$ErrorActionPreference = "Stop"
$repo = Join-Path $HOME "math-sdk"
$remote = if ($env:NUC_GIT_REMOTE) { $env:NUC_GIT_REMOTE } else { "https://github.com/splurgetech/math-sdk.git" }
$branch = if ($env:NUC_GIT_BRANCH) { $env:NUC_GIT_BRANCH } else { "main" }

if (-not (Test-Path $repo)) {
    git clone $remote $repo
    Set-Location $repo
    git checkout $branch
} else {
    $bak = Join-Path $HOME "math-sdk-library-backup"
    $lib = Join-Path $repo "games\0_0_clash_kronos\library"
    if (Test-Path $lib) {
        Write-Host "Backing up library to $bak"
        Remove-Item -Recurse -Force $bak -ErrorAction SilentlyContinue
        New-Item -ItemType Directory -Force -Path $bak | Out-Null
        Copy-Item -Recurse -Force "$lib\*" $bak\
    }
    Remove-Item -Recurse -Force $repo
    git clone $remote $repo
    Set-Location $repo
    git checkout $branch
}

$bak = Join-Path $HOME "math-sdk-library-backup"
if (Test-Path $bak) {
    $libNew = Join-Path $repo "games\0_0_clash_kronos\library"
    New-Item -ItemType Directory -Force -Path $libNew | Out-Null
    Copy-Item -Recurse -Force "$bak\*" $libNew\
}

& (Join-Path $repo "scripts\nuc_install_python312.ps1")
& (Join-Path $repo "scripts\setup_windows.ps1")
& (Join-Path $repo "scripts\smoke_test_windows.ps1")
