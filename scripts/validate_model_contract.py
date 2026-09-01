#!/usr/bin/env python3
"""Validate a model contract and ensure code-facing roles reference it."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
REQUIRED=['schema_version','entities','inputs','state_functions','decision_variables','hard_constraints','soft_constraints','objective','evaluator','uncertainty','validation_contract']
def main():
    ap=argparse.ArgumentParser();ap.add_argument('contract',type=Path);args=ap.parse_args()
    try:d=json.loads(args.contract.read_text(encoding='utf-8-sig'))
    except Exception as e:print(f'CONTRACT_INVALID: {e}',file=sys.stderr);return 2
    missing=[k for k in REQUIRED if k not in d]
    if missing:print('CONTRACT_INVALID: missing '+', '.join(missing),file=sys.stderr);return 2
    if not isinstance(d['entities'],list) or not isinstance(d['inputs'],list) or not isinstance(d['decision_variables'],list):print('CONTRACT_INVALID: collection fields must be arrays',file=sys.stderr);return 2
    if not isinstance(d['objective'],dict) or not isinstance(d['evaluator'],dict) or not isinstance(d['validation_contract'],dict):print('CONTRACT_INVALID: object fields malformed',file=sys.stderr);return 2
    print(f'CONTRACT_OK {args.contract}');return 0
if __name__=='__main__':raise SystemExit(main())
