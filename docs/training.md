# 素养训练模式手册（Training Mode）

> 目标：让 agent 在**不看范例**的情况下多次解题，解完后与模范资源库做**审美对比与素养学习**，最终通过 6 维审核 + 你挑选"逼近方向"完成训练。
> 核心原则：**先独立思考，后对照学习；不照抄范例，只学素养。** 这与你自己的学习方式同构。

## 一、资源库（resource-library/）

- 6 类子目录：`papers/`（优秀论文）、`ideas/`（解题思路卡片）、`figures/`（优秀图）、`formulas/`（公式）、`tables/`（表格）、`assets/`（赛题/其它）。
- 放入素材的格式与登记规则见 `resource-library/README.md` 与各类 README。
- 登记：`python scripts/resource_index.py .` 重建 `index.json`；`--check` 校验一致性。

## 二、训练闭环（每轮 `roundN` → `results/training/roundN/`）

```
阶段A 闭卷解题（training-solver）
  读取 planning/training_config.json（题源/目标素养/轮次）
  【禁读】closed 模式解题阶段不得打开 resource-library/（含 index.json 之外的任何条目）
  按现有门禁流程产出完整解答：方法卡/风险探针/代码/run_summary/结果/论文段
  → results/training/roundN/solution/

阶段B 开卷对照学习（training-reflector）
  解完后才按目标素养打开 resource-library/ 对应类别
  逐项对比 → 素养学习报告 L_i（差距 + 可迁移要点，自写不抄）
  → results/training/roundN/reflection.md

阶段C 多维审核 + 挑选（training-auditor + training_scorecard.py）
  机械层：model_quality_gate / claim_coverage / abstract_checker / ai_trace_checker / leakage_check / figure_consistency_check / section_structure_check
  素养层：6 维评分卡（agent 初评 + 你终评 1–5）
  → results/training/roundN/scorecard.json + 多轮汇总 results/training/summary.json
  你挑选"逼近方向"→ 更新 training_config 侧重 → 下一轮
```

## 三、6 维素养定义（评分卡维度）

| 维度 | 考察 | 机械锚点 |
|---|---|---|
| mathematical 数学素养 | 模型选择/抽象合理性、公式严谨、数值稳健 | model_quality_gate、risk probe |
| innovation 创新素养 | 多范式视角、简化阶梯、独特切入点 | 方法卡"为什么不走另一范式" |
| figure 绘图素养 | 顶刊审美（配色/版式/标注）、图-结论一致 | publication-gallery、figure_consistency_check |
| expression 表达素养 | 结构契合、逻辑链、语言凝练无 AI 腔 | paper-skeleton、section_structure_check、ai_trace_checker |
| evidence 证据素养 | 数字可溯源、不确定性、基线公平 | claim_coverage、frozen 宏、latex_assembly 扫描 |
| completeness 完整素养 | 问题覆盖、结论可辩护、局限诚实 | claim_coverage、abstract_checker 结论覆盖 |

每维评分：agent 自评（1–5 + 证据路径）→ 你终评（1–5 + 一句话）→ 与范例对照评语（reflection 里）。

## 四、开始一次训练

1. 放赛题：`resource-library/assets/problems/<题目>.txt`（或改 `problem_source`）。
2. 放/更新范例素材（papers/ideas/figures/formulas/tables），跑 `resource_index.py .`。
3. 核对 `planning/training_config.json`（mode/rounds/target_skills）。
4. 让 agent 执行 `training-solver`（自动进入三阶段闭环）；每轮后你审 `reflection.md` 与 `scorecard.json`，在 `summary.json` 的挑选环节给出方向。

## 五、规则与边界

- **closed 隔离**：`training-solver` 技能规则与 `training_config.json` 的 `closed_phase_forbidden_paths` 双声明禁读；执行时人工监督。
- **不污染竞赛流程**：训练产物全部在 `results/training/`；正常竞赛（G1–G6）不读取资源库与训练结果。
- **不预设"标准答案"**：资源库是素养标杆，不是答案库；解题不要求与范例一致。
- **版权**：只放有权使用的素材并标注来源。
