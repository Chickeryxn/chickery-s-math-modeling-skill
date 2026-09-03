# Workflow integrity scripts

These scripts are standard-library-only and domain-neutral. They enforce or audit the project contracts; they do not choose a mathematical model.

## Shared helpers (`scripts/lib/common.py`)

Import-safe stdlib helpers for new and migrated scripts: `utf8_streams()`
(reconfigure stdout/stderr to UTF-8 — call from `main()`, never at import
time), `sha256_file()`, `safe_path(root, raw)` (containment guard),
`load_json()`, `frozen_claims(data)` (normalizes both `frozen_numbers` shapes),
and the `FROZEN_GLOB` constant. Existing scripts still carry their own local
copies; when you touch one, migrate its copy to `common` in the same change so
the duplication shrinks over time.

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
python scripts/work_record.py init .
python scripts/work_record.py log "parse done" . --subject Q1 --artifacts planning/parse/problem_parse.json
python scripts/work_record.py gate Q1 G2 . --evidence methods/Q1/probes/risk_probe_summary.json
python scripts/work_record.py decision Q1 q1_method_choice .
python scripts/work_record.py check .
```

## Contracts

- `workflow_guard.py`: monotonic gates and sensitive artifact eligibility. `derive Qx` returns the gate at which the evidence is currently stuck (G1..G(n-1) satisfied, Gn not yet evidenced); `require Qx <kind>` allows producing an artifact only when that value is at least the kind's minimum gate. Note the intended semantics: `require` checks the evidence-derived gate level, not the blocker list — a kind whose own artifact is missing (e.g. `paper_section` before the section exists) is expected to be produced while that artifact is still absent; the blockers list is authoritative for humans and `qa_report`, while `require` guards the gate level and the special preconditions (package sign-off for `frozen_numbers`). A manifest cannot promote the derived gate.
- `validate_decisions.py`: verifiable user-source requirement for `DECIDED`. A `DECIDED` record must contain a nested `source` with `source_type=user_answer`, `user_message_id`, and `user_verbatim_answer`, and use `recorded_at` as the timestamp. To cite external/user evidence as `evidence:<id>`, create `planning/evidence_registry.json` first (see `planning/evidence_registry.example.json`).
- `create_run_snapshot.py`: unified `run` execution plus begin/finalize/validate snapshot lifecycle; successful runs must be executed by the runner. `run` executes the `--command` string **without a platform shell**: the command is split into an argv (POSIX quoting on Unix, cmd-style double-quote grouping on Windows) and executed directly, so quoting behavior is deterministic across platforms and shell metacharacters cannot inject (`|`, `>`, `&&`, `%VAR%` are literal arguments — wrap explicit `cmd /c ...`/`sh -c ...` if a shell feature is genuinely needed). A byte-identical deterministic rerun is a valid reproduction (advisory `outputs_unchanged` flag), not an error; missing outputs after an exit-0 process and interrupted runs always leave a terminal snapshot, never a `RUNNING` one.
- `lineage.py`: hash-addressed source lineage and stale assessment.
- `validate_independence.py`: main/baseline/verifier separation checks.
- `validate_model_contract.py`: problem-specific contract shape check.
- `qa_report.py`: layered status summary; it never upgrades a blocked gate.
- `check_frozen_freshness.py`: per-claim freshness of `frozen_numbers.json` (source exists, not newer than `frozen_at`); exit 2 on any stale claim. Freshness is mtime-based: a git checkout, unpack, or copy that resets mtimes can produce a false STALE verdict — treat STALE as "verify and re-freeze", not as proof of tampering. Naive `frozen_at` values (no `Z`/`±hh:mm`) **fail closed as STALE** — a local-time value read as UTC could hide a stale claim; re-freeze with an explicit offset. Wired into `validate_repo.py` (runs when a `frozen_numbers.json` exists).
- `figure_render_audit.py`: every figure referenced by a paper section must exist under `paper/figures/` and carry a sibling `<name>.render.json` (`status: PASS`, `rendered_at`).
- `preflight.py`: one-command submission bundle (claim_coverage / abstract_checker / ai_trace_checker / latex_assembly --check-only --strict / figure_consistency_check / section_structure_check); steps run only when their inputs exist.
- `polish_stats.py`: quantified writing metrics (long-sentence ratio, filler phrases, AI connectors) as an advisory pre-scan for paper-polisher; `--strict` exits 2 on long-sentence ratio > 0.25 or filler total > 8.
- `sync_plugin.py`: portable skill-tree synchronization and hash check.
- Run snapshots additionally record an optional `vcs` block (git HEAD + dirty list) when the workspace is a git repository.
- `resource_index.py`: scans `resource-library/` and (re)builds `index.json`; `--check` verifies the index matches disk.
- `training_scorecard.py`: literacy training scorecard contract. `round <dir>` scaffolds/validates one round's `scorecard.json` (six dimensions, agent self-scores with evidence paths, null user scores, mechanical-check list); `summary <dir>` aggregates rounds into `summary.json` (radar, ranking, mechanical tally); `--check` modes validate without writing.
- `work_record.py`: work-record tree (see `docs/work-record.md`). `init` scaffolds `records/`; `log` appends a timestamped session entry; `gate` records a monotonic gate transition with existing evidence; `decision` mirrors a ledger record into a decision card (refuses to fabricate); `retro` scaffolds a review; `replay` regenerates a session draft from manifests/ledgers/run summaries/frozen numbers (`--write` stores it); `index` rebuilds `records/README.md`; `check` validates index sync, links, timestamps, and gate monotonicity. `--runtime` auto-detects codex/claude/dsh.

## Run lifecycle

Use `run` for normal experiments so the tool captures command output and return code:

```powershell
python scripts/create_run_snapshot.py run . runs/run1 --command "python code/main.py" --result-ref results/result.json --validation-ref results/validation.json --planned-budget "{\"iterations\":100}"
python scripts/validate_run_snapshot.py . runs/run1
```

Use `begin`/`finalize` only for integrations that can provide equivalent runner evidence. Direct finalization with `executed_by_runner=false` cannot claim `SUCCESS`.
