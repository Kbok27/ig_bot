import pandas as pd
from utils.data_loader import get_data
from strategies.strategy_trend_legs import run_strategy

# Load top 3 from CSV
results_df = pd.read_csv("optimize_results/strategy_batch_results.csv")
top_strategies = results_df.sort_values(by="Final_equity", ascending=False).head(3)

# Load historical data
df = get_data(source="mt5", symbol="EURUSD.a", timeframe=5, bars=1000)
pip_size = 0.0001

# Prepare equity DataFrame
equity_df = pd.DataFrame()

# Run each strategy and collect equity per trade
for idx, row in top_strategies.iterrows():
    result = run_strategy(
        df.copy(),
        pip_size=pip_size,
        min_leg_length=1,
        initial_equity=1000,
        sl_pips=int(row["SL_pips"]),
        tp_pips=int(row["TP_pips"]),
        risk_percent=row["Risk_percent"]
    )

    label = f"SL{int(row['SL_pips'])}_TP{int(row['TP_pips'])}_Risk{row['Risk_percent']}"
    equity_series = [t["equity"] for t in result["trades"]]

    # Pad shorter equity lists if necessary
    equity_df[label] = pd.Series(equity_series)

# Save to CSV
equity_df.to_csv("optimize_results/top3_equity_curves.csv", index_label="Trade_Number")
print("[✅] Equity curves saved to optimize_results/top3_equity_curves.csv")
