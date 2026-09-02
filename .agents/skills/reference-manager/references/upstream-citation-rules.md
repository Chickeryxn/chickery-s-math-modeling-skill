# Upstream citation rules (self-written, offline)

Self-written distillation of citation-verification ideas from [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) `nature-citation` / `nature-ref-verifier` (Apache-2.0). The upstream network-backed executables are NOT imported; only these offline rules are used. Live verification (Crossref/PubMed) is an optional external capability, never a core requirement.

## Support grading

Assign every citation a support grade:

- `strong` — the cited source directly establishes the claim (method origin, theorem, standard result).
- `partial` — the source supports a component or provides context.
- `background` — general context; keep only when it earns its place.
- `metadata-only` — flagged for removal (no real support).

## Field-completeness gate (BibTeX)

Every entry must have: author (non-placeholder), title, year. Additionally for articles: journal, volume, number or pages, DOI when available. Flag: placeholder authors ("Someone"), obviously fake DOIs, generic AI-looking titles.

## Difference-pattern vocabulary (for the audit report)

- 🔴 blocking: unverifiable source, conflicting metadata for the same key, citation contradicts the claim.
- 🟡 warning: DOI unresolved (offline check: malformed or missing), volume/page missing.
- 🟢 ok: traceable source file / registry entry / user confirmation.

## Offline-first rule

Run the mechanical checks (fields, format, duplicates, placeholder detection) offline. Network verification is optional and must be declared in the audit report when used.
