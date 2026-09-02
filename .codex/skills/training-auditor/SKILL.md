---
name: training-auditor
description: Multi-dimensional audit for a training round. Runs mechanical checks, drafts the 6-dimension literacy scorecard via scripts/training_scorecard.py, and prepares the summary for the user to pick the next direction. Used in docs/training.md phase C.
whenToUse: In the literacy-training loop phase C: run mechanical checks and draft the 6-dimension scorecard for human steering.
---

# Purpose

Turn a round's artifacts into a **6-dimension literacy scorecard** and a summary the human can use to steer training.

# Preconditions

- Round solution and `reflection.md` exist under `results/training/roundN/`.

# Workflow

1. **Mechanical checks** (run, record exit/status into the scorecard).
   Training artifacts live under `results/training/roundN/`, NOT the contest
   workspace paths — point every check at the round's own files and never at
   `methods/Qx`, `paper/sections/`, or `workspace/` (a training audit must not
   scan the real contest):
   - `python scripts/model_quality_gate.py <round_root>` (round root = `results/training/roundN/solution` layout, adapted per the solver's neutral layout)
   - `python scripts/claim_coverage.py <round_root>`
   - `python scripts/abstract_checker.py results/training/roundN/solution/<abstract file> --subquestions Q1,Q2,...` (if the round has sections)
   - `python scripts/ai_trace_checker.py results/training/roundN/solution/<file>` (sample)
   - `python scripts/leakage_check.py --profile results/training/roundN/solution/data_profile.json --target <y>` (if applicable)
   - `python scripts/figure_consistency_check.py results/training/roundN/solution/figures`
   - `python scripts/section_structure_check.py <round_root>`
2. **Literacy scorecard**: run `python scripts/training_scorecard.py round results/training/roundN --json` to get the template, then fill agent self-scores (1–5 + evidence path per dimension), leaving `user_score` null for the human.
3. **Summary**: aggregate all rounds with `python scripts/training_scorecard.py summary results/training --json` → `results/training/summary.json` (radar data + ranking + "direction suggestion" placeholders).
4. Present the scorecard + summary to the user and ask them to (a) finalize scores, (b) pick the next-round direction.

# Dimensions

mathematical / innovation / figure / expression / evidence / completeness — definitions and mechanical anchors are in `docs/training.md` §3.

# Rules

- Mechanical status is reported separately from literacy scores; a passing script does not imply a high literacy score.
- Do not invent user scores; leave them null.
- Do not modify the closed-book solution during audit.

# Verification

- Scorecard JSON exists with all 6 dimensions, agent scores + evidence, null user scores.
- Mechanical check statuses are attached.
- Summary JSON aggregates all rounds when run with `summary`.
