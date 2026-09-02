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

The guard is advisory-plus: it blocks accidental edits, it does not replace
the validators. Pure standard library. Self-test: `python guard_frozen.py --check`.
"""
from __future__ import annotations
import json, sys

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit", "ReplaceInFile",
               "apply_patch", "create_file", "edit_file", "replace"}
FROZEN_MARK = "frozen_numbers.json"
RAW_MARKS = ("workspace/data_raw", "data_raw/", "\\data_raw\\", "/data_raw/")


def collect_strings(node) -> list[str]:
    out = []
    if isinstance(node, str):
        out.append(node)
    elif isinstance(node, dict):
        for v in node.values():
            out.extend(collect_strings(v))
    elif isinstance(node, list):
        for v in node:
            out.extend(collect_strings(v))
    return out


def decide(payload: dict) -> tuple[int, str | None]:
    """Return (exit_code, reason). exit 0 allows; exit 2 blocks."""
    tool = str(payload.get("tool_name") or payload.get("tool") or "")
    if tool and tool not in WRITE_TOOLS:
        return 0, None
    inputs = payload.get("tool_input") or payload.get("input") or payload
    for s in collect_strings(inputs):
        if FROZEN_MARK in s:
            return 2, (f"[guard] Blocked: '{FROZEN_MARK}' is immutable. "
                       "To change a frozen value: thaw -> modify canonical source -> "
                       "rerun affected work -> refreeze (record in freeze_change_log.md).")
        low = s.lower()
        if any(m in low for m in RAW_MARKS):
            return 2, "[guard] Blocked: workspace/data_raw/ is read-only. Write cleaned copies under workspace/data_clean/."
    return 0, None


def main() -> int:
    if "--check" in sys.argv:
        assert decide({"tool_name": "Edit", "tool_input": {"file_path": "results/Q1/reports/frozen_numbers.json"}})[0] == 2
        assert decide({"tool_name": "Edit", "tool_input": {"file_path": "workspace/data_raw/x.csv"}})[0] == 2
        assert decide({"tool_name": "Read", "tool_input": {"file_path": "results/Q1/reports/frozen_numbers.json"}})[0] == 0
        assert decide({"tool_name": "Edit", "tool_input": {"file_path": "paper/sections/q1.tex"}})[0] == 0
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
