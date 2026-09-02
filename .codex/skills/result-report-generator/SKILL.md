---
name: result-report-generator
description: Summarize modeling experiment evidence, compare the approved main method with a usable baseline, surface fallback triggers, and produce a decision-point or final report without creating routine per-round prose.
license: MIT
whenToUse: When experiment artifacts must be condensed into decision-point or final evidence without choosing a winner.
---

# Purpose

Turn saved experiment artifacts into compact evidence. Do not treat ordinary successful runs as requiring a long report, and do not choose the winning method.

# Inputs

- `run_summary.json`
- method card and probe summary
- decision ledger
- saved tables, metrics, and figures
- session `rigor_profile`

Stop if the run summary claims outputs that do not exist or if main and baseline are not comparable.

# Modes

## Ordinary lean round

- Validate the run summary and referenced artifacts.
- Return a compact evidence digest in the conversation.
- Do not save a Markdown report unless:
  - a fallback trigger fired;
  - a material anomaly or contradiction exists;
  - the human must make a proceed/adjust/fallback decision.

## Decision-point round

Save:

`results/Qx/experiments/roundN/qx_decision_report.md`

Include only:

- main vs baseline metrics;
- output-degeneracy/concentration evidence;
- assumption or feasibility warnings;
- robustness evidence already available;
- fallback trigger state;
- unresolved trade-offs.

Then invoke `decision-prompt-builder`. After the human answers, route the answer to `modeler-decision-logger`.

## Final/submission mode

Save:

`results/Qx/reports/qx_final_result_analysis.md`

Include:

- final main/baseline comparison;
- uncertainty and error;
- concentration/degeneracy interpretation;
- robustness links;
- limitations and applicable scope;
- exact source paths for numerical claims.

# Rejection and Fallback

- Archive a method only after a human `result_verdict` or `fallback_activation` decision.
- Move rejected code and outputs to `workspace/archived/<Qx>/<method>_REJECTED_roundN/`.
- Add one compact history line to `qx_method_card.md`; do not create a separate iteration log.
- Do not archive from an AI suggestion alone.

# Rules

- Do not fabricate metrics, comparisons, or interpretations.
- Separate facts from human verdicts.
- Do not create `result-report-generator_modeler_decision.md`.
- Do not repeat the full run summary; cite it and extract only decision-relevant evidence.
- Do not call a diagnostic reference a usable baseline.
- Do not generate paper prose.

# Verification

- Every reported number resolves to a saved artifact.
- Main/baseline comparison uses the same split, unit, and metric definition.
- Output concentration and fallback trigger are addressed.
- Reports are generated only at decision points or final mode.
- Human verdicts are read from or appended to the canonical JSONL ledger.


## Evidence strength

Before reporting a result, resolve the current lineage and actual run snapshot. Do not call a candidate stable when the executed budget differs from the plan without recording the degradation. Separate numerical verification from global-optimality claims and human result judgment.


## v0.3 evidence restrictions

Resolve the current gate, run snapshot, lineage, and actual budget before writing a result report. Do not call a degraded run fully executed; do not call a numerically verified result globally optimal without a proof or an explicitly qualified claim.
