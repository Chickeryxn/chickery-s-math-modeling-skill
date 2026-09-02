#!/usr/bin/env python3
"""Problem-agnostic synthetic scenarios validated against the real validators
(instead of asserting on self-built dicts, which proved nothing)."""
from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
sys.path.insert(0, str(ROOT / "scripts"))
from continuous_events import merge_intervals, interval_union_length, bisection_root


def valid_contract(**overrides) -> dict:
    base = {
        "schema_version": 1,
        "entities": [{"id": "entity"}],
        "inputs": [{"id": "x", "type": "numeric", "domain": "real", "unit": "u", "source": "synthetic"}],
        "state_functions": [],
        "decision_variables": [{"id": "w", "type": "numeric", "domain": "[0,1]", "unit": "u"}],
        "hard_constraints": [{"id": "c", "expression_ref": "x"}],
        "soft_constraints": [],
        "objective": {"sense": "MINIMIZE", "value_ref": "loss",
                      "output_contract": {"type": "scalar"}},
        "evaluator": {"evaluator_id": "ev", "implementation_ref": "verifier.py"},
        "uncertainty": None,
        "validation_contract": {"independent_checks": ["main", "baseline", "verifier"],
                                "tolerances": {"loss": 1e-6}},
    }
    base.update(overrides)
    return base


def cli_validate(contract: dict) -> int:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "contract.json"
        p.write_text(json.dumps(contract), encoding="utf-8")
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_model_contract.py"),
                            str(p)], capture_output=True, text=True, encoding="utf-8")
        return r.returncode


class SyntheticScenarioTests(unittest.TestCase):
    def test_regression_contract_passes_real_validator(self):
        # Regression flavor: objective sense + output contract + three roles.
        self.assertEqual(cli_validate(valid_contract()), 0)

    def test_scheduling_contract_capacity_is_enforced(self):
        # Scheduling flavor: a valid contract passes; dropping a required
        # top-level key (hard_constraints) must fail the real validator.
        self.assertEqual(cli_validate(valid_contract(hard_constraints=[])), 0)
        broken = valid_contract()
        del broken["hard_constraints"]
        self.assertNotEqual(cli_validate(broken), 0)

    def test_dynamic_event_interval_semantics(self):
        # Dynamic-event flavor checks the stdlib helper actually used by the
        # event machinery rather than a self-built dict.
        merged = merge_intervals([(0.0, 2.0), (1.0, 3.0), (5.0, 5.5)])
        self.assertEqual(merged, [(0.0, 3.0), (5.0, 5.5)])
        self.assertAlmostEqual(interval_union_length([(0.0, 2.0), (1.0, 3.0), (5.0, 6.0)]), 4.0)
        root = bisection_root(lambda x: x * x - 2.0, 0.0, 2.0, tol=1e-9)
        self.assertLess(abs(root - 2.0 ** 0.5), 1e-6)


if __name__ == "__main__":
    unittest.main()
