#!/usr/bin/env python3
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from workflow_guard import require_gate, check_transition
from validate_decisions import validate

class WorkflowTests(unittest.TestCase):
    def make_root(self, gate='G1', decision=False):
        td=tempfile.TemporaryDirectory();root=Path(td.name)
        (root/'planning/manifests').mkdir(parents=True);(root/'methods/Q1').mkdir(parents=True)
        (root/'planning/manifests/Q1.json').write_text(json.dumps({'current_gate':gate}),encoding='utf-8')
        if decision:
            (root/'methods/Q1/q1_decisions.jsonl').write_text(json.dumps({'decision_id':'d1','decision_type':'method_choice','status':'DECIDED','decided_by':'human','choice':'M1','rationale':'user supplied','evidence_refs':[],'recorded_at':'2026-09-01T00:00:00Z','source':{'source_type':'user_answer','user_message_id':'u1','user_verbatim_answer':'I choose M1'}})+'\n',encoding='utf-8')
        self.addCleanup(td.cleanup);return root
    def test_code_blocked_before_human_decision(self):
        with self.assertRaises(RuntimeError):require_gate(self.make_root('G2'), 'Q1','model_code')
    def test_code_allowed_with_verifiable_decision(self):
        self.assertEqual(require_gate(self.make_root('G2.5',True),'Q1','model_code')['artifact_kind'],'model_code')
    def test_transition_regression_rejected(self):
        with self.assertRaises(RuntimeError):check_transition({'current_gate':'G3'},{'current_gate':'G2'})
    def test_paper_requires_claim_scope_or_authorization(self):
        root=self.make_root('G5',True)
        with self.assertRaises(RuntimeError):require_gate(root,'Q1','paper_section')

    def test_freeze_requires_package_signoff(self):
        root=self.make_root('G4',True)
        with self.assertRaises(RuntimeError):require_gate(root,'Q1','frozen_numbers')

    def test_decision_validator_rejects_fake_human(self):
        root=self.make_root();path=root/'methods/Q1/q1_decisions.jsonl';path.write_text(json.dumps({'decision_id':'d','decision_type':'method_choice','status':'DECIDED','decided_by':'human','rationale':'AI made this','choice':'M1','evidence_refs':[],'recorded_at':'2026-09-01','source':{'source_type':'ai_summary'}})+'\n',encoding='utf-8')
        self.assertTrue(validate(path,root))

if __name__=='__main__':unittest.main()
