#!/usr/bin/env python3
"""Create an immutable, hash-addressed experiment run snapshot."""
from __future__ import annotations
import argparse, hashlib, json, os, platform, shlex, subprocess, sys, time
from pathlib import Path

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def files_manifest(root: Path, paths: list[str]) -> dict:
    out={}
    for raw in paths:
        p=(root/raw).resolve()
        if not p.exists(): raise FileNotFoundError(p)
        if p.is_file(): out[str(p.relative_to(root))]=sha256(p)
        else:
            for child in p.rglob('*'):
                if child.is_file():out[str(child.relative_to(root))]=sha256(child)
    return dict(sorted(out.items()))

def write_snapshot(root: Path, run_dir: Path, args):
    run_dir.mkdir(parents=True,exist_ok=False)
    config_manifest=files_manifest(root,args.config) if args.config else {}
    input_manifest=files_manifest(root,args.inputs) if args.inputs else {}
    code_manifest=files_manifest(root,args.code) if args.code else {}
    config_hash=hashlib.sha256(json.dumps(config_manifest,sort_keys=True).encode()).hexdigest()
    planned=json.loads(args.planned_budget) if args.planned_budget else {}
    actual=json.loads(args.actual_budget) if args.actual_budget else planned
    degraded=bool(args.degraded or planned!=actual)
    metadata={
      'run_id':run_dir.name,'schema_version':1,'planned_budget':planned,'actual_budget':actual,
      'degraded':degraded,'degradation_reason':args.degradation_reason if degraded else None,
      'input_manifest':input_manifest,'code_manifest':code_manifest,
      'config_manifest':config_manifest,'config_hash':config_hash,
      'command':args.command,'environment':{'python':sys.version,'platform':platform.platform(),'cwd':str(root)},
      'status':'RUNNING','started_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'result_ref':None,'validation_ref':None
    }
    (run_dir/'config_snapshot.json').write_text(json.dumps({'planned_budget':planned,'actual_budget':actual,'config_manifest':config_manifest},ensure_ascii=False,indent=2),encoding='utf-8')
    (run_dir/'config_hash.txt').write_text(config_hash+'\n',encoding='utf-8')
    (run_dir/'input_manifest.json').write_text(json.dumps(input_manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (run_dir/'code_manifest.json').write_text(json.dumps(code_manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (run_dir/'environment.json').write_text(json.dumps(metadata['environment'],ensure_ascii=False,indent=2),encoding='utf-8')
    (run_dir/'command.txt').write_text(args.command+'\n',encoding='utf-8')
    (run_dir/'stdout.log').write_text('',encoding='utf-8');(run_dir/'stderr.log').write_text('',encoding='utf-8')
    (run_dir/'run_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    return metadata

def finalize(root: Path, run_dir: Path, status: str, result_ref: str, validation_ref: str) -> dict:
    path=run_dir/'run_metadata.json'
    data=json.loads(path.read_text(encoding='utf-8-sig'))
    if data.get('status') != 'RUNNING': raise RuntimeError('run is already finalized')
    for ref in (result_ref,validation_ref):
        if not (root/ref).is_file(): raise FileNotFoundError(root/ref)
    if status not in {'SUCCESS','FAILED','INTERRUPTED','DEGRADED_SUCCESS'}: raise ValueError('invalid final status')
    data['status']=status;data['result_ref']=result_ref;data['validation_ref']=validation_ref;data['finished_at']=time.strftime('%Y-%m-%dT%H:%M:%S%z')
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    return data

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    b=sub.add_parser('begin');b.add_argument('root',type=Path);b.add_argument('run_dir',type=Path);b.add_argument('--config',action='append',default=[]);b.add_argument('--inputs',action='append',default=[]);b.add_argument('--code',action='append',default=[]);b.add_argument('--planned-budget');b.add_argument('--actual-budget');b.add_argument('--degraded',action='store_true');b.add_argument('--degradation-reason',default=None);b.add_argument('--command',required=True)
    f=sub.add_parser('finalize');f.add_argument('root',type=Path);f.add_argument('run_dir',type=Path);f.add_argument('--status',required=True);f.add_argument('--result-ref',required=True);f.add_argument('--validation-ref',required=True)
    args=ap.parse_args()
    try:
        if args.mode=='begin': result=write_snapshot(args.root.resolve(),args.run_dir.resolve(),args)
        else: result=finalize(args.root.resolve(),args.run_dir.resolve(),args.status,args.result_ref,args.validation_ref)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except Exception as exc:print(str(exc),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
