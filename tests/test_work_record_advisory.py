#!/usr/bin/env python3
"""work_record check advisory: DECIDED ledger records without mirrored decision
cards are reported as an advisory, never as a check failure (0.8.0)."""
from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

DECISION = {"decision_id": "q1_method_choice", "decision_type": "method_choice",
            "status": "DECIDED", "decided_by": "human", "choice": "M1",
            "rationale": "User supplied rationale", "evidence_refs": [],
            "recorded_at": "2026-09-01T00:00:00Z",
            "source": {"source_type": "user_answer", "user_message_id": "m1",
                       "user_verbatim_answer": "I choose M1"}}


def run_script(script, *args, cwd=None):
    return subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args],
                          capture_output=True, text=True, encoding="utf-8", cwd=cwd)


class WorkRecordAdvisoryTests(unittest.TestCase):
    def test_missing_mirror_is_advisory_not_failure(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = run_script("work_record.py", "init", str(root))
            self.assertEqual(p.returncode, 0, p.stderr)
            ledger = root / "methods/Q1/q1_decisions.jsonl"
            ledger.parent.mkdir(parents=True, exist_ok=True)
            ledger.write_text(json.dumps(DECISION) + "\n", encoding="utf-8")
            p = run_script("work_record.py", "check", str(root))
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("advisory: decision cards missing", p.stderr)
            # after mirroring the card, the advisory disappears
            p = run_script("work_record.py", "decision", "Q1", "q1_method_choice", str(root))
            self.assertEqual(p.returncode, 0, p.stderr)
            p = run_script("work_record.py", "index", str(root))
            self.assertEqual(p.returncode, 0, p.stderr)
            p = run_script("work_record.py", "check", str(root))
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertNotIn("advisory: decision cards missing", p.stderr)


if __name__ == "__main__":
    unittest.main()
