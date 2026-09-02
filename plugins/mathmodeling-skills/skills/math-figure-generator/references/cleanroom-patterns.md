# Clean-Room Figure Patterns (self-written)

> These patterns were written independently for this repository, **inspired by** the chart-type ideas popular in scientific visualization (including those seen in [jihe520/sci-box](https://github.com/jihe520/sci-box), whose own code carries no license and is therefore NOT copied). All implementations below are original, use only `matplotlib` + `numpy` (numpy ≥ 2.0 for `np.trapezoid`; fall back to `np.trapz` on older numpy), use deterministic seeds and simulated data, and never claim to reproduce any specific publication.
> Use with `math-figure-generator`: pick the smallest pattern that communicates the claim; adapt data; keep labels/units; run render checks.

```python
# Shared preamble (Agg backend, vector text, deterministic seeds)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['pdf.fonttype'] = 42
rng = np.random.default_rng(2026)
# numpy >= 2.0 renamed np.trapz -> np.trapezoid (the old name was removed);
# pick whichever the installed numpy provides so these snippets run on both.
TRAPZ = getattr(np, 'trapezoid', None) or getattr(np, 'trapz', None)

PALETTE = {'primary': '#1A6FC4', 'primary_light': '#5B9BD5', 'baseline': '#767676',
           'positive': '#2E9E44', 'negative': '#E53935', 'accent1': '#E28E2C', 'accent2': '#7B5FD6'}
```

## 1. Paired raincloud (group A vs group B)

```python
def kde(x, grid):
    h = 1.06 * np.std(x) * len(x) ** (-1 / 5)  # Silverman rule
    return np.mean(np.exp(-0.5 * ((grid[:, None] - x[None, :]) / h) ** 2) / (h * np.sqrt(2 * np.pi)), axis=1)

def paired_raincloud(ax, a, b, label_a='Group A', label_b='Group B'):
    for i, (x, lab, color) in enumerate(zip((a, b), (label_a, label_b), (PALETTE['primary'], PALETTE['baseline']))):
        grid = np.linspace(x.min() - 1, x.max() + 1, 200)
        dens = kde(x, grid) / kde(x, grid).max() * 0.35
        ax.fill_betweenx(grid, i, i + dens, alpha=0.35, color=color)
        ax.plot([i] * len(grid), grid, lw=0.8, color=color)
        ax.plot((i + dens).tolist(), grid, lw=0.8, color=color)
        jit = rng.uniform(-0.08, 0.08, size=len(x))
        ax.scatter(i + jit, x, s=8, alpha=0.5, color=color, edgecolors='none')
        ax.boxplot(x, positions=[i + 0.42], widths=0.12, showfliers=False, patch_artist=True,
                   boxprops=dict(facecolor='white', color=color))
        ax.plot([i, i + 0.42], [np.mean(x)] * 2, color=PALETTE['negative'], lw=1.2)
    ax.set_xticks([0.2, 1.2]); ax.set_xticklabels([label_a, label_b])
    ax.set_ylabel('Value'); ax.set_title('Paired raincloud')
```

## 2. ROC curves with CI band (simulated 5-fold CV)

```python
def roc_with_ci(ax, n_models=3, n_folds=5, n_thresh=200):
    for m in range(n_models):
        tprs, base_fpr = [], np.linspace(0, 1, n_thresh)
        for _ in range(n_folds):
            auroc = rng.uniform(0.65, 0.92)
            tpr = base_fpr ** (1 / max(auroc, 1e-6))  # deterministic ROC shape from AUC
            tprs.append(tpr)
        mean = np.mean(tprs, axis=0); sd = np.std(tprs, axis=0)
        color = [PALETTE['primary'], PALETTE['accent1'], PALETTE['accent2']][m]
        ax.plot(base_fpr, mean, lw=1.6, color=color,
                label=f'Model {m+1} (AUC={TRAPZ(mean, base_fpr):.2f})')
        ax.fill_between(base_fpr, mean - sd, mean + sd, alpha=0.15, color=color)
    ax.plot([0, 1], [0, 1], ls='--', color=PALETTE['baseline'])
    ax.set_xlabel('False positive rate'); ax.set_ylabel('True positive rate')
    ax.legend(loc='lower right', fontsize=8); ax.set_title('ROC with CI band (simulated)')
```

## 3. Taylor diagram (simulated correlation / std ratios)

```python
def taylor_diagram(ax, corr, std_ratio, labels):
    # corr: correlations to reference; std_ratio: std/ref_std
    theta = np.arccos(np.clip(corr, -1, 1)); r = std_ratio
    rr = np.linspace(0, 2, 100)
    ax.plot(rr * np.cos(np.linspace(0, np.pi / 2, 100)),
            rr * np.sin(np.linspace(0, np.pi / 2, 100)), color=PALETTE['baseline'], lw=0.8)
    ax.plot([0, 1.4], [0, 0], color=PALETTE['baseline'], lw=0.8)
    for t, rr_, lab in zip(theta, r, labels):
        ax.scatter(rr_ * np.cos(t), rr_ * np.sin(t), s=40, color=PALETTE['primary'])
        ax.annotate(lab, (rr_ * np.cos(t), rr_ * np.sin(t)), textcoords='offset points',
                    xytext=(6, 6), fontsize=8)
    ax.set_aspect('equal'); ax.set_xlim(0, 1.6); ax.set_ylim(0, 1.6)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_title('Taylor diagram (simulated)')
```

## 4. Chord diagram (simulated flows)

```python
from matplotlib.patches import Wedge, PathPatch
from matplotlib.path import Path

def chord_diagram(ax, flow, labels):
    # flow: NxN symmetric matrix; draw N sectors + bezier ribbons
    n = len(flow); total = flow.sum()
    widths = flow.sum(axis=1) / total * 2 * np.pi
    start = 0.0
    for i, w in enumerate(widths):
        ax.add_patch(Wedge((0, 0), 1.0, np.degrees(start), np.degrees(start + w),
                           width=0.12, facecolor=plt.cm.tab20(i % 20)))
        mid = start + w / 2
        ax.text(1.16 * np.cos(mid), 1.16 * np.sin(mid), labels[i],
                ha='center', va='center', fontsize=7, rotation=np.degrees(mid))
        start += w
    for i in range(n):
        for j in range(i + 1, n):
            v = flow[i, j]
            if v <= 0: continue
            a0 = sum(widths[:i]) + widths[i] / 2; a1 = sum(widths[:j]) + widths[j] / 2
            p = Path([(np.cos(a0), np.sin(a0)), (0, 0), (np.cos(a1), np.sin(a1))],
                     [Path.MOVETO, Path.CURVE3, Path.CURVE3])
            ax.add_patch(PathPatch(p, lw=0.0, alpha=min(0.6, v / flow.max()), color=plt.cm.tab20(i % 20)))
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_aspect('equal')
    ax.axis('off'); ax.set_title('Chord diagram (simulated flows)')
```

## 5. Grouped circular heatmap (simulated ring)

```python
def circular_heatmap(ax, data, group_labels, feature_labels):
    # data: features x items
    nf, ni = data.shape
    theta = np.linspace(0, 2 * np.pi, ni, endpoint=False)
    for f in range(nf):
        vals = data[f]
        norm = (vals - vals.min()) / max(vals.max() - vals.min(), 1e-9)
        r = 0.4 + f * 0.28
        ax.bar(theta, np.full(ni, 0.24), width=2 * np.pi / ni, bottom=r,
               color=plt.cm.RdBu_r(norm), edgecolor='none', alpha=0.9)
    ax.set_ylim(0, 2.2); ax.axis('off')
    ax.set_title('Grouped circular heatmap (simulated)')
```

## 6. Correlation pairgrid (simulated 5x5)

```python
def correlation_pairgrid(fig, X, names):
    n = X.shape[1]
    for i in range(n):
        for j in range(n):
            ax = fig.add_subplot(n, n, i * n + j + 1)
            if i == j:
                ax.hist(X[:, i], bins=12, color=PALETTE['primary'], alpha=0.7); ax.set_xticks([]); ax.set_yticks([])
            elif i < j:
                c = np.corrcoef(X[:, i], X[:, j])[0, 1]
                ax.scatter(X[:, i], X[:, j], s=6, alpha=0.5, color=PALETTE['primary'])
                ax.text(0.05, 0.9, f'{c:.2f}', transform=ax.transAxes, fontsize=8)
            else:
                ax.axis('off')
            if j == 0: ax.set_ylabel(names[i], fontsize=7)
            if i == n - 1: ax.set_xlabel(names[j], fontsize=7)
```

## 7. Forest plot (point estimates with CI)

```python
def forest_plot(ax, labels, est, lo, hi, ref=None):
    y = np.arange(len(labels))[::-1]
    ax.errorbar(est, y, xerr=[np.array(est)-np.array(lo), np.array(hi)-np.array(est)],
                fmt='o', color=PALETTE['primary'], ecolor=PALETTE['baseline'], capsize=3, ms=5)
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=8)
    if ref is not None:
        ax.axvline(ref, ls='--', color=PALETTE['baseline'], lw=0.9)
    ax.set_xlabel('Estimate (95% CI)'); ax.set_title('Forest plot (simulated)')
```

## 8. Density ridge plot (per-group distributions)

```python
def density_ridge(ax, groups, labels):
    for i, (g, lab) in enumerate(zip(groups, labels)):
        grid = np.linspace(np.min(g), np.max(g), 200)
        d = kde(g, grid); d = d / d.max() * 0.8
        ax.fill_between(grid, i, i + d, alpha=0.45, color=PALETTE['primary'] if i % 2 == 0 else PALETTE['accent1'])
        ax.text(grid[np.argmax(d)], i + d.max() + 0.08, lab, ha='center', fontsize=8)
    ax.set_yticks([]); ax.set_ylim(-0.2, len(groups) + 0.6); ax.set_xlabel('Value')
    ax.set_title('Density ridge (simulated)')
```

## 9. Clustered heatmap (reordered rows/columns)

```python
def clustered_heatmap(ax, Z, row_labels, col_labels):
    # Z: rows x cols; cluster rows by single linkage on correlation distance,
    # then reorder rows so merged clusters stay adjacent.
    def hclust(M):
        # single-linkage greedy merge; returns a leaf ordering that keeps
        # every merged cluster contiguous (previously `perm` was never
        # updated, so the "reordered" claim silently produced no reorder).
        n = len(M)
        active = list(range(n))
        groups = {i: [i] for i in range(n)}
        while len(active) > 1:
            best = None
            for ai, a in enumerate(active):
                for b in active[ai + 1:]:
                    d = 1 - abs(np.corrcoef(M[a], M[b])[0, 1])
                    if best is None or d < best[0]:
                        best = (d, a, b)
            _, a, b = best
            M[a] = (M[a] + M[b]) / 2          # merged centroid
            groups[a] = groups[a] + groups[b] # keep adjacency
            active.remove(b)
        return groups[active[0]]
    perm = hclust(Z.copy())
    im = ax.imshow(Z[perm], aspect='auto', cmap='RdBu_r', vmin=-1, vmax=1)
    ax.set_yticks(range(len(perm))); ax.set_yticklabels([row_labels[i] for i in perm], fontsize=7)
    ax.set_xticks(range(Z.shape[1])); ax.set_xticklabels(col_labels, fontsize=7, rotation=45, ha='right')
    ax.figure.colorbar(im, ax=ax, fraction=0.03, pad=0.02); ax.set_title('Clustered heatmap (simulated)')
```

## 10. Multi-panel time series (shared x)

```python
def time_series_panels(fig, t, series_list, labels):
    for i, (s, lab) in enumerate(zip(series_list, labels)):
        ax = fig.add_subplot(len(series_list), 1, i + 1, sharex=ax if i else None)
        ax.plot(t, s, color=PALETTE['primary'], lw=1.4)
        ax.set_ylabel(lab, fontsize=8); ax.grid(alpha=0.25)
        if i < len(series_list) - 1: ax.set_xticks([])
    ax.set_xlabel('Time')
```

## Usage rules

- All patterns are **simulated-data examples**: replace the data with the model's real outputs; never claim these simulated figures reproduce any source study.
- Type 1 diagnostics stay internal; only Type 3/4 versions (with real data, render-checked) enter the paper.
- **Color**: the canonical palette for this skill is `references/color-systems.md` (primary `#1A6FC4`, baseline grey). The upstream `references/upstream/nature-figure/api.md` `DEFAULT_COLORS` are reference material only — do not mix two palettes in one figure.
- See also the publication rules in the repository-level `references/upstream/nature-figure/` (figure contract, QA contract) and `references/upstream/lupynow-writing/figure-and-code-guide.md` (Figure Contract, matplotlib-only).
