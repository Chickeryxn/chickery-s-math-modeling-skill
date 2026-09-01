from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from create_run_snapshot import begin, finish, validate, run
class RunSnapshotTests(unittest.TestCase):
    def make_args(self, root):
        class A: pass
        a=A();a.config=['config.json'];a.inputs=['input.txt'];a.code=['code.py'];a.planned_budget='{"iterations":10}';a.actual_budget='{"iterations":7}';a.degraded=False;a.degradation_reason=None;a.acceptance_impact=[];a.claim_restriction=[];a.command='python code.py';return a
    def test_begin_requires_actual_budget_and_finalize_hashes_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'input.txt').write_text('i');(root/'code.py').write_text('c');(root/'config.json').write_text('{}');run=root/'runs/r1';a=self.make_args(root);d=begin(root,run,a);self.assertTrue(d['degraded']);self.assertEqual(d['status'],'RUNNING')
            (root/'result.json').write_text('result-v1');(root/'validation.json').write_text('validation-v1')
            with self.assertRaises(RuntimeError):finish(root,run,'SUCCESS','result.json','validation.json',1,True)
            f=finish(root,run,'DEGRADED_SUCCESS','result.json','validation.json',0,True);self.assertEqual(f['status'],'DEGRADED_SUCCESS');self.assertEqual(validate(root,run)['status'],'PASS')
    def test_unified_runner_executes_and_captures_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'input.txt').write_text('i');(root/'code.py').write_text('c');(root/'config.json').write_text('{}')
            args=self.make_args(root);args.actual_budget=args.planned_budget;args.command="python -c \"from pathlib import Path; Path('result.json').write_text('r'); Path('validation.json').write_text('v'); print('ok')\"";args.result_ref='result.json';args.validation_ref='validation.json';run_dir=root/'runs/r1'
            out=run(root,run_dir,args);self.assertEqual(out['status'],'SUCCESS');self.assertTrue((run_dir/'stdout.log').read_text().strip()=='ok');self.assertEqual(validate(root,run_dir)['status'],'PASS')

    def test_success_without_runner_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'config.json').write_text('{}');(root/'input.txt').write_text('i');(root/'code.py').write_text('c');(root/'result.json').write_text('r');(root/'validation.json').write_text('v');run=root/'runs/r1';d=begin(root,run,self.make_args(root))
            with self.assertRaises(RuntimeError):finish(root,run,'SUCCESS','result.json','validation.json',0,False)
if __name__=='__main__':unittest.main()
