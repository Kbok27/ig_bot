import pandas as pd
import json
import os

# Load extended results
df = pd.read_csv("optimize_results/strategy_batch_extended_results.csv")

# Filter: only strategies with enough trades
filtered = df[df["Trades"] >= 20]

# Sort by Final Equity and take top N
top_n = 5
top_strategies = filtered.sort_values(by="Final_equity", ascending=False).head(top_n)

# Format for JSON
json_configs = []
for _, row in top_strategies.iterrows():
    config = {
        "symbol": row["Symbol"],
        "sl_pips": int(row["SL_pips"]),
        "tp_pips": int(row["TP_pips"]),
        "risk_percent": float(row["Risk_percent"])
    }
    json_configs.append(config)

# Save to JSON file
os.makedirs("optimize_results", exist_ok=True)
with open("optimize_results/top_strategies.json", "w") as f:
    json.dump(json_configs, f, indent=4)

print(f"[✅] Top {top_n} strategies saved to optimize_results/top_strategies.json")
