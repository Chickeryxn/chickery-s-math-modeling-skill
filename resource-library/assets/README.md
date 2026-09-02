# assets/ —— 其它素材

放训练所需其它素材：赛题文件、题解范例、可复现数据、通用复现脚本等。规则同其它目录：**素材 + 说明**，登记进 `index.json`。

结构（支持目录由 `scripts/resource_index.py` 归入 `supporting`）：

```text
assets/
├── problems/   # 赛题文件（.txt/.pdf），供 planning/training_config.json 的 problem_source 指向
├── data/       # 可复现数据/可视化数据
├── code/       # 通用复现脚本（python/matlab/其它）
└── figures/    # 可复现示例图
```

## 说明模板（每条素材一份说明，必填/选填）

```markdown
- **category**：assets
- **entry_id**：<唯一 id>
- **source**：<出处>                         （必填）
- **类型**：赛题 / 数据 / 脚本 / 图 / 其它
- **用途**：<在训练闭环或 problem_source 中的用途>
- **is_problem**：<是否赛题；若是给出 training_config.problem_source 指向>   （选填）
- **rights**：<有权使用/来源标注>            （必填）
- **tags**：<关键词>

## 内容说明
- <文件是什么、怎么用、放在哪（content/data/code/figures）>

## 完整性自检清单
- [ ] 说明含"用途"与"来源"
- [ ] 是赛题则已注明 problem_source 指向
- [ ] 素材有权使用并标注来源
- [ ] 已登记：`python scripts/resource_index.py .`
```
