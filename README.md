# 数学建模工作区与 Codex 技能

[简体中文](README.md) | [English](README.en.md)

本项目提供带有门禁检查、决策溯源、实验快照、产物谱系、独立性验证和分层 QA 工具的数学建模工作流模板。

## 快速开始

```bash
git clone https://github.com/Chickeryxn/chickery-s-math-modeling-skill.git
cd chickery-s-math-modeling-skill
git checkout mathmodeling-new-skeleton
```

在 Codex 或 Claude 中打开仓库根目录。将当前问题和附件放入：

```text
workspace/problem.txt
workspace/data_raw/<题目附件>
```

原始附件只读；清洗副本写入 `workspace/data_clean/`。默认工作流为：

```text
problem-parser
→ problem-classifier
→ data-auditor-cleaner
→ workflow-orchestrator
```

会话配置位于 `planning/session_config.json`，默认使用 `learning + lean`。

## G1–G6 工作流

```text
G1 问题框架化
→ G2 方法筛选
→ G2.5 人工选型
→ G3 代码与实验复核
→ G4 结果判断与冻结
→ G5 论文段落就绪
→ G6 最终审计
```

门禁由 manifest 和 canonical evidence 共同判断；manifest 不能单独提升门禁。局部脚本通过不等于整体门禁通过。人工方法、结果、稳定性和主张范围必须记录在追加式 JSONL 决策日志中。

## 工作流完整性工具

常用命令：

```powershell
python scripts/run_tests.py
python scripts/validate_repo.py .
python scripts/validate_skill_trees.py .
python scripts/sync_plugin.py . --check
python scripts/validate_model_contract.py planning/model_contract.example.json
python scripts/workflow_guard.py . derive Q1
python scripts/workflow_guard.py . require Q1 model_code
python scripts/create_run_snapshot.py run . runs/<run_id> --command "python code/main.py" --result-ref results/result.json --validation-ref results/validation.json
python scripts/lineage.py assess . path/to/artifact.lineage.json
```

详细参数见 `scripts/README.md`；合同定义见 `schemas/README.md`。

## 模型合同

问题框架化阶段应创建项目专属 `model_contract.json`，声明实体、输入、状态函数、决策变量、硬约束、软约束、目标函数、评估器、不确定性处理和验证合同。`schemas/model_contract.schema.json` 是通用结构，不应写入任何具体题目实体或参数。

主方法、usable baseline 和 verifier 必须引用同一模型合同及其哈希，但使用独立的实现和运行证据。

## 实验快照与产物谱系

实验应通过统一运行器记录计划预算、实际预算、预算差异、输入/代码/配置哈希、命令、环境、返回码、结果和验证文件。实际预算低于计划预算时，运行标记为 `DEGRADED_SUCCESS`，相关稳定性或最优性表述必须降级。

关键产物使用 lineage 记录来源、验证者、消费者、代码/配置/输入哈希和决策 ID。上游哈希变化会使下游产物变为 `STALE`，stale 产物不能用于冻结或论文装配。

## 人工决策与独立性

`DECIDED` 只能绑定可验证的用户回答来源；AI 摘要不得替代用户原话。main、baseline、verifier 是不同角色，不能因为脚本文件名不同就声称独立。使用相应验证器检查静态文件、运行引用和独立实验记录。

## 目录与插件

```text
.codex/skills/
.claude/skills/
plugins/mathmodeling-skills/skills/
planning/
methods/
code/
results/
robustness/
paper/
schemas/
scripts/
tests/
workspace/
```

当前项目包含一个 marketplace catalog：

```text
.agents/plugins/marketplace.json
```

以及两个插件 manifest：

```text
plugins/mathmodeling-skills/.codex-plugin/plugin.json
plugins/mathmodeling-skills/.claude-plugin/plugin.json
```

更新 `.codex/skills/` 后，运行 `python scripts/sync_plugin.py .` 同步 Claude 和插件分发副本。

## Preset 与 references

`planning/presets/` 中的 preset 必须显式激活、带版本并标记为 advisory；preset 只能提供默认值，不能覆盖问题合同或人工决定。`references/` 中的内容是参考知识，不会自动成为新问题的强制约束。

## 测试与限制

```powershell
python scripts/run_tests.py
python scripts/validate_repo.py .
```

测试覆盖门禁、人工决策、运行快照、预算降级、lineage/stale、独立性、连续事件、模型合同、技能同步、分层 QA 和三类合成场景。

项目提供工作流模板和执行校验工具；它不声称能够阻止所有绕过脚本的直接文件写入。项目本身不编码 offline/network policy。
