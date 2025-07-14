# optimize_tp_sl.py
# Parameter sweep for TP/SL and ATR-based SL at project root, results to optimize_results/trade_logs

import os
import sys
import itertools
import traceback
from datetime import datetime

import MetaTrader5 as mt5
import pandas as pd

from strategies.strategy_sma_stoch_rr_v2 import run_strategy

# Instrument-specific pip factors for index symbols only
PIP_FACTORS = {
    "NAS100.a": 0.1
    # Add other index symbols here as needed, e.g. "SP500.a": 0.1
}

# Symbols and MT5 settings (focus on indices)
SYMBOLS = ["NAS100.a"]
TIMEFRAME = mt5.TIMEFRAME_M5
BARS = 10000

# Sweep ranges (pips)
TP_SPACE = range(20, 61, 10)  # 20, 30, 40, 50, 60
SL_SPACE = range(10, 31, 5)   # 10, 15, 20, 25, 30

# Directory for sweep results
RESULTS_DIR = os.path.join("optimize_results", "trade_logs")
# Ensure the results directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)


def initialize_mt5():
    """
    Initialize the MT5 connection or exit on failure.
    """
    if not mt5.initialize():
        print(f"[❌] MT5 init failed: {mt5.last_error()}")
        sys.exit(1)
    print("[✅] MT5 initialized")


def main():
    initialize_mt5()
    summary = []

    for symbol in SYMBOLS:
        # Load data once per symbol
        rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, BARS)
        if rates is None or len(rates) == 0:
            print(f"[⚠️] No data for {symbol}, skipping.")
            continue

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "tick_volume": "Volume"
        }, inplace=True)

        pip_factor = PIP_FACTORS.get(symbol, 0.1)

        for tp, sl in itertools.product(TP_SPACE, SL_SPACE):
            try:
                # Run strategy with ATR-based stop-loss enabled
                res = run_strategy(
                    df,
                    take_profit_pips=tp,
                    stop_loss_pips=sl,
                    pip_factor=pip_factor,
                    use_atr_stop=True,
                    atr_stop_multiplier=1.0,
                    atr_period=10,
                    atr_multiplier=1.0,
                    sma50_distance_pips=30,
                    min_candle_size_pips=0.5,
                    min_leg_move=0.3,
                    max_leg_gap=10,
                    initial_equity=1000.0
                )

                trades = res["trade_log"]
                wins = res["wins"]
                losses = res["losses"]
                total = wins + losses
                win_rate = wins / total if total else 0

                avg_win = trades.loc[trades["profit"] > 0, "profit"].mean() if wins else 0
                avg_loss = trades.loc[trades["profit"] <= 0, "profit"].mean() if losses else 0

                gross_wins = trades.loc[trades["profit"] > 0, "profit"].sum()
                gross_losses = trades.loc[trades["profit"] <= 0, "profit"].sum()
                profit_factor = gross_wins / abs(gross_losses) if gross_losses != 0 else float("inf")

                expectancy = win_rate * avg_win + (1 - win_rate) * avg_loss

                summary.append({
                    "symbol": symbol,
                    "tp": tp,
                    "sl": sl,
                    "win_rate": win_rate,
                    "profit_factor": profit_factor,
                    "expectancy": expectancy
                })

            except Exception:
                tb = traceback.format_exc()
                print(f"[⚠️] Error on {symbol} TP={tp}, SL={sl}:\n{tb}")

    # Save summary to optimize_results/trade_logs folder
    summary_df = pd.DataFrame(summary)
    outfile = os.path.join(RESULTS_DIR, "tp_sl_sweep_summary.csv")
    summary_df.to_csv(outfile, index=False)
    print(f"✅ Sweep complete. Results saved to {outfile}")

    mt5.shutdown()
    print("[ℹ️] MT5 shutdown complete")


if __name__ == "__main__":
    main()
