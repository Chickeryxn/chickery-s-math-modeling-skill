# Upstream: nature-skills (figure rules)

- **Source repository**: https://github.com/Yuan1z0825/nature-skills
- **Fixed commit**: `ebd722e18808442688bd205917a3e774195c258f` (shallow clone HEAD, reviewed 2026-09)
- **License**: Apache-2.0 (root LICENSE). Files below are imported verbatim from the upstream repo; Apache-2.0 requires retaining this notice and the license text (see `LICENSES/Apache-2.0.txt` and `NOTICE.md`).
- **Imported files** (from `skills/nature-figure/references/`):
  - `figure-contract.md` — conclusion-first figure contract (claim → visual → evidence).
  - `qa-contract.md` — publication QA delivery list; 5pt glyph minimum, render gates.
  - `design-theory.md` — typography / color / export rules for publication figures.
  - `api.md` — PALETTE constants and matplotlib style API used by upstream.
  - `multipanel-evidence-architecture.md` — multi-panel evidence architecture guidance.
- **Scope**: Only the Markdown rule layer is imported. Upstream Python/R renderers, the OpenRouter GPT-Image path, and the `figures4papers` assets (which carry **no license** upstream) are intentionally NOT imported.
- **Drift note**: Upstream rules carry date stamps and reference Nature-specific numeric rules (e.g. <250-word captions, 89/183 mm). Treat as advisory guidance, not official journal requirements.
