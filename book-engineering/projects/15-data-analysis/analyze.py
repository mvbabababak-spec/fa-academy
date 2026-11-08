"""Analyze a tiny synthetic study log; no network or real personal data."""
from io import StringIO
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for script/headless use.
import matplotlib.pyplot as plt

DATA = '''topic,minutes
python,30
python,45
math,60
math,
'''


def analyze(csv_text):
    df = pd.read_csv(StringIO(csv_text))
    if not {'topic', 'minutes'}.issubset(df.columns):
        raise ValueError('required columns: topic, minutes')
    df['minutes'] = pd.to_numeric(df['minutes'], errors='raise')
    if (df['minutes'].dropna() < 0).any():
        raise ValueError('minutes cannot be negative')
    missing = int(df[['topic', 'minutes']].isna().any(axis=1).sum())
    clean = df.dropna(subset=['topic', 'minutes'])
    if clean.empty:
        raise ValueError('no complete rows')
    totals = clean.groupby('topic', sort=True)['minutes'].sum()
    mean = float(np.mean(clean['minutes'].to_numpy()))
    return missing, totals, mean


def main():
    missing, totals, mean = analyze(DATA)
    print('omitted_rows=', missing)
    print('total_minutes=', int(totals.sum()))
    print('mean_minutes=', f'{mean:.1f}')
    print('by_topic=', totals.to_dict())
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(totals.index, totals.values, color='#536fd1')
    ax.set(title='Study time by topic', xlabel='Topic', ylabel='Minutes')
    fig.tight_layout()
    path = Path('study_summary.webp')
    fig.savefig(path, format='webp', dpi=120)
    plt.close(fig)
    print('chart=', path)


if __name__ == '__main__':
    main()
