# Mathematical Modeling Contest AI Skill Library

[简体中文](README.md) | [English](README.en.md)

**Math Modeling Skill** — an Agent skill library and executable workflow framework for mathematical-modeling contests (CUMCM / MCM/ICM): 32 Claude/Codex/DSH skills plus 28 standard-library-only validation scripts turn "AI writes code, humans make decisions, everything reproducible and auditable" into a machine-enforced process contract.

| Badge | Value |
|---|---|
| License | [MIT](LICENSE) |
| Version | 0.7.1 (plugin manifests in sync) |
| Runtime | Python 3.10+ (standard library only, no third-party dependencies) |
| Platforms | Windows / Linux / macOS |
| Tests | 171 cases, `python scripts/run_tests.py` all green |

## What this is (30 seconds)

Mathematical-modeling contests now allow AI assistance, but letting an Agent "free-wheel" creates two risks: **the AI makes modeling judgments for you** (choosing methods, writing rationales, drawing conclusions), and **results are untrustworthy** (code that never ran, numbers without provenance, versions nobody can verify).

This project splits a contest into **six gate stages (G1–G6)**; passing each gate requires verifiable evidence artifacts on disk, checked automatically by the validators under `scripts/` — gates are driven by evidence and can never be self-declared. 32 single-purpose skills cover every step from reading the problem to delivering the paper.

| Principle | Meaning |
|---|---|
| **AI owns mechanical correctness** | Parsing, coding, running experiments, assembling evidence, and drafting sections are AI tasks |
| **Humans own modeling judgment** | Method choice, result verdicts, confidence, physical meaning, and contribution framing are human decisions, always recorded |
| **Evidence drives everything** | Gates, freezes, and paper numbers must trace back to real on-disk artifacts and hashes, never to verbal claims |

## Quick start (4 steps)

```bash
git clone https://github.com/Chickeryxn/chickery-s-math-modeling-skill.git
cd chickery-s-math-modeling-skill
git checkout mathmodeling-new-skeleton
```

1. Open the repository root with **Codex, Claude, or DeepSeek Harness (DSH) desktop**.
2. Put the problem and attachments into `workspace/problem.txt` and `workspace/data_raw/<attachments>` (raw attachments are read-only; cleaned copies go to `workspace/data_clean/`).
3. Ask the agent to self-check: `python scripts/validate_repo.py .`.
4. Start the workflow: `problem-parser → problem-classifier → data-auditor-cleaner → workflow-orchestrator` (the agent advances gate by gate and asks you at modeling-judgment points).

Session configuration lives in `planning/session_config.json`: `interaction_mode` (`learning`/`speed`) controls question density, `rigor_profile` (`lean`/`submission`) controls artifact and audit density; new workspaces default to `learning + lean`, switch to `submission` before handoff.

## Core concepts (60 seconds)

![Generic gate pipeline](docs/diagrams/archify/assets/mm-generic-workflow.png)

**Gates**: each subquestion (Q1, Q2, …) advances independently through the same gates — G1 problem framing → G2 method screening → G2.5 human method choice → G3 code & experiment review → G4 results judged & frozen → G5 paper sections → G6 final audit. The current gate is derived from disk evidence by `scripts/workflow_guard.py derive Qx`; the **manifest is only a cache and can never promote a gate**.

**Key rules**

- Model code may only be generated when G2 and G2.5 both pass.
- Human method/result/stability/claim-scope decisions must be appended to the JSONL decision ledger; the AI never writes rationales for the human.
- Every number in the paper must come from `results/Qx/reports/frozen_numbers.json`; changing one requires thaw → modify canonical source → rerun → refreeze, logged in `freeze_change_log.md`; never hand-edit.
- Figures are typed: Type 1 diagnostics never enter the paper; only Type 3/4 may, after passing render checks.

**Skill groups** (32 total; [full table in the reference](docs/reference.md))

| Group | Covers |
|---|---|
| Problem understanding | parsing, classification, paper analysis, data cleaning |
| Method & decisions | method screening, choice cards, decision ledger, assumptions & symbols |
| Code & experiments | code generation/review (Python, MATLAB/Beita Tianyuan), robustness |
| Results & paper | result reports, figures, method explanations, freeze, writing/polishing/citations |
| Orchestration & auditing | gate routing, completeness/consistency/QA audits, work records |
| Training mode | closed-book solving, literacy reflection, multi-dimensional audit |

## Documentation map

Pick by goal (full index: [docs/](docs/README.md)):

| Goal | Document |
|---|---|
| Understand why each gate exists, with exercises | [Learning path](docs/learning-path.md) |
| Train high-quality modeling answers (closed → reflect → audit) | [Training mode](docs/training.md) |
| Keep a detailed work-process log (`records/` tree) | [Work record tree](docs/work-record.md) |
| Use DSH desktop (skill discovery / sandbox / smoke checklist) | [DSH adaptation](docs/dsh-compatibility.md) |
| Build the paper (xelatex + CUMCMThesis) | [Paper build](docs/paper-build.md) |
| Skills / contracts / commands / layout / glossary / upstream | [Reference](docs/reference.md) |

## FAQ

**Q: Can it solve problems or write the paper for me?**
No. AI handles mechanical correctness only; method choice, result verdicts, physical interpretation, and contribution framing are yours to decide and record — which is also what the organizers' AI rules require.

**Q: What dependencies do I need?**
Zero third-party dependencies. All scripts use only the Python standard library (3.10+); `python scripts/run_tests.py` self-checks.

**Q: Does it work with Codex, Claude, and DSH?**
Yes. The three standalone trees (`.codex/`, `.claude/`, `.agents/`) are identical; edit `.codex/skills/` first, then run `python scripts/sync_plugin.py .` and verify with `validate_skill_trees.py`.

**Q: Can I hand-edit `frozen_numbers.json`?**
No. To change a frozen value: thaw → modify the canonical source → rerun the affected experiments → refreeze, and record the reason in `freeze_change_log.md`.

**Q: How do I extend or modify a skill?**
Edit `.codex/skills/<skill>/SKILL.md`, run `python scripts/sync_plugin.py .` to sync all copies, then verify with `validate_skill_trees.py`.

**Q: What is the relationship to XiaoMaColtAI and other upstream libraries?**
This project merged 6 upstream projects and locked 12 decisions (history in [references/README.md](references/README.md)); the current executable contract is `AGENTS.md`, `schemas/`, and `scripts/`.

## License and acknowledgements

[MIT License](LICENSE). Built on ideas from [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill), [latexstudio/CUMCMThesis](https://github.com/latexstudio/CUMCMThesis), [Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills), [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills), and [jihe520/sci-box](https://github.com/jihe520/sci-box); diagrams generated by [tt-a1i/archify](https://github.com/tt-a1i/archify). See [references/README.md](references/README.md) and [NOTICE.md](NOTICE.md).
