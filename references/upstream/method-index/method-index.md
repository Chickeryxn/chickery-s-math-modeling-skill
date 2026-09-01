# 方法家族索引（Method Family Index）

> 本索引为**自写参考**（clean-room），受 XiaoMaColtAI 算法库与 Lupynow cookbook 启发，但未复制其原文。用于 `method-selector` 组建候选池前的快速路由；不是决策指令。算法细节以对应上游仓库与权威教材为准。

## 评价/排序类（evaluation / ranking）

| 子类 | 典型方法 | 适用信号 | 主要风险 |
|---|---|---|---|
| 客观赋权 | 熵权法、变异系数法、CRITIC | 有指标数据矩阵、需避免主观权重 | 权重主导、指标冗余 |
| 主观赋权 | AHP、模糊 AHP | 有专家判断、指标少 | 一致性、主观性 |
| 综合评价 | TOPSIS、灰色关联、秩和比、FCE、DEA | 多指标打分/排名 | 方向/权重不当、分数集中 |
| 排序稳定性 | 扰动分析、top-k 重叠 | 任何排名结果 | 排名脆弱 |

参考：[Lupynow model-selection-matrix](../../references/upstream/lupynow-writing/model-selection-matrix.md)、[nature-figure 图契约](../../references/upstream/nature-figure/figure-contract.md)。

## 预测/估计类（prediction / estimation）

| 子类 | 典型方法 | 适用信号 | 主要风险 |
|---|---|---|---|
| 时间序列 | 指数平滑、ARIMA/SARIMA、GM(1,1) | 短序列、趋势+季节 | 非平稳、外推越界 |
| 回归 | 线性/岭/Lasso、逐步回归 | 连续目标、特征中等 | 多重共线性、过拟合 |
| 机器学习 | RF、XGBoost、LightGBM、SVM | 特征多、非线性 | 数据量不足、泄漏、不可解释 |
| 深度学习 | BP、LSTM（小数据慎用） | 序列/图像、数据量大 | 过拟合、可解释性差 |

参考：XiaoMaColtAI `assets/02-预测类算法说明.md`（无许可证，仅按链接查阅）、Lupynow `cookbook-ml.md`（MIT，已并入写作层？未并入，仅参考）。

## 优化/决策类（optimization / decision）

| 子类 | 典型方法 | 适用信号 | 主要风险 |
|---|---|---|---|
| 精确 | LP/IP/MILP、网络流、DP | 线性结构、规模适中 | 规模爆炸、可行域问题 |
| 启发式 | GA、PSO、SA、ACO、DE | 非线性/组合、规模大 | 收敛性、参数敏感 |
| 多目标 | NSGA-II、加权和 | 多目标权衡 | Pareto 分布、主观权重 |
| 鲁棒 | CVaR、鲁棒优化 | 数据不确定 | 保守性 |

参考：XiaoMaColtAI `assets/01-优化类算法说明.md`（链接）、Lupynow `cookbook-optimization.md`/`cookbook-game-theory.md`（参考）。

## 分类/聚类类（classification / clustering）

| 子类 | 典型方法 | 适用信号 | 主要风险 |
|---|---|---|---|
| 分类 | 逻辑回归、决策树、RF、SVM、KNN | 有标签 | 类别不平衡、校准 |
| 聚类 | K-Means、层次、DBSCAN、GMM | 无标签 | 簇数选择、稳定性 |
| 降维/变换 | PCA、FA、CLR、NMF | 高维/成分数据 | 可解释性 |

参考：XiaoMaColtAI `assets/05-统计、07-机器学习`（链接）、Lupynow `cookbook-clustering.md`（参考）。

## 机理/动力学类（mechanism / dynamics）

| 子类 | 典型方法 | 适用信号 | 主要风险 |
|---|---|---|---|
| 微分方程 | ODE/PDE 数值解、参数拟合 | 有物理机理 | 参数不可辨识、单位错误 |
| 系统仿真 | 蒙特卡洛、离散事件、元胞自动机 | 随机/涌现 | 复现数不足、分布假设 |
| 博弈 | 纳什均衡、演化博弈 | 多主体交互 | 收益矩阵设定 |

参考：XiaoMaColtAI `assets/06-综合、04-图论`（链接）、Lupynow `cookbook-mechanistic.md`（参考）。

## 图/网络/路由类（graph / routing / network）

| 子类 | 典型方法 | 适用信号 | 主要风险 |
|---|---|---|---|
| 最短路/流 | Dijkstra、最大流、最小费用流 | 网络结构 | 边权设定、操作约束 |
| 组合优化 | TSP/VRP 建模、匈牙利 | 匹配/路径 | 规模、可行性 |
| 中心性 | 度/介数/K-Shell | 网络分析 | 指标解释 |

参考：XiaoMaColtAI `assets/04-图论与网络分析算法说明.md`（链接）、Lupynow `cookbook-network.md`（参考）。

## 使用规则

1. 先看题目要求的**输出形态**（评价/预测/优化/…），再按本索引缩小候选；不按模型名反向套题。
2. 每个候选都必须过 `method-selector` 的风险探针（可执行性/数据覆盖/假设/输出退化/扰动/规模）。
3. 详细算法实现以各上游仓库与教材为准；本索引只负责"路由"，不提供"决策"。
