# File: generate_best_pr.py

import argparse
import pandas as pd

def performance_report(results_dir: str):
    # 1) LOAD THE CSVs
    print(f"▶️  Loading equity & trades from '{results_dir}'…")
    eq     = pd.read_csv(
        f"{results_dir}/equity.csv",
        parse_dates=['timestamp'],
        index_col='timestamp'
    )

    # read trades *without* forcing parse_dates/index_col
    trades = pd.read_csv(f"{results_dir}/trades.csv")
    if 'timestamp' in trades.columns:
        trades['timestamp'] = pd.to_datetime(trades['timestamp'])
        trades.set_index('timestamp', inplace=True)
    else:
        # empty or no timestamp column—just ensure we have the P/L column
        print("⚠️  No timestamp column in trades.csv, proceeding with an empty index.")
        trades.set_index(pd.Index([], name='timestamp'), inplace=True)

    # 2) COMPUTE YOUR METRICS
    total_trades  = len(trades)
    wins          = trades[trades['P/L'] > 0]['P/L']
    losses        = trades[trades['P/L'] <= 0]['P/L']

    net_profit    = trades['P/L'].sum()
    win_rate      = (len(wins) / total_trades * 100) if total_trades else 0.0
    avg_win       = wins.mean()  if not wins.empty  else 0.0
    avg_loss      = losses.mean() if not losses.empty else 0.0
    profit_factor = (wins.sum() / -losses.sum()) if losses.sum() != 0 else float('inf')
    max_dd        = eq['drawdown'].max() * 100  # as a percent

    # 3) PRINT THE PERFORMANCE REPORT
    print("\n📊 PERFORMANCE REPORT")
    print(f"• Total trades     : {total_trades}")
    print(f"• Net profit       : {net_profit:.2f}")
    print(f"• Win rate         : {win_rate:.2f}%")
    print(f"• Avg win          : {avg_win:.4f}")
    print(f"• Avg loss         : {avg_loss:.4f}")
    print(f"• Profit factor    : {profit_factor:.2f}")
    print(f"• Max drawdown     : {max_dd:.2f}%\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate P&L report from equity.csv & trades.csv"
    )
    parser.add_argument(
        "--results-dir", required=True,
        help="Path to the folder containing equity.csv and trades.csv"
    )
    args = parser.parse_args()

    performance_report(args.results_dir)
