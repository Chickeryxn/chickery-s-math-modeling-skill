# Schemas

The schema files are **documented contracts** (lightweight, human-readable,
domain-neutral). The executable checks live in the `scripts/validate_*.py`
validators and in the golden-example guard (`tests/test_examples.py`); the JSON
files themselves are not loaded by any validator, so the coupling between the
two sides is enforced by `tests/test_schemas_consistency.py` — when you change
a validator's required keys or status vocabulary, update the matching schema
file (and vice versa) in the same change. A new problem supplies a separate
`model_contract.json`; do not modify these schemas with problem entities or
parameters.

The decision and run snapshot schemas are checked by `validate_decisions.py`
and `validate_run_snapshot.py`; the model contract is checked by
`validate_model_contract.py` (each validator's `required`/status sets must
equal the schema's).

- `lineage.schema.json`: source, validation, input/config/code hash, and stale-state contract (produced by `scripts/lineage.py make`, assessed by `scripts/lineage.py assess`).
- `run_snapshot.schema.json`: immutable experiment snapshot contract (produced by `scripts/create_run_snapshot.py`, validated by `scripts/validate_run_snapshot.py`).
- `decision.schema.json`: human-decision provenance contract (validated by `scripts/validate_decisions.py`).

## Artifacts without a dedicated schema file

The following workspace artifacts are validated by hand-written checks in the
scripts or by the golden-example guard (`tests/test_examples.py`), not by a
JSON Schema in `schemas/`:

- `planning/manifests/Qx.json` — checked by `scripts/validate_manifest.py` (shape + no gate overclaim) and `tests/test_examples.py`;
- `planning/parse/problem_parse.json`, `planning/classification/problem_classification.json` — structural depth checked by `scripts/workflow_guard.py` (`parse_ready` / `classification_ready`) and `tests/test_examples.py`;
- `methods/Qx/probes/risk_probe_summary.json` — checked by `scripts/workflow_guard.py` (`risk_probe_ready`);
- `results/Qx/experiments/roundN/run_summary.json` — consumed by `scripts/model_quality_gate.py`, `validate_independence.py`, `qa_report.py`; shape guarded by `tests/test_examples.py`;
- `results/Qx/reports/frozen_numbers.json` — checked by `scripts/check_frozen_freshness.py`, `claim_coverage.py`, `latex_assembly.py`; shape guarded by `tests/test_examples.py`;
- key artifacts' sibling `.lineage.json` — produced by `scripts/lineage.py make`; a structural teaching sample lives at `planning/examples/lineage.example.json` (self-referential, not part of any real gate derivation).

Keep these shape guarantees in one place: if you change a producer (a skill or
`scripts/`), update the matching golden example and the `tests/test_examples.py`
assertions in the same change.
