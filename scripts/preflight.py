#!/usr/bin/env python3
"""Preflight bundle for a submission: run the G6-relevant mechanical checks in
one command and summarize their status.

Steps run only when their inputs exist (skipped otherwise, never false-failed):
  - claim_coverage (subquestion -> section / frozen / abstract number coverage)
  - abstract_checker (per-subquestion numbers in the abstract)
  - ai_trace_checker (sampled paper sections)
  - latex_assembly --check-only --strict (bare numbers / frozen references)
  - figure_consistency_check (paper/figures naming and size consistency)
  - section_structure_check (skeleton presence, order, length share)

Pure standard library. Exit codes: 0 = no applied step failed; 2 = at least
one applied step failed (any failure blocks final assembly by convention).
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".pdf", ".svg", ".eps", ".tif", ".tiff"}


def run(cmd: list, cwd: Path) -> dict:
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True,
                       encoding="utf-8", errors="replace")
    return {"returncode": p.returncode,
            "stdout_tail": (p.stdout or "")[-1500:],
            "stderr_tail": (p.stderr or "")[-1500:]}


def audit(root: Path) -> dict:
    r = root.resolve()
    py = sys.executable
    steps = []
    manifests = sorted((r / "planning" / "manifests").glob("Q*.json"))
    sections = sorted((r / "paper" / "sections").glob("*.tex")) + \
               sorted((r / "paper" / "sections").glob("*.md"))
    frozen = sorted((r / "results").glob("*/reports/frozen_numbers.json"))
    figures_dir = r / "paper" / "figures"
    figures = [p for p in figures_dir.glob("*")
               if p.is_file() and p.suffix.lower() in IMAGE_EXTS] if figures_dir.is_dir() else []

    if manifests:
        rep = run([py, str(r / "scripts" / "claim_coverage.py"), str(r), "--strict", "--json"], r)
        steps.append({"name": "claim_coverage", "applied": True, **rep})
    else:
        steps.append({"name": "claim_coverage", "applied": False, "reason": "no manifests"})

    abstract = next((p for p in sections if "abstract" in p.name.lower()), None)
    if abstract and manifests:
        subq = ",".join(p.stem for p in manifests)
        rep = run([py, str(r / "scripts" / "abstract_checker.py"), str(abstract),
                   "--subquestions", subq, "--strict", "--json"], r)
        steps.append({"name": "abstract_checker", "applied": True, **rep})
    else:
        steps.append({"name": "abstract_checker", "applied": False,
                      "reason": "no abstract section or no manifests"})

    if sections:
        reps = [run([py, str(r / "scripts" / "ai_trace_checker.py"), str(p),
                     "--strict", "--json"], r) for p in sections]
        steps.append({"name": "ai_trace_checker", "applied": True,
                      "files": [p.relative_to(r).as_posix() for p in sections],
                      "failures": sum(1 for x in reps if x["returncode"] != 0),
                      "returncode": max((x["returncode"] for x in reps), default=0),
                      "details": reps})
    else:
        steps.append({"name": "ai_trace_checker", "applied": False, "reason": "no sections"})

    if sections and frozen:
        rep = run([py, str(r / "scripts" / "latex_assembly.py"), str(r),
                   "--check-only", "--strict"], r)
        steps.append({"name": "latex_assembly", "applied": True, **rep})
    else:
        steps.append({"name": "latex_assembly", "applied": False,
                      "reason": "no paper sections or no frozen numbers"})

    if figures:
        rep = run([py, str(r / "scripts" / "figure_consistency_check.py"),
                   str(figures_dir), "--strict", "--json"], r)
        steps.append({"name": "figure_consistency_check", "applied": True, **rep})
    else:
        steps.append({"name": "figure_consistency_check", "applied": False,
                      "reason": "no figures in paper/figures"})

    if len(sections) >= 2 and frozen:
        rep = run([py, str(r / "scripts" / "section_structure_check.py"),
                   str(r), "--strict", "--json"], r)
        steps.append({"name": "section_structure_check", "applied": True, **rep})
    else:
        steps.append({"name": "section_structure_check", "applied": False,
                      "reason": "fewer than two paper sections or no frozen numbers"})

    applied = [s for s in steps if s.get("applied")]
    failed = [s["name"] for s in applied if s.get("returncode") != 0]
    return {"status": "PASS" if not failed else "FAIL",
            "steps": steps, "applied": len(applied),
            "skipped": len(steps) - len(applied), "failed": failed}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--strict", action="store_true",
                    help="exit 2 when any applied step fails (default behavior); kept for compatibility")
    a = ap.parse_args()
    out = audit(a.root)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["status"] != "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
