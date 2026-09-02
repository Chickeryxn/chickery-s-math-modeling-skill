---
name: python-code-reviewer
description: Review, run, debug, and verify approved Python modeling code against its code plan, data contract, method decision, risk conditions, and experiment outputs, saving one compact JSON review.
whenToUse: When Python model code must be reviewed and run against the plan, data contract, and outputs (five named checks).
---

# Preconditions

- Python code and `code/Qx/qx_code_plan.md` exist.
- Approved method decision, method card, data profile, and relevant run summary are available.
- Required inputs are accessible.

# Workflow

1. Resolve the approved main and usable baseline. Flag scripts for unapproved candidates unless a fallback activation exists.
2. Inspect and run the code in the intended order.
3. Evaluate required checks:
   - `syntax`: imports, execution, exceptions, and obvious runtime faults.
   - `input_contract`: paths, fields, units, shapes, missing-data handling, and raw-data protection.
   - `method_alignment`: formulas, objectives, constraints, assumptions, main/baseline roles, and fallback scope match the approved plan.
   - `reproducibility`: seed, deterministic setup, dependency/runtime record, and rerun consistency.
   - `output_contract`: saved tables/metrics/figures, valid run summary, comparable main/baseline metrics, degeneracy evidence, and fallback-trigger state.
4. Add risk-specific checks only when relevant, such as leakage, constraint feasibility, numerical stability, or scale.
5. If asked to fix findings, make minimal changes, rerun affected checks, and record the repair. Otherwise report findings without changing code.
6. Save `code/Qx/reviews/qx_python_review.json`.

# Review Schema

```json
{
  "schema_version": 1,
  "question_id": "Q1",
  "language": "python",
  "reviewed_files": [],
  "decision_id": "q1_method_choice",
  "checks": {
    "syntax": {"status": "PASS", "evidence": []},
    "input_contract": {"status": "PASS", "evidence": []},
    "method_alignment": {"status": "PASS", "evidence": []},
    "reproducibility": {"status": "PASS", "evidence": []},
    "output_contract": {"status": "PASS", "evidence": []}
  },
  "findings": [],
  "verdict": "PASSED",
  "reviewed_at": "ISO-8601"
}
```

Statuses are `PASS`, `FAIL`, or `NOT_APPLICABLE` with a reason. Any required `FAIL` blocks G3.

# Rules

- Do not pad evidence to reach a count.
- Do not fabricate execution or outputs.
- Do not approve a toy diagnostic reference as the official baseline.
- Do not silently change mathematical meaning.
- Do not create success logs beyond the review JSON.
- Treat code newer than its review as requiring the affected checks to rerun, not necessarily the entire pipeline.

# Verification

- Every required named check has concrete evidence.
- Main and baseline are approved and comparable.
- Run summary and on-disk outputs agree.
- Review verdict follows check statuses.


## Independence and lineage checks

In addition to the named checks, verify that main, baseline, and verifier have distinct implementation paths and that baseline/verifier do not use the main result as their only numeric input. Check the run snapshot and lineage hashes before accepting a result. Report `CONDITIONAL` or `GATE_BLOCKED` when the evidence is incomplete; do not infer independence from filenames.


## v0.3 semantic checks

Run `validate_independence.py` and `validate_run_snapshot.py` where applicable. Distinguish `STATICALLY_DISTINCT`, `RUNTIME_INDEPENDENT`, `NOT_INDEPENDENT`, and `NOT_VERIFIED`; do not infer runtime independence from different filenames. Check the model contract hash and lineage before passing output.
