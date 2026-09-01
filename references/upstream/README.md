# references/upstream —— 上游融合知识资产

本目录是**经审核的上游知识资产层**，供各技能按需引用。定位与 `references/` 一致：**advisory 参考，不是自动要求**；不改变本仓库治理契约（AGENTS.md / schemas / scripts）。

## 来源与许可证总表

| 子目录 | 来源仓库 | 固定 commit | 许可证 | 引入内容 | 状态 |
|---|---|---|---|---|---|
| `nature-figure/` | [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) | `ebd722e` | Apache-2.0 | 图契约/QA/设计理论/PALETTE/多面板架构 | 逐字引入（保留声明） |
| `nature-writing/` | 同上 | `ebd722e` | Apache-2.0 | 润色/写作/统计/共享规则 + check_consistency.py | 逐字引入（保留声明） |
| `lupynow-writing/` | [Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills) | `3a9428c` | MIT | 去 AI 味/四轮自审/句式库/Figure Contract/决策矩阵 | 逐字引入（保留版权行） |
| `method-index/` | 综合（XiaoMaColtAI 等） | — | MIT（自写） | 方法家族索引 + 门禁映射/稳健性清单 | 自写（clean-room） |

## 校验

`python scripts/validate_upstream_assets.py .` 校验：
- 每个子目录存在 `UPSTREAM.md`，且含 `Source repository`、`License`、`Imported files` 字段；
- 清单中声明的文件真实存在；
- 许可证声明属于允许集合（`MIT` / `Apache-2.0` / `self-authored`）。

## 使用约定

- 技能引用时用相对路径（如 `../../references/upstream/nature-figure/figure-contract.md`）。
- 不修改被引入的上游文件内容；如需改编，复制到技能自己的 `references/` 再改并在头部注明来源。
- 上游规则中的数字/断言（如"However 51 ≫ Furthermore 22"、Nature 图注 <250 词）为语料/历史统计，引用时标注时点。

## 明确未引入（许可证或边界原因）

- XiaoMaColtAI：根目录无 LICENSE；`tools/docx|pdf|xlsx` 为 **Anthropic 专有**；算法库 438KB（无许可证）——一律不复制。
- sci-box：仓库根无 LICENSE；图模板含硬编码论文出处——不复制，仅作理念启发。
- CUMCMThesis：无 LICENSE——模板不 vendor，见 `docs/paper-build.md` 的构建期外部依赖说明。
- nature-skills `figures4papers` 资产：无许可证，禁止复制。
- 一切网络执行（MCP/搜索 API/下载器）与外部运行时：不入核心。
