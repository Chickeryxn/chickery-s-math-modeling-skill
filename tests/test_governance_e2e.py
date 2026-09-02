#!/usr/bin/env python3
"""Governance-layer e2e tests: the executable-contract validators and the
P1 fixes from the 0.7.0 audit (require_gate NameError, FAIL-verdict probes,
result_report deadlock, empty lineage, QA blocking propagation, drift checks).
"""
from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "plugins" / "mathmodeling-skills" / "hooks"))
import workflow_guard as wg
from unittest import mock

SKILL_SRC = """---
name: smoke-skill
description: smoke test skill
---
# Body
"""


def run_script(script, *args, cwd=None):
    return subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args],
                          capture_output=True, text=True, encoding="utf-8", cwd=cwd or ROOT)


class QaReportExitTests(unittest.TestCase):
    def test_gate_blocked_exits_2(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "planning" / "manifests").mkdir(parents=True)
            (root / "planning" / "manifests" / "Q1.json").write_text(
                json.dumps({"question_id": "Q1", "current_gate": "G1"}), encoding="utf-8")
            p = run_script("qa_report.py", str(root))
            self.assertEqual(p.returncode, 2)
            self.assertIn("GATE_BLOCKED", p.stdout)

    def test_not_run_exits_0(self):
        with tempfile.TemporaryDirectory() as td:
            p = run_script("qa_report.py", td)
            self.assertEqual(p.returncode, 0)
            self.assertIn("NOT_RUN", p.stdout)


class SyncDriftTests(unittest.TestCase):
    def make_trees(self, root):
        (root / ".codex" / "skills" / "smoke-skill").mkdir(parents=True)
        (root / ".codex" / "skills" / "smoke-skill" / "SKILL.md").write_text(SKILL_SRC, encoding="utf-8")
        (root / "AGENTS.md").write_text("# policy\n", encoding="utf-8")
        (root / "LICENSE").write_text("MIT\n", encoding="utf-8")
        p = run_script("sync_plugin.py", str(root))
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_sync_drift_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.make_trees(root)
            target = root / ".claude" / "skills" / "smoke-skill" / "SKILL.md"
            target.write_text(SKILL_SRC + "// mutated\n", encoding="utf-8")
            p = run_script("sync_plugin.py", str(root), "--check")
            self.assertEqual(p.returncode, 2)
            p = run_script("sync_plugin.py", str(root))
            self.assertEqual(p.returncode, 0)
            p = run_script("sync_plugin.py", str(root), "--check")
            self.assertEqual(p.returncode, 0)

    def test_skill_tree_drift_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.make_trees(root)
            (root / "plugins" / "mathmodeling-skills" / ".codex-plugin").mkdir(parents=True)
            (root / "plugins" / "mathmodeling-skills" / ".claude-plugin").mkdir(parents=True)
            (root / ".agents" / "plugins").mkdir(parents=True)
            for name in (".codex-plugin", ".claude-plugin"):
                (root / "plugins" / "mathmodeling-skills" / name / "plugin.json").write_text(
                    json.dumps({"name": "mathmodeling-skills", "version": "0.7.0"}), encoding="utf-8")
            (root / ".agents" / "plugins" / "marketplace.json").write_text(json.dumps({
                "name": "x", "plugins": [{"name": "mathmodeling-skills",
                                          "source": {"source": "local", "path": "./plugins/mathmodeling-skills"}}]}),
                encoding="utf-8")
            p = run_script("validate_skill_trees.py", str(root))
            self.assertEqual(p.returncode, 0, p.stderr)
            (root / ".agents" / "skills" / "smoke-skill" / "SKILL.md").write_text(SKILL_SRC + "// drift\n", encoding="utf-8")
            p = run_script("validate_skill_trees.py", str(root))
            self.assertEqual(p.returncode, 2)

    def test_sync_dry_run_reports_without_writing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.make_trees(root)
            target = root / ".claude" / "skills" / "smoke-skill" / "SKILL.md"
            target.write_text(SKILL_SRC + "// mutated\n", encoding="utf-8")
            p = run_script("sync_plugin.py", str(root), "--dry-run")
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("would_copy", p.stdout)
            p = run_script("sync_plugin.py", str(root), "--check")
            self.assertEqual(p.returncode, 2)  # dry-run must not have written

    def test_sync_keeps_target_extras_without_prune(self):
        # Regression: plain sync used to silently delete target-tree files that
        # do not exist in the source tree (user-local additions were lost).
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.make_trees(root)
            extra = root / ".claude" / "skills" / "local-skill" / "SKILL.md"
            extra.parent.mkdir(parents=True)
            extra.write_text("# local skill\n", encoding="utf-8")
            p = run_script("sync_plugin.py", str(root))
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("kept_extras", p.stdout)
            self.assertTrue(extra.is_file(), "extra file was silently deleted")
            p = run_script("sync_plugin.py", str(root), "--check")
            self.assertEqual(p.returncode, 2, "check must flag kept extras")
            p = run_script("sync_plugin.py", str(root), "--prune")
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertFalse(extra.is_file(), "--prune should remove extras")
            p = run_script("sync_plugin.py", str(root), "--check")
            self.assertEqual(p.returncode, 0, p.stderr)


class ManifestAndSnapshotCliTests(unittest.TestCase):
    def test_validate_manifest_overclaim_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "planning" / "manifests").mkdir(parents=True)
            m = root / "planning" / "manifests" / "Q1.json"
            m.write_text(json.dumps({"schema_version": 2, "question_id": "Q1", "rigor_profile": "lean",
                                     "current_gate": "G6", "status": "active", "artifacts": {},
                                     "allowed": {}, "blockers": [], "next_action": "x"}), encoding="utf-8")
            p = run_script("validate_manifest.py", str(root), str(m))
            self.assertEqual(p.returncode, 2)

    def test_validate_run_snapshot_cli(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "config.json").write_text("{}", encoding="utf-8")
            (root / "input.txt").write_text("i", encoding="utf-8")
            (root / "code.py").write_text("c", encoding="utf-8")
            command = ("python -c \"from pathlib import Path; "
                       "Path('result.json').write_text('r'); Path('validation.json').write_text('v')\"")
            args = [sys.executable, str(ROOT / "scripts" / "create_run_snapshot.py"),
                    "run", str(root), "runs/r1",
                    "--config", "config.json", "--inputs", "input.txt", "--code", "code.py",
                    "--planned-budget", '{"i":1}', "--actual-budget", '{"i":1}',
                    "--command", command,
                    "--result-ref", "result.json", "--validation-ref", "validation.json"]
            p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", cwd=root)
            self.assertEqual(p.returncode, 0, p.stderr[-300:])
            run_dir = root / "runs" / "r1"
            p = run_script("validate_run_snapshot.py", str(root), str(run_dir))
            self.assertEqual(p.returncode, 0, p.stderr)
            (root / "result.json").write_text("tampered", encoding="utf-8")
            p = run_script("validate_run_snapshot.py", str(root), str(run_dir))
            self.assertEqual(p.returncode, 2)


class WorkflowGuardRegressionTests(unittest.TestCase):
    def test_probe_with_fail_verdict_passes_gate2(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "planning" / "parse").mkdir(parents=True)
            (root / "planning" / "classification").mkdir(parents=True)
            (root / "planning" / "parse" / "problem_parse.json").write_text(
                json.dumps({"data_inventory": []}), encoding="utf-8")
            (root / "planning" / "classification" / "problem_classification.json").write_text(
                json.dumps({"task_type": "regression"}), encoding="utf-8")
            (root / "methods" / "Q1").mkdir(parents=True)
            (root / "methods" / "Q1" / "probes").mkdir(parents=True)
            (root / "methods" / "Q1" / "q1_method_card.md").write_text(
                "main_candidate: M1\nusable_baseline: M0\nRisk-probe summary\nBaseline validity\n", encoding="utf-8")
            (root / "methods" / "Q1" / "probes" / "risk_probe_summary.json").write_text(json.dumps({
                "methods": {"M1": {"verdict": "PASS", "output_degeneracy": {"status": "PASS", "metrics": {}}},
                            "M2": {"verdict": "FAIL"}}}), encoding="utf-8")
            state = wg.derive_state(root, "Q1")
            self.assertNotEqual(state["gate"], "G1")

    def test_result_report_min_gate_is_3(self):
        self.assertEqual(wg.ARTIFACT_MIN_GATE["result_report"], 3)
        self.assertEqual(wg.ARTIFACT_MIN_GATE["robustness_report"], 3)

    def test_require_gate_artifacts_branch_no_nameerror(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "planning" / "manifests").mkdir(parents=True)
            (root / "planning").mkdir(parents=True, exist_ok=True)
            (root / "planning" / "model_contract.json").write_text(
                json.dumps({"objective": {"output_contract": {"type": "json"}}}), encoding="utf-8")
            (root / "planning" / "manifests" / "Q1.json").write_text(json.dumps({
                "question_id": "Q1", "current_gate": "G6", "artifacts": {"model_code": "code/Q1/main.py"}}),
                encoding="utf-8")
            with mock.patch.object(wg, "derive_state",
                                   return_value={"gate": "G6", "checks": {"package_signoff": True}}):
                try:
                    wg.require_gate(root, "Q1", "model_code")
                    self.fail("expected a RuntimeError gate block, not a pass")
                except NameError as exc:
                    self.fail(f"NameError regression: {exc}")
                except RuntimeError:
                    pass  # GATE_BLOCKED from artifact lineage is the correct outcome


class EvidenceEscapeTests(unittest.TestCase):
    def test_work_record_gate_rejects_outside_path(self):
        import work_record as wr
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wr.cmd_init(type("A", (), {"root": root})())
            outside = Path(td).parent / "outside_probe.md"
            outside.write_text("x", encoding="utf-8")
            rc = wr.cmd_gate(type("A", (), {"root": root, "subject": "Q1", "gate": "G1",
                                            "evidence": [str(outside)], "note": None})())
            self.assertEqual(rc, 2)

    def test_training_scorecard_rejects_escape(self):
        import training_scorecard as ts
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            rd = root / "results" / "training" / "round1"
            rd.mkdir(parents=True)
            self.assertIsNone(ts.resolve_evidence(rd, str(root.parent / "outside.md")))
            self.assertIsNone(ts.resolve_evidence(rd, "../../../../etc/passwd"))


if __name__ == "__main__":
    unittest.main()
