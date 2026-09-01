# Changelog

## 0.3.1 — 2026-09-01

- Fixed a gate deadlock: `solution_package` and `frozen_numbers` are now producible at G4 (previously both required G5 while their absence capped the derived gate at G4); `frozen_numbers` still requires a human `package_signoff`.
- Made `risk_probe_ready` accept both the documented array-shaped and dict-shaped `methods` in `risk_probe_summary.json` (previously the array shape crashed `workflow_guard derive` with an uncaught `AttributeError`).
- Aligned decision records on `recorded_at` + nested `source` (user-answer provenance) across `AGENTS.md`, the decision-logger skill, and the validator; `validate_decisions.py` now rejects non-ISO-8601 timestamps.
- Aligned `references/README.md` with the current G1–G6 gate contract and the single matplotlib figure engine; fixed `related-paper-analyzer` input paths and added the `workspace/papers/` skeleton.
- Clarified the derive/require gate semantics, independence runtime-reference contract, and `evidence_registry.json` usage in the docs.
- Added gate-progression regression tests covering the full G1–G6 path to `final_assembly`.

## 0.3.0 — 2026-09-01

- Added evidence-derived gate computation instead of trusting manifest gates.
- Added strict user-answer evidence paths and decision supersession validation.
- Added a unified experiment runner with output-change, return-code, and budget-degradation checks.
- Added lineage hash maps, propagation, and manifest-level lineage validation.
- Added layered QA integration and explicit independent-role runtime references.
- Added bilingual README documentation and corrected the single marketplace/two manifest layout.
- Added end-to-end synthetic workflow tests for regression, scheduling, and dynamic-event families.


## 0.2.0 — 2026-09-01

- Added executable workflow gate checks and monotonic manifest transition validation.
- Added verifiable human-decision provenance checks.
- Added immutable experiment run snapshots with planned/actual budget and hash manifests.
- Added domain-neutral model-contract and artifact-lineage contracts with stale detection.
- Added independent main/baseline/verifier validation.
- Added layered QA status vocabulary and generic continuous-event tests.
- Added synthetic regression, scheduling, and dynamic-event contract tests.
- Added portable Python skill synchronization for Windows, Linux, and macOS.
- Separated optional presets from the domain-neutral core.
- Deliberately did not add a network/offline policy.
