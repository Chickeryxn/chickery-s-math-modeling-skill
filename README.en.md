# Mathematical Modeling Contest AI Skill Library

[简体中文](README.md) | [English](README.en.md)

**Let AI help you model — but never decide for you.** AI parses the problem, writes code, runs experiments, assembles evidence, and drafts the paper; you choose the methods, judge the results, set confidence, and explain the physics. This repo turns that division of labor into **6 evidence-driven gates (G1–G6)**, 32 skills, and 32 standard-library-only scripts, so "AI writes code, humans make decisions, everything reproducible and auditable" becomes a machine-checked process.

| Badge | Value |
|---|---|
| Version | [0.9.0](CHANGELOG.md) (plugin manifests in sync) |
| Contents | 32 skills · 32 standard-library-only scripts · Python 3.10+ (zero third-party deps) |
| Platforms | Windows / Linux / macOS |
| CI | [![CI](https://github.com/Chickeryxn/chickery-s-math-modeling-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/Chickeryxn/chickery-s-math-modeling-skill/actions/workflows/ci.yml) Ubuntu/Windows × Py 3.10–3.12, 247 test cases all green |
| License | [MIT](LICENSE) |

## What problem it solves

Modeling contests now allow AI assistance, but letting an Agent "free-wheel" usually fails in two ways:

| Risk | What it looks like | Consequence |
|---|---|---|
| **AI makes judgment calls for you** | Picks your methods, writes rationales, draws conclusions | Nobody stops a wrong direction; the paper cannot survive review |
| **Results cannot be trusted** | Code that never ran, numbers without provenance, unverifiable versions | "I computed it" cannot be proven and collapses under questioning |

**This repo's answer:** split a contest into 6 checkable gates. Each gate requires evidence files on disk, verified automatically by validators under `scripts/` — **a gate can only be opened by evidence; the Agent saying "done" counts for nothing.**

## Who does what

| Who | Does | How it is enforced |
|---|---|---|
| **AI** | Parses, codes, runs experiments, assembles evidence, drafts sections | Mechanical work, AI handles all of it |
| **You** | Chooses methods, judges results, sets confidence, explains physics and contribution | Every decision is appended to `methods/Qx/qx_decisions.jsonl` with your verbatim answer; the AI never writes rationales for you |
| **Evidence** | Final arbiter of gates, freezes, and paper numbers | Everything traces to real on-disk artifacts and hashes; verbal claims are void |

This is exactly the division of labor contest AI rules require: AI is the tool; the modeling judgment and responsibility stay with the contestants.

## Quick start (~5 minutes)

```bash
git clone https://github.com/Chickeryxn/chickery-s-math-modeling-skill.git
cd chickery-s-math-modeling-skill
```

You are already on the development branch `mathmodeling-new-skeleton` (the repo default); no checkout needed.

1. Open the repository root with **Codex, Claude, or DeepSeek Harness (DSH) desktop**.
2. Put the problem into `workspace/problem.txt` and attachments into `workspace/data_raw/` (raw files are read-only; cleaned copies are written to `workspace/data_clean/` by the workflow).
3. Self-check the environment: `python scripts/validate_repo.py .`
4. Have the Agent start in order: `problem-parser → problem-classifier → data-auditor-cleaner → workflow-orchestrator`. It advances gate by gate and stops to ask you at every point where you must decide.

Two configuration switches (`planning/session_config.json`):

| Switch | Values | Effect | When |
|---|---|---|---|
| `interaction_mode` | `learning` / `speed` | Question density and when AI suggestions appear | Use `learning` as a beginner; switch to `speed` once fluent |
| `rigor_profile` | `lean` / `submission` | Artifact and audit density (never changes who decides) | Use `lean` while exploring; switch to `submission` before handoff |

## How the 6 gates work

![Generic gate pipeline](docs/diagrams/archify/assets/mm-generic-workflow.png)

Each subquestion (Q1, Q2, …) advances independently through the same gates. "Who opens" means who holds the decision at that stage:

| Gate | What happens | Who opens |
|---|---|---|
| **G1 Problem framed** | Problem parsed, data inventoried, goals and success criteria set | You confirm the key framing first |
| **G2 Method screened** | Candidate method card + risk probe produced (no coding yet) | AI drafts; probe evidence speaks |
| **G2.5 Method chosen by human** | Only after YOU pick the method may code be generated | **You** |
| **G3 Code & experiments reviewed** | Code runs, input/output contracts hold, results reproducible | AI self-review + machine checks |
| **G4 Results judged & frozen** | You judge results/stability/claim scope; numbers freeze into `frozen_numbers.json` | **You** |
| **G5 Paper section ready** | Writing uses frozen numbers only; figures pass render checks | AI drafts; you confirm the physics |
| **G6 Final audit passed** | Cross-media consistency / completeness / QA audits | Machine reports; you sign off |

**Hard rules:**

- **Changing a number requires a process**: every number in the paper comes from `results/Qx/reports/frozen_numbers.json`; to change one: thaw → edit the canonical source → rerun → refreeze, and record the reason in `freeze_change_log.md`; never hand-edit.
- **Figures are typed**: Type 1 is internal debugging only and never enters the paper; only Type 3/4 may, after passing render verification.
- **G5/G6 run only in `submission` mode**; in `lean` mode the workflow stops at the G4 judgment.

## The 32 skills at a glance

Grouped by function (full table in the [reference](docs/reference.md)):

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
| First time here — understand why the gates exist | [Learning path](docs/learning-path.md) |
| Run this workflow on DSH desktop | [DSH adaptation](docs/dsh-compatibility.md) |
| Train high-quality modeling answers | [Training mode](docs/training.md) |
| Build the paper (xelatex + CUMCMThesis) | [Paper build](docs/paper-build.md) |
| Skills / commands / layout / glossary | [Reference](docs/reference.md) |
| 0.9.0 audit-fix ledger (issue → resolution) | [Audit-fix list](docs/audit-fix-0.9.0.md) |

## FAQ

**Q: Can it solve problems or write the paper for me?**
No — and it should not. AI handles mechanical correctness only; method choice, result verdicts, physics, and contributions are yours to decide and record, which is exactly the division contest AI rules require.

**Q: What do I need to install?**
Zero third-party dependencies. All scripts use only the Python standard library (3.10+); `python scripts/run_tests.py` self-checks.

**Q: Does it work with Codex, Claude, and DSH?**
Yes. The three skill trees `.codex/skills/`, `.claude/skills/`, `.agents/skills/` are each complete and identical; edit `.codex/skills/` first, then run `python scripts/sync_plugin.py .` and validate.

**Q: Can I hand-edit `frozen_numbers.json`?**
No. Changing a frozen value requires thaw → edit source → rerun → refreeze, with the reason recorded in `freeze_change_log.md`.

**Q: Where do I start on my first run?**
Follow the [learning path](docs/learning-path.md); or run one contest problem end-to-end with the default `learning + lean` config and watch where the workflow stops to ask you.

**Q: What is the relationship to XiaoMaColtAI and other upstream libraries?**
This project merged 6 upstream projects and locked 12 decisions (history in [references/README.md](references/README.md)); the current executable contract is `AGENTS.md`, `schemas/`, and `scripts/`.

## License and acknowledgements

[MIT License](LICENSE). Built on ideas from [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill), [latexstudio/CUMCMThesis](https://github.com/latexstudio/CUMCMThesis), [Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills), [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills), and [jihe520/sci-box](https://github.com/jihe520/sci-box); diagrams generated by [tt-a1i/archify](https://github.com/tt-a1i/archify). See [references/README.md](references/README.md) and [NOTICE.md](NOTICE.md).
