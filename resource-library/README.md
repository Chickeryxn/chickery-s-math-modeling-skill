# 数学建模素养资源库（resource-library/）

> 用途：**训练模式的"模范素材库"**。用户拉取项目后，把优秀的论文、解题思路、图、公式、表格等放入对应子目录；agent 在"闭卷解题→开卷对照学习"训练闭环中把这些素材当作**审美与素养标杆**（不照抄，只学素养）。
> 使用前提：本库只用于 `docs/training.md` 的训练模式；正常竞赛流程（G1–G6）**不读取本库**。

## 目录结构

```text
resource-library/
├── README.md      # 本文件
├── index.json     # 机器可读清单（scripts/resource_index.py 自动生成，勿手改）
├── papers/        # 优秀论文：PDF/MD + 亮点自评说明
├── ideas/         # 优秀创新解题思路：方法-风险-教训卡片（MD）
├── figures/       # 优秀图：PNG/SVG + 同名字段说明（用途/配色/版式/为什么好）
├── formulas/      # 优秀公式：LaTeX 片段 + 说明（推导/适用/陷阱）
├── tables/        # 优秀表格：三线表/描述 + 说明
└── assets/        # 其它素材（赛题文件、题解范例、可视化数据等）
```

## 放入素材的规则（每类 README 有详细格式）

1. **一个条目 = 素材文件 + 同名前缀的说明**（如 `papers/2024C_entropy_topsis.pdf` + `papers/2024C_entropy_topsis.md` 说明）。
2. 说明至少包含：**来源/用途/为什么优秀/可迁移要点**（为 `training-reflector` 提供对照锚点）。
3. 版权：只放你有权使用的素材；标注来源。
4. 登记：放入后用 `python scripts/resource_index.py .` 重建 `index.json`（并 `--check` 校验一致性）。

## 训练模式如何使用本库

1. `training-solver`（闭卷）：**解题阶段禁止读取本库**——独立思考在先。
2. `training-reflector`（开卷）：解完后按目标素养打开对应类别，逐项对比，产出"素养学习报告"（差距 + 可迁移要点，自写不抄）。
3. `training-auditor`：6 维素养评分卡（数学/创新/绘图/表达/证据/完整）初评，由你终评。
4. 多轮结果汇总后由你挑选"逼近方向"，反馈下一轮侧重。

详见 [`docs/training.md`](../docs/training.md)。

## 示例模板说明

各子目录预置了**自写的示例卡片模板**（非真实竞赛内容），用于演示格式：按模板结构填入你自己的优秀素材即可；不需要的模板可删除。
