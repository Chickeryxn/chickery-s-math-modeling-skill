# Changelog

## 0.9.0 — 2026-09-02

Maintenance release from a full multi-angle audit (P0 correctness → P3 engineering):

- **Validator correctness (P0)**:
  - `leakage_check` no longer crashes on mixed date/numeric time columns (epoch normalization); `--delimiter` is honored; mixed formats flagged.
  - `claim_coverage` maps Chinese-numeral section headings (问题三 → Q3) so present sections are not reported MISSING.
  - `check_frozen_freshness` rejects escaping/absolute source refs, accepts `+0800` offsets on Python 3.10, warns on tz-less `frozen_at`, and documents mtime semantics.
  - `latex_assembly` detects duplicate claim ids, keeps macro names unique, parses .bib with balanced braces (skips @comment), fixes the LaTeX-comment stripping condition, counts characters not bytes, guards unresolved template placeholders, and emits a single AI-declaration section.
  - `work_record` replay reads `current_gate`; session artifact links get a `../../` prefix and `check` resolves links from the file's directory; decision cards quote verbatim values.
  - `run_tests` refuses a false-green pass when no tests are discovered.
  - `workflow_guard` validates the Qx id shape and keeps snapshot references inside the project root.
- **Contract unification (P1)**: per-question frozen-number paths everywhere; audit cycle de-locked (consistency → completeness → QA); the three writer prerequisites defined once; model-code-analyzer owns `model_contract.json` + the independent verifier; one shared review status vocabulary; training rounds isolated from contest paths; unified render-evidence key set; MATLAB snapshots must come from the unified runner.
- **Docs/examples/upstream (P2)**: reference.md/dsh-compatibility test-count drift fixed and guarded by `test_doc_claims`; archify index skill count fixed; golden examples made internally consistent (value ↔ locator ↔ ledger) with cross-example assertions; post-contest lessons no longer target hash-protected upstream files; NOTICE labels modified imports and all four skill trees; five-state upstream usage map added; `validate_upstream_assets` requires full hashes.json coverage; clean-room TOC line removed from the paper template.
- **Engineering (P3)**: GitHub Actions CI (Py 3.10–3.12 × Ubuntu/Windows) running tests + repo validation + tree checks + CRLF hygiene; deterministic deadline-hint tests; real-validator synthetic scenario tests; orphan fixtures removed; `tests/support.py`; `scripts/lib/common.py` shared helpers; `validate_repo --only/--skip-tests`; `validate_decisions --json`; uncertainty N/A declarations honored by the model quality gate; marketplace carries a version enforced against plugin manifests; frozen guard fails open on unknown tools; figure audit ignores commented/verbatim `\includegraphics`; `license: MIT` frontmatter on all 32 skills.
- Version badges/plugin manifests/marketplace bumped to 0.9.0; tests grew to 243.

## 0.8.0 — 2026-09-02

Full content-strategy hardening (engine semantics, automated-gap closure, golden examples, decision-interface policy, training cold start):

- **Profile-aware gates**: `workflow_guard derive/require` accept `--profile lean|submission|auto` (auto reads `session_config.rigor_profile`; default stays strict submission). In lean the engine caps at the G4 result-judgment subgate (human verdicts on computed evidence); freeze/paper/audits remain submission gates. `qa_report` and `validate_manifest` derive under each manifest's `rigor_profile`, so lean workspaces are no longer misreported as `GATE_BLOCKED`.
- **Structural depth checks**: parse subquestions need `goal` + non-empty `required_outputs`; classification subquestions need `primary_type`; usable risk-probe candidates must carry `output_degeneracy`; method-card placeholders are rejected. G1 blocks when the parse declares `human_decisions_needed` with no verifiable human framing record yet. G3 gates on the latest experiment round only (older exploratory rounds are advisory). Optional advisory `deadline_hint` from `session_config.deadline` or `--deadline`.
- **Automation gaps closed**: `scripts/check_frozen_freshness.py` (frozen claims must resolve to sources not newer than `frozen_at`; wired into `validate_repo`); `scripts/figure_render_audit.py` (paper-referenced figures exist and carry `<name>.render.json` PASS evidence; Type 2–4 figures entering the paper all require render evidence); `scripts/preflight.py` (one-command submission bundle over claim_coverage / abstract / ai-trace / latex `--strict` / figure consistency / skeleton); `scripts/polish_stats.py` (quantified long-sentence/filler/connector metrics for paper-polisher). Run snapshots record an optional `vcs` block (git HEAD + dirty files).
- **Decision-interface policy**: method-card machine anchors documented as language-locked (Chinese body allowed); `user_message_id: "unavailable:<platform>"` marker policy instead of invented ids; batch matrix cards in speed mode with per-subquestion independence; judgment spectrum (mechanical / half-judgment / human); optional rationale fill-in frames the AI never fills in.
- **Golden examples**: `planning/examples/` filled examples for every canonical artifact with README mapping each to its contract/validator; `tests/test_examples.py` guards them; all standalone validators pass on the example directory.
- **Content & training**: whenToUse routing metadata on all 32 skills; zero-license training cold start via archived submissions; clean-round independence (previous-round solutions forbidden in closed clean rounds); related-paper evidence-gap handoff; light `cleaned_from` data lineage; post-contest "candidate lessons" AI-drafts for human confirmation; optional progress tracking on the learning path; advisory network-allowlist preset; optional `Reviewed at` convention for upstream assets.
- **Process tooling**: `work_record check` advisories ledger `DECIDED` records without mirrored decision cards; `sync_plugin --dry-run`; hooks read-guard boundary documented for training isolation.
- **Fix**: `references/upstream/nature-figure/hashes.json` recorded CRLF bytes for three audit scripts while `.gitattributes` mandates LF — aligned the ledger to the LF checkout content (upstream file bytes untouched); `.gitattributes` now covers `*.jsonl`.
- Tests grew to 215; scripts 28 → 32; plugin version 0.8.0.

## 0.7.1 — 2026-09-02

- **README readability rewrite (structure C)**: README.md/README.en.md changed from an 18-section maintenance reference (~370 lines) to a landing page (~130 lines) — "what this is (30s)" → "quick start (4 steps)" → "core concepts (60s)" → documentation map → FAQ essentials. Skills full table, contracts, command reference, directory layout, test coverage, glossary, upstream, and limitations moved to the new `docs/reference.md`; a new `docs/README.md` indexes all manuals by goal (learning-path / training / work-record / post-contest-review / paper-build / dsh-compatibility / modeling-self-review / reference). No external links referenced README anchors, so no breakage; `test_doc_claims` still guards badge counts (32 skills / 171 tests / 28 scripts / version).

## 0.7.0 — 2026-09-02

Full-audit hardening (7-angle parallel audit + empirical reproduction of every P1):

- **Gate engine fixes**: `require_gate` no longer crashes on manifests with `artifacts` (NameError); risk probes with a `FAIL` verdict no longer stall G1 (PASS/CONDITIONAL candidate required instead); `result_report` minimum gate lowered 4→3 (removes the `require result_report` deadlock); `require_gate` runtime path e2e-tested.
- **Validator correctness**: `model_quality_gate` picks the latest run by round number (round10 > round9); `training_scorecard summary --check` ignores `generated_at` (no more permanent out-of-sync) and `round` reads `training_config.json` from the correct root; `lineage.assess({})` rejects zero-provenance lineage; `create_run_snapshot` decodes child output as UTF-8 (GBK Windows), fixes degraded/budget consistency, rejects non-terminal snapshots and out-of-root run dirs, writes LF; `qa_report` propagates `GATE_BLOCKED` via exit code and `validate_repo` now treats it as an error.
- **Encoding**: all 27 scripts force UTF-8 output (GBK console crash / mojibake in validate_repo JSON fixed).
- **Hooks guard**: `guard_frozen.py` now screens DSH lowercase `write`/`edit` tools, matches paths case-insensitively with component boundaries (no false positives on `my_data_raw/` or content mentions), and the DSH patch documents `pluginRoot` (without it `${CLAUDE_PLUGIN_ROOT}` never substitutes and every tool call would be blocked).
- **Docs/claims**: README script count corrected to 28 with an exact-phrase guard in `test_doc_claims`; sync/tree rows now mention `.agents/skills/` and four trees; CLAUDE.md/README tree wording updated; `docs/work-record.md` command examples use space-separated args; AGENTS.md documents `package_signoff`/`submission_authorization`, G1/G4/G6 engine notes, and the manual `frozen_at` freshness rule; NOTICE.md now lists all 12 previously missing upstream files; `lineage.schema.json` drops the unimplemented `INVALIDATED` status.
- **Security**: evidence path containment enforced in `work_record gate`/`decision` and `training_scorecard.resolve_evidence`; `latex_assembly` escapes ledger `choice` text and uniquifies all-symbol macro names.
- **Coverage**: new `tests/test_governance_e2e.py` (11 tests) covers validate_repo/qa exit codes, sync/tree drift detection, manifest overclaim, run-snapshot CLI, the three gate-engine regressions, and evidence escapes.
- Tests grew to 171.

## 0.6.1 — 2026-09-02

- **Doc-claims regression net**: `tests/test_doc_claims.py` asserts README skill/test/script counts and plugin versions match disk, so the past "14/16 scripts" style drift fails CI instead of rotting.
- **Hook guard**: `plugins/mathmodeling-skills/hooks/guard_frozen.py` — a PreToolUse hook (pure stdlib) that blocks writes to `frozen_numbers.json` and `workspace/data_raw/` (exit 2 + reason) while allowing everything else; wired into `hooks.json` (Claude reads it directly; DSH via the optional cordis patch in `docs/dsh-compatibility.md`); 9 tests.
- **Work-record replay**: `work_record.py replay [--date] [--write]` regenerates a session draft from manifests, decision ledgers, run summaries, and frozen numbers (draft is `replay: true`, never appended to by `log`); 2 tests.
- DSH smoke checklist added to `docs/dsh-compatibility.md`; archify 32-skill architecture JSON re-validated (showcase: 0 errors/0 warnings) and interactive HTML regenerated locally (not committed).
- Tests grew to 154.

## 0.6.0 — 2026-09-01

- **Work record tree**: added `records/` — a human-readable, evidence-linked process log (sessions/subjects/gates/decisions/retros) managed by `scripts/work_record.py` (init/log/gate/decision/retro/index/check; pure stdlib; advisory only, never gate-blocking); new `work-logger` skill (32nd) guiding when and what to record; manual `docs/work-record.md`.
- **DeepSeek Harness 0.7.0 adaptation**: full audit `docs/dsh-compatibility.md` (skill discovery via in-repo `.agents/skills/`, AGENTS/CLAUDE injection, sandbox, decision `user_message_id` convention `dsh:<session>:<seq>`, optional hooks patch). Skill tree now has a 4th standalone copy `.agents/skills/` (DSH auto-discovery), synced by `sync_plugin.py` and verified by `validate_skill_trees.py` (4 trees + manifests + marketplace).
- **Governance & docs**: AGENTS.md dual-tree policy → multi-runtime policy + "Runtime Notes (DeepSeek Harness)" section; portable `python scripts/sync_plugin.py .` promoted alongside `sync-plugin.sh`; workflow-orchestrator AGENTS.md reference made location-agnostic; modeler-decision-logger documents the DSH message-id convention; `.gitattributes` added (LF normalization) to stabilize hash-locked 4-tree sync; README bilingual updated (32 skills, 27 scripts, 138 tests, 0.6.0, two new sections); scripts/README updated.
- Tests grew to 138 (work_record: 14).

## 0.5.0 — 2026-09-01

- **Training mode (literacy training loop)**: added `resource-library/` — six showcase categories (papers/ideas/figures/formulas/tables/assets) with per-category READMEs and self-written example templates, plus `scripts/resource_index.py` (scans the library and (re)builds `index.json`; `--check` verifies it). The library is a literacy benchmark, never an answer key: the normal contest flow never reads it.
- **Closed-book training skills ×3**: `training-solver` (solves a training problem without reading `resource-library/`), `training-reflector` (open-book literacy comparison per dimension, citing paths), `training-auditor` (runs mechanical checks, drafts the 6-dimension scorecard, aggregates the summary for human direction). Synced 3-way (`.codex` → `.claude` + plugin distribution).
- **Scorecard tooling**: `scripts/training_scorecard.py` — scaffolds/validates each round's `scorecard.json` (six literacy dimensions with agent self-score + evidence path, null user scores, mechanical-check list) and aggregates rounds into `summary.json` (radar, ranking, mechanical tally).
- **Configuration & docs**: `planning/training_config.json` (mode `closed`, 3 rounds, target skills, closed-phase forbidden paths) and `docs/training.md` (phase A closed-book solve → phase B literacy reflection → phase C multi-dimensional audit + human direction; artifacts under `results/training/roundN/`).
- Tests grew to 124 (resource index, training scorecard).

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
