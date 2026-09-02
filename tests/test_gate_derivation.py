from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from workflow_guard import derive_state,require_gate,QID_RE

def write(p,text='x'):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def decision(q,kind,did):
    return {'decision_id':did,'decision_type':kind,'status':'DECIDED','decided_by':'human','choice':'user-choice','rationale':'User supplied rationale','evidence_refs':[],'recorded_at':'2026-09-01T00:00:00Z','source':{'source_type':'user_answer','user_message_id':did+'-message','user_verbatim_answer':'User supplied answer'}}
class GateDerivationTests(unittest.TestCase):
    def test_gate_is_derived_from_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);qid='Q1';write(root/'planning/parse/problem_parse.json',json.dumps({'data_inventory':[]}));write(root/'planning/classification/problem_classification.json','{}');write(root/'methods/Q1/q1_method_card.md','# main_candidate usable_baseline\n## Baseline validity\n## Risk-probe summary');write(root/'methods/Q1/probes/risk_probe_summary.json',json.dumps({'methods':{'M1':{'verdict':'PASS','output_degeneracy':{'status':'PASS','metrics':{}}}}}));write(root/'workspace/data/data_profile.json','{}');write(root/'planning/model_contract.json',json.dumps({'schema_version': 1, 'entities': [{'id': 'entity'}], 'inputs': [{'id': 'input', 'type': 'numeric', 'domain': 'real', 'unit': 'unit', 'source': 'synthetic'}], 'state_functions': [], 'decision_variables': [{'id': 'decision', 'type': 'numeric', 'domain': '[0,1]', 'unit': 'unit'}], 'hard_constraints': [{'id': 'constraint', 'expression_ref': 'synthetic'}], 'soft_constraints': [], 'objective': {'sense': 'MAXIMIZE', 'value_ref': 'score', 'output_contract': {'type': 'scalar'}}, 'evaluator': {'evaluator_id': 'synthetic', 'implementation_ref': 'verifier.py'}, 'uncertainty': None, 'validation_contract': {'independent_checks': ['main', 'baseline', 'verifier'], 'tolerances': {'score': 1e-06}}}));write(root/'planning/manifests/Q1.json',json.dumps({'current_gate':'G2'}))
            self.assertEqual(derive_state(root,qid)['gate'],'G2')
            with self.assertRaises(RuntimeError):require_gate(root,qid,'model_code')
            write(root/'methods/Q1/q1_decisions.jsonl',json.dumps(decision(qid,'method_choice','method'))+'\n')
            self.assertEqual(derive_state(root,qid)['gate'],'G2.5')
            self.assertEqual(require_gate(root,qid,'model_code')['derived_gate'],'G2.5')
    def test_progression_reaches_g6_only_with_all_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);qid='Q1';write(root/'planning/parse/problem_parse.json',json.dumps({'data_inventory':[]}));write(root/'planning/classification/problem_classification.json','{}');write(root/'methods/Q1/q1_method_card.md','# main_candidate usable_baseline\n## Baseline validity\n## Risk-probe summary');write(root/'methods/Q1/probes/risk_probe_summary.json',json.dumps({'methods':{'M1':{'verdict':'PASS','output_degeneracy':{'status':'PASS','metrics':{}}}}}));write(root/'workspace/data/data_profile.json','{}');write(root/'methods/Q1/q1_decisions.jsonl','\n'.join(json.dumps(decision(qid,k,k)) for k in ['method_choice'])+'\n');write(root/'results/Q1/experiments/round1/result.json','result');write(root/'results/Q1/experiments/round1/validation.json','validation');write(root/'results/Q1/experiments/round1/run_snapshot.json',json.dumps({'run_id':'r1','status':'SUCCESS','return_code':0,'result_ref':'results/Q1/experiments/round1/result.json','validation_ref':'results/Q1/experiments/round1/validation.json','executed_by_runner':True}));write(root/'results/Q1/experiments/round1/run_summary.json',json.dumps({'run_snapshot':'results/Q1/experiments/round1/run_snapshot.json'}));write(root/'code/Q1/reviews/q1_review.json',json.dumps({'checks':{k:{'status':'PASS'} for k in ['syntax','input_contract','method_alignment','reproducibility','output_contract']}}));self.assertEqual(derive_state(root,qid)['gate'],'G3')
            with (root/'methods/Q1/q1_decisions.jsonl').open('a',encoding='utf-8') as f:f.write('\n'.join(json.dumps(decision(qid,k,k)) for k in ['result_verdict','stability_verdict','claim_scope'])+'\n')
            write(root/'results/Q1/reports/q1_final_result_analysis.md');write(root/'robustness/Q1/q1_robustness_report.md');self.assertEqual(derive_state(root,qid)['gate'],'G4')
            write(root/'results/Q1/reports/q1_solution_package_for_writer.md');write(root/'results/Q1/reports/frozen_numbers.json','{}');
            with (root/'methods/Q1/q1_decisions.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(decision(qid,'package_signoff','package'))+'\n')
            self.assertEqual(derive_state(root,qid)['gate'],'G5');write(root/'paper/sections/q1.tex');write(root/'paper/audits/cross_media_consistency_audit.md');write(root/'paper/audits/completeness_audit.md');write(root/'paper/qa_report.md');self.assertEqual(derive_state(root,qid)['gate'],'G6')
    def test_invalid_question_id_rejected(self):
        # Regression: qid was interpolated straight into paths/globs; a crafted id
        # like '../x' could read files outside the intended question directory.
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.assertTrue(QID_RE.match('Q1'))
            self.assertTrue(QID_RE.match('Q12'))
            self.assertFalse(QID_RE.match('q1'))
            self.assertFalse(QID_RE.match('../x'))
            self.assertFalse(QID_RE.match(''))
            for bad in ('../x','methods/..','Q1/../Q2',''):
                with self.assertRaises(ValueError):derive_state(root,bad)
    def test_snapshot_escaping_reference_rejected(self):
        # A run_summary pointing its snapshot at a path outside the root must not
        # satisfy the G3 run-summary check.
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);qid='Q1'
            write(root/'planning/parse/problem_parse.json',json.dumps({'data_inventory':[]}));write(root/'planning/classification/problem_classification.json','{}');write(root/'methods/Q1/q1_method_card.md','# main_candidate usable_baseline\n## Baseline validity\n## Risk-probe summary');write(root/'methods/Q1/probes/risk_probe_summary.json',json.dumps({'methods':{'M1':{'verdict':'PASS','output_degeneracy':{'status':'PASS','metrics':{}}}}}));write(root/'methods/Q1/q1_decisions.jsonl',json.dumps(decision(qid,'method_choice','m'))+'\n')
            write(root/'results/Q1/experiments/round1/run_summary.json',json.dumps({'run_snapshot':'../../outside_snapshot.json'}))
            outside=Path(td).parent/'outside_snapshot.json';write(outside,json.dumps({'run_id':'r','status':'SUCCESS','return_code':0,'result_ref':'x','validation_ref':'y','executed_by_runner':True}))
            state=derive_state(root,qid)
            self.assertNotEqual(state['gate'],'G3')
            outside.unlink(missing_ok=True)


if __name__=='__main__':unittest.main()
