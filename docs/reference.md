# 参考手册（Reference）

> 本页是 README 的参考性附录：技能全表、契约体系、命令速查、目录结构、测试覆盖、术语表、上游融合与边界。日常使用请从 [`README.md`](../README.md) 进入，先读 [文档索引](README.md)。

## 技能清单 32 个

技能树在 `.codex/skills/`、`.claude/skills/`、`.agents/skills/`（DSH 自动发现）各有一份完整独立副本（`plugins/mathmodeling-skills/skills/` 为分发副本）。按流水线分五组，另加一组训练模式技能：

### 问题理解

| 技能 | 一句话职责 | 主要产物 |
|---|---|---|
| `problem-parser` | 把题目解析为目标、对象、约束、输出、子问题与成功标准 | `planning/parse/problem_parse.json` |
| `problem-classifier` | 按输出与结构分类子问题任务型，暴露需人类裁定的框架歧义 | `planning/classification/problem_classification.json` |
| `related-paper-analyzer` | 只分析用户放在 `workspace/papers/` 的原文，提取可迁移方法线索 | `workspace/papers/related_paper_analysis.md` |
| `data-auditor-cleaner` | 附件映射、数据审计与清洗，产出一份可复用数据画像 | `workspace/data/data_profile.json`、`data_clean/` |

### 方法与决策

| 技能 | 一句话职责 | 主要产物 |
|---|---|---|
| `method-selector` | 组建「主候选+可用基线+≤1 条件备选」并跑方法专属风险探针 | `methods/Qx/qx_method_card.md`、`probes/risk_probe_summary.json` |
| `decision-prompt-builder` | 在真正的建模判断点生成「选择卡」，一次最多 3 问 | 不落盘（返回 choice_card） |
| `modeler-decision-logger` | 把人类原话忠实追加进决策账本，绝不代写理由 | `methods/Qx/qx_decisions.jsonl` |
| `model-assumptions-builder` | 提取与维护全局/方法假设，必要性判定留给人类 | `planning/model_assumptions.md` |
| `symbol-table-builder` | 维护全局符号与单位表，消除跨子问题冲突 | `planning/symbol_table.md` |

### 代码与实验

| 技能 | 一句话职责 | 主要产物 |
|---|---|---|
| `model-code-analyzer` | 把人类批准的方法翻译成语言无关的实现与实验契约 | `code/Qx/qx_code_plan.md` |
| `python-model-code-generator` | 生成并运行最小可复现 Python 主方法与基线 | `code/Qx/*.py`、`run_summary.json` |
| `matlab-model-code-generator` | 生成并运行 MATLAB / 北太天元兼容代码 | `code/matlab/Qx/*.m`、`run_summary.json` |
| `code-reviewer` | 按语言路由到对应评审器 | —（路由） |
| `python-code-reviewer` | 五项命名检查：语法/输入契约/方法对齐/可复现性/输出契约 | `code/Qx/reviews/qx_python_review.json` |
| `matlab-code-reviewer` | 同上 + 工具箱与北太天元兼容性检查 | `code/matlab/Qx/reviews/qx_matlab_review.json` |
| `robustness-checker` | 针对承重假设做扰动、重采样、基线对比等稳健性检验 | `robustness/Qx/qx_robustness_summary.json` |

### 结果与论文

| 技能 | 一句话职责 | 主要产物 |
|---|---|---|
| `result-report-generator` | 把实验工件压缩为决策点证据，不替人类选赢家 | `results/Qx/reports/qx_final_result_analysis.md` |
| `figure-table-planner` | 规划最少的证据性图表（Type 1–4） | `methods/Qx/qx_figure_table_plan.md` |
| `math-figure-generator` | 按统一配色/版式/渲染校验生成出版级图 | `paper/figures/` |
| `final-method-explainer` | 从方法卡/账本/结果生成权威最终方法说明 | `methods/Qx/qx_final_method_explanation.md` |
| `solution-package-builder` | 组装交付包并在人工签核后冻结数字 | `results/Qx/reports/qx_solution_package_for_writer.md`、`frozen_numbers.json` |
| `paper-section-writer` | 只从 solution package 与冻结数字起草论文段落 | `paper/sections/qx.tex` |
| `paper-polisher` | 语法/一致性/过度声明校准（借鉴 nature-polishing 原则） | 润色后的 `paper/sections/` |
| `reference-manager` | 校验引用真实性、生成 BibTeX、标记未验证项 | `paper/refs.bib`、`paper/reference_audit.md` |

### 编排与审计

| 技能 | 一句话职责 | 主要产物 |
|---|---|---|
| `workflow-orchestrator` | 门禁调度器：读状态、算门禁、路由下一步，不亲自建模写码 | `planning/manifests/Qx.json`（状态源） |
| `completeness-auditor` | 按当前 profile 核对交付证据是否存在且未过期 | `paper/audits/completeness_audit.md` |
| `consistency-auditor` | 跨介质核对数字/符号/参数/决策与文件一致性 | `paper/audits/cross_media_consistency_audit.md` |
| `quality-assurance-auditor` | 最终提交级五维审计（流程/证据/方法/论文/呈现） | `paper/qa_report.md` |
| `work-logger` | 维护 `records/` 工作记录树：会话日志、门禁迁移、决策卡镜像 | `records/`（`scripts/work_record.py`） |

### 训练模式

| 技能 | 一句话职责 | 主要产物 |
|---|---|---|
| `training-solver` | 闭卷求解训练题：全程不得读取 `resource-library/` | `results/training/roundN/solution/` |
| `training-reflector` | 开卷对照资源库逐维复盘，产出可迁移的素养差距 | `results/training/roundN/reflection.md` |
| `training-auditor` | 跑机械检查、起草六维素养记分卡、汇总供人类定方向 | `results/training/roundN/scorecard.json`、`summary.json` |

## 契约体系

领域无关契约定义在 `schemas/`，由 `scripts/` 中的校验器强制执行；**新题目不得修改 schema**，题目语义写入独立的 `planning/model_contract.json`。

| 契约 | Schema 文件 | 校验器 | 说明 |
|---|---|---|---|
| 模型契约 | `schemas/model_contract.schema.json` | `validate_model_contract.py` | 实体/输入/状态函数/决策变量/约束/目标/评估器/不确定性/验证合同；main、baseline、verifier 必须引用同一合同哈希 |
| 人类决策 | `schemas/decision.schema.json` | `validate_decisions.py` | `DECIDED` 必须含 `source`（`user_answer` + 用户消息 ID + 原话）且时间戳为 ISO-8601 |
| 运行快照 | `schemas/run_snapshot.schema.json` | `create_run_snapshot.py` / `validate_run_snapshot.py` | 计划/实际预算、输入/代码/配置哈希、命令、环境、返回码；成功必须由统一运行器执行 |
| 产物谱系 | `schemas/lineage.schema.json` | `lineage.py` / `validate_artifacts.py` | 来源/验证者/消费者/哈希/决策 ID；上游变更 → 下游 `STALE` |

## 命令速查

| 命令 | 用途 |
|---|---|
| `python scripts/run_tests.py` | 运行全部测试（标准库 unittest，无第三方依赖） |
| `python scripts/validate_repo.py .` | 仓库级完整性总检（技能树、测试、契约、快照、血缘、QA） |
| `python scripts/validate_skill_trees.py .` | 四棵技能树哈希一致性 + 插件 manifest 版本一致 |
| `python scripts/sync_plugin.py . [--check]` | 同步 `.codex/skills/` → `.claude/skills/`、`.agents/skills/` 与插件分发副本 |
| `python scripts/workflow_guard.py . derive Q1 --profile lean\|submission\|auto` | 从证据推导 Q1 当前门禁（lean 止于 G4 结果判定子门；auto 读 `session_config`；缺省 submission）；可选 `--deadline` 输出剩余时间提示 |
| `python scripts/workflow_guard.py . require Q1 model_code` | 产出敏感工件前检查门禁（不满足则 GATE_BLOCKED） |
| `python scripts/validate_model_contract.py planning/model_contract.example.json` | 校验模型契约结构并输出合同哈希 |
| `python scripts/validate_decisions.py . methods/Q1/q1_decisions.jsonl` | 校验决策账本（人类溯源、追加式、时间戳） |
| `python scripts/create_run_snapshot.py run . runs/<run_id> --command "python code/main.py" --result-ref results/result.json --validation-ref results/validation.json` | 统一运行器执行实验并生成不可变快照 |
| `python scripts/validate_run_snapshot.py . runs/<run_id>` | 校验快照完整性（成功必须由运行器执行） |
| `python scripts/lineage.py assess . path/to/artifact.lineage.json` | 评估产物血缘 CURRENT/STALE/MISSING |
| `python scripts/validate_artifacts.py . planning/manifests/Q1.json` | 校验 manifest 声明的工件均有 CURRENT 血缘 |
| `python scripts/qa_report.py .` | 生成分层 QA 报告（任何阻塞层缺失即非 PASS） |
| `python scripts/work_record.py check .` | 校验工作记录树（索引同步/链接/时间与门禁单调；账本无镜像决策卡为 advisory 提示） |
| `python scripts/check_frozen_freshness.py .` | 冻结数字新鲜度（源文件存在且不晚于 `frozen_at`；已接入 validate_repo） |
| `python scripts/figure_render_audit.py .` | 论文引图存在性 + `<图名>.render.json` 渲染证据审计 |
| `python scripts/preflight.py .` | 提交前预检一键汇总（claim_coverage/abstract/ai_trace/latex `--strict`/图一致性/骨架） |
| `python scripts/polish_stats.py <章节文件>` | 量化写作指标（>30 词长句比例/占位套话/AI 连接词），`paper-polisher` 前置扫描 |
| `python scripts/sync_plugin.py . --dry-run` | 预览四树同步将覆盖的差异（不写盘） |

详细参数见 [`scripts/README.md`](../scripts/README.md)，契约说明见 [`schemas/README.md`](../schemas/README.md)。

## 目录结构

```text
.
├── .codex/skills/                 # Codex 技能树（32 个，同步源）
├── .claude/skills/                # Claude 技能树（完整独立副本）
├── .agents/skills/                # DeepSeek Harness 技能树（仓库内自动发现，完整独立副本）
├── plugins/mathmodeling-skills/   # 插件分发包（两个 manifest + 技能副本 + hooks）
├── .agents/plugins/marketplace.json  # marketplace 目录清单
├── AGENTS.md                      # 工作流政策唯一事实来源（门禁/工件/人工决策/冻结/审计）
├── CLAUDE.md                      # Claude 运行规则（Codex/DSH 侧由 AGENTS.md 覆盖）
├── planning/                      # 会话配置、parse/classification、manifests、presets、示例契约
├── methods/Qx/                    # 方法卡、决策账本、风险探针、最终方法说明
├── code/                          # 模型代码与评审（code/Qx/、code/matlab/Qx/）
├── results/Qx/                    # 实验轮次、报告、solution package、frozen_numbers.json
├── results/training/              # 训练模式产物（roundN/ 与 summary.json）
├── robustness/Qx/                 # 稳健性证据
├── paper/                         # 论文章节、图、引用与三审报告
├── workspace/                     # problem.txt、data_raw/（只读）、data_clean/、papers/
├── resource-library/              # 训练模式示范资源库（papers/ideas/figures/formulas/tables/assets）
├── records/                       # 工作记录树（sessions/subjects/gates/decisions/retros，advisory）
├── references/                    # 上游知识库（历史决策，advisory，非强制）
├── schemas/                       # 领域无关契约（4 个 schema + 说明）
├── scripts/                       # 32 个纯标准库脚本（含 1 个 bash 兼容包装）
├── docs/                          # 手册（索引/学习/训练/记录/复盘/DSH/论文/参考）
├── docs/diagrams/archify/         # 通用流程图（PNG/SVG/交互 HTML/JSON 源）
└── tests/                         # 241 个测试用例
```

## 测试覆盖

`python scripts/run_tests.py`（241 个用例，全标准库）覆盖：

- 门禁证据推导与单调迁移（含完整 G1→G6 推进链到 `final_assembly`）
- 人类决策溯源（伪造人类、未注册证据、路径逃逸均被拒绝）
- 运行快照与预算降级（`DEGRADED_SUCCESS`、未由运行器执行的成功被拒）
- 产物血缘与 STALE 传播、空血缘拒绝
- main/baseline/verifier 独立性（共享指标源被拒）
- 模型契约结构、四树技能同步、分层 QA（含 GATE_BLOCKED 退出码传导）
- 三类合成场景（回归 / 排程 / 动态事件）端到端测试
- 风险探针 list/dict 两种结构兼容、FAIL verdict 不卡门禁
- 论文装配（`latex_assembly`：装配/冻结宏转义/choice 转义/宏名唯一/AI 声明/裸数字扫描）
- 上游资产校验（`validate_upstream_assets`，含 SHA-256 漂移与 NOTICE 交叉）
- AI 痕迹扫描（`ai_trace_checker`，含 `--config` 自定义阈值）
- 摘要质量检查（`abstract_checker`）与学习摘要生成（`learning_summary`）
- 模型质量门（`model_quality_gate`）、泄漏启发式（`leakage_check`）与题目覆盖校验（`claim_coverage`）
- 图表一致性（`figure_consistency_check`）与论文章节结构检查（`section_structure_check`）
- 资源库索引（`resource_index`，含嵌套目录）与训练记分卡（`training_scorecard`）
- 工作记录树（`work_record`）与 hooks 守卫（`guard_frozen`，含 DSH 小写工具）
- 文档计数守卫（`doc_claims`）与治理层 e2e（`governance_e2e`）
- 门禁 profile 双轨（lean 子门 / submission 全链 / auto 读配置）、结构深度检查（parse/classification/probe 退化块）与 framing 决策阻塞
- 冻结新鲜度（`check_frozen_freshness`）、图渲染证据（`figure_render_audit`）、提交预检编排（`preflight`）
- 量化写作指标（`polish_stats`）、运行快照可选 `vcs` 记录、决策 `unavailable:` 消息 ID 标记策略
- 金样例守卫（`test_examples`）与 work_record 决策卡镜像 advisory

## 术语表

| 术语 | 含义 |
|---|---|
| 门禁（gate） | G1–G6 六道关卡 + G2.5 人工选型点，由证据推导、单调推进 |
| manifest | `planning/manifests/Qx.json`，每子问题的机器可读状态缓存（不能自我提升门禁） |
| canonical evidence | 磁盘上真实存在的权威工件，门禁推导的唯一依据 |
| 风险探针（risk probe） | 方法专属的限时小实验，检查可执行性/数据覆盖/假设/输出退化/扰动/规模 |
| 选择卡（choice card） | 只在建模判断点出现的 2–3 个互斥选项，附后果说明，由人类作答 |
| 决策账本（decision ledger） | `methods/Qx/qx_decisions.jsonl`，追加式 JSONL；`DECIDED` 必须绑定用户原话 |
| 运行快照（run snapshot） | 统一运行器产出的不可变实验记录（预算/哈希/命令/环境/返回码） |
| DEGRADED_SUCCESS | 成功但实际预算低于计划的运行状态，相关声明须降级 |
| 产物谱系（lineage） | 工件的来源/验证者/消费者/哈希记录；上游变更使下游变 `STALE` |
| 模型合同（model contract） | `planning/model_contract.json`，题目专属的实体/约束/目标/评估/验证定义 |
| 冻结数字（frozen numbers） | `frozen_numbers.json`，论文数字唯一真相源，禁止手改 |
| main / baseline / verifier | 主方法 / 可用基线 / 独立验证者，三者角色分离且必须互检独立 |
| rigor profile | `lean`（探索期精简工件）或 `submission`（提交期全量工件与三审） |
| interaction mode | `learning`（多提问、先答后建议）或 `speed`（少提问、可并列建议） |
| preset | 必须显式激活、带版本、advisory 的默认值集，不得覆盖合同或人类决定 |

## 上游融合

本项目在**不改变治理核心**（AGENTS.md / schemas / scripts、G1–G6 门禁、28 技能骨架 + 3 训练技能 + 1 记录技能、零第三方运行时依赖、单一 matplotlib 引擎）的前提下，融合了 6 个上游项目的知识规则层与纯标准库工具层：

| 上游 | 引入内容 | 方式 |
|---|---|---|
| [nature-skills](https://github.com/Yuan1z0825/nature-skills)（Apache-2.0） | 图契约/QA/PALETTE、写作润色规则、统计 P0/P1/P2、结果分配与一致性工具 | 逐字引入至 `references/upstream/`，保留声明 |
| [Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills)（MIT） | 去 AI 味规则、四轮自审、句式库、Figure Contract、方法决策矩阵、8 本算法 cookbook | 逐字引入，保留版权行 |
| [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill)（无许可，不复制） | 门禁映射、数值求解稳健性 9 项、复现理念 | clean-room 自写至 `references/upstream/method-index/` |
| [sci-box](https://github.com/jihe520/sci-box)（无许可，不复制） | 图型启发 | clean-room 图模板（`math-figure-generator` references） |
| [CUMCMThesis](https://github.com/latexstudio/CUMCMThesis)（无许可，不 vendor） | 国赛论文模板 | 构建期外部依赖，见 [`docs/paper-build.md`](paper-build.md) |
| [archify](https://github.com/tt-a1i/archify)（MIT） | 流程图生成 | 外部工具 + 已提交生成物（`docs/diagrams/archify/`） |

引入纪律：Apache-2.0 / MIT 内容保留声明与许可文本；无许可证或专有内容（如 XiaoMaColtAI 的 `tools/docx|pdf|xlsx`）一律不复制；网络执行（检索/MCP）与第三方运行时（Node/TeX/Pandoc/LibreOffice）不入核心。校验命令：`python scripts/validate_upstream_assets.py .`。来源与许可证明细见 [`references/upstream/README.md`](../references/upstream/README.md)、`LICENSES/` 与 `NOTICE.md`。

## 限制与边界

- 本项目提供的是**工作流模板与执行校验工具**，不声称能阻止一切绕过脚本的直接文件写入。
- 校验器检查的是**已落盘工件**；AI 的诚实性最终仍依赖使用者遵守流程。
- 本项目**不编码 offline/network 策略**；如需离线约束，属环境或用户级配置。
- 门禁与审计是质量保障，不构成对竞赛成绩或论文结论的任何担保。
