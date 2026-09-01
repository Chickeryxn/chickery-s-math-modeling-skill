#!/usr/bin/env python3
"""Shared workflow gate and write-scope enforcement for the modeling workspace."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

GATES = {
    "G1": 1, "G1_PROBLEM_FRAMED": 1,
    "G2": 2, "G2_METHOD_SCREENED": 2,
    "G2.5": 2.5, "G2_5_HUMAN_CHOSEN": 2.5,
    "G3": 3, "G3_CODE_REVIEWED": 3,
    "G4": 4, "G4_RESULTS_JUDGED": 4,
    "G5": 5, "G5_PAPER_READY": 5,
    "G6": 6, "G6_FINAL_AUDIT": 6,
}

# Minimum gate for sensitive artifact families.
ARTIFACT_MIN_GATE = {
    "model_code": 2.5,
    "code_plan": 2.5,
    "experiment": 2.5,
    "result_report": 4,
    "robustness_report": 3,
    "solution_package": 5,
    "paper_section": 5,
    "frozen_numbers": 4,
    "final_assembly": 6,
}


def _value(manifest: dict) -> float:
    raw = manifest.get("current_gate", manifest.get("gate", "G1"))
    if raw not in GATES:
        raise ValueError(f"unknown gate: {raw}")
    return GATES[raw]


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"manifest must be an object: {path}")
    return data


def decision_is_human_confirmed(record: dict) -> bool:
    source = record.get("source") or {}
    return (
        record.get("status") == "DECIDED"
        and record.get("decided_by") == "human"
        and source.get("source_type") == "user_answer"
        and bool(source.get("user_message_id"))
        and bool(source.get("user_verbatim_answer"))
    )


def human_decision_exists(root: Path, question_id: str, decision_type: str | None = None) -> bool:
    path = root / "methods" / question_id / f"{question_id.lower()}_decisions.jsonl"
    if not path.is_file():
        return False
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            try:
                record=json.loads(line)
                if decision_is_human_confirmed(record) and (decision_type is None or record.get("decision_type") == decision_type):
                    return True
            except json.JSONDecodeError:
                continue
    return False


def require_gate(root: Path, question_id: str, artifact_kind: str, *, allow_override=False) -> dict:
    if artifact_kind not in ARTIFACT_MIN_GATE:
        raise ValueError(f"unknown artifact kind: {artifact_kind}")
    manifest_path = root / "planning" / "manifests" / f"{question_id}.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"GATE_BLOCKED: missing manifest {manifest_path}")
    manifest = load_manifest(manifest_path)
    actual = _value(manifest)
    required = ARTIFACT_MIN_GATE[artifact_kind]
    if not allow_override and actual < required:
        raise RuntimeError(
            f"GATE_BLOCKED: {question_id} at {manifest.get('current_gate')} cannot produce "
            f"{artifact_kind}; requires gate >= {required}"
        )
    if artifact_kind in {"model_code", "code_plan"} and not human_decision_exists(root, question_id, "method_choice"):
        raise RuntimeError(
            f"GATE_BLOCKED: {question_id} has no verifiable human DECIDED method_choice record with user source"
        )
    if artifact_kind in {"solution_package", "frozen_numbers"} and not human_decision_exists(root, question_id, "package_signoff"):
        raise RuntimeError(
            f"GATE_BLOCKED: {question_id} has no verifiable human DECIDED package_signoff record"
        )
    if artifact_kind == "paper_section" and not (human_decision_exists(root, question_id, "claim_scope") or human_decision_exists(root, question_id, "submission_authorization")):
        raise RuntimeError(
            f"GATE_BLOCKED: {question_id} has no verifiable human claim_scope or submission_authorization record"
        )
    return {"question_id": question_id, "artifact_kind": artifact_kind, "actual_gate": actual, "required_gate": required}


def check_transition(old: dict, new: dict) -> None:
    old_gate, new_gate = _value(old), _value(new)
    if new_gate < old_gate:
        raise RuntimeError(f"INVALID_TRANSITION: gate regression {old.get('current_gate')} -> {new.get('current_gate')}")
    if new.get("status") == "final" and new_gate < 6:
        raise RuntimeError("INVALID_TRANSITION: final status requires G6")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    sub = ap.add_subparsers(dest="command", required=True)
    g = sub.add_parser("require")
    g.add_argument("question_id")
    g.add_argument("artifact_kind", choices=sorted(ARTIFACT_MIN_GATE))
    t = sub.add_parser("transition")
    t.add_argument("old_manifest", type=Path)
    t.add_argument("new_manifest", type=Path)
    args = ap.parse_args()
    try:
        if args.command == "require":
            print(json.dumps(require_gate(args.root.resolve(), args.question_id, args.artifact_kind), ensure_ascii=False))
        else:
            check_transition(load_manifest(args.old_manifest), load_manifest(args.new_manifest))
            print("TRANSITION_OK")
        return 0
    except (RuntimeError, ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
