#!/usr/bin/env python3
"""Repository-level integrity checks for the generic workflow project."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);args=ap.parse_args();r=args.root.resolve();errors=[];reports=[]
    commands=[
      [sys.executable,str(r/'scripts/validate_skill_trees.py'),str(r)],
      [sys.executable,str(r/'scripts/validate_model_contract.py'),str(r/'planning/model_contract.example.json')],
      [sys.executable,str(r/'scripts/run_tests.py')],
    ]
    commands += [[sys.executable,str(r/'scripts/validate_manifest.py'),str(p)] for p in sorted((r/'planning/manifests').glob('*.json'))]
    for command in commands:
      p=subprocess.run(command,cwd=r,text=True,capture_output=True)
      reports.append({'command':command,'returncode':p.returncode,'stdout':p.stdout[-2000:],'stderr':p.stderr[-2000:]})
      if p.returncode!=0:errors.append(command)
    result={'status':'PASS' if not errors else 'FAIL','reports':reports}
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if not errors else 2
if __name__=='__main__':raise SystemExit(main())
