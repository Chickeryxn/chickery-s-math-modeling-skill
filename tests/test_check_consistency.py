#!/usr/bin/env python3
"""Tests for the imported pure-stdlib consistency checker
(references/upstream/nature-writing/check_consistency.py, Apache-2.0)."""
from __future__ import annotations
import sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "references" / "upstream" / "nature-writing"))
from check_consistency import run_checks, read_sources, DEFAULT_TERM_GROUPS


def check_text(text: str, groups=None):
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    p = root / "manuscript.md"
    p.write_text(text, encoding="utf-8")
    try:
        return run_checks([p], groups)
    finally:
        td.cleanup()


class CheckConsistencyTests(unittest.TestCase):
    def test_clean_text_no_findings(self):
        findings = check_text("The model uses 10 cm resolution and a fixed seed.")
        self.assertEqual(findings, [])

    def test_mixed_unit_equivalence_detected(self):
        # 10 cm vs 0.1 m are equivalent lengths; upstream flags equivalent-unit mixing
        findings = check_text("Panel A uses 10 cm; panel B uses 0.1 m.")
        self.assertTrue(any(f.code == "EQUIVALENT_LENGTH_UNIT_VARIANT" for f in findings),
                        [f.code for f in findings])

    def test_term_group_mixing_detected(self):
        findings = check_text("this study shows X. this work shows Y.", dict(DEFAULT_TERM_GROUPS))
        self.assertTrue(any(f.code == "TERM_VARIANTS_PRESENT" for f in findings),
                        [f.code for f in findings])


if __name__ == "__main__":
    unittest.main()
