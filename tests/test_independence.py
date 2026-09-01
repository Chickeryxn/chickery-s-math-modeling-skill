from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_independence import validate

class IndependenceTests(unittest.TestCase):
    def test_distinct_roles_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'main.py').write_text('main',encoding='utf-8'); (root/'baseline.py').write_text('baseline',encoding='utf-8'); (root/'verifier.py').write_text('verifier',encoding='utf-8')
            summary={'methods':[{'role':'main_candidate','script':'main.py'},{'role':'usable_baseline','script':'baseline.py'}],'verifier':{'script':'verifier.py'},'comparison':{'main_metric_source':'main-result','baseline_metric_source':'baseline-result'}}
            p=root/'summary.json';p.write_text(json.dumps(summary),encoding='utf-8')
            self.assertEqual(validate(root,p)['status'],'PASS')
    def test_shared_metric_source_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for name in ('main.py','baseline.py','verifier.py'):(root/name).write_text(name,encoding='utf-8')
            summary={'methods':[{'role':'main_candidate','script':'main.py'},{'role':'usable_baseline','script':'baseline.py'}],'verifier':{'script':'verifier.py'},'comparison':{'main_metric_source':'same','baseline_metric_source':'same'}}
            p=root/'summary.json';p.write_text(json.dumps(summary),encoding='utf-8')
            self.assertEqual(validate(root,p)['status'],'FAIL')
if __name__=='__main__':unittest.main()
