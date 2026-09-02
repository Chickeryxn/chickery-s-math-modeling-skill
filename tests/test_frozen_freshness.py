#!/usr/bin/env python3
"""Frozen-number freshness checker tests (0.8.0)."""
from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_frozen_freshness import audit


def write(p: Path, text='x'):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


def claim(claim_id: str, source: str, frozen_at: str) -> dict:
    return {'claim_id': claim_id, 'value': 1.0, 'unit': 'u', 'source_file': source,
            'source_locator': '$.x', 'frozen_at': frozen_at,
            'frozen_by_skill': 'solution-package-builder', 'decision_id': 'd1'}


def frozen_file(root: Path, claims: list) -> Path:
    p = root / 'results/Q1/reports/frozen_numbers.json'
    write(p, json.dumps({'claims': claims}))
    return p


class FrozenFreshnessTests(unittest.TestCase):
    def test_current_claims_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / 'results/Q1/experiments/final/metrics/main.json', json.dumps({'rmse': 1.0}))
            frozen_file(root, [claim('q1_rmse', 'results/Q1/experiments/final/metrics/main.json',
                                     '2099-01-01T00:00:00Z')])
            out = audit(root)
            self.assertEqual(out['status'], 'PASS')
            self.assertEqual(out['claims_checked'], 1)

    def test_source_newer_than_frozen_at_is_stale(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / 'results/Q1/experiments/final/metrics/main.json', json.dumps({'rmse': 2.0}))
            frozen_file(root, [claim('q1_rmse', 'results/Q1/experiments/final/metrics/main.json',
                                     '2020-01-01T00:00:00Z')])
            out = audit(root)
            self.assertEqual(out['status'], 'FAIL')
            self.assertEqual(len(out['stale']), 1)
            self.assertIn('newer than frozen_at', out['stale'][0]['reason'])

    def test_missing_source_is_stale(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            frozen_file(root, [claim('q1_rmse', 'results/Q1/gone.json', '2099-01-01T00:00:00Z')])
            self.assertEqual(audit(root)['status'], 'FAIL')

    def test_map_shaped_frozen_file_supported(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / 'results/Q1/experiments/final/metrics/main.json', '1')
            p = root / 'results/Q1/reports/frozen_numbers.json'
            write(p, json.dumps({'q1_rmse': claim('q1_rmse',
                                                  'results/Q1/experiments/final/metrics/main.json',
                                                  '2099-01-01T00:00:00Z')}))
            self.assertEqual(audit(root)['status'], 'PASS')

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / 'results/Q1/experiments/final/metrics/main.json', '1')
            frozen_file(root, [claim('q1_rmse', 'results/Q1/experiments/final/metrics/main.json',
                                     '2099-01-01T00:00:00Z')])
            p = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'check_frozen_freshness.py'),
                                str(root)], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(p.returncode, 0, p.stderr)

    def test_escaping_source_is_rejected(self):
        # Regression: an absolute source path (or one escaping root via '..')
        # was resolved outside the workspace without a containment check.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outside = Path(td).parent / 'outside-secret.json'
            write(outside, 'x')
            frozen_file(root, [claim('q1_rmse', str(outside), '2099-01-01T00:00:00Z')])
            out = audit(root)
            self.assertEqual(out['status'], 'FAIL')
            self.assertIn('escapes project root', out['stale'][0]['reason'])
            outside.unlink(missing_ok=True)

    def test_dotdot_escaping_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / 'results/Q1/reports/frozen_numbers.json',
                  json.dumps({'claims': [claim('q1_rmse', '../../../../etc/hosts',
                                               '2099-01-01T00:00:00Z')]}))
            out = audit(root)
            self.assertEqual(out['status'], 'FAIL')
            self.assertIn('escapes project root', out['stale'][0]['reason'])

    def test_no_colon_offset_frozen_at_accepted(self):
        # Python 3.10's fromisoformat rejects '+0800' (no colon); the checker
        # must normalize it. frozen_at in the far future keeps the claim fresh.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / 'results/Q1/experiments/final/metrics/main.json', '1')
            frozen_file(root, [claim('q1_rmse', 'results/Q1/experiments/final/metrics/main.json',
                                     '2099-01-01T00:00:00+0800')])
            out = audit(root)
            self.assertEqual(out['status'], 'PASS', out)

    def test_naive_frozen_at_warns_but_passes(self):
        # A tz-less frozen_at is interpreted as UTC (advisory warning only).
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / 'results/Q1/experiments/final/metrics/main.json', '1')
            frozen_file(root, [claim('q1_rmse', 'results/Q1/experiments/final/metrics/main.json',
                                     '2099-01-01T00:00:00')])
            out = audit(root)
            self.assertEqual(out['status'], 'PASS')
            self.assertEqual(len(out['warnings']), 1)
            self.assertIn('no timezone', out['warnings'][0]['reason'])


if __name__ == '__main__':
    unittest.main()
