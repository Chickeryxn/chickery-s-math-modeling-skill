---
name: training-reflector
description: Open-book literacy reflection. After training-solver produced a closed-book solution, compare it against the resource-library showcase (papers/ideas/figures/formulas/tables) dimension by dimension and write a literacy learning report. Used in docs/training.md phase B.
whenToUse: In the literacy-training loop phase B: compare the closed-book solution with the showcase library dimension by dimension.
---

# Purpose

Turn the showcase library into **transferable literacy**, not answers. Compare the closed-book solution with exemplary materials and write down gaps + transferable points, in your own words.

# Preconditions

- A completed round solution at `results/training/roundN/solution/`.
- `planning/training_config.json` lists `resource_categories` and `target_skills`.

# Workflow

1. Read the round solution (do NOT modify it).
2. Read `resource-library/index.json` and the categories named in `resource_categories`.
3. For each `target_skill` dimension, compare the solution with the showcase entries of the relevant category:
   - `mathematical`: model abstraction, formula rigor, numeric robustness vs `formulas/` + `papers/`;
   - `innovation`: multi-paradigm thinking, simplification ladder vs `ideas/`;
   - `figure`: palette/layout/annotation/claim-alignment vs `figures/` + `publication-gallery.md`;
   - `expression`: structure/logic/language vs `papers/` + `paper-skeleton.md`;
   - `evidence`: traceability, uncertainty, baseline fairness vs `tables/` + showcase papers;
   - `completeness`: coverage, defensible conclusions, honest limitations.
4. Write `results/training/roundN/reflection.md`:
   - per dimension: solution snapshot → showcase anchor (path) → gap → transferable point (1–3 lines each);
   - a "top-3 to improve next round" section.
5. Do not copy showcase text into the report; paraphrase and cite paths.

# Rules

- This phase is open-book by design; closed phase already ended.
- Cite evidence paths, do not paste large excerpts.
- Be specific: "palette uses 8 hues" beats "colors could be better".

# Verification

- `reflection.md` exists with one section per target skill and cited paths.
- Top-3 improvements are actionable.
- No showcase content was pasted verbatim.
