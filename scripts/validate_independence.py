#!/usr/bin/env python3
"""Validate static and declared runtime independence of main/baseline/verifier."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

RUNTIME_KEYS={'result_ref','validation_ref','input_manifest','run_snapshot','config_ref','result_source','validation_source'}

def digest(root: Path, ref: str) -> str:
    p=(root/ref).resolve()
    try:p.relative_to(root.resolve())
    except ValueError:raise ValueError(f'path escapes project root: {ref}')
    if not p.is_file():raise FileNotFoundError(p)
    return hashlib.sha256(p.read_bytes()).hexdigest()

def refs_from(obj):
    vals=[]
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k in RUNTIME_KEYS and isinstance(v,str):vals.append((k,v))
            elif isinstance(v,(dict,list)):vals.extend(refs_from(v))
    elif isinstance(obj,list):
        for x in obj:vals.extend(refs_from(x))
    return vals

def validate(root: Path, summary: Path) -> dict:
    data=json.loads(summary.read_text(encoding='utf-8-sig'));errors=[]
    methods=[m for m in data.get('methods',[]) if isinstance(m,dict)]
    roles={m.get('role'):m for m in methods}
    for role in ('main_candidate','usable_baseline'):
        if role not in roles:errors.append(f'missing role {role}')
    verifier=data.get('verifier') or {}
    if not verifier.get('script'):errors.append('missing verifier.script')
    role_refs={};runtime_refs={}
    for role,m in list(roles.items())+[('verifier',verifier)]:
        ref=m.get('script')
        if ref:
            try:role_refs[role]={'path':ref,'sha256':digest(root,ref)}
            except Exception as exc:errors.append(str(exc))
        runtime_refs[role]=set(v for _,v in refs_from(m))
    hashes=[x['sha256'] for x in role_refs.values()]
    if len(hashes)!=len(set(hashes)):errors.append('role script hashes are not distinct')
    comp=data.get('comparison') or {}
    if comp.get('main_metric_source') and comp.get('main_metric_source')==comp.get('baseline_metric_source'):errors.append('main and baseline share metric source')
    shared=runtime_refs.get('main_candidate',set()) & runtime_refs.get('usable_baseline',set())
    result_like=sorted(x for x in shared if any(t in x.lower() for t in ('result','output','metric','snapshot','validation')))
    if result_like:errors.append('main/baseline share result-like runtime refs: '+', '.join(result_like))
    declared=data.get('independence') or {}
    required_runtime={'result_ref','validation_ref','run_snapshot'}
    runtime_complete=all(required_runtime.issubset({k for k,_ in refs_from(m)}) for m in list(roles.values())+[verifier])
    status='NOT_INDEPENDENT' if errors else ('RUNTIME_INDEPENDENT' if declared.get('runtime_status')=='RUNTIME_INDEPENDENT' and runtime_complete else 'STATICALLY_DISTINCT')
    if declared.get('runtime_status')=='RUNTIME_INDEPENDENT' and not runtime_complete:errors.append('runtime independence declared without result_ref, validation_ref, and run_snapshot for every role');status='NOT_VERIFIED'
    return {'status':'PASS' if not errors else 'FAIL','independence_status':status,'errors':errors,'roles':role_refs,'runtime_refs':{k:sorted(v) for k,v in runtime_refs.items()},'shared_result_like_refs':result_like}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('summary',type=Path);a=ap.parse_args()
    try:r=validate(a.root.resolve(),a.summary.resolve())
    except Exception as exc:print(str(exc),file=sys.stderr);return 2
    print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['status']=='PASS' else 2
if __name__=='__main__':raise SystemExit(main())
