# Upstream statistics checklist (self-written, advisory)

Condensed from [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) `nature-statistics` (Apache-2.0; full rule files at `references/upstream/nature-writing/`). Use to choose robustness/statistics checks that carry weight; do not pad with irrelevant tests.

## P0 / P1 / P2 grading

- **P0 (blocking)**: pseudo-replication, multiple-comparison without correction, claiming causation from correlation, unit errors, outcome leakage.
- **P1 (must-report)**: missing uncertainty (no CI/error bars), unstated test assumptions, unstated sample size, unreported seeds.
- **P2 (quality)**: effect-size reporting, sensitivity bounds, distribution checks.

## Minimum statistical reporting

1. What was tested and against what baseline (metric definition identical).
2. Sample size / effective sample size / replications.
3. Point estimate + uncertainty (CI, std, or interval).
4. Test or method assumptions actually checked.
5. Seed(s) and deterministic setup.

## Figure statistics rules

- Show uncertainty whenever it is part of the claim.
- Do not truncate axes misleadingly.
- Baseline and main method visually distinct but not exaggerated.

## Review checklist (condensed)

- Every final claim maps to a check or an explicit limitation.
- No overclaim: "significantly" only with a stated test/threshold.
- Robustness checks are targeted at load-bearing assumptions (see `robustness-checker`).
