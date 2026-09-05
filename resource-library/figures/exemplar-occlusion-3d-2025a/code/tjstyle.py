# -*- coding: utf-8 -*-
"""Top-journal/宋体+Times style module (shared). Chinese=SimSun, Latin/digits=Times New Roman (per-glyph fallback). Opaque data, no grid, black-edged legend."""
import os
import matplotlib.font_manager as _fm
for _p in [r"C:\Windows\Fonts\simsun.ttc", r"C:\Windows\Fonts\times.ttf"]:
    try: _fm.fontManager.addfont(_p)
    except Exception: pass
import matplotlib.pyplot as plt
plt.rcParams.update({
    "font.family": ["SimSun", "Times New Roman"],  # SimSun primary (CJK+Latin, Times-like serif); Times fallback
    "font.size": 10.5, "font.weight": "normal", "axes.titlesize": 10.5, "axes.titleweight": "normal", "axes.labelweight": "normal",
    "axes.labelsize": 10.5, "xtick.labelsize": 9.5, "ytick.labelsize": 9.5,
    "legend.fontsize": 8, "axes.unicode_minus": False,
    "figure.dpi": 90, "savefig.dpi": 220,
    "axes.grid": False, "grid.alpha": 0.0,
    "legend.frameon": True, "legend.framealpha": 1.0, "legend.edgecolor": "black",
    "mathtext.fontset": "stix",
    "mathtext.default": "bf",  # bold ALL math (physical) symbols, uniformly
})
# Saturated, high-contrast palette (no pale colors)
TJ = dict(BLACK="#000000", DARKRED="#8B1A1A", RED="#B22222", NAVY="#12365C", BLUE="#1F4E79",
          GREEN="#2E7D32", FOREST="#1B5E20", ORANGE="#D2691E", PURPLE="#6A1B9A",
          MAGENTA="#8E2A8E", TEAL="#00796B", GREY="#4A4A4A", GOLD="#B8860B")
def leg(ax, *a, **k):
    k.setdefault("frameon", True); k.setdefault("framealpha", 1.0)
    k.setdefault("edgecolor", "black"); k.setdefault("fancybox", False)
    return ax.legend(*a, **k)
import matplotlib.patheffects as _pe
def _th(col, lw): return [_pe.withStroke(linewidth=lw, foreground=col)]
def thicken(fig, lw=1.25):
    """Bold-stroke all axis-label/title/tick/legend text so it reads as bold (works for CJK & Latin, no tofu)."""
    for ax in fig.axes:
        labs = [ax.xaxis.label, ax.yaxis.label]
        if hasattr(ax, "zaxis"): labs.append(ax.zaxis.label)
        for lab in labs:
            if lab.get_text():
                c = lab.get_color() or "black"; lab.set_path_effects(_th(c, lw))
        if ax.title.get_text():
            c = ax.title.get_color() or "black"; ax.title.set_path_effects(_th(c, lw*1.1))
        for tl in list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
            if tl.get_text():
                c = tl.get_color() or "black"; tl.set_path_effects(_th(c, lw*0.8))
        lg = ax.get_legend()
        if lg is not None:
            for t in lg.get_texts():
                c = t.get_color() or "black"; t.set_path_effects(_th(c, lw*0.8))
    s = getattr(fig, "_suptitle", None)
    if s is not None and s.get_text():
        c = s.get_color() or "black"; s.set_path_effects(_th(c, lw*1.2))