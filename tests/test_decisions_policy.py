#!/usr/bin/env python3
"""Decision-interface policy tests (0.8.0): explicit 'unavailable:' message-id
markers pass validation when the verbatim answer is present, and the marker is
never accepted without it."""
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_decisions import validate


def write(p: Path, text='x'):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


def record(message_id: str, verbatim: str = 'I choose M2') -> dict:
    return {'decision_id': 'q1_method_choice', 'decision_type': 'method_choice',
            'status': 'DECIDED', 'decided_by': 'human', 'choice': 'M2',
            'rationale': 'User supplied rationale', 'evidence_refs': [],
            'recorded_at': '2026-09-01T00:00:00Z',
            'source': {'source_type': 'user_answer', 'user_message_id': message_id,
                       'user_verbatim_answer': verbatim}}


class DecisionMarkerPolicyTests(unittest.TestCase):
    def test_unavailable_marker_accepted_with_verbatim(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger = root / 'methods/Q1/q1_decisions.jsonl'
            write(ledger, json.dumps(record('unavailable:codex')) + '\n')
            self.assertEqual(validate(ledger, root), [])

    def test_dsh_convention_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger = root / 'methods/Q1/q1_decisions.jsonl'
            write(ledger, json.dumps(record('dsh:sess-1:7')) + '\n')
            self.assertEqual(validate(ledger, root), [])

    def test_marker_without_verbatim_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger = root / 'methods/Q1/q1_decisions.jsonl'
            write(ledger, json.dumps(record('unavailable:codex', verbatim='  ')) + '\n')
            self.assertTrue(validate(ledger, root))


if __name__ == '__main__':
    unittest.main()
