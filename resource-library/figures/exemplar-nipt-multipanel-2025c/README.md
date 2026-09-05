# 示范条目：NIPT 时点与胎儿异常判定（关系/决策/分类三型）——图审美模范

- **category**：figures
- **entry_id**：exemplar-nipt-multipanel-2025c
- **source**：resource-library/assets/problems/2025/C题/附件.xlsx（男胎 1082、女胎 605）+ 模型计算
- **year/contest**：2025 / 全国大学生数学建模竞赛 C 题
- **rights**：附件为竞赛资料(仅引用)；图与计算自写，MIT
- **tags**：关系/趋势、优化/决策、分类/判定、ROC、分组、矢量PDF

## 图型与用途
① Y 染色体浓度 vs 检测孕周(按 BMI 分组 + 4% 阈值线)【关系】；② 期望风险 R(t)(按 BMI 分组 + 各组合优时点)【决策】；③ 女胎非整倍体判别(ROC + 判别得分分布，类不均衡如实标注)【分类】。
用途：BMI 越高达标越迟、各 BMI 组合优时点与风险水平、女胎判别力集中在 X 染色体浓度而 Z 值失效——**结论由曲线/阈值/最优点/ROC 直白表达**。

## 为什么优秀（可迁移规则）
- 配色：主 #1A6FC4 + 分组 #4C9A2A/#E08214 + 阈值/异常 #B91C1C + 灰基线 #767676；不透明、不滥用红绿。
- 版式：分组着色+幂律拟合+4% 阈值线；风险曲线+最优点(▲)+12/27w 阈值线；左 ROC+右分布(step 轮廓防遮盖)；dpi=300、bbox tight、无网格。
- 字号：宋体中文+Times 类衬线+STIX；**符号(Y,w,BMI,R(t),t,AUC)全局加粗**；普通文字常规、按紧凑度调字号。
- 标注：黑边不透明图例；阈值线/区间/最优点/ROC 对角参考线/AUC；类不均衡与"λ 人工权重"如实注明。
- **可迁移规则**：统计/决策题 = 分组着色 + 阈值线/最优点/ROC 直白表达结论；类不平衡用 step 轮廓+标注，不写文字结论。

## 复现 check
python resource-library/figures/exemplar-nipt-multipanel-2025c/code/make_nipt_final.py（需 numpy/pandas/scipy/sklearn）。每图 render.json+.pdf+.png(300dpi)。

## 素养对照
绘图(分组/阈值/最优点/ROC，类不平衡用 step 轮廓) · 证据(真实附件+GroupKFold+AUC+67/605 如实) · 表达(结论由图) · 数学(power 拟合、pooled logistic、期望风险 R=(1-P)+λL、ROC) · 创新(风险最小化时点 + 组合 vs 单指标 ROC 对照) · 完整(关系/决策/分类覆盖)。

## 训练对照锚点
> ①分组着色并标阈值/最优点/ROC？②结论由图表达？③类不平衡/不确定性如实？④符号加粗？⑤无网格/入框？

## 完整性自检
- [ ] 含可迁移绘图规则  [ ] code/ 真实  [ ] 权利标注  [ ] 已登记  [ ] 每图 render.json+.pdf+.png

> 审美规则总纲见 resource-library/figures/topjournal-style/README.md；资源库访问按「Problem-Start Mode Gate」。
