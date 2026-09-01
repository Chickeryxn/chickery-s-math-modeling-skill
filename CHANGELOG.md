# Changelog

## 0.4.4 — 2026-09-01

- **Model diversity & abstraction**: added `references/abstraction-patterns.md` (abstraction four-step + 2–3 modeling paradigms per problem type + simplification ladder); `method-selector` now requires ≥2 modeling paradigms in the shortlist (unless the output locks one) and references the cookbooks; `method-index` gained the multi-paradigm/simplification section.
- **Imported Lupynow cookbooks ×8** (MIT): optimization/ML/evaluation/mechanistic/statistical/network/clustering/game-theory "selection quick-reference + core formulas + traps" under `references/upstream/lupynow-cookbook/` (provenance + hashes registered).
- **Publication-grade figures**: imported nature-figure pure-stdlib render audits (`audit_panel_alignment.py`, `audit_pdf_text.py`, `validate_figure.py`, Apache-2.0); added `references/publication-gallery.md` (per-chart-type top-journal standards with good/bad samples); added 4 more clean-room matplotlib patterns (forest, density ridge, clustered heatmap, multi-panel time series); added `scripts/figure_consistency_check.py` (set-wide naming/size/manifest consistency).
- **Structure-conforming writing**: added `references/paper-skeleton.md` (full contest skeleton with purpose/structure/red lines per section); `scripts/section_structure_check.py` (section presence, order, length share); imported nature-reviewer `technical-concern-taxonomy.md` (Apache-2.0); `abstract_checker` now checks conclusion coverage per subquestion (`--subquestions`).
- Tests grew to 111.

## 0.4.3 — 2026-09-01

- **High-quality modeling answers**: added `scripts/model_quality_gate.py` (G4-preceding mechanical gate: seed recorded, baseline comparable with real metrics, uncertainty present or explicitly N/A, output contract aligned); `scripts/leakage_check.py` (time-column disorder, target duplication, duplicate rows heuristics for predictive data); `scripts/claim_coverage.py` (every subquestion must have a paper section, frozen numbers, and abstract number coverage).
- **Modeling discipline**: added `docs/modeling-self-review.md` (assumptions / complexity / interpretability / fairness / result-baseline checklist between G2 and G4) and `planning/timeline.md` (72h/96h time budget across the six gates); method-card contract gained complexity-budget and interpretability-need fields; `workflow_guard derive` now reports a `next_stage_hint`.
- Tests grew to 102 (quality gate, leakage, claim coverage, stage hint).

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
