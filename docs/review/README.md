# 全仓库审阅报告 · 全流程交互流程图册

> 审阅对象：本仓库（数学建模竞赛 AI 工作流技能库，v0.9.1 基线）。
> 审阅方式：全量文件盘点（409 个文件）＋四路并行深度审阅（政策文档 / 32 技能 / 34 脚本与 schema 与测试 / 模板·资源库·插件·上游资产）＋本机真实运行仓库自检（271 用例全绿，1 skip）。
> 制图：Archify（workflow v2，zh-CN）。七张图均通过 archify 9 项校验与桌面四视口视觉验证（无滚动溢出、正文可读）。

## 一、完整审阅报告

[`00-审阅报告.md`](00-审阅报告.md) —— 三层契约体系、32 技能分组、34 脚本盘点、G1–G6 门禁语义、配置双轨、宿主矩阵、实测记录、审阅观察与全部使用流程清单。

## 二、交互流程图册（1 张总览 + 6 张超长分流程图）

交互 HTML 使用内嵌 SVG/CSS/脚本，**自包含、离线可用**；支持明/暗主题、缩放平移、搜索、节点聚焦、连线追踪与 PNG/SVG/WebM 导出。

| 图 | 覆盖使用流程 | 静态预览 | 交互版（本地打开） | JSON 源 |
|---|---|---|---|---|
| 00 总览全景 | 全部流程一览与导航 | ![总览](assets/00-overview.png) | [00-overview.html](00-overview.html) | [sources](sources/f0-overview.workflow.json) |
| F1 接入与赛题启动 | 三宿主打开 / 双配置开关 / 隔离自检 / 读题链四技能 / 框架裁决 | ![F1](assets/01-launch.png) | [01-launch.html](01-launch.html) | [sources](sources/f1-launch.workflow.json) |
| F2 单子问题六门禁 | G1→G2→G2.5→G3→G4→G5/G6 全部技能/证据/校验/人类裁决/双轨 | ![F2](assets/02-gates.png) | [02-gates.html](02-gates.html) | [sources](sources/f2-gates.workflow.json) |
| F3 论文装配与提交 | writer 三前置 → 图链 → 写作润色 → G6 三审 → 装配预检 → 编译授权 | ![F3](assets/03-paper.png) | [03-paper.html](03-paper.html) | [sources](sources/f3-paper.workflow.json) |
| F4 训练模式闭环 | 资源库 → 闭卷 → 开卷对照 → 六维计分 → 人类挑方向 → 下一轮 | ![F4](assets/04-training.png) | [04-training.html](04-training.html) | [sources](sources/f4-training.workflow.json) |
| F5 记录·复盘·沉淀 | records 树与 work_record 命令 / 赛后判定 / learning_summary / 归档 | ![F5](assets/05-records.png) | [05-records.html](05-records.html) | [sources](sources/f5-records.workflow.json) |
| F6 维护·同步·分发 | 契约编辑纪律 / 四树同步 / 全量校验 / CI 8 步 / 版本与宿主差异 | ![F6](assets/06-maintenance.png) | [06-maintenance.html](06-maintenance.html) | [sources](sources/f6-maintenance.workflow.json) |

## 三、怎么查看

- **GitHub 文件页**：优先看静态预览 PNG（HTML 需下载后在浏览器打开才能交互）。
- **本地交互查看（推荐）**：克隆仓库后直接用浏览器打开本目录的 `index.html`（或任一 `0*.html`）。
- **在线交互查看（可选）**：将仓库 `docs/` 目录配置为 GitHub Pages 发布目录，即可在线访问交互版（图自包含、无外部字体依赖）。
- **二次编辑**：用 Archify 加载 `sources/*.workflow.json` 修改后重新导出 HTML / SVG / PNG（Node ≥ 18）：

```bash
node <archify>/bin/archify.mjs deliver workflow sources/f2-gates.workflow.json f2-gates.html --quality standard --json
```

## 四、口径与边界

- 图与报告为**通用工作流说明**，不含任何具体赛题数据、模型结果或论文结论。
- “AI 负责机械正确性、人类拥有建模判断”是所有图的隐含主线：人类裁决点（G2.5 选型 / G4 判定 / 签核 / 提交授权）均须在磁盘留痕（`source` 原话）。
- 门禁与审计是质量保障，不构成对竞赛成绩或论文结论的担保。
- 更新日期：2026-09-03。
