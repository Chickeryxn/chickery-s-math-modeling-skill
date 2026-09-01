#!/usr/bin/env python3
"""Validate append-only human decision ledgers without inventing decisions."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

STATUSES = {"SUGGESTED", "PENDING", "DECIDED", "SUPERSEDED", "STALE"}
DECIDED_TYPES = {"framing", "method_choice", "fallback_activation", "result_verdict", "stability_verdict", "assumption_necessity", "claim_scope", "package_signoff", "submission_authorization"}


def error(errors, path, msg): errors.append(f"{path}: {msg}")


def validate(path: Path, root: Path) -> list[str]:
    errors=[]; ids=set(); lines=path.read_text(encoding="utf-8-sig").splitlines()
    for no,line in enumerate(lines,1):
        if not line.strip(): continue
        loc=f"{path}:{no}"
        try: rec=json.loads(line)
        except json.JSONDecodeError as exc:
            error(errors,loc,f"invalid JSON: {exc}");continue
        if not isinstance(rec,dict): error(errors,loc,"record is not an object");continue
        for k in ("decision_id","decision_type","status","source","choice","evidence_refs","recorded_at"):
            if k not in rec: error(errors,loc,f"missing {k}")
        did=rec.get("decision_id")
        if did in ids:error(errors,loc,f"duplicate decision_id {did}")
        ids.add(did)
        if rec.get("status") not in STATUSES:error(errors,loc,"invalid status")
        source=rec.get("source") or {}
        if rec.get("status")=="DECIDED":
            if rec.get("decided_by")!="human": error(errors,loc,"DECIDED must be decided_by=human")
            if source.get("source_type")!="user_answer":error(errors,loc,"DECIDED requires source.source_type=user_answer")
            for k in ("user_message_id","user_verbatim_answer"):
                if not source.get(k):error(errors,loc,f"DECIDED source missing {k}")
            if rec.get("decision_type") not in DECIDED_TYPES:error(errors,loc,"unknown decision_type")
        if rec.get("status") in {"SUGGESTED","PENDING"} and rec.get("decided_by")=="human":
            error(errors,loc,"pending/suggested record cannot claim human decision")
        if rec.get("status")=="DECIDED" and not rec.get("rationale"):
            error(errors,loc,"DECIDED requires non-empty rationale copied from user or explicitly marked absent")
        for ref in rec.get("evidence_refs",[]) or []:
            if isinstance(ref,str) and ref.startswith((".","/")):
                candidate=(root/ref).resolve()
                if not candidate.exists():error(errors,loc,f"missing evidence ref {ref}")
    return errors


def main():
    ap=argparse.ArgumentParser();ap.add_argument("root",type=Path);ap.add_argument("ledger",type=Path)
    args=ap.parse_args();errs=validate(args.ledger,args.root.resolve())
    if errs:
        print("\n".join(errs),file=sys.stderr);return 2
    print(f"DECISION_LEDGER_OK {args.ledger}");return 0
if __name__=="__main__":raise SystemExit(main())
