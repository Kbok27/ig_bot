# File: optimize/optimize_batch_extended.py

import json
import argparse
from pathlib import Path
import pandas as pd

# Alias the real data loader to match existing references
from utils.data_utils import get_data as load_symbol_data

# Default parameters for simple config dicts (when symbol/timeframe/bars aren’t provided)
DEFAULT_SYMBOL = "BTCUSD.a"
DEFAULT_TIMEFRAME = 2
DEFAULT_BARS = 2000


def run_optimizer(jobs_json: str, output_csv: str, output_json: str):
    """
    Run a batch optimization over a list of configs.

    Supports both "full" job dicts (with symbol, timeframe, bars, strategy_kwargs)
    and "simple" strat_kwargs-only dicts (e.g. entries from top_configs.json).

    jobs_json:    Path to JSON file with one or more config dicts
    output_csv:   Path to write out a CSV of metrics
    output_json:  Path to write out a JSON of metrics
    """
    # Load job configurations
    with open(jobs_json, 'r', encoding='utf-8') as f:
        jobs = json.load(f)

    # Wrap single dict in list
    if isinstance(jobs, dict):
        jobs = [jobs]

    results = []
    for cfg in jobs:
        # Determine whether this is a full job or simple strat_kwargs
        if 'strategy_kwargs' in cfg or 'symbol' in cfg:
            symbol = cfg.get('symbol', DEFAULT_SYMBOL)
            timeframe = cfg.get('timeframe', DEFAULT_TIMEFRAME)
            bars = cfg.get('bars', DEFAULT_BARS)
            strat_kwargs = cfg.get('strategy_kwargs', {})
        else:
            # Simple dict: treat entire cfg as strategy_kwargs
            symbol = DEFAULT_SYMBOL
            timeframe = DEFAULT_TIMEFRAME
            bars = DEFAULT_BARS
            strat_kwargs = cfg

        # Fetch OHLC data for this symbol/timeframe
        df = load_symbol_data(symbol, timeframe, bars)

        # TODO: plug in your real apply_strategy() & compute_metrics() here
        # For now we output strat_kwargs + placeholder zeros
        metrics = {
            **strat_kwargs,
            'profit': 0,
            'win_rate': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'max_drawdown': 0.0,
            'sharpe': 0.0
        }
        results.append(metrics)

    # Save out
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_csv, index=False)
    df_results.to_json(output_json, orient='records', indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Run extended batch optimization and export results"
    )
    parser.add_argument(
        "--jobs-json", required=True,
        help="JSON file with one or more config dicts"
    )
    parser.add_argument(
        "--csv", required=True,
        help="Where to write CSV results"
    )
    parser.add_argument(
        "--json", required=True,
        help="Where to write JSON results"
    )
    args = parser.parse_args()

    run_optimizer(args.jobs_json, args.csv, args.json)


if __name__ == "__main__":
    main()
