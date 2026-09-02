#!/usr/bin/env python3
"""Work-record tree: a human-readable, evidence-linked process log (pure stdlib).

The tree lives under `records/` at the repository root:

    records/README.md        index (rebuilt by `index`; verified by `--check`)
    records/sessions/        session logs: YYYY-MM-DD-SSS.md, timestamped entries
    records/subjects/        per-subquestion narratives: Q1.md
    records/gates/           gate-transition timelines per subquestion: Q1.md
    records/decisions/       decision cards mirrored from qx_decisions.jsonl
    records/retros/          retrospective skeletons: YYYY-MM-DD-<slug>.md

The record tree is the readable narrative layer over the machine-readable
contracts (manifests, ledgers, run summaries, lineage). It is advisory only:
it never participates in gate judgment. Entries record facts and artifact
paths; human rationale is mirrored verbatim from the decision ledger, never
rewritten.

Commands:
  python scripts/work_record.py init [root]
  python scripts/work_record.py log "<text>" [root] [--subject Qx] [--artifacts a,b]
                            [--tags t1,t2] [--runtime codex|claude|dsh]
  python scripts/work_record.py gate Qx <G#> [root] --evidence p1,p2 [--note "..."]
  python scripts/work_record.py decision Qx <decision_id> [root] [--ledger path]
  python scripts/work_record.py retro "<title>" [root]
  python scripts/work_record.py replay [root] [--date YYYY-MM-DD] [--write]
  python scripts/work_record.py index [root]
  python scripts/work_record.py check [root]

Exit codes: 0 PASS, 2 FAIL.
"""
from __future__ import annotations
import argparse, json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

RECORDS = "records"
SUBDIRS = ("sessions", "subjects", "gates", "decisions", "retros")
GATES = ["G1", "G2", "G2.5", "G3", "G4", "G5", "G6"]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TS_RE = re.compile(r"^\d{2}:\d{2}:\d{2}$")
LINK_RE = re.compile(r"\]\(([^)#]+)\)")
FRONT_RE = re.compile(r"^---\s*$")


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def local_time() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def detect_runtime() -> str:
    if os.environ.get("DSH_SESSION_ID") or os.environ.get("DSH_SHELL"):
        return "dsh"
    if os.environ.get("CLAUDE_CODE_ENTRYPOINT") or os.environ.get("ANTHROPIC_API_KEY"):
        return "claude"
    return "codex"


def root_of(args) -> Path:
    return (args.root or Path(".")).resolve()


def rec(root: Path, *parts: str) -> Path:
    return root / RECORDS / Path(*parts)


def parse_frontmatter(path: Path) -> dict | None:
    """Return frontmatter dict, or None when absent/invalid."""
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fm = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip("'\"")
    return fm if fm else None


def write_frontmatter(path: Path, fields: dict) -> None:
    body = "---\n"
    for k, v in fields.items():
        body += f"{k}: {v}\n"
    body += "---\n"
    path.write_text(body, encoding="utf-8")


def gate_rank(g: str) -> int:
    return GATES.index(g)


def next_session_path(root: Path, date: str) -> Path:
    sdir = rec(root, "sessions")
    sdir.mkdir(parents=True, exist_ok=True)
    existing = sorted(p for p in sdir.glob(f"{date}-*.md") if not p.name.endswith("-replay.md"))
    if existing:
        return existing[-1]
    return sdir / f"{date}-001.md"


def ensure_tree(root: Path) -> None:
    for sub in SUBDIRS:
        (rec(root, sub)).mkdir(parents=True, exist_ok=True)


def cmd_init(args) -> int:
    root = root_of(args)
    ensure_tree(root)
    idx = rec(root, "README.md")
    if not idx.exists():
        idx.write_text(build_index(root), encoding="utf-8")
    print(json.dumps({"status": "INITIALIZED", "records": str(rec(root))}, ensure_ascii=False))
    return 0


def cmd_log(args) -> int:
    root = root_of(args)
    ensure_tree(root)
    date = datetime.now().strftime("%Y-%m-%d")
    path = next_session_path(root, date)
    runtime = args.runtime or detect_runtime()
    first = not path.exists()
    if first:
        head = (f"---\ndate: {date}\nsession: {path.stem}\nruntime: {runtime}\n"
                f"tags: {json.dumps(args.tags or [], ensure_ascii=False)}\n---\n\n"
                f"# 会话 {path.stem}\n\n")
    else:
        head = ""
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"## {ts} - {args.text}\n"
    if args.artifacts:
        for a in args.artifacts:
            entry += f"- 产物: [{a}]({a})\n"
    if args.subject:
        entry += f"- 子问题: {args.subject}\n"
    if args.tags:
        entry += f"- 标签: {', '.join(args.tags)}\n"
    entry += "\n"
    with path.open("a", encoding="utf-8") as f:
        f.write(head + entry)
    print(json.dumps({"status": "LOGGED", "session": path.name, "entry": ts}, ensure_ascii=False))
    return 0


def cmd_gate(args) -> int:
    root = root_of(args)
    ensure_tree(root)
    q = args.subject.upper()
    g = args.gate.upper()
    if g not in GATES:
        print(f"unknown gate {g}; expected one of {GATES}", file=sys.stderr)
        return 2
    evidence = []
    for e in args.evidence:
        p = (root / e).resolve()
        if not p.is_file():
            print(f"evidence not found: {e}", file=sys.stderr)
            return 2
        evidence.append(e)
    path = rec(root, "gates", f"{q}.md")
    last = None
    if path.exists():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            m = re.match(r"^\| \S+ \| (G[\d.]+) \|", line)
            if m and m.group(1) in GATES:
                last = m.group(1)
    if last and gate_rank(g) < gate_rank(last):
        print(f"gate regression: {g} after {last} in {path}", file=sys.stderr)
        return 2
    if not path.exists():
        write_frontmatter(path, {"subject": q, "status": "active"})
        with path.open("a", encoding="utf-8") as f:
            f.write(f"\n# {q} 门禁迁移\n\n| 时间 | 门禁 | 证据 | 备注 |\n|---|---|---|---|\n")
    row = f"| {local_time()} | {g} | {', '.join(evidence)} | {args.note or ''} |\n"
    with path.open("a", encoding="utf-8") as f:
        f.write(row)
    print(json.dumps({"status": "GATE_RECORDED", "subject": q, "gate": g}, ensure_ascii=False))
    return 0


def cmd_decision(args) -> int:
    root = root_of(args)
    ensure_tree(root)
    q = args.subject.upper()
    ledger = (root / args.ledger) if args.ledger else None
    if ledger is None or not ledger.is_file():
        cand = root / "methods" / q / f"{q.lower()}_decisions.jsonl"
        if cand.is_file():
            ledger = cand
        else:
            print(f"ledger not found for {q}; pass --ledger", file=sys.stderr)
            return 2
    found = None
    for no, line in enumerate(ledger.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rec_ = json.loads(line)
        except Exception:
            continue
        if isinstance(rec_, dict) and rec_.get("decision_id") == args.decision_id:
            found = (no, rec_)
            break
    if found is None:
        print(f"decision_id not found in {ledger}: {args.decision_id}", file=sys.stderr)
        return 2
    no, rec_ = found
    date = str(rec_.get("recorded_at", local_time()))[:10]
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", args.decision_id)
    path = rec(root, "decisions", f"{date}-{q}-{slug}.md")
    src = rec_.get("source") or {}
    body = (
        f"---\ndate: {date}\nsubject: {q}\ndecision_id: {args.decision_id}\n"
        f"ledger: {ledger.relative_to(root).as_posix()}\n---\n\n"
        f"# 决策卡：{args.decision_id}\n\n"
        f"- 子问题: {q} | 类型: {rec_.get('decision_type')} | 状态: {rec_.get('status')}\n"
        f"- 决定人: {rec_.get('decided_by')} | 时间: {rec_.get('recorded_at')}\n"
        f"- 账本位置: {ledger.relative_to(root).as_posix()}:{no}\n\n"
        f"## 选择\n\n{rec_.get('choice')}\n\n"
        f"## 理由（用户原话，AI 不重写）\n\n{rec_.get('rationale')}\n\n"
        f"## 证据引用\n\n"
        + "\n".join(f"- {r}" for r in (rec_.get("evidence_refs") or []))
        + f"\n\n## 来源消息\n\n- 消息 ID: {src.get('user_message_id')}\n"
        f"- 用户原话: {src.get('user_verbatim_answer')}\n")
    path.write_text(body, encoding="utf-8")
    print(json.dumps({"status": "CARD_WRITTEN", "card": path.name}, ensure_ascii=False))
    return 0


def cmd_retro(args) -> int:
    root = root_of(args)
    ensure_tree(root)
    date = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff-]+", "-", args.title).strip("-") or "retro"
    path = rec(root, "retros", f"{date}-{slug}.md")
    if not path.exists():
        path.write_text(
            f"---\ndate: {date}\ntitle: {args.title}\nstatus: draft\n---\n\n"
            f"# 复盘：{args.title}\n\n- 背景\n- 关键决策回顾（对照决策卡）\n"
            f"- 被结果验证的判断 / 被推翻的判断\n- 可迁移要点\n- 下一步\n",
            encoding="utf-8")
    print(json.dumps({"status": "RETRO_SCAFFOLDED", "file": path.name}, ensure_ascii=False))
    return 0


def build_index(root: Path) -> str:
    def rows(sub):
        d = rec(root, sub)
        if not d.is_dir():
            return ""
        out = []
        for p in sorted(d.glob("*.md")):
            out.append(f"- [{p.name}]({sub}/{p.name})")
        return "\n".join(out) + ("\n" if out else "")

    counts = {s: len(list(rec(root, s).glob("*.md"))) for s in SUBDIRS} if rec(root).is_dir() else {}
    return (
        "# 工作记录树\n\n"
        "> 人类可读的、证据链接的过程日志层（advisory，不参与门禁判定）。\n"
        "> 本索引由 `python scripts/work_record.py index` 生成；`check` 校验一致性。\n\n"
        f"文件数：{sum(counts.values())}。\n\n"
        f"## 会话日志（{counts.get('sessions', 0)}）\n\n{rows('sessions')}"
        f"## 子问题叙事（{counts.get('subjects', 0)}）\n\n{rows('subjects')}"
        f"## 门禁迁移（{counts.get('gates', 0)}）\n\n{rows('gates')}"
        f"## 决策卡（{counts.get('decisions', 0)}）\n\n{rows('decisions')}"
        f"## 复盘（{counts.get('retros', 0)}）\n\n{rows('retros')}")


def cmd_replay(args) -> int:
    """Replay machine-readable artifacts into a session-log draft.

    Facts are collected from manifests, decision ledgers, run summaries, and
    frozen numbers. The draft is a starting point: the agent verifies and
    annotates it; it never replaces the real record. --write stores the draft
    as sessions/<date>-replay.md; without --write it prints to stdout.
    """
    root = root_of(args)
    if not rec(root).is_dir():
        print("records/ missing; run `work_record.py init`", file=sys.stderr)
        return 2
    date = args.date or datetime.now().strftime("%Y-%m-%d")
    entries = []
    for p in sorted((root / "planning" / "manifests").glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        gate = d.get("gate") or d.get("derived_gate") or d.get("stage")
        entries.append((str(d.get("updated_at") or d.get("recorded_at") or ""),
                        f"{p.stem} manifest: gate={gate}"))
    for p in sorted((root / "methods").glob("*/q*_decisions.jsonl")):
        q = p.parent.name
        for no, line in enumerate(p.read_text(encoding="utf-8-sig").splitlines(), 1):
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if not isinstance(r, dict):
                continue
            ts = r.get("recorded_at", "")
            entries.append((ts, f"{q} decision {r.get('decision_id')}: "
                                f"{r.get('decision_type')} {r.get('status')} -> {r.get('choice')} "
                                f"(ledger {p.relative_to(root).as_posix()}:{no})"))
    for p in sorted((root / "results").glob("*/experiments/*/run_summary.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        entries.append((str(d.get("recorded_at") or ""),
                        f"run {d.get('question')} round{d.get('round')}: "
                        f"{d.get('status')} methods={d.get('methods')}"))
    for p in sorted((root / "results").glob("*/reports/frozen_numbers.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        claims = d.get("claims") if isinstance(d, dict) else None
        n = len(claims) if isinstance(claims, list) else 0
        entries.append(("", f"frozen {p.parent.parent.name}: {n} claim(s)"))
    entries.sort(key=lambda e: e[0])
    body = (f"---\ndate: {date}\nsession: {date}-replay\nruntime: {detect_runtime()}\n"
            f"replay: true\n---\n\n# 回放草稿 {date}\n\n"
            f"> 由工件自动生成（manifests/账本/run_summary/frozen），供审阅补注；非正式记录。\n\n")
    if not entries:
        body += "（当日无工件条目）\n"
    for ts, text in entries:
        t = ts[11:19] if len(ts) >= 19 else "00:00:00"
        body += f"## {t} - {text}\n\n"
    if args.write:
        out = rec(root, "sessions") / f"{date}-replay.md"
        out.write_text(body, encoding="utf-8")
        print(json.dumps({"status": "REPLAY_WRITTEN", "file": out.name,
                          "entries": len(entries)}, ensure_ascii=False))
    else:
        print(body, end="")
    return 0


def cmd_index(args) -> int:
    root = root_of(args)
    if not rec(root).is_dir():
        print(f"records/ missing; run `work_record.py init`", file=sys.stderr)
        return 2
    rec(root, "README.md").write_text(build_index(root), encoding="utf-8")
    print(json.dumps({"status": "INDEX_REBUILT"}, ensure_ascii=False))
    return 0


def check_session(path: Path, errors: list) -> None:
    fm = parse_frontmatter(path)
    if fm is None:
        errors.append(f"{path}: missing/invalid frontmatter")
        return
    for k in ("date", "session", "runtime"):
        if not fm.get(k):
            errors.append(f"{path}: frontmatter missing {k}")
    if not DATE_RE.match(fm.get("date", "")):
        errors.append(f"{path}: bad date in frontmatter")
    last = None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        m = re.match(r"^## (\d{2}:\d{2}:\d{2}) - ", line)
        if m:
            if last and m.group(1) < last:
                errors.append(f"{path}: entries out of order ({m.group(1)} after {last})")
            last = m.group(1)


def check_gates(path: Path, errors: list) -> None:
    fm = parse_frontmatter(path)
    if fm is None or not fm.get("subject"):
        errors.append(f"{path}: missing subject frontmatter")
    last = None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        m = re.match(r"^\| \S+ \| (G[\d.]+) \|", line)
        if m and m.group(1) in GATES:
            if last and gate_rank(m.group(1)) < gate_rank(last):
                errors.append(f"{path}: gate regression ({m.group(1)} after {last})")
            last = m.group(1)


def check_links(root: Path, path: Path, errors: list) -> None:
    for m in LINK_RE.finditer(path.read_text(encoding="utf-8-sig")):
        ref = m.group(1)
        if ref.startswith(("http://", "https://", "#")) or ref.startswith(("sessions/", "subjects/",
                                                                           "gates/", "decisions/", "retros/")):
            continue
        if not (root / ref).exists():
            errors.append(f"{path}: broken link {ref}")


def cmd_check(args) -> int:
    root = root_of(args)
    if not rec(root).is_dir():
        print("records/ missing", file=sys.stderr)
        return 2
    errors = []
    for p in sorted(rec(root, "sessions").glob("*.md")):
        check_session(p, errors)
    for p in sorted(rec(root, "gates").glob("*.md")):
        check_gates(p, errors)
    for sub in SUBDIRS:
        for p in sorted(rec(root, sub).glob("*.md")):
            check_links(root, p, errors)
    generated = build_index(root)
    if rec(root, "README.md").read_text(encoding="utf-8-sig") != generated:
        errors.append("records/README.md out of sync - run `work_record.py index`")
    for p in sorted(rec(root, "decisions").glob("*.md")):
        fm = parse_frontmatter(p)
        if fm and fm.get("ledger"):
            lp = root / fm["ledger"]
            if not lp.is_file():
                errors.append(f"{p}: ledger missing {fm['ledger']}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 2
    print(json.dumps({"status": "PASS", "records": str(rec(root))}, ensure_ascii=False))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="command", required=True)
    for name, func in (("init", cmd_init), ("index", cmd_index), ("check", cmd_check)):
        p = sub.add_parser(name)
        p.add_argument("root", nargs="?", type=Path, default=None)
        p.set_defaults(func=func)
    p_log = sub.add_parser("log")
    p_log.add_argument("text")
    p_log.add_argument("root", nargs="?", type=Path, default=None)
    p_log.add_argument("--subject")
    p_log.add_argument("--artifacts", nargs="+", default=[])
    p_log.add_argument("--tags", nargs="+", default=[])
    p_log.add_argument("--runtime", choices=["codex", "claude", "dsh"])
    p_log.set_defaults(func=cmd_log)
    p_gate = sub.add_parser("gate")
    p_gate.add_argument("subject")
    p_gate.add_argument("gate")
    p_gate.add_argument("root", nargs="?", type=Path, default=None)
    p_gate.add_argument("--evidence", nargs="+", required=True)
    p_gate.add_argument("--note")
    p_gate.set_defaults(func=cmd_gate)
    p_dec = sub.add_parser("decision")
    p_dec.add_argument("subject")
    p_dec.add_argument("decision_id")
    p_dec.add_argument("root", nargs="?", type=Path, default=None)
    p_dec.add_argument("--ledger")
    p_dec.set_defaults(func=cmd_decision)
    p_retro = sub.add_parser("retro")
    p_retro.add_argument("title")
    p_retro.add_argument("root", nargs="?", type=Path, default=None)
    p_retro.set_defaults(func=cmd_retro)
    p_replay = sub.add_parser("replay")
    p_replay.add_argument("root", nargs="?", type=Path, default=None)
    p_replay.add_argument("--date")
    p_replay.add_argument("--write", action="store_true",
                          help="write sessions/<date>-replay.md instead of printing")
    p_replay.set_defaults(func=cmd_replay)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
