from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p = Path(__file__).resolve().parent.parent / 'assets/images/babak-ai/ch16-graph.webp'
x = np.linspace(-1, 6, 200)
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, 2*x+3, color='#3456b8', linewidth=3, label='y = 2x + 3')
ax.axhline(11, color='#c05b49', linestyle='--', linewidth=2, label='y = 11')
ax.scatter([4], [11], color='#173c8a', s=80, zorder=5)
ax.annotate('(4, 11)', (4, 11), xytext=(4.2, 9.5), fontsize=13)
ax.set(xlabel='x', ylabel='y', xlim=(-1, 6), ylim=(0, 16), title='Intersection: 2x + 3 = 11')
ax.set_xticks(range(-1, 7));ax.set_yticks(range(0, 17, 2))
ax.grid(alpha=.25);ax.legend();fig.tight_layout()
p.parent.mkdir(parents=True, exist_ok=True);fig.savefig(p, format='webp', dpi=140);plt.close(fig)
print(p.stat().st_size)
