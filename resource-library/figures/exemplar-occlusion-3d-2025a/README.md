# 示范条目：烟幕干扰弹几何遮蔽（3D 侧向 + 独立 2D 视图）——图审美模范

- **category**：figures
- **entry_id**：exemplar-occlusion-3d-2025a
- **source**：2025 国赛 A 题题面常数建模计算（自写）；成图见 content/（png+pdf+render.json），代码见 code/
- **year/contest**：2025 / 全国大学生数学建模竞赛 A 题
- **rights**：本条目自写自绘，MIT；无第三方图片
- **tags**：3D 几何、运动学、遮蔽、2D 正/侧视图、矢量PDF

## 图型与用途
① 3D 几何遮蔽(侧向 elev=18,azim=-62)；② 独立二维正视图(x–z 铅垂：高度+云团下沉)与侧视图(y–z：真目标偏 +y、云团须偏向 +y)；③ 有效遮蔽时长 vs 起爆延迟(单峰+最优点)；④ 遮蔽时长 vs 速度×横向偏移(等高线)。
用途：表达"云团须落在导弹 M(t)→真目标视线上(真目标 y=+200m)"；单发遮蔽峰值≈4s、对速度不敏感、对横向偏移极敏感——**结论均由图直白表达，不写文字**。

## 为什么优秀（可迁移规则）
- 配色：主 #1A6FC4 / 灰基线 #767676 / 方向 #B91C1C / 辅助 #4C9A2A·#E08214·#8E44AD·#0F9D58；饱和不透明、不滥用红绿。
- 版式：3D 侧向避免正对；正/侧视图为**独立设计的二维投影**(图标与 3D 统一)；bbox_inches='tight' 内容不越框；dpi=300。
- 字号：中文宋体、西文/数字 Times 类衬线、数学 STIX；**物理/英文字母全局加粗**；普通文字常规；3D 轴标签放大并贴近坐标轴(labelpad=8)。
- 标注：黑边不透明图例在坐标区内；语义化标记(导弹 >、无人机 s、云团 *)；阈值/最优/几何位置即结论。
- **可迁移规则**：几何/运动学题 = 3D 侧向主图 + 独立 2D 正/侧视图 + 结论由几何位置表达。

## 复现 check
python resource-library/figures/exemplar-occlusion-3d-2025a/code/make_2025A_figs_fixed.py（需 numpy/matplotlib；tjstyle.py 同目录）。每图 render.json(status=PASS)+.pdf+.png(300dpi)。

## 素养对照
绘图(配色/语义标记/多视角/无网格/入框) · 证据(题面常数可溯源) · 表达(结论由图) · 数学(视线-云球相交/最优延迟) · 创新(偏+y 遮蔽洞见+敏感性) · 完整(3D+2D+决策+灵敏度)。

## 训练对照锚点
> ①3D 是否侧向？②是否有独立 2D 正/侧视图且图标与 3D 一致？③标记语义化？④结论是否由图表达？⑤字号/图例/网格/越界？

## 完整性自检
- [ ] 含可迁移绘图规则  [ ] code/ 真实存在  [ ] 权利标注  [ ] 已 resource_index 登记  [ ] 每图 render.json+.pdf+.png

> 审美规则总纲见 resource-library/figures/topjournal-style/README.md；资源库访问按 AGENTS.md「Problem-Start Mode Gate」(训练=禁看/非训练=参考)。
