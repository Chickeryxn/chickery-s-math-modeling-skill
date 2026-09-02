#!/usr/bin/env python3
"""Tests for scripts/work_record.py (pure standard library)."""
from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import work_record as wr


def make_root():
    td = tempfile.TemporaryDirectory()
    return td, Path(td.name)


def run_cli(args):
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "work_record.py"), *args],
                          capture_output=True, text=True, encoding="utf-8")


class InitTests(unittest.TestCase):
    def test_init_creates_tree(self):
        td, root = make_root()
        self.assertEqual(wr.cmd_init(type("A", (), {"root": root})()), 0)
        for sub in wr.SUBDIRS:
            self.assertTrue((root / "records" / sub).is_dir())
        self.assertTrue((root / "records" / "README.md").is_file())
        td.cleanup()

    def test_init_idempotent(self):
        td, root = make_root()
        wr.cmd_init(type("A", (), {"root": root})())
        self.assertEqual(wr.cmd_init(type("A", (), {"root": root})()), 0)
        td.cleanup()


class LogTests(unittest.TestCase):
    def test_log_creates_session_and_entries(self):
        td, root = make_root()
        wr.cmd_init(type("A", (), {"root": root})())
        self.assertEqual(wr.cmd_log(type("A", (), {"root": root, "text": "parse done",
                                                  "subject": "Q1", "artifacts": ["planning/parse/problem_parse.json"],
                                                  "tags": ["parse"], "runtime": "dsh"})()), 0)
        sess = list((root / "records" / "sessions").glob("*.md"))[0]
        content = sess.read_text(encoding="utf-8")
        self.assertIn("date:", content)
        self.assertIn("runtime: dsh", content)
        self.assertIn("## ", content)
        self.assertIn("parse done", content)
        self.assertIn("[planning/parse/problem_parse.json]", content)
        td.cleanup()

    def test_log_second_entry_same_session(self):
        td, root = make_root()
        wr.cmd_init(type("A", (), {"root": root})())
        a = type("A", (), {"root": root, "text": "one", "subject": None, "artifacts": [],
                           "tags": None, "runtime": None})
        b = type("A", (), {"root": root, "text": "two", "subject": None, "artifacts": [],
                           "tags": None, "runtime": None})
        wr.cmd_log(a)
        wr.cmd_log(b)
        files = list((root / "records" / "sessions").glob("*.md"))
        self.assertEqual(len(files), 1)
        self.assertIn("two", files[0].read_text(encoding="utf-8"))
        td.cleanup()

    def test_detect_runtime_dsh(self):
        import os
        old = os.environ.get("DSH_SESSION_ID")
        os.environ["DSH_SESSION_ID"] = "session-1"
        try:
            self.assertEqual(wr.detect_runtime(), "dsh")
        finally:
            if old is None:
                os.environ.pop("DSH_SESSION_ID", None)
            else:
                os.environ["DSH_SESSION_ID"] = old


class GateTests(unittest.TestCase):
    def make_evidence(self, root, name="planning/parse/problem_parse.json"):
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("{}", encoding="utf-8")
        return p

    def test_gate_records_and_monotonic(self):
        td, root = make_root()
        wr.cmd_init(type("A", (), {"root": root})())
        self.make_evidence(root)
        g1 = type("A", (), {"root": root, "subject": "Q1", "gate": "G1",
                            "evidence": ["planning/parse/problem_parse.json"], "note": "ok"})
        g2 = type("A", (), {"root": root, "subject": "Q1", "gate": "G2",
                            "evidence": ["planning/parse/problem_parse.json"], "note": "ok"})
        self.assertEqual(wr.cmd_gate(g1), 0)
        self.assertEqual(wr.cmd_gate(g2), 0)
        content = (root / "records" / "gates" / "Q1.md").read_text(encoding="utf-8")
        self.assertIn("| G1 |", content)
        self.assertIn("| G2 |", content)
        td.cleanup()

    def test_gate_regression_rejected(self):
        td, root = make_root()
        wr.cmd_init(type("A", (), {"root": root})())
        self.make_evidence(root)
        ev = ["planning/parse/problem_parse.json"]
        wr.cmd_gate(type("A", (), {"root": root, "subject": "Q1", "gate": "G3", "evidence": ev, "note": None})())
        rc = wr.cmd_gate(type("A", (), {"root": root, "subject": "Q1", "gate": "G2", "evidence": ev, "note": None})())
        self.assertEqual(rc, 2)
        td.cleanup()

    def test_gate_missing_evidence_rejected(self):
        td, root = make_root()
        wr.cmd_init(type("A", (), {"root": root})())
        rc = wr.cmd_gate(type("A", (), {"root": root, "subject": "Q1", "gate": "G1",
                                        "evidence": ["nope.md"], "note": None})())
        self.assertEqual(rc, 2)
        td.cleanup()


class DecisionTests(unittest.TestCase):
    def test_decision_card_mirrors_ledger(self):
        td, root = make_root()
        wr.cmd_init(type("A", (), {"root": root})())
        ledger = root / "methods" / "Q1" / "q1_decisions.jsonl"
        ledger.parent.mkdir(parents=True)
        rec = {"decision_id": "q1_method_choice", "decision_type": "method_choice",
               "status": "DECIDED", "decided_by": "human", "choice": "M2",
               "rationale": "human verbatim rationale", "evidence_refs": [],
               "recorded_at": "2026-09-01T10:00:00+00:00",
               "source": {"source_type": "user_answer", "user_message_id": "dsh:session-1:3",
                          "user_verbatim_answer": "用 M2"}}
        ledger.write_text(json.dumps(rec, ensure_ascii=False) + "\n", encoding="utf-8")
        rc = wr.cmd_decision(type("A", (), {"root": root, "subject": "Q1",
                                            "decision_id": "q1_method_choice", "ledger": None})())
        self.assertEqual(rc, 0)
        card = list((root / "records" / "decisions").glob("*.md"))[0]
        content = card.read_text(encoding="utf-8")
        self.assertIn("human verbatim rationale", content)
        self.assertIn("dsh:session-1:3", content)
        td.cleanup()

    def test_decision_missing_id_rejected(self):
        td, root = make_root()
        wr.cmd_init(type("A", (), {"root": root})())
        ledger = root / "methods" / "Q1" / "q1_decisions.jsonl"
        ledger.parent.mkdir(parents=True)
        ledger.write_text("{}\n", encoding="utf-8")
        rc = wr.cmd_decision(type("A", (), {"root": root, "subject": "Q1",
                                            "decision_id": "missing", "ledger": None})())
        self.assertEqual(rc, 2)
        td.cleanup()


class IndexCheckTests(unittest.TestCase):
    def test_index_and_check_roundtrip(self):
        td, root = make_root()
        wr.cmd_init(type("A", (), {"root": root})())
        wr.cmd_log(type("A", (), {"root": root, "text": "x", "subject": None, "artifacts": [],
                                  "tags": None, "runtime": None})())
        self.assertEqual(wr.cmd_index(type("A", (), {"root": root})()), 0)
        self.assertEqual(wr.cmd_check(type("A", (), {"root": root})()), 0)
        td.cleanup()

    def test_check_detects_index_drift(self):
        td, root = make_root()
        wr.cmd_init(type("A", (), {"root": root})())
        wr.cmd_index(type("A", (), {"root": root})())
        wr.cmd_log(type("A", (), {"root": root, "text": "new", "subject": None, "artifacts": [],
                                  "tags": None, "runtime": None})())
        self.assertEqual(wr.cmd_check(type("A", (), {"root": root})()), 2)
        td.cleanup()

    def test_check_detects_broken_link(self):
        td, root = make_root()
        wr.cmd_init(type("A", (), {"root": root})())
        (root / "records" / "sessions" / "2026-09-01-001.md").write_text(
            "---\ndate: 2026-09-01\nsession: 2026-09-01-001\nruntime: codex\n---\n\n## 10:00:00 - x\n- 产物: [gone](gone.md)\n",
            encoding="utf-8")
        self.assertEqual(wr.cmd_check(type("A", (), {"root": root})()), 2)
        td.cleanup()

    def test_cli_end_to_end(self):
        td, root = make_root()
        p = run_cli(["init", str(root)])
        self.assertEqual(p.returncode, 0)
        p = run_cli(["check", str(root)])
        self.assertEqual(p.returncode, 0)
        td.cleanup()


class ReplayTests(unittest.TestCase):
    def make_artifacts(self, root):
        m = root / "planning" / "manifests" / "Q1.json"
        m.parent.mkdir(parents=True)
        m.write_text(json.dumps({"question": "Q1", "gate": "G2"}), encoding="utf-8")
        led = root / "methods" / "Q1" / "q1_decisions.jsonl"
        led.parent.mkdir(parents=True)
        led.write_text(json.dumps({"decision_id": "q1_method_choice", "decision_type": "method_choice",
                                   "status": "DECIDED", "choice": "M2",
                                   "recorded_at": "2026-09-01T10:00:00+00:00"}) + "\n", encoding="utf-8")
        rs = root / "results" / "Q1" / "experiments" / "round1" / "run_summary.json"
        rs.parent.mkdir(parents=True)
        rs.write_text(json.dumps({"question": "Q1", "round": 1, "status": "SUCCESS",
                                  "methods": ["M2"]}), encoding="utf-8")
        fz = root / "results" / "Q1" / "reports" / "frozen_numbers.json"
        fz.parent.mkdir(parents=True)
        fz.write_text(json.dumps({"claims": [{"claim_id": "c1"}, {"claim_id": "c2"}]}), encoding="utf-8")

    def test_replay_write_and_check(self):
        td, root = make_root()
        wr.cmd_init(type("A", (), {"root": root})())
        self.make_artifacts(root)
        rc = wr.cmd_replay(type("A", (), {"root": root, "date": "2026-09-01", "write": True})())
        self.assertEqual(rc, 0)
        f = root / "records" / "sessions" / "2026-09-01-replay.md"
        content = f.read_text(encoding="utf-8")
        self.assertIn("gate=G2", content)
        self.assertIn("q1_method_choice", content)
        self.assertIn("round1", content)
        self.assertIn("2 claim(s)", content)
        wr.cmd_index(type("A", (), {"root": root})())
        self.assertEqual(wr.cmd_check(type("A", (), {"root": root})()), 0)
        td.cleanup()

    def test_log_after_replay_uses_new_session(self):
        td, root = make_root()
        wr.cmd_init(type("A", (), {"root": root})())
        self.make_artifacts(root)
        wr.cmd_replay(type("A", (), {"root": root, "date": "2026-09-01", "write": True})())
        wr.cmd_log(type("A", (), {"root": root, "text": "manual entry", "subject": None,
                                  "artifacts": [], "tags": None, "runtime": None})())
        sessions = list((root / "records" / "sessions").glob("*.md"))
        names = [p.name for p in sessions]
        self.assertTrue(any(n.endswith("-replay.md") for n in names))
        manual = [p for p in sessions if not p.name.endswith("-replay.md")]
        self.assertEqual(len(manual), 1)
        self.assertIn("manual entry", manual[0].read_text(encoding="utf-8"))
        replay = [p for p in sessions if p.name.endswith("-replay.md")][0]
        self.assertNotIn("manual entry", replay.read_text(encoding="utf-8"))
        td.cleanup()


if __name__ == "__main__":
    unittest.main()
