# 数学建模工作区与 Codex 技能

这是一个可直接克隆的数学建模竞赛工作区模板，包含：

- Codex 项目技能：`.codex/skills/`
- Claude 项目技能：`.claude/skills/`
- 可安装的 `mathmodeling-skills` 插件：`plugins/mathmodeling-skills/`
- 数学建模工作目录：`workspace/`、`methods/`、`code/`、`results/`、`paper/` 等
- 门禁、可复现实验、冻结数字和论文审计规则：`AGENTS.md`

本仓库是**空题目工作区**，不包含任何旧赛题数据、旧代码、旧实验结果或旧论文。

## 快速开始：作为项目使用

适用于希望在 Codex 或 Claude 中直接打开整个数学建模工作区的用户。

```bash
git clone https://github.com/Chickeryxn/chickery-s-math-modeling-skill.git
cd chickery-s-math-modeling-skill
git checkout mathmodeling-new-skeleton
```

然后在 Codex/Claude 中打开仓库根目录。将新赛题材料放入：

```text
workspace/problem.txt
workspace/data_raw/<新题附件>
```

不要修改 `workspace/data_raw/` 中的原始附件；清洗副本应写入 `workspace/data_clean/`。

首次工作流顺序：

```text
problem-parser
→ problem-classifier
→ data-auditor-cleaner
→ workflow-orchestrator
```

默认配置位于：

```text
planning/session_config.json
```

当前默认值是 `interaction_mode=learning`、`rigor_profile=lean`。

## 作为 Codex 插件安装

如果只想安装技能，而不把仓库作为当前项目打开，可以使用仓库自带的本地 marketplace：

```bash
# 在仓库根目录执行
codex plugin marketplace add .
codex plugin add mathmodeling-skills@chickery-s-math-modeling-skill
```

安装后建议新建一个 Codex 对话，使新技能在新会话中生效。

Windows PowerShell 示例：

```powershell
cd "D:\path\to\chickery-s-math-modeling-skill"
codex plugin marketplace add .
codex plugin add mathmodeling-skills@chickery-s-math-modeling-skill
```

如果仓库被克隆到其他目录，仍使用 marketplace 名称
`chickery-s-math-modeling-skill`，不要把本地绝对路径写入配置文件。

## 作为 Claude 插件使用

仓库也保留了 Claude 技能树和 Claude 插件清单：

```text
.claude/skills/
plugins/mathmodeling-skills/.claude-plugin/plugin.json
```

在 Claude 环境中使用时，按该环境的插件安装方式加载
`plugins/mathmodeling-skills/`，或直接将仓库作为项目打开。

## 目录说明

```text
.
├── .codex/skills/                  # Codex 项目技能
├── .claude/skills/                 # Claude 项目技能
├── plugins/mathmodeling-skills/   # Codex/Claude 插件分发副本
├── planning/                       # 配置、解析、分类、门禁状态
├── workspace/                      # 题目、原始数据和清洗数据
├── methods/                        # 方法卡、风险探针和人工决策
├── code/                           # Python/MATLAB 建模代码
├── results/                        # 实验结果与冻结数字
├── robustness/                     # 鲁棒性检查
├── paper/                          # 论文、图表和审计
└── references/                     # 只读流程知识库
```

`.codex/skills/`、`.claude/skills/` 和
`plugins/mathmodeling-skills/skills/` 应保持一致。技能修改后可运行：

```bash
bash scripts/sync-plugin.sh
bash scripts/sync-plugin.sh --check
```

## 建模工作流原则

- AI 负责机械正确性、代码运行、证据整理和一致性审计。
- 建模取向、方法选择、必要假设、物理解释和最终贡献表述由人类确认。
- 数据链保持：

```text
原始数据 → 清洗数据 → 模型代码 → 实验结果 → 冻结数字 → 论文
```

- 未通过相应门禁前，不生成后续阶段的正式产物。
- 不把旧题目的结果或数字复制到新题目工作区。

## 许可

本项目按 MIT License 发布，见根目录 `LICENSE`。

## 仓库分支

当前模板分支：`mathmodeling-new-skeleton`

主仓库：<https://github.com/Chickeryxn/chickery-s-math-modeling-skill>