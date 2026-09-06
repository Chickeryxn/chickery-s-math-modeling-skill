# 论文构建说明（Paper build）

## 目标

把 `paper-section-writer` 产出的分节草稿（`paper/sections/qx.tex`）装配成可编译的主文档，并让论文中的数字严格来自 `frozen_numbers.json`。

## 装配

```powershell
python scripts/latex_assembly.py .            # 生成 paper/main.tex + paper/build_report.json
python scripts/latex_assembly.py . --dry-run  # 只查看装配计划
```

装配脚本（纯标准库）会：
1. 按文件名顺序扫描 `paper/sections/*.tex`，生成 `\input` 清单；
2. 读取 `results/*/reports/frozen_numbers.json`，为每个 claim 生成 `\newcommand` 宏（论文正文引用宏而非裸数字）；
3. 从决策账本（`submission_authorization`）与 `paper/ai_use_disclosure.md` 生成 AI 工具使用声明段；
4. 输出页数估算（粗略）与文件清单。

## 编译

```powershell
xelatex main.tex    # 在 paper/ 下；至少两遍以解析交叉引用
```

要求：TeX Live / MiKTeX / MacTeX（xelatex 引擎），系统装有中文字体与 Times New Roman/Arial（Linux 需安装对应字体包）。

## 模板策略（重要）

本仓库**不内置任何第三方 LaTeX 模板代码**（CUMCMThesis 无许可证，不得 vendor）。两种选择：

1. **默认 clean-room 基线**：`templates/paper/main.tex`（本仓库自写，覆盖题目/摘要/中文章节编号/无目录/AI 声明/附录骨架；不含官方承诺书与编号页）。
2. **官方模板（推荐提交时使用）**：自行按固定 commit 获取 [latexstudio/CUMCMThesis](https://github.com/latexstudio/CUMCMThesis)（含承诺书、编号页、2026 格式与 AI 声明命令），然后：

```powershell
python scripts/latex_assembly.py . --template <你本地的 cumcmthesis 主文档路径>
```

> 模板获取属**构建期外部依赖**：请核对固定 commit（如 `38d1f21`）与许可证状态后再使用；本仓库不托管其代码。

## 论文必须包含比赛要求的全部内容，并产出一份由 LaTeX 编译的 PDF

- **内容齐全**：论文须覆盖国赛/美赛全部栏目（摘要、问题重述、模型假设、符号说明、问题分析、模型构建、模型求解、结果分析、稳健性/误差、结论、参考文献、AI 使用声明、附录/支撑材料清单）。摘要逐问有数字；正文每问有结论。
- **有图有表**：结果分析、稳健性等小节须配**足够且必要的图与表**（Type 2–4 图进入论文、Type 1 诊断图永不进论文；进入论文的图须通过 `scripts/figure_render_audit.py .` 渲染校验）。图表规划见 `figure-table-planner` 与 `math-figure-generator`。
- **容量与格式**：以 `references/award-papers/` 的获奖论文为**容量/格式标杆**（正文 ≤ 30 页、摘要 ≤ 1 页、每篇配图/表数量适中）；由 `scripts/section_structure_check.py` 核对骨架齐全与顺序。
- **产出 PDF**：`python scripts/latex_assembly.py .` 生成 `paper/main.tex` 后，在 `paper/` 下 `xelatex main.tex`（至少两遍以解析交叉引用）编译出 **`paper/main.pdf`**。提交时以该 PDF 为最终版；`preflight.py` 会核验页数、裸数字、图表一致性与骨架。
- **图/表/附录文件**：`paper/figures/` 与 `paper/sections/*.tex` 一并作为交付物，保证 PDF、图、表、源代码可复核。

## 机械校验（提交前）

- 正文页数 ≤ 30、摘要 ≤ 1 页、电子版 PDF ≤ 20 MB（2026 修订稿）；用 LaTeX 构建日志与 PDF 元数据核对。
- 每个数字在正文中应引用冻结宏（如 `\q1mainrmse`），禁止手写裸数字。
- 引用以 `\cref` 风格（图~x / 表x）统一；参考文献用 `reference-manager` 产出的条目转 `\bibitem`。
- 汇编后运行三审（G6）：一致性/完整性/质检。

## 提交前预检（preflight）

`python scripts/preflight.py .` 一键串联提交相关的机械检查：`claim_coverage`（每问有节/冻结/摘要数字）、`abstract_checker`（摘要逐问数字）、`ai_trace_checker --strict`（抽样章节）、`latex_assembly --check-only --strict`（裸数字与冻结引用）、`figure_consistency_check`（paper/figures）、`section_structure_check --strict`（骨架顺序与篇幅）。输入工件缺失的步骤自动跳过；任一已执行的步骤失败即返回 2——提交前 10 分钟跑一次即可兜底。

配套的两个单项审计：

- `python scripts/check_frozen_freshness.py .` — 冻结数字新鲜度（源文件存在且不晚于 `frozen_at`），已接入 `validate_repo.py`。
- `python scripts/figure_render_audit.py .` — 论文章节引用的每张图都存在且有 `<图名>.render.json` 渲染证据。
