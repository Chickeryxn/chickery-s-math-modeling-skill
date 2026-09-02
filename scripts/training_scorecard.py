#!/usr/bin/env python3
"""Training literacy scorecard: scaffold, validate, and aggregate (pure stdlib).

The training loop (docs/training.md) produces one scorecard per round:
results/training/roundN/scorecard.json. This script owns the scorecard
contract — six literacy dimensions, agent self-scores with evidence paths,
user final scores (null until the human decides), and the mechanical-check
attachment list.

Commands:
  python scripts/training_scorecard.py round <round_dir> [--json] [--check]
      Scaffold a template scorecard if missing, validate it, and print a
      compact status (or the full JSON with --json). --check only validates.
  python scripts/training_scorecard.py summary <results_dir> [--json] [--check]
      Aggregate all round scorecards into summary.json (radar per dimension,
      ranking by total, mechanical-check tally). --check verifies summary.json
      matches the rounds on disk.

Exit codes: 0 PASS, 2 FAIL.
"""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path


def _utf8_streams() -> None:
    """Force UTF-8 on std streams when run as a CLI (import-time safe).

    Never call this at import time: tests import this module, and changing
    the test process's stream encoding would break GBK-decodable output
    captured by scripts/validate_repo.py.
    """
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCORECARD = "scorecard.json"
SUMMARY = "summary.json"
SCHEMA_VERSION = 1

# Dimension id -> one-line description (kept in sync with docs/training.md §3).
DIMENSIONS = {
    "mathematical": "model abstraction, formula rigor, numeric robustness",
    "innovation": "multi-paradigm thinking, simplification ladder",
    "figure": "palette/layout/annotation/claim alignment",
    "expression": "structure, logic, language quality",
    "evidence": "traceability, uncertainty, baseline fairness",
    "completeness": "coverage, defensible conclusions, honest limitations",
}
SCORE_RANGE = (1, 5)
CHECK_STATUSES = {"PASS", "FAIL", "SKIP", "N/A"}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def blank_dimension() -> dict:
    return {
        "description": None,
        "agent_score": None,
        "agent_evidence": None,
        "user_score": None,
        "user_comment": None,
        "sample_comparison": None,
    }


def template(round_no: int, mode: str) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "round": round_no,
        "mode": mode,
        "dimensions": {d: blank_dimension() for d in DIMENSIONS},
        "mechanical_checks": [],
        "direction": None,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }


def round_number(round_dir: Path) -> int:
    import re
    m = re.search(r"round(\d+)", round_dir.name)
    return int(m.group(1)) if m else 0


def load_round_config(root: Path) -> dict:
    """Best-effort read of planning/training_config.json (empty dict on failure)."""
    p = root / "planning" / "training_config.json"
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            return {}
    return {}


def resolve_evidence(round_dir: Path, path: str):
    """Resolve an evidence path relative to the round dir or any ancestor.

    Returns the first existing candidate inside the project, or None. Absolute
    paths and paths escaping the project root are rejected (no existence
    oracle on arbitrary files, no absolute paths leaked into committed
    scorecards).
    """
    if not path:
        return None
    candidate = Path(path)
    if candidate.is_absolute():
        return None
    for base in (round_dir, round_dir.parent, round_dir.parent.parent):
        hit = (base / candidate).resolve()
        try:
            hit.relative_to(round_dir.parent.parent.parent.resolve())
        except ValueError:
            continue
        if hit.exists():
            return hit
    return None


def validate_scorecard(round_dir: Path, data: dict, errors: list, warnings: list) -> bool:
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version: expected {SCHEMA_VERSION}, got {data.get('schema_version')}")
    dims = data.get("dimensions")
    if not isinstance(dims, dict):
        errors.append("dimensions: missing or not an object")
        return False
    missing = [d for d in DIMENSIONS if d not in dims]
    if missing:
        errors.append(f"dimensions: missing {sorted(missing)}")
    extra = [d for d in dims if d not in DIMENSIONS]
    if extra:
        errors.append(f"dimensions: unknown {sorted(extra)}")
    for dim, spec in dims.items():
        if not isinstance(spec, dict):
            errors.append(f"{dim}: not an object")
            continue
        for key in ("agent_score", "user_score"):
            val = spec.get(key)
            if val is not None and not (isinstance(val, int) and not isinstance(val, bool)
                                        and SCORE_RANGE[0] <= val <= SCORE_RANGE[1]):
                errors.append(f"{dim}.{key}: score must be int {SCORE_RANGE} or null, got {val!r}")
        if spec.get("agent_score") is not None and not spec.get("agent_evidence"):
            errors.append(f"{dim}: agent score set but agent_evidence missing")
        if spec.get("agent_evidence"):
            hit = resolve_evidence(round_dir, spec["agent_evidence"])
            if hit is None:
                errors.append(f"{dim}.agent_evidence: path does not exist: {spec['agent_evidence']}")
    checks = data.get("mechanical_checks")
    if not isinstance(checks, list):
        errors.append("mechanical_checks: must be a list")
    else:
        for c in checks:
            if not isinstance(c, dict) or not c.get("name"):
                errors.append("mechanical_checks: entry must be an object with 'name'")
                continue
            if c.get("status") not in CHECK_STATUSES:
                errors.append(f"mechanical_checks.{c.get('name')}: bad status {c.get('status')!r}")
    return not errors


def load_or_scaffold(round_dir: Path, mode: str) -> tuple[dict, bool]:
    path = round_dir / SCORECARD
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8-sig")), False
    round_dir.mkdir(parents=True, exist_ok=True)
    data = template(round_number(round_dir), mode)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return data, True


def cmd_round(args) -> int:
    round_dir = args.round_dir.resolve()
    # round_dir = <root>/results/training/roundN  ->  config root is 3 levels up
    config = load_round_config(round_dir.parent.parent.parent)
    mode = config.get("mode", "closed")
    if args.check and not (round_dir / SCORECARD).is_file():
        print(f"{SCORECARD} missing in {round_dir}", file=sys.stderr)
        return 2
    data, created = load_or_scaffold(round_dir, mode)
    errors, warnings = [], []
    ok = validate_scorecard(round_dir, data, errors, warnings)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    if not ok:
        print("status: FAIL", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 2
    filled = sum(1 for s in data["dimensions"].values() if s["agent_score"] is not None)
    verdict = {"status": "PASS", "round": data.get("round"), "scaffolded": created,
               "dimensions_filled": filled, "dimensions_total": len(DIMENSIONS),
               "mechanical_checks": len(data.get("mechanical_checks", []))}
    if not args.json:
        print(json.dumps(verdict, ensure_ascii=False, indent=2))
    return 0


def summarize(root: Path) -> dict:
    rounds = []
    for sub in sorted(root.iterdir()):
        if not sub.is_dir() or not sub.name.startswith("round"):
            continue
        path = sub / SCORECARD
        if path.is_file():
            try:
                rounds.append(json.loads(path.read_text(encoding="utf-8-sig")))
            except Exception:
                continue
    rounds.sort(key=lambda r: r.get("round", 0))
    radar = {d: [] for d in DIMENSIONS}
    for data in rounds:
        for d in DIMENSIONS:
            s = data.get("dimensions", {}).get(d, {}).get("agent_score")
            radar[d].append(s)
    ranking = []
    for data in rounds:
        scores = [data.get("dimensions", {}).get(d, {}).get("agent_score") for d in DIMENSIONS]
        valid = [s for s in scores if isinstance(s, int)]
        total = sum(valid) if valid else None
        ranking.append({"round": data.get("round"), "total": total,
                        "filled": len(valid), "mode": data.get("mode")})
    ranking.sort(key=lambda r: (r["total"] is None, -(r["total"] or 0), r["round"]))
    mech = {}
    for data in rounds:
        for c in data.get("mechanical_checks", []):
            name, status = c.get("name"), c.get("status")
            mech.setdefault(name, {})[status] = mech.get(name, {}).get(status, 0) + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "rounds": [r.get("round") for r in rounds],
        "radar": radar,
        "ranking": ranking,
        "mechanical_tally": mech,
        "generated_at": utcnow(),
    }


def cmd_summary(args) -> int:
    root = args.results_dir.resolve()
    if not root.is_dir():
        print(f"results dir missing: {root}", file=sys.stderr)
        return 2
    data = summarize(root)
    path = root / SUMMARY
    if args.check:
        if not path.is_file():
            print(f"{SUMMARY} missing in {root}", file=sys.stderr)
            return 2
        try:
            existing = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            print(f"{SUMMARY} invalid: {exc}", file=sys.stderr)
            return 2
        def comparable(d):
            return {k: v for k, v in d.items() if k != "generated_at"}
        if comparable(existing) != comparable(data):
            print(f"{SUMMARY} out of sync - run training_scorecard.py summary (no --check)",
                  file=sys.stderr)
            return 2
        print(json.dumps({"status": "PASS", "rounds": len(data["rounds"])}, ensure_ascii=False))
        return 0
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    print(json.dumps({"status": "WRITTEN", "rounds": len(data["rounds"]),
                      "ranking": data["ranking"]}, ensure_ascii=False, indent=2))
    return 0


def main():
    _utf8_streams()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="command", required=True)
    p_round = sub.add_parser("round", help="scaffold/validate one round scorecard")
    p_round.add_argument("round_dir", type=Path)
    p_round.add_argument("--json", action="store_true", help="print full scorecard JSON")
    p_round.add_argument("--check", action="store_true", help="validate only, no scaffold")
    p_round.set_defaults(func=cmd_round)
    p_sum = sub.add_parser("summary", help="aggregate round scorecards into summary.json")
    p_sum.add_argument("results_dir", type=Path)
    p_sum.add_argument("--json", action="store_true", help="print full summary JSON")
    p_sum.add_argument("--check", action="store_true", help="verify summary.json matches disk")
    p_sum.set_defaults(func=cmd_summary)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
