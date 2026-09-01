# Schemas

The schemas are lightweight, human-readable contracts consumed by the repository-local validators. They are intentionally domain-neutral. A new problem supplies a separate `model_contract.json`; do not modify these schemas with problem entities or parameters.


The decision and run snapshot schemas are checked by `validate_decisions.py` and `validate_run_snapshot.py`; the model contract is checked by `validate_model_contract.py`.

- `lineage.schema.json`: source, validation, input/config/code hash, and stale-state contract.
