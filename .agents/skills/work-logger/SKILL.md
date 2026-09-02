---
name: work-logger
description: Maintain the human-readable work-record tree (records/) — append session log entries, gate transitions, and mirrored decision cards after each workflow action, using scripts/work_record.py. Advisory narrative layer; never invents rationale.
---

# Purpose

Keep a detailed, evidence-linked process log under `records/` (one folder, multiple Markdown docs = a work-record tree). The tree is the readable narrative layer over the machine-readable contracts (manifests, ledgers, run summaries, lineage); it is advisory only and never participates in gate judgment.

# When to log

Log after each of these moments (do not log before work exists):

- a gate transition is evidenced (G1..G6 / G2.5): `work_record.py gate Qx <G#> --evidence p1,p2 [--note ...]`;
- a human decision is appended to the ledger: `work_record.py decision Qx <decision_id>` (mirrors the ledger record verbatim; refuses to fabricate);
- a run summary / experiment round completes, a freeze happens, or a paper section is drafted: `work_record.py log "<what was done>" --subject Qx --artifacts <paths> --tags <tags>`;
- a session ends: one `log` entry summarizing the session and its next step;
- a review/retro is due: `work_record.py retro "<title>"`.

At session start, run `work_record.py check` once; if the index is stale, `work_record.py index`.

# Rules

- **Facts only**: record what was done, which artifacts were produced, and which decisions were made. Never write a rationale the human did not say; decision cards mirror the ledger verbatim.
- **Advisory**: never treat the record tree as a gate requirement; never block work because a record is missing.
- **Evidence paths**: use repository-relative paths that exist on disk; the `gate` command rejects missing evidence.
- **No duplicates**: do not copy full artifacts into records/ — link to them.
- Works identically under Codex, Claude, and DeepSeek Harness (`--runtime` is auto-detected from `$env:DSH_SESSION_ID`, Claude env, or defaults to codex).

# Verification

- `python scripts/work_record.py check` passes (index in sync, links resolve, timestamps and gate transitions monotonic).
- Every logged entry has a timestamp and links to artifacts rather than inlining them.
- Decision cards contain only ledger-sourced content.
