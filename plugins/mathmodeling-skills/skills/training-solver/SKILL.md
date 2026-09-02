---
name: training-solver
description: Closed-book training solver. Solve a training problem from start to finish WITHOUT reading resource-library/, then hand off to training-reflector. Used in the literacy-training loop (docs/training.md).
whenToUse: In the literacy-training loop phase A: solve closed-book without reading resource-library or prior-round solutions.
---

# Purpose

Produce a complete solution for one training round in **closed-book** mode. This skill exists so the agent practices independently first; the showcase library is a literacy benchmark, not an answer key.

# Closed-book rule (mandatory)

- In `closed` mode, **do not read anything under `resource-library/`** during this phase (config: `planning/training_config.json` → `mode`; `closed_phase_forbidden_paths`).
- When the round config enables clean rounds (e.g. `round_problem_sources` lists a fresh problem per round, or the human asks for a clean solve), also **do not read earlier rounds' solutions** under `results/training/roundN-1/solution/` — each round must be solved independently.
- You may use normal project resources (AGENTS.md rules, `references/abstraction-patterns.md`, method index, skills) — the ban is only on the showcase library and prior solutions when a clean round is requested.
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

# Isolation rule (mandatory, prevents training/contest cross-contamination)

A training round runs in the SAME repository as the real contest workspace, so
it must never touch the contest's canonical paths:

- **Never write to** `methods/Qx/`, `code/Qx/`, `code/matlab/Qx/`,
  `planning/parse/`, `planning/classification/`, `planning/manifests/`,
  `planning/framing_decisions.jsonl`, `planning/symbol_table.md`,
  `planning/model_assumptions.md`, `workspace/`, `paper/`, `robustness/Qx/`,
  `results/Qx/`, or the global `planning/session_config.json` /
  `planning/training_config.json`.
- **Never modify** the real contest's decision ledgers or global planning
  files; the training round's ledger is its own file under
  `results/training/roundN/` (e.g. `.../solution/round_decisions.jsonl`).
- Mirror every workflow artifact under `results/training/roundN/solution/`
  with a neutral layout (e.g. `.../solution/parse.json`,
  `.../solution/method_card.md`, `.../solution/code/main.py`,
  `.../solution/run_summary.json`); do not expect the contest-gate validators
  to run against training artifacts.
- When the round needs a scratch workspace (data cleaning, extra runs), put it
  under `results/training/roundN/scratch/`, never under `workspace/`.

Consequence: the normal contest flow (G1–G6) never reads `results/training/`
and training never writes the contest's canonical paths, so the two stay
isolated even in one repository.

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
- No contest-canonical path (`methods/Qx`, `code/Qx`, `planning/parse`,
  `planning/classification`, `planning/manifests`, `workspace/`, `paper/`,
  `results/Qx`) was written during the round.
