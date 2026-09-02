#!/usr/bin/env python3
"""Portable skill-tree synchronizer; .codex/skills is the source tree.

Copies the source tree into every target tree (.claude, .agents, plugin
distribution). By default only files present in the source are added or
overwritten; files that exist in a target but not in the source are KEPT and
reported as extras (they may be user-local additions). Pass --prune to delete
those extras instead. --check verifies the trees are byte-identical (no drift,
no extras) without writing anything.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, sys
from pathlib import Path


def _utf8():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def files(root: Path) -> list[str]:
    return sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and p.name != ".DS_Store" and not p.name.endswith(".pyc"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_tree(src: Path, dst: Path, prune: bool) -> list[str]:
    """Copy every source file into dst; with prune, remove target-only files.

    Returns the list of removed extra files (empty without --prune).
    """
    dst.mkdir(parents=True, exist_ok=True)
    source = set(files(src))
    for rel in source:
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / rel, target)
    removed = []
    if prune:
        for rel in sorted(set(files(dst)) - source):
            (dst / rel).unlink()
            removed.append(rel)
    return removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root', type=Path)
    ap.add_argument('--check', action='store_true',
                    help='verify trees are byte-identical without writing')
    ap.add_argument('--dry-run', action='store_true',
                    help='show what would be copied/removed without writing')
    ap.add_argument('--prune', action='store_true',
                    help='delete target-tree files absent from the source tree '
                         '(default keeps them and reports them as extras)')
    args = ap.parse_args()
    r = args.root.resolve()
    src = r / '.codex' / 'skills'
    targets = [r / '.claude' / 'skills',
               r / 'plugins' / 'mathmodeling-skills' / 'skills',
               r / '.agents' / 'skills']
    if not src.is_dir():
        print('missing source tree', file=sys.stderr)
        return 2
    dist_copies = [('AGENTS.md', r / 'plugins' / 'mathmodeling-skills' / 'AGENTS.md'),
                   ('LICENSE', r / 'plugins' / 'mathmodeling-skills' / 'LICENSE')]
    if args.dry_run:
        plan = []
        for dst in targets:
            source = set(files(src))
            existing = set(files(dst)) if dst.is_dir() else set()
            plan.append({
                'target': str(dst),
                'would_copy': sorted(source - existing),
                'would_remove': sorted(existing - source) if args.prune else [],
                'kept_extras': sorted(existing - source) if not args.prune else [],
            })
        for name, dst in dist_copies:
            if not dst.is_file() or sha(r / name) != sha(dst):
                plan.append({'target': str(dst), 'would_copy': [name],
                             'would_remove': [], 'kept_extras': []})
        print(json.dumps({'status': 'DRY_RUN', 'prune': args.prune, 'plan': plan},
                         ensure_ascii=False, indent=2))
        return 0
    if not args.check:
        for dst in targets:
            copy_tree(src, dst, args.prune)
        for name, dst in dist_copies:
            shutil.copy2(r / name, dst)
    src_hash = {rel: sha(src / rel) for rel in files(src)}
    errors = []
    kept_extras = {}
    for dst in targets:
        if not dst.is_dir():
            errors.append(f'missing target tree: {dst}')
            continue
        got = {rel: sha(dst / rel) for rel in src_hash if (dst / rel).is_file()}
        missing = [rel for rel in src_hash if rel not in got]
        mismatched = [rel for rel in src_hash if rel in got and got[rel] != src_hash[rel]]
        if missing or mismatched:
            errors.append(f'drift: {dst} (missing={missing or []} '
                          f'mismatched={mismatched or []})')
        extras = sorted(set(files(dst)) - set(src_hash))
        if args.check:
            if extras:
                errors.append(f'extra files in {dst}: {extras} '
                              '(run: python scripts/sync_plugin.py . --prune)')
        elif extras:
            kept_extras[str(dst)] = extras
    for name, dst in dist_copies:
        try:
            if sha(r / name) != sha(dst):
                errors.append(f'{name} distribution drift')
        except FileNotFoundError:
            errors.append(f'{name} distribution file missing')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 2
    out = {'status': 'PASS', 'source': str(src),
           'targets': [str(x) for x in targets], 'files': len(src_hash)}
    if kept_extras:
        # Advisory: target-only files were kept (no --prune). --check would
        # still flag them, so pruning is expected before a release.
        out['kept_extras'] = kept_extras
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    _utf8()
    raise SystemExit(main())
