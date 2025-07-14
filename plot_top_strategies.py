import pandas as pd
import matplotlib.pyplot as plt
from utils.data_loader import get_data
from strategies.strategy_trend_legs import run_strategy

# Load results and sort
results_df = pd.read_csv("optimize_results/strategy_batch_results.csv")
top_strategies = results_df.sort_values(by="Final_equity", ascending=False).head(3)

# Load data
df = get_data(source="mt5", symbol="EURUSD.a", timeframe=5, bars=1000)
pip_size = 0.0001

# Plot setup
plt.figure(figsize=(10, 6))

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

    trades = result["trades"]
    equity_series = [t["equity"] for t in trades]

    label = f"SL:{row['SL_pips']} TP:{row['TP_pips']} Risk:{row['Risk_percent']}%"
    plt.plot(equity_series, label=label)

plt.title("Top 3 Strategy Equity Curves")
plt.xlabel("Trade #")
plt.ylabel("Equity ($)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("optimize_results/top3_equity_curves.png")
plt.show()
