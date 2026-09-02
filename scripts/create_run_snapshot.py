#!/usr/bin/env python3
"""Create, execute, and validate hash-addressed experiment run snapshots."""
from __future__ import annotations
import sys
import argparse, hashlib, json, platform, subprocess, sys, time
from pathlib import Path


try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
FINAL_STATUSES={"SUCCESS","FAILED","INTERRUPTED","DEGRADED_SUCCESS"}

def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def safe(root:Path,raw:str)->Path:
 p=(root/raw).resolve()
 try:p.relative_to(root)
 except ValueError:raise ValueError(f'path escapes project root: {raw}')
 return p
def manifest(root:Path,paths:list[str])->dict:
 out={}
 for raw in paths:
  p=safe(root,raw)
  if not p.exists():raise FileNotFoundError(p)
  items=[p] if p.is_file() else [x for x in p.rglob('*') if x.is_file()]
  for x in items:out[x.relative_to(root).as_posix()]=sha256(x)
 return dict(sorted(out.items()))
def budget_delta(planned,actual):
 keys=sorted(set(planned)|set(actual));return {k:{'planned':planned.get(k),'actual':actual.get(k)} for k in keys if planned.get(k)!=actual.get(k)}
def vcs_snapshot(root):
 """Optional version-control context: git HEAD and dirty files when the
 workspace is a git repository. Best-effort; never blocks the run."""
 try:
  if not (root/'.git').exists():return None
  head=subprocess.run(['git','rev-parse','HEAD'],cwd=root,capture_output=True,text=True,encoding='utf-8',errors='replace')
  dirty=subprocess.run(['git','status','--porcelain'],cwd=root,capture_output=True,text=True,encoding='utf-8',errors='replace')
  lines=[ln[:200] for ln in (dirty.stdout or '').splitlines() if ln.strip()]
  return {'available':True,'head':(head.stdout or '').strip() or None,
          'dirty':lines[:50],'dirty_count':len(lines)}
 except Exception:
  return None
def write_json(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def begin(root,run_dir,args):
 run_dir.mkdir(parents=True,exist_ok=False);planned=json.loads(args.planned_budget or '{}');actual=json.loads(args.actual_budget or args.planned_budget or '{}');delta=budget_delta(planned,actual);degraded=bool(args.degraded or delta)
 cm=manifest(root,args.config);im=manifest(root,args.inputs);code=manifest(root,args.code);ch=hashlib.sha256(json.dumps(cm,sort_keys=True).encode()).hexdigest()
 data={'schema_version':2,'run_id':run_dir.name,'planned_budget':planned,'actual_budget':actual,'budget_delta':delta,'degraded':degraded,'degradation_reason':args.degradation_reason if degraded else None,'acceptance_impact':args.acceptance_impact,'claim_restrictions':args.claim_restriction,'input_manifest':im,'code_manifest':code,'config_manifest':cm,'config_hash':ch,'command':args.command,'environment':{'python':sys.version,'platform':platform.platform(),'cwd':str(root)},'vcs':vcs_snapshot(root),'status':'RUNNING','started_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'return_code':None,'result_ref':None,'validation_ref':None,'result_hash':None,'validation_hash':None,'executed_by_runner':False}
 write_json(run_dir/'config_snapshot.json',{'planned_budget':planned,'actual_budget':actual,'budget_delta':delta,'config_manifest':cm});(run_dir/'config_hash.txt').write_text(ch+'\n',encoding='utf-8',newline='\n');write_json(run_dir/'input_manifest.json',im);write_json(run_dir/'code_manifest.json',code);write_json(run_dir/'environment.json',data['environment']);(run_dir/'command.txt').write_text(args.command+'\n',encoding='utf-8',newline='\n');(run_dir/'stdout.log').write_text('',encoding='utf-8',newline='\n');(run_dir/'stderr.log').write_text('',encoding='utf-8',newline='\n');write_json(run_dir/'run_metadata.json',data);return data
def finish(root,run_dir,status,result_ref,validation_ref,return_code,executed):
 p=run_dir/'run_metadata.json';data=json.loads(p.read_text(encoding='utf-8-sig'))
 if data.get('status')!='RUNNING':raise RuntimeError('run already finalized')
 if status not in FINAL_STATUSES:raise ValueError('invalid final status')
 rp=safe(root,result_ref);vp=safe(root,validation_ref)
 if status in {'SUCCESS','DEGRADED_SUCCESS'}:
  if return_code!=0:raise RuntimeError('successful status requires return_code=0')
  if not executed:raise RuntimeError('successful status requires execution by unified runner')
  if not rp.is_file() or not vp.is_file():raise FileNotFoundError('result/validation missing')
 if data.get('degraded') and status=='SUCCESS':status='DEGRADED_SUCCESS'
 data.update({'status':status,'return_code':return_code,'result_ref':result_ref,'validation_ref':validation_ref,'result_hash':sha256(rp) if rp.is_file() else None,'validation_hash':sha256(vp) if vp.is_file() else None,'executed_by_runner':executed,'finished_at':time.strftime('%Y-%m-%dT%H:%M:%S%z')})
 data['vcs']=vcs_snapshot(root)  # post-run state: outputs appear as untracked/dirty
 write_json(p,data);return data
def run(root,run_dir,args):
 data=begin(root,run_dir,args)
 result_path=safe(root,args.result_ref); validation_path=safe(root,args.validation_ref)
 before={str(p):sha256(p) if p.is_file() else None for p in (result_path,validation_path)}
 started=time.time()
 try:
  proc=subprocess.run(args.command,cwd=root,shell=True,text=True,capture_output=True,encoding='utf-8',errors='replace')
 except BaseException:
  (run_dir/'stderr.log').write_text('runner exception\n',encoding='utf-8')
  raise
 (run_dir/'stdout.log').write_text(proc.stdout,encoding='utf-8',newline='\n')
 (run_dir/'stderr.log').write_text(proc.stderr,encoding='utf-8',newline='\n')
 data=json.loads((run_dir/'run_metadata.json').read_text(encoding='utf-8-sig'));data['elapsed_seconds']=time.time()-started;data['process_return_code']=proc.returncode;write_json(run_dir/'run_metadata.json',data)
 if proc.returncode==0:
  for p in (result_path,validation_path):
   if not p.is_file(): raise RuntimeError(f'successful run did not create required output: {p}')
  after={str(p):sha256(p) for p in (result_path,validation_path)}
  if all(before[str(p)]==after[str(p)] for p in (result_path,validation_path)):
   raise RuntimeError('successful run did not create or change result/validation outputs')
 status=('DEGRADED_SUCCESS' if data['degraded'] else 'SUCCESS') if proc.returncode==0 else 'FAILED'
 return finish(root,run_dir,status,args.result_ref,args.validation_ref,proc.returncode,True)
def validate(root,run_dir):
 p=run_dir/'run_metadata.json'
 if not p.is_file():return {'status':'FAIL','errors':['missing run_metadata.json']}
 d=json.loads(p.read_text(encoding='utf-8-sig'));e=[]
 for k in ('run_id','planned_budget','actual_budget','budget_delta','degraded','input_manifest','code_manifest','config_hash','command','environment','status','return_code','result_ref','validation_ref','executed_by_runner'):
  if k not in d:e.append('missing '+k)
 if d.get('status') not in FINAL_STATUSES:e.append(f'non-terminal status {d.get("status")}')
 if d.get('status') in {'SUCCESS','DEGRADED_SUCCESS'}:
  if not d.get('executed_by_runner'):e.append('success not executed by runner')
  if d.get('return_code')!=0:e.append('success return code is nonzero')
  for field,hfield in (('result_ref','result_hash'),('validation_ref','validation_hash')):
   try:x=safe(root,d.get(field,''))
   except Exception:e.append(field+' invalid');continue
   if not x.is_file():e.append(field+' missing')
   elif sha256(x)!=d.get(hfield):e.append(field+' hash changed')
 if d.get('budget_delta') and not d.get('degraded'):e.append('budget_delta present but degraded false')
 if d.get('degraded') and not d.get('budget_delta') and not d.get('degradation_reason'):e.append('explicit degraded missing degradation_reason')
 return {'status':'PASS' if not e else 'FAIL','errors':e,'run_id':d.get('run_id')}
def add_common(p):
 p.add_argument('root',type=Path);p.add_argument('run_dir',type=Path);p.add_argument('--config',action='append',default=[]);p.add_argument('--inputs',action='append',default=[]);p.add_argument('--code',action='append',default=[]);p.add_argument('--planned-budget');p.add_argument('--actual-budget');p.add_argument('--degraded',action='store_true');p.add_argument('--degradation-reason');p.add_argument('--acceptance-impact',action='append',default=[]);p.add_argument('--claim-restriction',action='append',default=[]);p.add_argument('--command',required=True)
def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True);b=sub.add_parser('begin');add_common(b);r=sub.add_parser('run');add_common(r);r.add_argument('--result-ref',required=True);r.add_argument('--validation-ref',required=True);f=sub.add_parser('finalize');f.add_argument('root',type=Path);f.add_argument('run_dir',type=Path);f.add_argument('--status',required=True);f.add_argument('--result-ref',required=True);f.add_argument('--validation-ref',required=True);f.add_argument('--return-code',type=int,required=True);v=sub.add_parser('validate');v.add_argument('root',type=Path);v.add_argument('run_dir',type=Path);a=ap.parse_args();root=a.root.resolve();rd=a.run_dir.resolve()
 try:
  if a.mode=='begin':out=begin(root,safe(root,str(a.run_dir).replace('\\','/')),a)
  elif a.mode=='run':out=run(root,safe(root,str(a.run_dir).replace('\\','/')),a)
  elif a.mode=='finalize':out=finish(root,safe(root,str(a.run_dir).replace('\\','/')),a.status,a.result_ref,a.validation_ref,a.return_code,False)
  else:out=validate(root,safe(root,str(a.run_dir).replace('\\','/')))
  print(json.dumps(out,ensure_ascii=False,indent=2));return 0 if out.get('status')!='FAIL' else 2
 except Exception as e:print(str(e),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
