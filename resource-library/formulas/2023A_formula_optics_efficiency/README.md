# 公式：太阳几何与光学效率链

- **category**：formulas
- **entry_id**：2023A_formula_optics_efficiency
- **source**：自写提炼（2023 CUMCM A 题 A092/A127/A165/A175 的共性）。
- **tags**：太阳几何、有效轴、五项效率、DNI、场功率

## 公式
1) 太阳高度角/方位角：$sinalpha_s=cosdeltacosarphicosomega+sindeltasinarphi$，$cosgamma_s=rac{sindelta-sinalpha_ssinarphi}{cosalpha_scosarphi}$，$omega=rac{pi}{12}(ST-12)$，$sindelta=sinrac{2pi D}{365}sin(rac{2pi}{360}	imes23.45)$。
2) 法向直接辐射：$DNI=G_0[a+bexp(-c/sinalpha_s)]$（$G_0=1.366$ kW/m²，$a,b,c$ 与海拔 $H$(km) 有关）。
3) 光学效率链：$eta=eta_{sb},eta_{cos},eta_{at},eta_{trunc},eta_{ref}$（$eta_{ref}=0.92$，$eta_{at}=0.99321-0.0001176,d_{HR}+1.97	imes10^{-8}d_{HR}^2$，$d_{HR}le1000$）。
4) 场功率：$E_{field}=DNIsum_i A_ieta_i$。
5) 反射定律/法向：$ec n=(-ec I+ec R)/|-ec I+ec R|$；$cosalpha_h=n_z$。
（符号：$alpha_s,gamma_s$=太阳高度/方位角；$delta,omega,arphi$=赤纬/时角/纬度；$eta$=光学效率，下标 sb/cos/at/trunc/ref=阴影遮挡/余弦/大气透射/截断/反射；$A_i$=镜面积；$d_{HR}$=镜心到集热器中心距离。）

## 符号与前提
- **符号**：见上式；角度 rad/°，长度 m，功率 kW 或 MW。
- **适用前提**：光-镜-接收类问题；把锥形太阳光当非平行光束；用坐标变换+取点近似覆盖真实镜面。

## 推导链
1. 由地点/日期/时刻算太阳天球坐标（高度/方位/赤纬/时角）。
2. 反射定律定镜面法向（主光线过集热器中心）。
3. 逐项算五种效率（解析项 + 几何投影/MC 项）。
4. 乘 DNI 加总得场功率；对多时刻取平均得年均。

## 数值算例
- 2023A：给定 6×6m、安装高 4m、1745/1744 面，Q1 得 年均光学效率约 0.49~0.63、功率 24~38.3MW、单位面积约 0.38~0.61 kW/m²（各篇因口径/取点不同而异）。示例仅示意，非唯一答案。

## 陷阱
- 单位/口径：$d_{HR}$ 用 m、海拔用 km（$a,b,c$ 的 H 是 km）；E_field 单位 kW vs MW；方位/时角符号约定（北纬/东经、ST 当地时）。
- 平均口径：$E[prodeta_k]$ 与 $prod E[eta_k]$ 不相等；月均=每月21日5时点，年均是否按日照积分须说明。
- 符号复用（H=镜高/海拔；$gamma$ 两义）、把塔径简化为集热器同径（几何过简化）会失真。

## 可迁移
- 同类题：光热/光伏/光学/辐射传热。
- 同思想异解法：太阳几何换库/近似；效率链换成其它乘性损耗；DNI 换成实测/其它模型。

## 素养对照（可迁移规则）
- **数学素养**：前提声明、几何律、单位/口径一致。
- **证据素养**：数值算例可复核；对平均口径与几何简化诚实。

## 训练对照锚点（training-reflector 用时）
> 拿你的光学建模与这条对比：太阳几何/反射律是否正确？单位与平均口径是否一致？是否诚实标注几何简化？把最弱一条写进 reflection.md。

## 完整性自检清单
- [x] 含公式（LaTeX）+ 符号说明
- [x] 含"适用前提"与"推导链"
- [x] 含数值算例
- [x] 含"陷阱"（单位/口径/平均/符号复用/几何简化）
- [ ] 已登记：`python scripts/resource_index.py .`