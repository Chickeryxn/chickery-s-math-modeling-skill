# 示范条目：碳化硅/硅外延层厚度（干涉光谱 + 多光束判据）——图审美模范

- **category**：figures
- **entry_id**：exemplar-thickness-spectra-2025b
- **source**：resource-library/assets/problems/2025/B题/附件1..4.xlsx（实测光谱）+ 给定常数(n_SiC=2.6,n_Si=3.4) 计算
- **year/contest**：2025 / 全国大学生数学建模竞赛 B 题
- **rights**：附件为竞赛资料(仅引用)；图与计算自写，MIT
- **tags**：干涉光谱、薄膜测厚、两入射角、多光束、柱状hatch、矢量PDF

## 图型与用途
① SiC 反射光谱+干涉条纹(10°/15° 两面板，Δν̃ 箭头标注)；② 厚度反演(两入射角：级次-波数回归 + 误差棒点图)；③ 多光束判据 Si vs SiC(左调制曲线/右可见度·2次谐波比柱图)。
用途：条纹蕴含厚度、两角互检一致(差<1%)、Si 多光束需修正而 SiC 近两光束——**由图直白表达**。

## 为什么优秀（可迁移规则）
- 配色：主 #1A6FC4(SiC)/#B91C1C(Si·阈值)/#E08214(15°)/#767676(参考)；不透明、不滥用红绿。
- 版式：两面板共享波数轴；左大右小突出回归/对比；dpi=300；bbox tight；无网格。
- 字号：宋体中文+Times 类衬线+STIX；**物理符号(Δν̃,d,m,θ′,V,A1/A2)全局加粗**；轴标签/刻度达标。
- 标注：黑边不透明图例；干涉谷标记、Δν̃ 双向箭头；两角厚度+误差棒；**柱状 hatch 与图例一致(Si=//、SiC=..)**。
- **可迁移规则**：光谱题 = 两条件对照 + 周期/厚度定量标注 + 二级特征(谐波比)柱状量化；对比柱 hatch 与图例一致。

## 复现 check
python resource-library/figures/exemplar-thickness-spectra-2025b/code/render_figures_2025B.py（读附件 xlsx）。每图 render.json+.pdf+.png(300dpi)。

## 素养对照
绘图(两面板共享轴/回归+误差棒/hatch 与图例一致) · 证据(实测+两法/两角交叉验证) · 表达(结论由图) · 数学(2nd cosθ=mλ 反演/FFT 求频/谐波比) · 创新(用可见度+2次谐波比量化"多光束") · 完整(光谱→厚度→判据链)。

## 训练对照锚点
> ①两角度对照+定量标注？②回归/反演可视化且标差异？③二级特征量化现象？④柱/序列 hatch+图例一致、无网格、入框？⑤符号加粗？

## 完整性自检
- [ ] 含可迁移绘图规则  [ ] code/、数据引用真实  [ ] 权利标注  [ ] 已登记  [ ] 每图 render.json+.pdf+.png

> 审美规则总纲见 resource-library/figures/topjournal-style/README.md；资源库访问按「Problem-Start Mode Gate」。
