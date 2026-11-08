from pathlib import Path
import math
from matplotlib.figure import Figure
x=[i/1000 for i in range(1001)]
def h(p): return -sum(v*math.log2(v) for v in (p,1-p) if v>0)
fig=Figure(figsize=(10,6),layout='constrained');ax=fig.subplots();ax.plot(x,[h(v) for v in x],color='#335ec7',linewidth=3);ax.scatter([0,.5,1],[0,1,0],color='#cc5645',zorder=3);ax.annotate('(0.5, 1 bit)',(.5,1),xytext=(.58,.89))
ax.set(xlabel='Probability p',ylabel='Entropy (bits)',title='Entropy of a Bernoulli distribution',xlim=(0,1),ylim=(0,1.08));ax.grid(alpha=.25)
p=Path(__file__).resolve().parent.parent/'assets/images/babak-ai/ch21-entropy.webp';p.parent.mkdir(parents=True,exist_ok=True);fig.savefig(p,format='webp',dpi=150);print('bytes=',p.stat().st_size)
