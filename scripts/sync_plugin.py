#!/usr/bin/env python3
"""Portable skill-tree synchronizer; .codex/skills is the source tree."""
from __future__ import annotations
import sys
import argparse, hashlib, json, shutil, sys
from pathlib import Path


try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

def files(root):return sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name!='.DS_Store' and not p.name.endswith('.pyc'))
def sync_tree(src,dst):
    dst.mkdir(parents=True,exist_ok=True)
    source=set(files(src)); existing=set(files(dst))
    for rel in existing-source:(dst/rel).unlink()
    for rel in source:
        target=dst/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/rel,target)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--check',action='store_true');ap.add_argument('--dry-run',action='store_true',help='show what would be copied/removed without writing');args=ap.parse_args();r=args.root.resolve();src=r/'.codex/skills';targets=[r/'.claude/skills',r/'plugins/mathmodeling-skills/skills',r/'.agents/skills']
    if not src.is_dir():print('missing source tree',file=sys.stderr);return 2
    if args.dry_run:
        plan=[]
        for dst in targets:
            missing=[];extra=[]
            if dst.is_dir():
                existing={p.relative_to(dst).as_posix() for p in dst.rglob('*') if p.is_file()}
                source={p.relative_to(src).as_posix() for p in src.rglob('*') if p.is_file()}
                missing=sorted(source-existing);extra=sorted(existing-source)
            plan.append({'target':str(dst),'would_copy':missing,'would_remove':extra})
        if not (r/'plugins/mathmodeling-skills/AGENTS.md').is_file() or sha(r/'AGENTS.md')!=sha(r/'plugins/mathmodeling-skills/AGENTS.md'):
            plan.append({'target':'plugins/mathmodeling-skills/AGENTS.md','would_copy':['AGENTS.md'],'would_remove':[]})
        if not (r/'plugins/mathmodeling-skills/LICENSE').is_file() or sha(r/'LICENSE')!=sha(r/'plugins/mathmodeling-skills/LICENSE'):
            plan.append({'target':'plugins/mathmodeling-skills/LICENSE','would_copy':['LICENSE'],'would_remove':[]})
        print(json.dumps({'status':'DRY_RUN','plan':plan},ensure_ascii=False,indent=2));return 0
    if not args.check:
        for dst in targets:sync_tree(src,dst)
        shutil.copy2(r/'AGENTS.md',r/'plugins/mathmodeling-skills/AGENTS.md');shutil.copy2(r/'LICENSE',r/'plugins/mathmodeling-skills/LICENSE')
    src_hash={rel:sha(src/rel) for rel in files(src)}
    errors=[]
    for dst in targets:
        got={rel:sha(dst/rel) for rel in files(dst)} if dst.is_dir() else {}
        if got!=src_hash:errors.append(f'drift: {dst}')
    try:
        if sha(r/'AGENTS.md')!=sha(r/'plugins/mathmodeling-skills/AGENTS.md'):errors.append('AGENTS distribution drift')
    except FileNotFoundError:
        errors.append('AGENTS distribution file missing')
    try:
        if sha(r/'LICENSE')!=sha(r/'plugins/mathmodeling-skills/LICENSE'):errors.append('LICENSE distribution drift')
    except FileNotFoundError:
        errors.append('LICENSE distribution file missing')
    if errors:print('\n'.join(errors),file=sys.stderr);return 2
    print(json.dumps({'status':'PASS','source':str(src),'targets':[str(x) for x in targets],'files':len(src_hash)},ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
