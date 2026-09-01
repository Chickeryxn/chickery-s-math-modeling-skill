from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate_model_contract import main as unused
class ModelContractTests(unittest.TestCase):
 def write(self,d):
  p=Path(d)/'contract.json';p.write_text(json.dumps({'schema_version':1,'entities':[{'id':'entity'}],'inputs':[{'id':'input','type':'numeric','domain':'real','unit':'u','source':'input'}],'state_functions':[{'id':'state','arguments':['t'],'output':'real','definition_ref':'state'}],'decision_variables':[{'id':'decision','type':'numeric','domain':'[0,1]','unit':'u'}],'hard_constraints':[{'id':'constraint','expression_ref':'constraint'}],'soft_constraints':[],'objective':{'sense':'MINIMIZE','value_ref':'loss','output_contract':{'type':'scalar'}},'evaluator':{'evaluator_id':'eval','implementation_ref':'eval.py'},'uncertainty':None,'validation_contract':{'independent_checks':['main','baseline','verifier'],'tolerances':{'loss':1e-6}}}),encoding='utf-8');return p
 def test_resolved_contract_passes(self):
  import subprocess
  with tempfile.TemporaryDirectory() as td:
   p=self.write(td);r=subprocess.run([sys.executable,str(ROOT/'scripts/validate_model_contract.py'),str(p),'--require-resolved'],capture_output=True,text=True);self.assertEqual(r.returncode,0)
 def test_duplicate_variable_fails(self):
  import subprocess
  with tempfile.TemporaryDirectory() as td:
   p=self.write(td);d=json.loads(p.read_text());d['decision_variables'].append(dict(d['decision_variables'][0]));p.write_text(json.dumps(d),encoding='utf-8');r=subprocess.run([sys.executable,str(ROOT/'scripts/validate_model_contract.py'),str(p)],capture_output=True,text=True);self.assertNotEqual(r.returncode,0)
if __name__=='__main__':unittest.main()
