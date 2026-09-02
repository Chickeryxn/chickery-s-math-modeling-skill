# 数学建模素养资源库（resource-library/）

> 用途：**训练模式的"模范素材库"**。用户拉取项目后，把优秀的论文、解题思路、图、公式、表格等放入对应子目录；agent 在"闭卷解题→开卷对照学习"训练闭环中把这些素材当作**审美与素养标杆**（不照抄，只学素养）。
> 使用前提：本库只用于 `docs/training.md` 的训练模式；正常竞赛流程（G1–G6）**不读取本库**。

## 目录结构（条目目录 + 支持目录）

每条训练条目是一个**独立目录**（自包含、易扩容），也兼容旧的"扁平 素材+同名说明"：

```text
resource-library/
├── papers/<entry_id>/    # {README.md, content/(论文), code/(复现脚本), figures/(可选)}
├── ideas/<entry_id>/     # {README.md, code/(演示/求解脚本可选)}
├── figures/<entry_id>/   # {README.md, content/(成品图), code/(生成脚本), data/(可选)}
├── formulas/<entry_id>/  # {README.md, content/(公式), code/(数值验证可选)}
├── tables/<entry_id>/    # {README.md, content/(表格), code/(生成脚本), data/(原始数据)}
└── assets/               # {problems/(赛题), data/, code/, figures/}
```

- 条目目录里的 `README.md` 是**入口说明**（按各类 README 内嵌的详细模板填写）；其余文件是支持物。
- `content/`、`code/`、`data/`、`figures/` 为**支持目录**（成品、生成脚本、输入数据、渲染图），由 `scripts/resource_index.py` 归入各分类的 `supporting`，不会作为训练"条目"。
- 示例：`figures/example-rank-bar/`（真实 PNG + `plot_rank_bar.py` + `rank_scores.csv` + 详细说明）——绘图类条目既有"放图片的文件夹"也有"放代码的文件夹"。

## 条目说明（详细模板）

每类 README 内嵌一份**详细模板**（分必填/选填，含：公共元数据 `category/entry_id/source/year/contest/rights/tags`、类别专属字段、**素养对照**（对齐训练 6 维评分卡）、**训练对照锚点**、**完整性自检清单**）。条目 `README.md` 按模板填写，`example*.md` 为填好值的演示范本。

放入素材的规则：

1. 每条 = 一个条目目录（或同一前缀的扁平文件集合），说明用对应详细模板。
2. 说明至少覆盖模板中的**必填项**（来源/权利、用途或亮点、可迁移规则、自检清单）。
3. 版权：只放你有权使用的素材并标注来源。
4. 登记：放入后用 `python scripts/resource_index.py .` 重建 `index.json`（`--check` 校验一致性；`index.json` 为机器生成，勿手改，`schema_version 2`）。

## 训练模式如何使用本库

1. `training-solver`（闭卷）：**解题阶段禁止读取本库**——独立思考在先。
2. `training-reflector`（开卷）：解完后按目标素养打开对应类别，逐项对比（用各条目"训练对照锚点"作检查清单），产出"素养学习报告"（差距 + 可迁移要点，自写不抄）。
3. `training-auditor`：6 维素养评分卡（数学/创新/绘图/表达/证据/完整）初评，由你终评。
4. 多轮结果汇总后由你挑选"逼近方向"，反馈下一轮侧重。

详见 [`docs/training.md`](../docs/training.md)。

## 示例模板说明

各子目录预置了**自写的详细示例**（`example*.md` 为扁平演示；`figures/example-rank-bar/` 为条目目录演示），用于演示完整格式：按模板结构填入你自己的优秀素材即可；不需要的示例可删除。
