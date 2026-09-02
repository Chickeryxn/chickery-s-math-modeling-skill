#!/usr/bin/env python3
"""Generate a post-contest learning summary skeleton.

Reads the decision ledgers (methods/*/q*_decisions.jsonl) and frozen numbers
(results/*/reports/frozen_numbers.json) and writes a Markdown review skeleton:
- decision timeline per subquestion (type, choice, status, rationale);
- per-Qx verdicts (result/stability/claim-scope) and frozen claim IDs;
- a blank "lessons" section for the human modeler to fill in.

Pure standard library. The AI extracts facts only; lessons are human-owned.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

DECISION_GLOB = "methods/*/q*_decisions.jsonl"
FROZEN_GLOB = "results/*/reports/frozen_numbers.json"


def collect_decisions(root: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for p in sorted(root.glob(DECISION_GLOB)):
        qid = p.parent.name  # Q1
        records = []
        for line in p.read_text(encoding="utf-8-sig").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if isinstance(rec, dict):
                records.append(rec)
        if records:
            out[qid] = records
    return out


def collect_frozen(root: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for p in sorted(root.glob(FROZEN_GLOB)):
        qid = p.parent.parent.name  # results/Qx/reports -> Qx
        try:
            data = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        claims = data.get("claims") if isinstance(data, dict) else None
        if not isinstance(claims, list):
            claims = [v for k, v in data.items() if isinstance(v, dict) and "claim_id" in v] if isinstance(data, dict) else []
        ids = [c.get("claim_id") for c in claims if isinstance(c, dict) and c.get("claim_id")]
        if ids:
            out[qid] = ids
    return out


def decision_line(rec: dict) -> str:
    dtype = rec.get("decision_type", "?")
    status = rec.get("status", "?")
    choice = rec.get("choice")
    choice_s = f" → {choice}" if choice else ""
    return f"- `{rec.get('decision_id','?')}` [{dtype}] {status}{choice_s}"


def render(root: Path) -> str:
    lines = [
        "# 赛后复盘：学习摘要（骨架）",
        "",
        "> 本文件由 `scripts/learning_summary.py` 从决策账本与冻结数字自动生成；",
        "> 「教训」列需要你（人类建模者）填写——AI 只摘录事实，不替你总结判断。",
        "> 完整复盘方法见 `docs/post-contest-review.md`。",
        "",
    ]
    decisions = collect_decisions(root)
    frozen = collect_frozen(root)
    if not decisions and not frozen:
        lines += ["（未找到决策账本或冻结数字，本仓库尚无实际竞赛数据。）", ""]
        return "\n".join(lines)
    for qid in sorted(set(list(decisions) + list(frozen))):
        lines += [f"## {qid}", ""]
        if qid in decisions:
            lines += ["### 决策时间线", ""]
            lines += [decision_line(r) for r in decisions[qid]]
            lines += [""]
        if qid in frozen:
            lines += ["### 冻结数字（claim ID）", ""]
            lines += ["- `" + cid + "`" for cid in frozen[qid]]
            lines += [""]
        lines += ["### 事后判定与教训（人工填写）", ""]
        lines += ["| 决策 | 事后证据 | 判定（对/错/不确定） | 教训（下次怎么做） |", "|---|---|---|---|", ""]
    lines += ["---", "", "自检：是否每项判定都有证据？至少一条教训写成了可复用的红线？", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    root = a.root.resolve()
    text = render(root)
    if a.out:
        out = a.out if a.out.is_absolute() else root / a.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out.relative_to(root)}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
