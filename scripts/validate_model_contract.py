#!/usr/bin/env python3
"""Validate a domain-neutral model contract and its role references."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
REQUIRED=['schema_version','entities','inputs','state_functions','decision_variables','hard_constraints','soft_constraints','objective','evaluator','uncertainty','validation_contract']

def check_items(items,name,required,errors):
 if not isinstance(items,list):errors.append(f'{name} must be an array');return
 seen=set()
 for i,x in enumerate(items):
  if not isinstance(x,dict):errors.append(f'{name}[{i}] must be an object');continue
  ident=x.get('id')
  if not isinstance(ident,str) or not ident.strip():errors.append(f'{name}[{i}] missing non-empty id')
  elif ident in seen:errors.append(f'{name} duplicate id {ident}')
  else:seen.add(ident)
  for key in required:
   if key not in x or x[key] in (None,''):errors.append(f'{name}[{i}] missing {key}')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('contract',type=Path);ap.add_argument('--require-resolved',action='store_true');a=ap.parse_args()
 try:d=json.loads(a.contract.read_text(encoding='utf-8-sig'))
 except Exception as e:print(f'CONTRACT_INVALID: {e}',file=sys.stderr);return 2
 errors=[f'missing {k}' for k in REQUIRED if k not in d]
 check_items(d.get('entities'),'entities',[],errors)
 check_items(d.get('inputs'),'inputs',['type','domain','unit','source'],errors)
 check_items(d.get('state_functions'),'state_functions',['arguments','output','definition_ref'],errors)
 check_items(d.get('decision_variables'),'decision_variables',['type','domain','unit'],errors)
 check_items(d.get('hard_constraints'),'hard_constraints',['expression_ref'],errors)
 check_items(d.get('soft_constraints'),'soft_constraints',['penalty_ref'],errors)
 for name in ('objective','evaluator','validation_contract'):
  if not isinstance(d.get(name),dict):errors.append(f'{name} must be an object')
 obj=d.get('objective',{});ev=d.get('evaluator',{});vc=d.get('validation_contract',{})
 if obj.get('sense') not in {'MINIMIZE','MAXIMIZE','minimize','maximize'}:errors.append('objective.sense must be MINIMIZE or MAXIMIZE')
 if not isinstance(obj.get('value_ref'),str) or not obj.get('value_ref'):errors.append('objective.value_ref must be non-empty')
 if not isinstance(obj.get('output_contract'),dict) or not obj.get('output_contract'):errors.append('objective.output_contract must be a non-empty object')
 if not ev.get('evaluator_id') or not ev.get('implementation_ref'):errors.append('evaluator requires evaluator_id and implementation_ref')
 if not isinstance(vc.get('independent_checks'),list) or not vc['independent_checks']:errors.append('validation_contract.independent_checks must be a non-empty array')
 if not isinstance(vc.get('tolerances'),dict) or not vc.get('tolerances'):errors.append('validation_contract.tolerances must be a non-empty object')
 if a.require_resolved:
  raw=a.contract.read_text(encoding='utf-8-sig').lower()
  if 'problem-specific' in raw or 'todo' in raw or 'example' in raw:errors.append('resolved contract still contains placeholder/example text')
 if errors:print('\n'.join(errors),file=sys.stderr);return 2
 digest=hashlib.sha256(a.contract.read_bytes()).hexdigest();print(json.dumps({'status':'PASS','contract_hash':digest},ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
