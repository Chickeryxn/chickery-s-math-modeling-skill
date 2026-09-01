# CUMCM2026 只读知识库（references/）

本目录是只读知识库，存放 6 个上游项目合并后的固定决策与流程契约。除本文件外，后续由阶段门禁体系自动维护。

## 六个上游项目与定位
1. latexstudio/CUMCMThesis —— 国赛 LaTeX 论文模板（PDF 主线输出）。
2. Lupynow/math-modeling-skills —— 去 AI 味 + 四轮自审等写作质控。
3. Yuan1z0825/nature-skills —— nature-figure 期刊级配图引擎。
4. XiaoMaColtAI/math-modeling-skill —— 五门禁主干（方法论骨架）。
5. 本仓库 —— 安装/项目模式、AGENTS.md、28 skills、results/Qx/ 目录与 frozen_numbers.json 数字真相源。
6. jihe520/sci-box —— 常规图/示意图引擎与科研工具集。

## 12 项已锁定决策
1A 主线 XiaoMaColtAI（五门禁主干）；2B 官方 PDF（CUMCMThesis + XiaoMaColtAI LaTeX 工具）；3A 合并 frozen_numbers.json（唯一数字真相源，复现清单并入）；4A 全候选（主候选 + 基线 + ≤1 条件备选）；5AB 双图引擎（sci-box 常规图/示意图 + nature-figure 期刊级图）；6A 国赛中文不叠 nature-polishing，只用 Lupynow 去 AI 味 + 四轮自审；7C 项目模式先 dry-run 再写配置；8A 每对话独立 PROJECT_ROOT，技能全局装一次；9C 五门禁管进度 + G2.5/G4 人工裁决 + 质检 Subagent 机械核对；10A 三角色协作默认关闭，仅固定质检；11A 实验目录统一 results/Qx/；12A 按主办方规则，AI 不替用户做建模判断与贡献论述。

## 门禁体系（五门禁 + 两处人工裁决）
G1 PROBLEM_FRAMED（问题框架化）→ G2 METHOD_SCREENED（方法筛选，含风险探针）→ G2.5 CHOSEN_BY_HUMAN（人工选型）→ G3 CODE_AND_EXPERIMENT_REVIEWED（代码与实验评审）→ G4 RESULTS_FROZEN / JUDGED_BY_HUMAN（人工裁决 + 数字冻结）→ G5 PAPER_SECTION_READY → G6 AUDIT_LAYER_PASSED（一致性/完整性/质检三审）。

## 数字唯一真相源
论文中出现的每个数字必须来自 results/Qx/reports/frozen_numbers.json；任何改动都要记录变更并重新冻结，禁止手改。

## 双图引擎路由
常规图/示意图 → sci-box；期刊级/发表质量图 → nature-figure；诊断图（类型1）永不进论文。

## 合规
AI 只负责机械正确性；建模判断、数字含义、假设框架、贡献论述由用户承担。每轮可输出 ai_use_disclosure.md 记录 AI 参与范围。


## Core versus preset boundary

This directory is a read-only index of historical and upstream knowledge. Its entries are not automatic requirements for a new problem. The executable core contract lives in `AGENTS.md`, `schemas/`, and `scripts/`; competition-specific choices must be explicitly activated as an optional preset under `planning/presets/` and remain subordinate to the current problem contract and human decisions.
