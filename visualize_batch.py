# File: visualize_batch.py

import pandas as pd
import matplotlib.pyplot as plt
import os
import sys


def find_csv():
    # Try both locations for your batch_summary.csv
    candidates = [
        os.path.join('results', 'batch_summary.csv'),
        os.path.join('centralized', 'results', 'batch_summary.csv'),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        "None of the expected CSV paths were found:\n  " +
        "\n  ".join(candidates)
    )


def main():
    # 1) Locate and load the CSV
    csv_path = find_csv()
    print(f"📂 Loading data from {csv_path!r}")
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    df.index.name = df.index.name or 'index'
    print("🗄 DataFrame:")
    print(df)

    # 2) Pick which column to plot
    if 'backtest' in df.columns:
        col = 'backtest'
    elif 'net-profit' in df.columns:
        col = 'net-profit'
    else:
        col = df.select_dtypes('number').columns[0]
    print(f"📈 Plotting column: {col!r}")

    # 3) Draw the chart
    fig, ax = plt.subplots()
    df[col].plot(ax=ax, marker='o')
    ax.set_title(f"{col} over {df.index.name}")
    ax.set_xlabel(df.index.name)
    ax.set_ylabel(col)

    # 4) Save into the same results area
    # Preserve whichever folder structure you have
    if os.path.exists(os.path.join('results')):
        out_dir = os.path.join('results', 'plots')
    else:
        out_dir = os.path.join('centralized', 'results', 'plots')
    os.makedirs(out_dir, exist_ok=True)

    out_path = os.path.join(out_dir, 'batch_backtest_plot.png')
    fig.savefig(out_path, bbox_inches='tight')
    print(f"✅ Saved plot to {out_path!r}")


if __name__ == "__main__":
    main()
