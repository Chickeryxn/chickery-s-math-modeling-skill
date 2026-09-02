---
name: consistency-auditor
description: Run scoped or final cross-media consistency checks for mathematical-modeling artifacts, comparing canonical numbers, symbols, parameters, decisions, files, and paper claims without performing full-workspace audits for low-risk changes.
whenToUse: After CANONICAL or FROZEN changes, or before final assembly, to run scoped or final cross-media consistency checks.
---

# Modes

- `scoped`: run only for a `CANONICAL` or `FROZEN` change and only for affected Qx/identifiers.
- `final`: run across all submission artifacts before assembly.

# Sources of Truth

Prefer:

- `results/Qx/reports/frozen_numbers.json` (per-subquestion) for paper numbers;
- `qx_decisions.jsonl` for human judgments;
- `planning/symbol_table.md` for symbols/units;
- approved code plan and run summary for parameters and executed methods;
- solution package for writer-facing structure.

Use legacy decision logs or Markdown reviews only during migration.

# Checks

1. Numerical claims match frozen values and units.
2. Formula, parameter, constraint, and method roles match approved code and plan.
3. Symbols and units match the global symbol table.
4. Referenced tables, figures, code, and data files exist.
5. Why-this-method, result verdict, stability, confidence, and claim scope resolve to human decision IDs.
6. Freeze and decisions are not stale relative to materially changed cited evidence.
7. Paper figures referenced by sections carry render evidence (run `scripts/figure_render_audit.py .`; every `<figure>.render.json` must have `status: PASS` and a present `rendered_at`).

# Scoped Workflow

1. Receive changed files/identifiers and their impact class.
2. Resolve affected Qx and downstream consumers.
3. Check only those relationships.
4. Return a compact digest or save `results/Qx/reports/scoped_consistency.json` when durable evidence is needed.
5. Do not rewrite other artifacts.

# Final Workflow

1. Check all submission Qx.
2. Save `paper/audits/cross_media_consistency_audit.md`.
3. Report `PASSED`, `FAILED`, or `NOT_RUN`.
4. List concrete divergences and repair owners. Do not pad a pass list.

# Rules

- Do not run a full audit for formatting, comments, scratch work, or ordinary pre-freeze exploration.
- Do not infer canonical numbers from the paper.
- Do not repair divergences inside the audit.
- Do not approve final assembly directly.

# Verification

- Scope matches the semantic impact.
- Every divergence identifies source, consumer, and expected repair.
- Final audit covers all seven check classes listed under # Checks (numerical
  claims, formula/parameter/method roles, symbols/units, file existence,
  decision-ID resolution, freeze/decision staleness, figure render evidence).
- Verdict follows actual evidence rather than an item count.


## Lineage and status checks

Check sibling lineage records and source hashes for every canonical artifact. A changed source makes a consumer `STALE`; do not repair or silently select among competing snapshots. Report numerical consistency separately from gate eligibility and human-decision provenance.


## v0.3 lineage checks

Run `validate_artifacts.py` for manifest-declared artifacts and `lineage.py propagate` for repository-wide status refresh. Any `MISSING`, `STALE`, or `INVALIDATED` canonical artifact is a divergence, not a local pass. Never silently select among competing final snapshots.
