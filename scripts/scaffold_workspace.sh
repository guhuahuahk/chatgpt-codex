#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "$0")" && pwd)"
PY_SCRIPT="$SCRIPT_DIR/scaffold_workspace.py"

if [[ ! -f "$PY_SCRIPT" ]]; then
  echo "Missing scaffold script: $PY_SCRIPT" >&2
  exit 1
fi

python3 "$PY_SCRIPT" "$@"
