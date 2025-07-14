import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

# Load data
df = pd.read_csv("optimize_results/strategy_batch_extended_results.csv")

# Optional filter: only include meaningful runs
df = df[df["Trades"] >= 20]

# Sort by Final Equity
df = df.sort_values(by="Final_equity", ascending=False)

# Rename columns for nicer display
df = df.rename(columns={
    "Symbol": "Symbol",
    "SL_pips": "SL",
    "TP_pips": "TP",
    "Risk_percent": "Risk %",
    "Final_equity": "Equity",
    "Win_rate_percent": "Win %",
    "Sharpe_ratio": "Sharpe",
    "Max_drawdown": "Drawdown",
    "Profit_factor": "Profit Factor",
    "Trades": "Trades"
})

# Create interactive table
fig = px.scatter(
    df,
    x="Sharpe",
    y="Equity",
    size="Profit Factor",
    color="Risk %",
    hover_data=["Symbol", "SL", "TP", "Win %", "Drawdown", "Trades"]
)

# Save full interactive HTML
output_path = "optimize_results/strategy_dashboard.html"
pio.write_html(fig, file=output_path, auto_open=True)

print(f"[✅] Dashboard saved to {output_path}")
