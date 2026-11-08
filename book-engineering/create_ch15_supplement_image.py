from pathlib import Path
import sys
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / 'book-engineering/projects/15-data-analysis-supplement'))
from analyze import DATA, analyze, make_plot
_, totals, _ = analyze(DATA)
path = root / 'assets/images/babak-ai/ch15-study.webp'
path.parent.mkdir(parents=True, exist_ok=True)
make_plot(totals, path)
print('bytes=', path.stat().st_size)
