#!/usr/bin/env bash
# Shared SSH target for the Windows NUC (see ~/.ssh/config Host nuc).
set -euo pipefail

NUC_HOST="${NUC_HOST:-nuc}"
NUC_MATH_SDK="${NUC_MATH_SDK:-math-sdk}"
NUC_GAME_LIB="games/0_0_clash_kronos_cluster/library"

nuc_ssh() {
  ssh -o BatchMode=yes -o ConnectTimeout=15 "$NUC_HOST" "$@"
}

nuc_repo_path() {
  # OpenSSH on Windows: relative paths are under the user's home directory.
  echo "$NUC_MATH_SDK"
}
