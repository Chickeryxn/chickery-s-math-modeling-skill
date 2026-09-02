#!/usr/bin/env python3
"""Tests for scripts/claim_coverage.py (pure standard library)."""
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from claim_coverage import load_subquestions, section_qids, frozen_per_qid, coverage, cn_num_to_arabic


def make_workspace(with_sections=True, with_frozen=True, with_abstract=True,
                   abstract_numbers="2.4 与 0.88"):
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    (root / "planning" / "parse").mkdir(parents=True)
    (root / "paper" / "sections").mkdir(parents=True)
    (root / "results" / "Q1" / "reports").mkdir(parents=True)
    (root / "results" / "Q2" / "reports").mkdir(parents=True)
    (root / "planning" / "parse" / "problem_parse.json").write_text(
        json.dumps({"subquestions": [{"id": "Q1"}, {"id": "Q2"}]}), encoding="utf-8")
    if with_sections:
        abstract = ("\\begin{abstract}本模型的主要结果为 %s。\\end{abstract}\n"
                    % abstract_numbers) if with_abstract else ""
        (root / "paper" / "sections" / "q1.tex").write_text(
            "\\section{问题一：建模}\n结果 2.4。\n" + abstract, encoding="utf-8")
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

    def test_chinese_numeral_heading_maps_to_arabic_qid(self):
        # Regression: 问题三 was mapped to "Q三" instead of "Q3", so a present
        # section was reported MISSING against a parse id of "Q3".
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        (root / "paper" / "sections").mkdir(parents=True)
        (root / "paper" / "sections" / "q3.tex").write_text(
            "\\section{问题三：建模}\n结果 3.5。\n", encoding="utf-8")
        (root / "paper" / "sections" / "q12.tex").write_text(
            "\\section{问题十二：验证}\n结果 0.5。\n", encoding="utf-8")
        sq = section_qids(root)
        self.assertIn("Q3", sq["q3.tex"])
        self.assertIn("Q12", sq["q12.tex"])
        self.assertNotIn("Q三", sq["q3.tex"])
        td.cleanup()

    def test_cn_num_to_arabic_edge_cases(self):
        self.assertEqual(cn_num_to_arabic("一"), "1")
        self.assertEqual(cn_num_to_arabic("九"), "9")
        self.assertEqual(cn_num_to_arabic("十"), "10")
        self.assertEqual(cn_num_to_arabic("十二"), "12")
        self.assertEqual(cn_num_to_arabic("二十一"), "21")
        self.assertEqual(cn_num_to_arabic("3"), "3")
        # unhandled shape (百/千) falls back verbatim instead of crashing
        self.assertEqual(cn_num_to_arabic("一百"), "一百")

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

    def test_abstract_with_wrong_numbers_fails(self):
        # Regression: an abstract that contains *some* number but none of the
        # frozen values must not pass ("any digit anywhere" used to pass).
        td, root = make_workspace(abstract_numbers="9.99")
        c = coverage(root)
        self.assertEqual(c["status"], "PARTIAL")
        self.assertTrue(any("abstract states none of its frozen numbers" in m
                            for m in c["missing"]))
        td.cleanup()

    def test_no_abstract_reported_as_unverifiable(self):
        # Regression: extract_abstract used to fall back to the whole section
        # text, so a missing abstract silently passed on body-text numbers.
        td, root = make_workspace(with_abstract=False)
        c = coverage(root)
        self.assertEqual(c["status"], "PARTIAL")
        self.assertTrue(any("abstract section not found" in m for m in c["missing"]))
        td.cleanup()

    def test_missing_parse_reported(self):
        td, root = make_workspace()
        (root / "planning" / "parse" / "problem_parse.json").unlink()
        c = coverage(root)
        self.assertEqual(c["status"], "PARTIAL")
        self.assertTrue(any("problem_parse.json missing" in m for m in c["missing"]))
        td.cleanup()


if __name__ == "__main__":
    unittest.main()
