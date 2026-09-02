#!/usr/bin/env python3
"""Hash-based artifact lineage with explicit current/stale/missing states."""
from __future__ import annotations
import sys
import argparse, hashlib, json, sys, time
from pathlib import Path


try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def root_path(root: Path, raw: str) -> Path:
    # Resolve root first (Windows 8.3 short-name safety: resolve() expands
    # RUNNER~1 -> runneradmin; comparing against an unresolved root raised
    # spurious 'not in subpath' errors).
    root = root.resolve()
    p = (root / raw).resolve()
    try:
        p.relative_to(root)
    except ValueError:
        raise ValueError(f'path escapes project root: {raw}')
    return p

def refs(root: Path, paths):
    out=[]
    for raw in paths:
        p=root_path(root, raw)
        out.append({'path':str(Path(raw).as_posix()),'exists':p.is_file(),'sha256':sha256(p) if p.is_file() else None})
    return out

def make(root: Path, artifact: str, created, validated, consumed, decisions, inputs=None, config=None, code=None):
    root_path(root, artifact)
    created_refs=refs(root, created); validated_refs=refs(root, validated)
    def hash_map(paths):
        out={}
        for raw in (paths or []):
            p=root_path(root, raw)
            if p.is_file(): out[str(Path(raw).as_posix())]=sha256(p)
        return out
    status='CURRENT' if all(x['exists'] for x in created_refs+validated_refs) else 'MISSING'
    return {'schema_version':2,'artifact':str(Path(artifact).as_posix()),'status':status,'created_from':created_refs,'validated_by':validated_refs,'consumed_by':consumed,'decision_ids':decisions,'input_hash':hash_map(inputs),'config_hash':hash_map(config),'code_hash':hash_map(code),'created_at':time.strftime('%Y-%m-%dT%H:%M:%S%z')}

def make_lineage(root, artifact, created, validated, consumed, decisions, inputs=None, config=None, code=None):
    return make(root, artifact, created, validated, consumed, decisions, inputs, config, code)

def assess(root: Path, path: Path):
    data=json.loads(path.read_text(encoding='utf-8-sig'));issues=[]
    # A lineage object with no provenance at all must not pass as CURRENT:
    # it would let a zero-trace artifact satisfy validate_artifacts.
    has_refs=bool(data.get('created_from') or data.get('validated_by'))
    has_hashes=any((data.get(g) or {}) for g in ('input_hash','config_hash','code_hash'))
    if not has_refs and not has_hashes:
        issues.append({'reason':'NO_PROVENANCE'})
    for group in ('created_from','validated_by'):
        for ref in data.get(group,[]):
            try: p=root_path(root, ref['path'])
            except ValueError: issues.append({'path':ref.get('path'),'reason':'ESCAPES_ROOT'}); continue
            if not p.is_file(): issues.append({'path':ref.get('path'),'reason':'MISSING'})
            elif ref.get('sha256') and sha256(p)!=ref['sha256']: issues.append({'path':ref.get('path'),'reason':'HASH_CHANGED'})
    for group in ('input_hash','config_hash','code_hash'):
        for raw,digest in (data.get(group) or {}).items():
            try: p=root_path(root, raw)
            except ValueError: issues.append({'path':raw,'reason':'ESCAPES_ROOT'}); continue
            if not p.is_file(): issues.append({'path':raw,'reason':'MISSING'})
            elif digest and sha256(p)!=digest: issues.append({'path':raw,'reason':'HASH_CHANGED'})
    data['status']='MISSING' if any(x['reason']=='MISSING' for x in issues) else ('STALE' if issues else 'CURRENT')
    data['stale_reasons']=issues
    return data

def assess_all(root: Path, write=False):
    output=[]
    for path in sorted(root.rglob('*.lineage.json')):
        data=assess(root,path); output.append({'path':str(path.relative_to(root)),'status':data['status'],'stale_reasons':data['stale_reasons']})
        if write: path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return output

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True)
    m=sub.add_parser('make');m.add_argument('root',type=Path);m.add_argument('artifact');m.add_argument('--created-from',action='append',default=[]);m.add_argument('--validated-by',action='append',default=[]);m.add_argument('--consumed-by',action='append',default=[]);m.add_argument('--decision-id',action='append',default=[]);m.add_argument('--input-ref',action='append',default=[]);m.add_argument('--config-ref',action='append',default=[]);m.add_argument('--code-ref',action='append',default=[]);m.add_argument('--out',type=Path,required=True)
    a=sub.add_parser('assess');a.add_argument('root',type=Path);a.add_argument('lineage',type=Path)
    p=sub.add_parser('propagate');p.add_argument('root',type=Path);p.add_argument('--write',action='store_true')
    x=ap.parse_args()
    try:
        if x.cmd=='make':
            data=make(x.root.resolve(),x.artifact,x.created_from,x.validated_by,x.consumed_by,x.decision_id,x.input_ref,x.config_ref,x.code_ref);x.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');code=0
        elif x.cmd=='assess': data=assess(x.root.resolve(),x.lineage.resolve());code=0 if data['status']=='CURRENT' else 1
        else: data={'status':'PASS','artifacts':assess_all(x.root.resolve(),x.write)};code=0 if all(x['status']=='CURRENT' for x in data['artifacts']) else 1
        print(json.dumps(data,ensure_ascii=False,indent=2));return code
    except Exception as exc: print(str(exc),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
