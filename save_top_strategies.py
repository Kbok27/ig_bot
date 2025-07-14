import pandas as pd
import json
import os

def save_top_strategies():
    csv_path = "optimize_results/optimization_results.csv"
    df = pd.read_csv(csv_path)

    # Filter: only strategies with enough trades
    filtered = df[df["Number of Trades"] >= 20]

    # Sort by Final Equity and take top N
    top_n = 5
    top_strategies = filtered.sort_values(by="Final Equity", ascending=False).head(top_n)

    # Format for JSON
    json_configs = []
    for _, row in top_strategies.iterrows():
        config = {
            "min_candle_size_pips": int(row["Min Candle Size Pips"]),
            "sma50_distance_pips": int(row["SMA50 Distance Pips"]),
            "atr_period": int(row["ATR Period"]),
            "atr_multiplier": float(row["ATR Multiplier"]),
            "total_trades": int(row["Number of Trades"]),
            "wins": int(row["Wins"]),
            "losses": int(row["Losses"]),
            "win_rate_pct": float(row["Win Rate"]),
            "final_equity": float(row["Final Equity"]),
        }
        json_configs.append(config)

    # Save to JSON file
    os.makedirs("optimize_results", exist_ok=True)
    with open("optimize_results/top_strategies.json", "w") as f:
        json.dump(json_configs, f, indent=4)

    print(f"[✅] Top {top_n} strategies saved to optimize_results/top_strategies.json")

if __name__ == "__main__":
    save_top_strategies()
