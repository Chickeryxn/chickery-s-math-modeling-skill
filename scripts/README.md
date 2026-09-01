# Workflow integrity scripts

These scripts are standard-library-only and domain-neutral. They enforce or audit the project contracts; they do not choose a mathematical model.

## Common commands

```powershell
python scripts/validate_repo.py .
python scripts/run_tests.py
python scripts/validate_skill_trees.py .
python scripts/sync_plugin.py . --check
python scripts/validate_model_contract.py planning/model_contract.example.json
python scripts/validate_decisions.py . methods/Q1/q1_decisions.jsonl
python scripts/workflow_guard.py . require Q1 model_code
python scripts/lineage.py assess . path/to/artifact.lineage.json
python scripts/validate_artifacts.py . planning/manifests/Q1.json
python scripts/validate_run_snapshot.py . results/Q1/experiments/run1
```

## Contracts

- `workflow_guard.py`: monotonic gates and sensitive artifact eligibility. `derive Qx` returns the gate at which the evidence is currently stuck (G1..G(n-1) satisfied, Gn not yet evidenced); `require Qx <kind>` allows producing an artifact only when that value is at least the kind's minimum gate. A manifest cannot promote the derived gate.
- `validate_decisions.py`: verifiable user-source requirement for `DECIDED`. A `DECIDED` record must contain a nested `source` with `source_type=user_answer`, `user_message_id`, and `user_verbatim_answer`, and use `recorded_at` as the timestamp. To cite external/user evidence as `evidence:<id>`, create `planning/evidence_registry.json` first (see `planning/evidence_registry.example.json`).
- `create_run_snapshot.py`: unified `run` execution plus begin/finalize/validate snapshot lifecycle; successful runs must be executed by the runner. The command runs through the local shell, so the command string must be trusted.
- `lineage.py`: hash-addressed source lineage and stale assessment.
- `validate_independence.py`: main/baseline/verifier separation checks.
- `validate_model_contract.py`: problem-specific contract shape check.
- `qa_report.py`: layered status summary; it never upgrades a blocked gate.
- `sync_plugin.py`: portable skill-tree synchronization and hash check.
- `resource_index.py`: scans `resource-library/` and (re)builds `index.json`; `--check` verifies the index matches disk.
- `training_scorecard.py`: literacy training scorecard contract. `round <dir>` scaffolds/validates one round's `scorecard.json` (six dimensions, agent self-scores with evidence paths, null user scores, mechanical-check list); `summary <dir>` aggregates rounds into `summary.json` (radar, ranking, mechanical tally); `--check` modes validate without writing.

## Run lifecycle

Use `run` for normal experiments so the tool captures command output and return code:

```powershell
python scripts/create_run_snapshot.py run . runs/run1 --command "python code/main.py" --result-ref results/result.json --validation-ref results/validation.json --planned-budget "{\"iterations\":100}"
python scripts/validate_run_snapshot.py . runs/run1
```

Use `begin`/`finalize` only for integrations that can provide equivalent runner evidence. Direct finalization with `executed_by_runner=false` cannot claim `SUCCESS`.
