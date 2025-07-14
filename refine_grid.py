"""
refine_grid.py

Automatically derive a refined parameter grid from walk-forward summary results.
Reads the `walkforward_summary.csv`, identifies the top N most frequent parameter combinations,
and builds a new, smaller grid for a follow-up optimization.
"""
import pandas as pd
from itertools import product
import json

def main():
    WF_CSV = 'results/walkforward_summary.csv'
    TOP_N = 5  # number of top combos to consider

    # Load walk-forward summary
    df = pd.read_csv(WF_CSV)

    # Define parameter columns
    param_cols = [
        'take_profit_pips', 'stop_loss_pips',
        'sma50_distance_pips', 'min_candle_size_pips',
        'atr_period', 'atr_multiplier'
    ]

    # Count frequency of each combination
    combo_counts = (
        df.groupby(param_cols)
          .size()
          .reset_index(name='count')
          .sort_values('count', ascending=False)
    )

    # Take top N combos
    top_combos = combo_counts.head(TOP_N)
    print(f"Top {TOP_N} parameter combos by frequency:")
    print(top_combos)

    # For each parameter, collect unique values from top combos
    refined_grid = {}
    for col in param_cols:
        refined_grid[col] = sorted(top_combos[col].unique().tolist())

    # Display the refined grid
    print("\nRefined param_grid for next search:")
    print(json.dumps(refined_grid, indent=2))

    # Optionally save to JSON
    with open('results/refined_param_grid.json', 'w') as f:
        json.dump(refined_grid, f, indent=2)
    print("Saved refined grid to results/refined_param_grid.json")

if __name__ == '__main__':
    main()
