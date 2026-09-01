#!/usr/bin/env python3
"""Cross-platform validation of all standalone skill trees and plugin metadata."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path


def rel_files(root: Path):
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and p.name != ".DS_Store")

def hashes(root: Path):
    out={}
    for rel in rel_files(root):
        out[rel]=hashlib.sha256((root/rel).read_bytes()).hexdigest()
    return out

def same(a: Path,b: Path):
    ha,hb=hashes(a),hashes(b)
    return ha==hb,ha,hb

def main():
    ap=argparse.ArgumentParser();ap.add_argument("root",type=Path);args=ap.parse_args();root=args.root.resolve();errors=[]
    trees=[root/".codex"/"skills",root/".claude"/"skills",root/"plugins"/"mathmodeling-skills"/"skills"]
    base=trees[0]
    if not base.is_dir():errors.append(f"missing skill tree {base}")
    for tree in trees[1:]:
        if not tree.is_dir():errors.append(f"missing skill tree {tree}");continue
        ok,_,_=same(base,tree)
        if not ok:errors.append(f"skill tree drift: {base} != {tree}")
    for path in [root/"planning"/"session_config.json",root/".agents"/"plugins"/"marketplace.json",root/"plugins"/"mathmodeling-skills"/".codex-plugin"/"plugin.json",root/"plugins"/"mathmodeling-skills"/".claude-plugin"/"plugin.json"]:
        try:json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:errors.append(f"invalid JSON {path}: {exc}")
    if errors:
        print("\n".join(errors),file=sys.stderr);return 2
    print(json.dumps({"status":"PASS","skill_files":len(rel_files(base)),"trees":"synchronized"},ensure_ascii=False));return 0
if __name__=="__main__":raise SystemExit(main())
