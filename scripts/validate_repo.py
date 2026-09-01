#!/usr/bin/env python3
"""Run repository-local contract, integrity, and test checks."""
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path

def run(cmd,cwd):
    p=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,encoding='utf-8',errors='replace')
    return {'command':cmd,'returncode':p.returncode,'stdout':p.stdout[-3000:],'stderr':p.stderr[-3000:]}

def main():
    try:sys.stdout.reconfigure(encoding='utf-8',errors='replace')
    except Exception:pass
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);a=ap.parse_args();r=a.root.resolve();reports=[];errors=[];py=sys.executable
    def add(cmd, required=True):
        rep=run(cmd,r);reports.append(rep)
        if required and rep['returncode']!=0:errors.append(cmd)
    add([py,str(r/'scripts/validate_skill_trees.py'),str(r)])
    add([py,str(r/'scripts/run_tests.py')])
    example=r/'planning/model_contract.example.json'
    if example.is_file():add([py,str(r/'scripts/validate_model_contract.py'),str(example)])
    for p in sorted((r/'planning/manifests').glob('*.json')):add([py,str(r/'scripts/validate_manifest.py'),str(r),str(p)])
    for p in sorted((r/'planning/manifests').glob('*.json')):add([py,str(r/'scripts/validate_artifacts.py'),str(r),str(p)])
    for p in sorted(r.glob('methods/Q*/**/*_decisions.jsonl')):add([py,str(r/'scripts/validate_decisions.py'),str(r),str(p)])
    for p in sorted(r.glob('results/**/run_metadata.json')):add([py,str(r/'scripts/validate_run_snapshot.py'),str(r),str(p.parent)])
    for p in sorted(r.glob('**/*.lineage.json')):add([py,str(r/'scripts/lineage.py'),'assess',str(r),str(p)])
    for p in sorted(r.glob('results/**/run_summary.json')):
        try:d=json.loads(p.read_text(encoding='utf-8-sig'))
        except Exception:continue
        if d.get('methods') or d.get('verifier'):
            add([py,str(r/'scripts/validate_independence.py'),str(r),str(p)])
    qa=run([py,str(r/'scripts/qa_report.py'),str(r)],r);reports.append(qa)
    add([py,str(r/'scripts/validate_upstream_assets.py'),str(r)])
    result={'status':'PASS' if not errors else 'FAIL','errors':errors,'checks':reports}
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if not errors else 2
if __name__=='__main__':raise SystemExit(main())
