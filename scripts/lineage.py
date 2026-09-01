#!/usr/bin/env python3
"""Hash-based artifact lineage and stale detection."""
from __future__ import annotations
import argparse, hashlib, json, sys, time
from pathlib import Path

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def make_lineage(root: Path, artifact: Path, created_from: list[str], validated_by: list[str], consumed_by: list[str], decision_ids: list[str]) -> dict:
    def refs(paths):
        return [{'path':p,'sha256':sha256((root/p).resolve()) if (root/p).is_file() else None} for p in paths]
    return {'schema_version':1,'artifact':str(artifact.as_posix()),'status':'CURRENT','created_from':refs(created_from),'validated_by':refs(validated_by),'consumed_by':consumed_by,'decision_ids':decision_ids,'created_at':time.strftime('%Y-%m-%dT%H:%M:%S%z')}

def assess(root: Path, path: Path) -> dict:
    data=json.loads(path.read_text(encoding='utf-8-sig')); stale=[]
    for group in ('created_from','validated_by'):
        for ref in data.get(group,[]):
            p=(root/ref['path']).resolve()
            if not p.exists():stale.append({'path':ref['path'],'reason':'MISSING'})
            elif ref.get('sha256') and sha256(p)!=ref['sha256']:stale.append({'path':ref['path'],'reason':'HASH_CHANGED'})
    data['status']='STALE' if stale else 'CURRENT';data['stale_reasons']=stale;return data

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True)
    m=sub.add_parser('make');m.add_argument('root',type=Path);m.add_argument('artifact',type=Path);m.add_argument('--created-from',action='append',default=[]);m.add_argument('--validated-by',action='append',default=[]);m.add_argument('--consumed-by',action='append',default=[]);m.add_argument('--decision-id',action='append',default=[])
    a=sub.add_parser('assess');a.add_argument('root',type=Path);a.add_argument('lineage',type=Path)
    args=ap.parse_args()
    if args.cmd=='make':
        data=make_lineage(args.root.resolve(),args.artifact,args.created_from,args.validated_by,args.consumed_by,args.decision_id);print(json.dumps(data,ensure_ascii=False,indent=2));return 0
    data=assess(args.root.resolve(),args.lineage.resolve());print(json.dumps(data,ensure_ascii=False,indent=2));return 1 if data['status']!='CURRENT' else 0
if __name__=='__main__':raise SystemExit(main())
