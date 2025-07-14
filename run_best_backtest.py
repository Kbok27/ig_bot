import os
import pandas as pd
from strategies.strategy_trend_legs import run_strategy
from utils.plotting_utils import plot_strategy_chart
from utils.equity_utils import plot_equity_curve

def main():
    symbol = "NAS100"
    file_path = os.path.join("data", f"{symbol}_5m.csv")

    print(f"[INFO] Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.set_index("Time")

    df = df.dropna(subset=["Close", "Open", "High", "Low", "Volume"])

    # Best parameters from sweep
    best_params = {
        "min_leg_move": 2.0,
        "max_leg_gap": 3,
        "min_legs_before_trade": 2,
        "debug": True
    }

    print(f"[INFO] Running final backtest with parameters: {best_params}")
    result_df, trades_df, equity_curve, debug_log = run_strategy(
        df,
        min_leg_move=best_params["min_leg_move"],
        max_leg_gap=best_params["max_leg_gap"],
        min_legs_before_trade=best_params["min_legs_before_trade"],
        debug=best_params["debug"]
    )

    print(f"[INFO] Final backtest complete. Total trades: {len(trades_df)}")
    print(f"[INFO] Final equity: {equity_curve[-1] if equity_curve else 'N/A'}")
    print("[INFO] Sample debug logs:")
    for log in debug_log[:5]:
        print(log)

    plot_strategy_chart(result_df, trades_df, symbol=symbol, output_folder="plots")
    plot_equity_curve(equity_curve, symbol=symbol, output_folder="plots")

if __name__ == "__main__":
    main()
