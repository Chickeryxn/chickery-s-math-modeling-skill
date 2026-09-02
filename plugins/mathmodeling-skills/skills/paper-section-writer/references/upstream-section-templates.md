# Upstream section templates (self-written)

Self-written distillation of abstract/introduction structure ideas from [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) (Apache-2.0 rules live at `references/upstream/nature-writing/`); no upstream text copied here.

## Abstract (three patterns)

- **V1 (question-driven)**: 背景缺口 → 本工作解决的问题 → 方法一句话 → 关键定量结果 → 意义。
- **V2 (result-driven)**: 方法名+对象 → 主要指标与对比数字 → 稳健性 → 局限一句。
- **V3 (hybrid, contest style)**: 每问必有一数；问题一→方法→结果，逐问推进；末句给总体结论与适用范围。

Contest rule: every subquestion must carry at least one number in the abstract.

## Introduction

Part A: 问题背景与主办方要求（引用题目附件）；Part B: 现有方法/基线及其不足（可引用 `related-paper-analyzer` 产物）；Part C: 本工作路线与贡献（贡献须为人工确认，见决策账本）。

## Paper-card evidence system (condensed)

For each claim record: claim ID → frozen value/source → robustness support → human decision ID → figure/table ref → limitation. Use evidence labels `[Paper]/[External]/[Analysis]` to keep provenance honest. A claim with no source is a blocker, not a draft.

## Usage

- These are structural guidance; numbers and interpretations must come from the per-subquestion `results/Qx/reports/frozen_numbers.json` and the decision ledger.
- See `references/upstream/nature-writing/` for the full rule files (main-text-discipline, terminology-ledger, consistency-sweep).
