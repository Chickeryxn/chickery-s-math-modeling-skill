#!/usr/bin/env python3
"""Regression tests for the fixes: probe-shape crash, gate deadlock, decision docs.

Covers:
1. A risk probe using the documented array shape must not crash derive_state.
2. A full G1..G6 progression must be able to produce solution_package,
   frozen_numbers, paper_section, and final_assembly through require_gate
   (previously a deadlock: producing the package/freeze required G5 while
   their absence capped the derived gate at G4).
3. A decision record shaped like the AGENTS.md example (recorded_at + source)
   must pass validate_decisions.
"""
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from workflow_guard import derive_state, require_gate, stage_hint, STAGE_HINTS
from validate_decisions import validate

def write(p: Path, text: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')

def decision(did: str, dtype: str, choice: str = 'user choice') -> dict:
    return {'decision_id':did,'decision_type':dtype,'status':'DECIDED','decided_by':'human',
            'choice':choice,'rationale':'User supplied rationale','evidence_refs':[],
            'recorded_at':'2026-09-01T00:00:00Z',
            'source':{'source_type':'user_answer','user_message_id':did+'-message',
                      'user_verbatim_answer':'User supplied answer'}}

def base_workspace():
    td=tempfile.TemporaryDirectory();root=Path(td.name)
    write(root/'planning/parse/problem_parse.json',json.dumps({'data_inventory':[]}))
    write(root/'planning/classification/problem_classification.json','{}')
    write(root/'planning/manifests/Q1.json',json.dumps({'current_gate':'G1'}))
    write(root/'methods/Q1/q1_method_card.md',
          '# main_candidate usable_baseline\n## Baseline validity\n## Risk-probe summary')
    write(root/'planning/model_contract.json',json.dumps({
        'schema_version':1,'entities':[{'id':'e'}],
        'inputs':[{'id':'i','type':'numeric','domain':'real','unit':'u','source':'s'}],
        'state_functions':[],'decision_variables':[{'id':'d','type':'numeric','domain':'[0,1]','unit':'u'}],
        'hard_constraints':[{'id':'c','expression_ref':'x'}],'soft_constraints':[],
        'objective':{'sense':'MAXIMIZE','value_ref':'s','output_contract':{'type':'scalar'}},
        'evaluator':{'evaluator_id':'e','implementation_ref':'v.py'},'uncertainty':None,
        'validation_contract':{'independent_checks':['main','baseline','verifier'],'tolerances':{'s':1e-6}}}))
    write(root/'methods/Q1/q1_decisions.jsonl',json.dumps(decision('d_method','method_choice','M1'))+'\n')
    return td, root

def add_g3_evidence(root: Path):
    runs=root/'results/Q1/experiments/round1'
    write(runs/'run_metadata.json',json.dumps({
        'schema_version':2,'run_id':'round1','planned_budget':{},'actual_budget':{},
        'budget_delta':{},'degraded':False,'input_manifest':{},'code_manifest':{},
        'config_hash':'x','command':'python main.py','environment':{},
        'status':'SUCCESS','return_code':0,'result_ref':'results/Q1/result.json',
        'validation_ref':'results/Q1/validation.json',
        'result_hash':'0'*64,'validation_hash':'0'*64,'executed_by_runner':True}))
    write(runs/'run_summary.json',json.dumps({'run_snapshot':'results/Q1/experiments/round1/run_metadata.json'}))
    write(root/'results/Q1/result.json','x');write(root/'results/Q1/validation.json','x')
    write(root/'code/Q1/reviews/q1_python_review.json',json.dumps({
        'checks':{'syntax':{'status':'PASS'},'input_contract':{'status':'PASS'},
                  'method_alignment':{'status':'PASS'},'reproducibility':{'status':'PASS'},
                  'output_contract':{'status':'PASS'}}}))
    write(root/'results/Q1/reports/q1_final_result_analysis.md','x')
    write(root/'robustness/Q1/q1_robustness_report.md','x')
    with open(root/'methods/Q1/q1_decisions.jsonl','a',encoding='utf-8') as f:
        for dtype in ('result_verdict','stability_verdict','claim_scope'):
            f.write(json.dumps(decision('d_'+dtype,dtype))+'\n')

class GateProgressionTests(unittest.TestCase):
    def test_documented_list_probe_shape_does_not_crash(self):
        td,root=base_workspace()
        write(root/'methods/Q1/probes/risk_probe_summary.json',json.dumps({
            'schema_version':1,'question_id':'Q1','generated_at':'2026-09-01','data_refs':[],
            'methods':[{'id':'M1','role':'usable_baseline','executability':{'status':'PASS'},
                        'data_coverage':{'status':'PASS'},'assumption_checks':[],
                        'output_degeneracy':{'status':'PASS'},
                        'perturbation_sensitivity':{'status':'PASS'},
                        'scale_check':{'status':'PASS'},'verdict':'PASS'}]}))
        try:
            state=derive_state(root,'Q1')
        except AttributeError as exc:
            self.fail(f'derive_state crashed on list-shaped probe: {exc}')
        self.assertEqual(state['gate'],'G2.5')  # screening done + choice present, runs missing
        td.cleanup()

    def test_dict_probe_shape_still_works(self):
        td,root=base_workspace()
        write(root/'methods/Q1/probes/risk_probe_summary.json',json.dumps({'methods':{'M1':{'verdict':'PASS','output_degeneracy':{'status':'PASS','metrics':{}}}}}))
        self.assertEqual(derive_state(root,'Q1')['gate'],'G2.5')
        td.cleanup()

    def test_full_progression_reaches_freeze_and_assembly(self):
        td,root=base_workspace()
        write(root/'methods/Q1/probes/risk_probe_summary.json',json.dumps({'methods':{'M1':{'verdict':'PASS','output_degeneracy':{'status':'PASS','metrics':{}}}}}))
        add_g3_evidence(root)
        # G1-G3 plus result evidence complete -> stuck at G4
        self.assertEqual(derive_state(root,'Q1')['gate'],'G4')
        # solution package may now be produced (previously deadlocked at G5)
        self.assertEqual(require_gate(root,'Q1','solution_package')['artifact_kind'],'solution_package')
        write(root/'results/Q1/reports/q1_solution_package_for_writer.md','x')
        with open(root/'methods/Q1/q1_decisions.jsonl','a',encoding='utf-8') as f:
            f.write(json.dumps(decision('d_signoff','package_signoff'))+'\n')
        # frozen numbers may now be produced (previously deadlocked at G5)
        self.assertEqual(require_gate(root,'Q1','frozen_numbers')['artifact_kind'],'frozen_numbers')
        write(root/'results/Q1/reports/frozen_numbers.json',json.dumps({'claims':[]}))
        # paper section requires G5
        self.assertEqual(derive_state(root,'Q1')['gate'],'G5')
        self.assertEqual(require_gate(root,'Q1','paper_section')['artifact_kind'],'paper_section')
        write(root/'paper/sections/q1.tex','x')
        # final assembly still blocked without the three audits
        with self.assertRaises(RuntimeError):
            require_gate(root,'Q1','final_assembly')
        for audit in ('cross_media_consistency_audit.md','completeness_audit.md'):
            write(root/'paper/audits'/audit,'x')
        write(root/'paper/qa_report.md','x')
        self.assertEqual(derive_state(root,'Q1')['gate'],'G6')
        self.assertEqual(require_gate(root,'Q1','final_assembly')['artifact_kind'],'final_assembly')
        td.cleanup()

    def test_stage_hint_present(self):
        self.assertTrue(stage_hint('G2').startswith('next:'))
        self.assertEqual(stage_hint('G6'), STAGE_HINTS['G6'])

    def test_agents_md_example_decision_passes_validation(self):
        td=tempfile.TemporaryDirectory()
        root=Path(td.name)
        ledger=root/'methods/Q1/q1_decisions.jsonl'
        # Fields mirror the AGENTS.md example (recorded_at + nested source).
        record={'decision_id':'q2_method_choice','decision_type':'method_choice','status':'DECIDED',
                'decided_by':'human','captured_in_mode':'learning','choice':'M2',
                'rationale':'M2 is selected because ...','evidence_refs':[],
                'recorded_at':'2026-09-01T12:00:00Z',
                'source':{'source_type':'user_answer','user_message_id':'msg-1',
                          'user_verbatim_answer':'I choose M2'}}
        write(ledger,json.dumps(record)+'\n')
        self.assertEqual(validate(ledger,root),[])
        td.cleanup()

if __name__=='__main__':unittest.main()
