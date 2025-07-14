import pandas as pd
import json
import os

def clean_csv_and_export_json(csv_path, clean_csv_path, json_path, top_n=5, min_trades=20):
    # Load CSV safely, skip any bad lines
    print(f"[INFO] Loading CSV with skipping bad lines from {csv_path}")
    df = pd.read_csv(csv_path, on_bad_lines='skip')

    # Strip whitespace from headers to avoid hidden spaces issues
    df.columns = df.columns.str.strip()
    print("[DEBUG] Columns after load:", list(df.columns))  # Debug columns found

    # Save cleaned CSV
    df.to_csv(clean_csv_path, index=False)
    print(f"[INFO] Clean CSV saved to {clean_csv_path}")

    # Filter by minimum trades - use exact column name from CSV
    filtered = df[df["Number of Trades"] >= min_trades]

    # Sort by Net Profit descending and get top N
    top_strategies = filtered.sort_values(by="Net Profit", ascending=False).head(top_n)

    # Prepare JSON export with all relevant fields from your CSV
    json_configs = []
    for _, row in top_strategies.iterrows():
        config = {
            "Number of Trades": int(row["Number of Trades"]),
            "Win Rate": float(row["Win Rate"]),
            "Average Win": float(row["Average Win"]),
            "Average Loss": float(row["Average Loss"]),
            "Profit Factor": float(row["Profit Factor"]),
            "Net Profit": float(row["Net Profit"]),
            "Max Drawdown": float(row["Max Drawdown"]),
            "Sharpe Ratio": float(row["Sharpe Ratio"]),
            "Expectancy": float(row["Expectancy"]),
            "min_leg_move": float(row["min_leg_move"]),
            "max_leg_gap": float(row["max_leg_gap"]),
            "min_legs_before_trade": int(row["min_legs_before_trade"])
        }
        json_configs.append(config)

    # Make sure directory exists
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    # Write JSON file
    with open(json_path, "w") as f:
        json.dump(json_configs, f, indent=4)

    print(f"[✅] Top {top_n} strategies saved to {json_path}")

# Example usage:
if __name__ == "__main__":
    csv_path = "optimize_results/optimization_results.csv"         # Your CSV input path
    clean_csv_path = "optimize_results/optimization_results_clean.csv"  # Clean CSV output
    json_path = "optimize_results/top_strategies.json"             # JSON output

    clean_csv_and_export_json(csv_path, clean_csv_path, json_path)
