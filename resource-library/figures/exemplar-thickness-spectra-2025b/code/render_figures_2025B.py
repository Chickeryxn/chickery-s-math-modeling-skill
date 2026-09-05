# -*- coding: utf-8 -*-
"""
2025 国赛 B 题(碳化硅/硅外延层厚度, 红外干涉) — 结论先行签名图 可复现渲染脚本。
全部数值来自 附件 xlsx 实测光谱 + 给定常数(n_SiC=2.6, n_Si=3.4); 离线计算; 不伪造任何数值。
产物: results/training/round1/2025B/figures/*.png
"""
import os, numpy as np, pandas as pd
from scipy.signal import find_peaks, savgol_filter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MAIN = "#1A6FC4"; GRAY = "#767676"; HL = "#B91C1C"
ACC1 = "#4C9A2A"; ACC2 = "#E08214"
BASE = r"resource-library/assets/problems/2025/B题/附件/"
N = {"SiC": 2.6, "Si": 3.4}
OUTDIR = r"results/training/round1/2025B/figures"
os.makedirs(OUTDIR, exist_ok=True)
CM = "cm$^{-1}$"

import tjstyle
ND = r"$\Delta\tilde{\nu}$"


def load(fname):
    df = pd.read_excel(BASE + fname, header=0); c = list(df.columns)
    return df[c[0]].to_numpy(float), df[c[1]].to_numpy(float)

def ctp(t, n):
    return np.sqrt(1 - (np.sin(np.deg2rad(t)) / n) ** 2)

def build(fname, mat, theta, lo, hi):
    nu, R = load(fname); m = (nu >= lo) & (nu <= hi)
    nus, Rs = nu[m], R[m]
    osc = Rs - np.polyval(np.polyfit(nus, Rs, 5), nus)
    osc_s = savgol_filter(osc, 31, polyorder=2)
    Nn = len(nus); Sp = np.abs(np.fft.rfft(osc_s * np.hanning(Nn)))
    fr = np.fft.rfftfreq(Nn, d=nus[1] - nus[0])
    k0 = np.searchsorted(fr, 1.0 / (nus[-1] - nus[0]) * 1.5)
    f0 = fr[k0 + np.argmax(Sp[k0:])]
    def cost(f):
        c = np.cos(2*np.pi*f*nus); s = np.sin(2*np.pi*f*nus)
        A = np.vstack([c, s, np.ones_like(nus)]).T
        be, *_ = np.linalg.lstsq(A, osc_s, rcond=None); rr = osc_s - A@be
        return np.sum(rr*rr), np.hypot(be[0], be[1]), rr
    fl = np.linspace(f0*0.95, f0*1.05, 1201); f1 = fl[np.argmin([cost(f)[0] for f in fl])]
    fl2 = np.linspace(f1*0.9995, f1*1.0005, 401); f1 = fl2[np.argmin([cost(f)[0] for f in fl2])]
    _, a1, rr = cost(f1)
    ch = np.cos(2*np.pi*2*f1*nus); sh = np.sin(2*np.pi*2*f1*nus)
    b2, *_ = np.linalg.lstsq(np.vstack([ch, sh, np.ones_like(nus)]).T, osc_s, rcond=None)
    a2 = np.hypot(b2[0], b2[1])
    dist = max(1, int(0.4 * (1/f1) / (nus[1]-nus[0]))); prom = 0.30*np.std(osc_s)
    pk, _ = find_peaks(osc_s, prominence=prom, distance=dist)
    vk, _ = find_peaks(-osc_s, prominence=prom, distance=dist)
    xs = list(nus[pk]) + list(nus[vk])
    ys = list(np.arange(len(pk)).astype(float)) + list(np.arange(len(vk)) + 0.5)
    b, _ = np.polyfit(np.array(xs), np.array(ys), 1)
    c = ctp(theta, N[mat])
    return dict(nus=nus, Rs=Rs, osc=osc_s, f1=f1, a1=a1, a2=a2, pk=pk, vk=vk,
                n=N[mat], ctp=c, mat=mat, theta=theta,
                d_cos=f1/(2*N[mat]*c)*1e4, d_order=b/(2*N[mat]*c)*1e4,
                vis=a1/np.mean(Rs), harm2=a2/a1,
                res_sig=np.sqrt(np.mean(rr**2))/np.std(osc_s),
                dpm=np.median(np.diff(nus[pk])) if len(pk) > 2 else np.nan,
                dvm=np.median(np.diff(nus[vk])) if len(vk) > 2 else np.nan,
                asym=(abs(np.median(np.diff(nus[vk]))-np.median(np.diff(nus[pk])))
                      / min(np.median(np.diff(nus[vk])), np.median(np.diff(nus[pk])))*100)
                if len(pk) > 2 and len(vk) > 2 else np.nan)

SIC10 = build("附件1.xlsx", "SiC", 10, 1800, 3950)
SIC15 = build("附件2.xlsx", "SiC", 15, 1800, 3950)
SI10 = build("附件3.xlsx", "Si", 10, 1300, 3950)
SI15 = build("附件4.xlsx", "Si", 15, 1300, 3950)

def relm(a, period, wmul=3.0):
    step = a["nus"][1] - a["nus"][0]; w = int(wmul*period/step); w = w if w%2 else w+1
    base = savgol_filter(a["Rs"], w, 3)
    return (a["Rs"] - base) / base * 100

RM_SI = relm(SI10, 429); RM_SIC = relm(SIC10, 256)


def dnu_arrow(ax, a, x0, x1, y, txt):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="<->", color=GRAY, lw=1.3))
    ax.text((x0+x1)/2, y + 0.11, txt, ha="center", va="bottom", fontsize=8.5, color=GRAY)


def fig1():
    fig, axs = plt.subplots(2, 1, figsize=(6.6, 4.4), sharex=True)
    for ax, a, lab, col in [(axs[0], SIC10, "SiC 10° (附件1, 入射角10°)", MAIN),
                            (axs[1], SIC15, "SiC 15° (附件2, 入射角15°)", ACC2)]:
        ax.plot(a["nus"], a["Rs"], color=col, lw=1.1, label=lab)
        ax.plot(a["nus"][a["vk"]], a["Rs"][a["vk"]], "v", ms=5.5, color=HL,
                zorder=5, label="干涉谷(最小值)")
        vk = a["vk"]
        i = len(vk) // 2 - 1
        x0, x1 = a["nus"][vk[i]], a["nus"][vk[i+1]]
        dnu_arrow(ax, a, x0, x1, a["Rs"].min()-0.12*(a["Rs"].max()-a["Rs"].min()),
                  f"{ND} = {1/a['f1']:.0f} " + CM)
        ax.set_ylabel("反射率  R (%)")
        tjstyle.leg(ax, loc="upper right", ncol=2, fontsize=8)
        ax.set_ylim(a["Rs"].min()-0.62, a["Rs"].max()+0.9)
    axs[1].set_xlabel("波数  (" + CM + ")")
    fig.suptitle("SiC 反射光谱与干涉条纹（10° / 15° 两入射角）",
                 fontsize=11.5, fontweight="bold", y=0.985)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    p = os.path.join(OUTDIR, "fig1_spectrum_fringes_SiC_two_angle.png")
    fig.savefig(p,dpi=300,bbox_inches="tight"); fig.savefig(p.replace(".png",".pdf"),bbox_inches="tight"); plt.close(fig)
    return p


def fig2():
    fig, (L, R) = plt.subplots(1, 2, figsize=(6.6, 4.0), gridspec_kw={"width_ratios": [1.5, 1]})
    for a, col, lab, mk in [(SIC10, MAIN, "10°", "o"), (SIC15, ACC2, "15°", "s")]:
        nus, pk, vk = a["nus"], a["pk"], a["vk"]
        xs = np.array(list(nus[pk]) + list(nus[vk]))
        ys = np.array(list(np.arange(len(pk)).astype(float)) + list(np.arange(len(vk)) + 0.5))
        b, c0 = np.polyfit(xs, ys, 1)
        xx = np.array([xs.min()-40, xs.max()+40])
        L.plot(xx, b*xx+c0, color=col, lw=1.8,
               label=f"{lab}: 2·n·d·cosθ' = {2*a['n']*a['ctp']:.3f} → d = {a['d_order']:.2f} μm")
        L.plot(nus[pk], np.arange(len(pk)), mk, ms=4.5, color=col)
        L.plot(nus[vk], np.arange(len(vk))+0.5, mk, ms=4.5, color=col)
    L.set_xlabel("波数  (" + CM + ")"); L.set_ylabel("相对干涉级次  m")
    L.set_title(r"$m = 2\,n\,d\,\cos\theta'\,\tilde{\nu}$" + "  线性回归", fontsize=10.5)
    tjstyle.leg(L, loc="lower right", fontsize=7.5)
    d10, d15 = SIC10["d_order"], SIC15["d_order"]
    d10c, d15c = SIC10["d_cos"], SIC15["d_cos"]
    for xv, a, col in [(0, SIC10, MAIN), (1, SIC15, ACC2)]:
        lo = min(a["d_order"], a["d_cos"]); hi = max(a["d_order"], a["d_cos"]); mid = (lo+hi)/2
        R.errorbar([xv], [mid], yerr=[[mid-lo], [hi-mid]], fmt="D", ms=7, color=col,
                   ecolor=col, capsize=5, lw=1.6,
                   label=f"{a['theta']}°: d={a['d_order']:.2f} μm")
    R.set_xticks([0, 1]); R.set_xticklabels(["10°", "15°"])
    R.set_ylabel("外延层厚度  d (μm)"); R.set_ylim(7.45, 7.72)
    R.set_title(f"Δd = {abs(d10-d15):.2f} μm  ({abs(d10-d15)/d10*100:.1f}%)")
    tjstyle.leg(R, loc="upper left", fontsize=7.5)
    fig.suptitle("外延层厚度反演（两入射角对照）",
                 fontsize=11.5, fontweight="bold", y=1.0)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    p = os.path.join(OUTDIR, "fig2_thickness_two_angles_SiC.png")
    fig.savefig(p,dpi=300,bbox_inches="tight"); fig.savefig(p.replace(".png",".pdf"),bbox_inches="tight"); plt.close(fig)
    return p


def fig3():
    fig, (L, R) = plt.subplots(1, 2, figsize=(6.6, 4.2), gridspec_kw={"width_ratios": [1.5, 1]})
    ms = SI10["nus"] >= 2150
    mc = SIC10["nus"] >= 2150
    L.plot(SI10["nus"][ms], RM_SI[ms], color=HL, lw=1.0, label="Si (附件3, 10°)")
    L.plot(SIC10["nus"][mc], RM_SIC[mc], color=MAIN, lw=1.0, label="SiC (附件1, 10°)")
    L.axhline(0, color=GRAY, lw=0.7, ls=":")
    L.set_xlabel("波数  (" + CM + ")")
    L.set_ylabel("相对反射率调制  (R/R$_0$ - 1, %)")
    L.set_xlim(2150, 3750); L.set_ylim(-12, 12)
    tjstyle.leg(L, loc="upper right", fontsize=7.5)
    L.set_title("相对调制深度（Si vs SiC）", fontsize=10.5)
    labels = ["条纹可见度\n$V$ = $A_1/R_0$", "2次谐波比\n$A_2/A_1$"]
    si = [SI10["vis"], SI10["harm2"]]; sic = [SIC10["vis"], SIC10["harm2"]]
    x = np.arange(2); w = 0.34
    R.bar(x-w/2, si, w, color=HL, hatch="//", edgecolor="k", lw=0.6, label="Si")
    R.bar(x+w/2, sic, w, color=MAIN, hatch="..", edgecolor="k", lw=0.6, label="SiC")
    for xi, v in zip(x-w/2, si): R.text(xi, v+0.005, f"{v:.2f}", ha="center", fontsize=7.5)
    for xi, v in zip(x+w/2, sic): R.text(xi, v+0.005, f"{v:.2f}", ha="center", fontsize=7.5)
    R.set_xticks(x); R.set_xticklabels(labels, fontsize=8); R.set_ylim(0, 0.17)
    R.set_ylabel("无量纲"); R.set_title("可见度 / 2次谐波比", fontsize=10.5)
    tjstyle.leg(R, loc="upper right", fontsize=7.5)
    fig.suptitle("多光束判据：Si vs SiC（约束可见度 · 2 次谐波比）",
                 fontsize=11.5, fontweight="bold", y=1.0)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    p = os.path.join(OUTDIR, "fig3_multibeam_Si_vs_SiC.png")
    fig.savefig(p,dpi=300,bbox_inches="tight"); fig.savefig(p.replace(".png",".pdf"),bbox_inches="tight"); plt.close(fig)
    return p


print("FACTS:")
for k, a in [("SiC10", SIC10), ("SiC15", SIC15), ("Si10", SI10), ("Si15", SI15)]:
    print(f"  {k}: d_cos={a['d_cos']:.3f} d_order={a['d_order']:.3f} dnu={1/a['f1']:.2f} "
          f"vis={a['vis']:.4f} harm2={a['harm2']:.4f} asym={a['asym']:.1f}% res_sig={a['res_sig']:.2f}")
outs = [fig1(), fig2(), fig3()]
print("OUTPUTS:")
for p in outs:
    print(" ", p, os.path.getsize(p), "bytes")
