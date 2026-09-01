#!/usr/bin/env python3
"""Validate append-only decision ledgers with verifiable user provenance."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
STATUSES={"SUGGESTED","PENDING","DECIDED","SUPERSEDED","STALE"}
DECIDED_TYPES={"framing","method_choice","fallback_activation","result_verdict","stability_verdict","assumption_necessity","claim_scope","package_signoff","submission_authorization"}
DATE_PREFIX=re.compile(r'^\d{4}-\d{2}-\d{2}')

def resolve_project_file(root:Path, ref:str)->Path|None:
    if not isinstance(ref,str) or not ref.strip(): return None
    if ref.startswith("evidence:"): return None
    raw=Path(ref)
    if raw.is_absolute():
        candidate=raw.resolve()
    else:
        candidate=(root/raw).resolve()
    try: candidate.relative_to(root.resolve())
    except ValueError: raise ValueError("evidence path escapes project root")
    return candidate

def validate(path:Path, root:Path)->list[str]:
    errors=[];seen={};records=[]
    registry_path=root/'planning'/'evidence_registry.json'
    registry={}
    if registry_path.is_file():
        try: registry=json.loads(registry_path.read_text(encoding='utf-8-sig'))
        except Exception as exc: errors.append(f'{registry_path}: invalid evidence registry: {exc}')
    registered=set((registry.get('evidence') or {}).keys()) if isinstance(registry,dict) else set()
    for no,line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(),1):
        if not line.strip():continue
        loc=f"{path}:{no}"
        try:r=json.loads(line)
        except json.JSONDecodeError as e:errors.append(f"{loc}: invalid JSON: {e}");continue
        if not isinstance(r,dict):errors.append(f"{loc}: record is not an object");continue
        for k in ('decision_id','decision_type','status','source','choice','evidence_refs','recorded_at'):
            if k not in r:errors.append(f"{loc}: missing {k}")
        did=r.get('decision_id')
        if not isinstance(did,str) or not did.strip():errors.append(f"{loc}: decision_id must be non-empty string")
        elif did in seen:errors.append(f"{loc}: duplicate decision_id {did}; first at line {seen[did]}")
        else:seen[did]=no
        ts=r.get('recorded_at')
        if not isinstance(ts,str) or not ts.strip():errors.append(f"{loc}: recorded_at must be a non-empty string")
        elif not DATE_PREFIX.match(ts):errors.append(f"{loc}: recorded_at must start with an ISO-8601 date (YYYY-MM-DD): {ts}")
        status=r.get('status')
        if status not in STATUSES:errors.append(f"{loc}: invalid status {status}")
        source=r.get('source') or {}
        if not isinstance(source,dict):errors.append(f"{loc}: source must be object");source={}
        if status=='DECIDED':
            if r.get('decided_by')!='human':errors.append(f"{loc}: DECIDED must use decided_by=human")
            if source.get('source_type')!='user_answer':errors.append(f"{loc}: DECIDED requires source_type=user_answer")
            for k in ('user_message_id','user_verbatim_answer'):
                if not isinstance(source.get(k),str) or not source[k].strip():errors.append(f"{loc}: DECIDED source missing {k}")
            if r.get('decision_type') not in DECIDED_TYPES:errors.append(f"{loc}: invalid DECIDED decision_type")
            if not isinstance(r.get('rationale'),str) or not r['rationale'].strip():errors.append(f"{loc}: DECIDED rationale must be non-empty")
        elif r.get('decided_by')=='human':errors.append(f"{loc}: non-DECIDED record cannot claim decided_by=human")
        if status in {'SUPERSEDED','STALE'} and not r.get('supersedes'):errors.append(f"{loc}: {status} requires supersedes")
        if r.get('supersedes') and r['supersedes'] not in seen:errors.append(f"{loc}: supersedes must point to an earlier record")
        refs=r.get('evidence_refs')
        if not isinstance(refs,list):errors.append(f"{loc}: evidence_refs must be an array");refs=[]
        for ref in refs:
            if isinstance(ref,str) and ref.startswith('evidence:'):
                if ref.split(':',1)[1] not in registered:errors.append(f'{loc}: unregistered evidence id: {ref}')
                continue
            try:candidate=resolve_project_file(root,ref)
            except ValueError as e:errors.append(f"{loc}: {e}");continue
            if candidate is None or not candidate.is_file():errors.append(f"{loc}: evidence ref must resolve to a file: {ref}")
        records.append(r)
    return errors

def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('ledger',type=Path);a=ap.parse_args()
    try:errors=validate(a.ledger.resolve(),a.root.resolve())
    except Exception as e:print(str(e),file=sys.stderr);return 2
    if errors:print('\n'.join(errors),file=sys.stderr);return 2
    print(f'DECISION_LEDGER_OK {a.ledger}');return 0
if __name__=='__main__':raise SystemExit(main())
