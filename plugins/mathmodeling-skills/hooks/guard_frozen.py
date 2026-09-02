#!/usr/bin/env python3
"""PreToolUse hook guard: block edits to frozen numbers and raw data.

Reads a Claude/DSH hook payload (JSON) from stdin:

    {"tool_name": "Edit", "tool_input": {"file_path": "...", "content": "..."}, ...}

Contract (Claude Code hooks and DSH dsh-hooks-claude-code bridge):
- exit 0: allow (plain stdout allowed)
- exit 2: block, stderr text is the reason shown to the model

Protected paths (project policy, AGENTS.md):
- any "frozen_numbers.json" write   -> numbers are frozen; edit = thaw -> change
  canonical source -> rerun -> refreeze (never hand-edit)
- any "workspace/data_raw/" write   -> raw attachments are read-only

Scope rules:
- Only WRITE_TOOLS are screened; this includes DSH's lowercase `write`/`edit`.
- Only path-like tool-input fields are scanned (file_path/path/old_path/
  new_path and their nested occurrences), never free-text content, so a doc
  that merely mentions "frozen_numbers.json" is not blocked.
- Matching is case-insensitive (Windows paths are case-insensitive) and uses
  path-component boundaries, so "not_frozen_numbers.json" or "my_data_raw/"
  are not false positives.

The guard is advisory: it deters accidental edits and is bypassable via other
tools (e.g. Bash); the validators are the authoritative contract. Pure
standard library. Self-test: `python guard_frozen.py --check`.
"""
from __future__ import annotations
import json, sys

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit", "ReplaceInFile",
               "apply_patch", "create_file", "edit_file", "replace",
               "write", "edit", "multi_edit", "replace_in_file"}
PATH_KEYS = {"file_path", "path", "old_path", "new_path", "destination",
             "src", "dst", "source", "target"}
FROZEN_MARK = "frozen_numbers.json"


def is_data_raw(s: str) -> bool:
    low = s.lower().replace("\\", "/")
    return "/data_raw/" in low or low.startswith("data_raw/") or low == "data_raw"


def path_strings(node) -> list[str]:
    """Collect only path-like string values from a payload (recursively)."""
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(k, str) and k.lower() in PATH_KEYS and isinstance(v, str):
                out.append(v)
            else:
                out.extend(path_strings(v))
    elif isinstance(node, list):
        for v in node:
            out.extend(path_strings(v))
    return out


def decide(payload: dict) -> tuple[int, str | None]:
    """Return (exit_code, reason). exit 0 allows; exit 2 blocks."""
    tool = str(payload.get("tool_name") or payload.get("tool") or "")
    if tool and tool not in WRITE_TOOLS:
        return 0, None
    inputs = payload.get("tool_input") or payload.get("input") or payload
    for s in path_strings(inputs):
        if s.lower() == FROZEN_MARK or s.lower().endswith("/" + FROZEN_MARK) or s.lower().endswith("\\" + FROZEN_MARK):
            return 2, (f"[guard] Blocked: '{FROZEN_MARK}' is immutable. "
                       "To change a frozen value: thaw -> modify canonical source -> "
                       "rerun affected work -> refreeze (record in freeze_change_log.md).")
        if is_data_raw(s):
            return 2, "[guard] Blocked: workspace/data_raw/ is read-only. Write cleaned copies under workspace/data_clean/."
    return 0, None


def main() -> int:
    if "--check" in sys.argv:
        assert decide({"tool_name": "Edit", "tool_input": {"file_path": "results/Q1/reports/frozen_numbers.json"}})[0] == 2
        assert decide({"tool_name": "Write", "tool_input": {"file_path": "workspace/data_raw/x.csv"}})[0] == 2
        assert decide({"tool_name": "write", "tool_input": {"file_path": "results/Q1/reports/FROZEN_NUMBERS.JSON"}})[0] == 2
        assert decide({"tool_name": "edit", "tool_input": {"path": "workspace\\data_raw\\a.csv"}})[0] == 2
        assert decide({"tool_name": "Read", "tool_input": {"file_path": "results/Q1/reports/frozen_numbers.json"}})[0] == 0
        assert decide({"tool_name": "Edit", "tool_input": {"file_path": "paper/sections/q1.tex"}})[0] == 0
        assert decide({"tool_name": "Edit", "tool_input": {"file_path": "docs/not_frozen_numbers.json.bak"}})[0] == 0
        assert decide({"tool_name": "Edit", "tool_input": {"content": "mentions frozen_numbers.json in text"}})[0] == 0
        print("guard self-check OK")
        return 0
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    try:
        payload = json.loads(raw)
    except Exception:
        return 0  # unparseable payload: do not block
    code, reason = decide(payload)
    if code == 2:
        print(reason or "blocked", file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
