"""Analyze synthetic study sessions, with explicit missing-data policy."""
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

DATA = '''topic,minutes
python,30
python,45
math,60
math,
'''


def analyze(csv_text):
    frame = pd.read_csv(StringIO(csv_text))
    if not {'topic', 'minutes'}.issubset(frame.columns):
        raise ValueError('missing required columns')
    frame['minutes'] = pd.to_numeric(frame['minutes'], errors='raise')
    if frame['topic'].isna().any() or frame['topic'].str.strip().eq('').any():
        raise ValueError('topic missing')
    present = frame['minutes'].dropna().to_numpy()
    if not np.isfinite(present).all() or (present < 0).any():
        raise ValueError('minutes must be finite and nonnegative')
    clean = frame.dropna(subset=['minutes']).copy()
    if clean.empty:
        raise ValueError('no measured minutes')
    totals = clean.groupby('topic')['minutes'].sum().sort_index()
    return clean, totals, int(frame['minutes'].isna().sum())


def make_plot(totals, filename):
    fig = Figure(figsize=(7, 4), layout='constrained')
    ax = fig.subplots()
    ax.bar(totals.index, totals.values, color='#627bd2')
    ax.set(title='Study minutes by topic', ylabel='Minutes', xlabel='Topic')
    fig.savefig(filename, format='webp', dpi=140)


def main():
    clean, totals, missing = analyze(DATA)
    print('valid_rows=', len(clean), 'missing_rows=', missing)
    print('mean_minutes=', float(np.mean(clean['minutes'].to_numpy())))
    print('totals=', {key: float(value) for key, value in totals.items()})
    with TemporaryDirectory() as directory:
        output = Path(directory) / 'study.webp'
        make_plot(totals, output)
        print('webp_created=', output.is_file())


if __name__ == '__main__':
    main()
