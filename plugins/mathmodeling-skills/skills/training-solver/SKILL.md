---
name: training-solver
description: Closed-book training solver. Solve a training problem from start to finish WITHOUT reading resource-library/, then hand off to training-reflector. Used in the literacy-training loop (docs/training.md).
---

# Purpose

Produce a complete solution for one training round in **closed-book** mode. This skill exists so the agent practices independently first; the showcase library is a literacy benchmark, not an answer key.

# Closed-book rule (mandatory)

- In `closed` mode, **do not read anything under `resource-library/`** during this phase (config: `planning/training_config.json` → `mode`; `closed_phase_forbidden_paths`).
- You may use normal project resources (AGENTS.md rules, `references/abstraction-patterns.md`, method index, skills) — the ban is only on the showcase library.
- If the user explicitly switches `mode` to `open`, the ban is lifted and you may consult the library before solving.

# Workflow

1. Read `planning/training_config.json` (rounds, target_skills, problem_source) and the round number (from `results/training/`).
2. Read the problem from `problem_source` (or the user-provided path).
3. Follow the normal modeling workflow for the solution:
   - problem parse/classification; data profile if data exists;
   - method card with ≥2 modeling paradigms and rationale chain (why this / why not the other paradigm);
   - risk probe; human choice record (append to the round's decision ledger);
   - code + run summary; results with uncertainty; frozen-macro-ready numbers;
   - paper-skeleton-conforming draft sections.
4. Save everything under `results/training/roundN/solution/` (method card, probe, code, run_summary, results, sections).
5. Do not look at the showcase library; do not self-evaluate against it here.

# Output

A compact round report in conversation plus the saved artifacts. Then hand off to `training-reflector` with the round path.

# Rules

- Never read `resource-library/` in closed mode.
- Never claim the solution is "the best possible" — evaluation happens in phase C.
- Keep the solution honest: mark assumptions, uncertainties, and limitations.

# Verification

- No `resource-library/` path appears in this phase's reads.
- Solution artifacts exist under `results/training/roundN/solution/`.
- Human choice is recorded before code generation (per workflow gates).
