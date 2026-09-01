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
```

## Contracts

- `workflow_guard.py`: monotonic gates and sensitive artifact eligibility.
- `validate_decisions.py`: verifiable user-source requirement for `DECIDED`.
- `create_run_snapshot.py`: begin/finalize immutable experiment metadata.
- `lineage.py`: hash-addressed source lineage and stale assessment.
- `validate_independence.py`: main/baseline/verifier separation checks.
- `validate_model_contract.py`: problem-specific contract shape check.
- `qa_report.py`: layered status summary; it never upgrades a blocked gate.
- `sync_plugin.py`: portable skill-tree synchronization and hash check.
