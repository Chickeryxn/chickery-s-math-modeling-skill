from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from qa_report import audit


def make_root(manifest: dict):
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    (root / 'planning' / 'manifests').mkdir(parents=True)
    (root / 'planning' / 'manifests' / 'Q1.json').write_text(
        json.dumps(manifest), encoding='utf-8')
    return td, root


class QALayerTests(unittest.TestCase):
    def test_blocked_gate_is_not_overall_pass(self):
        td, root = make_root({'current_gate': 'G4', 'blockers': ['need human result'],
                              'allowed': {'freeze': False}})
        self.assertEqual(audit(root)['overall_status'], 'GATE_BLOCKED')
        td.cleanup()

    def test_no_manifests_reports_not_run(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = audit(root)
            self.assertEqual(out['overall_status'], 'NOT_RUN')
            self.assertEqual(out['questions'], [])
        # empty manifests dir also counts as NOT_RUN
        with tempfile.TemporaryDirectory() as td2:
            root2 = Path(td2)
            (root2 / 'planning' / 'manifests').mkdir(parents=True)
            self.assertEqual(audit(root2)['overall_status'], 'NOT_RUN')

    def test_blocked_empty_workspace_is_gate_blocked_not_crash(self):
        # A manifest that claims a gate but has no framing evidence on disk is
        # correctly reported as blocked (engine derives G1 with blockers),
        # rather than crashing or passing.
        td, root = make_root({'question_id': 'Q1', 'rigor_profile': 'lean',
                              'current_gate': 'G1', 'status': 'active',
                              'artifacts': {}, 'allowed': {},
                              'blockers': [], 'next_action': {}})
        out = audit(root)
        self.assertEqual(out['overall_status'], 'GATE_BLOCKED')
        self.assertTrue(any('Q1' in str(f) for f in out['blocking_findings']))
        td.cleanup()

    def test_bad_manifest_json_reported_not_engine_crash(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        (root / 'planning' / 'manifests').mkdir(parents=True)
        (root / 'planning' / 'manifests' / 'Q1.json').write_text('not json', encoding='utf-8')
        out = audit(root)
        self.assertEqual(out['overall_status'], 'GATE_BLOCKED')
        self.assertTrue(any('Q1' in str(f) for f in out['blocking_findings']))
        td.cleanup()


if __name__ == '__main__':
    unittest.main()
