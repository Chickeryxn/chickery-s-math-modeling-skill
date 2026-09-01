#!/usr/bin/env python3
"""Manifest-aware layered QA summary; does not turn local PASS into gate PASS."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

def artifact_status(root: Path, ref):
    p=(root/ref).resolve()
    return 'CURRENT' if p.is_file() else 'MISSING'

def audit(root: Path) -> dict:
    manifests=sorted((root/'planning'/'manifests').glob('Q*.json')) if (root/'planning'/'manifests').is_dir() else []
    questions=[]; blockers=[]
    for p in manifests:
        try:m=json.loads(p.read_text(encoding='utf-8-sig'))
        except Exception as exc:
            questions.append({'question_id':p.stem,'gate_status':'GATE_BLOCKED','mechanical':'NOT_RUN','semantic':'NOT_RUN','provenance':'NOT_RUN','issues':[str(exc)]});blockers.append(f'invalid manifest {p}');continue
        gate=m.get('current_gate','G1'); allowed=m.get('allowed',{}); issues=[]
        if m.get('blockers'):issues.extend(m['blockers'])
        gate_status='GATE_BLOCKED' if issues or allowed.get('freeze') is False and gate in {'G4','G5','G6'} else 'CURRENT'
        questions.append({'question_id':p.stem,'gate':gate,'gate_status':gate_status,'mechanical':'PASS' if not issues else 'CONDITIONAL','semantic':'CONDITIONAL' if issues else 'NOT_RUN','provenance':'HUMAN_JUDGMENT_PENDING' if issues else 'NOT_RUN','issues':issues})
        blockers.extend(f'{p.stem}: {x}' for x in issues)
    overall='GATE_BLOCKED' if blockers else ('NOT_RUN' if not questions else 'CONDITIONAL')
    return {'schema_version':1,'overall_status':overall,'questions':questions,'blocking_findings':blockers,'status_vocabulary':['MECHANICAL_PASS','SEMANTIC_PASS','CONDITIONAL','HUMAN_JUDGMENT_PENDING','GATE_BLOCKED','NOT_RUN']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path);args=ap.parse_args();data=audit(args.root.resolve());text=json.dumps(data,ensure_ascii=False,indent=2);print(text)
    if args.out:args.out.write_text(text+'\n',encoding='utf-8')
    return 0
if __name__=='__main__':raise SystemExit(main())
