#!/usr/bin/env python3
"""Tests for scripts/training_scorecard.py (pure standard library)."""
from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import training_scorecard as ts


def make_round(root: Path, n: int, scores: dict | None = None):
    """Create results/training/roundN with a solution artifact and scorecard.

    scores maps dimension -> (score, evidence). Evidence is used verbatim;
    callers pass a path that resolves relative to the round dir or its
    ancestors (the default below resolves relative to results/).
    """
    rd = root / "results" / "training" / f"round{n}"
    sol = rd / "solution"
    sol.mkdir(parents=True)
    (sol / "run_summary.md").write_text("ok", encoding="utf-8")
    data = ts.template(n, "closed")
    if scores:
        for dim, (score, evidence) in scores.items():
            data["dimensions"][dim]["agent_score"] = score
            data["dimensions"][dim]["agent_evidence"] = evidence or str(
                (sol / "run_summary.md").relative_to(rd.parent.parent))
    data["mechanical_checks"] = [{"name": "model_quality_gate", "status": "PASS"}]
    (rd / ts.SCORECARD).write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
    return rd


class ScorecardScaffoldTests(unittest.TestCase):
    def test_template_shape(self):
        t = ts.template(1, "closed")
        self.assertEqual(t["schema_version"], 1)
        self.assertEqual(set(t["dimensions"]), set(ts.DIMENSIONS))
        for spec in t["dimensions"].values():
            self.assertIsNone(spec["agent_score"])
            self.assertIsNone(spec["user_score"])

    def test_round_scaffolds_when_missing(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        rd = root / "results" / "training" / "round1"
        (rd / "solution").mkdir(parents=True)
        rc = ts.cmd_round(type("A", (), {"round_dir": rd, "json": False, "check": False})())
        self.assertEqual(rc, 0)
        self.assertTrue((rd / ts.SCORECARD).is_file())
        td.cleanup()

    def test_round_check_missing_fails(self):
        td = tempfile.TemporaryDirectory()
        rd = Path(td.name) / "results" / "training" / "round2"
        rc = ts.cmd_round(type("A", (), {"round_dir": rd, "json": False, "check": True})())
        self.assertEqual(rc, 2)
        td.cleanup()


class ScorecardValidateTests(unittest.TestCase):
    def test_valid_scorecard_passes(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        rd = make_round(root, 1, {"mathematical": (4, None)})
        rc = ts.cmd_round(type("A", (), {"round_dir": rd, "json": False, "check": False})())
        self.assertEqual(rc, 0)
        td.cleanup()

    def test_out_of_range_score_fails(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        rd = make_round(root, 1, {"figure": (9, None)})
        errors, warnings = [], []
        data = json.loads((rd / ts.SCORECARD).read_text(encoding="utf-8"))
        self.assertFalse(ts.validate_scorecard(rd, data, errors, warnings))
        self.assertTrue(any("figure.user_score" in e or "figure.agent_score" in e for e in errors))
        td.cleanup()

    def test_missing_evidence_path_fails(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        rd = make_round(root, 1, {"evidence": (3, "does/not/exist.md")})
        errors, warnings = [], []
        data = json.loads((rd / ts.SCORECARD).read_text(encoding="utf-8"))
        self.assertFalse(ts.validate_scorecard(rd, data, errors, warnings))
        self.assertTrue(any("agent_evidence" in e for e in errors))
        td.cleanup()


class SummaryTests(unittest.TestCase):
    def test_summary_aggregates_rounds(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        scores_r1 = {d: (3, None) for d in ts.DIMENSIONS}
        scores_r2 = {d: (4, None) for d in ts.DIMENSIONS}
        make_round(root, 1, scores_r1)
        make_round(root, 2, scores_r2)
        rc = ts.cmd_summary(type("A", (), {"results_dir": root / "results" / "training",
                                           "json": False, "check": False})())
        self.assertEqual(rc, 0)
        data = json.loads((root / "results" / "training" / ts.SUMMARY).read_text(encoding="utf-8"))
        self.assertEqual(data["rounds"], [1, 2])
        self.assertEqual(data["radar"]["mathematical"], [3, 4])
        self.assertEqual(data["ranking"][0]["round"], 2)
        self.assertEqual(data["mechanical_tally"]["model_quality_gate"]["PASS"], 2)
        td.cleanup()

    def test_summary_check_roundtrip(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        make_round(root, 1, {"innovation": (4, None)})
        res = root / "results" / "training"
        self.assertEqual(ts.cmd_summary(type("A", (), {"results_dir": res, "json": False,
                                                       "check": False})()), 0)
        self.assertEqual(ts.cmd_summary(type("A", (), {"results_dir": res, "json": False,
                                                       "check": True})()), 0)
        td.cleanup()

    def test_summary_check_detects_drift(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        make_round(root, 1, {"expression": (4, None)})
        res = root / "results" / "training"
        self.assertEqual(ts.cmd_summary(type("A", (), {"results_dir": res, "json": False,
                                                       "check": False})()), 0)
        (res / ts.SUMMARY).write_text('{"schema_version": 1, "rounds": [99]}', encoding="utf-8")
        self.assertEqual(ts.cmd_summary(type("A", (), {"results_dir": res, "json": False,
                                                       "check": True})()), 2)
        td.cleanup()


class CliTests(unittest.TestCase):
    def test_cli_round_end_to_end(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        rd = root / "results" / "training" / "round1"
        (rd / "solution").mkdir(parents=True)
        p = subprocess.run([sys.executable, str(ROOT / "scripts" / "training_scorecard.py"),
                            "round", str(rd), "--json"],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(p.returncode, 0)
        out = json.loads(p.stdout)
        self.assertEqual(out["round"], 1)
        self.assertEqual(len(out["dimensions"]), 6)
        td.cleanup()


if __name__ == "__main__":
    unittest.main()

