"""
walkforward_sweep.py

This script performs a walk-forward optimization and testing for a given symbol.

Steps:
1. Initialize the MT5 connection.
2. In each rolling window:
   a. Fetch an in-sample slice for optimization.
   b. Sweep through TP and ATR-stop multipliers to find the best in-sample expectancy.
   c. Fetch the subsequent out-of-sample slice.
   d. Test the best in-sample configuration out-of-sample.
   e. Record OOS performance metrics (win rate and expectancy).
3. Save all window results to CSV and print summary.

Usage:
    python walkforward_sweep.py

Output:
    optimize_results/trade_logs/walkforward/walkforward_results.csv
"""

import os
import sys
import itertools
import traceback
from datetime import datetime

import MetaTrader5 as mt5
import pandas as pd

from strategies.strategy_sma_stoch_rr_v2 import run_strategy

# === Configuration ===
SYMBOL = "NAS100.a"
PIP_FACTORS = {SYMBOL: 0.1}

# Data fetch parameters
TIMEFRAME = mt5.TIMEFRAME_M5
BARS_PER_WINDOW = 2000
OUT_OF_SAMPLE = 500
WINDOW_STEP = 500

# Parameter grid
TP_SPACE = [20, 40, 60]
ATR_MULT_SPACE = [0.5, 1.0, 1.5]

# Output directory
RESULTS_DIR = os.path.join('optimize_results', 'trade_logs', 'walkforward')
os.makedirs(RESULTS_DIR, exist_ok=True)


def initialize_mt5():
    """
    Initialize the MT5 connection, or exit on failure.
    """
    if not mt5.initialize():
        print(f"[❌] MT5 init failed: {mt5.last_error()}")
        sys.exit(1)
    print(f"[ℹ️] MT5 initialized for {SYMBOL}")


def get_data(symbol: str, start_pos: int, bars: int) -> pd.DataFrame:
    """
    Fetch `bars` bars starting at `start_pos`. Return None if insufficient data.
    """
    rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, start_pos, bars)
    if rates is None or len(rates) < bars:
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','tick_volume':'Volume'}, inplace=True)
    return df


def main():
    initialize_mt5()
    summary = []
    start = 0
    window_idx = 1

    # Walk-forward loop
    while True:
        print(f"\n[INFO] Window #{window_idx}: bars {start} to {start + BARS_PER_WINDOW}")
        insample_df = get_data(SYMBOL, start, BARS_PER_WINDOW)
        oos_df = get_data(SYMBOL, start + BARS_PER_WINDOW, OUT_OF_SAMPLE)
        if insample_df is None or oos_df is None:
            print("[ℹ️] No more data, finishing.")
            break

        # In-sample optimization
        best_cfg = None
        best_exp = -float('inf')
        for tp, atr_mult in itertools.product(TP_SPACE, ATR_MULT_SPACE):
            res = run_strategy(
                insample_df,
                take_profit_pips=tp,
                stop_loss_pips=tp // 2,
                pip_factor=PIP_FACTORS[SYMBOL],
                use_atr_stop=True,
                atr_stop_multiplier=atr_mult,
                atr_period=10,
                atr_multiplier=1.0,
                sma50_distance_pips=30,
                min_candle_size_pips=0.5,
                min_leg_move=0.3,
                max_leg_gap=10,
                initial_equity=1000.0
            )
            wins, losses = res['wins'], res['losses']
            total = wins + losses
            if total == 0:
                continue
            avg_win = res['trade_log']['profit'][res['trade_log']['profit'] > 0].mean() or 0
            avg_loss = res['trade_log']['profit'][res['trade_log']['profit'] <= 0].mean() or 0
            exp_val = (wins / total) * avg_win + (losses / total) * avg_loss
            if exp_val > best_exp:
                best_exp, best_cfg = exp_val, (tp, atr_mult)
        print(f"[OPT] Best in-sample TP={best_cfg[0]} ATRmult={best_cfg[1]} (exp={best_exp:.3f})")

        # Out-of-sample test
        tp, atr_mult = best_cfg
        oos_res = run_strategy(
            oos_df,
            take_profit_pips=tp,
            stop_loss_pips=tp // 2,
            pip_factor=PIP_FACTORS[SYMBOL],
            use_atr_stop=True,
            atr_stop_multiplier=atr_mult,
            atr_period=10,
            atr_multiplier=1.0,
            sma50_distance_pips=30,
            min_candle_size_pips=0.5,
            min_leg_move=0.3,
            max_leg_gap=10,
            initial_equity=1000.0
        )
        wins_oos, losses_oos = oos_res['wins'], oos_res['losses']
        total_oos = wins_oos + losses_oos
        win_rate_oos = wins_oos / total_oos if total_oos else 0
        avg_win_oos = oos_res['trade_log']['profit'][oos_res['trade_log']['profit'] > 0].mean() or 0
        avg_loss_oos = oos_res['trade_log']['profit'][oos_res['trade_log']['profit'] <= 0].mean() or 0
        exp_oos = win_rate_oos * avg_win_oos + (1 - win_rate_oos) * avg_loss_oos
        print(f"[OOS] WinRate={win_rate_oos:.2%} Expectancy={exp_oos:.3f}")

        # Record
        summary.append({
            'window_start': insample_df['time'].iloc[0],
            'window_end': insample_df['time'].iloc[-1],
            'oos_start': oos_df['time'].iloc[0],
            'tp': tp,
            'atr_mult': atr_mult,
            'oos_win_rate': win_rate_oos,
            'oos_expectancy': exp_oos
        })

        # Advance window
        start += WINDOW_STEP
        window_idx += 1

    # Save results
    out_file = os.path.join(RESULTS_DIR, 'walkforward_results.csv')
    df_res = pd.DataFrame(summary)
    df_res.to_csv(out_file, index=False)
    print(f"\n✅ Walk-forward complete. Results → {out_file}")

    # Summary statistics
    overall_wr = df_res['oos_win_rate'].mean() * 100
    overall_exp = df_res['oos_expectancy'].mean()
    best = df_res.loc[df_res['oos_expectancy'].idxmax()]
    worst = df_res.loc[df_res['oos_expectancy'].idxmin()]
    print("\n--- Walk-Forward Summary ---")
    print(f"Average OOS Win Rate: {overall_wr:.2f}%")
    print(f"Average OOS Expectancy: {overall_exp:.3f} pips/trade")
    print(f"Best Window: Start {best['window_start']} TP={best['tp']} ATR={best['atr_mult']} -> Exp={best['oos_expectancy']:.3f}")
    print(f"Worst Window: Start {worst['window_start']} TP={worst['tp']} ATR={worst['atr_mult']} -> Exp={worst['oos_expectancy']:.3f}")

    mt5.shutdown()


if __name__ == '__main__':
    main()
