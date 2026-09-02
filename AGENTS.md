# Core Philosophy

- **The AI owns mechanical correctness; the human owns modeling judgment.**
- Start from goals, objects, constraints, data, outputs, variables, relationships, and checkable conclusions.
- Do not start from model names or favorite techniques.
- Separate assumptions, observations, derivations, and validated conclusions.
- Preserve evidence that changes a decision; do not create files merely to prove that a skill ran.

# Configuration

`planning/session_config.json` has two independent controls:

```json
{
  "interaction_mode": "learning",
  "rigor_profile": "lean"
}
```

- `interaction_mode`: `learning` or `speed`. It changes question density and when AI suggestions are shown.
- `rigor_profile`: `lean` or `submission`. It changes artifact and audit density, never the human-judgment boundary.
- Default to `learning + lean` in a fresh workspace.
- Use `lean` while exploring and iterating. Switch to `submission` only when preparing writer handoff or final assembly.
- Optional `deadline` (ISO-8601): when present, `workflow_guard.py derive` emits an advisory `deadline_hint` (remaining-time guidance such as "switch to submission", "stop new experiments"); it is never a gate input.
- For compatibility, read legacy `{ "mode": "learning" | "speed" }` as `interaction_mode`.

# Repository Skill Copies

- `.codex/skills/` and `.claude/skills/` are two complete, independently usable skill trees; `.agents/skills/` is the third standalone copy, auto-discovered by DeepSeek Harness (DSH) 0.7.0 when the repo is opened as the workspace (project-level root, no installation needed).
- Every skill and referenced local resource required at runtime must exist in every tree; no tree may depend on a wrapper, symlink, or path into another tree.
- When a shared skill contract changes, update and validate all copies in the same change.
- Runtime-specific wording may differ only when necessary, but each copy must remain standalone and behaviorally consistent with this policy.
- `plugins/mathmodeling-skills/skills/` is the generated distribution copy used by the native Codex and Claude plugin manifests. After the standalone trees agree, refresh the distribution copy with `python scripts/sync_plugin.py .` (portable, works on Windows) or the POSIX wrapper `scripts/sync-plugin.sh`, and verify with `python scripts/sync_plugin.py . --check` / `scripts/sync-plugin.sh --check`.
- Keep both plugin manifests and the marketplace catalog aligned for every release. Bump the version in both plugin manifests and keep the marketplace catalog aligned.

# Runtime Notes (DeepSeek Harness desktop 0.7.0)

DSH runs the same workspace and scripts; the workflow contract is unchanged. Operational notes:

- The workspace root opened in DSH is `PROJECT_ROOT`; the sandbox default is `workspace-write`, which allows writing inside the workspace root plus platform temp dirs. Scripts that must write outside (e.g. `--out` to an external path) require a wider sandbox permission with justification.
- `python` and `git` must be on `PATH` (the harness inherits the environment; it ships no Python).
- The per-session identifier is `$env:DSH_SESSION_ID`; record it as `user_message_id` in decision ledgers using the convention `dsh:<session_id>:<seq>` (a non-empty string per the decision schema). `$env:DSH_SESSION_JSONL` points at the session log if referenced.
- Agent hooks are not active by default in DSH; the optional SessionStart guardrail banner requires a profile patch (see `docs/dsh-compatibility.md`). The Claude-only `plugins/mathmodeling-skills/hooks/hooks.json` (guardrail banner + frozen/raw-data guard) remains inert in DSH and Codex unless the optional patch is applied.
- Console encoding: scripts force UTF-8 output; `validate_repo.py` captures child output as UTF-8 with replacement errors, so CJK text is safe on GBK consoles.

# Workflow Discipline

- Parse before classifying; classify before screening methods.
- Ask the modeler about output form, priority, unacceptable failure, and experiment budget before creating a method shortlist.
- Build a role-based shortlist rather than filling a quota:
  - one `main_candidate`;
  - one `usable_baseline`;
  - at most one `conditional_fallback`.
- Allow only a main candidate plus baseline when no genuine fallback exists.
- A trivial reference that cannot complete the real task is `diagnostic_reference`, not a baseline.
- Fully implement the human-approved main method and usable baseline only. Activate a fallback only when its recorded trigger fires.
- Keep changes minimal, traceable, and reviewable.

# Human Decision Convention

Human decisions are captured in one append-only ledger per subquestion:

`methods/Qx/qx_decisions.jsonl`

Use `planning/framing_decisions.jsonl` for global or pre-subquestion framing decisions made before a Qx method directory exists.

Each line is a JSON object with at least:

```json
{
  "decision_id": "q2_method_choice",
  "decision_type": "method_choice",
  "status": "DECIDED",
  "decided_by": "human",
  "captured_in_mode": "learning",
  "choice": "M2",
  "rationale": "M2 is selected because ...",
  "evidence_refs": ["methods/Q2/probes/risk_probe_summary.json"],
  "recorded_at": "ISO-8601 timestamp",
  "source": {
    "source_type": "user_answer",
    "user_message_id": "<user message id>",
    "user_verbatim_answer": "<user's verbatim answer>"
  }
}
```

- A `DECIDED` record must contain the nested `source` object above; without a verifiable user answer the record is invalid per `scripts/validate_decisions.py`. Use `recorded_at` (ISO-8601) for the timestamp.

- The AI may present evidence and options but must not originate the human's choice, rationale, confidence, physical interpretation, or submission authorization.
- The AI may append the user's answer verbatim or faithfully structure it; it must not strengthen or invent the rationale.
- Do not create per-skill `*_modeler_decision.md` files for new work.
- Existing decision Markdown files remain readable during migration but are not required for new work.
- A decision passes only when it is human-authored, evidence-linked, non-empty, and contains no placeholder.

# Choice Cards

Use choice cards only at modeling-judgment points, normally twice per subquestion:

1. Before method screening: output form, interpretability/performance priority, unacceptable failure, experiment budget.
2. After the first meaningful experiment: proceed, adjust, or activate the fallback.

An optional third card may be used before final freeze for claim scope and confidence. Do not ask users to decide mechanically checkable matters.

Additional human decision types enforced by the gate engine but not part of a choice-card flow: `package_signoff` (required before `frozen_numbers` may be produced, G4) and `submission_authorization` (consumed by `latex_assembly.py` for the AI-use declaration). Record them in the same JSONL ledger with the same `source` requirements.

# Workflow Gates

The gate engine (`scripts/workflow_guard.py derive Qx [--profile lean|submission|auto]`) derives gates from canonical evidence. `--profile auto` reads `planning/session_config.json` (`rigor_profile`); the engine default is the strict `submission` derivation. In `lean`, the engine caps at the G4 result-judgment subgate (freeze/paper/audits are submission gates). The engine checks artifact existence and structural depth, not semantic PASS verdicts — audit contents are judged by the human at handoff.

## G1 — PROBLEM_FRAMED

- Parse, classification, data inventory, success criteria, and human framing exist.
- Note: the gate engine derives G1 from the mechanical files and their structural depth: a parse declaring `subquestions` must give each a `goal` and a non-empty `required_outputs`; a classification declaring `subquestions` must give each a `primary_type`. When the parse lists `human_decisions_needed`, a verifiable human `framing` record (`planning/framing_decisions.jsonl` or the Qx ledger) is required before screening. Success-criteria review remains a human step at this stage.

## G2 — METHOD_SCREENED

- `methods/Qx/qx_method_card.md` defines the main candidate, usable baseline, and optional conditional fallback.
- `methods/Qx/probes/risk_probe_summary.json` exists.
- The main candidate and usable baseline pass the applicable risk checks.
- Any fallback has an explicit activation trigger.
- No fixed candidate count or source-line limit is used.

## G2.5 — METHOD_CHOSEN_BY_HUMAN

- `qx_decisions.jsonl` contains a `DECIDED` human `method_choice` record citing probe evidence.
- Code generation is allowed only when G2 and G2.5 both pass.

## G3 — CODE_AND_EXPERIMENT_REVIEWED

- The approved main method and usable baseline ran.
- `results/Qx/experiments/roundN/run_summary.json` records configuration, seed, metrics, outputs, and failures.
- A language review artifact contains the required named checks:
  - `syntax`
  - `input_contract`
  - `method_alignment`
  - `reproducibility`
  - `output_contract`
- New review artifacts use `code/Qx/reviews/qx_<lang>_review.json`. Legacy Markdown reviews may be read during migration.

## G4 — RESULTS_JUDGED_AND_FROZEN

- The human decision ledger contains result, stability, and claim-scope verdicts tied to computed evidence.
- Final result analysis and robustness report exist.
- In `submission` profile, the solution package and immutable `frozen_numbers.json` exist and are current.
- Note: the gate engine derives G4 from disk evidence under the active profile. In `lean`, G4 is the result-judgment subgate: the human result/stability/claim-scope verdicts on computed evidence. In `submission`, G4 additionally requires the final result analysis, robustness report, solution package, package sign-off, and current `frozen_numbers.json`. Artifact contents are judged by the human reviewers at G4/G6. G3 gates on the latest experiment round only; older exploratory rounds without run snapshots are advisory, not blocking.

## G5 — PAPER_SECTION_READY

- The writer uses the solution package as the primary source.
- Numerical claims come from `frozen_numbers.json`.
- Physical/domain interpretation and contribution claims are human-confirmed.
- Every paper figure passes render verification.

## G6 — FINAL_AUDIT_PASSED

Run only in `submission` profile. All three must pass:

- cross-media consistency;
- semantic completeness;
- final quality assurance.

Note: as with G4, the engine checks audit-artifact existence, not their PASS verdicts; the audit contents are verified by the human at handoff. G5/G6 are submission-only gates: the engine does not evaluate them under `--profile lean`.

# Risk Probe Contract

The risk probe replaces universal ≤30-line PoCs. It is time-bounded, method-specific, and may use reusable scripts.

`methods/Qx/probes/risk_probe_summary.json` must contain:

- `executability`: can the method produce a legal result?
- `data_coverage`: missingness, effective sample size, imbalance, cardinality, and distribution coverage.
- `assumption_checks`: only checks relevant to the method, such as stationarity, multicollinearity, identifiability, clusterability, or constraint feasibility.
- `output_degeneracy`: variance, unique-output count, top-k mass, entropy/Gini, score or rank concentration, and constraint slack where applicable.
- `perturbation_sensitivity`: response to a small justified perturbation.
- `scale_check`: runtime and memory at representative sizes.
- `verdict`: `PASS`, `CONDITIONAL`, or `FAIL`, with evidence and fallback trigger when conditional.

Do not reject a method merely because an irrelevant generic test is unavailable. Do reject or condition it when a load-bearing assumption fails or its output degenerates.

# Lean Artifact Contract

During exploration, keep only:

```text
planning/session_config.json
planning/framing_decisions.jsonl       # only when global framing decisions exist
planning/manifests/Qx.json
methods/Qx/qx_method_card.md
methods/Qx/qx_decisions.jsonl
methods/Qx/probes/risk_probe_summary.json
results/Qx/experiments/roundN/run_summary.json
```

- `planning/manifests/Qx.json` is the machine-readable state source.
- Derive dashboards from manifests; do not rewrite a large dashboard after every state transition.
- `qx_method_card.md` contains roles, assumptions, risks, fallback triggers, and a compact decision history. Do not maintain a separate iteration log for new work.
- Successful runs store summaries and artifact paths. Persist full console logs only for failures or when needed to reproduce an anomaly.
- Ordinary rounds do not require a Markdown experiment report. Generate one only at a human decision point or for the final round.

# Submission Artifact Contract

Before writer handoff, add:

```text
methods/Qx/qx_final_method_explanation.md
code/Qx/reviews/qx_<lang>_review.json
results/Qx/reports/qx_final_result_analysis.md
robustness/Qx/qx_robustness_report.md
results/Qx/reports/qx_solution_package_for_writer.md
results/Qx/reports/frozen_numbers.json
```

The three critical writer rules remain:

1. No final method explanation, no paper section.
2. No final result analysis, no writer handoff.
3. The writer reads the solution package rather than guessing from scattered results.

# Change Impact and Auditing

Classify a change before auditing:

- `NONE`: scratch files, formatting, comments, non-semantic documentation. No consistency audit.
- `LOCAL`: exploratory code or method-card changes before freeze. Run local tests/review only.
- `CANONICAL`: data schema/units, symbols, equations, parameters, official result values, or figure paths. Run a scoped consistency check for affected Qx.
- `FROZEN`: anything that can change a frozen number or paper claim. Log the thaw, update the canonical source, rerun affected experiments, re-freeze, then run scoped consistency.

Do not run a full-workspace audit merely because multiple files changed. Always run the full three-auditor layer once in `submission` profile before final assembly.

# Frozen Numbers

- Numbers flow code → results → freeze → paper.
- Never edit `frozen_numbers.json` by hand.
- To change a frozen value: **解冻 → 修改 canonical source → 重跑 affected work → 重冻结**.
- Record the reason in `results/Qx/reports/freeze_change_log.md`.
- A freeze is stale when a referenced canonical source is newer than `frozen_at`.
- `scripts/check_frozen_freshness.py .` automatically flags stale claims (missing source, source newer than `frozen_at`, or invalid `frozen_at`) and is wired into `validate_repo.py`; run it before G4/G6 in `submission`.

# Experiment Output

Every executed round writes:

```text
results/Qx/experiments/roundN/
├── figures/
├── tables/
├── metrics/
└── run_summary.json
```

Create `logs/` only when a failure, warning, or reproducibility need justifies it.

`run_summary.json` records question, round, approved methods, role, status, inputs, outputs, metric summary, seed, environment, warnings, and fallback-trigger state.

# Modeling and Coding Rules

- Match methods to output, data, interpretability, time, and contest constraints.
- Do not choose complexity for appearance.
- Do not invent data, assumptions, evidence, results, or references.
- Keep assumptions explicit and distinguish necessary from simplifying assumptions.
- Maintain `planning/symbol_table.md`; define every symbol and unit before use.
- Use fixed random seeds.
- Save formal outputs to files; console output alone is not a deliverable.
- Keep raw data untouched under `workspace/data_raw/`; write cleaned copies under `workspace/data_clean/`.

# Figures and Paper

- Type 1 diagnostic: internal only.
- Type 2 comparison: may appear in paper; like Type 3/4 it must pass render verification in `submission`.
- Type 3 paper: must support a main claim and pass publication-quality render checks.
- Type 4 appendix: supplementary and referenced from the main text; render-verified in `submission`.
- The figure generator writes a sibling `<figure>.render.json` (status `PASS`, `rendered_at`, checks) for every Type 2–4 figure; `scripts/figure_render_audit.py .` verifies that every figure referenced by a paper section exists and carries render evidence.
- Paper claims must remain proportional to tested evidence.
- Mention eliminated methods only when the record helps explain a real trade-off; do not manufacture breadth.

# Verification

- In `lean`, verify the current gate and only the affected artifacts.
- In `submission`, verify all required artifacts, frozen-number lineage, figure rendering, references, and the three independent audits.
- A review or audit passes by completing its named semantic checks, not by reaching an arbitrary bullet count.
- Flag uncertainty and blocking issues explicitly.
- Do not approve final assembly while any G6 auditor fails.


# Machine-Enforced Workflow Integrity (v0.3)

The prose rules above are paired with repository-local validators under `scripts/`. Skills must treat these as the executable contract:

- Run `python scripts/validate_repo.py .` for repository integrity checks.
- Run `python scripts/workflow_guard.py . derive Qx` and `require Qx <artifact_kind>` before creating sensitive downstream artifacts; the derived state is authoritative over the manifest cache.
- A `DECIDED` ledger record is valid only when it contains a nested `source` with `source_type=user_answer`, `user_message_id`, and `user_verbatim_answer`; AI-authored summaries are not sufficient.
- Every completed experiment must have an immutable run snapshot containing planned and actual budgets, input/code/config hashes, command, environment, result reference, and validation reference.
- Main, baseline, and verifier are separate roles. A baseline or verifier may not claim independence by reading the main result as its only numeric input.
- Problem-specific semantics belong in a project `model_contract.json`; `schemas/model_contract.schema.json` remains domain-neutral.
- Key artifacts must carry a sibling `.lineage.json` or an equivalent lineage object with source, input, config, code hashes, and decision IDs. Run `scripts/validate_artifacts.py` and reject `MISSING`/`STALE` artifacts.
- QA must report mechanical, semantic, provenance, lineage, independence, human-judgment, and gate status separately; a local check passing does not imply final assembly is allowed.

The repository intentionally does not encode an offline/network policy. Network restrictions, if desired, remain an environment or user-level concern.
