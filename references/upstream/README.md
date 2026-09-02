# references/upstream —— 上游融合知识资产

本目录是**经审核的上游知识资产层**，供各技能按需引用。定位与 `references/` 一致：**advisory 参考，不是自动要求**；不改变本仓库治理契约（AGENTS.md / schemas / scripts）。

## 来源与许可证总表

| 子目录 | 来源仓库 | 固定 commit | 许可证 | 引入内容 | 状态 |
|---|---|---|---|---|---|
| `nature-figure/` | [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) | `ebd722e` | Apache-2.0 | 图契约/QA/设计理论/PALETTE/多面板架构 + 3 个纯标准库渲染审计脚本 | 逐字引入（保留声明） |
| `nature-writing/` | 同上 | `ebd722e` | Apache-2.0 | 润色/写作/统计/共享规则 + check_consistency.py + 评审关注分类 | 逐字引入（保留声明） |
| `lupynow-writing/` | [Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills) | `3a9428c` | MIT | 去 AI 味/四轮自审/句式库/Figure Contract/决策矩阵 | 逐字引入（保留版权行） |
| `lupynow-cookbook/` | 同上 | `3a9428c` | MIT | 8 本算法 cookbook（优化/ML/评价/机理/统计/网络/聚类/博弈） | 逐字引入（保留版权行） |
| `method-index/` | 综合（XiaoMaColtAI 等） | — | MIT（自写） | 方法家族索引 + 门禁映射/稳健性清单 | 自写（clean-room） |

## 校验

`python scripts/validate_upstream_assets.py .` 校验：
- 每个子目录存在 `UPSTREAM.md`，且含 `Source repository`、`License`、`Imported files` 字段；
- 清单中声明的文件真实存在；
- 许可证声明属于允许集合（`MIT` / `Apache-2.0` / `self-authored`）。

## 使用约定

- 技能引用时用相对路径，从技能目录起算：`../../references/upstream/nature-figure/figure-contract.md`（技能位于 `<tree>/skills/<skill>/`，上溯两级到仓库根；从 `references/upstream/` 内部则用 `../nature-figure/...`——不要写成 `../../references/upstream/...`，那会解析到不存在的 `references/references/upstream/`）。
- 不修改被引入的上游文件内容；如需改编，复制到技能自己的 `references/` 再改并在头部注明来源。
- 上游规则中的数字/断言（如"However 51 ≫ Furthermore 22"、Nature 图注 <250 词）为语料/历史统计，引用时标注时点。
- 每个 `UPSTREAM.md` 可附加可选的 `Reviewed at: YYYY-MM-DD` 行，记录维护者最近一次复核时间（advisory，不强校验）；语料统计类断言继续标注时点引用。

## 用法映射（四态清单）

哪些文件可以直接用、哪些只可参考、哪些引用了本仓库未 vendor 的脚本：

| 状态 | 含义 | 清单 |
|---|---|---|
| **已吸收** | 已改写入技能自有 references 或本库自有层，agent 优先用本地版 | `lupynow-writing/de-ai-writing.md`（→ `ai_trace_checker`/`paper-polisher`）、`model-selection-matrix.md`（→ `method-selector`）、`lupynow-cookbook/*`（→ `method-selector`/代码生成器）、`nature-writing/consistency-sweep.md`/`terminology-ledger.md`/`main-text-discipline.md`（→ `consistency-auditor`/`paper-polisher`） |
| **可直读** | 与竞赛论文直接相关，按需加载原文 | `nature-figure/figure-contract.md`、`qa-contract.md`、`design-theory.md`、`api.md`、`multipanel-evidence-architecture.md`、`nature-figure` 三个审计脚本、`nature-writing/style-guardrails.md` 等（注意是 Nature 期刊向规则，套用 CUMCM 中文论文时只取"语言服务论证"原则） |
| **含未 vendor 引用** | 原文提到本仓库未引入的脚本/资源，照做会 FileNotFound | `nature-figure/qa-contract.md`（`audit_figure_collisions.py`/`figure_safety.py`/`nature-article-requirements.md`/`requirements.txt`）、`api.md`（`figure_safety.py`/`panel_alignment.R`）、`design-theory.md`（`demos.md`）、`multipanel-evidence-architecture.md`（`../../nature-shared/...`）、`lupynow-cookbook/*`（`code-templates/...` 共 15 处）、`lupynow-writing/common-phrases.md`（`model-validation.md`）、`model-selection-matrix.md`（`problem-decomposition.md`）、`nature-writing/nat-comms-2025-diction.md`（`published-article-patterns.md`）、`consistency-sweep.md`（`scripts/check_consistency.py` 执行路径——该 py 已 vendor，但路径在本仓库不可用）、`nature-writing/style-guardrails.md` 等（"见 SKILL.md" 提示，指向上游技能而非本仓库）——agent 应忽略这些命令/路径，改用已 vendor 的脚本（`audit_panel_alignment.py`/`audit_pdf_text.py`/`validate_figure.py`/`scripts/figure_render_audit.py`） |
| **仅参考** | 只取理念，不直接套用 | Nature 投稿流程文件（`reviewer-checklist.md`、`technical-concern-taxonomy.md` 等 40KB 面向 Nature 投稿）、上游所有"网络核验"步骤 |

> 新增/更新本清单时保持简洁：宁可让 agent 读错一份文件，也不要让它在缺失脚本上浪费时间。

## 已知规则冲突的裁决顺序（先看这里）

上游原文之间偶有矛盾（逐字引入所致）。消费方（尤其 `paper-polisher`、`method-selector`、`math-figure-generator`）按以下优先级裁决，本仓库自有规则始终优先于任何上游文件：

1. **去 AI 味/连接词上限**：以 `lupynow-writing/de-ai-writing.md` 的量化上限为准（`moreover ≤ 1`、`moreover+furthermore ≤ 2`、"it is worth noting that ≤1" 等）。`lupynow-writing/common-phrases.md` 第十节的递进词列表只作词汇选择参考，**不得**推翻上述上限；`paper-polisher` 的 12 点清单与 `scripts/ai_trace_checker.py` 是执行入口。
2. **图注长度**：`nature-writing/style-guardrails.md` 的 "≤300 词" 是上限建议；语料统计提示（如 "Nature 图注 <250 词"）是统计口径，不是规则。使用 ≤300 词上界并标注语料时点。
3. **绘图工具**：`lupynow-cookbook/cookbook-ml.md` 的 "NN-SVG / draw.io" 一条为未裁剪残留，以本仓库 **matplotlib-only** 图引擎政策为准（`math-figure-generator`）。
4. **过度声明词表**：以 `paper-polisher` 十二点清单为准（它整合并引用上游风格文件）；上游 overclaim 词表出现分歧时不再逐个调和，统一走 `paper-polisher`。
5. **统计/排版数字**（5pt 字形、89/183 mm 等）：语料/自写综合，非 Nature 官方条款；引用时标注"语料统计"。`validate_figure.py` 等已 vendor 脚本中的规则以其自身 docstring 声明为准。

## 明确未引入（许可证或边界原因）

- XiaoMaColtAI：根目录无 LICENSE；`tools/docx|pdf|xlsx` 为 **Anthropic 专有**；算法库 438KB（无许可证）——一律不复制。
- sci-box：仓库根无 LICENSE；图模板含硬编码论文出处——不复制，仅作理念启发。
- CUMCMThesis：无 LICENSE——模板不 vendor，见 `docs/paper-build.md` 的构建期外部依赖说明。
- nature-skills `figures4papers` 资产：无许可证，禁止复制。
- 一切网络执行（MCP/搜索 API/下载器）与外部运行时：不入核心。
