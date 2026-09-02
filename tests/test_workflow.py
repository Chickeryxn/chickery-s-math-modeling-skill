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
        if gate in {'G2','G2.5','G3','G4','G5','G6'}:
            for rel,text in [('planning/parse/problem_parse.json',json.dumps({'data_inventory':[]})),('planning/classification/problem_classification.json','{}'),('workspace/data/data_profile.json','{}'),('methods/Q1/q1_method_card.md','# main_candidate usable_baseline\n## Baseline validity\n## Risk-probe summary'),('methods/Q1/probes/risk_probe_summary.json',json.dumps({'methods':{'M1':{'verdict':'PASS','output_degeneracy':{'status':'PASS','metrics':{}}}}}) )]:
                p=root/'planning/model_contract.json';p.write_text('{"schema_version": 1, "entities": [{"id": "entity"}], "inputs": [{"id": "input", "type": "numeric", "domain": "real", "unit": "unit", "source": "synthetic"}], "state_functions": [], "decision_variables": [{"id": "decision", "type": "numeric", "domain": "[0,1]", "unit": "unit"}], "hard_constraints": [{"id": "constraint", "expression_ref": "synthetic"}], "soft_constraints": [], "objective": {"sense": "MAXIMIZE", "value_ref": "score", "output_contract": {"type": "scalar"}}, "evaluator": {"evaluator_id": "synthetic", "implementation_ref": "verifier.py"}, "uncertainty": null, "validation_contract": {"independent_checks": ["main", "baseline", "verifier"], "tolerances": {"score": 1e-06}}}',encoding='utf-8')
                p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
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

    def test_unregistered_external_evidence_fails(self):
        root=self.make_root();path=root/'methods/Q1/q1_decisions.jsonl';path.write_text(json.dumps({'decision_id':'d','decision_type':'method_choice','status':'DECIDED','decided_by':'human','rationale':'user supplied','choice':'M1','evidence_refs':['evidence:not-registered'],'recorded_at':'2026-09-01','source':{'source_type':'user_answer','user_message_id':'u1','user_verbatim_answer':'I choose M1'}})+'\n',encoding='utf-8')
        # validate() returns the list of errors; it must be non-empty here.
        self.assertTrue(len(validate(path,root))>0)

    def test_relative_evidence_path_must_exist(self):
        root=self.make_root();path=root/'methods/Q1/q1_decisions.jsonl';path.write_text(json.dumps({'decision_id':'d','decision_type':'method_choice','status':'DECIDED','decided_by':'human','rationale':'user supplied','choice':'M1','evidence_refs':['methods/Q1/missing.json'],'recorded_at':'2026-09-01','source':{'source_type':'user_answer','user_message_id':'u1','user_verbatim_answer':'I choose M1'}})+'\n',encoding='utf-8')
        # validate() returns the list of errors; it must be non-empty here.
        self.assertTrue(len(validate(path,root))>0)

    def test_decision_validator_rejects_fake_human(self):
        root=self.make_root();path=root/'methods/Q1/q1_decisions.jsonl';path.write_text(json.dumps({'decision_id':'d','decision_type':'method_choice','status':'DECIDED','decided_by':'human','rationale':'AI made this','choice':'M1','evidence_refs':[],'recorded_at':'2026-09-01','source':{'source_type':'ai_summary'}})+'\n',encoding='utf-8')
        # validate() returns the list of errors; it must be non-empty here.
        self.assertTrue(len(validate(path,root))>0)

if __name__=='__main__':unittest.main()
