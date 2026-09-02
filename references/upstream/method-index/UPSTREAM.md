# Method index (clean-room)

> Reviewed at: 2026-09-02 (repository maintenance pass)
- **Source repository**: self-authored (inspired by XiaoMaColtAI/math-modeling-skill and Lupynow cookbooks; no upstream files copied)
- **Nature**: Original content written for this repository. It summarizes method families and engineering practices **inspired by** upstream projects that carry no license or proprietary licenses, so their original files are NOT copied here:
  - XiaoMaColtAI/math-modeling-skill (root has no LICENSE; `tools/docx|pdf|xlsx` are Anthropic proprietary) — algorithm-library structure and the "M1/P1/P2/W1/W2" gate timing, re-expressed as mapping tables against this repository's G1–G6 gates.
  - Lupynow cookbooks/playbooks and code templates (MIT but third-party-dependent, zero tests) — only the method-family taxonomy and the "problem-adaptation" template philosophy are reflected.
- **License**: MIT (this repository's license).
- **Imported files**:
  - `method-index.md` — method family index (evaluation/prediction/optimization/classification/clustering/mechanism/simulation/graph), one row per family with applicability, typical approaches, and risks; links to upstream repos for details.
  - `xiaomacoltai-methodology.md` — gate mapping (M1/P1/P2/W1/W2 → G1–G6), numerical-solution robustness checklist (9 items), reproducibility-manifest schema, and the three-role orchestration idea (modeler/programmer/writer), all rewritten in this repository's own words.
- **Drift note**: Upstream repos evolve; treat linked upstream repos as the authoritative source for algorithm details.
