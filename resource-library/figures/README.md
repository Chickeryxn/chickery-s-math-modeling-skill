# figures/ —— 优秀图

放**优秀图**（PNG/SVG/PDF），训练对照"绘图素养"。每条目二选一：

- **条目目录**（推荐，自包含）：`figures/<entry_id>/{README.md, content/(成品图), code/(生成脚本), data/(输入数据可选)}`
  - 参阅示范：`figures/example-rank-bar/`（`content/rank_bar.png` + `code/plot_rank_bar.py` + `data/rank_scores.csv` + 详细 `README.md`）。
- **扁平条目**（兼容）：`figures/<name>.png` + `figures/<name>.md` 同名前缀说明。

`content/`、`code/`、`data/`、`figures/`（若再嵌套）为**支持目录**，由 `scripts/resource_index.py` 归入各分类的 `supporting`，不会作为训练"条目"。

## 说明模板（条目 `README.md` 或扁平 `<name>.md` 按此填，字段分必填/选填）

```markdown
- **category**：figures
- **entry_id**：<唯一 id>
- **source**：<出处/链接>            （必填）
- **year/contest**：<年份/赛事>        （选填）
- **rights**：<有权使用/来源标注>       （必填）
- **tags**：<逗号分隔>                （选填）

## 图型与用途
- **图型**：排名条/分布对比/相关矩阵/时间序列/森林图/机制图/…
- **用途**：<支撑哪个结论>
- **数据来源**：<指向 data/ 或实验/冻结文件>       （必填）

## 为什么优秀（可迁移的绘图规则）
- **配色**：<主色 hex / 灰基线 / 方向色；为何不滥用红绿>
- **版式**：<多面板顺序 / 留白 / 字号 / figsize+dpi>
- **字号**：<最终尺寸下最小字号 ≥5pt 等>
- **标注**：<单位 / 图例 / 显著性 / 来源>
- **可迁移规则**：<绘此图的一条可复用的审美规则>     （必填）

## 复现 check
- 生成脚本：`code/xxx.py`（可选；真实条目给出运行命令）
- 渲染校验：`scripts/figure_render_audit.py .`（或至少目视：无裁剪/重叠、标注清晰）

## 素养对照（逐维，只填真正示范的维度）
- **绘图素养**：<配色/版式/标注规则>
- **证据素养**：<数值可溯源>
- **表达素养**：<图注讲清结论>
（可选其它维：数学/创新/完整）

## 训练对照锚点（training-reflector 用时）
> <拿你的解与这条对比时，检查哪几条、把最弱一条写进 reflection.md>

## 完整性自检清单
- [ ] 含"可迁移绘图规则"
- [ ] 引用的 code/data 路径真实存在
- [ ] 图有权使用并标注来源
- [ ] 已登记：`python scripts/resource_index.py .`
```
