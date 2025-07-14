# examine_params.py
"""
Load the parameter optimization results and display the top-performing parameter sets.
"""
import os
import pandas as pd
from utils.logger import log

RESULTS_CSV = os.path.join('results', 'param_optimization.csv')
TOP_N = 10


def main():
    if not os.path.exists(RESULTS_CSV):
        log(f"Results file not found: {RESULTS_CSV}", level="ERROR")
        return

    # Load full optimization results
    df = pd.read_csv(RESULTS_CSV)

    # Ensure numeric types
    for col in ['win_rate', 'avg_return', 'sharpe']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Sort by Sharpe descending, then avg_return, then win_rate
    df_sorted = df.sort_values(
        by=['sharpe', 'avg_return', 'win_rate'],
        ascending=[False, False, False]
    )

    # Print the top N
    print(f"Top {TOP_N} Parameter Sets by Sharpe Ratio:")
    print(df_sorted.head(TOP_N).to_string(index=False))

    # Optionally save top N to CSV
    top_csv = os.path.join('results', f'top_{TOP_N}_params.csv')
    df_sorted.head(TOP_N).to_csv(top_csv, index=False)
    print(f"Saved top {TOP_N} to {top_csv}")


if __name__ == '__main__':
    main()
