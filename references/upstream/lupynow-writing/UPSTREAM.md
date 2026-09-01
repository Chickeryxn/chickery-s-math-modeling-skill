# Upstream: Lupynow/math-modeling-skills (writing quality control)

- **Source repository**: https://github.com/Lupynow/math-modeling-skills
- **Fixed commit**: `3a9428c006cc1b977c6a72a531b739a62868a4bc` (shallow clone HEAD, reviewed 2026-09)
- **License**: MIT (root LICENSE, © 2026 Lupynow). Imported verbatim; retain the copyright notice (see `LICENSES/MIT.txt` and `NOTICE.md`). Note: the per-skill `LICENSE` copies inside the upstream repo carry "Copyright (c) 2026" without a holder; confirm with upstream before commercial redistribution.
- **Imported files** (from the upstream repo):
  - `de-ai-writing.md` — from `skills/math-modeling-paper/references/`; quantifiable AI-trace rules (frequency caps, banned phrases, result-description rules).
  - `self-review-framework.md` — from `skills/math-modeling-paper/references/`; four-round self review + Claim-Evidence map.
  - `common-phrases.md` — from `skills/math-modeling-paper/references/`; bilingual phrase bank with anti-templating variants.
  - `figure-and-code-guide.md` — from `skills/math-modeling-paper/references/`; Figure Contract + matplotlib rcParams. **Trimmed for this repository**: draw.io/Visio/MATLAB-drawing/R-ggplot2/seaborn tool recommendations replaced with matplotlib-only guidance; the C++ language section removed (Python/MATLAB only).
  - `model-selection-matrix.md` — from `skills/math-modeling-solver/references/`; decision matrix + anti-homogenization conflict-resolution rules.
- **Scope**: Markdown rule layer only. The upstream code templates (29 files) depend on third-party packages and carry no tests; they are NOT imported (see `references/upstream/method-index/` for the clean-room method index instead).
- **Drift note**: Content references contest-year facts and third-party tools; treat as advisory.
