import pandas as pd
import os
from strategies.strategy_trend_legs import run_strategy

def param_search(file_path, output_csv="results/param_search_results.csv"):
    min_leg_moves = [0.05, 0.1, 0.15, 0.2]
    max_leg_gaps = [3, 5, 7, 10]
    min_legs_before_trade = 3  # keep fixed for now

    results = []

    df = pd.read_csv(file_path)
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.set_index("Time")
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

    for min_leg_move in min_leg_moves:
        for max_leg_gap in max_leg_gaps:
            print(f"Testing min_leg_move={min_leg_move}, max_leg_gap={max_leg_gap}...")
            _, trades, equity_curve, _ = run_strategy(df, min_leg_move=min_leg_move, max_leg_gap=max_leg_gap,
                                                     min_legs_before_trade=min_legs_before_trade, debug=False)
            total_trades = len(trades)
            net_profit = equity_curve[-1] if equity_curve else 0

            results.append({
                "min_leg_move": min_leg_move,
                "max_leg_gap": max_leg_gap,
                "total_trades": total_trades,
                "net_profit": net_profit,
            })

    results_df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    results_df.to_csv(output_csv, index=False)
    print(f"Parameter search complete. Results saved to {output_csv}")

if __name__ == "__main__":
    file_path = "data/NAS100_5m.csv"  # Adjust path as needed
    param_search(file_path)
