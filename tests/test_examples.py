#!/usr/bin/env python3
"""Golden-example guard: planning/examples artifacts must keep passing the
standalone structural checks promised in planning/examples/README.md."""
from __future__ import annotations
import json, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from workflow_guard import method_card_ready, risk_probe_ready, parse_ready, classification_ready
from validate_decisions import validate as validate_decisions

EX = ROOT / "planning" / "examples"


def load_json(name: str):
    return json.loads((EX / name).read_text(encoding="utf-8-sig"))


class GoldenExampleTests(unittest.TestCase):
    def test_parse_example_passes_structural_depth(self):
        data = load_json("problem_parse.example.json")
        self.assertTrue(parse_ready(data))
        self.assertTrue(isinstance(data.get("data_inventory"), list))

    def test_classification_example_has_primary_types(self):
        self.assertTrue(classification_ready(load_json("problem_classification.example.json")))

    def test_method_card_example_keeps_machine_anchors_with_chinese_body(self):
        card = EX / "method-card.example.md"
        self.assertTrue(method_card_ready(card))
        # A translated-header placeholder card must not pass the gate
        bad = EX.parent / "examples_bad_card.md"
        try:
            bad.write_text("# 方法卡\n主方法：M1\n基线：M0\n占位：待填\n", encoding="utf-8")
            self.assertFalse(method_card_ready(bad))
        finally:
            bad.unlink(missing_ok=True)

    def test_risk_probe_example_ready(self):
        self.assertTrue(risk_probe_ready(EX / "risk_probe_summary.example.json"))

    def test_decisions_example_passes_validation(self):
        errors = validate_decisions(EX / "decisions.example.jsonl", EX)
        self.assertEqual(errors, [])

    def test_manifest_example_validates_standalone(self):
        p = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_manifest.py"),
                            str(EX), str(EX / "manifest.example.json")],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_review_and_run_summary_shape(self):
        review = load_json("python_review.example.json")
        checks = review.get("checks") or {}
        for k in ("syntax", "input_contract", "method_alignment", "reproducibility", "output_contract"):
            self.assertEqual(checks.get(k, {}).get("status"), "PASS")
            self.assertTrue(checks[k].get("evidence"))
        summary = load_json("run_summary.example.json")
        roles = {m.get("role") for m in summary.get("methods", [])}
        self.assertIn("main_candidate", roles)
        self.assertIn("usable_baseline", roles)
        self.assertTrue(summary.get("verifier", {}).get("script"))

    def test_frozen_numbers_example_shape(self):
        frozen = load_json("frozen_numbers.example.json")
        claim = (frozen.get("claims") or [None])[0]
        self.assertIsNotNone(claim)
        for k in ("claim_id", "value", "source_file", "frozen_at", "decision_id"):
            self.assertIn(k, claim)


if __name__ == "__main__":
    unittest.main()
