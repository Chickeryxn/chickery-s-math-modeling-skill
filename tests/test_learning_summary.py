#!/usr/bin/env python3
"""Tests for scripts/learning_summary.py (pure standard library)."""
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from learning_summary import collect_decisions, collect_frozen, render


def make_workspace():
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    (root / "methods" / "Q1").mkdir(parents=True)
    (root / "results" / "Q1" / "reports").mkdir(parents=True)
    (root / "methods" / "Q1" / "q1_decisions.jsonl").write_text(
        json.dumps({"decision_id": "d1", "decision_type": "method_choice",
                    "status": "DECIDED", "choice": "M2", "rationale": "fit data"}) + "\n"
        + json.dumps({"decision_id": "d2", "decision_type": "result_verdict",
                      "status": "DECIDED", "choice": "accept"}) + "\n", encoding="utf-8")
    (root / "results" / "Q1" / "reports" / "frozen_numbers.json").write_text(
        json.dumps({"claims": [{"claim_id": "q1_rmse", "value": 2.4}]}), encoding="utf-8")
    return td, root


class LearningSummaryTests(unittest.TestCase):
    def test_collect_decisions(self):
        td, root = make_workspace()
        d = collect_decisions(root)
        self.assertEqual(list(d), ["Q1"])
        self.assertEqual(len(d["Q1"]), 2)
        td.cleanup()

    def test_collect_frozen(self):
        td, root = make_workspace()
        f = collect_frozen(root)
        self.assertEqual(f, {"Q1": ["q1_rmse"]})
        td.cleanup()

    def test_render_includes_sections_and_blank_lessons(self):
        td, root = make_workspace()
        text = render(root)
        self.assertIn("## Q1", text)
        self.assertIn("q1_rmse", text)
        self.assertIn("method_choice", text)
        self.assertIn("事后判定与教训", text)
        td.cleanup()

    def test_render_empty_workspace(self):
        td = tempfile.TemporaryDirectory()
        text = render(Path(td.name))
        self.assertIn("未找到决策账本", text)
        td.cleanup()


if __name__ == "__main__":
    unittest.main()
