#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
python3 "$ROOT/scripts/sync_plugin.py" "$ROOT" "$@"
