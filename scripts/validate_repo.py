#!/usr/bin/env python3
"""Run repository-local contract, integrity, and test checks."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True,
                       encoding='utf-8', errors='replace')
    return {'command': cmd, 'returncode': p.returncode,
            'stdout': p.stdout[-3000:], 'stderr': p.stderr[-3000:]}


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument('root', type=Path)
    ap.add_argument('--only', nargs='+', default=[],
                    help='run only these check groups: skill_trees tests contract '
                         'snapshots lineage independence qa upstream figures frozen '
                         'decisions manifests artifacts resources')
    ap.add_argument('--skip-tests', action='store_true',
                    help='skip the unittest suite (useful for quick runs)')
    a = ap.parse_args()
    r = a.root.resolve()
    reports, errors = [], []
    py = sys.executable
    only = set(a.only)

    def want(group: str) -> bool:
        return not only or group in only

    def add(group: str, cmd, required=True):
        if not want(group):
            return
        rep = run(cmd, r)
        reports.append(rep)
        if required and rep['returncode'] != 0:
            errors.append({'group': group, 'command': cmd,
                           'exit': rep['returncode'],
                           'stderr_tail': rep['stderr'][-500:]})

    if want('skill_trees'):
        add('skill_trees', [py, str(r / 'scripts' / 'validate_skill_trees.py'), str(r)])
    if want('tests') and not a.skip_tests:
        add('tests', [py, str(r / 'scripts' / 'run_tests.py')])
    if want('contract'):
        example = r / 'planning' / 'model_contract.example.json'
        if example.is_file():
            add('contract', [py, str(r / 'scripts' / 'validate_model_contract.py'), str(example)])
    def scanned(group: str, items: list) -> None:
        # Keep empty artifact groups visible: "nothing found to check" is an
        # advisory fact, not a silent pass (an empty workspace previously
        # reported PASS for every scoped group while checking nothing).
        if want(group):
            if items:
                for it in items:
                    add(group, it)
            else:
                reports.append({'group': group, 'note': 'no artifacts to check',
                                'scanned': 0})

    scanned('manifests', [[py, str(r / 'scripts' / 'validate_manifest.py'), str(r), str(p)]
                          for p in sorted((r / 'planning' / 'manifests').glob('*.json'))])
    scanned('artifacts', [[py, str(r / 'scripts' / 'validate_artifacts.py'), str(r), str(p)]
                          for p in sorted((r / 'planning' / 'manifests').glob('*.json'))])
    scanned('decisions', [[py, str(r / 'scripts' / 'validate_decisions.py'), str(r), str(p)]
                          for p in sorted(r.glob('methods/Q*/**/*_decisions.jsonl'))])
    scanned('snapshots', [[py, str(r / 'scripts' / 'validate_run_snapshot.py'), str(r), str(p.parent)]
                          for p in sorted(r.glob('results/**/run_metadata.json'))])
    scanned('lineage', [[py, str(r / 'scripts' / 'lineage.py'), 'assess', str(r), str(p)]
                        for p in sorted(r.glob('**/*.lineage.json'))])
    indep_cmds = []
    for p in sorted(r.glob('results/**/run_summary.json')):
        try:
            d = json.loads(p.read_text(encoding='utf-8-sig'))
        except Exception:
            continue
        if d.get('methods') or d.get('verifier'):
            indep_cmds.append([py, str(r / 'scripts' / 'validate_independence.py'), str(r), str(p)])
    scanned('independence', indep_cmds)
    if want('qa'):
        qa = run([py, str(r / 'scripts' / 'qa_report.py'), str(r)], r)
        reports.append(qa)
        if qa.get('returncode') != 0:
            errors.append({'group': 'qa', 'command': [py, str(r / 'scripts' / 'qa_report.py'), str(r)],
                           'exit': qa['returncode'], 'stderr_tail': qa['stderr'][-500:]})
    if want('upstream'):
        add('upstream', [py, str(r / 'scripts' / 'validate_upstream_assets.py'), str(r)])
    if want('figures'):
        add('figures', [py, str(r / 'scripts' / 'figure_render_audit.py'), str(r)])
    if want('frozen'):
        frozen_files = list(r.glob('results/*/reports/frozen_numbers.json'))
        if frozen_files:
            add('frozen', [py, str(r / 'scripts' / 'check_frozen_freshness.py'), str(r)])
    if want('resources') and (r / 'resource-library').is_dir():
        # resource-library index must match disk: an out-of-sync committed
        # index used to be invisible to every CI step and repo check.
        add('resources', [py, str(r / 'scripts' / 'resource_index.py'), str(r), '--check'])

    result = {'status': 'PASS' if not errors else 'FAIL',
              'errors': errors, 'checks': reports}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == '__main__':
    raise SystemExit(main())
