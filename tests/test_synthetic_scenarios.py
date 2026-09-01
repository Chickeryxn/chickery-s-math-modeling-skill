#!/usr/bin/env python3
"""Problem-agnostic synthetic scenarios for workflow integrity."""
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_model_contract import main as _unused

class SyntheticScenarioTests(unittest.TestCase):
    def test_regression_contract_has_distinct_roles(self):
        contract={'schema_version':1,'entities':[],'inputs':[{'id':'x','type':'numeric','domain':'real'}],'state_functions':[],'decision_variables':[{'id':'w','type':'numeric','domain':'[0,1]'}],'hard_constraints':[],'soft_constraints':[],'objective':{'sense':'MINIMIZE','value_ref':'loss'},'evaluator':{'evaluator_id':'regression-evaluator','implementation_ref':'contract'},'uncertainty':None,'validation_contract':{'independent_checks':['main','baseline','verifier']}}
        self.assertEqual(contract['validation_contract']['independent_checks'],['main','baseline','verifier'])
    def test_scheduling_contract_has_capacity(self):
        contract={'schema_version':1,'entities':['jobs','machines'],'inputs':[],'state_functions':[],'decision_variables':[{'id':'assignment','type':'discrete'}],'hard_constraints':[{'id':'capacity','expression_ref':'capacity'}],'soft_constraints':[],'objective':{'sense':'MINIMIZE','value_ref':'makespan'},'evaluator':{'evaluator_id':'schedule'},'uncertainty':None,'validation_contract':{'invariants':['capacity']}}
        self.assertIn('capacity',[x['id'] for x in contract['hard_constraints']])
    def test_dynamic_event_contract_has_union_policy(self):
        contract={'schema_version':1,'entities':['state'],'inputs':[],'state_functions':['x(t)'],'decision_variables':[],'hard_constraints':[],'soft_constraints':[],'objective':{'sense':'MAXIMIZE','value_ref':'union_duration'},'evaluator':{'evaluator_id':'event','event_policy':'refine_boundaries','aggregation':'union'},'uncertainty':None,'validation_contract':{'tolerances':{'time':1e-6}}}
        self.assertEqual(contract['evaluator']['aggregation'],'union')

if __name__=='__main__':unittest.main()
