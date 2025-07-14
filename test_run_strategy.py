# test_run_strategy.py

from strategies.strategy_sma_stoch_rr_v2 import run_strategy
import pandas as pd

def test_run():
    df = pd.read_csv("data/NAS100_m5.csv", parse_dates=True, index_col=0)
    result = run_strategy(df)
    
    print(f"Type of result: {type(result)}")
    print(f"Length of result: {len(result)}")
    for i, item in enumerate(result):
        print(f"Item {i} type: {type(item)}")

if __name__ == "__main__":
    test_run()
