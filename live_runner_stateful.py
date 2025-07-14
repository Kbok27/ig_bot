# File: live_runner_stateful.py

import os
import json
import argparse
import pandas as pd
from utils.data_utils import get_data
from strategies.strategy_sma_stoch_rr_v2 import run_strategy

STATE_FILE      = "bot_state.json"
DEFAULT_BALANCE = 100_000.0

def load_state():
    if os.path.exists(STATE_FILE):
        raw = json.load(open(STATE_FILE))
        return {
            "last_ts": raw.get("last_ts", None),
            "balance": raw.get("balance", DEFAULT_BALANCE)
        }
    return {"last_ts": None, "balance": DEFAULT_BALANCE}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def main(symbol: str, timeframe: int, full_bars: int, initial_window: int):
    state = load_state()

    # 1) load all historical bars
    df_all = get_data(symbol=symbol, timeframe=timeframe, bars=full_bars)
    print(f"Loaded {len(df_all)} bars for {symbol}")

    # 2) find start index
    if state["last_ts"]:
        last_dt   = pd.to_datetime(state["last_ts"])
        start_idx = df_all.index.searchsorted(last_dt, side="right")
    else:
        start_idx = initial_window

    total = len(df_all)

    # 3) process each unseen bar once
    for i in range(start_idx, total):
        window = df_all.iloc[: i+1]
        ts     = window.index[-1]

        # ⬇️ **Pass both** the DataFrame AND the current balance
        new_balance = run_strategy(window, state["balance"])

        # 4) update & persist state
        state["last_ts"] = ts.isoformat()
        state["balance"] = new_balance
        save_state(state)

        print(f"[{i+1}/{total}] {ts} → balance: {new_balance:.2f}")

    print("All bars processed. Exiting.")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Stateful bar runner")
    p.add_argument("--symbol",         type=str, default="BTCUSD.a")
    p.add_argument("--timeframe",      type=int, default=5)
    p.add_argument("--full_bars",      type=int, default=5000)
    p.add_argument("--initial_window", type=int, default=1000)
    args = p.parse_args()
    main(args.symbol, args.timeframe, args.full_bars, args.initial_window)
