from pathlib import Path
import sys
from matplotlib.figure import Figure
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'book-engineering/projects/20-optimization'))
from gradient_descent import optimize,loss
fig=Figure(figsize=(10,6),layout='constrained');ax=fig.subplots()
for rate in (0.1,1.1):
 path=optimize(0,rate,20);ax.plot(range(len(path)),[loss(x) for x in path],marker='o',markersize=3,label=f'learning rate = {rate}')
ax.set_yscale('log');ax.set(xlabel='Iteration',ylabel='Loss (log scale)',title='Quadratic loss: learning-rate comparison');ax.grid(alpha=.25,which='both');ax.legend()
p=root/'assets/images/babak-ai/ch20-descent.webp';p.parent.mkdir(parents=True,exist_ok=True);fig.savefig(p,format='webp',dpi=150);print('bytes=',p.stat().st_size)
