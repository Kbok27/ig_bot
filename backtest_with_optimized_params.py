import argparse
import os
import pandas as pd
from strategies.strategy_trend_legs import run_strategy
from utils.plotting_utils import plot_strategy_chart
from utils.equity_utils import plot_equity_curve
from utils.performance_utils import calculate_performance_metrics

def main(args):
    df = pd.read_csv("data/NAS100_5m.csv")
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.set_index("Time")
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

    print(f"[INFO] Running backtest with parameters: {args}")

    result_df, trades, equity_curve, debug_log = run_strategy(
        df,
        min_leg_move=args.min_leg_move,
        max_leg_gap=args.max_leg_gap,
        min_legs_before_trade=args.min_legs_before_trade,
        debug=False
    )

    print(f"[INFO] Trades taken: {len(trades)}")
    print(f"[INFO] Final equity: {equity_curve[-1] if equity_curve else 'N/A'}")

    plot_strategy_chart(result_df, trades, symbol="NAS100", output_folder="plots")
    plot_equity_curve(equity_curve, symbol="NAS100", output_folder="plots")

    metrics = calculate_performance_metrics(trades, equity_curve)
    # You can also save metrics here if desired

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backtest with optimized params")
    parser.add_argument("--min_leg_move", type=float, required=True)
    parser.add_argument("--max_leg_gap", type=int, required=True)
    parser.add_argument("--min_legs_before_trade", type=int, required=True)
    args = parser.parse_args()
    main(args)
