#!/usr/bin/env python3
"""Produce evidence-aware layered QA without collapsing local checks into gate success."""
from __future__ import annotations
import sys
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from workflow_guard import derive_state
from create_run_snapshot import validate as validate_run
from lineage import assess as assess_lineage
from validate_independence import validate as validate_independence


try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

STATUSES=['MECHANICAL_PASS','SEMANTIC_PASS','CONDITIONAL','HUMAN_JUDGMENT_PENDING','GATE_BLOCKED','NOT_RUN','CURRENT','STALE','MISSING']

def q_artifact_lineages(root,qid,manifest=None):
    candidates=list((root/'planning').rglob(f'{qid}*.lineage.json'))+list((root/'results'/qid).rglob('*.lineage.json'))+list((root/'methods'/qid).rglob('*.lineage.json'))+list((root/'robustness'/qid).rglob('*.lineage.json'))
    artifact_refs=[]
    if isinstance(manifest,dict):
        artifact_refs=[v for v in (manifest.get('artifacts') or {}).values() if isinstance(v,str) and (root/v).is_file()]
    if not candidates and not artifact_refs:return {'status':'NOT_RUN','errors':[],'checked':0}
    errors=[];statuses=[];lineage_names={p.name for p in candidates}
    for ref in artifact_refs:
        name=Path(ref).name
        # lineage files follow the `<artifact>.lineage.json` convention; the
        # old second disjunct (p.stem == name) could never be true for such
        # files and has been removed.
        if f'{name}.lineage.json' not in lineage_names:
            errors.append({'path':ref,'reason':'LINEAGE_MISSING'});statuses.append('MISSING')
    for p in candidates:
        try:d=assess_lineage(root,p);statuses.append(d.get('status'));errors.extend(d.get('stale_reasons',[]))
        except Exception as exc:errors.append({'path':str(p),'reason':str(exc)});statuses.append('STALE')
    if 'STALE' in statuses:return {'status':'STALE','errors':errors,'checked':len(candidates)}
    if 'MISSING' in statuses:return {'status':'MISSING','errors':errors,'checked':len(candidates)}
    return {'status':'CURRENT','errors':errors,'checked':len(candidates)}

def q_independence(root,qid):
    summaries=list((root/'results'/qid).rglob('run_summary.json')) if (root/'results'/qid).is_dir() else []
    if not summaries:return {'status':'NOT_RUN','errors':[]}
    statuses=[];errors=[]
    for p in summaries:
        try:
            d=validate_independence(root,p);statuses.append(d.get('independence_status'));errors.extend(d.get('errors',[]))
        except Exception as exc:statuses.append('NOT_VERIFIED');errors.append(str(exc))
    if 'NOT_INDEPENDENT' in statuses:return {'status':'NOT_INDEPENDENT','errors':errors}
    if 'RUNTIME_INDEPENDENT' in statuses:return {'status':'RUNTIME_INDEPENDENT','errors':errors}
    if 'STATICALLY_DISTINCT' in statuses:return {'status':'STATICALLY_DISTINCT','errors':errors}
    return {'status':'NOT_VERIFIED','errors':errors}

def q_runs(root,qid):
    runs=list((root/'results'/qid).rglob('run_metadata.json')) if (root/'results'/qid).is_dir() else []
    if not runs:return {'status':'NOT_RUN','errors':[],'checked':0}
    errors=[];states=[]
    for p in runs:
        try:d=validate_run(root,p.parent);states.append(d.get('status'));errors.extend(d.get('errors',[]))
        except Exception as exc:states.append('FAIL');errors.append(str(exc))
    return {'status':'PASS' if all(x=='PASS' for x in states) else 'CONDITIONAL','errors':errors,'checked':len(runs)}

def audit(root):
    manifests=sorted((root/'planning'/'manifests').glob('Q*.json')) if (root/'planning'/'manifests').is_dir() else []
    if not manifests:return {'schema_version':2,'overall_status':'NOT_RUN','questions':[],'blocking_findings':[],'status_vocabulary':STATUSES}
    questions=[];blocking=[]
    for p in manifests:
        qid=p.stem
        try:
            m=json.loads(p.read_text(encoding='utf-8-sig'))
            prof=m.get('rigor_profile') if m.get('rigor_profile') in ('lean','submission') else 'submission'
            state=derive_state(root,qid,prof);lineage=q_artifact_lineages(root,qid,m);runs=q_runs(root,qid);ind=q_independence(root,qid)
            gate='GATE_BLOCKED' if state['blockers'] else state['gate']
            mechanical='MECHANICAL_PASS' if not state['blockers'] and runs['status'] in {'PASS','NOT_RUN'} else 'CONDITIONAL'
            semantic='SEMANTIC_PASS' if not state['blockers'] and ind['status'] in {'RUNTIME_INDEPENDENT','STATICALLY_DISTINCT'} and lineage['status'] in {'CURRENT','NOT_RUN'} else 'CONDITIONAL'
            provenance='HUMAN_JUDGMENT_PENDING' if any(not state['checks'].get(x,False) for x in ('method_choice','result_verdict','stability_verdict','claim_scope')) else 'SEMANTIC_PASS'
            issues=list(state['blockers'])+list(runs['errors'])+list(lineage['errors'])+list(ind['errors'])
            if issues:blocking.extend(f'{qid}: {x}' for x in issues)
            questions.append({'question_id':qid,'derived_gate':state['gate'],'gate_status':gate,'mechanical_status':mechanical,'semantic_status':semantic,'provenance_status':provenance,'lineage_status':lineage['status'],'independence_status':ind['status'],'run_status':runs['status'],'issues':issues})
        except Exception as exc:
            questions.append({'question_id':qid,'gate_status':'GATE_BLOCKED','mechanical_status':'NOT_RUN','semantic_status':'NOT_RUN','provenance_status':'NOT_RUN','lineage_status':'NOT_RUN','independence_status':'NOT_RUN','run_status':'NOT_RUN','issues':[str(exc)]});blocking.append(f'{qid}: {exc}')
    overall='GATE_BLOCKED' if blocking or any(q['gate_status']=='GATE_BLOCKED' for q in questions) else ('CONDITIONAL' if any(q['semantic_status']=='CONDITIONAL' for q in questions) else 'SEMANTIC_PASS')
    return {'schema_version':2,'overall_status':overall,'questions':questions,'blocking_findings':blocking,'status_vocabulary':STATUSES}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path);a=ap.parse_args();d=audit(a.root.resolve());text=json.dumps(d,ensure_ascii=False,indent=2);print(text)
    if a.out:
        try:
            a.out.parent.mkdir(parents=True,exist_ok=True)
            a.out.write_text(text+'\n',encoding='utf-8')
        except OSError as exc:
            print(f'cannot write --out: {exc}',file=sys.stderr);return 2
    # Propagate a blocked gate to the exit code so validate_repo can gate on it.
    return 0 if d.get('overall_status') not in {'GATE_BLOCKED'} else 2
if __name__=='__main__':raise SystemExit(main())
