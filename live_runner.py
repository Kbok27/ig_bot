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
    # 1) Load shared state
    state = load_state()

    # 2) Fetch full history once
    df_all = get_data(symbol=symbol, timeframe=timeframe, bars=full_bars)
    print(f"Loaded {len(df_all)} bars for {symbol}")

    # 3) Determine starting index
    if state["last_ts"]:
        last_dt   = pd.to_datetime(state["last_ts"])
        start_idx = df_all.index.searchsorted(last_dt, side="right")
    else:
        start_idx = initial_window

    total = len(df_all)

    # 4) Process each new bar exactly once
    for i in range(start_idx, total):
        window = df_all.iloc[: i+1]
        ts     = window.index[-1]

        # ← pass in current balance, get updated balance back
        new_balance = run_strategy(window, state["balance"])

        # update state
        state["last_ts"] = ts.isoformat()
        state["balance"] = new_balance
        save_state(state)

        print(f"[{i+1}/{total}] {ts} → balance: {new_balance:.2f}")

    print("All bars processed. Exiting.")

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Stateful runner: never reprocess bars & track balance"
    )
    p.add_argument("--symbol",         type=str, default="BTCUSD.a")
    p.add_argument("--timeframe",      type=int, default=5)
    p.add_argument("--full_bars",      type=int, default=5000,
                   help="Total bars to pull from MT5")
    p.add_argument("--initial_window", type=int, default=1000,
                   help="How many bars to skip on first run (warm-up)")
    args = p.parse_args()

    main(args.symbol, args.timeframe, args.full_bars, args.initial_window)
