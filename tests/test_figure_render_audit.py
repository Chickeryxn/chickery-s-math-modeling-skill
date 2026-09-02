#!/usr/bin/env python3
"""Figure render-evidence audit tests (0.8.0)."""
from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from figure_render_audit import audit


def write(p: Path, text='x'):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


def render_evidence(figure_abs: Path) -> Path:
    ev = figure_abs.parent / (figure_abs.name + '.render.json')
    write(ev, json.dumps({'status': 'PASS', 'rendered_at': '2026-09-01T00:00:00Z',
                          'checks': {'clipping': 'PASS', 'legibility': 'PASS'}}))
    return ev


class FigureRenderAuditTests(unittest.TestCase):
    def make_workspace(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        self.addCleanup(td.cleanup)
        return root

    def test_tex_referenced_figure_without_evidence_fails(self):
        root = self.make_workspace()
        write(root / 'paper/sections/q1.tex',
              r'\includegraphics[width=0.5\textwidth]{figures/q1_main.png}')
        write(root / 'paper/figures/q1_main.png', 'png')
        out = audit(root)
        self.assertEqual(out['status'], 'FAIL')
        self.assertIn('missing render evidence', out['errors'][0]['reason'])

    def test_pass_with_render_evidence(self):
        root = self.make_workspace()
        write(root / 'paper/sections/q1.tex',
              r'\includegraphics[width=0.5\textwidth]{figures/q1_main.png}')
        write(root / 'paper/figures/q1_main.png', 'png')
        render_evidence(root / 'paper/figures/q1_main.png')
        out = audit(root)
        self.assertEqual(out['status'], 'PASS')
        self.assertEqual(out['referenced'][0]['figure'], 'q1_main.png')

    def test_missing_figure_file_fails(self):
        root = self.make_workspace()
        write(root / 'paper/sections/q1.tex',
              r'\includegraphics{figures/q1_missing.png}')
        out = audit(root)
        self.assertEqual(out['status'], 'FAIL')
        self.assertIn('referenced figure not found', out['errors'][0]['reason'])

    def test_non_pass_evidence_fails_and_unreferenced_is_advisory(self):
        root = self.make_workspace()
        write(root / 'paper/sections/q1.tex',
              r'\includegraphics{figures/q1_main.png}')
        ev = root / 'paper/figures/q1_main.png.render.json'
        write(ev, json.dumps({'status': 'WARN'}))
        write(root / 'paper/figures/q1_main.png', 'png')
        write(root / 'paper/figures/q1_unused.png', 'png')
        out = audit(root)
        self.assertEqual(out['status'], 'FAIL')
        self.assertIn('not PASS or missing rendered_at', out['errors'][0]['reason'])
        self.assertIn('q1_unused.png', out['unreferenced_figures'])

    def test_commented_and_verbatim_includegraphics_ignored(self):
        # Regression: \includegraphics inside LaTeX comments or \verb spans
        # used to count as requirements.
        root = self.make_workspace()
        write(root / 'paper/sections/q1.tex',
              "% \\includegraphics{figures/commented.png}\n"
              "\\verb|\\includegraphics{figures/verb.png}|\n"
              "\\includegraphics*{figures/starred.png}\n")
        write(root / 'paper/figures/starred.png', 'png')
        render_evidence(root / 'paper/figures/starred.png')
        out = audit(root)
        self.assertEqual(out['status'], 'PASS', out['errors'])
        refs = {x['figure'] for x in out['referenced']}
        self.assertEqual(refs, {'starred.png'})

    def test_markdown_reference_supported(self):
        root = self.make_workspace()
        write(root / 'paper/sections/q1.md', '![main](figures/q1_main.png)')
        write(root / 'paper/figures/q1_main.png', 'png')
        render_evidence(root / 'paper/figures/q1_main.png')
        self.assertEqual(audit(root)['status'], 'PASS')

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'figure_render_audit.py'),
                                str(root)], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(p.returncode, 0, p.stderr)

    def test_parent_traversal_reference_rejected(self):
        # Regression: lstrip('./') used to fold '../outside.png' into
        # 'outside.png', so an escaping reference matched a same-named figure.
        root = self.make_workspace()
        write(root / 'paper/sections/q1.tex',
              r'\includegraphics{../outside.png}' + '\n'
              r'\includegraphics{figures/q1_main.png}')
        write(root / 'paper/figures/q1_main.png', 'png')
        render_evidence(root / 'paper/figures/q1_main.png')
        write(root / 'outside.png', 'png')  # outside paper/figures, must not satisfy
        out = audit(root)
        self.assertIn('FAIL', out['status'])
        self.assertTrue(any('escaping figure reference' in e['reason'] for e in out['errors']),
                        out['errors'])

    def test_absolute_reference_rejected(self):
        root = self.make_workspace()
        write(root / 'paper/sections/q1.tex', r'\includegraphics{/etc/passwd.png}')
        out = audit(root)
        self.assertTrue(any('absolute figure reference' in e['reason'] for e in out['errors']))

    def test_extensionless_reference_resolved(self):
        # LaTeX often omits the extension; a unique match must resolve.
        root = self.make_workspace()
        write(root / 'paper/sections/q1.tex', r'\includegraphics{q1_main}')
        write(root / 'paper/figures/q1_main.png', 'png')
        render_evidence(root / 'paper/figures/q1_main.png')
        out = audit(root)
        self.assertEqual(out['status'], 'PASS', out['errors'])

    def test_duplicate_basename_is_ambiguous(self):
        root = self.make_workspace()
        write(root / 'paper/sections/q1.tex', r'\includegraphics{figures/plot.png}')
        write(root / 'paper/figures/a/plot.png', 'png')
        write(root / 'paper/figures/b/plot.png', 'png')
        render_evidence(root / 'paper/figures/a/plot.png')
        render_evidence(root / 'paper/figures/b/plot.png')
        out = audit(root)
        self.assertEqual(out['status'], 'FAIL')
        self.assertTrue(any('ambiguous' in e['reason'] for e in out['errors']), out['errors'])


if __name__ == '__main__':
    unittest.main()
