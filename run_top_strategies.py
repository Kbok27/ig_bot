import os
import pandas as pd
from datetime import datetime
import MetaTrader5 as mt5
import importlib.util
import sys

# ✅ LOAD THE CORRECT STRATEGY FILE
strategy_path = os.path.join("strategies", "strategy_sma_stoch_rr_v2.py")
spec = importlib.util.spec_from_file_location("strategy_sma_stoch_rr_v2", strategy_path)
strategy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(strategy)

print("[DEBUG] ✅ Loaded strategy from path:", strategy_path)

# ✅ ALWAYS LOAD FROM MT5
def load_data(symbol="NAS100.a", timeframe=mt5.TIMEFRAME_M5, bars=5000):
    print(f"[INFO] Connecting to MetaTrader 5 for symbol: '{symbol}' ({bars} bars @ {timeframe})...")

    if not mt5.initialize():
        raise RuntimeError("❌ Could not initialize MT5. Is MetaTrader 5 running and logged in?")

    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)

    if rates is None or len(rates) == 0:
        raise RuntimeError(f"❌ No data received from MT5 for {symbol}.")

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df.set_index("time", inplace=True)
    df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close"}, inplace=True)

    print(f"[INFO] ✅ Successfully loaded {len(df)} bars from MT5 for {symbol}.")
    return df

# ✅ PARAMETER SETS TO TEST
strategy_params = [
    {"atr_period": 14, "atr_multiplier": 1.5, "take_profit_pips": 40, "min_candle_size_pips": 1, "sma50_distance_pips": 50, "min_leg_move": 0.3, "max_leg_gap": 0.4, "min_legs_before_trade": 4},
    {"atr_period": 14, "atr_multiplier": 1.5, "take_profit_pips": 30, "min_candle_size_pips": 1, "sma50_distance_pips": 50, "min_leg_move": 1.5, "max_leg_gap": 1.0, "min_legs_before_trade": 3},
    {"atr_period": 10, "atr_multiplier": 1.2, "take_profit_pips": 50, "min_candle_size_pips": 1, "sma50_distance_pips": 40, "min_leg_move": 1.5, "max_leg_gap": 0.2, "min_legs_before_trade": 4},
    {"atr_period": 16, "atr_multiplier": 2.0, "take_profit_pips": 60, "min_candle_size_pips": 2, "sma50_distance_pips": 60, "min_leg_move": 0.8, "max_leg_gap": 0.05, "min_legs_before_trade": 2},
    {"atr_period": 12, "atr_multiplier": 1.8, "take_profit_pips": 45, "min_candle_size_pips": 2, "sma50_distance_pips": 55, "min_leg_move": 1.2, "max_leg_gap": 0.6, "min_legs_before_trade": 3},
]

# ✅ SIMPLE STATS EVALUATOR
def evaluate_trades(trades):
    wins = [t for t in trades if t.get("exit_price", 0) > t.get("entry_price", 0)] if trades else []
    losses = [t for t in trades if t.get("exit_price", 0) <= t.get("entry_price", 0)] if trades else []

    num_trades = len(trades)
    win_rate = len(wins) / num_trades if num_trades else 0
    avg_win = sum(t["exit_price"] - t["entry_price"] for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t["exit_price"] - t["entry_price"] for t in losses) / len(losses) if losses else 0
    profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
    net_profit = sum(t["exit_price"] - t["entry_price"] for t in trades) if trades else 0
    expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

    return {
        "Number of Trades": num_trades,
        "Win Rate": win_rate,
        "Average Win": avg_win,
        "Average Loss": avg_loss,
        "Profit Factor": profit_factor,
        "Net Profit": net_profit,
        "Expectancy": expectancy,
    }

# ✅ MAIN LOOP
def main():
    df = load_data(symbol="NAS100.a", timeframe=mt5.TIMEFRAME_M5, bars=5000)

    for i, params in enumerate(strategy_params, 1):
        print(f"\n🔁 Running strategy {i} with params: {params}")
        try:
            trades = strategy.run_strategy(df, **params)
            stats = evaluate_trades(trades)

            print(f"[✅] Strategy {i} Results:")
            for k, v in stats.items():
                print(f"   {k}: {v}")
        except Exception as e:
            print(f"[❌] Strategy {i} failed: {e}")

if __name__ == "__main__":
    main()
