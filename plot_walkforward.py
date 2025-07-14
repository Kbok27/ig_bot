import pandas as pd
import matplotlib.pyplot as plt

# Load the walk-forward results
df = pd.read_csv("optimize_results/trade_logs/walkforward/walkforward_results.csv", parse_dates=["window_start"])

# Plot OOS expectancy over time
plt.plot(df["window_start"], df["oos_expectancy"], marker='o')
plt.title("Walk-Forward Out-of-Sample Expectancy Over Time")
plt.xlabel("Window Start")
plt.ylabel("OOS Expectancy (pips/trade)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
