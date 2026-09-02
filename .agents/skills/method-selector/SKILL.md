---
name: method-selector
description: Build and risk-screen a compact role-based method shortlist for a mathematical-modeling subquestion. Use after problem framing and data profiling, before model code generation, to propose a main candidate, a usable baseline, and at most one conditional fallback without padding the pool.
license: MIT
whenToUse: When framing and data are ready and a role-based method shortlist with risk probes is needed before a human method choice.
---

# Purpose

Convert the framed problem and data profile into a small executable decision surface. Screen methods for load-bearing data, assumption, degeneracy, sensitivity, and scale risks before asking the human to choose.

This skill proposes and probes methods. The human chooses the method.

# Preconditions

- G1 problem framing passed.
- Required output and evaluation criteria are known.
- Relevant data inventory or audit exists.
- `planning/symbol_table.md` and `planning/model_assumptions.md` exist when the problem needs them.

If these are missing, return to the producer skill rather than guessing.

# Inputs

- Problem parse and classification.
- Data audit, including missingness, effective sample size, imbalance, cardinality, and distribution summaries.
- Literature analysis when available.
- Contest deadline, implementation language, interpretability needs, and compute limits.
- `planning/session_config.json`.
- Existing `methods/Qx/qx_method_card.md` and decision ledger when revising.

# Workflow

1. **Align the decision surface.**
   - Invoke `decision-prompt-builder` before generating an open-ended shortlist.
   - Ask about human-owned trade-offs, not algorithm names.
   - Reuse answers already present in the decision ledger.

2. **Derive method requirements.**
   - Start from required output, hard constraints, data characteristics, validation criteria, explanation burden, and experiment budget.
   - Identify the failure modes that would make a method unusable.

3. **Create a role-based shortlist.**
   - Generate candidates from **at least two modeling paradigms** unless the required output locks the paradigm (use the repo-level `references/abstraction-patterns.md` for the abstraction four-step and multi-paradigm templates).
   - One `main_candidate`: best fit to the chosen trade-off.
   - One `usable_baseline`: completes the real task and yields directly comparable outputs.
   - At most one `conditional_fallback`: differs in a meaningful mathematical way and has an explicit activation trigger.
   - If a simple reference cannot complete the real task, label it `diagnostic_reference`; it does not satisfy the baseline requirement.
   - Do not add a method merely to reach a candidate count; do not silently keep only one paradigm when the problem admits several.

4. **Define method-specific risk checks.**
   - Use the contract in `references/risk-probe-contract.md`.
   - Select only relevant assumption checks.
   - Always check output degeneracy or concentration with metrics appropriate to the output.
   - Bound probe runtime rather than source-line count.

5. **Run the risk probe on the main candidate and usable baseline.**
   - Use a representative slice or full-data diagnostic as appropriate; never rely only on the first rows.
   - The probe may use reusable scripts and may save detailed metrics, but its canonical output is one compact summary.
   - Probe the fallback only enough to establish that its trigger and risk profile are credible. Do not fully implement it.

6. **Write canonical artifacts.**
   - `methods/Qx/qx_method_card.md`
   - `methods/Qx/probes/risk_probe_summary.json`
   - Update `planning/manifests/Qx.json` if present.

7. **Ask for the method choice.**
   - Present the probe evidence through a choice card.
   - After the user answers, hand the exact answer to `modeler-decision-logger` for append-only capture in `methods/Qx/qx_decisions.jsonl`.
   - If no answer is available, stop. Do not create a placeholder decision file.

# Method Card Contract

`qx_method_card.md` stays compact and contains:

> Machine anchors: the role tokens `main_candidate` and `usable_baseline` and the section headers `Risk-probe summary` and `Baseline validity` are read by the gate engine (`scripts/workflow_guard.py`). Keep those exact tokens/headers anywhere in the file — they already appear in the tables below. All other prose (rationale chain, notes, compact history) may be written in Chinese. Do not leave placeholders such as `TODO`, `占位`, or `待填` anywhere in the card.

```markdown
# Qx Method Card

## Goal and success criteria

## Human constraints
- Output form:
- Priority:
- Unacceptable failure:
- Experiment budget:
- Complexity budget (why this complexity is needed):
- Interpretability need (who must be able to explain it):

## Shortlist
| ID | Role | Mathematical idea | Why eligible | Why not chosen (if not main) | Main risk | Implementation cost |

## Rationale chain (teaching aid)
For the main candidate, write one evidence-linked sentence per item — this is what the human will defend in the paper and what you should be able to explain to a teammate:
- Why this method fits the output form and data (assumption match):
- Why the baseline is a fair comparison:
- What would make this choice wrong (falsification condition):

## Main-vs-baseline comparison evidence (G2)
| Dimension | Main candidate | Usable baseline | Note |
|---|---|---|---|
| Metric difference (probe) | | | quantified, not adjectives |
| Complexity cost | | | runtime / implementation burden |
| Interpretability | | | who can explain it |
| Risk profile | | | from the risk probe |

## Baseline validity
- Real task completed:
- Comparable output/metric:
- If no, classification: diagnostic_reference

## Risk-probe summary
| ID | Executability | Data/assumptions | Degeneracy | Sensitivity | Scale | Verdict |

## Fallback trigger
- Trigger:
- Evidence to evaluate:

## Compact history
- One line per material change, with decision_id when human-owned.
```

Do not maintain a separate iteration log for new work.

# Probe Verdicts

- `PASS`: eligible for the human choice.
- `CONDITIONAL`: eligible only with a stated mitigation or fallback trigger.
- `FAIL`: not offered as a selectable main or baseline.

A method fails screening when a load-bearing assumption fails, the output degenerates, it cannot produce a legal result, or its cost violates the user's budget. A method does not fail merely because an irrelevant generic diagnostic is unavailable.

# Output and Handoff

After G2 screening:

- If the human choice is absent: return the evidence-backed choice card.
- If G2.5 is decided: hand the method card, probe summary, chosen IDs, and experiment budget to `model-code-analyzer`.
- Instruct code generation to implement only the approved main method and usable baseline.
- Keep the fallback dormant until its recorded trigger fires.

# Rules

- Do not use a fixed candidate count.
- Do not use source-line count as validation quality.
- Do not invent missing data fields, constraints, labels, or evaluation metrics.
- Do not call a nonfunctional toy method a baseline.
- Do not fully implement all shortlisted methods.
- Do not select the method or write the human rationale.
- Keep AI suggestions visibly separate from the human decision.

# Compatibility

When revising an older workspace, read:

- `methods/Qx/qx_method_candidates.md`
- `methods/Qx/qx_method_iteration_log.md`
- `methods/Qx/poc/`

Migrate material evidence into the method card and probe summary. Do not require new legacy PoCs or iteration logs.

# References

- Risk checks and summary schema: `references/risk-probe-contract.md`
- Method-family routing cues: `references/method-family-guide.md`
- Upstream method resources (self-written index + MIT decision matrix): `references/upstream-method-resources.md`
- Multi-paradigm abstraction: repo `references/abstraction-patterns.md`
- Algorithm cookbooks (MIT, advisory): repo `references/upstream/lupynow-cookbook/`

# Verification

- Shortlist contains a main candidate and a genuinely usable baseline.
- Optional fallback has a concrete trigger.
- Main and baseline have evidence-backed probe verdicts.
- Output-degeneracy checks are present.
- Method card and probe summary exist.
- No per-skill pending decision file was created.
- No code-generation handoff occurs before a human method choice is recorded.
