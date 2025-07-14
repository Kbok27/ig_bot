"""
walkforward_backtest.py

Performs walk-forward testing with optional live MT5 data:
  - If USE_MT5=true, pulls OHLC from MetaTrader5
  - Otherwise, recursively scans local CSVs under 'data/'
1. Splits each dataset into sequential train/test periods
2. Re-optimizes on each train slice using the grid
3. Validates on the subsequent test slice
4. Aggregates and writes results to CSV
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from itertools import product
from strategies.strategy_sma_stoch_rr_v2 import run_strategy
from utils.logger import log

# Optional MT5 integration
use_mt5 = os.getenv("USE_MT5", "False").lower() == "true"
if use_mt5:
    import MetaTrader5 as mt5
    if not mt5.initialize():
        raise RuntimeError(f"MT5 init failed: {mt5.last_error()}")

# Configuration
DATA_FOLDER  = 'data'
OOS_RESULTS  = 'results/walkforward_summary.csv'
TRAIN_LENGTH = timedelta(days=60)
TEST_LENGTH  = timedelta(days=20)

param_grid = {
    'take_profit_pips':     [10, 20, 30, 40],
    'stop_loss_pips':       [10, 20, 30],
    'sma50_distance_pips':  [20, 30, 40],
    'min_candle_size_pips': [0.5, 1.0],
    'atr_period':           [10, 14],
    'atr_multiplier':       [1.0, 1.5],
}
REQUIRED_COLS = ['Open', 'High', 'Low', 'Close']
records = []

# CSV reader helper
def fetch_csv(path):
    df = pd.read_csv(path)
    # Normalize common column names (case-insensitive)
    col_map = {}
    for col in df.columns:
        lower = col.lower()
        if lower == 'time':
            col_map[col] = 'Time'
        elif lower == 'open':
            col_map[col] = 'Open'
        elif lower == 'high':
            col_map[col] = 'High'
        elif lower == 'low':
            col_map[col] = 'Low'
        elif lower == 'close':
            col_map[col] = 'Close'
        elif lower == 'volume':
            col_map[col] = 'Volume'
    if col_map:
        df.rename(columns=col_map, inplace=True)

    if 'Time' not in df.columns:
        raise ValueError("Missing Time column in CSV")
    # Ensure required OHLC columns exist
    missing_cols = [c for c in ['Open','High','Low','Close'] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing OHLC columns in CSV: {missing_cols}")

    df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
    return df.dropna(subset=['Time']).sort_values('Time')

# MT5 data fetcher
def fetch_mt5(symbol, start, end):
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, start, end)
    df = pd.DataFrame(rates)
    df['Time'] = pd.to_datetime(df['time'], unit='s')
    df.rename(columns={
        'open':'Open','high':'High','low':'Low',
        'close':'Close','tick_volume':'Volume'
    }, inplace=True)
    return df[['Time','Open','High','Low','Close','Volume']]

# Build dataset list
items = []
if use_mt5:
    symbols = [s.name for s in mt5.symbols_get() if s.name.endswith('.a')]
    now = datetime.now()
    start_dt = now - (TRAIN_LENGTH + TEST_LENGTH)
    for sym in symbols:
        log(f"Fetching MT5 data for {sym}")
        try:
            df_full = fetch_mt5(sym, start_dt, now)
        except Exception as e:
            log(f"MT5 fetch error {sym}: {e}", level='ERROR')
            continue
        items.append((sym, df_full))
else:
    for root, _, files in os.walk(DATA_FOLDER):
        # Skip any result or temp CSVs
        files = [f for f in files if f.lower().endswith('.csv') and not any(tag in f.lower() for tag in ('_results.csv','mock_','_raw.csv'))]
        for fname in files:
            path = os.path.join(root, fname)
            rel  = os.path.relpath(path, DATA_FOLDER)
            sym  = os.path.splitext(rel.replace(os.sep, '_'))[0]
            try:
                df_full = fetch_csv(path)
            except Exception as e:
                log(f"CSV read error {sym}: {e}", level='ERROR')
                continue
            items.append((sym, df_full))

# Walk-forward logic per symbol
def run_wf(symbol, df_full):
    if df_full.empty:
        return
    missing = [c for c in REQUIRED_COLS if c not in df_full.columns]
    if missing:
        log(f"Skipping {symbol}: missing cols {missing}", level='WARN')
        return
    start = df_full['Time'].min()
    end   = df_full['Time'].max()
    ts = start
    while ts + TRAIN_LENGTH + TEST_LENGTH <= end:
        te   = ts + TRAIN_LENGTH
        tst  = te
        te2  = tst + TEST_LENGTH
        df_tr = df_full[(df_full['Time']>=ts)&(df_full['Time']<te)]
        df_te = df_full[(df_full['Time']>=tst)&(df_full['Time']<te2)]
        if df_tr.empty or df_te.empty:
            break
        # Re-optimize
        best_sh, best_p = -np.inf, None
        for combo in product(*param_grid.values()):
            p = dict(zip(param_grid.keys(), combo))
            try:
                _,_,eq_tr,_,_ = run_strategy(df_tr.copy(), test_mode=False, **p)
            except:
                continue
            r = np.diff(eq_tr)/eq_tr[:-1]
            s = (r.mean()/r.std(ddof=1)*np.sqrt(len(r))) if len(r)>1 and r.std(ddof=1)!=0 else 0.0
            if s > best_sh:
                best_sh, best_p = s, p
        if not best_p:
            ts += TEST_LENGTH
            continue
        # Test
        try:
            _,trds,eq_o,_,_ = run_strategy(df_te.copy(), test_mode=False, **best_p)
        except:
            ts += TEST_LENGTH
            continue
        tot = len(trds)
        wins = sum(1 for t in trds if t.get('pnl',0)>0)
        wr   = wins/tot*100 if tot>0 else 0
        ar   = sum(t.get('pnl',0) for t in trds)/tot if tot>0 else 0
        ro   = np.diff(eq_o)/eq_o[:-1]
        so   = (ro.mean()/ro.std(ddof=1)*np.sqrt(len(ro))) if len(ro)>1 and ro.std(ddof=1)!=0 else 0.0
        records.append({
            'symbol':symbol,
            'train_start':ts,'train_end':te,
            'test_start':tst,'test_end':te2,
            **best_p,
            'train_sharpe':round(best_sh,3),'test_sharpe':round(so,3),
            'test_win_rate':round(wr,2),'test_avg_return':round(ar,4),'test_trades':tot
        })
        ts += TEST_LENGTH

# Execute
for sym, df_full in items:
    run_wf(sym, df_full)

# Save results
os.makedirs(os.path.dirname(OOS_RESULTS), exist_ok=True)
pd.DataFrame(records).to_csv(OOS_RESULTS, index=False)
print(f"Walk-forward summary saved to {OOS_RESULTS}")
