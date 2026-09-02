---
name: matlab-model-code-generator
description: Generate and run minimal reproducible MATLAB or Beita Tianyuan compatible code for the human-approved main method and usable baseline, with compact experiment artifacts and a canonical run summary.
license: MIT
whenToUse: When the approved plan targets MATLAB or Beita Tianyuan and .m code must be generated and executed.
---

# Preconditions

- G2.5 human method choice is recorded.
- `code/matlab/Qx/qx_code_plan.md` exists.
- Required cleaned data and profile exist.
- The plan targets MATLAB or 北太天元.

Legacy artifacts may be read during migration but do not override the human decision.

# Workflow

1. Read the code plan, decision ledger, method card, probe conditions, and data profile.
2. Confirm scope: approved main plus usable baseline. Implement a fallback only after activation.
3. Generate conservative `.m` files under `code/matlab/Qx/`.
4. Prefer basic matrix/table operations and avoid optional toolboxes unless the plan approves them.
5. Save tables, metrics, useful figures, and `run_summary.json` under `results/Qx/experiments/roundN/`.
6. Evaluate output-degeneracy and fallback-trigger metrics required by the plan.
7. Use `diary` or another full log only for a failure or reproducibility warning.
8. Run in the available compatible runtime. If unavailable, report the unexecuted state explicitly.
9. Hand off to `code-reviewer`.

# Script Layout

```text
code/matlab/Qx/
├── qx_code_plan.md
├── qx_baseline.m
├── qx_main.m
├── qx_verifier.m     % independent verifier planned by model-code-analyzer
└── run_all.m        % only when useful
```

Do not create scripts for unapproved candidates or a duplicate README.

# Compatibility Rules

- Prefer `readtable`, `readmatrix`, `writetable`, `writematrix`, `save`, `load`, and `fullfile`.
- Use `rng(2026)` or the recorded seed.
- Use `jsonencode` when supported; otherwise write the required JSON fields deterministically.
- Avoid Live Scripts, App Designer, GUI code, Simulink, and toolbox-only functions unless explicitly approved.
- Note any 北太天元 compatibility risk in the run summary.

# Run Summary

Follow the `model-code-analyzer` contract, including approved decision ID, roles, paths, metrics, output-degeneracy evidence, fallback state, timing, seed, environment, warnings, and errors.

# Rules

- Do not change the selected mathematical method.
- Do not access or overwrite raw data.
- Do not fabricate successful execution when MATLAB/北太天元 is unavailable.
- Keep only evidence-bearing intermediate outputs.
- Separate Type 1 diagnostics from paper figures.

# Verification

- Main and baseline are directly comparable and both executed when a runtime is available.
- Fallback code exists only when activated.
- Formal outputs and run summary exist.
- Compatibility, seed, inputs, warnings, and errors are recorded.
- Required concentration/degeneracy checks are saved.
- Next handoff is `code-reviewer`.


## Immutable run requirement

Create the immutable run snapshot with `scripts/create_run_snapshot.py` exactly
as the Python generator does — a snapshot produced by the MATLAB code itself
cannot claim `SUCCESS` (the validator requires `executed_by_runner: true` and a
return code of 0). When no compatible runtime is available, record the round as
`NOT_RUN` with the snapshot begun but not finalized; never self-certify an
unexecuted round. Record planned and actual budgets, input/config/code hashes,
exact command, runtime, status, result reference, and validation reference.


## v0.3 runner requirement

Record MATLAB execution through the unified run snapshot contract or an equivalent snapshot with runner evidence, return code, output hashes, budget delta, and validation reference. Static files do not prove execution.
