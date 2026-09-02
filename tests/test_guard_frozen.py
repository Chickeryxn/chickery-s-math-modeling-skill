#!/usr/bin/env python3
"""Tests for the PreToolUse guard (plugins/mathmodeling-skills/hooks/guard_frozen.py)."""
from __future__ import annotations
import json, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins" / "mathmodeling-skills" / "hooks"))
import guard_frozen as g


def payload(tool, file_path, extra=None):
    ti = {"file_path": file_path}
    if extra:
        ti.update(extra)
    return {"tool_name": tool, "tool_input": ti}


class GuardDecideTests(unittest.TestCase):
    def test_blocks_frozen_edit(self):
        code, reason = g.decide(payload("Edit", "results/Q1/reports/frozen_numbers.json"))
        self.assertEqual(code, 2)
        self.assertIn("frozen", reason.lower())

    def test_blocks_raw_data_edit(self):
        code, _ = g.decide(payload("Write", "workspace/data_raw/attachments/2024C.xlsx"))
        self.assertEqual(code, 2)

    def test_allows_read_of_frozen(self):
        code, _ = g.decide(payload("Read", "results/Q1/reports/frozen_numbers.json"))
        self.assertEqual(code, 0)

    def test_allows_normal_edit(self):
        code, _ = g.decide(payload("Edit", "paper/sections/q1.tex"))
        self.assertEqual(code, 0)

    def test_allows_non_write_tool(self):
        code, _ = g.decide(payload("Bash", "results/Q1/reports/frozen_numbers.json"))
        self.assertEqual(code, 0)

    def test_nested_input_scan(self):
        code, _ = g.decide({"tool_name": "MultiEdit",
                            "tool_input": {"updates": [{"file_path": "workspace/data_raw/a.csv"}]}})
        self.assertEqual(code, 2)

    def test_unparseable_payload_not_blocked(self):
        p = subprocess.run([sys.executable, str(ROOT / "plugins" / "mathmodeling-skills" /
                                                "hooks" / "guard_frozen.py")],
                           input="not json", text=True, capture_output=True)
        self.assertEqual(p.returncode, 0)

    def test_cli_block_via_stdin(self):
        p = subprocess.run([sys.executable, str(ROOT / "plugins" / "mathmodeling-skills" /
                                                "hooks" / "guard_frozen.py")],
                           input=json.dumps(payload("Edit", "results/Q1/reports/frozen_numbers.json")),
                           text=True, capture_output=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn("Blocked", p.stderr)

    def test_self_check(self):
        p = subprocess.run([sys.executable, str(ROOT / "plugins" / "mathmodeling-skills" /
                                                "hooks" / "guard_frozen.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)


if __name__ == "__main__":
    unittest.main()
