# Changelog

## 0.4.2 — 2026-09-01

- **Size**: shrunk the repository without changing functionality — optimized the 4 diagram PNGs (re-save) and moved the 4 archify interactive HTML files (2.85 MB) out of git into on-demand regeneration (`generated/`, Node ≥ 18; JSON sources + SVG/PNG remain committed); updated README/archify docs and added `docs/diagrams/archify/generated/` to `.gitignore`.
- **Learning/capability layer**: added `docs/learning-path.md` (6-station learning path explaining why each gate exists), `docs/post-contest-review.md` (post-contest review with decision-ledger playback), and a practice-problem index in `method-index.md`.
- **Quality tooling**: added `scripts/abstract_checker.py` (abstract length / per-subquestion-number / AI-trace checks); `ai_trace_checker.py` supports `--config` custom thresholds; `latex_assembly.py` gained a bare-number scan (advisory), `--check-only`/`--strict` modes, and its report now includes the scan; `scripts/learning_summary.py` generates a post-contest review skeleton from ledgers + frozen numbers.
- **Method card**: added a rationale chain (why chosen / why not / falsification condition) and a main-vs-baseline comparison-evidence table to the method-card contract.
- Tests grew to 81 (abstract checker, learning summary, latex bare-number scan, ai-trace config, upstream-asset hash/NOTICE).

## 0.4.1 — 2026-09-01

- Fixed `cleanroom-patterns.md` raincloud rendering bug (mixed scalar/array plot) and verified all six patterns execute end to end.
- Hardened `latex_assembly.py`: frozen values are type-checked and LaTeX-escaped (dict/list values skipped and reported); added frozen-reference warnings, `refs.bib` → `\bibitem` injection, and a weighted page estimate.
- Trimmed the imported `figure-and-code-guide.md` to matplotlib-only guidance (draw.io/Visio/R/seaborn/C++ recommendations removed) and aligned its UPSTREAM.md declaration.
- Expanded `ai_trace_checker.py` rule set to the upstream de-AI-writing caps (absolute counts, moreover+furthermore combined limit) and added unit tests.
- Enhanced `validate_upstream_assets.py`: per-file SHA-256 drift guard (`hashes.json`, `--write-hashes`), stricter license check, and NOTICE.md cross-validation; added unit tests.
- Added unit tests for `ai_trace_checker`, `validate_upstream_assets`, and the imported `check_consistency.py` (68 total).
- Added source headers to all 22 upstream-imported files; added archify CLI regeneration notes; extended the method index with mixed-type routing and anti-homogenization rules.
- Fixed README test-count (34→68) and removed the stale dual-engine routing note in `references/README.md`.

## 0.4.0 — 2026-09-01

- Added the upstream integration layer: `references/upstream/` with provenance-tracked knowledge assets (nature-skills figure/writing/statistics rules under Apache-2.0; Lupynow de-AI-writing/self-review/phrase-bank/decision matrix under MIT; clean-room method index and XiaoMaColtAI methodology mapping).
- Added `scripts/validate_upstream_assets.py` (pure stdlib) wired into `validate_repo.py`; added `scripts/ai_trace_checker.py` (quantifiable AI-trace scan) and `scripts/latex_assembly.py` (paper section assembly + frozen-number macro injection + AI-use declaration) with tests.
- Added clean-room paper baseline `templates/paper/main.tex` and `docs/paper-build.md` (CUMCMThesis remains a build-time external dependency, not vendored).
- Enriched `math-figure-generator` (clean-room patterns), `paper-polisher`, `paper-section-writer`, `reference-manager`, `robustness-checker`, `method-selector` references.
- Added `LICENSES/` and `NOTICE.md` for third-party attribution.

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
