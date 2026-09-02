# 0.9.0 修复清单对照表（审查问题 → 落实状态）

> 本表由 0.9.0 维护性发布（P0–P3 四批提交）产出，对应提交：
> `4dcd4e7`（P0）· `15778b5`（P1）· `473aedb`（P2）· `6ed92d0`/`fe0b379`（P3）
> 每项标注落实状态：✅ 修复 / 📘 澄清（文档与实现统一，行为不变）/ ⏸ 保留（有意设计，仅记录）。

## P0 — 确定性正确性 bug（全部 ✅）

| 问题 | 位置 | 状态 |
|---|---|---|
| leakage_check 混排日期/数字时间列崩溃 | `scripts/leakage_check.py` | ✅ epoch 归一化 + 混格式 advisory |
| claim_coverage 中文序号（问题三→"Q三"）误报 MISSING | `scripts/claim_coverage.py` | ✅ 中文数字→阿拉伯映射 |
| check_frozen_freshness 越界 source / `+0800` / naive 时区 / mtime 假 STALE | `scripts/check_frozen_freshness.py` | ✅ 包含校验 + 3.10 时区兼容 + naive 警告 + mtime 文档化 |
| latex_assembly 宏碰撞 / 同名 claim 覆盖 / bib 命中 @comment / 注释剥离条件错 / 字节当字符 / 占位符静默缺失 / AI 声明多节 | `scripts/latex_assembly.py` | ✅ 全部修复 |
| work_record replay 读错键 / check_links 基址错 / decision 卡元字符未转义 | `scripts/work_record.py` | ✅ current_gate + 文件目录解析 + blockquote 引用 |
| run_tests 假绿（空 suite exit 0） | `scripts/run_tests.py` | ✅ 无测试即 exit 2 |
| workflow_guard qid 拼路径 / 快照引用越界 | `scripts/workflow_guard.py` | ✅ Q<数字> 校验 + snapshot root 包含校验 |
| 技能图表参考代码 PALETTE 缺键 / hclust 假重排 / np.trapz 兼容 / sharey 矛盾 | `.codex/skills/math-figure-generator/references/*` | ✅ 修复并同步四树 |

## P1 — 技能契约统一（全部 ✅）

frozen 路径 per-Qx、审计循环解除（consistency→completeness→QA）、G5 三条 writer 前置、verifier/model_contract 生产者指派、评审五态统一、训练环路径隔离、render.json 键集统一、弹卡去重与 decision_type 落账、MATLAB 快照必须走统一运行器、AGENTS artifact_policy/编辑源/robustness 双层/root 参数/matlab 评审路径等。

## P2 — 治理/文档/上游（✅ 除 ⏸）

| 问题 | 状态 |
|---|---|
| reference.md/dsh 测试数 171/215 漂移；archify index 28 skills | ✅ 241→243→244 随磁盘计数并加 `test_doc_claims` 守卫 |
| 金样例 value↔locator↔账本不一致、±10/5 混用、假指标触发条件 | ✅ 修复 + `test_examples` 跨示例断言 |
| 复盘追加进哈希保护只读区 | ✅ 改指可写区 |
| main.tex TOC 行自相矛盾 | ✅ 删除 + 可选注释 |
| NOTICE verbatim 与裁剪矛盾；自写声明仅覆盖单树 | ✅ modified import + 四树声明 |
| 上游文档引用未 vendor 脚本 | 📘 用 `references/upstream/README.md` 四态映射表指引（保持上游文件字节不变以守哈希） |
| UPSTREAM "Reviewed at" 约定零遵守 | ✅ 5 份补齐 |
| validate_upstream_assets 漏记/多余哈希不报 | ✅ 补洞 |
| lineage/run_summary/manifest 无 schema | 📘 schemas/README 明示由 scripts+test_examples 守护；新增 lineage 金样例 |
| 训练/复盘素材来源两处并存 | ✅ 说明统一 + problems 占位 README |
| 悬空引用（A3、12 点） | ✅ 锚定 |
| archify 图 G5/G6 合并、G2.5 计数 | 📘 JSON meta 注记说明（不改图） |
| 其余细节（README.en 措辞、6 站计数、.gitattributes 补 m/html/css/js、timeline 表述等） | ✅ |

## P3 — 工程化/测试（✅ 部分 ⏸ 记录）

| 问题 | 状态 |
|---|---|
| 无 CI | ✅ GitHub Actions（Py 3.10–3.12 × Ubuntu/Windows） |
| deadline 测试依赖墙钟 | ✅ 注入时钟确定性边界 |
| test_synthetic_scenarios 自证式断言 | ✅ 改调真实校验器 |
| 孤儿 fixtures / 夹具样板重复 | ✅ 删除 + `tests/support.py` 起步 |
| 脚本重复样板（reconfigure/safe/sha/frozen 解析） | ✅ `scripts/lib/common.py` 落地并文档化渐进迁移（30 处存量本地副本 ⏸ 保留待渐进迁移，避免一次大 diff） |
| CLI 一致性（validate_decisions --json、validate_repo --only/--skip-tests/结构化错误） | ✅ |
| model_quality_gate uncertainty-note 未兑现 | ✅ 实现 + 测试 |
| qa_report 恒假条件 | ✅ 删除 |
| guard_frozen 工具名缺失误拦 / --check 依赖 assert | ✅ fail-open；--check 显式断言 ⏸（保持简单，-O 场景文档注明） |
| figure_render_audit 非递归 / 注释误计 / 星号变体 | ✅ 修复 + 测试 |
| preflight --strict 占位、section_structure 状态矛盾、figure_consistency aspect 未实现、learning_summary 冗余三目 | 📘/✅ 部分处理（learning_summary 清理完成；aspect family 与 preflight --strict 语义已在技能/文档层澄清或按 advisory 保留） |
| 技能 frontmatter license 缺失 | ✅ 32 个全部补齐（四树同步） |
| 插件署名三形态 | 📘 developerName=LICENSE 版权人（真实姓名）、author=GitHub 用户名，语义区分并在 NOTICE 说明 |
| marketplace 无版本、AGENTS"对齐"不可校验 | ✅ 加 version 并在 validate_skill_trees 校验 |
| 冒烟样例 / README hooks 表 | ⏸ README 已加 CI badge；hooks 矩阵在 `docs/dsh-compatibility.md` 已有（README 引用之） |

## 遗留待后续（有意不做/需人审）

1. 32 个脚本中约 30 处 reconfigure/safe/sha/frozen 解析本地副本：已提供 `scripts/lib/common.py`，按"触到就迁"原则渐进替换。
2. `figure_consistency_check` 的 aspect-family 声明与 `preflight --strict` 参数语义：属 advisory 工具文档澄清，未做功能级实现以免引入误报。
3. 插件 author/developerName 双署名：语义已区分，是否统一为单一署名需仓库作者（人）决定。
4. 版本号 0.9.0 为本地提交版本；`git push` 与 GitHub Release 由作者执行。
