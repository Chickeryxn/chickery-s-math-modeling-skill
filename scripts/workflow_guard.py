#!/usr/bin/env python3
"""Derive workflow gates from canonical evidence and guard sensitive artifacts.

Semantics
---------
`derive_state` returns the gate at which the evidence is currently stuck:
gates G1..G(n-1) are satisfied and gate Gn is not yet evidenced.  This value
is used by `require_gate` as the "latest satisfied-or-stuck" gate: an artifact
kind is producible when that value is at least the kind's minimum gate
(`ARTIFACT_MIN_GATE`).  A manifest is a cache only and can never promote the
derived gate; transitions must be monotonic.
"""
from __future__ import annotations
import sys
import argparse, json, re, sys
from pathlib import Path
from datetime import datetime


try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
GATES={"G1":1,"G2":2,"G2.5":2.5,"G3":3,"G4":4,"G5":5,"G6":6,"G1_PROBLEM_FRAMED":1,"G2_METHOD_SCREENED":2,"G2_5_HUMAN_CHOSEN":2.5,"G3_CODE_REVIEWED":3,"G4_RESULTS_JUDGED":4,"G5_PAPER_READY":5,"G6_FINAL_AUDIT":6}
NAMES={1:'G1',2:'G2',2.5:'G2.5',3:'G3',4:'G4',5:'G5',6:'G6'}
ARTIFACT_MIN_GATE={"model_code":2.5,"code_plan":2.5,"experiment":2.5,"result_report":3,"robustness_report":3,"solution_package":4,"paper_section":5,"frozen_numbers":4,"final_assembly":6}
PROFILES={'lean','submission','auto'}

def read_profile(root: Path, profile: str) -> str:
    """Resolve the rigor profile: explicit lean/submission wins; 'auto' reads the
    workspace session_config (defaulting to 'submission' when absent/unknown so
    the strict, submission-grade derivation stays the default)."""
    if profile in ('lean','submission'):
        return profile
    cfg=root/'planning/session_config.json'
    if cfg.is_file():
        try:
            d=json.loads(cfg.read_text(encoding='utf-8-sig'))
            p=d.get('rigor_profile') if isinstance(d,dict) else None
            if p in ('lean','submission'):
                return p
        except Exception:
            pass
    return 'submission'

def read_deadline(root: Path) -> str | None:
    cfg=root/'planning/session_config.json'
    if cfg.is_file():
        try:
            d=json.loads(cfg.read_text(encoding='utf-8-sig'))
            dl=d.get('deadline') if isinstance(d,dict) else None
            if isinstance(dl,str) and dl.strip():
                return dl.strip()
        except Exception:
            pass
    return None

def deadline_hint(deadline_iso: str) -> str | None:
    """Advisory remaining-time guidance derived from an ISO-8601 deadline.
    Purely informational; never a gate input."""
    try:
        s=deadline_iso.strip()
        if s.endswith('Z'):
            s=s[:-1]+'+00:00'
        dl=datetime.fromisoformat(s)
    except Exception:
        return None
    now=datetime.now(dl.tzinfo) if dl.tzinfo else datetime.now()
    left=(dl-now).total_seconds()/3600.0
    if left<0:
        return 'deadline passed: submission-only: finish the three audits and assembly now; no new experiments'
    if left<6:
        return 'deadline <6h: stop new experiments; run the three audits and assemble submission only'
    if left<24:
        return 'deadline <24h: switch rigor_profile to submission; finish freeze, paper sections, and audits'
    if left<48:
        return 'deadline <48h: aim to freeze results soon; start paper drafting and robustness'
    return None

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

# Machine anchors for the method card: fixed English structural headers the
# gate reads (AGENTS.md / method-selector contract). Body prose and rationale
# may be written in Chinese; only these anchors are language-locked.
METHOD_CARD_ANCHORS=('main_candidate','usable_baseline','risk-probe summary','baseline validity')
PLACEHOLDER_TOKENS=('placeholder','todo:','tbd','占位','待填')
def method_card_ready(path):
    if not path or not path.is_file(): return False
    low=path.read_text(encoding='utf-8-sig').lower()
    if not all(a in low for a in METHOD_CARD_ANCHORS): return False
    if any(t in low for t in PLACEHOLDER_TOKENS): return False
    return True

def parse_ready(parse_data) -> bool:
    """Structural framing depth: when the parse declares subquestions, every one
    must carry a goal and a non-empty required_outputs list."""
    if not isinstance(parse_data,dict): return False
    sq=parse_data.get('subquestions')
    if sq is None: return True
    return isinstance(sq,list) and all(
        isinstance(s,dict) and bool(s.get('goal'))
        and isinstance(s.get('required_outputs'),list) and s.get('required_outputs')
        for s in sq)

def classification_ready(data) -> bool:
    """Structural classification depth: every declared subquestion must carry a
    primary task type (problem-classifier contract)."""
    if not isinstance(data,dict): return False
    sq=data.get('subquestions')
    if sq is None: return True
    return isinstance(sq,list) and all(
        isinstance(s,dict) and bool(s.get('primary_type')) for s in sq)

def framing_required_decided(root: Path, qid: str, parse_data) -> bool:
    """When the parse lists human decisions that are needed, G1 additionally
    requires at least one verifiable human `framing` record before screening."""
    if not isinstance(parse_data,dict) or not isinstance(parse_data.get('human_decisions_needed'),list):
        return True
    if not parse_data.get('human_decisions_needed'):
        return True
    ledgers=[root/'planning/framing_decisions.jsonl',
             root/'methods'/qid/f'{qid.lower()}_decisions.jsonl']
    for ledger in ledgers:
        if not ledger.is_file(): continue
        for line in ledger.read_text(encoding='utf-8-sig').splitlines():
            if not line.strip(): continue
            try: r=json.loads(line)
            except json.JSONDecodeError: continue
            if r.get('decision_type')=='framing' and r.get('status')=='DECIDED' and r.get('decided_by')=='human' \
               and isinstance(r.get('source'),dict) and r['source'].get('source_type')=='user_answer' \
               and bool(r['source'].get('user_message_id')) and bool(r['source'].get('user_verbatim_answer')):
                return True
    return False

def risk_probe_ready(path):
    if not path or not path.is_file(): return False
    try:
        data=load_json(path)
    except Exception:
        return False
    if not isinstance(data,dict): return False
    methods=data.get('methods') or {}
    if isinstance(methods,list):
        # Accept the documented array shape: [{"id": "M1", ...}, ...]
        methods={m.get('id') or f'method{i}':m for i,m in enumerate(methods) if isinstance(m,dict)}
    elif not isinstance(methods,dict):
        return False
    verdicts=[v.get('verdict') for v in methods.values() if isinstance(v,dict)]
    if not verdicts: return False
    # A FAIL verdict is legitimate (AGENTS.md risk-probe contract): the method
    # is just not offered as main/baseline. The probe passes for gate purposes
    # when every verdict is a legal value and at least one candidate is usable.
    if not (all(v in {'PASS','CONDITIONAL','FAIL'} for v in verdicts)
            and any(v in {'PASS','CONDITIONAL'} for v in verdicts)):
        return False
    # Usable candidates must carry output-degeneracy evidence (contract:
    # 'always check output degeneracy or concentration').
    return all(isinstance(v.get('output_degeneracy'),dict)
               for v in methods.values()
               if isinstance(v,dict) and v.get('verdict') in {'PASS','CONDITIONAL'})

def review_ready(path):
    if not path or not path.is_file(): return False
    try:data=load_json(path)
    except Exception:return False
    checks=data.get('checks') if isinstance(data,dict) else None
    required=('syntax','input_contract','method_alignment','reproducibility','output_contract')
    return isinstance(checks,dict) and all(k in checks and checks[k].get('status') in {'PASS','NOT_APPLICABLE'} for k in required)

def any_human_decision(root,qid,dtype):
    return human_decision_exists(root,qid,dtype)

def _round_no(path: Path) -> int:
    m=re.search(r'(\d+)\s*$',path.parent.name)
    return int(m.group(1)) if m else 0

QID_RE = re.compile(r'^Q\d+$')


def derive_state(root: Path, qid: str, profile: str = 'submission'):
    """Derive the current gate from canonical evidence.

    profile is 'lean' or 'submission' (callers resolve 'auto' via read_profile;
    the default stays 'submission' for strict, backward-compatible behavior).
    In lean, G4 is the result-judgment subgate (human verdicts on computed
    evidence); submission artifacts (final analysis, robustness file, package,
    freeze, sign-off) are required only in the submission track. G5/G6 are
    submission-only and are not evaluated in lean.
    """
    if not QID_RE.match(qid or ''):
        raise ValueError(f'invalid question id: {qid!r} (expected Q<number>, e.g. Q1)')
    checks={};
    parse_path=first(root,'planning/parse/problem_parse.json')
    classification_path=first(root,'planning/classification/problem_classification.json')
    checks['parse']=parse_path is not None and is_json_file(parse_path)
    checks['classification']=classification_path is not None and is_json_file(classification_path)
    parse_data=load_json(parse_path) if checks['parse'] else {}
    checks['parse_depth']=parse_ready(parse_data)
    checks['classification_depth']=classification_ready(load_json(classification_path)) if checks['classification'] else False
    checks['data_inventory']=isinstance(parse_data,dict) and isinstance(parse_data.get('data_inventory'),list)
    checks['framing']=all(checks.get(k,False) for k in ('parse','parse_depth','classification','classification_depth','data_inventory'))
    if not checks['framing']:
        return {'gate':'G1','checks':checks,'blockers':['problem framing evidence incomplete']}
    checks['human_framing']=framing_required_decided(root,qid,parse_data)
    if not checks['human_framing']:
        return {'gate':'G1','checks':checks,'blockers':['human framing decision pending']}
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
        try:
            snapshot=(root/ref).resolve()
            snapshot.relative_to(root.resolve())
        except ValueError:
            return False  # snapshot reference escapes the project root
        if not snapshot.is_file(): return False
        try: snap=load_json(snapshot)
        except Exception: return False
        required=('run_id','status','return_code','result_ref','validation_ref','executed_by_runner')
        return all(k in snap for k in required) and snap.get('status') in {'SUCCESS','DEGRADED_SUCCESS'} and snap.get('return_code')==0 and snap.get('executed_by_runner') is True
    # Only the latest experiment round gates G3: earlier exploratory rounds may
    # predate the unified runner and are not required to carry snapshots.
    if runs:
        mx=max(_round_no(x) for x in runs)
        latest=[x for x in runs if _round_no(x)==mx]
        checks['run_summary']=bool(latest) and all(run_summary_ready(x) for x in latest)
        checks['advisory_older_runs_without_snapshot']=any(not run_summary_ready(x) for x in runs if _round_no(x)<mx)
    else:
        checks['run_summary']=False
        checks['advisory_older_runs_without_snapshot']=False
    checks['review']=bool(reviews) and any(review_ready(x) for x in reviews)
    if not (checks['run_summary'] and checks['review']):
        return {'gate':'G2.5','checks':checks,'blockers':['run summary or passing code review missing']}
    checks['result_report']=first(root,f'results/{qid}/reports/{qid.lower()}_final_result_analysis.md') is not None
    checks['robustness']=first(root,f'robustness/{qid}/{qid.lower()}_robustness_report.md',f'robustness/{qid}/{qid.lower()}_robustness_summary.json') is not None
    checks['result_verdict']=any_human_decision(root,qid,'result_verdict')
    checks['stability_verdict']=any_human_decision(root,qid,'stability_verdict')
    checks['claim_scope']=any_human_decision(root,qid,'claim_scope')
    verdicts_ok=all(checks[k] for k in ('result_verdict','stability_verdict','claim_scope'))
    if profile=='lean':
        # Lean G4 = result-judgment subgate: human verdicts on computed evidence.
        if not verdicts_ok:
            return {'gate':'G3','checks':checks,'blockers':['human result decisions incomplete']}
        return {'gate':'G4','checks':checks,'blockers':[],
                'note':'lean profile: result-judgment subgate passed; submission-only gates (freeze/paper/audits) not evaluated'}
    if not (verdicts_ok and checks['result_report'] and checks['robustness']):
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

def require_gate(root,qid,kind,profile='submission'):
 if kind not in ARTIFACT_MIN_GATE:raise ValueError('unknown artifact kind: '+kind)
 state=derive_state(root,qid,profile);actual=gate_value(state['gate']);required=ARTIFACT_MIN_GATE[kind]
 if actual<required:raise RuntimeError(f'GATE_BLOCKED: evidence-derived {state["gate"]} cannot produce {kind}; requires >= {NAMES[required]}')
 if kind=='frozen_numbers' and not state['checks'].get('package_signoff'):
  raise RuntimeError('GATE_BLOCKED: frozen_numbers requires a human package_signoff decision')
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
   lineage_result=validate_artifacts(root,m)
   if lineage_result.get('status')!='PASS':raise RuntimeError('GATE_BLOCKED: manifest-declared artifact lineage is incomplete or stale')
  except ImportError: raise RuntimeError('GATE_BLOCKED: artifact validator unavailable')
 return {'question_id':qid,'artifact_kind':kind,'derived_gate':state['gate'],'profile':profile,'checks':state['checks']}
def check_transition(old,new):
 a=gate_value(old.get('current_gate','G1'));b=gate_value(new.get('current_gate','G1'))
 if b<a:raise RuntimeError('INVALID_TRANSITION: gate regression')
 if b>a and not (b-a<=1 or (a==2 and b==2.5)):raise RuntimeError('INVALID_TRANSITION: gate jump skips a stage')
 if new.get('status')=='final' and b<6:raise RuntimeError('INVALID_TRANSITION: final requires G6')
STAGE_HINTS={
 'G1':'next: G2 method screening (method card + risk probe)',
 'G2':'next: G2.5 human method choice (choice card -> qx_decisions.jsonl)',
 'G2.5':'next: G3 code & experiments (approved main + baseline only)',
 'G3':'next: G4 result judgment (run model_quality_gate + claim_coverage)',
 'G4':'next: G5 paper (solution package -> paper-section-writer)',
 'G5':'next: G6 final audit (consistency/completeness/QA)',
 'G6':'all gates passed; run full verification and check planning/timeline.md',
}
def stage_hint(gate):
 return STAGE_HINTS.get(gate,'')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);sub=ap.add_subparsers(dest='cmd',required=True);r=sub.add_parser('require');r.add_argument('question_id');r.add_argument('artifact_kind',choices=sorted(ARTIFACT_MIN_GATE));r.add_argument('--profile',choices=sorted(PROFILES),default='submission');d=sub.add_parser('derive');d.add_argument('question_id');d.add_argument('--profile',choices=sorted(PROFILES),default='submission');d.add_argument('--deadline',default=None,help='optional ISO-8601 contest deadline for an advisory remaining-time hint');t=sub.add_parser('transition');t.add_argument('old_manifest',type=Path);t.add_argument('new_manifest',type=Path);a=ap.parse_args();root=a.root.resolve()
 try:
  if a.cmd=='require':
   prof=read_profile(root,a.profile)
   print(json.dumps(require_gate(root,a.question_id,a.artifact_kind,prof),ensure_ascii=False))
  elif a.cmd=='derive':
   prof=read_profile(root,a.profile)
   state=derive_state(root,a.question_id,prof)
   out={'question_id':a.question_id,'profile':prof,**state,'next_stage_hint':stage_hint(state['gate'])}
   deadline=a.deadline or read_deadline(root)
   hint=deadline_hint(deadline) if deadline else None
   if hint: out['deadline_hint']=hint
   print(json.dumps(out,ensure_ascii=False))
  else:check_transition(load_json(a.old_manifest),load_json(a.new_manifest));print('TRANSITION_OK')
  return 0
 except (RuntimeError,ValueError,OSError) as e:print(str(e),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
