#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
SOURCE="$REPO_ROOT/.codex/skills"
CLAUDE_SOURCE="$REPO_ROOT/.claude/skills"
DESTINATION="$REPO_ROOT/plugins/mathmodeling-skills/skills"
MARKETPLACE="$REPO_ROOT/.agents/plugins/marketplace.json"
CHECK_ONLY=0

read_version() {
  python3 -c 'import json, sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["version"])' "$1"
}

check_versions() {
  local codex_version
  local claude_version
  codex_version="$(read_version "$REPO_ROOT/plugins/mathmodeling-skills/.codex-plugin/plugin.json")"
  claude_version="$(read_version "$REPO_ROOT/plugins/mathmodeling-skills/.claude-plugin/plugin.json")"
  if [ "$codex_version" != "$claude_version" ]; then
    printf 'error: plugin versions differ (Codex=%s Claude=%s)\n' "$codex_version" "$claude_version" >&2
    exit 1
  fi
}

check_marketplace() {
  python3 - "$MARKETPLACE" "$REPO_ROOT/plugins/mathmodeling-skills" <<'PY'
import json
import sys
from pathlib import Path

marketplace_path = Path(sys.argv[1])
plugin_root = Path(sys.argv[2]).resolve()
if not marketplace_path.is_file():
    raise SystemExit(f"error: missing repo marketplace: {marketplace_path}")

payload = json.loads(marketplace_path.read_text(encoding="utf-8"))
if payload.get("name") != "chickery-s-math-modeling-skill":
    raise SystemExit("error: unexpected marketplace name")
entries = [item for item in payload.get("plugins", []) if item.get("name") == "mathmodeling-skills"]
if len(entries) != 1:
    raise SystemExit("error: marketplace must contain exactly one mathmodeling-skills entry")
source = entries[0].get("source", {})
if source.get("source") != "local" or source.get("path") != "./plugins/mathmodeling-skills":
    raise SystemExit("error: marketplace plugin source must be ./plugins/mathmodeling-skills")
PY
}

if [ "${1:-}" = "--check" ]; then
  CHECK_ONLY=1
elif [ "$#" -gt 0 ]; then
  printf 'usage: %s [--check]\n' "$0" >&2
  exit 2
fi

if ! diff -qr --exclude='.DS_Store' "$SOURCE" "$CLAUDE_SOURCE" >/dev/null; then
  printf 'error: .codex/skills and .claude/skills differ; reconcile both standalone trees first\n' >&2
  exit 1
fi

check_versions
check_marketplace

if [ "$CHECK_ONLY" -eq 1 ]; then
  diff -qr --exclude='.DS_Store' "$SOURCE" "$DESTINATION"
  cmp "$REPO_ROOT/AGENTS.md" "$REPO_ROOT/plugins/mathmodeling-skills/AGENTS.md"
  cmp "$REPO_ROOT/LICENSE" "$REPO_ROOT/plugins/mathmodeling-skills/LICENSE"
  printf 'plugin package is synchronized\n'
  exit 0
fi

mkdir -p "$DESTINATION"
rsync -a --delete --exclude='.DS_Store' "$SOURCE/" "$DESTINATION/"
cp "$REPO_ROOT/AGENTS.md" "$REPO_ROOT/LICENSE" "$REPO_ROOT/plugins/mathmodeling-skills/"
printf 'synchronized plugin package from .codex/skills\n'