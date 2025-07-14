from strategies import strategy_sma_stoch_rr
import pandas as pd

print("✅ Running direct strategy test...")

# Create mock data
df = pd.DataFrame({
    "Time": pd.date_range(start="2024-01-01", periods=10, freq="T"),
    "Open": [100 + i for i in range(10)],
    "High": [101 + i for i in range(10)],
    "Low": [99 + i for i in range(10)],
    "Close": [100 + i for i in range(10)],
    "Volume": [1000] * 10
})

# Run your strategy
result = strategy_sma_stoch_rr.run_strategy(df)
print("✅ Finished. Result:", result)
