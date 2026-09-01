from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate_artifacts import validate
from lineage import make_lineage
class ArtifactValidationTests(unittest.TestCase):
 def test_missing_lineage_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'artifact.json').write_text('{}');m=root/'manifest.json';m.write_text(json.dumps({'artifacts':{'result':'artifact.json'}}));self.assertEqual(validate(root,m)['status'],'FAIL')
 def test_current_lineage_passes(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'input.txt').write_text('v1');(root/'artifact.json').write_text('{}');ld=make_lineage(root,Path('artifact.json'),['input.txt'],[],[],[]);(root/'artifact.json.lineage.json').write_text(json.dumps(ld));m=root/'manifest.json';m.write_text(json.dumps({'artifacts':{'result':'artifact.json'}}));self.assertEqual(validate(root,m)['status'],'PASS')
if __name__=='__main__':unittest.main()
