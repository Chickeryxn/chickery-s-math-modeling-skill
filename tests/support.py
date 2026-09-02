#!/usr/bin/env python3
"""Shared fixtures/helpers for repository-local tests (pure standard library).

Several gate tests used to each copy their own write()/decision()/
model_contract scaffolding; keep those in one place so a schema change needs
one edit, not five.
"""
from __future__ import annotations
import json, tempfile
from pathlib import Path
from typing import Iterator


def make_root() -> tuple[tempfile.TemporaryDirectory, Path]:
    td = tempfile.TemporaryDirectory()
    return td, Path(td.name)


def write(p: Path, text: str | dict = "x"):
    if isinstance(text, dict):
        text = json.dumps(text)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def decision(did: str, dtype: str, choice: str = "user choice",
             status: str = "DECIDED", source_type: str = "user_answer",
             recorded_at: str = "2026-09-01T00:00:00Z") -> dict:
    """A structurally valid decision record (validate_decisions-compatible)."""
    return {
        "decision_id": did, "decision_type": dtype, "status": status,
        "decided_by": "human" if status == "DECIDED" else None,
        "choice": choice, "rationale": "User supplied rationale",
        "evidence_refs": [], "recorded_at": recorded_at,
        "source": {"source_type": source_type,
                   "user_message_id": did + "-message",
                   "user_verbatim_answer": "User supplied answer"},
        "supersedes": None,
    }


MODEL_CONTRACT = {
    "schema_version": 1,
    "entities": [{"id": "entity"}],
    "inputs": [{"id": "input", "type": "numeric", "domain": "real",
                "unit": "unit", "source": "synthetic"}],
    "state_functions": [],
    "decision_variables": [{"id": "decision", "type": "numeric",
                            "domain": "[0,1]", "unit": "unit"}],
    "hard_constraints": [{"id": "constraint", "expression_ref": "synthetic"}],
    "soft_constraints": [],
    "objective": {"sense": "MAXIMIZE", "value_ref": "score",
                  "output_contract": {"type": "scalar"}},
    "evaluator": {"evaluator_id": "synthetic", "implementation_ref": "verifier.py"},
    "uncertainty": None,
    "validation_contract": {"independent_checks": ["main", "baseline", "verifier"],
                            "tolerances": {"score": 1e-6}},
}


def write_model_contract(root: Path):
    write(root / "planning" / "model_contract.json", MODEL_CONTRACT)


def write_round_metadata(root: Path, qid: str = "Q1", round_no: int = 1,
                         result: str = "result", validation: str = "validation") -> Path:
    """Write a valid roundN/run_metadata.json + result/validation files and
    return the run_metadata path (contents mirror create_run_snapshot output)."""
    base = root / "results" / qid / "experiments" / f"round{round_no}"
    write(base / "result.json", result)
    write(base / "validation.json", validation)
    meta = {
        "schema_version": 2, "run_id": f"round{round_no}",
        "planned_budget": {}, "actual_budget": {}, "budget_delta": {},
        "degraded": False, "input_manifest": {}, "code_manifest": {},
        "config_hash": "x", "command": "python main.py", "environment": {},
        "status": "SUCCESS", "return_code": 0,
        "result_ref": str((base / "result.json").relative_to(root).as_posix()),
        "validation_ref": str((base / "validation.json").relative_to(root).as_posix()),
        "executed_by_runner": True,
    }
    write(base / "run_metadata.json", meta)
    return base / "run_metadata.json"
