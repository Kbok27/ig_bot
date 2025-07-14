"""
validate_oos.py

Runs the top-N parameter sets (from results/top_10_params.csv) on fresh out-of-sample CSVs in data/oos/ and reports performance.
"""
import os
import pandas as pd
import numpy as np
from strategies.strategy_sma_stoch_rr_v2 import run_strategy
from utils.logger import log

# Paths
TOP_PARAMS_CSV = os.path.join('results', 'top_10_params.csv')
OOS_FOLDER = os.path.join('data', 'oos')
REPORT_CSV = os.path.join('results', 'oos_validation.csv')

# Load top parameter sets
top_df = pd.read_csv(TOP_PARAMS_CSV)

# Ensure out-of-sample folder exists
if not os.path.isdir(OOS_FOLDER):
    raise FileNotFoundError(f"OOS folder not found: {OOS_FOLDER}")

records = []
for fname in os.listdir(OOS_FOLDER):
    if not fname.lower().endswith('.csv'):
        continue
    symbol = os.path.splitext(fname)[0]
    csv_path = os.path.join(OOS_FOLDER, fname)

    # Load the OOS data
    df = pd.read_csv(csv_path)
    if 'Time' in df.columns:
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        df = df.dropna(subset=['Time'])
    else:
        log(f"Skipping {symbol}: no 'Time' column", level='WARN')
        continue

    # Run the strategy for each top parameter set
    for _, row in top_df.iterrows():
        params = row.drop(['symbol', 'trades', 'win_rate', 'avg_return', 'sharpe']).to_dict()
        try:
            _, trades, equity_curve, _, _ = run_strategy(df.copy(), test_mode=True, **params
            )
        except Exception as e:
            log(f"OOS error on {symbol} with params {params}: {e}", level='ERROR')
            continue

        total = len(trades)
        wins = sum(1 for t in trades if t.get('pnl', 0) > 0)
        win_rate = wins / total * 100 if total > 0 else 0.0
        avg_ret = sum(t.get('pnl', 0) for t in trades) / total if total > 0 else 0.0
        returns = np.diff(equity_curve) / equity_curve[:-1]
        sharpe = (
            returns.mean() / returns.std(ddof=1) * np.sqrt(len(returns))
        ) if len(returns) > 1 and returns.std(ddof=1) != 0 else 0.0

        records.append({
            'symbol': symbol,
            **params,
            'trades': total,
            'win_rate': round(win_rate, 2),
            'avg_return': round(avg_ret, 4),
            'sharpe': round(sharpe, 2)
        })

# Save the report
os.makedirs('results', exist_ok=True)
df_report = pd.DataFrame(records)
df_report.to_csv(REPORT_CSV, index=False)
print(f"OOS validation complete. Results saved to {REPORT_CSV}")
