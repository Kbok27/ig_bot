# File: parameter_sweep_runner.py
import argparse
import pandas as pd
from typing import List, Dict
from utils.data_utils import get_data
from strategies.strategy_sma_stoch_rr_v2 import run_strategy


def calculate_metrics(trades_df: pd.DataFrame) -> Dict[str, float]:
    """
    Compute performance metrics from a trades DataFrame.
    Expects the DataFrame to have a 'P/L' column for profit/loss per trade.
    """
    if 'P/L' in trades_df.columns:
        trades_df = trades_df.rename(columns={'P/L': 'pnl'})
    pnl = trades_df['pnl']
    profit = pnl.sum()
    total = len(pnl)
    wins = pnl[pnl > 0]
    losses = pnl[pnl <= 0]
    win_rate = len(wins) / total if total else 0.0
    avg_win = wins.mean() if not wins.empty else 0.0
    avg_loss = losses.mean() if not losses.empty else 0.0
    cum = pnl.cumsum()
    max_drawdown = (cum.cummax() - cum).max() if not cum.empty else 0.0
    std = pnl.std(ddof=0)
    sharpe = (pnl.mean() / std * (total ** 0.5)) if std and total else 0.0
    return {
        'profit': profit,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'max_drawdown': max_drawdown,
        'sharpe': sharpe
    }


def parameter_sweep(
    df: pd.DataFrame,
    param_grid: List[Dict[str, float]],
    debug: bool = False
) -> pd.DataFrame:
    """
    Runs a parameter sweep, applying `run_strategy` to each config
    and collecting performance metrics.
    """
    results = []
    for params in param_grid:
        if 'rr_ratio' in params:
            params['reward_ratio'] = params.pop('rr_ratio')
        if debug:
            print(f"Running sweep with parameters: {params}")
        _, trades = run_strategy(df.copy(), **params)
        metrics = calculate_metrics(trades)
        results.append({**params, **metrics})
    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(
        description="Run parameter sweeps for the SMA-Stoch-RR strategy (live MT5 data)"
    )
    parser.add_argument("--symbol", required=True, help="Trading symbol (e.g. 'BTCUSD.a')")
    parser.add_argument("--timeframe", type=int, required=True, help="Bar timeframe in minutes")
    parser.add_argument("--bars", type=int, required=True, help="Number of historical bars to fetch")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    df = get_data(symbol=args.symbol, timeframe=args.timeframe, bars=args.bars)

    param_grid: List[Dict[str, float]] = [
        {"fast_sma": 5, "slow_sma": 50, "stoch_k": 14, "stoch_d": 3, "reward_ratio": 2.0},
        {"fast_sma": 10, "slow_sma": 100, "stoch_k": 14, "stoch_d": 3, "reward_ratio": 2.0},
    ]

    results = parameter_sweep(df, param_grid, debug=args.debug)

    output_path = f"results/{args.symbol}_parameter_sweep.csv"
    results.to_csv(output_path, index=False)
    print(f"Sweep complete: saved results to {output_path}")


if __name__ == "__main__":
    main()
