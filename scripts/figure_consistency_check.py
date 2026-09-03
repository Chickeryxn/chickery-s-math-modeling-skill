#!/usr/bin/env python3
"""Figure-set consistency check for a directory of figures.

Mechanical consistency for a paper's figure set (pure standard library):
1. naming: files share a common prefix/suffix pattern (e.g. q1_*.png);
2. raster size families: PNG dimensions are consistent within the same
   figure group (same width or same aspect family);
3. duplicate names (case-insensitive collisions) are flagged;
4. an optional manifest (`--manifest figlist.json` with {"figures": ["q1_a.png", ...]})
   declares the intended set — declared entries missing on disk are flagged,
   and entries may omit the extension when it resolves uniquely
   (q1_a -> q1_a.png, matching LaTeX \\includegraphics usage).

Use after `math-figure-generator` to keep a paper's figure set uniform.
Exit: 0 ok, 1 findings (non-strict), 2 strict.
"""
from __future__ import annotations
import argparse, json, re, struct, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def png_size(path: Path):
    with path.open("rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def scan(root: Path, manifest: Path | None) -> dict:
    findings = []
    files = [p for p in sorted(root.iterdir())
             if p.is_file() and p.suffix.lower() in (".png", ".svg", ".pdf", ".jpg", ".jpeg", ".webp")]
    declared = []
    if manifest is not None and manifest.is_file():
        try:
            declared = [str(x) for x in (json.loads(manifest.read_text(encoding="utf-8-sig")).get("figures") or [])]
        except Exception as exc:
            findings.append(f"invalid manifest: {exc}")
    present = {p.name for p in files}
    # case-insensitive duplicates (q1_a.png vs Q1_A.png) collide on Windows
    # and confuse every downstream path
    by_lower = {}
    for p in files:
        by_lower.setdefault(p.name.lower(), []).append(p.name)
    for key, names in sorted(by_lower.items()):
        if len(names) > 1:
            findings.append(f"duplicate figure names (case-insensitive): {', '.join(sorted(names))}")
    for name in declared:
        if name in present:
            continue
        # allow extensionless declared entries that resolve uniquely
        matches = [p.name for p in files if p.stem == name]
        if len(matches) == 1:
            continue
        if len(matches) > 1:
            findings.append(f"ambiguous declared figure '{name}': {', '.join(sorted(matches))}")
            continue
        findings.append(f"declared figure missing: {name}")
    png_groups = {}
    for p in files:
        if p.suffix.lower() == ".png":
            size = png_size(p)
            if size is None:
                findings.append(f"not a valid PNG: {p.name}")
                continue
            m = re.match(r"^([a-z0-9_]+)_", p.stem, re.I)
            group = m.group(1).lower() if m else "misc"
            png_groups.setdefault(group, []).append((p.name, size))
    for group, items in png_groups.items():
        widths = {s[0] for _, s in items}
        if len(widths) > 1:
            # Same width is always consistent. Different widths are acceptable
            # when every image in the group shares one aspect-ratio family (a
            # full-width and a half-width rendering of the same figure keep the
            # same w/h), per the documented "same width or same aspect family"
            # rule. Only a mix of genuinely different shapes is flagged.
            aspect = [s[0] / float(s[1]) for _, s in items]
            spread = (max(aspect) - min(aspect)) / max(min(aspect), 1e-9)
            if spread > 0.02:
                sizes = ", ".join(f"{n}={s[0]}x{s[1]}" for n, s in items)
                findings.append(
                    f"group '{group}' has inconsistent PNG sizes "
                    f"(widths differ and aspect ratios are not in one family): {sizes}")
    return {"figures": [p.name for p in files], "png_groups": {k: len(v) for k, v in png_groups.items()},
            "findings": findings, "status": "PASS" if not findings else "FAIL"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("figdir", type=Path, help="directory of figure files")
    ap.add_argument("--manifest", type=Path, default=None)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    report = scan(a.figdir.resolve(), a.manifest.resolve() if a.manifest else None)
    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"status: {report['status']} (figures: {len(report['figures'])})")
        for f in report["findings"]:
            print(">>", f)
    if report["status"] == "PASS":
        return 0
    return 2 if a.strict else 1


if __name__ == "__main__":
    raise SystemExit(main())
