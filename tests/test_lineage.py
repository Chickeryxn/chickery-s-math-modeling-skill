#!/usr/bin/env python3
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from lineage import make_lineage, assess

class LineageTests(unittest.TestCase):
    def test_current_and_stale(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'input.txt').write_text('v1',encoding='utf-8')
            data=make_lineage(root,Path('artifact.json'),['input.txt'],[],[],[])
            p=root/'artifact.lineage.json';p.write_text(json.dumps(data),encoding='utf-8')
            self.assertEqual(assess(root,p)['status'],'CURRENT')
            (root/'input.txt').write_text('v2',encoding='utf-8')
            self.assertEqual(assess(root,p)['status'],'STALE')

if __name__=='__main__':unittest.main()
