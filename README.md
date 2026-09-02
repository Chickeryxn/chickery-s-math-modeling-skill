# 数学建模竞赛 AI 工作流技能库

[简体中文](README.md) | [English](README.en.md)

**Math Modeling Skill** — 面向 CUMCM / MCM/ICM 等数学建模竞赛的 Agent 技能库与可执行工作流框架：32 个 Claude/Codex/DSH 技能 + 28 个纯标准库脚本，把「AI 写代码、人类做决策、一切可复现可审计」变成机器可强制的过程契约。

| 徽章 | 值 |
|---|---|
| 许可 | [MIT](LICENSE) |
| 版本 | 0.7.1（插件 manifest 同步） |
| 运行环境 | Python 3.10+（仅标准库，无第三方依赖） |
| 平台 | Windows / Linux / macOS |
| 测试 | 171 个用例，`python scripts/run_tests.py` 全绿 |

## 这是什么

数学建模竞赛允许 AI 辅助，但直接让 Agent「自由发挥」会带来两类风险：**AI 越权替你做建模判断**（选方法、编理由、下结论），以及**结果不可信**（代码没跑、数字无出处、版本过期无法核对）。

本项目把一次竞赛拆成 **6 个门禁关卡（G1–G6）**，每过一关必须留下可核对的证据工件，由 `scripts/` 下的校验器自动检查——门禁只能由证据推动，不能自我声明。同时用 32 个职责单一的技能覆盖从读题到交论文的每一步。

| 原则 | 含义 |
|---|---|
| **AI 负责机械正确性** | 解析题目、写代码、跑实验、整理证据、起草论文，均由 AI 完成 |
| **人类拥有建模判断权** | 选方法、判结果、定置信度、物理意义与贡献论述，只能由人类拍板，并留痕 |
| **证据驱动一切** | 门禁、冻结、论文数字都必须溯源到磁盘上的真实工件与哈希，禁止口头声明 |

## 快速开始

```bash
git clone https://github.com/Chickeryxn/chickery-s-math-modeling-skill.git
cd chickery-s-math-modeling-skill
git checkout mathmodeling-new-skeleton
```

1. 用 **Codex、Claude 或 DeepSeek Harness（DSH）桌面版**打开仓库根目录。
2. 把题目与附件放入 `workspace/problem.txt`、`workspace/data_raw/<题目附件>`（原始附件只读，清洗副本写入 `workspace/data_clean/`）。
3. 让 agent 跑一次自检：`python scripts/validate_repo.py .`。
4. 开始工作流：`problem-parser → problem-classifier → data-auditor-cleaner → workflow-orchestrator`（agent 会按门禁逐步推进并在建模判断点询问你）。

会话配置在 `planning/session_config.json`：`interaction_mode`（`learning`/`speed`）控制提问密度，`rigor_profile`（`lean`/`submission`）控制工件与审计密度；新工作区默认 `learning + lean`，提交前切到 `submission`。

## 核心概念

![通用门控流水线](docs/diagrams/archify/assets/mm-generic-workflow.png)

**门禁**：每次竞赛按子问题（Q1、Q2…）独立推进，每个子问题走同一套门禁——G1 问题框架化 → G2 方法筛选 → G2.5 人工选型 → G3 代码与实验评审 → G4 结果判定与冻结 → G5 论文章节 → G6 最终审计。门禁由 `scripts/workflow_guard.py derive Qx` 从磁盘证据推导，**manifest 只是缓存，不能自我提升**。

**关键规则**

- 只有 G2 与 G2.5 同时通过，才允许生成模型代码。
- 人工方法、结果、稳定性与声明范围决策，必须记入追加式 JSONL 决策账本，AI 不得代写理由。
- 论文中出现的每个数字必须来自 `results/Qx/reports/frozen_numbers.json`；改数要走「解冻 → 改源头 → 重跑 → 重冻结」并记录变更日志，禁止手改。
- 图分四型：Type 1 诊断图只做内部调试，永不进论文；Type 3/4 才进论文并须通过渲染校验。

**技能分组**（32 个，[全表见参考手册](docs/reference.md#技能清单-32-个)）

| 分组 | 覆盖 |
|---|---|
| 问题理解 | 解析、分类、文献分析、数据清洗 |
| 方法与决策 | 方法筛选、选择卡、决策账本、假设与符号表 |
| 代码与实验 | 代码生成/评审（Python、MATLAB/北太天元）、稳健性 |
| 结果与论文 | 结果报告、图表、方法说明、冻结、论文写作/润色/引用 |
| 编排与审计 | 门禁调度、完整性/一致性/QA 审计、工作记录 |
| 训练模式 | 闭卷求解、素养复盘、多维审核（专项能力训练） |

## 文档地图

按你的目标选文档（完整索引见 [docs/](docs/README.md)）：

| 目标 | 文档 |
|---|---|
| 理解"每个门禁为什么存在"、练习自检 | [学习路径](docs/learning-path.md) |
| 训练 agent 的高品质建模能力（闭卷→复盘→审核） | [训练模式](docs/training.md) |
| 详细记录工作过程（`records/` 记录树） | [工作记录树](docs/work-record.md) |
| 用 DSH 桌面版（技能发现/沙箱/冒烟清单） | [DSH 适配](docs/dsh-compatibility.md) |
| 构建论文（xelatex + CUMCMThesis） | [论文构建](docs/paper-build.md) |
| 技能全表/契约/命令/目录/术语/上游 | [参考手册](docs/reference.md) |

## 常见问题

**Q：它能直接替我做题或写论文吗？**
不能。AI 只做机械正确性；方法选择、结果判定、物理解释与贡献论述必须由你决定并留痕——这也是主办方 AI 使用规则的要求。

**Q：需要安装什么依赖？**
零第三方依赖。所有脚本仅用 Python 标准库（3.10+），`python scripts/run_tests.py` 即可自检。

**Q：Codex、Claude 和 DSH 都能用吗？**
能。三棵技能树（`.codex/`、`.claude/`、`.agents/`）各自完整独立、内容一致；修改技能时先改 `.codex/skills/` 再运行 `python scripts/sync_plugin.py .` 同步，用 `validate_skill_trees.py` 校验。

**Q：`frozen_numbers.json` 能直接手改吗？**
不能。改数必须：解冻 → 修改源头 → 重跑受影响实验 → 重冻结，并在 `freeze_change_log.md` 记录原因。

**Q：如何扩展或修改技能？**
改 `.codex/skills/<skill>/SKILL.md` 后运行 `python scripts/sync_plugin.py .` 同步全部副本，再用 `validate_skill_trees.py` 校验。

**Q：和 XiaoMaColtAI 等上游技能库是什么关系？**
本项目合并了 6 个上游项目并锁定 12 项决策（历史见 [references/README.md](references/README.md)）；现行可执行契约以 `AGENTS.md`、`schemas/`、`scripts/` 为准。

## 许可与致谢

[MIT License](LICENSE)。合并借鉴了 [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill)、[latexstudio/CUMCMThesis](https://github.com/latexstudio/CUMCMThesis)、[Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills)、[Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills)、[jihe520/sci-box](https://github.com/jihe520/sci-box) 等上游项目；流程图由 [tt-a1i/archify](https://github.com/tt-a1i/archify) 生成。详细合并决策见 [references/README.md](references/README.md) 与 [NOTICE.md](NOTICE.md)。
