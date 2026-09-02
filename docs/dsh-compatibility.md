# DeepSeek Harness（DSH）0.7.0 适配报告与使用指南

> 本文档基于对 DSH 桌面版 0.7.0 内核源码的只读审计（包：`@deepseek-ai/dsh` 0.1.2-alpha.1 及 `dsh-skill`、`dsh-skill-filesystem`、`dsh-agent-instructions`、`dsh-hooks-*`、`dsh-sandbox-*` 等），结合本仓库全量文件审计，给出逐项适配性判定与使用方法。
> 结论先行：**核心工作流天然适配 DSH 0.7.0，无需改任何契约；本仓库已通过 `.agents/skills/` 第四副本实现"打开即用"。**

## 一、判定总表

| 区域 | 判定 | 依据（DSH 0.7.0 行为） | 本仓库处理 |
|---|---|---|---|
| 技能发现 | ✅ 天然适配 | 项目级根 `<仓库>/.agents/skills/<name>/SKILL.md`（rank 200）与 `<仓库>/.dsh/skills/`（rank 100）自动发现；frontmatter 仅要求 kebab-case `name` + `description` | 技能树新增 `.agents/skills/` 第四副本（`sync_plugin.py` 同步，`validate_skill_trees.py` 校验） |
| 仓库指令注入 | ✅ 天然适配 | 从项目根（`.git` 标记）向下逐目录加载 `AGENTS.md`/`CLAUDE.md`（+`.local` 覆盖），每文件 ≤1 MiB；README 不使用 | AGENTS.md 增补 DSH 运行环境小节；CLAUDE.md 一句话 |
| 脚本执行 | ✅ 可用 | 无内置 Python；`python`/`git` 需在 PATH（继承环境）；默认沙箱 `workspace-write` 可写仓库根与临时目录 | 文档化前置条件；脚本全部纯标准库、UTF-8 输出 |
| 决策账本 | ✅ 可用（约定） | 校验器仅要求 `user_message_id` 为非空字符串 | 约定 `dsh:<session_id>:<seq>`（`$env:DSH_SESSION_ID`）；不改校验器 |
| marketplace / plugin manifest | ❌ DSH 不支持 | 内核零命中；`.agents/` 仅作技能根 | 保留（Codex/Claude 必需，`validate_skill_trees.py` 强制）；DSH 不读取 |
| hooks（SessionStart 横幅） | ⚠️ 能力存在但默认不挂载 | `dsh-hooks-claude-code`/`dsh-hooks-codex` 桥存在，但所有内置组合零挂载 | 见下文"可选 hooks 补丁"（默认不启用） |
| 行尾/哈希同步 | ⚠️ 已加固 | 无 `.gitattributes` + autocrlf 混排有漂移风险 | 新增 `.gitattributes` 统一 LF + 4 树重同步验证 |
| 控制台编码 | ✅ 已加固 | 脚本强制 UTF-8；`validate_repo.py` 以 UTF-8/errors=replace 捕获子进程 | 保持 |
| 外部工具链 | ⚠️ 使用时需具备 | matplotlib+numpy（图技能）、xelatex（论文构建）、Node≥18（archify 再生成）、MATLAB/北太天元（可选） | 与 Codex/Claude 一致，"不入核心" |

## 二、DSH 技能发现机制（0.7.0 事实）

- 目录优先级（rank 越小越优先）：`<仓库>/.dsh/skills`（100）→ `<仓库>/.agents/skills`（200）→ `customSkillDirs`（300）→ `<DSH_HOME>/skills`（400，桌面版 `DSH_HOME` = `<userData>\harness`）→ `~/.agents/skills`（500，受 `$DSH_AGENTS_HOME` 影响）→ `$DSH_BUNDLED_SKILL_DIR`（600）。
- 技能文件形式：`<name>/SKILL.md`（资源基目录 = 技能目录）或扁平 `<name>.md`。
- frontmatter：必填 `name`（`/^[a-z0-9]+(?:-[a-z0-9]+)*$/`）+ `description`；可选 `whenToUse`、`metadata`、`disable-model-invocation`、`user-invocable`。缺 frontmatter/name/description 的文件被静默忽略。
- 会话目录只会在 agent preset 挂载了 `skill-filesystem`/`tool-skill` 时出现（`standard` preset 默认挂载）。

**结论**：把仓库克隆/打开为 DSH 工作区，`.agents/skills/` 下的 32 个技能即被自动发现，无需安装、无需配置。

## 三、仓库内已完成的适配

1. `scripts/sync_plugin.py`：同步目标 `[.claude/skills, plugins/.../skills, .agents/skills]`（`.codex` 为源）。
2. `scripts/validate_skill_trees.py`：4 树哈希一致性校验。
3. `AGENTS.md`："Repository Skill Copies" 更新为三独立副本 + 插件分发；新增 "Runtime Notes (DeepSeek Harness desktop 0.7.0)"：PROJECT_ROOT=工作区根、`dsh:<session_id>:<seq>` 消息 ID 约定、沙箱说明、python/git 前置、hooks 默认不生效、UTF-8 编码。
4. `CLAUDE.md`：指出 DSH 读取 `.agents/skills/`，运行细则见 AGENTS.md 与本文档。
5. `.codex/skills/workflow-orchestrator/SKILL.md`：AGENTS.md 引用改为位置无关（项目根优先；裸安装时回退同树打包副本或询问用户）。
6. `.codex/skills/modeler-decision-logger/SKILL.md`：明确 DSH 下 `user_message_id` 约定。
7. 新技能 `work-logger`（工作记录树，见 `docs/work-record.md`），4 树同步。
8. `scripts/work_record.py` + `tests/test_work_record.py`：过程日志工具（纯标准库，三运行时一致）。

## 四、使用指南（在 DSH 桌面版中使用本仓库）

1. 用 DSH 打开仓库根目录（`D:\...\chickery-s-math-modeling-skill`）；会话技能目录会自动出现 32 个技能。
2. 前置：确保 `python`（≥3.10）与 `git` 在 PATH。
3. 沙箱：默认 `workspace-write`（可写仓库根与临时目录）即可跑全部工作流；脚本若需写仓库外路径（如 `--out` 外部目录），需更高权限并说明理由。
4. 初始化自检：`python scripts/validate_repo.py .`、`python scripts/run_tests.py`。
5. 决策账本：`user_message_id` 填 `dsh:<$env:DSH_SESSION_ID>:<序号>`。
6. 工作记录：按 `work-logger` 技能执行 `python scripts/work_record.py ...`；会话后 `check` + `index`。
7. 图示再生成（可选）：archify CLI 需 Node ≥ 18，见 `docs/diagrams/archify/README.md`。
8. 论文构建（可选）：xelatex 与 CUMCMThesis，见 `docs/paper-build.md`。

## 五、可选：启用 SessionStart 守护横幅（hooks）

DSH 0.7.0 默认不挂载任何钩子；需要复现 Claude 版 `hooks/hooks.json` 的启动横幅时，在 `<userData>\harness\cordis.patch.yml`（即 `$DSH_HOME/cordis.patch.yml`）追加：

```yaml
# 挂载 Claude 钩子桥，指向本仓库的 hooks 配置
plugins:
  - id: "@deepseek-ai/dsh-hooks-claude-code"
    config:
      configPath: "<仓库绝对路径>/plugins/mathmodeling-skills/hooks/hooks.json"
```

或使用 Codex 桥（`@deepseek-ai/dsh-hooks-codex`，事件：SessionStart/UserPromptSubmit/PreToolUse/PostToolUse/Stop；仅同步命令钩子）。钩子经 shell 执行，JSON 载荷在 stdin；退出码 0=放行、2=阻断。**默认不启用**：零配置即可用完整工作流。

## 六、验证命令

```powershell
python scripts/validate_repo.py .                 # 仓库级总检（含 4 树）
python scripts/sync_plugin.py . --check           # 4 树哈希一致性
python scripts/validate_skill_trees.py .          # 4 树 + manifest 版本 + marketplace
python scripts/work_record.py check .             # 记录树一致性
python scripts/run_tests.py                       # 138 用例
```

## 七、边界与保留项

- DSH 不读取 `.codex-plugin`/`.claude-plugin`/`marketplace.json`/`hooks.json`——这些文件**保留**以服务 Codex/Claude，任何改动都必须过 `validate_skill_trees.py`。
- DSH 无内置 Python 运行器；一律经 pwsh 调 `python`，沙箱只限制写权限不限制执行。
- 限制性沙箱（read-only）下 pwsh 为 ConstrainedLanguage、受限进程派生 `stdio:'pipe'` 子进程会 EPERM——`create_run_snapshot.py` 的 `shell=True` 在 DSH 下经 cmd.exe 执行用户命令，属既有"命令字符串必须可信"契约（`scripts/README.md`）。
