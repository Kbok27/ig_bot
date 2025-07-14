"""
synthetic_oos.py

Generates a synthetic out-of-sample CSV (random-walk OHLCV) into data/oos/ for testing.
"""
import os
import pandas as pd
import numpy as np

# Ensure data/oos exists relative to this script
dir_path = os.path.join(os.path.dirname(__file__), 'data', 'oos')
os.makedirs(dir_path, exist_ok=True)

# Generate synthetic random-walk data
n_bars = 100
start_price = 100.0
date_index = pd.date_range(end=pd.Timestamp.now(), periods=n_bars, freq='5T')
np.random.seed(42)
price_changes = np.random.normal(loc=0, scale=0.2, size=n_bars)
close = start_price + np.cumsum(price_changes)
open_ = np.concatenate([[start_price], close[:-1]])
high = np.maximum(open_, close) + np.abs(np.random.normal(0, 0.1, size=n_bars))
low = np.minimum(open_, close) - np.abs(np.random.normal(0, 0.1, size=n_bars))
volume = np.random.randint(100, 1000, size=n_bars)

# Create DataFrame
df_oos = pd.DataFrame({
    'Time': date_index,
    'Open': open_,
    'High': high,
    'Low': low,
    'Close': close,
    'Volume': volume
})

# Save to CSV
oos_path = os.path.join(dir_path, 'synthetic_oos.csv')
df_oos.to_csv(oos_path, index=False)
print(f'Synthetic OOS file created: {oos_path}')
