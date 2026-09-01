#!/usr/bin/env python3
"""Validate completed experiment snapshots and their hash-backed outputs."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from create_run_snapshot import validate

def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('run_dir',type=Path);a=ap.parse_args()
    result=validate(a.root.resolve(),a.run_dir.resolve());print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result.get('status')=='PASS' else 2
if __name__=='__main__':raise SystemExit(main())
