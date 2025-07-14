import pandas as pd
import matplotlib.pyplot as plt

# Load results
df = pd.read_csv("optimize_results/strategy_batch_extended_results.csv")

# === Filter: only include runs with sufficient data ===
filtered_df = df[df["Trades"] >= 20]

# Sort top 10 by Final Equity
top_df = filtered_df.sort_values(by="Final_equity", ascending=False).head(10)

# ==== Plot 1: Final Equity vs Sharpe ====
plt.figure(figsize=(10, 6))
plt.scatter(filtered_df["Sharpe_ratio"], filtered_df["Final_equity"], c="blue", label="Filtered")
plt.scatter(top_df["Sharpe_ratio"], top_df["Final_equity"], c="orange", label="Top 10", edgecolors='k')
plt.title("Final Equity vs Sharpe Ratio (Trades ≥ 20)")
plt.xlabel("Sharpe Ratio")
plt.ylabel("Final Equity")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("optimize_results/dashboard_filtered_equity_vs_sharpe.png")
plt.show()

# ==== Plot 2: Profit Factor vs Max Drawdown ====
plt.figure(figsize=(10, 6))
plt.scatter(filtered_df["Profit_factor"], filtered_df["Max_drawdown"], c="green")
plt.title("Profit Factor vs Max Drawdown (Trades ≥ 20)")
plt.xlabel("Profit Factor")
plt.ylabel("Max Drawdown")
plt.grid(True)
plt.tight_layout()
plt.savefig("optimize_results/dashboard_filtered_profit_vs_drawdown.png")
plt.show()

# ==== Print Top 10 ====
print("\n🏆 Top 10 Strategies (Trades ≥ 20):\n")
print(top_df[[
    "Symbol", "SL_pips", "TP_pips", "Risk_percent",
    "Final_equity", "Sharpe_ratio", "Win_rate_percent",
    "Max_drawdown", "Profit_factor", "Trades"
]])
