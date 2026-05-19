#!/usr/bin/env bash
# One-time (or reset): fresh git clone on NUC + Python 3.12 + venv + smoke test.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/nuc_common.sh"

BRANCH="$(cd "$REPO_ROOT" && git branch --show-current)"
REMOTE="${NUC_GIT_REMOTE:-https://github.com/splurgetech/math-sdk.git}"

cd "$REPO_ROOT"
echo "=== Push Mac main to GitHub (if ahead) ==="
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Commit Mac changes before bootstrap." >&2
  exit 1
fi
AHEAD="$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null || echo 0)"
[[ "$AHEAD" != "0" ]] && git push origin "$BRANCH"

echo "=== Bootstrap NUC repo ==="
nuc_ssh "powershell -NoProfile -ExecutionPolicy Bypass -Command \"
  \\\$repo = Join-Path \\\$HOME '$(nuc_repo_path)';
  \\\$bak = Join-Path \\\$HOME 'math-sdk-library-backup';
  \\\$lib = Join-Path \\\$repo 'games\\0_0_clash_kronos_cluster\\library';
  if (Test-Path \\\$lib) {
    Write-Host 'Backing up library to' \\\$bak;
    Remove-Item -Recurse -Force \\\$bak -ErrorAction SilentlyContinue;
    New-Item -ItemType Directory -Force -Path \\\$bak | Out-Null;
    Copy-Item -Recurse -Force \\\$lib\\* \\\$bak\\;
  }
  if (Test-Path \\\$repo) { Remove-Item -Recurse -Force \\\$repo; }
  git clone $REMOTE \\\$repo;
  Set-Location \\\$repo;
  git checkout $BRANCH;
  if (Test-Path \\\$bak) {
    \\\$libNew = Join-Path \\\$repo 'games\\0_0_clash_kronos_cluster\\library';
    New-Item -ItemType Directory -Force -Path \\\$libNew | Out-Null;
    Copy-Item -Recurse -Force \\\$bak\\* \\\$libNew\\;
  }
\""

echo "=== Install Python 3.12 on NUC (if missing) ==="
nuc_ssh "powershell -NoProfile -ExecutionPolicy Bypass -File \"\$HOME/$(nuc_repo_path)/scripts/nuc_install_python312.ps1\"" || true

echo "=== setup_windows + smoke test ==="
nuc_ssh "powershell -NoProfile -ExecutionPolicy Bypass -Command \"
  Set-Location \\\$HOME\\$(nuc_repo_path);
  .\\scripts\\setup_windows.ps1;
  .\\scripts\\smoke_test_windows.ps1;
\""

echo "=== Bootstrap complete ==="
