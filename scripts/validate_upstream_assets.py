#!/usr/bin/env python3
"""Validate the upstream asset layer under references/upstream/.

Checks, for every subdirectory:
1. a UPSTREAM.md exists;
2. it declares Source repository, License, and Imported files;
3. every imported file actually exists;
4. the declared license belongs to the allowed set
   (MIT / Apache-2.0 / self-authored).

Pure standard library; domain-neutral.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ALLOWED_LICENSES = {"mit", "apache", "apache-2.0", "apache 2.0", "self-authored", "self written"}


def parse_upstream_md(text: str) -> dict:
    fields = {}
    for line in text.splitlines():
        m = re.match(r"^-\s*\*\*([^*]+)\*\*[^:]*:\s*(.*)$", line.strip())
        if m:
            fields[m.group(1).strip()] = m.group(2).strip()
    imported = re.findall(r"^\s*-\s*`([^`]+)`", text, flags=re.MULTILINE)
    return {"fields": fields, "imported": imported}


def validate(root: Path) -> dict:
    base = root / "references" / "upstream"
    errors, checked = [], []
    if not base.is_dir():
        return {"status": "FAIL", "errors": ["references/upstream/ missing"], "checked": []}
    for sub in sorted(p for p in base.iterdir() if p.is_dir()):
        rel = sub.relative_to(root).as_posix()
        um = sub / "UPSTREAM.md"
        if not um.is_file():
            errors.append(f"{rel}: missing UPSTREAM.md")
            continue
        parsed = parse_upstream_md(um.read_text(encoding="utf-8"))
        fields, imported = parsed["fields"], parsed["imported"]
        missing_fields = [f for f in ("Source repository", "License") if f not in fields or not fields[f].strip()]
        if missing_fields:
            errors.append(f"{rel}: UPSTREAM.md missing fields: {', '.join(missing_fields)}")
        if "Imported files" not in fields:
            errors.append(f"{rel}: UPSTREAM.md missing 'Imported files' field")
        if not imported:
            errors.append(f"{rel}: no imported files declared")
        lic = fields.get("License", "").lower()
        if lic and not any(a in lic for a in ALLOWED_LICENSES):
            errors.append(f"{rel}: disallowed license: {fields.get('License')}")
        elif not lic:
            errors.append(f"{rel}: license not declared")
        if imported:
            for name in imported:
                p = sub / name
                if not p.is_file():
                    errors.append(f"{rel}: imported file missing: {name}")
        checked.append({"dir": rel, "files": len(imported), "license": fields.get("License", "")})
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "checked": checked}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    a = ap.parse_args()
    try:
        r = validate(a.root.resolve())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 0 if r["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
