---
name: decision-prompt-builder
description: Build one compact choice card at a genuine mathematical-modeling judgment point. Use before method screening, at the G4 result-judgment round (result/stability/claim-scope verdicts in lean and submission), or at freeze approval so the human chooses the trade-off while AI handles mechanical consequences.
license: MIT
whenToUse: At a genuine modeling-judgment point (before screening, G4 result judgment after experiments and robustness checks, or freeze/package sign-off) when the human must choose a trade-off.
---

# Purpose

Ask the smallest useful question that only the human modeler can answer. Present mutually exclusive options with consequences; do not turn mechanical checks into user questions.

# Inputs

- Current gate and the judgment it needs.
- Problem goal, required output, hard constraints, and available evidence.
- `planning/session_config.json`.
- Existing decisions in `methods/Qx/qx_decisions.jsonl`.

# Configuration

- Read `interaction_mode`; accept legacy `mode` for compatibility.
- `learning`: show 2–3 short questions and withhold the AI suggestion until the user answers.
- `speed`: show one compressed question and optionally show the AI suggestion alongside.
- `rigor_profile` does not change who owns the judgment.

# Choice-Card Workflow

1. Identify one load-bearing judgment.
2. Create 2–3 mutually exclusive options. Each option must state its practical consequence.
3. Add `都不合适 / 补充约束` (exactly this wording everywhere) when the listed options may not cover the user's intent.
4. Ask no more than three questions in one card.
5. Do not recommend an option in `learning` mode before the answer.
6. Pass the answer verbatim to `modeler-decision-logger`; do not create a per-skill pending decision file.

# Batch Cards (speed mode)

When several subquestions need the same question type (e.g. output form for Q1/Q2/Q3), one matrix card may ask the identical question once per subquestion in `speed` mode. Keep the decisions independent: each subquestion answer is captured as its own record with its own `decision_id` and verbatim source; never infer one row's answer from another row.

# Rationale Sentence Frames

A card may attach an optional fill-in frame such as "我选 X 是因为 ____，并能接受 ____ 代价。" Frames help the human produce a defensible one-sentence rationale; they are prompts, never substitutes — you must not fill in the rationale yourself.

# Standard Cards

## Before method screening

Ask only the missing high-impact items:

- output form to defend;
- interpretability/performance priority;
- unacceptable failure;
- experiment budget.

Do not ask the user to choose an algorithm name before evidence exists.

Example:

```markdown
请选择这轮方案的首要取向：

- A. 可解释性优先——方法更透明，但可能牺牲部分拟合效果。
- B. 平衡——接受中等复杂度，要求能解释且优于可信 baseline。
- C. 性能优先——允许更复杂的方法，但需要额外稳健性和解释工作。
- D. 都不合适 / 补充约束。
```

## 口径正交化确认（G1 framing; caliber orthogonalization）

Run at G1 framing (first parse, before method screening) when the problem has a **caliber/definition** dimension that is ambiguous. Confirms the three **orthogonal** axes and records each independently through `modeler-decision-logger` as `decision_type: framing_caliber` (into `planning/framing_decisions.jsonl` or the subquestion ledger).

Full option list + consequences + rationale: `references/framing-caliber.md`. Present **as many options as feasible** per axis, each with its practical consequence, plus `都不合适 / 补充约束`. Do **not** conflate the axes into one question; each is chosen and recorded separately. Example card:

```markdown
请确认题目口径（三根轴互相正交，请各自独立选择）：

【口径1 · 判据粒度】按什么粒度套用/计数判据？
- A. 逐子问题
- B. 逐对象/逐实体   - C. 逐类别/逐类型   - D. 逐时段/逐阶段
- E. 逐方案/逐策略   - F. 整体(汇总)       - G. 分层(先子后汇)
- H. 极值/最劣        - I. 分布/概率        - J. 阈值/达标
- K. 波动/灵敏度      - L. 可加总 vs 不可加总 - M. 综合评分
- N. 占比/人均        - O. 都不合适/补充约束

【口径2 · 服务关系】服务/指派/覆盖的实体关系是？
- A. 一对一(1:1)  - B. 一对多(1:N)  - C. 多对一(N:1)  - D. 多对多(N:M)
- E. 全覆盖/无遗漏 - F. 部分覆盖/可拒绝 - G. 顺序/排队   - H. 分层/级联
- I. 共享/竞争     - J. 可替换/多源   - K. 优先/加权     - L. 双向/互惠
- M. 离散 vs 连续强度 - N. 时间窗/时段 - O. 不适用       - P. 都不合适/补充约束

【口径3 · 总指标】多值合并成总指标时如何加总？
- A. 求和   - B. 加权和   - C. 平均     - D. 加权平均   - E. 最大值
- F. 最小值/最劣 - G. 极差/波动 - H. 排序/名次 - I. 达标率/覆盖率
- J. 效用/多目标 - K. 期望/风险  - L. 比率/效率  - M. 增长/变化率
- N. 罚函数/正则 - O. 归一化后汇总 - P. 综合评分   - Q. 都不合适/补充约束
```

Rules: each axis is a fully-human framing judgment (no AI recommendation in `learning` mode); the three axes are independent; record one `framing_caliber` record per axis; do not turn a mechanically determinable caliber into a user question.

## G4 result judgment (after the meaningful experiments and the robustness checks)

Run this round in BOTH `lean` and `submission`: the gate engine requires the
three verdicts below (recorded as `result_verdict`, `stability_verdict`,
`claim_scope`) before the workspace can leave G3 — none is optional and none
may be deferred to freeze. One card of up to three questions is enough (see
workflow rule 4); ask only the verdicts whose records are missing from
`methods/Qx/qx_decisions.jsonl`.

- Result verdict (`decision_type: result_verdict`): proceed with the current
  main method / adjust a stated assumption or parameter and rerun / activate
  the recorded fallback.
- Stability verdict (`decision_type: stability_verdict`): whether the
  robustness evidence supports the result and the intended claims (stable
  enough / not stable — adjust, rerun, or downgrade claims). Robustness
  evidence may come from `robustness-checker` or, in lean, from the observed
  run/seed behavior.
- Claim scope (`decision_type: claim_scope`): which claims the results support
  — keep / downgrade / drop.

Name the consequence and evidence for each option. Do not silently convert an
AI metric preference into the human verdict.

## Freeze / package sign-off point (`submission` only)

The package sign-off card (`decision_type: package_signoff`) and the AI-use
submission authorization (`decision_type: submission_authorization`) belong to
`solution-package-builder`'s package workflow (it asks for the sign-off and
records both through `modeler-decision-logger`). If that skill routes the card
through you, ask exactly the missing one — do not emit both back to back, and
do not invent the package sign-off yourself.

# Output

Return one `choice_card` block containing:

- `decision_id`
- `decision_type`
- `question`
- 2–3 options plus optional constraint override
- evidence paths
- the consequence of each option

Do not save the card unless another skill needs a durable prompt record.

# Rules

- Ask about trade-offs, not mechanically determinable facts.
- Prefer one card at a decision point; avoid repeated micro-confirmations.
- Do not pre-fill the user's choice or rationale.
- Do not mark a decision `DECIDED`.
- Do not require a prose essay. One evidence-linked sentence is sufficient when it captures the user's real reason.
- If there is no genuine human judgment, return control without asking a question.

# Verification

- Options are mutually exclusive and consequences are clear.
- The card is grounded in the current problem or computed evidence.
- No hidden recommendation appears in learning mode.
- No per-skill decision artifact was created.
