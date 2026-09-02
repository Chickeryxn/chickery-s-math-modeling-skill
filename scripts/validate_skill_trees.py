#!/usr/bin/env python3
"""Cross-platform validation of skill trees, plugin manifests, and marketplace metadata."""
from __future__ import annotations
import sys
import argparse,hashlib,json,sys
from pathlib import Path


try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

def rel_files(root):return sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name!='.DS_Store' and not p.name.endswith('.pyc'))
def hashes(root):return {rel:hashlib.sha256((root/rel).read_bytes()).hexdigest() for rel in rel_files(root)}
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);a=ap.parse_args();r=a.root.resolve();errors=[]
 trees=[r/'.codex/skills',r/'.claude/skills',r/'plugins/mathmodeling-skills/skills',r/'.agents/skills'];base=trees[0]
 if not base.is_dir():errors.append('missing source skill tree')
 else:
  source=hashes(base)
  for tree in trees[1:]:
   if not tree.is_dir():errors.append(f'missing skill tree {tree}')
   elif hashes(tree)!=source:errors.append(f'skill tree drift: {tree}')
 try:
  codex=load(r/'plugins/mathmodeling-skills/.codex-plugin/plugin.json');claude=load(r/'plugins/mathmodeling-skills/.claude-plugin/plugin.json');market=load(r/'.agents/plugins/marketplace.json')
  if codex.get('version')!=claude.get('version'):errors.append('plugin manifest versions differ')
  entries=[x for x in market.get('plugins',[]) if x.get('name')=='mathmodeling-skills']
  if len(entries)!=1:errors.append('marketplace must contain exactly one mathmodeling-skills entry')
  elif entries[0].get('source')!={'source':'local','path':'./plugins/mathmodeling-skills'}:errors.append('marketplace source mismatch')
 except Exception as exc:errors.append(f'metadata invalid: {exc}')
 if errors:print('\n'.join(errors),file=sys.stderr);return 2
 print(json.dumps({'status':'PASS','skill_files':len(source),'trees':'synchronized','plugin_version':codex.get('version')},ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
