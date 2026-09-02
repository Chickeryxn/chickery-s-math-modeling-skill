# Q1 Method Card（示例，正文理由可中文；机器锚点表头勿翻译）

> Machine anchors: keep the tokens `main_candidate` / `usable_baseline` and the
> section headers `Risk-probe summary` / `Baseline validity` anywhere in the
> card — the gate engine reads them. Body prose may be Chinese.

## Goal and success criteria

对 40 个城市按 12 项指标综合评价排序；要求权重客观、排序在 ±10% 权重扰动下 Top-10 稳定。

## Human constraints

- Output form: 每个城市的综合得分与完整排序，另附 Top-10 稳定性说明
- Priority: 可解释性优先（熵权-TOPSIS），可接受与更复杂模型的轻微性能差距
- Unacceptable failure: 排序完全依赖单一指标（权重主导）；分数无区分度
- Experiment budget: 全部候选共 ≤ 2 小时（探针 ≤ 10 分钟/方法）
- Complexity budget (why this complexity is needed): 客观赋权避免主观争议，方法在竞赛时间内可完整实现
- Interpretability need (who must be able to explain it): 队长需能在答辩中用一句话解释权重来源

## Shortlist

| ID | Role | Mathematical idea | Why eligible | Why not chosen (if not main) | Main risk | Implementation cost |
|---|---|---|---|---|---|---|
| M1 | main_candidate | 熵权定权 + TOPSIS 聚合 | 指标完整、权重客观可解释、输出为排序 | — | 指标冗余/权重主导 | 低 |
| M0 | usable_baseline | 等权归一化聚合得分 | 完全可完成排序任务、输出可比 | 等权默认所有指标同等重要 | 区分度弱 | 极低 |
| M2 | conditional_fallback | CRITIC 定权 + 灰色关联 | 能处理指标间相关性强的情形 | 与 M1 数学机制不同，仅当 M1 权重主导时启用 | 关联度解释复杂 | 中 |

## Rationale chain (teaching aid)

- Why this method fits the output form and data (assumption match): 熵权法以指标离散度定权，适合"无先验权重、指标量纲不同"的客观排序场景（数据画像显示 12 指标均为正向且无强线性冗余，见 probe）。
- Why the baseline is a fair comparison: 等权归一化给出同一输入下的直接可比排序与得分，机制上简单且可完成真任务。
- What would make this choice wrong (falsification condition): 若探针显示权重集中度>0.8（单一指标权重主导），或 ±5% 权重扰动下 Top-10 重叠<0.8，则 M1 不成立，改走 M2。

## Main-vs-baseline comparison evidence (G2)

| Dimension | Main candidate | Usable baseline | Note |
|---|---|---|---|
| Metric difference (probe) | Top-10 扰动重叠 0.92 | 0.85 | 量化而非形容词 |
| Complexity cost | ~30 分钟实现 | ~5 分钟 | 都在预算内 |
| Interpretability | 权重=信息量占比，可讲 | 等权默认，弱 | 答辩可解释 |
| Risk profile | PASS（degeneracy 检查通过） | PASS | 见 risk_probe_summary.example.json |

## Baseline validity

- Real task completed: 是（等权归一化可给出全部城市得分与排序）
- Comparable output/metric: 是（同一指标矩阵、同一得分口径）
- If no, classification: diagnostic_reference

## Risk-probe summary

| ID | Executability | Data/assumptions | Degeneracy | Sensitivity | Scale | Verdict |
|---|---|---|---|---|---|---|
| M1 | PASS (0.2s) | PASS（指标均正向、无共线超阈值） | PASS（CV=0.18，唯一得分 40/40） | PASS（±5% 权重扰动 Top-10 重叠 0.92） | PASS（40×12 秒级） | PASS |
| M0 | PASS (0.1s) | PASS | PASS（CV=0.12，得分区分度低于 M1） | PASS（±5% 扰动重叠 0.85） | PASS | PASS |

## Fallback trigger

- Trigger: M1 探针中权重集中度（最大权重占比）> 0.8，或 ±5% 扰动 Top-10 重叠 < 0.8
- Evidence to evaluate: 复用 risk_probe_summary.example.json 的 perturbation_sensitivity 与 output_degeneracy 输出；触发后先跑 M2 探针再提交 human choice

## Compact history

- 2026-09-02 示例：初建方法卡（对应决策示例 decisions.example.jsonl 中 method_choice-example）
