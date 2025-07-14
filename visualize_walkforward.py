# File: visualize_walkforward.py

import pandas as pd
import matplotlib.pyplot as plt
from config import SYMBOL, BARS

WF_CSV = "results/equity.csv"  # or walkforward_summary.csv

df = pd.read_csv(WF_CSV, parse_dates=['timestamp'], index_col='timestamp')
print(f"📊 Plotting {len(df)} rows (should match BARS+1) for {SYMBOL}")

# then your line plot of balance, etc.
plt.plot(df.index, df['balance'])
plt.title(f"Equity Curve: {SYMBOL} over {BARS} bars")
plt.show()
