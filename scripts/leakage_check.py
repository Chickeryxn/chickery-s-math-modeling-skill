#!/usr/bin/env python3
"""Leakage heuristics for predictive modeling data.

Pure standard library, advisory only. Checks a CSV/TSV file (or the workspace
data profile) for common leakage patterns:
1. declared columns exist (target / optional time column);
2. target column is not duplicated under a different name (heuristic name match);
3. when a time column is given, rows are in ascending time order (a shuffled
   time column means a random split would leak the future);
4. duplicate rows are reported.
5. mixed date/numeric time formats are flagged (ordering is then advisory).

Usage:
  python scripts/leakage_check.py --file workspace/data_clean/train.csv --target y [--time date] [--json]
  python scripts/leakage_check.py --profile workspace/data/data_profile.json --target y [--json]
"""
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def load_rows(path: Path, delimiter: str | None = None):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        try:
            sample = f.read(4096)
            f.seek(0)
            if delimiter is None:
                delimiter = csv.Sniffer().sniff(sample).delimiter
        except Exception:
            delimiter = delimiter or ","
        reader = csv.DictReader(f, delimiter=delimiter)
        headers = reader.fieldnames or []
        rows = list(reader)
    return headers, rows


def _is_date_format(token: str) -> bool:
    from datetime import datetime
    token = token.strip()
    if not token:
        return False
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", "%Y-%m-%d %H:%M:%S"):
        try:
            datetime.strptime(token, fmt)
            return True
        except Exception:
            continue
    return False


def parse_time(token: str):
    """Parse a time token into a uniform epoch-seconds float, or None.

    Both ISO-ish date formats and plain numeric tokens return floats so the
    disorder comparison never mixes datetime and float types (which would
    raise TypeError). Date formats are interpreted as UTC epochs to stay
    timezone-independent for ordering purposes.
    """
    from datetime import datetime, timezone
    token = token.strip()
    if _is_date_format(token):
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", "%Y-%m-%d %H:%M:%S"):
            try:
                dt = datetime.strptime(token, fmt)
                return dt.replace(tzinfo=timezone.utc).timestamp()
            except Exception:
                continue
    try:
        return float(token)
    except Exception:
        return None


def check_file(path: Path, target: str, time_col: str | None = None,
               delimiter: str | None = None) -> dict:
    findings = []
    headers, rows = load_rows(path, delimiter=delimiter)
    if target not in headers:
        findings.append(f"target column {target!r} not found (headers: {', '.join(headers[:8])})")
        return {"status": "FAIL", "findings": findings, "rows": len(rows)}
    # duplicate column names
    from collections import Counter
    dups = [h for h, c in Counter(headers).items() if c > 1]
    if dups:
        findings.append(f"duplicate column names: {dups}")
    # target duplicated under similar name
    target_like = re.sub(r"[^a-z0-9]", "", target.lower())
    for h in headers:
        if h == target:
            continue
        h_like = re.sub(r"[^a-z0-9]", "", h.lower())
        if h_like and (h_like == target_like or h_like in ("y", "label", "target")):
            findings.append(f"possible target duplication: column {h!r} looks like the target")
    # time order
    if time_col:
        if time_col not in headers:
            findings.append(f"time column {time_col!r} not found")
        else:
            prev = None
            disorder = 0
            parsed_kinds = set()
            for r in rows:
                raw = r.get(time_col, "")
                t = parse_time(raw)
                if t is None:
                    continue
                parsed_kinds.add("date" if _is_date_format(raw) else "numeric")
                if prev is not None and t < prev:
                    disorder += 1
                prev = t
            if len(parsed_kinds) > 1:
                findings.append(
                    f"time column {time_col!r} mixes date and numeric formats — "
                    "ordering comparisons are advisory only; normalize the column for a real split check")
            if disorder:
                findings.append(
                    f"time column {time_col!r} is not ascending ({disorder} inversions) — "
                    "a shuffled split would leak the future; use a chronological split")
    # duplicate rows
    seen, dup_rows = set(), 0
    for r in rows:
        key = tuple(r.get(h, "") for h in headers)
        if key in seen:
            dup_rows += 1
        else:
            seen.add(key)
    if dup_rows:
        findings.append(f"{dup_rows} duplicate rows found")
    return {"status": "PASS" if not findings else "FAIL", "findings": findings, "rows": len(rows)}


def check_profile(profile_path: Path, target: str) -> dict:
    findings = []
    try:
        data = json.loads(profile_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "FAIL", "findings": [f"invalid profile: {exc}"], "rows": 0}
    fields = data.get("fields") or []
    names = [f.get("name") or f.get("id") for f in fields if isinstance(f, dict)]
    if target not in names:
        findings.append(f"target {target!r} not in profile fields")
    time_like = [n for n in names if n and re.search(r"time|date|日期|时间", str(n), re.I)]
    if time_like:
        findings.append(f"time-like columns present ({', '.join(time_like)}) — "
                        "confirm chronological split in the cleaning script")
    return {"status": "PASS" if not findings else "FAIL", "findings": findings, "rows": 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=Path, help="CSV/TSV data file to scan")
    ap.add_argument("--profile", type=Path, help="workspace data_profile.json to scan")
    ap.add_argument("--target", required=True)
    ap.add_argument("--time", help="optional time/date column name")
    ap.add_argument("--delimiter", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.file:
        report = check_file(a.file.resolve(), a.target, a.time, a.delimiter)
    elif a.profile:
        report = check_profile(a.profile.resolve(), a.target)
    else:
        print("provide --file or --profile", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"status: {report['status']} (rows: {report['rows']})")
        for f in report["findings"]:
            print(">>", f)
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
