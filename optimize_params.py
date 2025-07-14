# optimize_params.py

import os
import pandas as pd
import numpy as np
from itertools import product
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from strategies.strategy_sma_stoch_rr_v2 import run_strategy
from utils.logger import log

# Define parameter grid
param_grid = {
    "take_profit_pips":      [10, 20, 30, 40],
    "stop_loss_pips":        [10, 20, 30],
    "sma50_distance_pips":   [20, 30, 40],
    "min_candle_size_pips":  [0.5, 1.0],
    "atr_period":            [10, 14],
    "atr_multiplier":        [1.0, 1.5],
}

OUTPUT_CSV = os.path.join("results", "param_optimization.csv")
MAX_WORKERS = os.cpu_count() or 4


def score_params(args):
    csv_path, combo, test_mode = args
    symbol = os.path.splitext(os.path.basename(csv_path))[0]
    df = pd.read_csv(csv_path)
    if 'Time' in df.columns:
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        df = df.dropna(subset=['Time'])
    else:
        raise ValueError("No Time column in CSV for optimization")
    df_out, trades, equity_curve, _, _ = run_strategy(
        df.copy(), test_mode=test_mode, **combo
    )
    total = len(trades)
    wins = sum(1 for t in trades if t.get('pnl', 0) > 0)
    win_rate = (wins / total * 100) if total > 0 else 0.0
    avg_return = sum(t.get('pnl', 0) for t in trades) / total if total > 0 else 0.0
    returns = np.diff(equity_curve) / equity_curve[:-1]
    sharpe = (
        returns.mean() / returns.std(ddof=1) * np.sqrt(len(returns))
    ) if len(returns) > 1 and returns.std(ddof=1) != 0 else 0.0
    result = {'symbol': symbol, **combo,
              'trades': total,
              'win_rate': round(win_rate,2),
              'avg_return': round(avg_return,4),
              'sharpe': round(sharpe,2)}
    return result


def optimize_single_symbol(csv_path, test_mode=False):
    symbol = os.path.splitext(os.path.basename(csv_path))[0]
    combos = [dict(zip(param_grid.keys(), vals)) for vals in product(*param_grid.values())]
    args_list = [(csv_path, combo, test_mode) for combo in combos]
    results = []
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(score_params, args): args for args in args_list}
        for future in tqdm(as_completed(futures), total=len(futures), desc=f"Optimizing {symbol}"):
            combo = futures[future]
            try:
                res = future.result()
                results.append(res)
            except Exception as e:
                log(f"Error on {symbol} {combo}: {e}", level='ERROR')
    return pd.DataFrame(results)


def main():
    os.makedirs('results', exist_ok=True)
    all_results = []
    for fname in os.listdir('data'):
        if not fname.lower().endswith('.csv'):
            continue
        path = os.path.join('data', fname)
        try:
            df_res = optimize_single_symbol(path, test_mode=False)
            all_results.append(df_res)
        except Exception as e:
            log(f"Error optimizing {fname}: {e}", level='ERROR')
    if not all_results:
        print("No optimization results generated.")
        return
    full_df = pd.concat(all_results, ignore_index=True)

    # Filter out combinations with zero trades
    filtered_df = full_df[full_df['trades'] > 0]
    if filtered_df.empty:
        print("All parameter combos resulted in zero trades. Try loosening your filters or using test_mode.")
    else:
        filtered_df.to_csv(OUTPUT_CSV, index=False)
        print(f"Optimization complete: {len(filtered_df)} valid rows saved to {OUTPUT_CSV}")

if __name__ == '__main__':
    main()
