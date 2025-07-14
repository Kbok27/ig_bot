# File: main.py
from pathlib import Path
import json
from utils.data_utils import get_data
from strategies.strategy_sma_stoch_rr_v2 import Strategy

def run_backtest(config):
    symbol       = config["symbol"]
    timeframe    = config.get("timeframe", 2)
    bars         = config.get("bars", 2000)
    strat_kwargs = config["strategy_kwargs"]

    # Extract SL/TP
    sl_pips = strat_kwargs.get("stop_loss_pips")
    tp_pips = strat_kwargs.get("take_profit_pips")
    print(f"▶ Running {symbol} | SL = {sl_pips} pips, TP = {tp_pips} pips")

    # Fetch data
    df = get_data(symbol, timeframe, bars)

    # Initialize strategy
    strat = Strategy(**strat_kwargs)

    # Run backtest
    trades = strat.backtest(df)
    trades.to_csv(Path("results") / f"{symbol}_trades.csv", index=False)

    # (rest of your equity, charting call, etc.)

def main():
    with open("jobs_list.json") as f:
        jobs = json.load(f)
    for job in jobs:
        run_backtest(job)

if __name__ == "__main__":
    main()
