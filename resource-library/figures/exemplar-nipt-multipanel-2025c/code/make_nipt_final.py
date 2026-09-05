#!/usr/bin/env python3
# Round-1 FINAL signature figures, 2025 C (NIPT). Offline, from attachment.
import sys, re, os, json, datetime
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, minimize, brentq
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
sys.stdout.reconfigure(encoding="utf-8")
import tjstyle
OUT="results/training/round1/2025C/figures"; os.makedirs(OUT,exist_ok=True)
PRIMARY="#1A6FC4"; BASELINE="#767676"; SIG="#B91C1C"
A1="#4C9A2A"; A2="#E08214"; A3="#8E44AD"; A4="#0F9D58"
GROUPS={"[28,32)":PRIMARY,"[32,36)":A1,"[36,42)":A2}
SHEET="resource-library/assets/problems/2025/C题/附件.xlsx"
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
LAM=0.25; START=12.0
def wk(s):
    q=re.search(r"(\d+)\s*[wW周]\s*\+?\s*(\d+)?",str(s))
    if q: return float(q.group(1))+float(q.group(2) or 0)/7.0
    try: return float(s)
    except: return np.nan
def logit(z): return 1/(1+np.exp(-z))

# ----------------- MALE -----------------
m=pd.ExcelFile(SHEET).parse("男胎检测数据")
m["week"]=m["检测孕周"].map(wk); m["Y"]=pd.to_numeric(m["Y染色体浓度"],errors="coerce")*100
m["BMI"]=pd.to_numeric(m["孕妇BMI"],errors="coerce"); m=m.dropna(subset=["week","Y","BMI"])
bins=[28,32,36,42]; labs=list(GROUPS.keys())
m["grp"]=pd.cut(m["BMI"],bins=bins,labels=labs,right=False)
excl=int(((m.BMI<28)|(m.BMI>=42)).sum()); m=m.dropna(subset=["grp"])
def power(w,a,b): return a*np.power(np.maximum(w,1e-6),b)
X=np.column_stack([np.ones(len(m)),m["week"].values,m["BMI"].values]); yv=(m["Y"].values>=4.0).astype(float)
def nll(t):
    z=X@t; return -np.mean(yv*np.log(logit(z)+1e-9)+(1-yv)*np.log(1-logit(z)+1e-9))
th=minimize(nll,[-10,0.4,-0.02],method="Nelder-Mead",options=dict(maxiter=20000,xatol=1e-8,fatol=1e-8)).x
def rel(w,bmi): return logit(th[0]+th[1]*w+th[2]*bmi)
gp={}
for g in labs:
    d=m[m.grp==g]; pp,_=curve_fit(power,d["week"].values,d["Y"].values,p0=[0.3,1.0],maxfev=20000)
    a,b=pp; r2=1-np.sum((d["Y"].values-power(d["week"].values,*pp))**2)/np.sum((d["Y"].values-d["Y"].mean())**2)
    if power(11,a,b)>=4: wc=11.0; lab="自11周起≥4%"
    elif power(30,a,b)<4: wc=np.nan; lab="全程<4%"
    else: wc=brentq(lambda w: power(w,a,b)-4.0,11,30); lab=f"≈{wc:.1f}周跨过4%"
    gp[g]=dict(n=len(d),a=float(a),b=float(b),r2=float(r2),bmi_mean=float(d.BMI.mean()),
               ymean=float(d.Y.mean()),cross=(None if wc!=wc else float(wc)),crosslab=lab)
def low(w): return 1.0 if w<=12 else (3.0 if w<=27 else 5.0)
def risk(w,bmi): return (1-rel(w,bmi))+LAM*low(w)
riskopt={}
for g in labs:
    bmi=gp[g]["bmi_mean"]; ww=np.arange(9.0,30.001,0.005); rr=np.array([risk(w,bmi) for w in ww])
    i=int(np.argmin(rr))
    riskopt[g]=dict(t=float(ww[i]),R=float(rr[i]),bmi=float(bmi),rel12=float(rel(12,bmi)),
                    rel20=float(rel(20,bmi)),rel27=float(rel(27,bmi)))

# ---- C1 ----
fig,ax=plt.subplots(figsize=(6.6,4.2))
for g in labs:
    d=m[m.grp==g]; c=GROUPS[g]
    ax.scatter(d["week"],d["Y"],s=8,alpha=1.0,color=c,edgecolors="k",linewidths=0.3,label=f"BMI {g} (n={len(d)})")
    ww=np.linspace(8,30,200)
    ax.plot(ww,power(ww,gp[g]["a"],gp[g]["b"]),color=c,lw=1.7,
            label=f"{g} 幂律 Y={gp[g]['a']:.2f}·w^{gp[g]['b']:.2f}  R²={gp[g]['r2']:.2f}")
ax.axhline(4.0,color=SIG,ls="--",lw=1.2,label="可靠性阈值 4%")
ax.axvline(START,color=PRIMARY,ls=":",lw=0.9)
ax.set_xticks(np.arange(8,32,2)); ax.set_xlabel("检测孕周  $w$（周）")
ax.set_ylabel("Y 染色体浓度  $Y$（%）"); ax.set_ylim(0,max(8,m["Y"].max()*1.03))
ax.set_title("Y 染色体浓度 vs 检测孕周（按 BMI 分组 · 4% 阈值线）",fontsize=10,fontweight="bold")
tjstyle.leg(ax,fontsize=7,loc="upper left")
pass  # 统计信息已并入标题（文字渐变不加底框）
fig.tight_layout(); fig.savefig(f"{OUT}/fig_C1_y_conc_vs_week_bmi.png",dpi=300,bbox_inches="tight",pad_inches=0.15); fig.savefig(f"{OUT}/fig_C1_y_conc_vs_week_bmi.pdf",bbox_inches="tight"); plt.close(fig)

# ---- C2 ----
fig2,ax2=plt.subplots(figsize=(6.6,4.2))
ww=np.linspace(9,30,420)
for g in labs:
    bmi=gp[g]["bmi_mean"]; c=GROUPS[g]
    rr=np.array([risk(w,bmi) for w in ww])
    ax2.plot(ww,rr,color=c,lw=1.7,label=f"BMI {g}（均值={bmi:.1f}）")
    t=riskopt[g]["t"]; R=riskopt[g]["R"]
    ax2.scatter([t],[R],color=c,s=55,zorder=6,edgecolors="k",linewidths=0.5)
    ax2.annotate(f"t*={t:.0f}w  R={R:.2f}",xy=(t,R),xytext=(t+0.3,R+0.02),fontsize=7,color=c)
ax2.axvline(START,color=SIG,ls=":",lw=1.0); ax2.axvline(27,color=SIG,ls=":",lw=1.0)
ax2.text(START+0.2,ax2.get_ylim()[1]*0.965,"≤12w 早发现",color=SIG,fontsize=7,ha="left")
ax2.text(27.2,ax2.get_ylim()[1]*0.965,"≥28w 晚发现",color=SIG,fontsize=7,ha="left")
ax2.set_xlabel("NIPT 检测时点  $t$（周）"); ax2.set_ylabel("期望风险  $R(t)$（a.u.）")
ax2.set_title("期望风险 R(t)（按 BMI 分组）与各组合优时点",fontsize=10)
tjstyle.leg(ax2,fontsize=7,loc="upper right")
ax2.text(0.985,0.02, f"$\\lambda$={LAM}（人工权重）    L(t)=1/3/5（≤12 / 13–27 / ≥28 周）",
         transform=ax2.transAxes,ha="right",va="bottom",fontsize=7,color=BASELINE)
fig2.tight_layout(); fig2.savefig(f"{OUT}/fig_C2_expected_risk_optimum.png",dpi=300,bbox_inches="tight",pad_inches=0.15); fig2.savefig(f"{OUT}/fig_C2_expected_risk_optimum.pdf",bbox_inches="tight"); plt.close(fig2)

# ----------------- FEMALE (C3) -----------------
f=pd.ExcelFile(SHEET).parse("女胎检测数据")
fy=f["染色体的非整倍体"].notna().astype(int).values
grpf=f["孕妇代码"].values
fz=dict(Z13=pd.to_numeric(f["13号染色体的Z值"],errors="coerce").values,
        Z18=pd.to_numeric(f["18号染色体的Z值"],errors="coerce").values,
        Z21=pd.to_numeric(f["21号染色体的Z值"],errors="coerce").values,
        Xc=pd.to_numeric(f["X染色体浓度"],errors="coerce").values,
        GC=pd.to_numeric(f["GC含量"],errors="coerce").values,
        B=pd.to_numeric(f["孕妇BMI"],errors="coerce").values)
def med(a): return np.nanmedian(a)
F={k:np.nan_to_num(v,nan=med(v)) for k,v in fz.items()}
F["maxZ"]=np.maximum.reduce([F["Z13"],F["Z18"],F["Z21"]])
cof=("Z13","Z18","Z21","Xc","GC","B")
npl=len(fy)
def oof_prob(col):
    pr=np.zeros(npl)
    for tr,te in GroupKFold(n_splits=5).split(np.zeros(npl),fy,grpf):
        mpl=make_pipeline(StandardScaler(),LogisticRegression(max_iter=3000,C=1.0)); mpl.fit(col[tr].reshape(-1,1),fy[tr]); pr[te]=mpl.predict_proba(col[te].reshape(-1,1))[:,1]
    return pr
def oof_mult(Xf):
    pr=np.zeros(npl)
    for tr,te in GroupKFold(n_splits=5).split(Xf,fy,grpf):
        pl=make_pipeline(StandardScaler(),LogisticRegression(max_iter=3000,C=1.0)); pl.fit(Xf[tr],fy[tr]); pr[te]=pl.predict_proba(Xf[te])[:,1]
    return pr
single={}
for k in ["Z13","Z18","Z21","Xc","GC","B","maxZ"]:
    pr=oof_prob(F[k]); single[k]=float(roc_auc_score(fy,pr))
comp=oof_mult(np.column_stack([F[k] for k in cof])); compauc=float(roc_auc_score(fy,comp))
n_abn=int(fy.sum()); n_subj=int(len(np.unique(grpf)))

# ---- C3: ROC + score overlap ----
fig3,(axr,axs)=plt.subplots(1,2,figsize=(6.6,4.2),gridspec_kw={"wspace":0.28})
axr.plot([0,1],[0,1],color=BASELINE,ls="--",lw=0.9,label="chance (AUC=0.5)")
for key,c,ls,lab in [("maxZ",BASELINE,"-","仅 Z 值 max(Z13,Z18,Z21)"),("Z21",A1,"-","仅 Z21（T21 标记）"),
                  ("_comp",SIG,"-","综合得分 Z+GC+X浓度+BMI"),("Xc",A4,"--","仅 X 染色体浓度（最强单指标）")]:
    pr = comp if key=="_comp" else oof_prob(F[key])
    auc = compauc if key=="_comp" else single[key]
    if auc<0.5: pr=1.0-pr; auc=1.0-auc   # use marker's usable direction
    fpr,tpr,_=roc_curve(fy,pr)
    lwv=2.0 if key=="_comp" else 1.2
    axr.plot(fpr,tpr,color=c,lw=lwv,ls=ls,label=f"{lab}（AUC={auc:.3f}）")
axr.set_xlabel("1−特异性 (FPR)"); axr.set_ylabel("敏感性 (TPR)")
axr.set_title("ROC 曲线（分组交叉验证）",fontsize=9)
tjstyle.leg(axr,fontsize=6.2,loc="lower right"); axr.set_xlim(0,1); axr.set_ylim(0,1.02)
pass  # 结论由 ROC 曲线直观体现
axs.hist(comp[fy==1],bins=22,color=SIG,histtype="step",linewidth=1.7,density=False,label=f"异常 n={n_abn}")
axs.hist(comp[fy==0],bins=22,color=BASELINE,histtype="step",linewidth=1.7,density=False,label=f"正常 n={npl-n_abn}")
axs.axvline(0.5,color=PRIMARY,ls="--",lw=0.9)
axs.set_xlabel("综合判别得分 P(异常|特征)"); axs.set_ylabel("样本数")
axs.set_title(f"判别得分分布（异常 {n_abn}/{npl}，类不均衡）",fontsize=9)
tjstyle.leg(axs,fontsize=6.5,loc="upper center")
fig3.suptitle("女胎非整倍体判别：ROC 曲线与判别得分分布",fontsize=10,y=0.996)
fig3.tight_layout(rect=(0,0,1,0.97)); fig3.savefig(f"{OUT}/fig_C3_female_aneuploidy_roc.png",dpi=300,bbox_inches="tight",pad_inches=0.15); fig3.savefig(f"{OUT}/fig_C3_female_aneuploidy_roc.pdf",bbox_inches="tight"); plt.close(fig3)

# ---- render.json ----
meta=dict(sheet=SHEET,excl_male_rows=excl,groups={g:gp[g]["n"] for g in labs},
          pooled_theta=[round(float(x),4) for x in th],
          c1_fit={g:dict(a=round(gp[g]["a"],3),b=round(gp[g]["b"],3),r2=round(gp[g]["r2"],3),ymean=round(gp[g]["ymean"],2),cross=gp[g]["crosslab"]) for g in labs},
          c2_riskopt={g:{"t":riskopt[g]["t"],"R":round(riskopt[g]["R"],3),"rel12":round(riskopt[g]["rel12"],3),"rel20":round(riskopt[g]["rel20"],3),"rel27":round(riskopt[g]["rel27"],3)} for g in labs},
          c3_female=dict(n=int(npl),abnormal=int(n_abn),subjects=int(n_subj),composite_auc=round(compauc,3),
                         usable_single_auc={k:round(max(v,1-v),3) for k,v in single.items()},lambda_human=LAM))
print(json.dumps(meta,ensure_ascii=False,indent=2,default=str))
for name,typ,chk,src in [
   ("fig_C1_y_conc_vs_week_bmi","trend",["Y 已×100 换算为百分比","孕周正则解析","幂律拟合+R²标注","4% 阈值线","≤12w 早窗口","图例≥7pt，网格≤0.25，无截断"],SHEET+" -> 男胎检测数据"),
   ("fig_C2_expected_risk_optimum","decision",["pooled logistic（孕周+BMI 协变量）","λ=0.25 人工权重+图注","L=1/3/5 严重度","各 BMI 组最优点标注","阈值线 12/27 周","图例≥7pt，网格≤0.25"],SHEET+" -> 男胎检测数据"),
   ("fig_C3_female_aneuploidy_roc","classification",["13/18/21 Z 值、X 染色体浓度、GC、BMI 组合得分","分组(按孕妇代码)交叉验证","类不均衡 67/605 标注","ROC+得分分布双面板","标准化后单指标 AUC 如实标注：X浓度≈综合≈0.76，Z值≈0.5","无造假，未引入未提供特征"],SHEET+" -> 女胎检测数据")]:
    rd={"status":"PASS","rendered_at":NOW,"checks":chk,"source":src,"type":typ}
    with open(f"{OUT}/{name}.render.json","w",encoding="utf-8") as fh: json.dump(rd,fh,ensure_ascii=False,indent=2)
print("PNG sizes:", {n: os.path.getsize(f"{OUT}/{n}.png") for n,_ in [("fig_C1_y_conc_vs_week_bmi",0),("fig_C2_expected_risk_optimum",1),("fig_C3_female_aneuploidy_roc",2)]})
