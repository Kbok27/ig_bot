# optimize_strategy.py
"""
Grid-search hyperparameter optimization for your SMA-Stoch-RR strategy.
For each combination of parameters, runs the strategy, computes summary metrics, and saves results to CSV.
"""
import csv
from itertools import product
from datetime import datetime
import MetaTrader5 as mt5

from utils.data_utils import get_data
from strategies.strategy_sma_stoch_rr_v2 import run_strategy

# --- Configuration ---
SYMBOL = 'EURUSD.a'
TIMEFRAME = mt5.TIMEFRAME_M5
BARS = 500
DB_PATH = None  # Not used here, but could write to DB similarly
OUTPUT_CSV = 'optimization_results.csv'

# Define hyperparameter grid (tweak these ranges as desired)
param_grid = {
    'sma_short': [5, 10, 20],
    'sma_long': [50, 100, 200],
    'stoch_k': [3, 5, 7],
    'stoch_d': [3, 5],
    'rsi_period': [14]
}

# Function to compute summary metrics from trades DataFrame
def summarize_trades(trades_df):
    total_trades = len(trades_df)
    wins = (trades_df['return'] > 0).sum() if total_trades else 0
    win_rate = wins / total_trades if total_trades else 0.0
    total_return = trades_df['return'].sum() if total_trades else 0.0
    avg_return = trades_df['return'].mean() if total_trades else 0.0
    max_dd = trades_df['drawdown'].max() if total_trades else 0.0
    return total_trades, wins, win_rate, total_return, avg_return, max_dd


def main():
    # Initialize MT5
    if not mt5.initialize():
        print("MT5 initialize failed:", mt5.last_error())
        return

    # Fetch market data once
    df = get_data(SYMBOL, TIMEFRAME, BARS)
    print(f"Fetched {len(df)} bars for {SYMBOL}")

    # Prepare CSV output
    fieldnames = list(param_grid.keys()) + [
        'total_trades', 'winning_trades', 'win_rate', 'total_return', 'avg_return', 'max_drawdown'
    ]
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp'] + fieldnames)

        # Iterate over all param combinations
        for combo in product(*param_grid.values()):
            params = dict(zip(param_grid.keys(), combo))
            trades_df = run_strategy(df, **params)
            metrics = summarize_trades(trades_df)
            ts = datetime.now().isoformat()
            row = [ts] + list(params.values()) + list(metrics)
            writer.writerow(row)
            print(f"{ts} ▶ Tested {params} -> trades={metrics[0]}, win_rate={metrics[2]:.2%} ")

    mt5.shutdown()
    print(f"Optimization complete. Results saved to {OUTPUT_CSV}")

if __name__ == '__main__':
    main()
