# File: optimize_and_plot.py

import os
import sys
import json
import argparse
import subprocess

import numpy as np
import pandas as pd
import MetaTrader5 as mt5

# ensure utils folder is on the path for data_utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
from data_utils import get_data
from strategies.strategy_sma_stoch_rr_v2 import run_strategy


def main():
    # ─── PARSE ARGUMENTS ───────────────────────────────────────────────────
    parser = argparse.ArgumentParser(
        description="Run optimization and generate dashboard plots in one command."
    )
    parser.add_argument("--symbol",       type=str,   required=True,
                        help="Trading symbol (e.g. EURUSD, NAS100)")
    parser.add_argument("--bars",         type=int,   default=20000,
                        help="Number of bars to load for each backtest")
    parser.add_argument("--min-trades",   type=int,   default=500,
                        help="Minimum trades filter for dashboard")
    parser.add_argument("--min-win-rate", type=float, default=0.18,
                        help="Minimum win rate filter for dashboard")
    parser.add_argument("--save-dir",     type=str,   default="plots",
                        help="Directory to save dashboard plots")
    args = parser.parse_args()

    # ─── INITIALIZE MT5 ─────────────────────────────────────────────────────
    if not mt5.initialize():
        print("[ERROR] MT5 initialization failed")
        return

    try:
        # ─── LOAD BARS ONCE ───────────────────────────────────────────────────
        SYMBOL    = args.symbol if args.symbol.endswith(".a") else args.symbol + ".a"
        TIMEFRAME = mt5.TIMEFRAME_M5

        print(f"[INFO] Loading {args.bars} bars for {SYMBOL} …")
        df_raw = get_data(
            source="mt5",
            symbol=SYMBOL,
            timeframe=TIMEFRAME,
            bars=args.bars
        )
        # strategy expects capitalized column names
        df_raw.columns = [c.capitalize() for c in df_raw.columns]
        print(f"[INFO]  → Done. Data shape = {df_raw.shape}")

        # ─── LOAD HYPERPARAMETER CONFIGS ──────────────────────────────────────
        cfg_path = os.path.join("optimize", "configs", "sample_configs.json")
        with open(cfg_path, "r") as f:
            config_list = json.load(f)

        # ─── RUN STRATEGY FOR EACH CONFIG ────────────────────────────────────
        summary_rows = []
        total = len(config_list)
        for idx, config in enumerate(config_list, start=1):
            print(f"[INFO] Config {idx}/{total}: {config}")
            result = run_strategy(df_raw)

            # normalize result to DataFrame of trades
            if isinstance(result, tuple) and isinstance(result[0], pd.DataFrame):
                trades_df = result[0]
            elif isinstance(result, pd.DataFrame):
                trades_df = result
            else:
                trades_list = result[0] if isinstance(result, tuple) else result
                if isinstance(trades_list, dict):
                    trades_list = list(trades_list.values())
                clean = []
                for t in trades_list:
                    if isinstance(t, dict):
                        clean.append(t)
                    elif hasattr(t, "__dict__"):
                        clean.append(vars(t))
                trades_df = pd.DataFrame(clean)

            # ensure profit column exists (compute from trade data if needed)
            if 'profit' not in trades_df.columns:
                # attempt to compute from entry/exit prices and side
                if {'entry_price','exit_price','side'}.issubset(trades_df.columns):
                    dir_map = {'buy':1, 'sell':-1}
                    trades_df['profit'] = (
                        trades_df['exit_price'] - trades_df['entry_price']
                    ) * trades_df['side'].map(dir_map)
                else:
                    trades_df['profit'] = 0.0

            # compute performance metrics
            n   = len(trades_df)
            win = trades_df['profit'].gt(0).mean() if n else np.nan
            eq  = trades_df['profit'].sum()
            gp  = trades_df['profit'].clip(lower=0).sum()
            gl  = (-trades_df['profit'].clip(upper=0)).sum()
            pf  = gp/gl if gl else np.nan
            md  = trades_df.get('drawdown', pd.Series()).max()
            ar  = trades_df['profit'].mean() if n else np.nan

            summary_rows.append({
                **config,
                'symbol':           SYMBOL,
                'num_trades':       n,
                'win_rate':         round(win,4),
                'final_equity':     round(eq,2),
                'gross_profit':     round(gp,2),
                'gross_loss':       round(gl,2),
                'profit_factor':    round(pf,3),
                'max_drawdown':     round(md,2),
                'avg_trade_return': round(ar,4)
            })

        # ─── WRITE OUT SUMMARY CSV ───────────────────────────────────────────
        out_dir    = os.path.join("optimize", "results")
        os.makedirs(out_dir, exist_ok=True)
        summary_csv = os.path.join(
            out_dir,
            f"optimizer_results_{SYMBOL.replace('.', '')}.csv"
        )
        pd.DataFrame(summary_rows).to_csv(summary_csv, index=False)
        print(f"[✅] Wrote optimization summary to {summary_csv}")

        # ─── CALL DASHBOARD PLOTTER ─────────────────────────────────────────
        dash_py = os.path.join(os.path.dirname(__file__), "plot_dashboard.py")
        if os.path.exists(dash_py):
            cmd = [
                sys.executable, dash_py,
                f"--summary-csv={summary_csv}",
                f"--min-trades={args.min_trades}",
                f"--min-win-rate={args.min_win_rate}",
                f"--save-dir={args.save_dir}"
            ]
            print(f"[ℹ] ▶ Generating dashboard: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        else:
            print(f"[⚠️] plot_dashboard.py not found, skipping dashboard.")

    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()
