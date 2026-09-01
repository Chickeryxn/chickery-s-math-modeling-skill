# Archify 数学建模流程可视化

本目录收录由 [tt-a1i/archify](https://github.com/tt-a1i/archify) 生成的通用数学建模流程图，用于解释本仓库的工作区结构、门控流程、子问题状态和文档冻结链。

这些图是**通用工作流说明**，不代表任何具体竞赛题、模型结果或论文结论。

## 图示导航

| 图示 | 说明 | 静态预览 | JSON 源文件 |
|---|---|---|---|
| 工作区系统架构 | 展示 28 个 skills、调度层、人类决策区和产物目录 | [PNG](assets/mm-workspace-architecture.png) / [SVG 文件](assets/mm-workspace-architecture.svg) | [JSON](sources/mm-workspace-architecture.architecture.json) |
| 通用门控流水线 | 展示 G1–G6 从问题理解到最终审计的主流程 | [PNG](assets/mm-generic-workflow.png) / [SVG 文件](assets/mm-generic-workflow.svg) | [JSON](sources/mm-generic-workflow.workflow.json) |
| 门控生命周期 | 展示单个子问题在 G1–G6 之间的状态迁移和人工等待点 | [PNG](assets/mm-gate-lifecycle.png) / [SVG 文件](assets/mm-gate-lifecycle.svg) | [JSON](sources/mm-gate-lifecycle.lifecycle.json) |
| 文档生成与冻结链 | 展示从问题解析、方法、代码、实验到论文审计的证据链 | [PNG](assets/mm-document-chain.png) / [SVG 文件](assets/mm-document-chain.svg) | [JSON](sources/mm-document-chain.dataflow.json) |

交互 HTML 为生成物、不入库；需要时按下方"再生成"在本地生成（Node ≥ 18）。

## 查看方式

- GitHub 文件页：优先打开 PNG；SVG 文件仍保留用于下载和本地编辑，但部分 GitHub 页面可能无法正确渲染其中的字体或样式。
- 本地交互查看：按"再生成"用 archify CLI 生成 HTML，再用浏览器打开。
- 在线交互查看：将仓库的 `docs/` 目录配置为 GitHub Pages 发布目录后，静态预览（SVG/PNG）可在线访问；交互版需在部署前本地生成并纳入 `docs/`。
- 二次编辑：在 Archify 中加载 `sources/` 下的 JSON 文件，再重新导出 HTML、SVG 或 PNG。

## 再生成（CLI，需 Node ≥ 18）

仓库内已提交 JSON 源与静态产物（PNG/SVG）；修改 `sources/*.json` 后可用 archify CLI 在本地生成交互 HTML 并校验（archify 为外部工具，运行时零 npm 依赖，MIT 许可，建议锁定版本 2.16.0）：

```bash
# 校验 JSON 源（质量门 showcase：0 错误 0 警告，可入 CI 做门禁）
node <path-to>/archify/bin/archify.mjs validate workflow sources/mm-generic-workflow.workflow.json --quality showcase --json
# 本地生成交互 HTML（输出到 generated/，该目录不入库）
node <path-to>/archify/bin/archify.mjs deliver workflow sources/mm-generic-workflow.workflow.json generated/mm-generic-workflow.workflow.html --quality showcase --json
```

PNG/SVG 需在浏览器中打开生成后的 HTML，用 Viewer 的 Export 菜单导出（CLI 不直出位图）。更新提醒与 Google Fonts 外链为上游可选触点，可在集成时按需禁用。版本锁定的来源记录见 `NOTICE.md`（archify commit `7a16d30`，v2.x 线）。

生成的交互 HTML 使用内嵌的 SVG、CSS 和脚本，不依赖仓库外的本机文件或本地浏览器安装路径。HTML 中的在线字体仅是可选增强，系统字体回退仍可用。

## 来源与范围

- 生成工具：[tt-a1i/archify](https://github.com/tt-a1i/archify)
- 原始生成目录：本机的 Archify 导出目录（未随仓库发布）。
- 本次公开内容：四张通用流程图的 JSON 源、SVG 和 PNG（交互 HTML 按需本地再生成，不入库）。
- 未公开：生成过程诊断输出、含本机绝对路径的报告，以及任何具体赛题的专属方法架构图。

## 目录约定

```text
archify/
├── README.md
├── index.html
├── sources/       # 可编辑 JSON 源文件（入库）
├── assets/        # GitHub 预览用 SVG/PNG（入库）
└── generated/     # 本地再生成的交互 HTML（不入库；见 .gitignore）
```

更新时间：2026-08-31