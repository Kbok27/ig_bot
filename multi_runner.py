import pandas as pd
import matplotlib.pyplot as plt

from utils.plotting_utils import generate_chart

RISK_PER_TRADE = 0.01  # 1% of equity
STOP_LOSS_PCT = 0.02   # 2% stop loss
TAKE_PROFIT_PCT = 0.04 # Optional TP at 4% for 2R

def run_strategy(df, symbol="TEST_SYMBOL", initial_equity=1000):
    required_cols = ['Close', 'Low', 'High']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    equity = initial_equity
    position = 0
    entry_price = 0
    stop_loss = 0
    take_profit = 0
    trades = []
    equity_curve = []
    position_list = []

    # === OPTIONAL: Add SMAs if not already present ===
    if "SMA20" not in df.columns:
        df["SMA20"] = df["Close"].rolling(20).mean()
    if "SMA50" not in df.columns:
        df["SMA50"] = df["Close"].rolling(50).mean()

    # === MOCK TRADE (remove later) ===
    trades.append({
        "Time": df.index[10],
        "Price": df["Close"].iloc[10],
        "Type": "BUY"
    })

    # === Prepare DataFrame for charting ===
    trades_df = pd.DataFrame(trades)

    # === Call plot ===
    generate_chart(df, symbol=symbol, trades=trades_df)

    return trades_df
