# Mathematical Modeling Contest AI Skill Library

[简体中文](README.md) | [English](README.en.md)

**Math Modeling Skill** — an Agent skill library and executable workflow framework for mathematical-modeling contests (CUMCM / MCM/ICM): 32 Claude/Codex/DSH skills plus 27 standard-library-only validation scripts turn "AI writes code, humans make decisions, everything reproducible and auditable" into a machine-enforced process contract.

| Badge | Value |
|---|---|
| License | [MIT](LICENSE) |
| Version | 0.6.0 (plugin manifests in sync) |
| Runtime | Python 3.10+ (standard library only, no third-party dependencies) |
| Platforms | Windows / Linux / macOS |
| Tests | 138 cases, `python scripts/run_tests.py` all green |

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick start](#quick-start)
- [Workflow and gates](#workflow-and-gates)
- [Skill catalog 32](#skill-catalog-32)
- [Contract system](#contract-system)
- [Command reference](#command-reference)
- [Directory layout](#directory-layout)
- [Test coverage](#test-coverage)
- [FAQ](#faq)
- [Glossary](#glossary)
- [Upstream integration](#upstream-integration)
- [Learning and review](#learning-and-review)
- [Training mode](#training-mode)
- [Work record tree](#work-record-tree)
- [DeepSeek Harness adaptation](#deepseek-harness-adaptation)
- [Limitations](#limitations)
- [License and acknowledgements](#license-and-acknowledgements)

## Overview

### The problem it solves

AI assistance is allowed in modeling contests, but letting an agent "free-wheel" creates two kinds of risk:

1. **The AI oversteps modeling judgment** — picking methods, fabricating rationales, and drawing conclusions on the modeler's behalf, which violates contest rules and academic integrity;
2. **Untrustworthy results** — whether the code actually ran, where numbers came from, and whether artifacts are stale can never be checked.

### The approach

This project splits a contest into six gate stages (G1–G6). Passing each gate requires **evidence artifacts** that can be verified on disk; the validators under `scripts/` check them automatically, so gates are driven by evidence and can never be self-declared. Meanwhile, 32 single-purpose skills cover every step from reading the problem to delivering the paper, with a clear division of labor between AI and human.

### Three core principles

| Principle | Meaning |
|---|---|
| **AI owns mechanical correctness** | Parsing, coding, running experiments, assembling evidence, and drafting sections are AI tasks |
| **Humans own modeling judgment** | Method choice, result verdicts, confidence, physical meaning, and contribution framing are human decisions, always recorded |
| **Evidence drives everything** | Gates, freezes, and paper numbers must trace back to real on-disk artifacts and hashes, never to verbal claims |

## Features

| Capability | What it does | What it prevents |
|---|---|---|
| Gate checks (G1–G6) | Derives the current gate from evidence; monotonic progression | Skipping stages; promoting a gate by editing the manifest |
| Decision provenance | Human decisions recorded in append-only JSONL ledgers bound to the user's verbatim answer | AI summaries masquerading as human judgment |
| Experiment snapshots | Unified runner records budget, hashes, command, environment, return code | Unreproducible results; claiming completion after budget cuts |
| Artifact lineage | Key artifacts carry source/validator/hashes; upstream changes mark consumers `STALE` | Using stale artifacts for freezing or paper assembly |
| Independence checks | main / baseline / verifier roles verified for distinct scripts and runtime refs | Fake baselines, fake verifiers, or reading the main result as the only input |
| Layered QA | Mechanical / semantic / provenance / lineage / independence / human-judgment / gate reported separately | A local check passing masquerading as overall approval |

## Quick start

```bash
git clone https://github.com/Chickeryxn/chickery-s-math-modeling-skill.git
cd chickery-s-math-modeling-skill
git checkout mathmodeling-new-skeleton
```

Open the repository root in Codex, Claude, or **DeepSeek Harness (DSH) desktop**, then put the problem statement and attachments in:

```text
workspace/problem.txt
workspace/data_raw/<attachments>
```

Raw attachments are read-only; cleaned copies go under `workspace/data_clean/`. The default workflow is:

```text
problem-parser → problem-classifier → data-auditor-cleaner → workflow-orchestrator
```

Session configuration lives in `planning/session_config.json`: `interaction_mode` (`learning`/`speed`) controls question density, `rigor_profile` (`lean`/`submission`) controls artifact and audit density. Fresh workspaces default to `learning + lean`; switch to `submission` before final assembly.

## Workflow and gates

Every subquestion (Q1, Q2, …) advances independently through the same gates. Gate state is derived from on-disk evidence by `scripts/workflow_guard.py derive Qx`; **the manifest is only a cache and cannot promote itself**, and transitions must be monotonic.

![Generic gate pipeline](docs/diagrams/archify/assets/mm-generic-workflow.png)

| Gate | Name | Pass conditions (evidence) | Main outputs |
|---|---|---|---|
| G1 | PROBLEM_FRAMED | Parse, classification, data inventory, success criteria, and human framing exist | `planning/parse/`, `planning/classification/` |
| G2 | METHOD_SCREENED | Method card defines main candidate + usable baseline; risk probe verdicts all PASS/CONDITIONAL; fallback has a trigger | `methods/Qx/qx_method_card.md`, `probes/risk_probe_summary.json` |
| G2.5 | METHOD_CHOSEN_BY_HUMAN | Ledger contains a human `DECIDED` `method_choice` record (bound to the user's verbatim answer) | `methods/Qx/qx_decisions.jsonl` |
| G3 | CODE_AND_EXPERIMENT_REVIEWED | Approved main and baseline executed; run summary complete; language review passes the five named checks | `code/Qx/reviews/`, `results/Qx/experiments/roundN/` |
| G4 | RESULTS_JUDGED_AND_FROZEN | Result/stability/claim-scope verdicts present; in `submission`, solution package and `frozen_numbers.json` exist and are current | `results/Qx/reports/` |
| G5 | PAPER_SECTION_READY | Writer uses the solution package as the only source; numbers come from the freeze; interpretation/contribution human-confirmed | `paper/sections/` |
| G6 | FINAL_AUDIT_PASSED | Consistency, completeness, and QA audits all pass (submission profile only) | `paper/audits/`, `paper/qa_report.md` |

**Key rules**

- Model code may be generated only when G2 and G2.5 both pass.
- Human method/result/stability/claim-scope decisions must be recorded in the append-only JSONL ledger; AI may not write the rationale.
- Every number in the paper must come from `results/Qx/reports/frozen_numbers.json`; changing a value requires "thaw → update the source → rerun → re-freeze" with a change log entry, never manual edits.
- Figures are typed: Type 1 diagnostics never enter the paper; only Type 3/4 may, and only after passing render checks.

More diagrams: [gate lifecycle](docs/diagrams/archify/assets/mm-gate-lifecycle.png) · [skill architecture](docs/diagrams/archify/assets/mm-workspace-architecture.png) · [document freeze chain](docs/diagrams/archify/assets/mm-document-chain.png) (interactive HTML is generated on demand with Node ≥ 18; see `docs/diagrams/archify/README.md`).

## Skill catalog 32

The skill tree ships as complete standalone copies under `.codex/skills/`, `.claude/skills/`, and `.agents/skills/` (auto-discovered by DSH; `plugins/mathmodeling-skills/skills/` is the distribution copy). Grouped by pipeline stage, plus a training-mode group:

### Problem understanding

| Skill | One-line responsibility | Main outputs |
|---|---|---|
| `problem-parser` | Parses the problem into goals, objects, constraints, outputs, subquestions, and success criteria | `planning/parse/problem_parse.json` |
| `problem-classifier` | Classifies subquestion task types from required output and structure; surfaces framing ambiguities for humans | `planning/classification/problem_classification.json` |
| `related-paper-analyzer` | Analyzes only user-supplied papers under `workspace/papers/` for transferable method cues | `workspace/papers/related_paper_analysis.md` |
| `data-auditor-cleaner` | Maps attachments, audits and cleans data, emits one reusable data profile | `workspace/data/data_profile.json`, `data_clean/` |

### Method and decisions

| Skill | One-line responsibility | Main outputs |
|---|---|---|
| `method-selector` | Builds a role-based shortlist (main + usable baseline + ≤1 conditional fallback) and runs method-specific risk probes | `methods/Qx/qx_method_card.md`, `probes/risk_probe_summary.json` |
| `decision-prompt-builder` | Builds one "choice card" at genuine modeling-judgment points, max 3 questions | Not persisted (returns a choice_card) |
| `modeler-decision-logger` | Faithfully appends the human's verbatim answer to the decision ledger | `methods/Qx/qx_decisions.jsonl` |
| `model-assumptions-builder` | Extracts and maintains global/method assumptions; necessity labels stay human-owned | `planning/model_assumptions.md` |
| `symbol-table-builder` | Maintains the global symbol/unit table and resolves cross-question conflicts | `planning/symbol_table.md` |

### Code and experiments

| Skill | One-line responsibility | Main outputs |
|---|---|---|
| `model-code-analyzer` | Translates the human-approved method into a language-neutral implementation and experiment contract | `code/Qx/qx_code_plan.md` |
| `python-model-code-generator` | Generates and runs minimal reproducible Python for main + baseline | `code/Qx/*.py`, `run_summary.json` |
| `matlab-model-code-generator` | Generates and runs MATLAB / Beita Tianyuan compatible code | `code/matlab/Qx/*.m`, `run_summary.json` |
| `code-reviewer` | Routes work to the matching language reviewer | — (router) |
| `python-code-reviewer` | Five named checks: syntax / input contract / method alignment / reproducibility / output contract | `code/Qx/reviews/qx_python_review.json` |
| `matlab-code-reviewer` | Same named checks plus toolbox and Beita Tianyuan compatibility | `code/matlab/Qx/reviews/qx_matlab_review.json` |
| `robustness-checker` | Runs perturbation, resampling, baseline-comparison, and other risk-targeted checks | `robustness/Qx/qx_robustness_summary.json` |

### Results and paper

| Skill | One-line responsibility | Main outputs |
|---|---|---|
| `result-report-generator` | Condenses experiment artifacts into decision-point evidence; never picks the winner | `results/Qx/reports/qx_final_result_analysis.md` |
| `figure-table-planner` | Plans the smallest evidence-bearing set of figures/tables (Type 1–4) | `methods/Qx/qx_figure_table_plan.md` |
| `math-figure-generator` | Produces publication-quality figures with shared color/layout conventions and render checks | `paper/figures/` |
| `final-method-explainer` | Builds the authoritative final method explanation from card/ledger/results | `methods/Qx/qx_final_method_explanation.md` |
| `solution-package-builder` | Assembles the writer package and freezes numbers after human sign-off | `results/Qx/reports/qx_solution_package_for_writer.md`, `frozen_numbers.json` |
| `paper-section-writer` | Drafts sections only from the solution package and frozen numbers | `paper/sections/qx.tex` |
| `paper-polisher` | Grammar, consistency, and overclaim calibration (borrowing nature-polishing principles) | Polished `paper/sections/` |
| `reference-manager` | Verifies citation authenticity, generates BibTeX, flags unverified entries | `paper/refs.bib`, `paper/reference_audit.md` |

### Orchestration and auditing

| Skill | One-line responsibility | Main outputs |
|---|---|---|
| `workflow-orchestrator` | Gate scheduler: reads state, derives gates, routes the next action; never models/codes/writes itself | `planning/manifests/Qx.json` (state source) |
| `completeness-auditor` | Checks required evidence per active profile is present and current | `paper/audits/completeness_audit.md` |
| `consistency-auditor` | Cross-media checks of numbers, symbols, parameters, decisions, and files | `paper/audits/cross_media_consistency_audit.md` |
| `quality-assurance-auditor` | Final five-dimension audit (workflow/evidence/method/paper/presentation) | `paper/qa_report.md` |
| `work-logger` | Maintains the `records/` work-record tree: session logs, gate transitions, mirrored decision cards | `records/` (`scripts/work_record.py`) |

### Training mode

| Skill | One-line responsibility | Main outputs |
|---|---|---|
| `training-solver` | Closed-book solve of a training problem: never reads `resource-library/` | `results/training/roundN/solution/` |
| `training-reflector` | Open-book literacy comparison against the resource library, per dimension | `results/training/roundN/reflection.md` |
| `training-auditor` | Runs mechanical checks, drafts the 6-dimension literacy scorecard, aggregates for human direction | `results/training/roundN/scorecard.json`, `summary.json` |

## Contract system

Domain-neutral contracts live in `schemas/` and are enforced by the validators in `scripts/`; **new problems must not modify the schemas** — problem semantics go into the separate `planning/model_contract.json`.

| Contract | Schema file | Validator | Description |
|---|---|---|---|
| Model contract | `schemas/model_contract.schema.json` | `validate_model_contract.py` | Entities/inputs/state functions/decision variables/constraints/objective/evaluator/uncertainty/validation; main, baseline, and verifier must reference the same contract hash |
| Human decisions | `schemas/decision.schema.json` | `validate_decisions.py` | `DECIDED` requires a `source` (`user_answer` + message id + verbatim answer) and an ISO-8601 `recorded_at` |
| Run snapshot | `schemas/run_snapshot.schema.json` | `create_run_snapshot.py` / `validate_run_snapshot.py` | Planned/actual budgets, input/code/config hashes, command, environment, return code; success must be runner-executed |
| Artifact lineage | `schemas/lineage.schema.json` | `lineage.py` / `validate_artifacts.py` | Source/validator/consumer/hashes/decision IDs; upstream changes mark consumers `STALE` |

## Command reference

| Command | Purpose |
|---|---|
| `python scripts/run_tests.py` | Run the whole test suite (standard-library unittest) |
| `python scripts/validate_repo.py .` | Repository-wide integrity check (skill trees, tests, contracts, snapshots, lineage, QA) |
| `python scripts/validate_skill_trees.py .` | Hash consistency across the three skill trees + plugin manifest versions |
| `python scripts/sync_plugin.py . [--check]` | Sync `.codex/skills/` → `.claude/skills/` and the plugin distribution copy |
| `python scripts/workflow_guard.py . derive Q1` | Derive Q1's current gate from evidence |
| `python scripts/workflow_guard.py . require Q1 model_code` | Gate check before producing sensitive artifacts (GATE_BLOCKED otherwise) |
| `python scripts/validate_model_contract.py planning/model_contract.example.json` | Validate contract shape and print the contract hash |
| `python scripts/validate_decisions.py . methods/Q1/q1_decisions.jsonl` | Validate the decision ledger (provenance, append-only, timestamps) |
| `python scripts/create_run_snapshot.py run . runs/<run_id> --command "python code/main.py" --result-ref results/result.json --validation-ref results/validation.json` | Execute an experiment via the unified runner and create an immutable snapshot |
| `python scripts/validate_run_snapshot.py . runs/<run_id>` | Validate snapshot integrity (success must be runner-executed) |
| `python scripts/lineage.py assess . path/to/artifact.lineage.json` | Assess lineage status CURRENT/STALE/MISSING |
| `python scripts/validate_artifacts.py . planning/manifests/Q1.json` | Validate manifest-declared artifacts have CURRENT lineage |
| `python scripts/qa_report.py .` | Generate the layered QA report (any blocking layer missing → not PASS) |

See [`scripts/README.md`](scripts/README.md) for detailed arguments and [`schemas/README.md`](schemas/README.md) for contract guidance.

## Directory layout

```text
.
├── .codex/skills/                 # Codex skill tree (32 skills; sync source)
├── .claude/skills/                # Claude skill tree (complete standalone copy)
├── .agents/skills/                # DeepSeek Harness skill tree (auto-discovered in-repo, complete standalone copy)
├── plugins/mathmodeling-skills/   # Distribution package (two manifests + skills + hooks)
├── .agents/plugins/marketplace.json  # marketplace catalog entry
├── AGENTS.md                      # Single source of truth for workflow policy (gates/artifacts/decisions/freeze/audits)
├── CLAUDE.md                      # Claude-specific operating rules
├── planning/                      # Session config, parse/classification, manifests, presets, example contracts
├── methods/Qx/                    # Method cards, decision ledgers, risk probes, final explanations
├── code/                          # Model code and reviews (code/Qx/, code/matlab/Qx/)
├── results/Qx/                    # Experiment rounds, reports, solution package, frozen_numbers.json
├── results/training/              # Training-mode artifacts (roundN/ and summary.json)
├── robustness/Qx/                 # Robustness evidence
├── paper/                         # Sections, figures, references, and the three final audits
├── workspace/                     # problem.txt, data_raw/ (read-only), data_clean/, papers/
├── resource-library/              # Training-mode showcase library (papers/ideas/figures/formulas/tables/assets)
├── records/                       # Work-record tree (sessions/subjects/gates/decisions/retros; advisory)
├── references/                    # Upstream knowledge base (historical decisions, advisory, not required)
├── schemas/                       # Domain-neutral contracts (4 schemas + README)
├── scripts/                       # 27 standard-library-only scripts (incl. 1 bash-compatible wrapper)
├── docs/diagrams/archify/         # Generic flow diagrams (PNG/SVG/JSON sources; interactive HTML generated on demand)
└── tests/                         # 138 test cases
```

## Test coverage

`python scripts/run_tests.py` (138 cases, standard library only) covers:

- Evidence-derived gate computation and monotonic transitions (including a full G1→G6 progression to `final_assembly`)
- Human-decision provenance (fake human, unregistered evidence, escaping paths all rejected)
- Run snapshots and budget degradation (`DEGRADED_SUCCESS`; success without the runner rejected)
- Artifact lineage and STALE propagation
- main/baseline/verifier independence (shared metric sources rejected)
- Model-contract shape, skill-tree synchronization, layered QA
- Three synthetic scenario families (regression / scheduling / dynamic events) end to end
- Risk-probe list/dict shape compatibility
- Paper assembly (`latex_assembly`: assembly, frozen-macro escaping, unsafe-value skipping, AI declaration)
- Upstream asset validation (`validate_upstream_assets`) and AI-trace scanning (`ai_trace_checker`)
- AI-trace scanning (`ai_trace_checker`, `--config` thresholds)
- Abstract quality (`abstract_checker`) and learning summary (`learning_summary`)
- Model quality gate (`model_quality_gate`), leakage heuristics (`leakage_check`), and claim coverage (`claim_coverage`)
- Figure-set consistency (`figure_consistency_check`) and paper section-structure check (`section_structure_check`)
- Abstract/conclusion quality (`abstract_checker`, with subquestion conclusion coverage)
- Resource-library index (`resource_index`) and training scorecard (`training_scorecard`: template, evidence-path validation, cross-round aggregation, drift detection)
- Work-record tree (`work_record`: scaffold/log/gate/decision-card/index/check, incl. time and gate monotonicity, link and index-sync checks)

## Learning and review

- [Learning path](docs/learning-path.md): six stations (read the problem, frame, choose methods, code/experiments, results/paper, reviewer's eye) explaining why each gate exists, with exercises and self-checks.
- [Post-contest review](docs/post-contest-review.md): revisit which modeling judgments were validated or overturned; `python scripts/learning_summary.py .` generates a review skeleton.
- [Modeling self-review](docs/modeling-self-review.md): structured review between G2 and G4 (assumptions / complexity / interpretability / fairness / result baseline).
- Time budget template: `planning/timeline.md` (72h/96h breakdown across the six stages).
- Agent capability resources: `references/abstraction-patterns.md` (multi-paradigm abstraction), `references/publication-gallery.md` (publication figure standards), `references/paper-skeleton.md` (paper skeleton), `references/upstream/lupynow-cookbook/` (8 algorithm cookbooks), `references/upstream/nature-figure/` (incl. render audit scripts).

## Training mode

A dedicated literacy-training loop for high-quality modeling answers (full manual: [`docs/training.md`](docs/training.md)):

- **Showcase library**: `resource-library/` keeps excellent papers, creative ideas, good figures, formulas, and tables in separate folders (`index.json` generated/verified by `python scripts/resource_index.py .`) — a literacy benchmark, not an answer key.
- **Closed-book solve**: `training-solver` solves a training problem **without reading the library** (enforced by `planning/training_config.json` → `closed_phase_forbidden_paths` plus the skill's own rules).
- **Open-book reflection**: `training-reflector` compares the solution with the showcase per dimension (mathematical / innovation / figure / expression / evidence / completeness) and writes transferable gaps.
- **Multi-dimensional audit**: `training-auditor` first runs the mechanical checks (quality gate / claim coverage / abstract / AI-trace / leakage / figure consistency / section structure), then drafts the 6-dimension scorecard (`python scripts/training_scorecard.py round|summary ...`) so you can pick the next direction and finalize scores.
- Each round lands in `results/training/roundN/` (solution/, reflection.md, scorecard.json); aggregation in `results/training/summary.json`. Normal contest flow never reads the library.

## Work record tree

A detailed, human-readable process log layered over the machine-readable contracts (full manual: [`docs/work-record.md`](docs/work-record.md)): `records/` is one folder with a multi-level tree of Markdown docs — `sessions/` (session logs), `subjects/` (per-subquestion narratives), `gates/` (gate transitions), `decisions/` (decision cards mirrored from the ledger), `retros/` (retrospectives). Tool: `python scripts/work_record.py` (init/log/gate/decision/retro/index/check; pure stdlib); the `work-logger` skill tells the agent when and what to record. The tree is **advisory**: facts and evidence links only, never part of gate judgment.

## DeepSeek Harness adaptation

Full audit: [`docs/dsh-compatibility.md`](docs/dsh-compatibility.md). Key points:

- DSH 0.7.0 auto-discovers the in-repo `.agents/skills/` tree (32 skills, open-and-use, no install); `AGENTS.md`/`CLAUDE.md` are auto-injected; the default `workspace-write` sandbox allows writing inside the opened repo.
- Prerequisites: `python` (≥3.10) and `git` on PATH; decision-ledger `user_message_id` convention `dsh:<$env:DSH_SESSION_ID>:<seq>`.
- 4-tree sync: `python scripts/sync_plugin.py . [--check]` (portable, Windows; POSIX wrapper `sync-plugin.sh`); `validate_skill_trees.py` verifies all 4 trees + both manifests + marketplace.
- Claude/Codex compatibility unchanged: `.codex-plugin`/`.claude-plugin`/`marketplace.json`/`hooks.json` remain and stay validated; `hooks.json` is inert in DSH by default (optional patch documented in the audit).

## FAQ

**Q: Can it do the problem or write the paper for me?**
No. AI handles mechanical correctness only; method choice, result verdicts, physical interpretation, and contribution framing must be decided by you and recorded — this is also what contest AI-usage rules require.

**Q: What dependencies do I need?**
None. All scripts use only the Python standard library; `python scripts/run_tests.py` is a self-check.

**Q: Does it work with both Codex and Claude?**
Yes. The two skill trees are each complete and consistent. When editing skills, change `.codex/skills/` first, then run `sync_plugin.py` to refresh the other copies.

**Q: Why is the default branch named `mathmodeling-new-skeleton`?**
It is the current development line. After cloning, run `git checkout mathmodeling-new-skeleton` as shown in this README.

**Q: Why is my experiment marked `DEGRADED_SUCCESS`?**
The actual budget fell below the planned budget (for example, fewer iterations). The run still succeeds, but stability/optimality claims must be downgraded — you may not claim the original plan was completed.

**Q: Can I edit `frozen_numbers.json` by hand?**
No. To change a value: thaw → update the canonical source → rerun the affected experiments → re-freeze, and record the reason in `freeze_change_log.md`.

**Q: Can diagnostic figures go into the paper?**
No. Type 1 diagnostics are internal only; only Type 3/4 figures may enter the paper, after passing render verification.

**Q: How do I extend or modify a skill?**
Edit `.codex/skills/<skill>/SKILL.md`, run `python scripts/sync_plugin.py .`, then verify with `validate_skill_trees.py`.

**Q: What is the relationship to upstream libraries such as XiaoMaColtAI?**
This project merges six upstream projects (XiaoMaColtAI, CUMCMThesis, Lupynow, nature-skills, sci-box, …) and locks 12 decisions; the historical record is in [`references/README.md`](references/README.md), but the current executable contract is `AGENTS.md`, `schemas/`, and `scripts/`.

## Glossary

| Term | Meaning |
|---|---|
| Gate | One of G1–G6 plus the G2.5 human-choice point; evidence-derived and monotonic |
| Manifest | `planning/manifests/Qx.json`, the machine-readable state cache per subquestion (cannot promote a gate) |
| Canonical evidence | Real, authoritative artifacts on disk — the only basis for gate derivation |
| Risk probe | Method-specific, time-bounded mini-experiment checking executability/data coverage/assumptions/output degeneracy/perturbation/scale |
| Choice card | 2–3 mutually exclusive options with consequences at a modeling-judgment point, answered by the human |
| Decision ledger | `methods/Qx/qx_decisions.jsonl`, append-only JSONL; `DECIDED` must bind the user's verbatim answer |
| Run snapshot | Immutable experiment record from the unified runner (budget/hashes/command/environment/return code) |
| DEGRADED_SUCCESS | A successful run whose actual budget fell short of the plan; related claims must be qualified |
| Lineage | An artifact's source/validator/consumer/hash record; upstream changes mark consumers `STALE` |
| Model contract | `planning/model_contract.json`, problem-specific definitions of entities/constraints/objective/evaluation/validation |
| Frozen numbers | `frozen_numbers.json`, the single source of truth for paper numbers; never edited by hand |
| main / baseline / verifier | Main method / usable baseline / independent verifier — separate roles that must prove independence |
| rigor profile | `lean` (minimal exploration artifacts) or `submission` (full artifacts and the three final audits) |
| interaction mode | `learning` (more questions, suggestions after answering) or `speed` (fewer questions, suggestions alongside) |
| preset | An explicitly activated, versioned, advisory set of defaults that cannot override contracts or human decisions |

## Upstream integration

Without changing the governance core (AGENTS.md / schemas / scripts, G1–G6 gates, the 28-skill skeleton plus 3 training skills and 1 record-keeping skill, zero third-party runtime dependencies, single matplotlib engine), this project integrates the knowledge-rule layer and pure-standard-library tool layer of six upstream projects:

| Upstream | What is integrated | How |
|---|---|---|
| [nature-skills](https://github.com/Yuan1z0825/nature-skills) (Apache-2.0) | Figure contract/QA/PALETTE, polishing rules, statistics P0/P1/P2, result-allocation and consistency tools | Verbatim under `references/upstream/`, notices retained |
| [Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills) (MIT) | De-AI-writing rules, four-round self review, phrase bank, Figure Contract, method decision matrix | Verbatim, copyright retained |
| [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) (no license; not copied) | Gate mapping, 9-point numerical robustness checklist, reproducibility ideas | Clean-room rewrite under `references/upstream/method-index/` |
| [sci-box](https://github.com/jihe520/sci-box) (no license; not copied) | Figure-pattern inspiration | Clean-room figure templates (in `math-figure-generator` references) |
| [CUMCMThesis](https://github.com/latexstudio/CUMCMThesis) (no license; not vendored) | Contest paper template | Build-time external dependency; see [`docs/paper-build.md`](docs/paper-build.md) |
| [archify](https://github.com/tt-a1i/archify) (MIT) | Flow-diagram generation | External tool + committed artifacts (`docs/diagrams/archify/`) |

Integration discipline: Apache-2.0 / MIT content keeps its notices and license texts; unlicensed or proprietary content (e.g. XiaoMaColtAI `tools/docx|pdf|xlsx`) is never copied; networked execution (search/MCP) and third-party runtimes (Node/TeX/Pandoc/LibreOffice) stay out of the core. Verify with `python scripts/validate_upstream_assets.py .`. See [`references/upstream/README.md`](references/upstream/README.md), `LICENSES/`, and `NOTICE.md` for provenance.

## Limitations

- This project provides a **workflow template and executable validation tools**; it does not claim to prevent every direct file write that bypasses the tools.
- Validators check **on-disk artifacts**; the honesty of the workflow ultimately depends on the user following it.
- This project **does not encode an offline/network policy**; offline constraints are an environment- or user-level concern.
- Gates and audits are quality assurance, not a guarantee of contest outcomes or paper conclusions.

## License and acknowledgements

[MIT License](LICENSE). This project merges and borrows from [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill), [latexstudio/CUMCMThesis](https://github.com/latexstudio/CUMCMThesis), [Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills), [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills), and [jihe520/sci-box](https://github.com/jihe520/sci-box); diagrams are generated by [tt-a1i/archify](https://github.com/tt-a1i/archify). See [`references/README.md`](references/README.md) for the merged decisions.
