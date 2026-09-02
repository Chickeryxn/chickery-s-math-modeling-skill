#!/usr/bin/env python3
"""Validate the upstream asset layer under references/upstream/.

Checks, for every subdirectory:
1. a UPSTREAM.md exists;
2. it declares Source repository, License, and Imported files;
3. every imported file actually exists;
4. the declared license starts with an allowed identifier
   (MIT / Apache-2.0 / self-authored);
5. when a `hashes.json` exists next to UPSTREAM.md, every imported file's
   SHA-256 matches the recorded digest (drift guard). Use --write-hashes to
   (re)generate the digests after a deliberate import update;
6. every non-self-authored Source repository appears in NOTICE.md.

Pure standard library; domain-neutral.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

LICENSE_STARTS = ("mit", "apache", "bsd", "self-authored", "self written")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_upstream_md(text: str) -> dict:
    fields = {}
    for line in text.splitlines():
        m = re.match(r"^-\s*\*\*([^*]+)\*\*[^:]*:\s*(.*)$", line.strip())
        if m:
            fields[m.group(1).strip()] = m.group(2).strip()
    # Only collect ``- `file` `` bullets AFTER the "Imported files" field line,
    # so backticked filenames mentioned in other fields (e.g. inside a License
    # description) are not misread as imported files.
    lines = text.splitlines()
    imported = []
    start = next((i for i, ln in enumerate(lines) if re.match(r"^-\s*\*\*Imported files\*\*", ln.strip())), None)
    if start is not None:
        for ln in lines[start:]:
            m = re.match(r"^\s*-\s*`([^`]+)`", ln)
            if m:
                imported.append(m.group(1))
    return {"fields": fields, "imported": imported}


def is_self_authored_source(source_text: str) -> bool:
    low = source_text.lower()
    return "self-authored" in low or "self written" in low


def validate(root: Path, notice_check: bool = True) -> dict:
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
        parsed = parse_upstream_md(um.read_text(encoding="utf-8-sig"))
        fields, imported = parsed["fields"], parsed["imported"]
        missing_fields = [f for f in ("Source repository", "License") if f not in fields or not fields[f].strip()]
        if missing_fields:
            errors.append(f"{rel}: UPSTREAM.md missing fields: {', '.join(missing_fields)}")
        if "Imported files" not in fields:
            errors.append(f"{rel}: UPSTREAM.md missing 'Imported files' field")
        if not imported:
            errors.append(f"{rel}: no imported files declared")
        lic = fields.get("License", "")
        low = lic.lower()
        if not lic:
            errors.append(f"{rel}: license not declared")
        elif not low.startswith(LICENSE_STARTS):
            errors.append(f"{rel}: disallowed license: {lic}")
        if imported:
            for name in imported:
                p = sub / name
                if not p.is_file():
                    errors.append(f"{rel}: imported file missing: {name}")
        # drift guard against hashes.json when present
        hashes_path = sub / "hashes.json"
        if hashes_path.is_file():
            try:
                recorded = json.loads(hashes_path.read_text(encoding="utf-8-sig"))
            except Exception as exc:
                errors.append(f"{rel}: invalid hashes.json: {exc}")
                recorded = {}
            if not isinstance(recorded, dict):
                errors.append(f"{rel}: hashes.json must be a mapping of file -> sha256")
                recorded = {}
            for name in imported:
                p = sub / name
                if not p.is_file():
                    continue
                cur = sha256(p)
                if name not in recorded:
                    errors.append(f"{rel}: imported file {name} missing from hashes.json "
                                  f"— re-run with --write-hashes after a deliberate import update")
                elif recorded.get(name) != cur:
                    errors.append(f"{rel}: hash drift for {name} (recorded {recorded.get(name)[:12]}…, "
                                  f"actual {cur[:12]}…) — re-import or update hashes.json")
            # every recorded digest must map to a declared imported file
            for name in recorded:
                if name not in imported:
                    errors.append(f"{rel}: hashes.json records undeclared file {name} "
                                  f"(not listed under 'Imported files')")
        checked.append({"dir": rel, "files": len(imported),
                        "license": lic, "source": fields.get("Source repository", "")})
    if notice_check:
        errors.extend(check_notice(root, checked))
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "checked": checked}


def check_notice(root: Path, checked: list[dict]) -> list[str]:
    notice = root / "NOTICE.md"
    if not notice.is_file():
        return ["NOTICE.md missing"]
    text = notice.read_text(encoding="utf-8")
    errs = []
    for entry in checked:
        if is_self_authored_source(entry.get("source", "")):
            continue
        src = entry.get("source", "")
        if src and src not in text:
            errs.append(f"NOTICE.md does not mention upstream source: {src}")
    return errs


def write_hashes(root: Path) -> dict:
    base = root / "references" / "upstream"
    out = {}
    for sub in sorted(p for p in base.iterdir() if p.is_dir()):
        um = sub / "UPSTREAM.md"
        if not um.is_file():
            continue
        imported = parse_upstream_md(um.read_text(encoding="utf-8-sig"))["imported"]
        rec = {}
        for name in imported:
            p = sub / name
            if p.is_file():
                rec[name] = sha256(p)
        (sub / "hashes.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n",
                                         encoding="utf-8")
        out[sub.name] = rec
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--write-hashes", action="store_true",
                    help="(re)generate hashes.json for every upstream dir, then validate")
    ap.add_argument("--no-notice-check", action="store_true")
    a = ap.parse_args()
    root = a.root.resolve()
    try:
        if a.write_hashes:
            write_hashes(root)
        r = validate(root, notice_check=not a.no_notice_check)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 0 if r["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
