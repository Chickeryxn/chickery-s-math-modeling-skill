# Mathematical Modeling Contest AI Skill Library

[简体中文](README.md) | [English](README.en.md)

**Let AI help you model — but never decide for you.** AI parses the problem, writes code, runs experiments, assembles evidence, and drafts the paper; you choose the methods, judge the results, set confidence, and explain the physics. This repo turns that division of labor into **6 evidence-driven gates (G1–G6)**, 32 skills, and 32 standard-library-only scripts, so "AI writes code, humans make decisions, everything reproducible and auditable" becomes a machine-checked process.

| Badge | Value |
|---|---|
| Version | [0.10.0](CHANGELOG.md) (plugin manifests in sync) |
| Contents | 32 skills · 32 standard-library-only scripts · Python 3.10+ (zero third-party deps) |
| Platforms | Windows / Linux / macOS |
| CI | [![CI](https://github.com/Chickeryxn/chickery-s-math-modeling-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/Chickeryxn/chickery-s-math-modeling-skill/actions/workflows/ci.yml) Ubuntu/Windows × Py 3.10–3.13, 281 test cases all green |
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

## Quick start

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

<p align="center">
  <a href="https://chickeryxn.github.io/chickery-s-math-modeling-skill/review/02-gates.html"><img src="docs/review/assets/02-gates.png" alt="Per-subquestion gates G1-G6 interactive preview" width="720"/></a><br/>
  <sub>Overview: [00-overview.html](https://chickeryxn.github.io/chickery-s-math-modeling-skill/review/00-overview.html) &middot; Gates diagram: [02-gates.html](https://chickeryxn.github.io/chickery-s-math-modeling-skill/review/02-gates.html)</sub>
</p>

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
- **Figures are typed**: Type 1 is internal debugging only and never enters the paper; Type 2–4 may enter the paper, and any figure that does must pass render verification in `submission` mode.
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

## Training mode: a three-step loop (optional)

Want to train high-quality modeling skills without polluting a real contest? All training output stays isolated in `results/training/`:

1. **Prepare**: drop the problem into `resource-library/assets/problems/` (or change `problem_source` in `planning/training_config.json`); after adding sample materials run `python scripts/resource_index.py .` to rebuild the index;
2. **Run the loop (per round `roundN`)**: `training-solver` solves closed-book (reading `resource-library/` is forbidden) → `training-reflector` compares open-book and records gaps → `training-auditor` runs mechanical checks and drafts the 6-dimension scorecard (mathematical / innovation / figure / expression / evidence / completeness);
3. **You steer**: give a final 1–5 score per dimension, pick the “next direction to approach”, update `training_config.json`, and start the next round; prefer switching problems/data between rounds, and clean rounds must not read the previous round’s solution.

See the [training mode guide](docs/training.md).
## Documentation map

Pick by goal (full index: [docs/](docs/README.md)):

| Goal | Document |
|---|---|
| First time here — understand why the gates exist | [Learning path](docs/learning-path.md) |
| Run this workflow on DSH desktop | [DSH adaptation](docs/dsh-compatibility.md) |
| Train high-quality modeling answers | [Training mode](docs/training.md) |
| Build the paper (xelatex + CUMCMThesis) | [Paper build](docs/paper-build.md) |
| Skills / commands / layout / glossary | [Reference](docs/reference.md) |
| 0.9.0 audit-fix ledger (0.9.1 changes in the [CHANGELOG](CHANGELOG.md)) | [Audit-fix list](docs/audit-fix-0.9.0.md) |
| Log your daily modeling process (`records/` work record tree, advisory) | [Work record tree](docs/work-record.md) |

## 🎨 Interactive visual tour: audit report & full workflow diagrams

This repository ships a full **audit report + an interactive diagram album** under [`docs/review/`](docs/review/): one overview plus six long-form workflow diagrams covering *setup & problem intake → per-subquestion gates G1–G6 → paper assembly & submission → post-contest review → training loop → repository maintenance & distribution*.

<p align="center">
  <a href="https://chickeryxn.github.io/chickery-s-math-modeling-skill/review/00-overview.html" title="Overview (interactive)"><img src="docs/review/assets/00-overview.png" alt="Full workflow overview preview" width="720"/></a>
</p>

| Diagram | Interactive | Static preview |
|---|---|---|
| 00 Overview | [00-overview.html](https://chickeryxn.github.io/chickery-s-math-modeling-skill/review/00-overview.html) | ![Overview](docs/review/assets/00-overview.png) |
| F1 Setup, configuration & intake | [01-launch.html](https://chickeryxn.github.io/chickery-s-math-modeling-skill/review/01-launch.html) | ![F1](docs/review/assets/01-launch.png) |
| F2 Per-subquestion gates G1–G6 | [02-gates.html](https://chickeryxn.github.io/chickery-s-math-modeling-skill/review/02-gates.html) | ![F2](docs/review/assets/02-gates.png) |
| F3 Paper assembly & submission | [03-paper.html](https://chickeryxn.github.io/chickery-s-math-modeling-skill/review/03-paper.html) | ![F3](docs/review/assets/03-paper.png) |
| F4 Training loop | [04-training.html](https://chickeryxn.github.io/chickery-s-math-modeling-skill/review/04-training.html) | ![F4](docs/review/assets/04-training.png) |
| F5 Records · review · learning | [05-records.html](https://chickeryxn.github.io/chickery-s-math-modeling-skill/review/05-records.html) | ![F5](docs/review/assets/05-records.png) |
| F6 Maintenance · sync · distribution | [06-maintenance.html](https://chickeryxn.github.io/chickery-s-math-modeling-skill/review/06-maintenance.html) | ![F6](docs/review/assets/06-maintenance.png) |

> Auto-deployed via GitHub Pages ([`.github/workflows/pages.yml`](.github/workflows/pages.yml)): click an “Interactive” link to open it in the browser. After cloning you can also open `docs/review/index.html` locally. Album guide: [`docs/review/README.md`](docs/review/README.md); full written audit: [`docs/review/00-审阅报告.md`](docs/review/00-审阅报告.md).


## Process log: the work record tree (optional)

Want a reviewable narrative of each contest session? The repo ships the `records/` **work record tree** — session logs `sessions/`, gate transitions `gates/`, mirrored decision cards `decisions/`, retros `retros/`, per-subquestion narratives `subjects/` — maintained by the `work-logger` skill through `scripts/work_record.py`. It is an **advisory narrative layer**: it never gates the workflow, and missing entries never block anything; human decisions are still authoritative in `methods/Qx/qx_decisions.jsonl`.

```bash
python scripts/work_record.py init .                     # create the tree once
python scripts/work_record.py log "finished Q1 experiment" --subject Q1
python scripts/work_record.py gate Q1 G3 --evidence <artifact-path>
python scripts/work_record.py check .                    # validate the tree
```

Commands and logging discipline: [work record tree guide](docs/work-record.md).
## FAQ

- **Can it solve the problem or write the paper for me?** No — and it should not. AI handles the mechanical parts (parsing, code, experiments, drafts); method choice, result verdicts, physical interpretation and submission authorization stay yours and are recorded in `methods/Qx/qx_decisions.jsonl` — exactly the split contest AI rules require.
- **What do I need to install?** Nothing third-party: Python 3.10+ only; `python scripts/run_tests.py` self-checks.
- **Where do I start?** Follow the four Quick-start steps, drop the problem files in, run `python scripts/validate_repo.py .`, and start with the default `learning + lean` (switch to `speed` once fluent and to `submission` before handoff).
- **Will problem sets, attachments or drafts leak into git?** No — `.gitignore` already excludes all contest content; for full isolation use a separate directory or a `git worktree`.
- **How are the Codex / Claude / DSH skill trees maintained?** Edit the canonical `.codex/skills/` tree only, then run `python scripts/sync_plugin.py .` to refresh the `.claude/.agents/plugin-distribution` copies and keep the four trees identical (DSH auto-discovers `.agents/skills/`).
- **Can I hand-edit `frozen_numbers.json`?** No — change a number only via thaw → edit source → rerun → refreeze, logging the reason in `freeze_change_log.md`.
- **What should I watch when touching upstream assets, scripts or the README?** Upstream files are SHA-256 guarded (`validate_upstream_assets.py`); the `hooks` are advisory and platform-dependent (see `docs/dsh-compatibility.md`); make the CI matrix and `python scripts/validate_repo.py .` pass before a release, and keep `docs/review/` plus the `test_doc_claims` guard in sync when you update README counters or the diagram album.
## License and acknowledgements

[MIT License](LICENSE). Built on ideas from [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill), [latexstudio/CUMCMThesis](https://github.com/latexstudio/CUMCMThesis), [Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills), [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills), and [jihe520/sci-box](https://github.com/jihe520/sci-box); diagrams generated by [tt-a1i/archify](https://github.com/tt-a1i/archify). See [references/README.md](references/README.md) and [NOTICE.md](NOTICE.md).
