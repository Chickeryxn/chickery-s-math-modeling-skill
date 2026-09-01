# Mathematical Modeling Workspace and Codex Skills

[简体中文](README.md) | [English](README.en.md)

This project provides a mathematical-modeling workflow template with executable gate checks, decision provenance, experiment snapshots, artifact lineage, independence checks, and layered QA.

## Quick start

```bash
git clone https://github.com/Chickeryxn/chickery-s-math-modeling-skill.git
cd chickery-s-math-modeling-skill
git checkout mathmodeling-new-skeleton
```

Open the repository root in Codex or Claude. Put the current problem statement and attachments in:

```text
workspace/problem.txt
workspace/data_raw/<attachments>
```

Treat raw attachments as read-only and write cleaned copies under `workspace/data_clean/`. The default workflow is:

```text
problem-parser
→ problem-classifier
→ data-auditor-cleaner
→ workflow-orchestrator
```

The session configuration is in `planning/session_config.json`, with `learning + lean` as the default.

## G1–G6 workflow

```text
G1 Problem Framed
→ G2 Method Screened
→ G2.5 Chosen by Human
→ G3 Code and Experiment Reviewed
→ G4 Results Judged and Frozen
→ G5 Paper Section Ready
→ G6 Final Audit
```

Gate status is derived from the manifest and canonical evidence; a manifest cannot promote itself. A passing local script does not imply that the overall gate passed. Human method, result, stability, and claim-scope decisions belong in append-only JSONL ledgers.

## Workflow integrity tools

Common commands:

```powershell
python scripts/run_tests.py
python scripts/validate_repo.py .
python scripts/validate_skill_trees.py .
python scripts/sync_plugin.py . --check
python scripts/validate_model_contract.py planning/model_contract.example.json
python scripts/workflow_guard.py . derive Q1
python scripts/workflow_guard.py . require Q1 model_code
python scripts/create_run_snapshot.py run . runs/<run_id> --command "python code/main.py" --result-ref results/result.json --validation-ref results/validation.json
python scripts/lineage.py assess . path/to/artifact.lineage.json
```

See `scripts/README.md` for detailed arguments and `schemas/README.md` for contract guidance.

## Model contract

During problem framing, create a problem-specific `model_contract.json` describing entities, inputs, state functions, decision variables, hard and soft constraints, the objective, evaluator, uncertainty handling, and validation. `schemas/model_contract.schema.json` is domain-neutral and should not contain problem entities or parameters.

Main, usable baseline, and verifier implementations must reference the same model contract and hash while retaining independent implementation and run evidence.

## Experiment snapshots and artifact lineage

Use the unified runner to record planned and actual budgets, budget deltas, input/code/config hashes, command, environment, return code, result, and validation files. A run with a material budget reduction is marked `DEGRADED_SUCCESS`, and stability or optimality claims must be qualified.

Key artifacts should carry lineage with source, validation, consumer, code/config/input hashes, and decision IDs. Changed source hashes make dependent artifacts `STALE`; stale artifacts cannot be used for freezing or final paper assembly.

## Human decisions and independence

A `DECIDED` record must have verifiable user-answer provenance; an AI summary cannot replace the user's verbatim answer. Main, baseline, and verifier are separate roles. Different filenames alone do not prove independence; use the dedicated validator for static references and runtime evidence.

## Layout and plugins

```text
.codex/skills/
.claude/skills/
plugins/mathmodeling-skills/skills/
planning/
methods/
code/
results/
robustness/
paper/
schemas/
scripts/
tests/
workspace/
```

The project has one marketplace catalog:

```text
.agents/plugins/marketplace.json
```

and two plugin manifests:

```text
plugins/mathmodeling-skills/.codex-plugin/plugin.json
plugins/mathmodeling-skills/.claude-plugin/plugin.json
```

After updating `.codex/skills/`, run `python scripts/sync_plugin.py .` to update the Claude and plugin distribution copies.

## Presets and references

Presets under `planning/presets/` must be explicitly activated, versioned, and marked advisory. They may provide defaults but cannot override a problem contract or human decision. Content under `references/` is advisory knowledge and is not automatically required for a new problem.

## Tests and limitations

```powershell
python scripts/run_tests.py
python scripts/validate_repo.py .
```

The tests cover gates, human decisions, run snapshots, budget degradation, lineage/stale status, independence, continuous events, model contracts, skill synchronization, layered QA, and three synthetic scenario families.

The project provides a workflow template and executable validation tools; it does not claim to prevent every direct file write that bypasses the tools. The project does not encode an offline or network policy.
