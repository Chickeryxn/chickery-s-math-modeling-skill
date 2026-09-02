---
name: paper-section-writer
description: Draft submission-ready mathematical-modeling paper sections from the approved solution package, frozen numbers, human decision ledger, and verified figures without searching scattered exploratory outputs or inventing interpretation.
whenToUse: In submission, when paper sections must be drafted from the solution package and frozen numbers only.
---

# References

- `references/upstream-section-templates.md` — self-written abstract/introduction patterns and paper-card evidence system (see repo `references/upstream/nature-writing/` for the Apache-2.0 originals).

# Preconditions

- `rigor_profile` is `submission`.
- The three writer prerequisites hold (numbered exactly as in
  `workflow-orchestrator` G5 and AGENTS.md "Submission Artifact Contract"):
  1. a final method explanation exists (`methods/Qx/qx_final_method_explanation.md`);
  2. a final result analysis exists (`results/Qx/reports/qx_final_result_analysis.md`);
  3. the solution package and current per-question frozen numbers exist
     (`results/Qx/reports/qx_solution_package_for_writer.md` and
     `results/Qx/reports/frozen_numbers.json`).
- Required human claim-scope and physical/domain-meaning decisions are recorded.

If any prerequisite is missing, return to its producer rather than drafting around the gap.

# Primary Sources

Use, in order:

1. `results/Qx/reports/qx_solution_package_for_writer.md`
2. `results/Qx/reports/frozen_numbers.json` (per-subquestion frozen claims)
3. `qx_decisions.jsonl`
4. verified paper figures/tables
5. final method explanation and robustness report for clarification

Do not hunt through raw experiment folders to invent a narrative.

# Workflow

1. Resolve the requested section and contest format.
2. Build a claim map:
   - claim ID;
   - frozen value/source;
   - robustness support;
   - human decision ID;
   - figure/table reference;
   - limitation.
3. Draft the method description to match the final explanation and code.
4. Draft results with:
   - value and comparison;
   - human-confirmed physical/domain meaning;
   - uncertainty or robustness;
   - limitation and applicable scope.
5. Mention the baseline and eliminated alternatives only when they explain a real decision.
6. Use only Type 2–4 figures as appropriate; never place Type 1 diagnostics in the paper.
7. Save `paper/sections/qx.tex` or the requested Markdown section.

# Human-Owned Content

The AI must not originate:

- why the method was chosen;
- what the headline number means physically;
- confidence and claim scope;
- contribution framing.

Transcribe these from the decision ledger with provenance. If absent, invoke a compact choice card and stop the final draft until answered; do not fill the paper with repeated sentinels.

# Rules

- Every numerical claim must match `results/Qx/reports/frozen_numbers.json` for its subquestion.
- Do not overclaim against untested methods or populations.
- Do not fabricate citations or causal meaning.
- Avoid procedural diary prose and ceremonial detail.
- Keep formulas, symbols, units, captions, and filenames consistent.
- Do not create a new decision artifact.

# Verification

- The three writer prerequisites (final method explanation, final result
  analysis, solution package + frozen numbers) all pass.
- Claim map resolves all numbers and judgments.
- Method, results, and figures match canonical artifacts.
- Physical meaning and contribution are human-owned.
- Limitations and uncertainty are visible.
- No Type 1 figure appears.


## Writer gate enforcement

Do not draft a final section from merely existing reports. Require current lineage, frozen-number references, human claim-scope provenance, and a passed G5 gate. If any prerequisite is absent, return `GATE_BLOCKED` with the exact producer and artifact needed.


## v0.3 writer enforcement

Require current frozen-number lineage, human claim-scope provenance, and the derived G5 gate before writing a final paper section. A result report alone is not a writer source.
