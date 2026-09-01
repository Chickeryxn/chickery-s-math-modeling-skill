#!/usr/bin/env python3
"""Tests for scripts/claim_coverage.py (pure standard library)."""
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from claim_coverage import load_subquestions, section_qids, frozen_per_qid, coverage


def make_workspace(with_sections=True, with_frozen=True):
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    (root / "planning" / "parse").mkdir(parents=True)
    (root / "paper" / "sections").mkdir(parents=True)
    (root / "results" / "Q1" / "reports").mkdir(parents=True)
    (root / "results" / "Q2" / "reports").mkdir(parents=True)
    (root / "planning" / "parse" / "problem_parse.json").write_text(
        json.dumps({"subquestions": [{"id": "Q1"}, {"id": "Q2"}]}), encoding="utf-8")
    if with_sections:
        (root / "paper" / "sections" / "q1.tex").write_text(
            "\\section{问题一：建模}\n结果 2.4。\n", encoding="utf-8")
        (root / "paper" / "sections" / "q2.tex").write_text(
            "\\section{问题二：验证}\n结果 0.88。\n", encoding="utf-8")
    if with_frozen:
        (root / "results" / "Q1" / "reports" / "frozen_numbers.json").write_text(
            json.dumps({"claims": [{"claim_id": "q1_rmse", "value": 2.4}]}), encoding="utf-8")
        (root / "results" / "Q2" / "reports" / "frozen_numbers.json").write_text(
            json.dumps({"claims": [{"claim_id": "q2_acc", "value": 0.88}]}), encoding="utf-8")
    return td, root


class ClaimCoverageTests(unittest.TestCase):
    def test_load_subquestions(self):
        td, root = make_workspace()
        self.assertEqual(load_subquestions(root), ["Q1", "Q2"])
        td.cleanup()

    def test_section_qids(self):
        td, root = make_workspace()
        sq = section_qids(root)
        self.assertIn("Q1", sq["q1.tex"])
        td.cleanup()

    def test_frozen_per_qid(self):
        td, root = make_workspace()
        fp = frozen_per_qid(root)
        self.assertEqual(fp.get("Q1"), ["q1_rmse"])
        td.cleanup()

    def test_coverage_full_passes(self):
        td, root = make_workspace()
        c = coverage(root)
        self.assertEqual(c["status"], "PASS")
        td.cleanup()

    def test_missing_section_fails(self):
        td, root = make_workspace(with_sections=False)
        c = coverage(root)
        self.assertEqual(c["status"], "PARTIAL")
        self.assertTrue(any("no paper section" in m for m in c["missing"]))
        td.cleanup()

    def test_missing_frozen_fails(self):
        td, root = make_workspace(with_frozen=False)
        c = coverage(root)
        self.assertEqual(c["status"], "PARTIAL")
        self.assertTrue(any("no frozen numbers" in m for m in c["missing"]))
        td.cleanup()


if __name__ == "__main__":
    unittest.main()
