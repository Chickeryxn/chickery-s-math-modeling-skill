#!/usr/bin/env python3
"""Validate manifest shape and prohibit unsupported gate claims."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
GATES={'G1','G2','G2.5','G3','G4','G5','G6','G1_PROBLEM_FRAMED','G2_METHOD_SCREENED','G2_5_HUMAN_CHOSEN','G3_CODE_REVIEWED','G4_RESULTS_JUDGED','G5_PAPER_READY','G6_FINAL_AUDIT'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('manifest',type=Path);args=ap.parse_args();m=json.loads(args.manifest.read_text(encoding='utf-8-sig'));errs=[]
    for k in ('schema_version','question_id','rigor_profile','current_gate','status','artifacts','allowed','blockers','next_action'):
        if k not in m:errs.append(f'missing {k}')
    if m.get('current_gate') not in GATES:errs.append('unknown current_gate')
    allowed=m.get('allowed',{})
    if m.get('current_gate') not in {'G6','G6_FINAL_AUDIT'} and allowed.get('final_assembly') is True:errs.append('final_assembly cannot be allowed before G6')
    if m.get('current_gate') not in {'G4','G5','G6','G4_RESULTS_JUDGED','G5_PAPER_READY','G6_FINAL_AUDIT'} and allowed.get('freeze') is True:errs.append('freeze cannot be allowed before G4')
    if errs:print('\n'.join(errs),file=sys.stderr);return 2
    print(f'MANIFEST_OK {args.manifest}');return 0
if __name__=='__main__':raise SystemExit(main())
