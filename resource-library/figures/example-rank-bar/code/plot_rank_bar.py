import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

# 演示数据：五行方案的综合得分（演示用，非真实竞赛数据）
names = ["方案A", "方案B", "方案C", "方案D", "方案E"]
score = [92, 86, 78, 71, 63]
mean = sum(score) / len(score)

fig, ax = plt.subplots(figsize=(6.4, 3.4), dpi=200)
bars = ax.barh(names[::-1], score[::-1], color="#767676")
# Top-1 用主色突出
bars[-1].set_color("#1A6FC4")
ax.axvline(mean, color="#B91C1C", linestyle="--", linewidth=1.2, label="均值参考线")
for b, v in zip(bars, score[::-1]):
    ax.text(v + 1, b.get_y() + b.get_height() / 2, f"{v}", va="center", fontsize=7)
ax.set_xlabel("综合得分（分）")
ax.set_title("方案排名图（演示模板 · 非真实数据）", fontsize=9)
ax.legend(loc="lower right", fontsize=7)
ax.tick_params(labelsize=7)
ax.set_ylim(-0.6, len(names) - 0.4)
fig.tight_layout()
out = Path(__file__).resolve().parents[1] / "content" / "rank_bar.png"
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out)
print("wrote", out)
