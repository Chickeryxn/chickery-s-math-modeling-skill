#!/usr/bin/env python3
"""Derive workflow gates from canonical evidence and guard sensitive artifacts."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
GATES={"G1":1,"G2":2,"G2.5":2.5,"G3":3,"G4":4,"G5":5,"G6":6,"G1_PROBLEM_FRAMED":1,"G2_METHOD_SCREENED":2,"G2_5_HUMAN_CHOSEN":2.5,"G3_CODE_REVIEWED":3,"G4_RESULTS_JUDGED":4,"G5_PAPER_READY":5,"G6_FINAL_AUDIT":6}
NAMES={1:'G1',2:'G2',2.5:'G2.5',3:'G3',4:'G4',5:'G5',6:'G6'}
ARTIFACT_MIN_GATE={"model_code":2.5,"code_plan":2.5,"experiment":2.5,"result_report":4,"robustness_report":3,"solution_package":5,"paper_section":5,"frozen_numbers":5,"final_assembly":6}

def gate_value(x):
 if x not in GATES:raise ValueError(f'unknown gate: {x}')
 return GATES[x]
def load_json(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def decision_records(root,qid):
 p=root/'methods'/qid/f'{qid.lower()}_decisions.jsonl';out=[]
 if not p.is_file():return out
 for line in p.read_text(encoding='utf-8-sig').splitlines():
  if line.strip():
   try:out.append(json.loads(line))
   except json.JSONDecodeError:pass
 return out
def human_decision_exists(root,qid,dtype):
 records=decision_records(root,qid); superseded={r.get('supersedes') for r in records if r.get('status')=='SUPERSEDED'}
 return any(r.get('decision_id') not in superseded and r.get('status')=='DECIDED' and r.get('decision_type')==dtype and r.get('decided_by')=='human' and (r.get('source') or {}).get('source_type')=='user_answer' and bool((r.get('source') or {}).get('user_message_id')) and bool((r.get('source') or {}).get('user_verbatim_answer')) for r in records)
def first(root,*patterns):
    for pattern in patterns:
        matches=sorted(root.glob(pattern))
        if matches:
            return matches[0]
    return None

def is_json_file(path):
    try:
        data=load_json(path)
        return isinstance(data,(dict,list))
    except Exception:
        return False

def method_card_ready(path):
    if not path or not path.is_file(): return False
    text=path.read_text(encoding='utf-8-sig')
    required=('main_candidate','usable_baseline','Risk-probe summary','Baseline validity')
    return all(x in text for x in required)

def risk_probe_ready(path):
    if not path or not path.is_file(): return False
    try:
        data=load_json(path)
    except Exception:
        return False
    if not isinstance(data,dict): return False
    methods=data.get('methods') or {}
    return bool(methods) and all(isinstance(v,dict) and v.get('verdict') in {'PASS','CONDITIONAL'} for v in methods.values())

def review_ready(path):
    if not path or not path.is_file(): return False
    try:data=load_json(path)
    except Exception:return False
    checks=data.get('checks') if isinstance(data,dict) else None
    required=('syntax','input_contract','method_alignment','reproducibility','output_contract')
    return isinstance(checks,dict) and all(k in checks and checks[k].get('status') in {'PASS','NOT_APPLICABLE'} for k in required)

def any_human_decision(root,qid,dtype):
    return human_decision_exists(root,qid,dtype)

def derive_state(root,qid):
    checks={};
    parse_path=first(root,'planning/parse/problem_parse.json')
    classification_path=first(root,'planning/classification/problem_classification.json')
    checks['parse']=parse_path is not None and is_json_file(parse_path)
    checks['classification']=classification_path is not None and is_json_file(classification_path)
    parse_data=load_json(parse_path) if checks['parse'] else {}
    checks['data_inventory']=isinstance(parse_data,dict) and isinstance(parse_data.get('data_inventory'),list)
    checks['framing']=all(checks.get(k,False) for k in ('parse','classification','data_inventory'))
    if not checks['framing']:
        return {'gate':'G1','checks':checks,'blockers':['problem framing evidence incomplete']}
    card=first(root,f'methods/{qid}/{qid.lower()}_method_card.md')
    probe=first(root,f'methods/{qid}/probes/risk_probe_summary.json')
    checks['method_card']=method_card_ready(card)
    checks['risk_probe']=risk_probe_ready(probe)
    if not (checks['method_card'] and checks['risk_probe']):
        return {'gate':'G1','checks':checks,'blockers':['method screening evidence incomplete']}
    checks['method_choice']=any_human_decision(root,qid,'method_choice')
    if not checks['method_choice']:
        return {'gate':'G2','checks':checks,'blockers':['verifiable human method_choice missing']}
    runs=sorted(root.glob(f'results/{qid}/experiments/**/run_summary.json'))
    reviews=sorted(root.glob(f'code/{qid}/reviews/*_review.json'))+sorted(root.glob(f'code/matlab/{qid}/reviews/*_review.json'))
    def run_summary_ready(path):
        if not is_json_file(path): return False
        data=load_json(path)
        ref=data.get('run_snapshot') or data.get('snapshot_ref')
        if not isinstance(ref,str): return False
        snapshot=(root/ref).resolve()
        if not snapshot.is_file(): return False
        try: snap=load_json(snapshot)
        except Exception: return False
        required=('run_id','status','return_code','result_ref','validation_ref','executed_by_runner')
        return all(k in snap for k in required) and snap.get('status') in {'SUCCESS','DEGRADED_SUCCESS'} and snap.get('return_code')==0 and snap.get('executed_by_runner') is True
    checks['run_summary']=bool(runs) and all(run_summary_ready(x) for x in runs)
    checks['review']=bool(reviews) and any(review_ready(x) for x in reviews)
    if not (checks['run_summary'] and checks['review']):
        return {'gate':'G2.5','checks':checks,'blockers':['run summary or passing code review missing']}
    checks['result_report']=first(root,f'results/{qid}/reports/{qid.lower()}_final_result_analysis.md') is not None
    checks['robustness']=first(root,f'robustness/{qid}/{qid.lower()}_robustness_report.md',f'robustness/{qid}/{qid.lower()}_robustness_summary.json') is not None
    checks['result_verdict']=any_human_decision(root,qid,'result_verdict')
    checks['stability_verdict']=any_human_decision(root,qid,'stability_verdict')
    checks['claim_scope']=any_human_decision(root,qid,'claim_scope')
    if not all(checks[k] for k in ('result_report','robustness','result_verdict','stability_verdict','claim_scope')):
        return {'gate':'G3','checks':checks,'blockers':['result, robustness, or human result decisions incomplete']}
    checks['package']=first(root,f'results/{qid}/reports/{qid.lower()}_solution_package_for_writer.md') is not None
    checks['freeze']=first(root,f'results/{qid}/reports/frozen_numbers.json') is not None
    checks['package_signoff']=any_human_decision(root,qid,'package_signoff')
    if not all(checks[k] for k in ('package','freeze','package_signoff')):
        return {'gate':'G4','checks':checks,'blockers':['solution package, frozen numbers, or package signoff incomplete']}
    checks['paper']=first(root,f'paper/sections/{qid.lower()}.tex',f'paper/sections/{qid.lower()}.md') is not None
    if not checks['paper']:
        return {'gate':'G5','checks':checks,'blockers':['paper section missing']}
    checks['consistency']=first(root,'paper/audits/cross_media_consistency_audit.md','paper/audits/final_consistency_audit.md') is not None
    checks['completeness']=first(root,'paper/audits/completeness_audit.md') is not None
    checks['qa']=first(root,'paper/qa_report.md','paper/audits/qa_report.md') is not None
    if not all(checks[k] for k in ('consistency','completeness','qa')):
        return {'gate':'G5','checks':checks,'blockers':['final audit layer incomplete']}
    return {'gate':'G6','checks':checks,'blockers':[]}

def require_gate(root,qid,kind):
 if kind not in ARTIFACT_MIN_GATE:raise ValueError('unknown artifact kind: '+kind)
 state=derive_state(root,qid);actual=gate_value(state['gate']);required=ARTIFACT_MIN_GATE[kind]
 if actual<required:raise RuntimeError(f'GATE_BLOCKED: evidence-derived {state["gate"]} cannot produce {kind}; requires >= {NAMES[required]}')
 m=root/'planning/manifests'/f'{qid}.json'
 if not m.is_file():
  raise RuntimeError(f'GATE_BLOCKED: missing required manifest {m}')
 manifest_data=load_json(m)
 claimed=gate_value(manifest_data.get('current_gate','G1'))
 if claimed>actual:raise RuntimeError(f'GATE_BLOCKED: manifest claims {claimed} but canonical evidence derives {state["gate"]}')
 if kind in {'model_code','code_plan'}:
  contract=root/'planning/model_contract.json'
  if not contract.is_file():raise RuntimeError(f'GATE_BLOCKED: missing resolved model contract {contract}')
  try:
   c=load_json(contract); raw=contract.read_text(encoding='utf-8-sig').lower()
   if 'problem-specific' in raw or 'todo' in raw or not isinstance(c.get('objective'),dict) or not c['objective'].get('output_contract'):
    raise RuntimeError(f'GATE_BLOCKED: model contract unresolved or incomplete: {contract}')
  except RuntimeError:raise
  except Exception as exc:raise RuntimeError(f'GATE_BLOCKED: invalid model contract {exc}')
 if manifest_data.get('artifacts'):
  try:
   from validate_artifacts import validate as validate_artifacts
   lineage_result=validate(root,m)
   if lineage_result.get('status')!='PASS':raise RuntimeError('GATE_BLOCKED: manifest-declared artifact lineage is incomplete or stale')
  except ImportError: raise RuntimeError('GATE_BLOCKED: artifact validator unavailable')
 return {'question_id':qid,'artifact_kind':kind,'derived_gate':state['gate'],'checks':state['checks']}
def check_transition(old,new):
 a=gate_value(old.get('current_gate','G1'));b=gate_value(new.get('current_gate','G1'))
 if b<a:raise RuntimeError('INVALID_TRANSITION: gate regression')
 if b>a and not (b-a<=1 or (a==2 and b==2.5)):raise RuntimeError('INVALID_TRANSITION: gate jump skips a stage')
 if new.get('status')=='final' and b<6:raise RuntimeError('INVALID_TRANSITION: final requires G6')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);sub=ap.add_subparsers(dest='cmd',required=True);r=sub.add_parser('require');r.add_argument('question_id');r.add_argument('artifact_kind',choices=sorted(ARTIFACT_MIN_GATE));d=sub.add_parser('derive');d.add_argument('question_id');t=sub.add_parser('transition');t.add_argument('old_manifest',type=Path);t.add_argument('new_manifest',type=Path);a=ap.parse_args();root=a.root.resolve()
 try:
  if a.cmd=='require':print(json.dumps(require_gate(root,a.question_id,a.artifact_kind),ensure_ascii=False))
  elif a.cmd=='derive':print(json.dumps({'question_id':a.question_id,**derive_state(root,a.question_id)},ensure_ascii=False))
  else:check_transition(load_json(a.old_manifest),load_json(a.new_manifest));print('TRANSITION_OK')
  return 0
 except (RuntimeError,ValueError,OSError) as e:print(str(e),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
