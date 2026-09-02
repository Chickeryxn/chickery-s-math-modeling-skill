# 工作记录树（Work Record Tree）

> 目标：在现有机器可读契约（manifests、决策账本、run_summary、lineage、frozen_numbers）之上，增加一层**人类可读、证据链接的详细过程日志**——一个文件夹（`records/`）下多级 Markdown 文档组成的记录树。
> 定位：**advisory 叙事层**。记录树不参与门禁判定，不增加任何门禁要求；它把"agent 做了什么、产出什么、人类做了什么决定"按时间与主题组织成可回看的叙事。
> 与 AGENTS.md"不要仅为证明技能运行而创建文件"的边界：记录层不是"技能运行证明"，而是**人类回看与复盘的过程叙事**——只在有真实内容（做了什么/产出什么/人类决定）时记录；纯"调用了某技能"式的空条目不应写入。

## 一、树结构

```text
records/
├── README.md            # 索引/总览（work_record.py index 重建；check 校验同步）
├── sessions/            # 会话流水：YYYY-MM-DD-SSS.md
├── subjects/            # 子问题叙事：Q1.md
├── gates/               # 门禁迁移时间线：Q1.md
├── decisions/           # 决策摘要卡：YYYY-MM-DD-Qx-<decision_id>.md
└── retros/              # 复盘：YYYY-MM-DD-<slug>.md
```

- `sessions/`：一次会话一篇；条目格式 `## HH:MM:SS - <做了什么>`，后跟产物链接（`- 产物: [path](path)`）、子问题、标签。同一天多次 `log` 追加到同一篇。文件名 `YYYY-MM-DD-SSS.md` 中 `SSS` 是当天的三位序号（`001` 起）；同一天后续 `log` 会继续追加到该文件，因此 `002` 等序号只会在新的一天出现（自动回放草稿以 `-replay` 后缀独立成篇，不占序号）。产物链接统一以仓库根为基准书写，`work_record.py log` 会自动加上相对 `records/sessions/` 的 `../../` 前缀，保证 Markdown 点击可打开。
- `gates/`：每子问题一篇表格（时间 | 门禁 | 证据 | 备注），`gate` 命令拒绝门禁回退与缺失证据。
- `decisions/`：每张决策卡从 `methods/Qx/qx_decisions.jsonl` **镜像**（选择/理由/证据/来源原话原样引用），找不到账本记录时拒绝生成——AI 不得编造。
- `subjects/`：每子问题一篇叙事，供人工/agent 按 G1→G6 汇总（可手工整理，不强制）。
- `retros/`：复盘骨架（背景/关键决策回顾/被验证或被推翻的判断/可迁移要点/下一步），可与 `python scripts/learning_summary.py .` 对接。

## 二、命令

```powershell
python scripts/work_record.py init [root]                       # 建树（幂等）
python scripts/work_record.py log "<文本>" [root] [--subject Qx] [--artifacts a b] [--tags t1 t2] [--runtime codex|claude|dsh]
python scripts/work_record.py gate Qx <G#> [root] --evidence p1 p2 [--note "..."]   # G1..G6 / G2.5
python scripts/work_record.py decision Qx <decision_id> [root] [--ledger 路径]       # 从账本镜像决策卡
python scripts/work_record.py retro "<标题>" [root]                                  # 复盘骨架
python scripts/work_record.py replay [root] [--date YYYY-MM-DD] [--write]            # 从工件回放会话草稿
python scripts/work_record.py index [root]                       # 重建 records/README.md
python scripts/work_record.py check [root]                       # 校验：索引同步/链接/时间单调/门禁不回退
```

- `replay` 从 `planning/manifests/`、`methods/*/q*_decisions.jsonl`、`results/*/experiments/*/run_summary.json`、`results/*/reports/frozen_numbers.json` 自动生成当日会话草稿：默认打印到 stdout，`--write` 写入 `sessions/YYYY-MM-DD-replay.md`（frontmatter 标记 `replay: true`，`log` 不会误追加到草稿文件）。草稿供人工/agent 审阅补注，**不替代正式记录**。

- `--runtime` 缺省自动探测：DSH 会话（`$env:DSH_SESSION_ID`）→ `dsh`；Claude 环境 → `claude`；否则 `codex`。
- 退出码：0 PASS / 2 FAIL（与其余校验脚本一致）。

## 三、记录纪律

- **只记事实**：做了什么、产出哪些工件、人类做了哪些决定；人类理由一律从账本镜像，绝不代写。
- **链接不复制**：条目引用仓库内相对路径的工件，不把工件内容抄进记录树。
- **advisory**：记录缺失不得阻塞任何工作；`check` 失败只提示补 `index`，不构成门禁。
- **judgment digest（可选）**：`records/session-digests/` 可放一行式对话内摘要（judgment-bearing 的决定要义 + 路径），供 `replay` 与复盘补充原料；仍是 advisory，不替代正式记录。
- 与 `logs/`（失败/复现用控制台日志，按 AGENTS.md 仅在需要时创建）区分：记录树是结构化过程叙事。
- 三运行时（Codex / Claude / DSH）行为一致；`work-logger` 技能负责指导 agent 何时记、记什么。

## 四、与现有契约的关系

| 层 | 载体 | 谁写 |
|---|---|---|
| 机器可读契约 | manifests、`qx_decisions.jsonl`、run_summary、lineage、frozen_numbers | 校验器强制 |
| 过程叙事（本树） | `records/` | agent 按 `work-logger` 纪律写，人工可改 |
| 复盘 | `learning_summary.py` + `records/retros/` | 从账本/冻结数生成骨架，教训人工填 |
