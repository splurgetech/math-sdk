#!/usr/bin/env bash
# One-time (or reset): fresh git clone on NUC + Python 3.12 + venv + smoke test.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/nuc_common.sh"

BRANCH="$(cd "$REPO_ROOT" && git branch --show-current)"

cd "$REPO_ROOT"
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Commit Mac changes before bootstrap." >&2
  exit 1
fi
AHEAD="$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null || echo 0)"
[[ "$AHEAD" != "0" ]] && git push origin "$BRANCH"

echo "=== Bootstrap NUC ==="
nuc_ssh "powershell -NoProfile -ExecutionPolicy Bypass -Command \"
  \\\$env:NUC_GIT_BRANCH='$BRANCH';
  if (-not (Test-Path \\\$env:USERPROFILE\\math-sdk\\.git)) {
    git clone https://github.com/splurgetech/math-sdk.git \\\$env:USERPROFILE\\math-sdk;
    Set-Location \\\$env:USERPROFILE\\math-sdk; git checkout $BRANCH;
    & \\\$env:USERPROFILE\\math-sdk\\scripts\\nuc_install_python312.ps1;
    & \\\$env:USERPROFILE\\math-sdk\\scripts\\setup_windows.ps1;
    & \\\$env:USERPROFILE\\math-sdk\\scripts\\smoke_test_windows.ps1;
  } else {
    & \\\$env:USERPROFILE\\math-sdk\\scripts\\nuc_bootstrap_remote.ps1;
  }
\""

echo "=== Bootstrap complete ==="
