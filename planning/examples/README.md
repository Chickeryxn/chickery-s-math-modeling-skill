# 金样例（planning/examples/）

> 本目录存放**填充完成（filled）的规范工件示例**，与各契约/SKILL 模板一一对应，供 agent 在真实竞赛中"照正样做"，也供学习者对照。所有示例为自包含演示（Q1=评价/排序、Q2=预测的合成题目），**不代表任何真实赛题结果**。
> 示例路径刻意避开仓库扫描器的真实 glob（不放在 `planning/parse/`、`planning/manifests/` 等），因此不会影响 `workflow_guard derive` 或 `qa_report` 对真实工作区的判定。

## 清单（工件 ↔ 契约/模板 ↔ 校验方式）

| 示例文件 | 对应工件 | 契约/技能 | 可独立校验 |
|---|---|---|---|
| `problem_parse.example.json` | `planning/parse/problem_parse.json` | `problem-parser` | 结构（含 `subquestions[*].goal/required_outputs`，满足 gate 深度检查） |
| `problem_classification.example.json` | `planning/classification/problem_classification.json` | `problem-classifier` | 结构（每 Qx 有 `primary_type`） |
| `method-card.example.md` | `methods/Qx/qx_method_card.md` | `method-selector` | `workflow_guard.method_card_ready`（机器锚点 + 无占位符，正文可中文） |
| `risk_probe_summary.example.json` | `methods/Qx/probes/risk_probe_summary.json` | `method-selector` / risk-probe-contract | `workflow_guard.risk_probe_ready`（PASS 方法含 `output_degeneracy`） |
| `decisions.example.jsonl` | `methods/Qx/qx_decisions.jsonl`（及 framing） | `modeler-decision-logger` | `python scripts/validate_decisions.py . planning/examples/decisions.example.jsonl`（以本目录为 root：`python scripts/validate_decisions.py planning/examples planning/examples/decisions.example.jsonl`） |
| `manifest.example.json` | `planning/manifests/Qx.json` | `workflow-orchestrator` | `python scripts/validate_manifest.py planning/examples planning/examples/manifest.example.json`（`current_gate: G1`，自洽） |
| `python_review.example.json` | `code/Qx/reviews/qx_python_review.json` | `python-code-reviewer` | 结构（五项命名检查均 PASS 且带 evidence） |
| `run_summary.example.json` | `results/Qx/experiments/roundN/run_summary.json` | `model-code-analyzer` | 结构（含 main/baseline/verifier 角色与 run_snapshot 引用） |
| `frozen_numbers.example.json` | `results/Qx/reports/frozen_numbers.json` | `solution-package-builder` | 结构（claims 含 source_file/frozen_at/decision_id） |

## 使用建议

- agent 产出前：加载对应示例作为"正样本"（例如写方法卡前看 `method-card.example.md` 的机器锚点与中文正文混排方式）。
- 教学：配合 `docs/learning-path.md` 各站使用。
- 校验示例是否腐坏：`tests/test_examples.py`（`python scripts/run_tests.py` 内含）会检查结构与锚点，README 中"可独立校验"列对应的命令应保持 PASS。

## 边界

- 需要真实工作区上下文的校验（`validate_artifacts` 的血缘对账、`qa_report` 的 manifest 驱动审计、`check_frozen_freshness` 的 mtime 新鲜度）**不适用于示例目录**——示例文件路径是自引用的教学材料，不模拟真实门禁推进。
