#!/usr/bin/env python3
"""Require and validate lineage for manifest-declared canonical artifacts."""
from __future__ import annotations
import sys
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lineage import assess


try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

def artifact_lineage_path(root,ref):
 p=(root/ref).resolve()
 return Path(str(p)+'.lineage.json')
def validate(root,manifest):
 data=json.loads(manifest.read_text(encoding='utf-8-sig'));errors=[];checked=[]
 for name,ref in (data.get('artifacts') or {}).items():
  if not isinstance(ref,str) or not ref.strip():continue
  p=(root/ref).resolve()
  try:p.relative_to(root.resolve())
  except ValueError:errors.append(f'{name}: artifact escapes project root');continue
  if not p.is_file():errors.append(f'{name}: artifact missing: {ref}');continue
  lp=artifact_lineage_path(root,ref)
  if not lp.is_file():errors.append(f'{name}: lineage missing: {lp.relative_to(root)}');continue
  try:ld=assess(root,lp)
  except Exception as exc:errors.append(f'{name}: invalid lineage: {exc}');continue
  checked.append({'artifact':ref,'lineage':str(lp.relative_to(root)),'status':ld.get('status')})
  if ld.get('status')!='CURRENT':errors.append(f'{name}: lineage {ld.get("status")}')
 return {'status':'PASS' if not errors else 'FAIL','errors':errors,'checked':checked}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('manifest',type=Path);a=ap.parse_args()
 try:r=validate(a.root.resolve(),a.manifest.resolve())
 except Exception as exc:print(str(exc),file=sys.stderr);return 2
 print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['status']=='PASS' else 2
if __name__=='__main__':raise SystemExit(main())
