---
name: decision-prompt-builder
description: Build one compact choice card at a genuine mathematical-modeling judgment point. Use before method screening, after a meaningful experiment, or before final claim/freeze approval so the human chooses the trade-off while AI handles mechanical consequences.
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
3. Add `都不合适 / 补充约束` when the listed options may not cover the user's intent.
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
- D. 都不合适 / 我补充约束。
```

## After a meaningful experiment

Use computed evidence to ask:

- proceed with the current main method;
- adjust a stated assumption or parameter and rerun;
- activate the recorded fallback.

Name the consequence and evidence for each option. Do not silently convert an AI metric preference into the human verdict.

## Before final freeze

Use only when claim scope or confidence is genuinely judgment-bearing:

- keep the claim;
- downgrade it;
- drop it.

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
