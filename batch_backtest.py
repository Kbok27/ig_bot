# batch_backtest.py

import os
import pandas as pd
import numpy as np
from strategies.strategy_sma_stoch_rr_v2 import run_strategy
from utils.logger import log

# Default strategy parameters
DEFAULT_KWARGS = {
    "take_profit_pips":      30,
    "stop_loss_pips":        20,
    "sma50_distance_pips":   30,
    "min_candle_size_pips":  0.5,
    "atr_period":            10,
    "atr_multiplier":        1.0,
    "min_leg_move":          0.3,
    "max_leg_gap":           10,
}


def backtest_csv_folder(folder="data", test_mode=False):
    """
    Backtest all CSV files in the given folder using the SMA/Stoch strategy.
    Returns a DataFrame summarizing performance per file/symbol.
    """
    results = []
    for fname in os.listdir(folder):
        if not fname.lower().endswith(".csv"):
            continue
        symbol = os.path.splitext(fname)[0]
        csv_path = os.path.join(folder, fname)
        log(f"Loading {symbol} from {csv_path}")

        # Read CSV without forced parse_dates
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            log(f"Failed to read {csv_path}: {e}", level="ERROR")
            continue

        # Detect and parse time column
        if 'Time' in df.columns:
            df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        elif 'time' in df.columns:
            df['Time'] = pd.to_datetime(df['time'], errors='coerce')
        else:
            log(f"Skipping {symbol}: no 'Time' column found", level="WARN")
            continue

        # Drop rows with invalid or missing times
        df = df.dropna(subset=['Time'])
        if df.empty:
            log(f"Skipping {symbol}: no valid timestamps after parsing", level="WARN")
            continue

        # Ensure we have OHLC data
        required_cols = ['Open', 'High', 'Low', 'Close']
        if not all(col in df.columns for col in required_cols):
            log(f"Skipping {symbol}: missing one of {required_cols}", level="WARN")
            continue

        # Run strategy
        df_out, trades, equity_curve, debug_log, extra = run_strategy(
            df.copy(), test_mode=test_mode, **DEFAULT_KWARGS
        )

        # Compute metrics
        total = len(trades)
        wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
        win_rate = wins / total * 100 if total > 0 else 0.0
        avg_return = sum(t.get("pnl", 0) for t in trades) / total if total > 0 else 0.0

        returns = np.diff(equity_curve) / equity_curve[:-1]
        sharpe = (
            returns.mean() / returns.std(ddof=1) * np.sqrt(len(returns))
        ) if len(returns) > 1 and returns.std(ddof=1) != 0 else 0.0

        results.append({
            "symbol": symbol,
            "trades": total,
            "win_rate": round(win_rate, 2),
            "avg_return": round(avg_return, 4),
            "sharpe": round(sharpe, 2),
        })

    summary_df = pd.DataFrame(results)
    os.makedirs("results", exist_ok=True)
    summary_df.to_csv("results/batch_summary.csv", index=False)
    return summary_df


if __name__ == "__main__":
    log("Starting batch backtest...")
    summary = backtest_csv_folder(folder="data", test_mode=False)
    print(summary)
