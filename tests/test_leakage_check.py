#!/usr/bin/env python3
"""Tests for scripts/leakage_check.py (pure standard library)."""
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from leakage_check import check_file, check_profile


def write_csv(root: Path, text: str) -> Path:
    p = root / "data.csv"
    p.write_text(text, encoding="utf-8")
    return p


class LeakageCheckTests(unittest.TestCase):
    def test_clean_data_passes(self):
        td = tempfile.TemporaryDirectory()
        p = write_csv(Path(td.name), "x,y\n1,2\n2,3\n3,4\n")
        r = check_file(p, "y")
        self.assertEqual(r["status"], "PASS")
        td.cleanup()

    def test_missing_target_fails(self):
        td = tempfile.TemporaryDirectory()
        p = write_csv(Path(td.name), "a,b\n1,2\n")
        r = check_file(p, "y")
        self.assertEqual(r["status"], "FAIL")
        td.cleanup()

    def test_time_disorder_detected(self):
        td = tempfile.TemporaryDirectory()
        p = write_csv(Path(td.name), "date,y\n2026-01-03,1\n2026-01-01,2\n2026-01-02,3\n")
        r = check_file(p, "y", time_col="date")
        self.assertTrue(any("not ascending" in f for f in r["findings"]))
        td.cleanup()

    def test_time_sorted_passes(self):
        td = tempfile.TemporaryDirectory()
        p = write_csv(Path(td.name), "date,y\n2026-01-01,1\n2026-01-02,2\n2026-01-03,3\n")
        r = check_file(p, "y", time_col="date")
        self.assertEqual(r["status"], "PASS")
        td.cleanup()

    def test_mixed_date_and_numeric_time_does_not_crash(self):
        # Regression: parse_time returned datetime for dates and float for
        # numeric tokens; comparing the two raised TypeError and crashed the
        # whole script. Both kinds now normalize to epoch-seconds floats.
        td = tempfile.TemporaryDirectory()
        p = write_csv(Path(td.name), "date,y\n2026-01-01,1\n100,2\n2026-01-02,3\n")
        r = check_file(p, "y", time_col="date")
        self.assertIn("status", r)
        self.assertTrue(any("mixes date and numeric formats" in f for f in r["findings"]))
        td.cleanup()

    def test_numeric_time_descending_detected(self):
        td = tempfile.TemporaryDirectory()
        p = write_csv(Path(td.name), "t,y\n300,1\n200,2\n100,3\n")
        r = check_file(p, "y", time_col="t")
        self.assertTrue(any("not ascending" in f for f in r["findings"]))
        td.cleanup()

    def test_delimiter_option_is_used(self):
        td = tempfile.TemporaryDirectory()
        p = write_csv(Path(td.name), "x;y\n1;2\n2;3\n")
        r = check_file(p, "y", delimiter=";")
        self.assertEqual(r["status"], "PASS")
        td.cleanup()

    def test_duplicate_rows_detected(self):
        td = tempfile.TemporaryDirectory()
        p = write_csv(Path(td.name), "x,y\n1,2\n1,2\n3,4\n")
        r = check_file(p, "y")
        self.assertTrue(any("duplicate rows" in f for f in r["findings"]))
        td.cleanup()

    def test_profile_scan(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        prof = root / "profile.json"
        prof.write_text(json.dumps({"fields": [{"name": "y"}, {"name": "date"}, {"name": "x"}]}),
                        encoding="utf-8")
        r = check_profile(prof, "y")
        self.assertTrue(any("time-like" in f for f in r["findings"]))
        td.cleanup()


if __name__ == "__main__":
    unittest.main()
