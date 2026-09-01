from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from qa_report import audit
class QALayerTests(unittest.TestCase):
    def test_blocked_gate_is_not_overall_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'planning/manifests').mkdir(parents=True);(root/'planning/manifests/Q1.json').write_text(json.dumps({'current_gate':'G4','blockers':['need human result'],'allowed':{'freeze':False}}),encoding='utf-8')
            self.assertEqual(audit(root)['overall_status'],'GATE_BLOCKED')
if __name__=='__main__':unittest.main()
