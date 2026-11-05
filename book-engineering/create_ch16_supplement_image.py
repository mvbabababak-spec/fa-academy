from pathlib import Path
import numpy as np
from matplotlib.figure import Figure

x = np.linspace(-1, 6, 200)
fig = Figure(figsize=(10, 6), layout='constrained')
ax = fig.subplots()
ax.plot(x, 2*x+3, linewidth=3, label='y = 2x + 3')
ax.axhline(11, color='#d06045', linewidth=2, label='y = 11')
ax.scatter([4], [11], color='#d06045', zorder=3)
ax.annotate('(4, 11)', (4, 11), xytext=(4.2, 9.4), fontsize=13)
ax.set(xlabel='x', ylabel='y', title='Solving 2x + 3 = 11 graphically', xlim=(-1, 6), ylim=(0, 16))
ax.grid(alpha=0.25)
ax.legend()
p = Path(__file__).resolve().parent.parent / 'assets/images/babak-ai/ch16-linear.webp'
p.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(p, format='webp', dpi=150)
print('bytes=', p.stat().st_size)
