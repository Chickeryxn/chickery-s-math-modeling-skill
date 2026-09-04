# -*- coding: utf-8 -*-
"""2025 国赛 A 题 烟幕干扰弹投放 —— 结论先行签名图(干净复现版; F1/F2 已修复文字遮挡/重叠)。数值由题面常数计算(无附件数据), 离线运行。"""
import numpy as np, matplotlib, warnings
matplotlib.use("Agg"); import matplotlib.pyplot as plt
import tjstyle
from mpl_toolkits.mplot3d import Axes3D
warnings.filterwarnings("ignore")

G,V_M=9.8,300.0
M1=np.array([20000.,0.,2000.]); DECOY=np.array([0.,0.,0.])
TRUE_XY,TRUE_R,TRUE_H=200.0,7.0,10.0
FY1=np.array([17800.,0.,1800.])
CLOUD_R,SINK,LIFE=10.0,3.0,20.0
V_D,DROP_T,BURST_T=120.0,1.5,5.1
U_MISS=(DECOY-M1)/np.linalg.norm(DECOY-M1)
C_MAIN="#1A6FC4"; C_BASE="#767676"; C_HL="#B91C1C"; C_A1="#4C9A2A"; C_A2="#E08214"; C_A3="#8E44AD"; C_A4="#0F9D58"; C_GRID="#B9B9B9"
BBOX=dict(boxstyle="round,pad=0.16",fc="white",ec="none",alpha=0.85)
SAVE="results/training/round1/2025A/figures/"

def missile(t): return M1+V_M*U_MISS*t
def drone(t,v=V_D): return FY1+v*np.array([-1.,0.,0.])*t
def burst_point(v,drop_t,burst_t,lateral_y=0.0):
    D=drone(drop_t,v).copy(); D[1]+=lateral_y; dt=burst_t-drop_t
    return D+v*np.array([-1.,0.,0.])*dt+np.array([0.,0.,-0.5*G*dt**2])
Z_AXIS=np.linspace(0.,TRUE_H,41)[None,:,None]
def obsc_dur(B,t_burst,dt=0.05):
    ts=np.arange(t_burst,t_burst+LIFE+1e-9,dt); t=ts[:,None,None]
    A=np.concatenate([np.zeros_like(Z_AXIS),TRUE_XY*np.ones_like(Z_AXIS),Z_AXIS],axis=-1)
    C=B-np.array([0,0,SINK])*(t-t_burst); M=M1+V_M*U_MISS*t
    d=A-M; pm=C-M; tp=np.clip(np.sum(pm*d,axis=-1)/np.sum(d*d,axis=-1),0.,1.)[...,None]
    dist=np.linalg.norm(C-(M+tp*d),axis=-1).min(axis=1); ob=(dist<=CLOUD_R)
    return ob.sum()*dt, ts, ob
def best_over_delay(v,lat):
    best=0.;bt=None
    for burst_t in np.arange(3.0,6.6,0.25):
        d=obsc_dur(burst_point(v,DROP_T,burst_t,lat),burst_t)[0]
        if d>best: best=d;bt=burst_t
    return best,bt

def fig_F1():
    tm=8.7; Ms=missile(tm); B=burst_point(V_D,DROP_T,BURST_T); drop=drone(DROP_T)
    Ccur=B-np.array([0,0,SINK])*(tm-BURST_T); TGT=np.array([0.0,TRUE_XY,TRUE_H/2])
    fig=plt.figure(figsize=(7.4,4.9),dpi=240); ax=fig.add_subplot(111,projection="3d")
    ax.set_xlim(16740,18020); ax.set_ylim(-60,220); ax.set_zlim(1600,1870)
    xm=np.linspace(18020,16740,90); tt=(20000-xm)/(V_M*abs(U_MISS[0])); Mt=np.array([missile(t) for t in tt])
    ax.plot(Mt[:,0],Mt[:,1],Mt[:,2],color=C_BASE,lw=1.8,marker=">",markevery=12,ms=4.5,label="导弹 M(t)·M1→假目标")
    ax.scatter(Mt[0,0],0,Mt[0,2],color=C_BASE,s=22,marker=">")
    ax.text(Mt[0,0]-260,-40,1795,"M1 来向",fontsize=6.5,color=C_BASE,bbox=BBOX)
    td=np.linspace(0,DROP_T,20); Dr=np.array([drone(t) for t in td])
    ax.plot(Dr[:,0],Dr[:,1],Dr[:,2],color=C_A2,lw=2.2,marker="s",markevery=6,ms=5,label="无人机 FY1·等高 z=1800 m")
    ax.scatter(*FY1,color=C_A2,s=24,marker="s")
    ax.plot([drop[0],B[0]],[drop[1],B[1]],[drop[2],B[2]],color=C_A4,lw=1.5,ls="--",label="投放→起爆(重力下落)")
    ax.scatter(*drop,color=C_A4,s=34,marker="o")
    ax.text(drop[0]-320,drop[1]-25,drop[2]+15,"投放点 t=1.5 s",fontsize=6.5,color=C_A4,bbox=BBOX)
    ax.scatter(*B,color=C_A3,s=46,marker="*")
    dirn=TGT-Ms; dirn=dirn/np.linalg.norm(dirn); end=Ms+dirn*1000
    ax.plot([Ms[0],end[0]],[Ms[1],end[1]],[Ms[2],end[2]],color=C_HL,lw=2.2,label="视线 M(t)→真目标")
    ax.scatter(*Ms,color=C_HL,s=42,marker="o")
    ax.text(Ms[0]-260,Ms[1]+35,Ms[2]+40,"导弹 M(8.7 s)",fontsize=6.5,color=C_HL,bbox=BBOX)
    u=np.linspace(0,2*np.pi,36); v=np.linspace(0,np.pi,22)
    def sph(c,r,color,al,s):
        xs=r*np.outer(np.cos(u),np.sin(v)); ys=r*np.outer(np.sin(u),np.sin(v)); zs=r*np.outer(np.ones_like(u),np.cos(v))
        ax.plot_surface(xs+c[0],ys+c[1],zs+c[2],color=color,alpha=al,linewidth=0,rstride=1,cstride=1,shade=True)
        ax.plot_wireframe(xs+c[0],ys+c[1],zs+c[2],color=color,linewidth=0.35,alpha=s,rstride=3,cstride=3)
    sph(Ccur,CLOUD_R,C_MAIN,1.0,1.0); ax.scatter(*Ccur,color=C_MAIN,s=80,marker="*",zorder=6,label="烟幕云团 r=10 m·下沉3 m/s")
    ax.text(Ccur[0]-430,Ccur[1]+85,Ccur[2]+55,"烟幕云团\n(r=10 m, 下沉 3 m/s)",fontsize=6.5,color=C_MAIN,bbox=BBOX)
    ax.text(end[0]+60,end[1]+30,end[2]+40,"→ 真目标 (0,200,0)\n(沿 +y 偏出视中线路)",fontsize=6.5,color=C_HL,bbox=BBOX)
    ax.xaxis.labelpad=8; ax.yaxis.labelpad=8; ax.zaxis.labelpad=8
    ax.set_xlabel("x (m)",fontsize=9.5); ax.set_ylabel("y (m, 横向放大示意)",fontsize=9.5); ax.set_zlabel("z (m)",fontsize=9.5)
    ax.tick_params(labelsize=8)
    ax.set_title("烟幕干扰几何遮蔽示意（M1 · FY1 · 真目标 · 烟幕云团）",fontsize=9,color="#111",pad=6)
    ax.view_init(elev=18,azim=-62); ax.set_box_aspect((1.0,0.9,0.55))
    ax.grid(False)
    tjstyle.leg(ax,fontsize=6.8,loc="upper right",ncol=2)
    plt.tight_layout(); out=SAVE+"2025A_F1_geometry3d.png"
    fig.savefig(out,dpi=300,bbox_inches="tight"); fig.savefig(out.replace(".png",".pdf"),bbox_inches="tight")
    plt.close(fig); return out

def fig_F2():
    dels=np.arange(2.0,6.05,0.05)
    durs=np.array([obsc_dur(burst_point(V_D,DROP_T,DROP_T+dd),DROP_T+dd)[0] for dd in dels])
    fig=plt.figure(figsize=(6.9,4.4),dpi=240); ax=fig.add_subplot(111)
    ax.plot(dels,durs,color=C_MAIN,lw=2.0,marker="o",ms=2.6,label="有效遮蔽时长")
    ipk=int(np.argmax(durs)); pk_d,pk_v=dels[ipk],durs[ipk]
    iq1=int(np.argmin(np.abs(dels-(BURST_T-DROP_T)))); q1_d,q1_v=dels[iq1],durs[iq1]
    ax.axvline(pk_d,color=C_A2,ls="--",lw=1.1); ax.axhline(pk_v,color=C_A2,ls=":",lw=1.1)
    ax.plot([q1_d],[q1_v],marker="o",ms=9,color=C_HL,zorder=5,label=f"Q1 给定延迟(3.6 s) → {q1_v:.2f} s")
    ax.annotate(f"最优延迟 ≈ {pk_d:.1f} s\n时长 ≈ {pk_v:.2f} s",xy=(pk_d,pk_v),xytext=(4.78,max(durs)+1.15),
                color=C_A2,fontsize=7.6,arrowprops=dict(arrowstyle="->",color=C_A2,lw=1.0,shrinkA=3,shrinkB=3),
                bbox=dict(boxstyle="round,pad=0.12",fc="none",ec="none"))
    ax.annotate(f"Q1: {q1_d:.2f} s → {q1_v:.2f} s",xy=(q1_d,q1_v),xytext=(2.5,0.15),
                color=C_HL,fontsize=7.6,arrowprops=dict(arrowstyle="->",color=C_HL,lw=1.0,shrinkA=3,shrinkB=3),
                bbox=dict(boxstyle="round,pad=0.12",fc="none",ec="none"))
    ax.set_xlabel("起爆延迟 (投放后时间, s)"); ax.set_ylabel("有效遮蔽时长 (s)")
    ax.set_title("有效遮蔽时长 vs 起爆延迟（Q1 配置与最优点）",fontsize=9,color="#111")
    ax.set_xlim(2.0,6.0); ax.set_ylim(0,max(durs)+1.9)
    tjstyle.leg(ax,fontsize=7.0,loc="upper left")
    out=SAVE+"2025A_F2_burstdelay_decision.png"; fig.savefig(out,dpi=300,bbox_inches="tight"); fig.savefig(out.replace(".png",".pdf"),bbox_inches="tight"); plt.close(fig); return out

def fig_F3():
    speeds=np.arange(70,141,10); lats=np.arange(-30,31,2); Z=np.zeros((len(speeds),len(lats)))
    for i,v in enumerate(speeds):
        for j,lat in enumerate(lats): Z[i,j]=best_over_delay(v,lat)[0]
    fig=plt.figure(figsize=(6.6,4.4),dpi=240); ax=fig.add_subplot(111); lev=np.arange(0,4.3,0.3)
    cs=ax.contourf(lats,speeds,Z,levels=lev,cmap="viridis",extend="both"); c=ax.contour(lats,speeds,Z,levels=lev,colors="white",linewidths=0.5)
    ax.clabel(c,inline=True,fontsize=6.0,fmt="%.0f")
    jmax=np.unravel_index(np.argmax(Z),Z.shape)
    ax.scatter(lats[jmax[1]],speeds[jmax[0]],marker="*",s=120,color=C_HL,zorder=6,label=f"最优: v={speeds[jmax[0]]:.0f} m/s, 偏移={lats[jmax[1]]:+d} m, {Z[jmax]:.2f} s")
    ax.scatter([0],[V_D],marker="o",s=70,color=C_HL,zorder=6,label="Q1 配置 (v=120, 偏移=0)")
    cb=fig.colorbar(cs,ax=ax,pad=0.02); cb.set_label("最大有效遮蔽时长 (s)",fontsize=7); cb.ax.tick_params(labelsize=6)
    ax.set_xlabel("弹点横向偏移 (m)  (+y 朝真目标一侧)"); ax.set_ylabel("无人机速度 (m/s)")
    ax.set_title("最大有效遮蔽时长（无人机速度 × 弹点横向偏移）",fontsize=9,color="#111")
    tjstyle.leg(ax,fontsize=7.0,loc="upper right")
    out=SAVE+"2025A_F3_speed_offset_sensitivity.png"; fig.savefig(out,dpi=300,bbox_inches="tight"); fig.savefig(out.replace(".png",".pdf"),bbox_inches="tight"); plt.close(fig); return out

def fig_F1_2d():
    """Two INDEPENDENT problem-focused 2D views (markers/colors/legend consistent with the 3D figure; NOT projections)."""
    tm=8.7; Ms=missile(tm); B=burst_point(V_D,DROP_T,BURST_T); drop=drone(DROP_T)
    Ccur=B-np.array([0,0,SINK])*(tm-BURST_T); TGT=np.array([0.0,TRUE_XY,TRUE_H/2])
    fig,(axf,axs)=plt.subplots(1,2,figsize=(11.4,4.4))
    # ---------- (a) FRONT: x-z vertical profile (altitudes + cloud sinking) ----------
    axf.scatter([drop[0]],[1800],color=C_A2,s=34,marker="o",label="无人机 FY1·z=1800 m")
    axf.plot([Ms[0],drop[0]],[Ms[2],1800],color=C_A2,lw=2.0,marker="s",markevery=3,ms=5,label="无人机轨迹")
    axf.scatter([Ms[0]],[Ms[2]],color=C_BASE,s=60,marker=">",label="导弹 M(8.7s)")
    axf.plot([drop[0],B[0]],[1800,B[2]],color=C_A4,lw=1.5,ls="--",label="投放→起爆(重力下落)")
    axf.add_patch(plt.Circle((Ccur[0],Ccur[2]),CLOUD_R,fill=True,color=C_MAIN,alpha=1.0,zorder=3))
    axf.scatter(Ccur[0],Ccur[2],color=C_MAIN,s=120,marker="*",zorder=4,label="烟幕云团(起爆后)")
    C2=B-np.array([0,0,SINK])*(tm+2.0-BURST_T)
    axf.add_patch(plt.Circle((C2[0],C2[2]),CLOUD_R,fill=False,color=C_MAIN,ls="--",zorder=3))
    axf.annotate("",xy=(C2[0],C2[2]),xytext=(Ccur[0],Ccur[2]),arrowprops=dict(arrowstyle="->",color=C_MAIN,lw=1.3))
    axf.text(Ccur[0]+90,Ccur[2]-16,"下沉箭头: 3 m/s",fontsize=6.8,color=C_MAIN)
    axf.plot([Ms[0],Ms[0]-700],[Ms[2],Ms[2]-360],color=C_HL,ls="--",lw=1.8,label="视线→真目标(下行, x=0)")
    axf.set_xlim(16800,17700); axf.set_ylim(1560,1900)
    axf.set_xlabel("x (m)",fontsize=9.5); axf.set_ylabel("z (m, 高度)",fontsize=9.5)
    axf.set_title("(a) 正视图·x–z 铅垂剖面：云团 3 m/s 下沉, 20 s 内需持续覆盖视线",fontsize=9.5,fontweight="bold")
    axf.tick_params(labelsize=8); axf.grid(False); tjstyle.leg(axf,fontsize=6.6,loc="upper left")
    # ---------- (b) SIDE: y-z plane (the +y offset crux) ----------
    axs.plot([0,0],[0,TRUE_H],color="#767676",ls=":",lw=0.9)
    axs.plot([TRUE_XY,TRUE_XY],[0,TRUE_H],color=C_HL,lw=2.2,label=f"真目标 y=+{TRUE_XY:.0f} m, 高10 m")
    axs.plot([Ms[1],TGT[1]],[Ms[2],TGT[2]],color=C_HL,ls="--",lw=1.8,label="视线 M(8.7s)→真目标")
    axs.scatter([Ms[1]],[Ms[2]],color=C_BASE,s=60,marker=">",label="导弹 M(8.7s)")
    axs.scatter([Ccur[1]],[Ccur[2]],color=C_MAIN,s=120,marker="*",zorder=4,label="烟幕云团中心(下沉3 m/s)")
    axs.add_patch(plt.Circle((Ccur[1],Ccur[2]),CLOUD_R,fill=True,color=C_MAIN,alpha=1.0))
    ylos=TRUE_XY*(Ms[0]-Ccur[0])/Ms[0]
    axs.plot([Ms[1],ylos],[Ms[2],Ccur[2]],color="#B91C1C",lw=1.1,ls=":")
    axs.text(2,Ccur[2]+8,f"云团y≈{Ccur[1]:.0f} vs 视线y≈{ylos:.1f} m",fontsize=6.8,color="#B91C1C")
    axs.set_xlim(-20,260); axs.set_ylim(1560,1900)
    axs.set_xlabel("y (m, 横向 / 侧向偏置)",fontsize=9.5); axs.set_ylabel("z (m, 高度)",fontsize=9.5)
    axs.set_title("(b) 侧视图·y–z 平面：真目标偏 +y, 云团须偏向 +y 才能遮蔽",fontsize=9.5,fontweight="bold")
    axs.tick_params(labelsize=8); axs.grid(False); tjstyle.leg(axs,fontsize=6.6,loc="upper left")
    fig.tight_layout(); out=SAVE+"2025A_F1_view_2d.png"
    fig.savefig(out,dpi=300,bbox_inches="tight"); fig.savefig(out.replace(".png",".pdf"),bbox_inches="tight"); plt.close(fig); return out

print("F1:",fig_F1()); print("F1_2d:",fig_F1_2d()); print("F2:",fig_F2()); print("F3:",fig_F3()); print("done")
