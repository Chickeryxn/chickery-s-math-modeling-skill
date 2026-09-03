#!/usr/bin/env python3
"""Model quality gate: mechanical checks on experiment results before G4.

Reads the latest run_summary per subquestion and checks:
1. a fixed random seed is recorded;
2. main_candidate and usable_baseline both have non-empty metric summaries
   (i.e. the baseline comparison is real, not a toy reference);
3. at least one numeric metric exists;
4. uncertainty is present (ci/std/interval/uncertainty keys) or explicitly
   declared not applicable (`uncertainty: null` with a note);
5. the model contract's objective output_contract exists for alignment.

Pure standard library. Exit: 0 pass, 1 findings (non-strict), 2 strict.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Accepted uncertainty keys, matched on the *whole key name* (or a
# snake/underscore prefix such as `ci_lower`), never by substring: a plain
# error metric like `mean_squared_error`/`test_error` is NOT an uncertainty
# estimate and must not satisfy the uncertainty requirement.
UNCERTAINTY_KEYS = ("uncertainty", "ci", "std", "stddev", "interval")
_UNCERTAINTY_KEY_RE = re.compile(
    r"^(uncertainty|ci|std|stddev|interval)(?:_|$)")


def is_uncertainty_key(key: str) -> bool:
    kl = key.lower()
    return bool(_UNCERTAINTY_KEY_RE.match(kl))


def latest_run_summary(root: Path, qid: str) -> Path | None:
    runs = list((root / "results" / qid / "experiments").rglob("run_summary.json"))
    if not runs:
        return None

    def round_key(p: Path) -> int:
        m = re.search(r"round(\d+)", str(p))
        return int(m.group(1)) if m else 0

    return max(runs, key=round_key)


def load_contract(root: Path) -> dict:
    p = root / "planning" / "model_contract.json"
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            return {}
    return {}


def flatten_metrics(obj) -> list:
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                out.append((k, v))
            elif isinstance(v, (dict, list)):
                out.extend(flatten_metrics(v))
    elif isinstance(obj, list):
        for x in obj:
            if isinstance(x, (int, float)) and not isinstance(x, bool):
                out.append(("item", x))
            else:
                out.extend(flatten_metrics(x))
    return out


_DECLARATION_KEY_SUFFIXES = ("_note", "_reason", "_na_reason")


def _is_evidence_slot(key: str) -> bool:
    """An uncertainty-shaped key that is a slot for an estimate (not a
    `*_note`/`*_reason` declaration field holding prose)."""
    return is_uncertainty_key(key) and not key.lower().endswith(_DECLARATION_KEY_SUFFIXES)


def _value_is_real_uncertainty(v) -> bool:
    """Whether a value under an uncertainty-shaped key is real evidence.

    Numbers (and numeric lists/dicts) count. Strings count only when they
    carry a numeric token or ±/~ (e.g. '±0.02', '95% CI 1.2–2.4'); bare
    placeholder text ('n/a', 'none', 'tbd', '待定', '-') does NOT satisfy the
    uncertainty requirement — the explicit `uncertainty: null` + note path is
    the only sanctioned "not applicable" declaration.
    """
    if v is None or isinstance(v, bool):
        return False
    if isinstance(v, (int, float)):
        return True
    if isinstance(v, (dict, list)):
        items = v.values() if isinstance(v, dict) else v
        return any(_value_is_real_uncertainty(x) for x in items)
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return False
        return (any(ch.isdigit() for ch in s) or "±" in s or "~" in s)
    return False


def has_uncertainty(obj) -> bool:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if _is_evidence_slot(str(k)) and _value_is_real_uncertainty(v):
                return True
            if isinstance(v, (dict, list)) and has_uncertainty(v):
                return True
    elif isinstance(obj, list):
        return any(has_uncertainty(x) for x in obj)
    return False


def placeholder_uncertainty_values(obj, prefix: str = "") -> list[str]:
    """Collect uncertainty-shaped evidence slots whose value is placeholder
    text (reported explicitly instead of silently passing or silently failing).
    `*_note`/`*_reason` declaration prose is not scanned as a slot."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}{k}"
            if _is_evidence_slot(str(k)):
                if isinstance(v, str) and not _value_is_real_uncertainty(v) and v.strip():
                    out.append(f"{key}: {v!r}")
                if isinstance(v, dict):
                    out.extend(placeholder_uncertainty_values(v, key + "."))
            elif isinstance(v, (dict, list)):
                out.extend(placeholder_uncertainty_values(v, prefix))
    elif isinstance(obj, list):
        for x in obj:
            out.extend(placeholder_uncertainty_values(x, prefix))
    return out


def gate(root: Path, qid: str) -> dict:
    findings = []
    summary_path = latest_run_summary(root, qid)
    if summary_path is None:
        return {"question": qid, "status": "FAIL",
                "findings": [f"no run_summary found under results/{qid}/experiments"]}
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"question": qid, "status": "FAIL", "findings": [f"invalid run_summary: {exc}"]}
    if data.get("random_seed") is None:
        findings.append("random_seed missing from run_summary")
    methods = data.get("methods") or []
    roles = {m.get("role") for m in methods if isinstance(m, dict)}
    if "main_candidate" not in roles:
        findings.append("no main_candidate in methods")
    if "usable_baseline" not in roles:
        findings.append("no usable_baseline in methods")
    metrics_ok = False
    baseline_metrics_ok = False
    for m in methods:
        if not isinstance(m, dict):
            continue
        flat = flatten_metrics(m.get("metrics_summary"))
        if m.get("role") == "main_candidate" and flat:
            metrics_ok = True
        if m.get("role") == "usable_baseline" and flat:
            baseline_metrics_ok = True
    if not metrics_ok:
        findings.append("main_candidate has no numeric metrics_summary")
    if not baseline_metrics_ok:
        findings.append("usable_baseline has no numeric metrics_summary (baseline not comparable)")
    if not has_uncertainty(data):
        # A placeholder string under an uncertainty key must be reported as the
        # specific problem instead of passing silently (it is not evidence).
        junk = placeholder_uncertainty_values(data)
        if junk:
            findings.append(
                "uncertainty key(s) hold placeholder text, not a real estimate: "
                + ", ".join(junk)
                + " (record a numeric CI/std/interval, or declare "
                  "'uncertainty': null with an explicit note)")
        else:
            # Per the docstring contract, an explicit `uncertainty: null` with
            # a human-written note is an acceptable "not applicable" declaration.
            top_unc = data.get("uncertainty")
            declared_na = top_unc is None and bool(
                data.get("uncertainty_note") or data.get("uncertainty_na_reason")
                or (isinstance(data, dict) and any(
                    isinstance(v, str) and ("n/a" in v.lower() or "不适用" in v or "not applicable" in v.lower())
                    for k, v in data.items() if "uncertain" in k.lower())))
            if not declared_na:
                findings.append("no uncertainty/CI/std recorded anywhere in run_summary "
                                "(add uncertainty or declare uncertainty: null with a note)")
    contract = load_contract(root)
    out_contract = ((contract.get("objective") or {}).get("output_contract")) if contract else None
    if not out_contract:
        findings.append("model_contract.json missing objective.output_contract (alignment unchecked)")
    return {"question": qid, "status": "PASS" if not findings else "FAIL",
            "findings": findings, "run_summary": str(summary_path.relative_to(root))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("question", help="subquestion id, e.g. Q1; use 'all' for every Qx with runs")
    ap.add_argument("--strict", action="store_true", help="exit 2 on any finding")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    root = a.root.resolve()
    reports = []
    if a.question.lower() == "all":
        qids = sorted({p.parent.parent.parent.name for p in
                       (root / "results").glob("*/experiments/*/run_summary.json")}
                      if (root / "results").is_dir() else set())
        reports = [gate(root, q) for q in qids]
    else:
        reports = [gate(root, a.question)]
    any_fail = any(r["status"] == "FAIL" for r in reports)
    if a.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
    else:
        for r in reports:
            print(f"{r['question']}: {r['status']}")
            for f in r["findings"]:
                print("  >>", f)
    return (2 if any_fail else 0) if a.strict else (1 if any_fail else 0)


if __name__ == "__main__":
    raise SystemExit(main())
