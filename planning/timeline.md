# 竞赛时间预算模板（Timeline）

> 用途：把 72 小时（国赛）/ 96 小时（美赛）拆到 6 个门禁阶段，防止"前期磨蹭、后期赶工"。按你的 `rigor_profile`（lean/submission）调整密度；`learning` 模式提问多，各阶段适当放宽。
> 记录方式：在 `planning/session_config.json` 同级放 `planning/timeline.md`，每阶段实际用时写在"实际"列；严重超支时回看 `docs/post-contest-review.md` 归因。

## 时间预算表（以 72h 为例；96h 可按比例 ×1.33）

| 阶段 | 门禁 | 建议预算 | 检查点（过门禁前必须完成） | 实际 |
|---|---|---|---|---|
| 读懂题目 | G1 | 3–4h | `problem_parse.json` 齐、每个 Qx 有明确输出、人工框架决策入账本 | |
| 数据与画像 | G1 内 | 2–3h | `data_profile.json`（缺失/不平衡/集中度）、清洗动作可解释 | |
| 选方法 | G2 | 3–4h | 方法卡 + 风险探针（PASS/CONDITIONAL）、对比证据表 | |
| 人工选型 | G2.5 | 1h | `qx_decisions.jsonl` 有 DECIDED method_choice（绑定原话） | |
| 代码与实验 | G3 | 12–16h | 主方法+基线跑通、run_summary 完整、五项评审通过 | |
| 结果判定与冻结 | G4 | 3–4h | 结果/稳定性/声明范围人工判定、`model_quality_gate` 通过、冻结数字 | |
| 论文 | G5 | 12–14h | 摘要每问必有一数、`claim_coverage` 全 PASS、图渲染校验 | |
| 三审与提交 | G6 | 3–4h | 一致性/完整性/QA 三审通过、`ai_trace_checker` 干净、`latex_assembly --check-only --strict` | |
| **机动** | — | **剩余** | 缓冲：复现、补图、打磨摘要 | |

## 纪律

1. 每个阶段结束**先过门禁再推进**（门禁由证据派生，不能跳过）。
2. 单阶段超支 ≥ 计划 50% 时：停 5 分钟，判断是"该阶段的必要深化"还是"陷进去了"——后者立即降级（如 lean 模式砍报告）。
3. 最后 6 小时只做**三审 + 提交物**，不新增实验。
4. 用 `scripts/workflow_guard.py . derive Qx` 看当前门禁，配合上表判断进度；`next_stage_hint` 会提示下一阶段。
