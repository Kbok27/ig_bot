import pandas as pd

# Adjust the path if needed
csv_path = "optimize_results/trade_logs/tp_atr_sweep_summary.csv"

# Load and rank by expectancy
df = pd.read_csv(csv_path)
top10 = df.sort_values("expectancy", ascending=False).head(10)

print("Top 10 TP / ATR-stop configs by expectancy:\n")
print(top10.to_string(index=False))
