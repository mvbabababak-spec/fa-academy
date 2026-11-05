from pathlib import Path
import numpy as np
from matplotlib.figure import Figure
x=np.linspace(-0.4,2.5,250)
fig=Figure(figsize=(10,6),layout='constrained');ax=fig.subplots()
ax.plot(x,x*x,linewidth=3,label='f(x) = x²');ax.plot(x,2*x-1,'--',linewidth=2,label='tangent: y = 2x − 1')
ax.scatter([1],[1],color='#d14c3c',zorder=3);ax.annotate('(1, 1); slope = 2',(1,1),xytext=(1.15,0.4))
ax.set(xlabel='x',ylabel='y',title='Derivative as tangent slope',ylim=(-1.5,6.5));ax.grid(alpha=.25);ax.legend()
p=Path(__file__).resolve().parent.parent/'assets/images/babak-ai/ch18-derivative.webp';p.parent.mkdir(parents=True,exist_ok=True);fig.savefig(p,format='webp',dpi=150);print('bytes=',p.stat().st_size)
