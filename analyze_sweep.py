# analyze_sweep.py

import pandas as pd

# Adjust path if needed
csv_path = "optimize_results/trade_logs/tp_atr_sweep_summary.csv"

# Load and sort
df = pd.read_csv(csv_path)
top = df.sort_values("expectancy", ascending=False).head(10)

print("Top 10 TP / ATR‐stop configurations by expectancy:\n")
print(top.to_string(index=False))
