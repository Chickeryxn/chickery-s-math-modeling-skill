#!/usr/bin/env python3
"""Guard: schemas/*.schema.json must stay consistent with the validators and
golden examples. The schema files are documented contracts, not runtime
schemas — nothing loads them — so this test is the coupling that keeps the two
sides from silently drifting apart.
"""
from __future__ import annotations
import json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def load(name: str) -> dict:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


class SchemasConsistencyTests(unittest.TestCase):
    def test_all_schema_files_are_valid_json(self):
        for name in ("decision", "lineage", "model_contract", "run_snapshot"):
            data = load(f"{name}.schema.json")
            self.assertIsInstance(data, dict)
            self.assertIn("required", data)
            self.assertIsInstance(data["required"], list)
            self.assertTrue(data["required"])

    def test_decision_schema_matches_validator(self):
        import validate_decisions
        schema = load("decision.schema.json")
        self.assertEqual(sorted(schema["required"]),
                         sorted(("decision_id", "decision_type", "status", "source",
                                 "choice", "evidence_refs", "recorded_at")))
        self.assertEqual(set(schema["status_values"]), validate_decisions.STATUSES)

    def test_model_contract_schema_matches_validator(self):
        import validate_model_contract
        schema = load("model_contract.schema.json")
        self.assertEqual(sorted(schema["required"]), sorted(validate_model_contract.REQUIRED))

    def test_run_snapshot_schema_matches_validator_required_keys(self):
        # Mirror of the key loop inside create_run_snapshot.validate(); if the
        # validator's checked set changes, update both sides in the same change.
        validator_keys = {
            "run_id", "planned_budget", "actual_budget", "budget_delta", "degraded",
            "input_manifest", "code_manifest", "config_hash", "command", "environment",
            "status", "return_code", "result_ref", "validation_ref", "executed_by_runner",
        }
        schema = load("run_snapshot.schema.json")
        self.assertEqual(set(schema["required"]), validator_keys)
        self.assertEqual(set(schema["status_values"]),
                         {"RUNNING", "SUCCESS", "FAILED", "INTERRUPTED", "DEGRADED_SUCCESS"})

    def test_lineage_schema_required_present_in_golden_example(self):
        schema = load("lineage.schema.json")
        example = json.loads((ROOT / "planning" / "examples" / "lineage.example.json")
                             .read_text(encoding="utf-8"))
        missing = [k for k in schema["required"] if k not in example]
        self.assertEqual(missing, [], f"lineage.example.json missing keys: {missing}")

    def test_schema_version_consistency(self):
        # domain-neutral schemas carry their own version; manifest-level golden
        # examples use schema_version 1 for the manifest/parse families.
        self.assertEqual(load("model_contract.schema.json")["schema_version"], 1)
        for name in ("decision", "lineage", "run_snapshot"):
            self.assertEqual(load(f"{name}.schema.json")["schema_version"], 2)


if __name__ == "__main__":
    unittest.main()
