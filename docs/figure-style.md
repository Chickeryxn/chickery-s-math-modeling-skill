# 附属项目接入：chickery-figure-style（图美观风格，可选配置）

> 本仓库（chickery-s-math-modeling-skill）是**主项目**；[chickery-figure-style](https://github.com/Chickeryxn/chickery-figure-style) 是它的**附属项目**——被设计成能被用户**简单、直接地配置进主项目**，用于统一"顶刊审美"作图风格。

## 一、为什么是附属项目
- **主项目**承载整套建模工作流与技能树；其绘图技能(如 math-figure-generator)与 `resource-library/figures/` 是"审美标准"的家。
- **附属项目**把上面这套审美规范打包成"**可选择配置**"的独立分发（预设 + 风格技能 + `tjstyle.py` + 示范图库 + 插件清单），可单独安装，也可一键织入主项目。

## 二、接入后你在主项目里拿到什么
在主项目 `resource-library/figures/` 下即已内置（无需附属仓库也能用）：
- `topjournal-style/` —— 审美规则（`README.md`）+ 可选配置（`scripts/figure_style_config.json`）+ 风格模块（`scripts/tjstyle.py`）。
- `exemplar-occlusion-3d-2025a/`、`exemplar-thickness-spectra-2025b/`、`exemplar-nipt-multipanel-2025c/` —— 三组**成图模范**（png+pdf+render.json+生成脚本）。

## 三、如何"直接配置"附属项目（任选其一，按最简单）
- **A. 已内置（零配置）**：直接克隆主项目即得以上内容；作图时 `import tjstyle`（把 `resource-library/figures/topjournal-style/scripts` 加入 `sys.path`）并读 `figure_style_config.json` 选预设。
- **B. 作为子模块（正式附属，保持同步）**：
  ```bash
  git submodule add https://github.com/Chickeryxn/chickery-figure-style plugins/chickery-figure-style
  git submodule update --init --recursive   # 克隆主项目后拉取附属
  ```
  （此后主项目锁定附属某次提交，`git submodule update` 升级。）
- **C. 作为独立插件（Codex/Claude/DSH 可选安装）**：把 `chickery-figure-style` 克隆/作为工作区打开，其 `.agents/skills/figure-style` 与 `.agents/plugins/marketplace.json` 会被宿主自动发现/可选安装；或在主项目的 `.agents/plugins/marketplace.json` 追加一条指向该附属的 `plugins` 入口。
- **D. 手动拷贝（一次性）**：`xcopy /eiy chickery-figure-style resource-library/figures/chickery-figure-style` 后 `python scripts/resource_index.py .`。

## 四、使用（主项目内）
```python
import sys; sys.path.insert(0, "resource-library/figures/topjournal-style/scripts")
import tjstyle, json
cfgs = json.load(open("resource-library/figures/topjournal-style/scripts/figure_style_config.json"))
# 默认 topjournal；可切 publication/compact/colorblind，或按需覆盖
with tjstyle  # tjstyle 已设好宋体/Times、符号加粗、数据不透明、无网格、黑边图例、内容不越框等
ax ...; tjstyle.leg(ax, ...)          # 黑边图例
fig.savefig("f.pdf", bbox_inches="tight"); fig.savefig("f.png", dpi=300, bbox_inches="tight")  # 矢量+PNG@300dpi
# 写 <name>.render.json
```

## 五、校验与边界
- 接入不新增主项目"技能数/脚本数/测试数"，故 `test_doc_claims`、`validate_skill_trees`、`validate_repo` 不受影响；新增的仅 `resource-library` 与 `docs` 内容，按 `python scripts/resource_index.py .` 登记即可。
- 全程离线；`references/` 只读区、四棵技能树编辑纪律(`.codex/skills` 为源→`sync_plugin.py`)保持不变。
