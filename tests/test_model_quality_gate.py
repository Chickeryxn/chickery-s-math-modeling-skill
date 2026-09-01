#!/usr/bin/env python3
"""Tests for scripts/model_quality_gate.py (pure standard library)."""
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from model_quality_gate import gate, has_uncertainty, flatten_metrics


def make_workspace(seed=True, baseline_metrics=True, uncertainty=True, contract=True):
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    r = root / "results" / "Q1" / "experiments" / "round1"
    r.mkdir(parents=True)
    main = {"method_id": "M1", "role": "main_candidate", "metrics_summary": {"rmse": 2.4}}
    base = {"method_id": "M0", "role": "usable_baseline",
            "metrics_summary": {"rmse": 3.1} if baseline_metrics else {}}
    data = {"question": "Q1", "round": "round1", "methods": [main, base]}
    if seed:
        data["random_seed"] = 2026
    if uncertainty:
        data["uncertainty"] = {"rmse_ci": [2.2, 2.6]}
    (r / "run_summary.json").write_text(json.dumps(data), encoding="utf-8")
    if contract:
        (root / "planning").mkdir(exist_ok=True)
        (root / "planning" / "model_contract.json").write_text(
            json.dumps({"objective": {"output_contract": {"type": "scalar"}}}), encoding="utf-8")
    return td, root


class ModelQualityGateTests(unittest.TestCase):
    def test_good_run_passes(self):
        td, root = make_workspace()
        g = gate(root, "Q1")
        self.assertEqual(g["status"], "PASS")
        self.assertEqual(g["findings"], [])
        td.cleanup()

    def test_missing_seed_fails(self):
        td, root = make_workspace(seed=False)
        g = gate(root, "Q1")
        self.assertTrue(any("random_seed" in f for f in g["findings"]))
        td.cleanup()

    def test_empty_baseline_fails(self):
        td, root = make_workspace(baseline_metrics=False)
        g = gate(root, "Q1")
        self.assertTrue(any("baseline not comparable" in f for f in g["findings"]))
        td.cleanup()

    def test_missing_uncertainty_fails(self):
        td, root = make_workspace(uncertainty=False)
        g = gate(root, "Q1")
        self.assertTrue(any("uncertainty" in f for f in g["findings"]))
        td.cleanup()

    def test_missing_contract_fails(self):
        td, root = make_workspace(contract=False)
        g = gate(root, "Q1")
        self.assertTrue(any("output_contract" in f for f in g["findings"]))
        td.cleanup()

    def test_no_run_fails(self):
        td = tempfile.TemporaryDirectory()
        g = gate(Path(td.name), "Q1")
        self.assertEqual(g["status"], "FAIL")
        td.cleanup()

    def test_has_uncertainty_nested(self):
        self.assertTrue(has_uncertainty({"metrics": {"a": {"ci": [1, 2]}}}))
        self.assertFalse(has_uncertainty({"metrics": {"a": 1}}))

    def test_flatten_metrics(self):
        self.assertEqual(len(flatten_metrics({"a": 1, "b": {"c": 2.0}, "d": [3, "x"]})), 3)


if __name__ == "__main__":
    unittest.main()
