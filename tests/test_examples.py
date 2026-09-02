#!/usr/bin/env python3
"""Golden-example guard: planning/examples artifacts must keep passing the
standalone structural checks promised in planning/examples/README.md."""
from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
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
        # A translated-header placeholder card must not pass the gate.
        # Use a temp dir, not the repo tree, so parallel runs cannot collide.
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "examples_bad_card.md"
            bad.write_text("# 方法卡\n主方法：M1\n基线：M0\n占位：待填\n", encoding="utf-8")
            self.assertFalse(method_card_ready(bad))

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

    def test_cross_example_consistency_frozen_value_matches_locator(self):
        # Regression: the frozen claim's value must equal what its
        # source_locator points at inside run_summary.example.json
        # (previously value 0.873 pointed at a cv of 0.18).
        frozen = load_json("frozen_numbers.example.json")
        claim = frozen["claims"][0]
        summary = load_json("run_summary.example.json")
        locator = claim["source_locator"]  # e.g. $.methods[0].metrics_summary.cv
        self.assertTrue(locator.startswith("$."))
        node = summary
        for part in locator[2:].split("."):
            idx = None
            if part.endswith("]"):
                head, _, tail = part.partition("[")
                idx = int(tail[:-1])
                part = head
            node = node[part]
            if idx is not None:
                node = node[idx]
        self.assertEqual(claim["value"], node)

    def test_cross_example_consistency_signoff_decision_exists(self):
        # The frozen claim's decision_id must resolve to a DECIDED
        # package_signoff record in the example ledger.
        frozen = load_json("frozen_numbers.example.json")
        decision_id = frozen["claims"][0]["decision_id"]
        found = False
        for line in (EX / "decisions.example.jsonl").read_text(encoding="utf-8-sig").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if (rec.get("decision_id") == decision_id
                    and rec.get("decision_type") == "package_signoff"
                    and rec.get("status") == "DECIDED"):
                found = True
        self.assertTrue(found, f"frozen claim decision {decision_id} not in ledger")

    def test_cross_example_consistency_fallback_trigger_uses_probe_fields(self):
        # Method-card fallback triggers must reference metrics that actually
        # exist in the probe summary (no invented fields).
        card = (EX / "method-card.example.md").read_text(encoding="utf-8-sig")
        probe = load_json("risk_probe_summary.example.json")
        # collect assumption-check names present in the probe
        probe_fields = set()
        for m in probe.get("methods", []):
            for chk in m.get("assumption_checks", []):
                probe_fields.add(chk.get("name"))
                probe_fields.add(chk.get("metric"))
        self.assertIn("indicator_redundancy", probe_fields)
        # the trigger text may only cite probe-produced terms
        trigger_block = card.split("## Fallback trigger", 1)[1].split("## Compact history", 1)[0]
        self.assertIn("indicator_redundancy", trigger_block)  # cited probe field exists
        self.assertNotIn("最大权重占比", trigger_block)  # removed invented metric
        self.assertNotIn("±10%", card)  # perturbation amounts are consistent at ±5%


if __name__ == "__main__":
    unittest.main()
