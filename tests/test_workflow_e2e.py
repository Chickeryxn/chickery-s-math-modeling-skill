from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from workflow_guard import derive_state,require_gate
from create_run_snapshot import run as run_snapshot

def write(path,text='x'):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')
def decision(dtype,did):
 return {'decision_id':did,'decision_type':dtype,'status':'DECIDED','decided_by':'human','choice':'user choice','rationale':'User supplied rationale','evidence_refs':[],'recorded_at':'2026-09-01T00:00:00Z','source':{'source_type':'user_answer','user_message_id':did+'-message','user_verbatim_answer':'User supplied answer'}}

class SyntheticWorkflowE2ETests(unittest.TestCase):
 def make_project(self,family):
  td=tempfile.TemporaryDirectory();root=Path(td.name);qid='Q1'
  write(root/'planning/parse/problem_parse.json',json.dumps({'data_inventory':[{'id':'synthetic'}]}))
  write(root/'planning/classification/problem_classification.json',json.dumps({'subquestions':[{'id':qid}]}))
  contract={'schema_version':1,'entities':[{'id':'entity'}],'inputs':[{'id':'input','type':'numeric','domain':'real','unit':'unit','source':'synthetic'}],'state_functions':[{'id':'state','arguments':['t'],'output':'real','definition_ref':'synthetic'}],'decision_variables':[{'id':'decision','type':'numeric','domain':'[0,1]','unit':'unit'}],'hard_constraints':[{'id':'constraint','expression_ref':'synthetic'}],'soft_constraints':[],'objective':{'sense':'MINIMIZE','value_ref':family+'_loss','output_contract':{'type':'scalar'}},'evaluator':{'evaluator_id':family+'_evaluator','implementation_ref':family+'_verifier.py'},'uncertainty':None,'validation_contract':{'independent_checks':['main','baseline','verifier'],'tolerances':{'loss':1e-6}}}
  write(root/'planning/model_contract.json',json.dumps(contract))
  write(root/'workspace/data/data_profile.json',json.dumps({'family':family}))
  write(root/'methods/Q1/q1_method_card.md','# Q1\nmain_candidate\nusable_baseline\n## Baseline validity\n## Risk-probe summary')
  write(root/'methods/Q1/probes/risk_probe_summary.json',json.dumps({'methods':{'main':{'verdict':'PASS'},'baseline':{'verdict':'PASS'}}}))
  write(root/'methods/Q1/q1_decisions.jsonl',json.dumps(decision('method_choice',family+'-method'))+'\n')
  write(root/'planning/manifests/Q1.json',json.dumps({'schema_version':1,'question_id':'Q1','rigor_profile':'lean','current_gate':'G2.5','status':'pending','artifacts':{},'allowed':{},'blockers':[],'next_action':{}}))
  write(root/'main.py',f'from pathlib import Path; Path("main_result.json").write_text("main-{family}")')
  write(root/'baseline.py',f'from pathlib import Path; Path("baseline_result.json").write_text("baseline-{family}")')
  write(root/'verifier.py',f'from pathlib import Path; Path("verifier_result.json").write_text("verifier-{family}")')
  self.addCleanup(td.cleanup);return root
 def add_g3(self,root,family):
  class A:pass
  a=A();a.config=[];a.inputs=['planning/model_contract.json'];a.code=['main.py'];a.planned_budget=json.dumps({'iterations':10});a.actual_budget=json.dumps({'iterations':10});a.degraded=False;a.degradation_reason=None;a.acceptance_impact=[];a.claim_restriction=[];a.command='python -c "from pathlib import Path; Path(\'result.json\').write_text(\'result\'); Path(\'validation.json\').write_text(\'validation\'); print(\'runner-ok\')"';a.result_ref='result.json';a.validation_ref='validation.json'
  run_snapshot(root,root/'results/Q1/experiments/run1',a)
  write(root/'results/Q1/experiments/run1/run_summary.json',json.dumps({'run_snapshot':'results/Q1/experiments/run1/run_metadata.json'}))
  write(root/'code/Q1/reviews/q1_review.json',json.dumps({'checks':{k:{'status':'PASS'} for k in ['syntax','input_contract','method_alignment','reproducibility','output_contract']}}))
 def test_three_families_reach_g4_only_after_human_judgment(self):
  for family in ('regression','scheduling','dynamic_event'):
   with self.subTest(family=family):
    root=self.make_project(family);self.assertEqual(derive_state(root,'Q1')['gate'],'G2.5')
    self.add_g3(root,family);self.assertEqual(derive_state(root,'Q1')['gate'],'G3')
    with (root/'methods/Q1/q1_decisions.jsonl').open('a',encoding='utf-8') as f:
     for dtype in ('result_verdict','stability_verdict','claim_scope'):f.write(json.dumps(decision(dtype,family+'-'+dtype))+'\n')
    write(root/'results/Q1/reports/q1_final_result_analysis.md');write(root/'robustness/Q1/q1_robustness_report.md')
    self.assertEqual(derive_state(root,'Q1')['gate'],'G4')
    with self.assertRaises(RuntimeError):require_gate(root,'Q1','frozen_numbers')
if __name__=='__main__':unittest.main()
