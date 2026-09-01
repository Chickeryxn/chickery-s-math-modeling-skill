from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from create_run_snapshot import write_snapshot, finalize
class RunSnapshotTests(unittest.TestCase):
    def test_begin_finalize_records_actual_budget_and_refs(self):
        class A: pass
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'input.txt').write_text('i');(root/'code.py').write_text('c');(root/'config.json').write_text('{}');(root/'result.json').write_text('{}');(root/'validation.json').write_text('{}')
            a=A();a.config=['config.json'];a.inputs=['input.txt'];a.code=['code.py'];a.planned_budget='{"iterations":10}';a.actual_budget='{"iterations":7}';a.degraded=False;a.degradation_reason=None;a.command='python code.py'
            run=root/'runs/r1';d=write_snapshot(root,run,a);self.assertTrue(d['degraded']);self.assertEqual(d['status'],'RUNNING')
            f=finalize(root,run,'DEGRADED_SUCCESS','result.json','validation.json');self.assertEqual(f['status'],'DEGRADED_SUCCESS');self.assertEqual(f['result_ref'],'result.json')
if __name__=='__main__':unittest.main()
