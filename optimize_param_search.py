import os
import pandas as pd
from strategies.strategy_trend_legs import run_strategy

def optimize_param_search():
    min_leg_move_vals = [0.1, 0.5, 1.0, 2.0]
    max_leg_gap_vals = [3, 5, 7]
    min_legs_before_trade_vals = [2, 3, 4]

    results = []

    os.makedirs("results", exist_ok=True)

    # Load your data here or pass it in as needed
    df = pd.read_csv("data/NAS100_5m.csv")
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.set_index("Time")
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

    for min_leg_move in min_leg_move_vals:
        for max_leg_gap in max_leg_gap_vals:
            for min_legs_before_trade in min_legs_before_trade_vals:
                print(f"Testing: min_leg_move={min_leg_move}, max_leg_gap={max_leg_gap}, min_legs_before_trade={min_legs_before_trade}")
                result_df, trades_df, equity_curve, debug_log = run_strategy(
                    df,
                    min_leg_move=min_leg_move,
                    max_leg_gap=max_leg_gap,
                    min_legs_before_trade=min_legs_before_trade,
                    debug=False
                )
                # Calculate metrics here or call your calculate_performance_metrics function
                from utils.performance_utils import calculate_performance_metrics
                metrics = calculate_performance_metrics(trades_df, equity_curve)
                metrics.update({
                    "min_leg_move": min_leg_move,
                    "max_leg_gap": max_leg_gap,
                    "min_legs_before_trade": min_legs_before_trade
                })
                results.append(metrics)

    results_df = pd.DataFrame(results)
    results_df.to_csv("results/optimization_results.csv", index=False)
    print("[INFO] Optimization results saved to results/optimization_results.csv")

if __name__ == "__main__":
    optimize_param_search()
