#!/usr/bin/env python3
"""Profile-aware gate derivation and structural depth checks (0.8.0).

Covers:
1. lean profile reaches the G4 result-judgment subgate without submission
   artifacts; the submission profile still requires final reports, package,
   freeze and sign-off before G4/G5.
2. 'auto' resolves rigor_profile from planning/session_config.json.
3. Structural depth: parse subquestions need goal + required_outputs;
   classification subquestions need a primary_type; usable risk-probe
   candidates need output-degeneracy evidence.
4. G3 gates on the latest experiment round only (older exploratory rounds are
   advisory, not blocking).
5. G1 additionally blocks when the parse declares human decisions that are
   needed but no verifiable human framing decision exists.
6. Advisory deadline hints and qa_report lean semantics.
"""
from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import workflow_guard as wg

def write(p: Path, text='x'):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')

def decision(dtype: str, did: str) -> dict:
    return {'decision_id': did, 'decision_type': dtype, 'status': 'DECIDED', 'decided_by': 'human',
            'choice': 'user choice', 'rationale': 'User supplied rationale', 'evidence_refs': [],
            'recorded_at': '2026-09-01T00:00:00Z',
            'source': {'source_type': 'user_answer', 'user_message_id': did + '-message',
                       'user_verbatim_answer': 'User supplied answer'}}

def full_framing(root: Path):
    write(root / 'planning/parse/problem_parse.json', json.dumps({
        'data_inventory': [{'id': 'd'}],
        'subquestions': [{'id': 'Q1', 'goal': 'predict y', 'required_outputs': ['y_hat']}]}))
    write(root / 'planning/classification/problem_classification.json', json.dumps({
        'subquestions': [{'id': 'Q1', 'primary_type': 'prediction'}]}))
    write(root / 'planning/manifests/Q1.json', json.dumps({
        'schema_version': 1, 'question_id': 'Q1', 'rigor_profile': 'lean', 'current_gate': 'G1',
        'status': 'active', 'artifacts': {}, 'allowed': {}, 'blockers': [], 'next_action': {}}))
    write(root / 'methods/Q1/q1_method_card.md',
          '# Q1 main_candidate usable_baseline\n## Baseline validity\n## Risk-probe summary\n正文理由可中文')
    write(root / 'methods/Q1/probes/risk_probe_summary.json', json.dumps({
        'methods': {'M1': {'verdict': 'PASS', 'output_degeneracy': {'status': 'PASS', 'metrics': {}}}}}))
    write(root / 'methods/Q1/q1_decisions.jsonl', json.dumps(decision('method_choice', 'm')) + '\n')

def add_g3_evidence(root: Path, round_name: str = 'round1', good: bool = True):
    base = root / 'results/Q1/experiments' / round_name
    write(base / 'result.json', 'r'); write(base / 'validation.json', 'v')
    if good:
        write(base / 'run_snapshot.json', json.dumps({
            'run_id': round_name, 'status': 'SUCCESS', 'return_code': 0,
            'result_ref': f'results/Q1/experiments/{round_name}/result.json',
            'validation_ref': f'results/Q1/experiments/{round_name}/validation.json',
            'executed_by_runner': True}))
    # A contract-shaped run summary with distinct main/baseline/verifier roles so
    # validate_independence treats the workspace as valid (STATICALLY_DISTINCT).
    for f, body in (('main.py', 'print("main")'), ('baseline.py', 'print("baseline")'),
                    ('verifier.py', 'print("verifier")')):
        write(root / 'code/Q1' / f, body)
    write(base / 'run_summary.json', json.dumps({
        'run_snapshot': f'results/Q1/experiments/{round_name}/run_snapshot.json',
        'methods': [
            {'method_id': 'M1', 'role': 'main_candidate', 'script': 'code/Q1/main.py',
             'result_ref': f'results/Q1/experiments/{round_name}/main_result.json',
             'validation_ref': f'results/Q1/experiments/{round_name}/main_validation.json'},
            {'method_id': 'M0', 'role': 'usable_baseline', 'script': 'code/Q1/baseline.py',
             'result_ref': f'results/Q1/experiments/{round_name}/base_result.json',
             'validation_ref': f'results/Q1/experiments/{round_name}/base_validation.json'}],
        'verifier': {'script': 'code/Q1/verifier.py',
                     'result_ref': f'results/Q1/experiments/{round_name}/verifier_result.json',
                     'validation_ref': f'results/Q1/experiments/{round_name}/verifier_validation.json'},
        'independence': {'runtime_status': 'STATICALLY_DISTINCT'}}))
    review = root / 'code/Q1/reviews/q1_review.json'
    write(review, json.dumps({'checks': {k: {'status': 'PASS', 'evidence': ['x']}
                                         for k in ['syntax', 'input_contract', 'method_alignment',
                                                   'reproducibility', 'output_contract']}}))

def add_verdicts(root: Path):
    with open(root / 'methods/Q1/q1_decisions.jsonl', 'a', encoding='utf-8') as f:
        for dtype in ('result_verdict', 'stability_verdict', 'claim_scope'):
            f.write(json.dumps(decision(dtype, dtype)) + '\n')


class ProfileGateTests(unittest.TestCase):
    def test_lean_reaches_result_judged_without_submission_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            full_framing(root)
            add_g3_evidence(root)
            # submission profile: final analysis + robustness still missing -> G3
            self.assertEqual(wg.derive_state(root, 'Q1', 'submission')['gate'], 'G3')
            # lean profile: verdicts not yet recorded -> G3
            self.assertEqual(wg.derive_state(root, 'Q1', 'lean')['gate'], 'G3')
            add_verdicts(root)
            # lean: human verdicts on computed evidence complete the result-judgment subgate
            lean_state = wg.derive_state(root, 'Q1', 'lean')
            self.assertEqual(lean_state['gate'], 'G4')
            self.assertEqual(lean_state['blockers'], [])
            self.assertIn('lean', lean_state.get('note', ''))
            # submission profile still blocked without final reports
            self.assertEqual(wg.derive_state(root, 'Q1', 'submission')['gate'], 'G3')
            # adding the submission reports advances the submission track to G4
            write(root / 'results/Q1/reports/q1_final_result_analysis.md')
            write(root / 'robustness/Q1/q1_robustness_report.md')
            self.assertEqual(wg.derive_state(root, 'Q1', 'submission')['gate'], 'G4')

    def test_auto_reads_session_config_profile(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.assertEqual(wg.read_profile(root, 'auto'), 'submission')
            write(root / 'planning/session_config.json', json.dumps({'rigor_profile': 'lean'}))
            self.assertEqual(wg.read_profile(root, 'auto'), 'lean')
            self.assertEqual(wg.read_profile(root, 'submission'), 'submission')

    def test_deep_parse_requires_goal_and_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / 'planning/parse/problem_parse.json', json.dumps({
                'data_inventory': [], 'subquestions': [{'id': 'Q1', 'goal': ''}]}))
            write(root / 'planning/classification/problem_classification.json', '{}')
            state = wg.derive_state(root, 'Q1')
            self.assertEqual(state['gate'], 'G1')
            self.assertIn('problem framing evidence incomplete', state['blockers'])

    def test_deep_classification_requires_primary_type(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / 'planning/parse/problem_parse.json', json.dumps({'data_inventory': []}))
            write(root / 'planning/classification/problem_classification.json',
                  json.dumps({'subquestions': [{'id': 'Q1'}]}))
            state = wg.derive_state(root, 'Q1')
            self.assertEqual(state['gate'], 'G1')

    def test_probe_usable_candidates_need_output_degeneracy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / 'planning/parse/problem_parse.json', json.dumps({'data_inventory': []}))
            write(root / 'planning/classification/problem_classification.json', '{}')
            write(root / 'methods/Q1/q1_method_card.md',
                  '# main_candidate usable_baseline\n## Baseline validity\n## Risk-probe summary')
            write(root / 'methods/Q1/probes/risk_probe_summary.json',
                  json.dumps({'methods': {'M1': {'verdict': 'PASS'}}}))
            self.assertEqual(wg.derive_state(root, 'Q1')['gate'], 'G1')

    def test_latest_round_only_gates_g3(self):
        for first_good, second_good in ((True, False), (False, True)):
            with self.subTest(first_good=first_good, second_good=second_good):
                with tempfile.TemporaryDirectory() as td:
                    root = Path(td)
                    full_framing(root)
                    add_g3_evidence(root, 'round1', good=first_good)
                    add_g3_evidence(root, 'round2', good=second_good)
                    gate = wg.derive_state(root, 'Q1')['gate']
                    if second_good:
                        # latest round (round2) is snapshot-backed -> G3
                        self.assertEqual(gate, 'G3')
                    else:
                        # latest round missing snapshot -> blocked at G2.5 even if round1 is fine
                        self.assertEqual(gate, 'G2.5')

    def test_framing_pending_blocks_g1(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root / 'planning/parse/problem_parse.json', json.dumps({
                'data_inventory': [], 'human_decisions_needed': ['output form']}))
            write(root / 'planning/classification/problem_classification.json', '{}')
            write(root / 'methods/Q1/q1_method_card.md',
                  '# main_candidate usable_baseline\n## Baseline validity\n## Risk-probe summary')
            write(root / 'methods/Q1/probes/risk_probe_summary.json', json.dumps({
                'methods': {'M1': {'verdict': 'PASS', 'output_degeneracy': {'status': 'PASS', 'metrics': {}}}}}))
            state = wg.derive_state(root, 'Q1')
            self.assertEqual(state['gate'], 'G1')
            self.assertIn('human framing decision pending', state['blockers'])
            write(root / 'planning/framing_decisions.jsonl',
                  json.dumps(decision('framing', 'framing-1')) + '\n')
            state = wg.derive_state(root, 'Q1')
            self.assertTrue(state['checks']['human_framing'])
            self.assertEqual(state['gate'], 'G2')

    def test_deadline_hints(self):
        now = datetime.now(timezone.utc)
        self.assertIsNone(wg.deadline_hint((now + timedelta(hours=72)).isoformat()))
        hint = wg.deadline_hint((now + timedelta(hours=2)).isoformat())
        self.assertIsNotNone(hint)
        self.assertIn('deadline <6h', hint)

    def test_deadline_hints_with_injected_clock(self):
        # Deterministic boundaries via the injectable `now` argument; the
        # previous variant depended on wall-clock timing around each branch.
        fixed = datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc)
        cases = [
            ('2026-08-31T23:00:00Z', 'deadline passed'),
            ('2026-09-01T05:00:00Z', 'deadline <6h'),
            ('2026-09-01T23:00:00Z', 'deadline <24h'),
            ('2026-09-02T23:00:00Z', 'deadline <48h'),
            ('2026-09-04T00:00:00Z', None),
        ]
        for deadline, expect in cases:
            got = wg.deadline_hint(deadline, now=fixed)
            if expect is None:
                self.assertIsNone(got, f'{deadline} should yield no hint')
            else:
                self.assertIsNotNone(got, f'{deadline} should yield a hint')
                self.assertIn(expect, got)

    def test_manifest_profile_snapshot_is_tolerated(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'planning' / 'manifests').mkdir(parents=True)
            m = root / 'planning/manifests/Q1.json'
            m.write_text(json.dumps({
                'schema_version': 1, 'question_id': 'Q1', 'rigor_profile': 'lean',
                'current_gate': 'G1', 'status': 'active', 'artifacts': {}, 'allowed': {},
                'blockers': [], 'next_action': {}, 'profile_snapshot': {'profile': 'lean'}}),
                encoding='utf-8')
            p = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'validate_manifest.py'),
                                str(root), str(m)], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(p.returncode, 0, p.stderr)

    def test_qa_report_lean_workspace_not_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            full_framing(root)
            add_g3_evidence(root)
            add_verdicts(root)
            # manifest records the lean profile; submission artifacts are absent
            manifest = root / 'planning/manifests/Q1.json'
            m = json.loads(manifest.read_text(encoding='utf-8-sig'))
            m['rigor_profile'] = 'lean'
            manifest.write_text(json.dumps(m), encoding='utf-8')
            p = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'qa_report.py'), str(root)],
                               capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            report = json.loads(p.stdout)
            self.assertNotEqual(report['overall_status'], 'GATE_BLOCKED')
            self.assertEqual(report['questions'][0]['derived_gate'], 'G4')


if __name__ == '__main__':
    unittest.main()
