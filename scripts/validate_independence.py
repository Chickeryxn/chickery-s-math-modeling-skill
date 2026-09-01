#!/usr/bin/env python3
"""Check that main, baseline, and verifier are genuinely separate implementations."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

def digest(root, ref):
    p=(root/ref).resolve()
    if not p.is_file(): raise FileNotFoundError(p)
    return hashlib.sha256(p.read_bytes()).hexdigest()

def validate(root: Path, summary: Path) -> dict:
    data=json.loads(summary.read_text(encoding='utf-8-sig')); methods=data.get('methods',[]); errors=[]
    by_role={m.get('role'):m for m in methods}
    for role in ('main_candidate','usable_baseline'):
        if role not in by_role:errors.append(f'missing role {role}')
    refs={}
    for role,m in by_role.items():
        ref=m.get('script')
        if not ref:errors.append(f'{role}: missing script');continue
        try:refs[role]={'path':ref,'sha256':digest(root,ref)}
        except FileNotFoundError as exc:errors.append(str(exc))
    if len({x['sha256'] for x in refs.values()}) != len(refs):errors.append('main and baseline share identical script bytes')
    comparison=data.get('comparison') or {}
    if comparison.get('main_metric_source') and comparison.get('main_metric_source') == comparison.get('baseline_metric_source'):
        errors.append('main and baseline use the same metric source; independent execution evidence required')
    verifier=(data.get('verifier') or {}).get('script')
    if verifier:
        try:refs['verifier']={'path':verifier,'sha256':digest(root,verifier)}
        except FileNotFoundError as exc:errors.append(str(exc))
    role_hashes=[x['sha256'] for k,x in refs.items() if k in ('main_candidate','usable_baseline','verifier')]
    if len(role_hashes) != len(set(role_hashes)):errors.append('verifier/main/baseline implementation bytes are not all distinct')
    return {'status':'PASS' if not errors else 'FAIL','errors':errors,'roles':refs}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('summary',type=Path);args=ap.parse_args()
    try:result=validate(args.root.resolve(),args.summary.resolve())
    except Exception as exc:print(str(exc),file=sys.stderr);return 2
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['status']=='PASS' else 2
if __name__=='__main__':raise SystemExit(main())
