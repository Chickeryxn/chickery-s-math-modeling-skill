#!/usr/bin/env python3
"""Preflight bundle orchestration tests (0.8.0)."""
from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from preflight import audit


def write(p: Path, text='x'):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


class PreflightTests(unittest.TestCase):
    def test_empty_root_skips_everything_and_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = audit(root)
            self.assertEqual(out['status'], 'PASS')
            self.assertEqual(out['applied'], 0)
            self.assertEqual(out['skipped'], len(out['steps']))
            p = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'preflight.py'), str(root)],
                               capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(p.returncode, 0, p.stderr)

    def test_step_names_are_present(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            names = [s['name'] for s in audit(root)['steps']]
            self.assertEqual(names, ['claim_coverage', 'abstract_checker', 'ai_trace_checker',
                                     'latex_assembly', 'figure_consistency_check',
                                     'section_structure_check'])

    def test_manifest_triggers_claim_coverage_and_fails_without_sections(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / 'planning/manifests/Q1.json', json.dumps({
                'question_id': 'Q1', 'current_gate': 'G4'}))
            out = audit(root)
            self.assertEqual(out['steps'][0]['applied'], True)
            # claim_coverage blocks until every subquestion has a paper section
            self.assertEqual(out['status'], 'FAIL')
            self.assertIn('claim_coverage', out['failed'])

    def test_no_abstract_section_skips_abstract_checker(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / 'paper/sections/q1.tex', 'x')
            steps = {s['name']: s for s in audit(root)['steps']}
            self.assertFalse(steps['abstract_checker']['applied'])


if __name__ == '__main__':
    unittest.main()
