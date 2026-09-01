#!/usr/bin/env python3
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from lineage import make_lineage, assess, assess_all

class LineageTests(unittest.TestCase):
    def test_hash_maps_and_propagation(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'input.txt').write_text('v1',encoding='utf-8');(root/'code.py').write_text('v1',encoding='utf-8');(root/'artifact.json').write_text('{}',encoding='utf-8')
            data=make_lineage(root,'artifact.json',['input.txt'],[],[],[],inputs=['input.txt'],code=['code.py']);p=root/'artifact.json.lineage.json';p.write_text(json.dumps(data),encoding='utf-8')
            (root/'input.txt').write_text('v2',encoding='utf-8');result=assess_all(root);self.assertEqual(result[0]['status'],'STALE');assess_all(root,write=True);self.assertEqual(json.loads(p.read_text())['status'],'STALE')

    def test_current_and_stale(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'input.txt').write_text('v1',encoding='utf-8')
            data=make_lineage(root,Path('artifact.json'),['input.txt'],[],[],[])
            p=root/'artifact.lineage.json';p.write_text(json.dumps(data),encoding='utf-8')
            self.assertEqual(assess(root,p)['status'],'CURRENT')
            (root/'input.txt').write_text('v2',encoding='utf-8')
            self.assertEqual(assess(root,p)['status'],'STALE')

if __name__=='__main__':unittest.main()
