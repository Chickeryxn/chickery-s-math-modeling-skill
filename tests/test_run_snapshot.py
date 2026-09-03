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

    def test_interrupted_run_finalizes_as_interrupted(self):
        # Regression: a KeyboardInterrupt inside the unified runner used to
        # leave run_metadata.json RUNNING forever (unfinalizable snapshot).
        import unittest.mock as mock, create_run_snapshot as crs
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'input.txt').write_text('i');(root/'code.py').write_text('c');(root/'config.json').write_text('{}')
            args=self.make_args(root);args.result_ref='result.json';args.validation_ref='validation.json';run_dir=root/'runs/r1'
            orig = crs.subprocess.run
            def boom(*a, **k): raise KeyboardInterrupt()
            crs.subprocess.run = boom
            try:
                with self.assertRaises(KeyboardInterrupt):
                    run(root, run_dir, args)
            finally:
                crs.subprocess.run = orig
            md=json.loads((run_dir/'run_metadata.json').read_text(encoding='utf-8-sig'))
            self.assertEqual(md['status'],'INTERRUPTED')
            self.assertEqual(validate(root,run_dir)['status'],'PASS')

    def test_deterministic_rerun_with_identical_outputs_succeeds(self):
        # Regression: a byte-identical reproduction run (the case this tool
        # exists to certify) used to raise "did not create or change outputs"
        # and leave a permanently RUNNING snapshot. Identical outputs are a
        # legitimate deterministic rerun, recorded as an advisory flag.
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/'input.txt').write_text('i');(root/'code.py').write_text('c');(root/'config.json').write_text('{}')
            (root/'result.json').write_text('r');(root/'validation.json').write_text('v')
            args=self.make_args(root)
            args.actual_budget = args.planned_budget  # identical budgets: not degraded
            args.command=("python -c \"from pathlib import Path; "
                          "Path('result.json').write_text('r'); "
                          "Path('validation.json').write_text('v')\"")
            args.result_ref='result.json';args.validation_ref='validation.json'
            run_dir=root/'runs/r1'
            out=run(root,run_dir,args)
            self.assertEqual(out['status'],'SUCCESS')
            self.assertTrue(out.get('outputs_unchanged'))
            self.assertEqual(validate(root,run_dir)['status'],'PASS')
            md=json.loads((run_dir/'run_metadata.json').read_text(encoding='utf-8-sig'))
            self.assertEqual(md['status'],'SUCCESS')
            self.assertTrue(md.get('outputs_unchanged'))

    def test_missing_output_after_success_is_terminal_failed(self):
        # Regression: a raise between the process and finish() used to leave a
        # RUNNING snapshot that could never be finalized. A process that exits 0
        # without producing the required outputs now records a terminal FAILED
        # snapshot (executed by the runner, return code 0) instead.
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/'input.txt').write_text('i');(root/'code.py').write_text('c');(root/'config.json').write_text('{}')
            args=self.make_args(root)
            args.command='python -c "import sys; sys.stdout.write(\'no output files\')"'
            args.result_ref='result.json';args.validation_ref='validation.json'
            run_dir=root/'runs/r1'
            out=run(root,run_dir,args)
            self.assertEqual(out['status'],'FAILED')
            self.assertEqual(validate(root,run_dir)['status'],'PASS')
            self.assertIn('did not create required output',
                          (run_dir/'stderr.log').read_text())
if __name__=='__main__':unittest.main()
